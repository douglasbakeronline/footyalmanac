# Douglas's mismatch rule against the price (11 Nov 2026, #224)

Douglas, after an 8-fold at 8.16 won (Leicester, Oxford Utd, Plymouth,
Redcar, Salisbury, Cray Wanderers, Curzon Ashton and a tennis leg): back
teams near the top of the table, on a good run, scoring a lot and conceding
little, at home to a side with the opposite on all of those. The question
was never whether these teams win (they mostly do) but whether they win
more often than their price says.

## The rule, fixed on the issue before any result was read

At kick-off, from league matches on earlier dates only (same-day games
never count), in the same league:

- home side: position in the top quarter (position <= teams / 4), 10+ points
  from its last five, goals scored per game in the league's top third,
  conceded per game in the bottom third (it concedes few)
- away side: bottom half (position > teams / 2), 5 or fewer points from its
  last five, scoring in the bottom third, conceding in the top third
- both 6+ league games played; the home win at an average price of 1.15-1.60

"Top third" means fewer than a third of the teams that have played are
strictly better on that rate. The table ranks on points, goal difference,
goals for. Slips take the day's k most likely legs by the bookmakers'
chance, the way `edge_accas` does. Code: `tools/card_legs_history.py`
(`mismatch_legs`, `mismatch_report`, `mismatch_verdict`), tests in
`tests/test_mismatch_rule.py`. Run in CI on 2022-23 to 2026-27
(`card-legs-history.yml` run 42932321819), every football-data league,
the National League included. Douglas's step 3 and 4 clubs (Redcar,
Salisbury, Cray Wanderers, Curzon Ashton) are not in football-data's files,
so that part of his slip is untested.

## The result

| season | legs | landed | bookmakers | return, average | return, best | Edge already flags |
|---|---|---|---|---|---|---|
| 2022-23 | 48 | 83.3% | 73.3% | +7.1% | +10.2% | 7 |
| 2023-24 | 38 | 68.4% | 72.6% | -10.9% | -8.9% | 11 |
| 2024-25 | 40 | 72.5% | 72.1% | -5.1% | -2.9% | 15 |
| 2025-26 | 49 | 67.3% | 71.0% | -11.9% | -9.6% | 13 |
| 2026-27 to date | 10 | 90.0% | 71.7% | +17.5% | +20.5% | 0 |
| **pooled** | **185** | **74.1%** | **72.2%** | **-3.7%** | **-1.2% (p(loss) 0.60)** | **46** |

Ahead of the price in 3 seasons of 5, short of the gate (4 of 5, pooled
p(loss) at the best price 0.30 or less). **The rule does not beat the
price.** Its teams win about three times in four, which is what the
bookmakers already charge for. The 139 legs the Edge flag does not catch do
no better (72.7% v 70.5%, -1.0% at best).

Slips, pooled: singles (the day's most likely leg) 106 of 146, -4.2% at best;
doubles 23 of 35 (65.7% v 52.8% expected), +15.1% at best, p 0.155. Only
35 days in five seasons had two legs, and the doubles' gain comes from the
same legs that lose as singles, so it is variance, not an edge. No day had
four.

## By the home side's games played (Douglas: "the more games in the season the more likely")

| games played | legs | landed | bookmakers | return, best | seasons ahead |
|---|---|---|---|---|---|
| 6-10 | 25 | 68.0% | 70.5% | -7.9% | 1 of 5 |
| 11-20 | 55 | 85.5% | 73.5% | +12.0% (p 0.035) | 4 of 5 |
| 21+ | 105 | 69.5% | 71.9% | -6.6% | 2 of 5 |
| 11+ (the two together) | 160 | 75.0% | 72.4% | about -0.2% | |

The 11-20 band passes the gate on its own. It is not a reason to ship a
flag: it is one band of three, on 55 legs (11 to 15 a season), and the band
after it, with twice the legs, loses in three seasons of five. If season form
made these teams beat their price, 21+ would be the strongest band; it is
the weakest by count. The 11+ band Douglas's comment named does not pass.
The market sharpens as the season goes on at least as fast as the table
does.

## What follows

- No flag, no Card change. The answer for Douglas: these teams win often,
  but no more often than the price already says, so backing them does not
  make money over five seasons.
- The weekly `tune.yml` run re-reads the fit and check seasons
  (`mismatch` in `card-legs-history.json`), so the 11-20 band can be watched
  without building anything. Treat it as confirmed only if it holds on the
  rest of 2026-27 (out of sample from today) at 30+ new legs.
- The rule is rare: about 40 legs a season across 20 divisions, so it could
  never carry a daily accumulator on football-data's leagues alone.
