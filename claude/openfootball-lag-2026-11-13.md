# openfootball stopped scoring matches on 20 Sep 2026 (13 Nov 2026)

## What was wrong

The build's current-season tables for the leagues openfootball supplies as a
whole season (fixtures and results in one file) are built from that file
alone. ESPN's season top-up (`topup_current`) ran only for the "gap" leagues
openfootball does not carry. On 13 Nov 2026 every openfootball 2026-27 file
held scores up to 20 Sep 2026 and nothing after:

| league | scored | last scored | blank fixtures before 13 Nov |
|---|---|---|---|
| en.1 | 50 | 20 Sep | 50 |
| en.2 | 95 | 20 Sep | 85 |
| es.1 | 69 | 20 Sep | 51 |
| de.1 | 36 | 20 Sep | 45 |
| it.1 | 50 | 20 Sep | 60 |
| fr.1 | 45 | 20 Sep | 45 |
| nl.1 | 63 | 20 Sep | 45 |
| pt.1 | 62 | 20 Sep | 37 |
| sco.1 | 42 | 20 Sep | 34 |
| at.1 | 42 | 20 Sep | 30 |
| gr.1 | 35 | 20 Sep | 35 |
| cze.1 | 71 | 20 Sep | 41 |
| br.1 | 277 | 20 Sep | 63 |
| tr.1 | 36 | 7 Sep | 63 |
| be.1 | 0 | none | 62 |

746 played matches missing from the ratings, read from the same files the
build fetches (the CI log's `unplayed fixture(s)` warning said 789 on 13 Nov,
the extra from football-data's leagues). Six rounds of the Premier League,
LaLiga and the Bundesliga were invisible to the model: every core-league
number since early October was priced on form to 20 Sep blended with last
season. Belgium had no current season at all. Nothing on the page said so;
the warning added on 26 Oct (meant for postponed fixtures) carried the count
but read like the usual handful of moved matches.

Why it matters for the Card: since rule 7 (11 Nov) the Card is the model's
own picks, football included, and the Edge flag reads the same numbers. A
stale table is the quiet failure `claude/data-integrity.md` warns about.

## The fix

- `build.lagging_codes`: a league with ESPN slugs, not cup, international,
  API-Football or football-data sourced, whose fixture file has blank fixtures
  dated before the window. Returns the day after its last scored fixture.
- `sources.topup_current(..., since=)`: the existing ESPN walk and its
  `current/` cache, started from that day rather than the season's start. A
  lag walk that fails is never marked done (a gap league's dead-slug rule is
  unchanged), so the next build asks again.
- `build.fill_lagging`: each ESPN result scores the blank fixture of the same
  home and away clubs, under openfootball's spelling, within 21 days of its
  date and before the window; a pair openfootball already scored nearby is
  left alone (the primary source wins). A match played more than a day off
  its scheduled date takes the played date. All or nothing on names (Rule 6):
  one ESPN club that matches nothing, or two that match one club, fills
  nothing for that league and prints a `::warning::` naming them.
- Aliases added from the cached Austrian, Greek and Scottish ESPN rows
  (`current/at.1`, `gr.1`, `sco.1`): Rheindorf Altach, WSG Swarovski Tirol,
  AEK Athens, OFI Crete, Saint Johnstone.

The tables are then built exactly as before. The model, its constants and
the calibration are unchanged; it now sees the results that were played.

## What to check on the first CI build

- The `lag <code>: N result(s) filled` lines (expect roughly the table above,
  less any genuine postponement), and any `ESPN results not used` warning:
  each named club is a missing alias, to add to `ALIASES` and `nametest.py`.
- The stale-unplayed warning should fall from about 789 to the genuinely
  postponed handful.
- The first walk asks ESPN for about 53 days a league (165 for Belgium), once;
  later builds ask three or four days.

Not tested here: the sandbox cannot reach ESPN, so the fill ran on stubbed
and cached rows only (`tests/test_lagging_results.py`, and `current/at.1`,
`gr.1` and `sco.1` against their 2026-27 files: every club matched once the
aliases were in, nothing double counted). CI is the check.
