# Data integrity: where this season goes missing

The board draws on two sources, and nothing in the build used to notice when
they failed to meet. This is the record of what that cost and what now guards
it. Every fault below had the same symptom: a club with no matches played, a
blend that fell straight through to last season, and a fixture priced and
published looking entirely normal.

## The two sources

- **openfootball** supplies last season for most competitions and the *whole*
  current season (played and unplayed) for ten European leagues plus Brazil.
  It spells clubs out in full: *FC Bayern München*, *Bayer 04 Leverkusen*,
  *FC Internazionale Milano*.
- **The live scoreboard** supplies fixtures for the other 61 competitions and
  for every cup tie. It abbreviates: *Bayern Munich*, *Bayer Leverkusen*,
  *Inter Milan*. It serves one date at a time and has no "give me the season"
  call.

A cup tie is rated against the club's **domestic** league, so a Champions
League fixture arrives carrying the live source's spelling and then has to be
found in a table keyed by openfootball's.

## Faults found, September 2026

**1. Unrated rows that were rated.** `team_block` looked up the prior-season
table with the unresolved live-source name. Clubs whose rating had just
resolved correctly were still marked "no season on file", which flagged the
fixture, demoted it a confidence tier under Celtic's Law and threw away its
form.

**2. Twenty-five leagues with ratings and no findable clubs.** `team_pool`
indexed only the most recent prior season while the ratings code fell back to
the older one when the newer was missing. Mexico, Ukraine, Czechia, Azerbaijan
and 21 others had ratings computed that no club could ever be matched into.
Fixing the fallback took the rated pool from 636 clubs to 981.

**3. Every European tie priced on last season.** The current-season table and
the shrunk current ratings were both looked up under the live-source name.
`cur_tables['de.1']['Bayern Munich']` returned nothing, `played` came back 0,
`blend()` returned the pure prior season. A Champions League tie saw P0 for
all four German clubs before the fix and P2 with real form after it.

**4. Founding years.** openfootball writes the year into the name where the
live source does not. Containment matching cannot see through a token wedged
into the middle, so *Bayer Leverkusen* never reached *Bayer 04 Leverkusen*.

**5. Cup ties never reached a domestic league at all.** `h_src` resolved the
club's division with a raw `last_league.get(name)`, no name matching, so every
club the live source spells differently missed. The tie fell back to the cup's
own code and both sides came out unrated. Both callers now go through
`domestic_of`.

**6. The live-sourced competitions had no current season whatsoever.** The
biggest of the six. `fetch_espn` was only ever asked for the fixture window,
today and the next few days, so every row it returned was a match not yet
played. `cur_tables[code]` for those 61 competitions was built from an empty
list. Greece, Mexico, MLS, the J-League, the Nordics: all priced on last year
and nothing else, all of the time. Faults 1 to 5 were the same failure through
a narrower door.

## Why it stayed hidden

None of these raised an error. The only visible symptom was a scatter of
"not rated — no season on file" rows, which read as missing data rather than
as a matching failure, and fault 6 did not even produce those where a prior
season existed.

**Rule taken from this: a name mismatch, or a missing current season, must
fail loudly or it will not be found.**

## The season-so-far cache

`sources.topup_current` walks a live-sourced competition's season a day at a
time into `current/<code>-<season>.json` and tops it up on each build.

- First walk is roughly 100 days per competition, six competitions at a time.
- After that it re-asks only the last **3** days (`RESCAN`), because a
  scoreboard corrects a scoreline, finalises an abandoned match, or fills in a
  game that was still in progress when yesterday's build ran.
- `deploy.yml` commits `current/` alongside the prediction archive. Without
  that every run redoes the whole walk.
- Results are merged with, not substituted for, whatever the fixture list
  carried, so a result that landed since the last top-up still counts.
- `build.py --no-topup` skips it, for a fast local build.

Verified against a simulated scoreboard: a Greek tie went from `played=0`,
unrated, no form and a Celtic's Law flag, to P4 with real form on both sides.
The second build fetched 4 days instead of 101 and produced an identical
table.

