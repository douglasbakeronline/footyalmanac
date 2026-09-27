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
