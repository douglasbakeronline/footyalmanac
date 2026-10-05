# England Premier League: league-specific home advantage (rejected, 5 Oct 2026)

Task (Mia, Experiment Lead): the Premier League (en.1) is the weakest league
with 30+ graded games on the live record (42% over 48, home rate 38%, 15
drawn). History only was used; record.json was not read (Rule 1). Same method
as `championship-test-2026-10-04.md`.

## What the history says

openfootball, live model and live calibration (`tune.live_baseline`),
walk-forward through `replay.replay_league` (prior season = previous one):

| Season | n | Actual H / D / A | Model H / D / A | Log loss | Accuracy |
|---|---|---|---|---|---|
| 2024-25 | 380 | 40.8 / 24.5 / 34.7 | 47.7 / 21.9 / 30.4 | 1.0006 | 51.3% |
| 2025-26 | 380 | 42.6 / 27.4 / 30.0 | 46.2 / 24.1 / 29.8 | 1.0311 | 50.0% |
| 2026-27 so far | 50 | 36.0 / 32.0 / 32.0 | 45.7 / 25.5 / 28.8 | 1.0305 | 42.0% |

The model over-states home wins by 3.6 to 6.9 points and under-states draws
by 2.6 to 3.3 in every season, so the home and draw gaps are real and the
same shape as the Championship. But the 42% is mostly the small sample:
50 games, and the first weeks of a season are the noisiest.

## The change tested

en.1-only home/away tilt (`ha_scale` through `venue_multipliers`; lower
shrinks the home edge and lifts draws). Fit on 2025-26, confirm on 2026-27,
paired bootstrap against the live configuration, Rule 3 gates (>=250 check
fixtures, p(worse) <= 0.30, gain >= 0.0005). 2024-25 is shown as extra
evidence, not a gate.

| ha_scale | 2025-26 (fit) delta / p(worse) | 2026-27 (check, n=50) delta / p(worse) | 2024-25 delta / p(worse) |
|---|---|---|---|
| 0.9 | -0.0005 / 0.29 | -0.0023 / 0.17 | -0.0024 / 0.01 |
| 0.8 | -0.0007 / 0.36 | -0.0043 / 0.18 | -0.0044 / 0.01 |
| 0.7 | -0.0005 / 0.43 | -0.0059 / 0.20 | -0.0059 / 0.03 |
| 0.6 | +0.0001 / 0.51 | -0.0072 / 0.22 | -0.0071 / 0.04 |

## Verdict: rejected, not shipped

- Fit season: the best setting (0.8) gains 0.0007 with p(worse) 0.36, over
  the 0.30 limit. 0.9 passes p(worse) but its gain of 0.0005 only just
  reaches the gain gate.
- Check season: 50 fixtures, far below the 250 minimum, so the confirm gate
  cannot pass. The -0.004 there is noise-wide (sd 0.005).
- Accuracy on the fit season falls (50.0% to 49.2% at 0.8). Picks barely
  move, so it would not lift the hit rate the task is about.
- The earlier season does favour a lower tilt, but one season is not a fit
  and 2025-26 does not agree; the shape looks season-dependent.

Nothing in `engine.py`, `calibration.json` or any constant changed.

## Open for later

Revisit when 2026-27 en.1 has 250+ games (about game-week 25, early 2027),
test ha_scale 0.9 and 0.8 on the then-completed 2025-26 fit and 2026-27
check. A per-league home tilt would also need to work for the other big
leagues (a tier-wide value is what the engine has), so test the top-five
together before adding a per-league key.
