# England Championship: a total-goals scale (rejected, 29 Oct 2026)

Task (Priya): one untested idea for en.2 after the 4 Oct (home advantage, rho),
5 Oct (newcomers), 12 Oct (shrink) and 22 Oct (draw lift) notes. Idea: the
model's predicted goals per game miss the Championship's actual level, so scale
both expected-goal rates by one constant. History only; record.json not read
(Rule 1). Reproduce: `python3 tools/championship_goals_scale.py` (needs network).

Walk-forward `replay.replay_league`, live RHO, live curve (1.135 / -0.30),
paired bootstrap, negative delta = better.

| Season | n | Live ll | Predicted v actual goals | x0.90 | x0.95 | x1.05 | x1.10 |
|---|---|---|---|---|---|---|---|
| 2023-24 | 557 | 1.0526 | 2.47 v 2.67 | +0.0041 | +0.0018 | -0.0013 (p .04) | -0.0022 (p .06) |
| 2024-25 | 557 | 1.0346 | 2.70 v 2.45 | -0.0003 | -0.0004 | +0.0007 | +0.0017 |
| 2025-26 (fit) | 557 | 1.0633 | 2.49 v 2.59 | +0.0013 | +0.0005 | -0.0001 (p .47) | +0.0002 |
| 2026-27 (confirm) | 95 | 1.0895 | 2.58 v 2.92 | -0.0017 | -0.0010 | +0.0013 | +0.0027 |

The league's goal level swings 2.45 to 2.92 a season and the model is under in
some seasons and over in others, so no single constant helps. On the fit season
the best scale gains 0.0001 (gate 0.0005, p(worse) 0.47), and the confirm season
prefers the opposite direction to 2023-24. Accuracy is unchanged in every cell
(total goals barely moves the pick).

Verdict: rejected, no model number changed. Do not repeat a en.2 goal-level
scale. Together with the earlier four notes: the Championship's misses are the
coin-flip middle and draws, not a mis-set constant of any kind tried so far.
