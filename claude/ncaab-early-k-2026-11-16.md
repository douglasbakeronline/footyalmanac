# College basketball: a faster K early in the season, and the Behind .500 mark (16 Nov 2026)

Asked by Douglas after UMBC v Iona. The board had UMBC at 81% (reserve). UMBC
won the America East last season but brought back no starters. The bookmakers
had Iona as favourites (about 56%), and so did most of the commentators. The
rating was carrying last season's team.

`claude/daily-list-losses-2026-11-14.md` had left two tests owed: a faster
early-season K and a heavier summer regression. Both ran on the replay
`sports.py --tune` uses.

## Test

`tools/ncaab_carry_eval.py`:

- fit 2024-25, check 2025-26 to the archive start (5,814 warm games);
- every variant gets its own season-phase calibration, fitted on the fit season;
- each variant is paired against live (k 32, hfa 100, regress 0.25, mov 1) on the same games;
- Rule 3 gates apply, plus the 65%+ honesty guard.

| Variant | Check log loss | Gain | p(worse) | 65%+ gap | Verdict |
|---|---|---|---|---|---|
| live | 0.5499 | | | 0.022 | |
| regress 0.35 | 0.5503 | -0.0005 | 0.96 | 0.020 | fail |
| regress 0.5 | 0.5517 | -0.0018 | 0.99 | 0.019 | fail |
| **early K x1.5 for 6 games** | **0.5475** | **+0.0024** | **0.00** | **0.020** | **pass** |
| early K x1.5 for 10 | 0.5480 | +0.0019 | 0.01 | 0.020 | pass |
| early K x2.0 for 6 | 0.5476 | +0.0023 | 0.02 | 0.017 | pass |
| early K x2.0 for 10 | 0.5490 | +0.0008 | 0.24 | 0.020 | pass |
| regress 0.35 + early K x1.5 for 6 | 0.5486 | +0.0013 | 0.04 | 0.017 | pass |

Findings:

- A heavier summer regression is worse. Pulling every team towards average hurts
  the many sides that did not change.
- Letting the first six games of a season move a rating half as far again
  helps. It finds the changed teams from their own results.
- x1.5 for 6 was the first faster-K variant listed and is the best of them.

## Shipped

- `sports.EARLY_K = {"ncaab": {"earlyK": 1.5, "earlyN": 6}}`. `Elo` counts a team's
  games since its last summer break (`season`) and applies the multiplier while
  either side is inside its first six.
- `tune_sport` merges the setting into every grid point, so `sports.json`'s
  params carry it.
- `tests/test_sports_early_k.py`.
- The free refit with the faster K chose k 25 and regress 0 and lost the phase
  calibration (65%+ gap 0.022 to 0.028). That set is untested, so
  `GRID_SPORT["ncaab"]` pins k, hfa, regress and mov at live.
- The refit (`sports.py --tune --only ncaab`) after the change:
  - check 0.5475, matching the test;
  - the phase calibration was refitted and applied (p(worse) 0.03, gap 0.019 to 0.020);
  - the Daily List bar stays at 85%.
- UMBC v Iona on the new setting: 77% (was 81%). Ratings 1596 v 1534 (was 1604 v 1513).

## The Behind .500 mark

The faster K does not mend one segment. In November and December, 70%+ picks of
a side that has played 3+ games this season with more losses than wins:

| Season | Picks | Landed | Quoted |
|---|---|---|---|
| 2024-25 | 155 | 72% | 80% |
| 2025-26 | 176 | 78% | 81% |
| All on file, live | 410 | 74.9% | 80.3% (z -2.8) |
| All on file, early K | 391 | 75.2% | 80.3% (z -2.6) |

Every other pick lands 85.8% against 85.2% quoted.

Shown on the row as "Behind .500" (`trailWary` in `index.html`, beside the
Away / Neutral mark). Display only: the number is unchanged and nothing is
hidden. UMBC (2-3) carries it tonight.

The segment was found on the seasons it is measured on, so the mark is a
caution, not a rule. Pre-registered: if live picks with the mark reach 100 and
land at or above quote, remove the mark. If they sit two standard errors or more
under, they leave the reserve (a release, a note).

## Not done

- Player-level returning minutes: not in any free feed this repo reads.
- College football has the same transfer churn. It was not tested here. The same
  tool can run with `history_for("cfb")` once its own check season is long enough.
