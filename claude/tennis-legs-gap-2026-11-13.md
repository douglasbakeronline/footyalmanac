# Tennis legs in the groups: where the gap sits (13 Nov 2026)

Task (HQ planner): tennis legs in the groups 33 of 55 against 40.1 expected. Find the kind of leg that falls short and replay a rule that drops it.

## What the record shows (`groupings-record.json`, every group kind, settled tennis legs, each match once)

109 distinct legs, 71 won, model's own chances sum 84.4 (z about -2.4). By attribute (won / legs, model expected, bookmakers' raw implied):

- Model minus raw implied price: -5 to 0 pts 32/50 (36.1, 37.4); 0 to 5 pts 17/27 (22.6, 22.0); 5+ pts 22/32 (26.4, 24.1). No band is the leak.
- Round 1 32/47 (35.4) v later rounds 39/62 (49.8). Same shortfall.
- Opposition 5.0+ 67/105 (82.1); the other 4 legs are too few.
- Card rule: rule 1 19/34 (23.4), rule 5 6/9, rule 6 5/5, none 40/59 (49.0). All under except the tiny cells.
- By time: 19-24 Oct 40/59 (49.0), 25-31 Oct 20/36 (24.9), 1-13 Nov 11/14 (11.2). The recent legs, after the 85% floor (CARD_RULE 10), are on quote.
- Bookmakers' raw implied sums are as high as the model's (80.3 v 82.1 on opp 5+): the market was wrong by the same amount, so it is not the model leaning on a kind of leg.
- By model band: 65-70% 2/8, 75-80% 15/27; no band monotone, cells of 8-27.

## Why no rule was replayed

No attribute separates the misses, and no tennis price history exists to replay a leg rule on (the pool starts 30 Oct; `claude/tennis-floor-85-2026-11-11.md`). Graded tennis overall lands on quote from 70% up (1,422 picks), so the model is not over-confident; the shortfall sits only in the Card-selected legs and mostly before the 85% floor. Cutting on cells of 8-27 legs would be fitting on the scoreboard (Rule 1). Rule 3 gates cannot be run, so no change shipped.

## Standing

The 85% floor and the tripwire (50 legs, two standard errors under quote; `cardLegsBySport` tennis 23/41, z -2.13, not fired) stay. Revisit when tennis Card legs under rule 10 reach 30 (`tennis75` replay).
