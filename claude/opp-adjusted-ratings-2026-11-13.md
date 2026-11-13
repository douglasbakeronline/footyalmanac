# Opponent-adjusted attack and defence ratings, 13 November 2026 (Ben)

Idea not in the tested list: `strength_from_table` rates a side on raw goals for
and against per game, so a side that played the weak half of the table early
looks better than it is. Test: divide each side's goals by what its opponents'
ratings say they would give or concede (3 iterations, ratings shrunk with the
live `SHRINK_FULL_SEASON` 4 each pass), blend with the raw rating by `lam`
(0 raw, 1 fully adjusted). `tools/opp_adjust_eval.py`; same harness shape as
`att_def_shrink_eval.py` (`tune.lambdas`, the replay's own functions, paired
bootstrap 1000 reps vs live). Data: what the session could fetch
(fit 2025/26 6,474 fixtures, check 2026/27 1,584; ESPN leagues partly missing).

Paired change in log loss vs live (negative better), p(worse) in brackets:

| lam | Calibration | Fit 2025/26 | Check 2026/27 |
|---|---|---|---|
| 0.25 | live | -0.0001 (0.29) | -0.0002 (0.08) |
| 0.25 | refit 1.10 / -0.30 | -0.0002 (0.14) | -0.0005 (0.04) |
| 0.50 | live | -0.0000 (0.41) | -0.0005 (0.09) |
| 0.50 | refit 1.10 / -0.30 | -0.0002 (0.17) | -0.0008 (0.03) |
| 1.00 | live | +0.0001 (0.65) | -0.0008 (0.11) |
| 1.00 | refit 1.10 / -0.45 | -0.0001 (0.45) | -0.0014 (0.03) |

The check season likes it (up to -0.0014) but the fit season, 4x larger, moves
at most 0.0002: under the 0.0005 gain gate at every setting, and p(worse) above
0.30 for the fully adjusted. A gain only on the small season is the pattern
that evaporated for SHRINK_FULL_SEASON and FORM_MAX. Rejected, nothing shipped.

Likely why: domestic leagues play a balanced schedule, so by mid-season
everyone's opponents average out; the adjustment only matters in the first
weeks, where the shrinkage and last season's prior dominate anyway.

Possibly worth a look later (not done): apply it only to the games-4-6 weak
spot (`claude/tuning-evidence.md`, 19 Oct), or in cup/uneven-schedule
competitions. Needs the same fit and check gates.