## What guards it now

`nametest.py`, run by `deploy.yml` **before** the build, so a bad change stops
the publish rather than reaching the board:

1. Known live-source spellings resolve to a club **and** that club has matches
   played behind it. An empty record is the exact symptom, so a match alone is
   not enough to pass.
2. No club in the rated pool resolves to a **different** club. A missed match
   leaves a visible gap; a wrong one prices a fixture with someone else's
   rating and says nothing. Currently 981 clubs, 0 resolving elsewhere.
3. Clubs separated only by a founding year stay apart — *CSKA Sofia* and
   *CSKA 1948 Sofia* are different clubs in the same city.

When a "not rated" row turns out to be a name mismatch, add the spelling to
`LIVE_NAMES` as well as fixing it, so it cannot come back.

## Matching rules, in order

`sources.match_team` is deliberately conservative and refuses rather than
guesses:

1. Exact name.
2. Exact normalised form. Normalisation strips accents and generic tokens
   (*FC*, *CF*, *SC*, *calcio*), then applies **aliases first, city exonyms
   second**. The other order turns "Inter Milan" into "inter milano" before
   the alias fires, and it then matches whatever else is in Milan — this
   happened, and resolved Inter to AC Milan.
3. Containment, with two guards: a candidate reducing to a bare city name
   identifies nobody, and more than one candidate means unmatched.
4. Last resort, containment with founding years stripped from both sides.
   Both guards still apply.

Stripping years belongs at step 4, not in the normalised form: as a
normalisation step it collapses the two CSKA clubs into one.

## Still open

- The 45 competitions with no **prior** season still need
  `backfill.py --probe` to prune dead slugs, then `backfill.py --season 2025`
  / `--season 2025-26`. The current-season cache does not replace this: a club
  three games into a season is still mostly its prior rating. Until then those
  fixtures carry a placeholder 1.00/1.00 and are flagged unrated.
- Whether genuinely-unrated rows should keep competing for the top of the
  board on raw confidence. They currently do, by an explicit choice in the
  code, and a placeholder rating can produce a confident-looking number off
  nothing. Douglas's call.


## 30 September 2026: gender, country and continent in club lookup

Roma women v Barcelona women (UWCL) was priced off men's Serie A Roma and
Ecuador's men's Barcelona SC. `build.domestic_of(team, comp)` now resolves a
name only among leagues where `engine.eligible_league(src, comp)` holds: same
gender (`engine.WOMEN_CODES`), and for a cup the cup's country or, for
continental cups, its confederation (`engine._CONFED`, by iso). League
fixtures use their own league first; remaining clashes take the higher
strength. Nothing eligible means unrated, which the publish gate withholds.


## 4 October 2026: duplicate league feeds

Audit of `predictions/2026-10-04.json`: no exact or reversed duplicates, no
unrated rows. One real fault: `af.203` (API-Football Super Lig) repeated
`tr.1`, so four fixtures were priced twice under different spellings
(Kasimpasa / Kasımpaşa), which exact-name checks cannot see; compare kickoff
times. `engine.AF_DUPLICATES` now keeps it out of `build.CODES`, and
`nametest.py` guards it. Of 227 `af-leagues.json` leagues it is the only live
overlap; `af.144` (Belgium) and `af.202` (Tunisia) would overlap `be.1` /
`tn.1` if those ever carry fixtures. Same-name clubs in different countries
(Al Arabi in three Gulf leagues, Police in Uganda and Kenya, Andorra the club
v the nation) are distinct, not matches. 42 rows carry a UTC kickoff on the
next day from their row date (Americas evenings); left as the local-day
convention.


## 12 October 2026: fixture audit, rescheduled games leave stale rows

