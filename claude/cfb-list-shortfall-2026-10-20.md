# College football Daily List: 30 of 41 against 33.6 expected (20 Oct 2026)

Theo, from the HQ planner. The planner's gap is real but was already acted on:
the bar went 70% -> 80% on 13 Oct (`sports.LIST_FLOOR`) and college football
came off the List on 19 Oct (`sports.LIST_OFF`). Nothing on the List to fix.

## Where the shortfall sits (live record, used only to locate it, Rule 1)

41 List picks, 30 landed (73.2%), 33.6 expected (82.0% quoted).

| Cut | n | landed | quoted |
|---|---|---|---|
| 70-75% | 10 | 6 (60%) | 73% |
| 75-80% | 7 | 5 (71%) | 77% |
| 80-85% | 11 | 8 (73%) | 83% |
| 85-90% | 6 | 5 (83%) | 87% |
| 90-95% | 6 | 5 (83%) | 93% |
| 95%+ | 1 | 1 | 95% |
| Home pick | 31 | 23 (74%) | 84% |
| Away pick | 10 | 7 (70%) | 77% |
| Before 13 Oct (70% bar) | 29 | 21 (72%) | 80% |
| 13 Oct on (80% bar) | 12 | 9 (75%) | 87% |

Every band lands under its quote by 4 to 11 points; no single band, side or
period carries it. Home v away is not separable at these sizes. Games played
are not informative (every pick had 40+ rated games). The one neutral-site pick
lost. The gap is a uniform offset of about 8 points, which at n=41 is
z -1.5: not distinguishable from bad luck on its own.

## Suspect: cumulative tested rate on rows

Real but not the cause of the miss. Rows showed 84-93% "tested" while the picks
were quoted 73-95%, so the shown rate overstates a 70-75% pick by about 11
points. History's own bands (13 Oct, `RELEASES.md`) already showed 70-80%
landing 71-78%; that is why the bar rose. Own-band rates would be stricter and
would read 71-78% for those rows. Not changed: the row is off the List now, and
the rate display is Douglas's call (open item in `CLAUDE.md`).

## Would a stricter rule have landed 80%?

Live, 80%+ only: 19 of 25 (76%) against 86% quoted. Even the 80% bar missed, so
a still-higher bar is not supported: 85%+ is 11 of 13 (85%), n too small to fit
anything, and fitting on this record is barred.

## Decision

No model or admission change. Probabilities unchanged. The pick set is already
off the List; the sports backtest (fit/check 80-85%: 87.7% / 87.4%) disagrees
with the live 73% for that band (8 of 11), and 11 games does not overturn
1,000+ of history. Return condition stands: put `cfb` back in `LIST_OFF` only
when its live record holds. Re-check once there are about 100 graded 80%+ picks
(reserve picks count for this: the reserve is graded as its own group).
