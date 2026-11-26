# England Championship: extra flattening early in the season (rejected, 26 Nov 2026)

Task (Priya): one idea not yet tested for en.2 after the 4 Oct (home advantage,
rho), 5 Oct (newcomers), 12 Oct (shrink), 22 Oct (draw lift), 29 Oct (goals
scale), 11 Nov (own curve) and 19 Nov (draw signals) notes. The 5 Oct breakdown
showed early season as a weak spot in 2025-26 (both sides under 8 games: ll
1.145, 31% accuracy). Idea: the live curve is a function of top-pick confidence
only, so add a temperature k on top of it when the less-played side has fewer
than N games. History only; record.json not read (Rule 1). Reproduce:
`python3 tools/championship_early_temper.py` (needs network for openfootball).

Walk-forward `replay.replay_league` for en.2, live RHO, live curve (now
1.085 - 0.20 x (conf - 0.45)); games played counted before the match date only.
Paired bootstrap, 1500 reps, negative delta = better. Early (<8) fixtures are
about 96 a season; 2026-27 has 95 fixtures in all, every one of them early.

| Early ll (live) | 2023-24 | 2024-25 | 2025-26 | 2026-27 |
|---|---|---|---|---|
| Early (<8 games) | 1.0789 | 1.0156 | 1.1483 | 1.0907 |
| Whole season | 1.0531 | 1.0349 | 1.0639 | 1.0907 |

Delta v live (p(worse)) for N 8:

| Season | k 0.1 | k 0.2 | k 0.4 |
|---|---|---|---|
| 2023-24 | -0.0003 (.27) | -0.0004 (.30) | -0.0005 (.35) |
| 2024-25 | +0.0005 (.87) | +0.0010 (.89) | +0.0020 (.92) |
| 2025-26 (fit) | -0.0013 (.00) | -0.0022 (.00) | -0.0037 (.00) |
| 2026-27 (confirm, 95) | -0.0020 (.20) | -0.0032 (.24) | -0.0045 (.28) |

Best on the fit season: N 8, k 0.4 (+0.0037). N 4, 6 and 10 show the same shape
at smaller size; 2024-25 is worse for every N and k at p(worse) 0.68 to 0.92.

Verdict: rejected, no model number changed. The fit season passes the gain and
p(worse) bars, but (a) 2025-26's early window is the one bad early window of
three completed seasons, 2024-25 had the best early window (1.016) and this
makes it worse, which is what a fit to one season's noise looks like; (b) the
confirm season has 95 fixtures against the 250 gate (`enoughData` fails), its
p(worse) 0.20 to 0.28 is a lean, not evidence. Revisit when 2026-27 has 250+
Championship fixtures (about January) AND 2026-27's early window (95 games,
ll 1.091, near 2025-26's) is read for a stage-of-season effect again; a second
completed season with a bad early window would change the answer, the pooled
2023-26 sign being only 2 in 3. Do not repeat a league-wide early-season
temperature for en.2 before then.
