# Eredivisie (nl.1) accuracy: tested and rejected, 5 October 2026

Task: nl.1 graded 44% over 43 games (home 30%, 13 drawn out), the weakest league
with 30+ graded games. History only; `record.json` was not used (Rule 1).
Script: replay.replay_league per season, scored under the live calibration with
tune.score_under, paired bootstrap (tune.paired). Data: openfootball, `.tunecache`.

## What the history says

| season | games | home | draw | away | goals/game | model acc | model log loss |
|---|---|---|---|---|---|---|---|
| 2023-24 | 306 | 43.1% | 24.8% | 32.0% | 3.24 | n/a (no prior) | |
| 2024-25 | 306 | 45.4% | 25.2% | 29.4% | 2.99 | 52.6% (prior 2023-24) | 0.9715 |
| 2025-26 | 305 | 44.3% | 26.2% | 29.5% | 3.18 | 50.8% | 0.9854 |
| 2026-27 so far | 63 | 30.2% | 27.0% | 42.9% | 3.81 | 47.6% | 1.0485 |

Over three full seasons the league's home rate is ordinary (44-45%) and the model
is better than its usual league level (log loss 0.97-0.99). The weak 44% on the
live record, and the 30% home rate, are a short run: the 2026-27 season has had
63 games, away wins running at 43% against 29-32% in every earlier season. That
is variance on a small sample, not a structural miss. Draws are the one steady
gap: the model gives ~21-24% per game, nl.1 has drawn 25-26% three years running.

## Tests (paired, bootstrapped, live calibration)

| change | 2023-24 -> 2024-25 (306) | 2024-25 -> 2025-26 (305) | 2025-26 -> 2026-27 (63) |
|---|---|---|---|
| home advantage x0.9 | +0.0003 (worse) | -0.0000 | -0.0078 |
| home advantage x0.8 | +0.0010 (worse, p 0.64) | +0.0004 (worse) | -0.0153 |
| home advantage x0.7 | +0.0021 (worse, p 0.71) | +0.0011 (worse) | -0.0223 |
| home advantage x1.1 | +0.0002 | +0.0004 | +0.0083 |
| RHO -0.12 (more draws) | -0.0014 (p worse 0.18) | -0.0010 (p worse 0.25) | -0.0017 |
| RHO -0.03 / 0.0 | worse | worse | worse |

(negative = better log loss)

## Verdict: nothing shipped

- **Lower home advantage**: worse on both full seasons. It only "wins" on the 63
  games of 2026-27, which is the very sample that created the complaint, so
  fitting to it would be chasing noise. Rejected.
- **More draws (RHO -0.12 for nl.1)**: the only candidate that improves both
  full seasons (about 0.001 log loss, p(worse) 0.18 and 0.25, clearing the
  fit-season gates). But the check season has 63 fixtures against the 250
  required (`MIN_HOLDOUT`), so Rule 3 cannot be satisfied; a per-league RHO
  also adds a structural constant for one league on a gain inside the ±0.005
  noise band. Not shipped. **Revisit when 2026-27 nl.1 reaches 250 games
  (about April 2027)**, and test RHO for all leagues at once rather than for nl.1,
  since the draw under-pricing may be general (the shared RHO is -0.06).
- Accuracy cannot be lifted by either lever: a draw is never the top pick at
  these probabilities, so draw handling moves log loss, not hit rate.

Not changed: engine.py, calibration.json, any constant.
