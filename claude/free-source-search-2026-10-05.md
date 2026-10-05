# Free source for an uncovered league: search, 5 Oct 2026 (Ava, Fixture Scout)

**Outcome: nothing added. No free, automatable source exists for the leagues still without data.** Written up so nobody repeats the search.

## What is still uncovered
First divisions in `engine.LEAGUES` with `live: True` but no working source: Croatia (`hrv.1`), Serbia (`srb.1`), Ukraine (`ukr.1`), Hungary (`hun.1`), South Korea (`kr.1`). ESPN has no slug for them (`claude/daily-list.md`) and openfootball publishes no schedule. Several of their lower divisions are already on the board through API-Football (`af-leagues.json`, paid).

## Checked, 5 Oct 2026
- **football-data.co.uk** `new/*.csv`: the 16 extra leagues are ARG, AUT, BRA, CHN, DNK, FIN, IRL, JPN, MEX, NOR, POL, ROU, RUS, SWE, SWZ, USA. Five are already in `sources.FDX`. The other 11 are covered by ESPN with matching volumes (2026 completed games, FDX v `current/`): Austria 42 v 39, Denmark 54 v 54, China 208 v 208, Norway 168 v 168, Sweden 176 v 176, Argentina 404 v 413, Mexico 88 v 88, USA 404 v 405, Japan 80 (FDX files it as 2026/2027) v 280 on ESPN. Swapping them would change spellings under a working history for no gain (`claude/data-integrity.md`). No file exists for Croatia, Serbia, Ukraine, Hungary or Korea.
- **ESPN** `hrv.1`, `srb.1`, `ukr.1`, `hun.1`, `kor.1`, `uae.1`, `pol.2`, `ger.3`: no usable scoreboard.
- **TheSportsDB free key (`/json/3/`)**: league ids exist (Croatia 4629, Serbia 4671, Ukraine 4354, Hungary 4690, K League 1 4689) but `eventsseason.php` returns **5 events per season** on the free key, for every league tried (including Mexico). Too thin to rate a league or price a round. Full seasons need a paid key, which breaks "no new keys".

## Decision
Not built (Rule 10). The only route that works today is API-Football, already paid for: add the five top flights to `sources.AF` with their league ids, replay each, and keep them off the Daily List until they pass 80% (`claude/data-expansion-plan.md`, "Next"). That is a model/data change for a session that can replay it, not an unattended one.