Audit of `predictions/2026-10-12.json` (2,014 rows, dated 12-18 Oct). Clean:
no exact or reversed duplicates, no club playing twice on one date in one
league, no unrated rows, no kick-off earlier than its row date, no two feeds
repeating a fixture (`AF_DUPLICATES` holds). 19 rows have no kick-off (Brazil
Serie A) and are dated by day. Same-name clubs on one date (Santos in Brazil
and Mexico, Platense in Argentina and Honduras, Liverpool in England women's
and Uruguay, Barcelona in Ecuador and Spain women's, San Miguel, Sandviken,
Atenas) are different clubs, each priced inside its own league, so nothing
forced and no `LIVE_NAMES` change.

One real finding, not fixed: `build.archive_predictions` keys rows on
`(league, date, home, away)`, so when the source moves a game the old-date row
stays beside the new one. Llerenense v Puebla Calzada (af.452) and Atletico
Mineros v Velarde (af.441) sit under both 17 and 18 Oct, the earlier build
carrying the 18th (01:21 UTC) and the later one the 17th (13:11 UTC). Across all 2026
archives: 46 such pairs, 4 touching a list or reserve flag. The site is built
from the current fixtures, so the page is right; the stale row never gets a
result on its date, so it is not graded as a hit or miss. Open question for
Douglas: drop an unplayed row when a later build moves the same
(league, home, away) to another date. It touches the archive and the
scoreboard, so it was left alone. Check first that stale rows do not inflate
the pending count in the records.

## 21 October 2026: fixture audit, Tanzania and Leatherhead double-booked, case-variant spellings

Audit of `predictions/2026-10-21.json` (1,999 rows, dated 21-27 Oct). Clean:
no exact, reversed or accent/case-folded duplicates, no unrated rows, no
kick-off earlier than its row date, no fixture repeated across two feeds
(`AF_DUPLICATES` holds; `nametest.py` passes). 29 rows have no kick-off and
are dated by day. No `LIVE_NAMES` change needed; `match_team` maps
`EAST BENGAL`, `KYOTO SANGA` and `VIKING FK` onto the right clubs.

Findings, none fixed (no network or API key in this run, so the source could
not be re-read, and a guessed fix would break Rule 6):

1. **Clubs playing twice at one kick-off.** af.567 (Tanzania) on 24 Oct 13:00
   UTC: Young Africans v Tabora United, Dodoma Jiji v Young Africans, Singida
   Black Stars v Tabora United. en.7i on 27 Oct 19:45 UTC: Welling United v
   Leatherhead and Leatherhead v Wingate & Finchley. A club cannot play two
   games at once, so at least one date or time in each set is the source's
   placeholder. The Tanzania set has been in every archive since 19 Oct, so
   it is the source, not a build glitch. None is on the Daily List
   (the list pick in af.567 is Young Africans v Mashujaa, 27 Oct, a different
   day). Whichever row is wrong will not be graded on its date.
2. **Rescheduled games leave a stale row** (same cause as 12 Oct): uy.1
   Defensor Sporting v Racing (23 and 24 Oct), fr.2 Montpellier v Red Star
   (24 and 26 Oct), and six Spanish and Greek lower-league games (24 and 25 Oct).
   The later build moved each; the earlier row is unplayed. None carries a
   list flag. Still the open question from 12 Oct.
3. **Case-variant spellings split a fixture in the 18 Oct archive.** Four
   fixtures (Churchill Brothers and Inter Kashi v East Bengal, Kyoto Sanga v
   Kashima Antlers, Aston Villa v Viking FK) sit twice, once as
   `EAST BENGAL` / `KYOTO SANGA` / `VIKING FK`, published 09:38, 14:57 and
   19:15 UTC, between builds with the normal spelling. The two spellings were
   priced differently (Viking FK home 73.8% v 57.5%; East Bengal rows flagged
   `celtic` on the upper-case copy only), so the upper-case source gave a
   worse read. `archive_predictions` keys on the exact spelling, so both
   stayed. It has not recurred since 18 Oct (19 to 21 Oct clean). Open
   suggestion: fold case in the archive key and the within-build backstop in
   `build.py`. It changes the archive and scoreboard, so it is left for
   Douglas; the cause (which source emitted upper case) is unknown.
