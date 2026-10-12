# Test, 12 October 2026: cap goals per match in the ratings (Ben)

Idea not in `tuning-evidence.md`: a margin-of-victory cap. A 6-0 or 7-1 tells
us less about a side than the score suggests, so clip each side's goals in a
match at N before they enter the table (attack, defence and the league goal
rate), as Elo systems cap goal difference. Form (points) is unaffected.

Harness: `tools/goal_cap_test.py`, `tune.lambdas` with `engine.build_table`
wrapped to clip scores. Paired bootstrap (1,500 reps) against the live
configuration under the live curve (1.135 / -0.30). Calibration also refitted
per setting (the trap in `tuning-evidence.md`). Fit 2025/26 (6,474 fixtures),
check 2026/27 (1,428). Only the 131 season files reachable from the sandbox
(ESPN/AF-sourced leagues mostly missing), so the same population for both arms.

| Cap | Curve | 2025/26 fit | 2026/27 check |
|---|---|---|---|
| 5 | live | -0.0002, p(worse) 0.19 | +0.0004, 0.92 |
| 5 | refit 1.15 / -0.25 | -0.0001, 0.29 | +0.0006, 0.92 |
| 4 | live | +0.0005, 0.90 | +0.0009, 0.90 |
| 4 | refit 1.15 / -0.50 | +0.0005, 0.91 | +0.0007, 0.86 |
| 3 | live | +0.0025, 1.00 | +0.0026, 0.95 |
| 3 | refit 1.05 / -0.50 | +0.0020, 1.00 | +0.0014, 0.87 |

Negative = better. Every cap is neutral to worse, more so the harder it
clips. Big wins are real evidence of strength, and Poisson shrinkage
(SHRINK_FULL_SEASON) already stops one result dominating. Rejected; nothing
shipped. Do not repeat without a different clipping scheme (for example a
margin-dependent weight rather than a hard cap) and a reason to expect it.
