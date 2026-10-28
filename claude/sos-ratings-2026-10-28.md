# Opponent-adjusted ratings (strength of schedule), 28 October 2026 (Ben)

Idea not in `tuning-evidence.md`: the season ratings are raw goals for and
against per game over the league rate (`engine.strength_from_table`), so a side
that played the weak half of the table early looks better than it is. Test: set
each side's attack from goals scored divided by what its opponents' defences
would concede on average (and defence likewise), shrunk with the same
`SHRINK_FULL_SEASON` weight, using the previous pass's ratings for the
opponents. Applied to both the prior-season and in-season tables. A `lam`
exponent scales how hard the opponent term bites; `iters` is the passes.

Method: `replay.replay_league` via `tune.lambdas`, core leagues, 2025/26 fit
(6,474 fixtures), 2026/27 check (1,523). Paired log-loss change against the
live model under the live curve (1.135 / -0.30), negative is better, 1,000-draw
bootstrap, p(worse) beside it. "Refit" picks the best (a, b) on the fit season
for that setting and applies it to both (rule 4). Harness `tools/sos_eval.py`.

| lam, passes | Calibration | 2025/26 | 2026/27 |
|---|---|---|---|
| 0.5, 1 | live | -0.0001, p(worse) 0.32 | -0.0004, 0.15 |
| 0.5, 1 | refit 1.15 / -0.30 | -0.0001, 0.31 | -0.0003, 0.27 |
| 1.0, 1 | live | +0.0001, 0.58 | -0.0004, 0.30 |
| 1.0, 1 | refit 1.15 / -0.45 | +0.0001, 0.60 | -0.0005, 0.24 |
| 1.0, 3 | live | +0.0001, 0.65 | -0.0007, 0.17 |
| 1.0, 3 | refit 1.15 / -0.45 | +0.0001, 0.66 | -0.0009, 0.13 |

Verdict: rejected. The fit season gains nothing (best -0.0001, worse for the
full adjustment), far under the 0.0005 gate and with p(worse) above 0.30. The
check season leans slightly better (up to -0.0009) but a fit that does not
move and a check that does is not a result to ship on (rule 3), and it is a
single short season. Within a league the schedule is close to balanced after a
few games, and the shrinkage plus last season's rating already dominate early
on, which is when the schedule differs most. Nothing shipped; no model number
changed. Worth revisiting only if the 2026/27 check season grows past about
4,000 fixtures and still shows the gain while a new fit season does too.
