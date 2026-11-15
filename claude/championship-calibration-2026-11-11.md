# England Championship: a league-specific calibration curve (rejected, 11 Nov 2026)

Task (Priya): one idea not yet tested for en.2 after the 4 Oct (home advantage,
rho), 5 Oct (newcomers), 12 Oct (shrink), 22 Oct (draw lift) and 29 Oct (goals
scale) notes. Idea: the live curve `T = 1.135 - 0.30 x (confidence - 0.45)` is
fitted across the core leagues; the Championship, the most even league, may
want its own (a, b), i.e. be less confident at every level. History only;
record.json not read (Rule 1). Reproduce:
`python3 tools/championship_calibration.py` (needs network for openfootball).

Where the misses are (from the 5 Oct breakdown, unchanged): promoted or
relegated sides are not consistently worse, early season was bad in 2025-26
only, big-gap games are fine (ll about 1.0), small-gap games and draws carry
the loss. So a flat shift in confidence is the one lever left that the
earlier tests did not touch.

Method: walk-forward `replay.replay_league` for en.2, live RHO, grid over
a in 0.9-1.5 and b in -0.6 to +0.3 (48 curves), best on the fit season
2025-26, then confirmed on 2026-27 and shown on the two earlier seasons.
Paired bootstrap, 1500 reps, negative delta = better.

| Season | n | Live ll | Best curve (a 1.3, b -0.6) delta | p(worse) |
|---|---|---|---|---|
| 2023-24 | 557 | 1.0526 | -0.0007 | 0.330 |
| 2024-25 | 557 | 1.0346 | +0.0000 | 0.529 |
| 2025-26 (fit) | 557 | 1.0633 | -0.0011 | 0.201 |
| 2026-27 (confirm) | 95 | 1.0895 | -0.0026 | 0.201 |

Surface: below a 1.135 (more confident) is worse everywhere, by up to 0.008;
above it (flatter, less confident) gains 0.0005-0.0011 on 2025-26, nothing on
2024-25 (a 1.3 is +0.0006 to +0.0013 worse at b -0.3 to 0) and 0.002-0.003 on
2026-27. So the direction (Championship picks should be somewhat less
confident) is consistent on three seasons of four, but the size is not stable.

Verdict: rejected, no model number changed. The fit-season gain (0.0011)
clears the 0.0005 gain bar and p(worse) 0.20 clears 0.30, but the confirm
season has 95 fixtures against the 250 gate (`enoughData` fails), 2024-25
shows no gain at the chosen curve, and the effect on the one season that
matters for the list (Lean-and-above picks) is nil: the Championship rarely
reaches the bar. A league-specific curve would also need new plumbing in
`engine.temper` and a second calibration file, a structural change (Rule 5)
for 0.001 log loss.

Revisit when 2026-27 has 250+ Championship fixtures (about December): rerun
the tool; if the confirm delta is at least 0.0005 better with p(worse) at most
0.30 and 2024-25 is not worse, the one-parameter version (a +0.15 for en.2
only) is the candidate, wired through `home-advantage.json`-style per-league
config rather than a second curve.

Together with the five earlier notes: the Championship's misses are honest
uncertainty, draws and the coin-flip middle. Do not repeat a constant sweep
for en.2 without a new data source.
