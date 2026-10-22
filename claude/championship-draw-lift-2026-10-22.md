# England Championship: a gap-dependent draw lift (rejected, 22 Oct 2026)

Task (Priya): the one idea the 12 Oct note left untested. The calibration
curve is a function of top-pick confidence only, so it cannot add draw mass
when the sides are close. History only; record.json not read (Rule 1).
Reproduce: `python3 tools/championship_draw_lift.py` (needs network for openfootball).

Method: walk-forward `replay.replay_league` for en.2, raw grid output
(live RHO), then draw x (1 + k x max(0, 0.30 - |p_home - p_away|) / 0.30),
renormalised, then the live curve (1.135 / -0.30). Paired bootstrap, 1500
reps. Negative delta = better.

| Season | n | Live ll | k 0.1 | k 0.2 | k 0.3 | k 0.5 | k 0.8 |
|---|---|---|---|---|---|---|---|
| 2023-24 | 557 | 1.0526 | +0.0011 | +0.0025 | +0.0041 | +0.0078 | +0.0142 |
| 2024-25 | 557 | 1.0346 | -0.0001 | +0.0000 | +0.0005 | +0.0021 | +0.0057 |
| 2025-26 (fit) | 557 | 1.0633 | +0.0012 (p .92) | +0.0027 (p .95) | +0.0044 | +0.0084 | +0.0154 |
| 2026-27 (confirm) | 95 | 1.0895 | -0.0007 (p .38) | -0.0010 (p .40) | -0.0010 (p .44) | -0.0003 | +0.0025 |

Mean predicted draw share v actual: 27.4% v 23.5%, 25.8% v 28.0%, 27.5% v
26.8%, 27.3% v 30.5% (2023-24 to 2026-27). The model already prices the
Championship's draws on average; the 2026-27 shortfall is 95 games of
noise. Lifting draws near-level games costs accuracy and log loss in the two
full seasons with the most data.

Verdict: rejected. On the fit season every k is worse (p(worse) above 0.9);
the only gains are on the 95-game confirm season, 0.001 at best, under the
0.0005-per-250-game evidence bar with p(worse) 0.40. No model number changed.
Do not repeat a draw lift, rho or home advantage test for en.2. Together with
the 5 Oct (newcomers) and 12 Oct (shrink) notes, the Championship's misses
are honest uncertainty: draws and the coin-flip middle, not a mis-set
constant. Remaining untested: team news (the general API-Football result
already rejects it), and nothing league-specific.
