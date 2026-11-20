# England Championship: draw signals from expected total goals and a club's own draw rate (rejected, 19 Nov 2026)

Task (Priya): one idea not yet tested for en.2 after the 4 Oct (home advantage,
rho), 5 Oct (newcomers), 12 Oct (shrink), 22 Oct (gap draw lift), 29 Oct
(goals scale) and 11 Nov (own calibration curve) notes. The misses are draws
(about 0.3 log loss each, 27% of games, never the top pick); the 22 Oct lift
keyed on the home/away gap only. Two draw signals not yet used. History only;
record.json not read (Rule 1). Reproduce: `python3 tools/championship_draw_total.py`
(needs network for openfootball).

Method: walk-forward `replay.replay_league` for en.2, live RHO, draw mass
altered on the raw grid output, renormalised, then the live curve (1.135 /
-0.30). Paired bootstrap, 1500 reps; negative delta = better.

- **A, expected total:** draw x max(0.3, 1 + k x (median total - total) / 0.5): low-scoring games draw more.
- **B, club draw rate:** draw x (mean of the two clubs' season-so-far draw
  rate, shrunk to 26.5% with 10 games of weight, over 26.5%)^g. Same-day games not counted.

| Season | n | Live ll | A k 0.1 | A k 0.2 | B g 0.5 | B g 1.0 |
|---|---|---|---|---|---|---|
| 2023-24 | 557 | 1.0526 | +0.0015 (p 0.93) | +0.0037 | -0.0009 (p 0.28) | -0.0004 |
| 2024-25 | 557 | 1.0346 | +0.0020 (p 0.94) | +0.0053 | +0.0003 (p 0.58) | +0.0017 |
| 2025-26 (fit) | 557 | 1.0633 | +0.0016 (p 0.93) | +0.0041 | +0.0023 (p 0.98) | +0.0054 |
| 2026-27 (95 so far) | 95 | 1.0895 | +0.0031 (p 0.93) | +0.0067 | +0.0016 (p 0.71) | +0.0040 |

Verdict: rejected, no model number changed. A is worse in every season at
every strength (p(worse) 0.93 to 0.997): low expected totals do not carry extra
draws the grid and rho have missed. B is worse on the fit season and on the
confirm season, and its one small gain (2023-24, -0.0009) is under the 0.0005
-per-gate bar with p(worse) 0.28 and flips sign next season: a club's draw
rate is not persistent enough within a season to use. Also, 2026-27 has 95
fixtures against the 250 gate.

Together with the earlier six notes: draw mass has now been tried by gap,
total, club tendency and rho, and constants of every kind. Do not repeat a
draw adjustment for en.2. The Championship's misses are the coin-flip middle
and a 27% draw rate; nothing league-specific left to fit from history.
