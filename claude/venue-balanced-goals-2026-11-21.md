# Venue-balanced goals in the ratings: rejected (21 Nov 2026, Ben)

Idea: `strength_from_table` builds attack / defence from goals scored and conceded with home and
away games mixed. Early in a season a side with more home games has inflated goals. Each match's
goals were divided by the venue multiplier (home goals by 1 + f(1.17 - 1), away by 1 + f(0.86 - 1))
before the table was built, so the rating is a neutral-venue rate (`expected_goals` re-applies the
multiplier). Not in the earlier notes (separate home/away ratings and a global tilt are different).

Harness: `tools/venue_balance_eval.py`, `tune.load` data, 2025/26 fit (6,474 fixtures), 2026/27
check (2,330), paired bootstrap, change in log loss (positive worse), at the live curve and with the
curve refitted per setting (a 1.10, b -0.30 / -0.15).

| f | live curve fit | live curve check | refit fit | refit check |
|---|---|---|---|---|
| 0.5 | +0.0002, p(worse) 0.87 | +0.0003, 0.85 | +0.0001, 0.70 | -0.0006, 0.06 |
| 1.0 | +0.0005, 0.93 | +0.0005, 0.81 | +0.0005, 0.89 | -0.0003, 0.31 |
| 1.5 | +0.0010, 0.97 | +0.0006, 0.74 | +0.0010, 0.97 | +0.0003, 0.63 |

Worse or flat on the fit season at every setting; the f 0.5 refit check gain is the curve moving,
and fit does not agree. Fails the Rule 3 gates. The ratings already carry what the home / away mix
adds, and the later-season tables balance themselves. Rejected; nothing shipped in the model.
