# The Czech First League scored from API-Football (18 Nov 2026)

## The gap

`claude/stale-league-flag-2026-11-14.md` left one league unmended. The Czech
First League's openfootball 2026-27 file stopped scoring after 20 Sep, and
ESPN's `cze.1` slug returns nothing for the season, so the lagging fill of
13 Nov (`build.fill_lagging`) had nothing to fill it with. Since 14 Nov its
fixtures carry a Celtic's Law flag ("missing 41 results from 9 Oct on"), so
they stay off the Daily List, the reserve, the Card's pool and the Edge flag.
Issue #293 left it open for a second source.

## The change

API-Football carries the league (id 345). The build already reads every
API-Football fixture by date into one shared pool for the 227 wider leagues
(`sources.af_season_pool`), so the Czech results are in hand on every CI
build at no extra call.

- `sources.AF_LAG = {"cze.1": 345}`: a lagging league ESPN cannot score and
  API-Football can.
- `sources.af_lag_results(code, season)` reads that league's played fixtures
  of the current season from the pool; `af_lag_pick` is the filter (season
  year, country, played only). The id was set by hand, so the country check
  is `af_rows`' for `AF_NEW`: every row that carries a country must say
  Czechia, or nothing is used and the build warns.
- `build.py`, after the ESPN lagging fill and before `stale_leagues`: a league
  in `AF_LAG` with unplayed fixtures before the window is filled by
  `fill_lagging(..., source="apifootball")`, under openfootball's spelling,
  all or nothing on names (Rule 6). The filled rows are marked
  `filledFrom: "apifootball"`. Nothing is written to `current/`: API-Football
  data is not for redistribution, and the next build reads the pool again.
- Names: openfootball writes Viktoria Plzeň, API-Football (as far as known)
  Plzen. `sources._base` now folds the Czech letters ň ř ý ů ě ť ď, and
  `plzen` is an alias of `viktoria plzen`. The other fifteen clubs match
  API-Football's short spellings one to one (`tests/test_af_lag.py`), Artis
  Brno and Zbrojovka Brno kept apart.

`stale_leagues` runs after the fill, so the Czech flag clears itself on the
first build that fills the table, and comes back on its own if the fill ever
fails.

## What to check on the first CI build

The build log should read `lag cze.1: N result(s) filled from API-Football`
with N about 41 (more as rounds pass) and no `cze.1` in the "table missing
results" warning. If it prints "club names unmatched", add the names it lists
to `ALIASES` (the guard filled nothing, so no wrong rating went out). If it
prints a country mismatch, id 345 is wrong for the league.

## What it does not do

No model constant, Card rule or stale-league threshold moved. `tune.py`'s
check-season fill (`tune.fill_current`) still reads the ESPN cache only, so
the Czech check season in the replays is unchanged; Czechia is not in the
calibration fit's core set either way.
