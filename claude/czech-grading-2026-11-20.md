# The Czech First League graded again (20 Nov 2026)

Build session, 20 Nov 2026 21:17 London.

## What looked wrong

The results ledger's ungraded report on the 19:17 UTC build led with `football|cze.1 8` (picks 3+ days past their start with no result). `record-graded.json` holds no Czech First League row at all for the 2026-27 season after openfootball stopped scoring on 20 Sep: 41 fixtures archived from 9 Oct to 8 Nov (6 reserve picks, 10 at 60%+, none on the Daily List) were never graded.

## Why

Since 18 Nov the build scores the Czech table from the API-Football day pool (`sources.AF_LAG`, `af_lag_results`; the same build log reads "lag cze.1: 40 result(s) filled from API-Football"), but wrote nothing to `current/` (`claude/czech-results-api-football-2026-11-18.md`). `score.py` grades from openfootball, the ESPN live source (ESPN's `cze.1` returns nothing) and the `current/` cache, so it never saw a Czech result. The ratings were mended; the scoreboard was not.

## What changed

`score.lag_results`: for each `AF_LAG` league with an ungraded past prediction, read the same pool through `af_lag_results` (no extra calls: the build reads it on the same run), map API-Football's spelling to the archive's all or nothing (Rule 6, `build._map_names`), grade a prediction from the one result of the same clubs on its own date, and pass results a day or two off through `nearby_results` with its guards (never twice, never a match played before the archived day unless the price was published before that day). Graded results are kept in `current/settled-results.json`, as the API-Football cup results already are, so they stay graded after the pool rolls past them. Without a key (a local run) it does nothing. `tests/test_score_lag.py`.

## What the first CI build should print

`score.py`: "N graded from API-Football results (cze.1)" with N about 41 on the first run, then a handful a round. If it prints "API-Football results not used, unmatched", add the listed names to `ALIASES`; nothing was graded. A country refusal means id 345 is wrong.

## Not changed

The model, the Card (Czech legs were Celtic-flagged off it from 14 Nov; its own grading is `groupings.settle`), the Daily List record (no Czech list pick in the window), the build's fill.

## Also read: League One on 14 Nov

The same report's `en.3 7` are seven League One games of 14 Nov (Bromley v Notts County among them) that ESPN listed with no score on every query since, while the five others that day scored. They look postponed in the international window, not lost by a key: no change made. They will be predicted again on their new dates.

## Roll back

`git revert` the merge, and drop the `cze.1` keys it added from `current/settled-results.json` in the same revert to ungrade them.
