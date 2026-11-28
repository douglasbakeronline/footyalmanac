# Tennis legs in the groups, 38 of 61 v 44.5 expected: fifth read (28 Nov 2026)

Task (HQ planner, 27 Nov): tennis legs in the Odds tab's groups since 19 Oct, 38/61 landed (62%) v 44.5 expected, z -1.9. Find the kind of leg that falls short and replay a rule leaving it out.

## Read
- `groupings-record.json` `cardLegsBySport.tennis` is unchanged since 14 Nov: 41 legs, 23 landed v 29.1 (z -2.13); at today's 75% floor 15 legs, 11 landed v 11.9 (z -0.57). The window is the same population as the reads of 13 Nov (`tennis-legs-gap-2026-11-13.md`), 19 Nov and 26 Nov (`tennis-card-legs-reread-2026-11-26.md`): rule 1 legs before the floors, plus older group kinds.
- The 13 Nov cuts (price gap, round, opposition price, Card rule, time, model band) found no attribute that separates the misses; the bookmakers' implied chance sums as high as the model's, so the market missed by the same amount. Legs from 1 Nov on are on quote.
- Graded tennis overall lands on quote from 70% up, so the model is not over-confident.

## Why no rule was replayed
The pool holds no tennis price history before 30 Oct, so Rule 3 gates (250+ check games, fit and check seasons) cannot be run on a leg rule. Cutting on cells of 8-27 legs read from the scoreboard would be fitting on `record.json` (Rule 1). `CARD_SPORTS_OFF` is not proposed: under 50 legs at the floor.

## Standing
No code change. The tripwire (50 legs at the floor, z -2) decides. The planner's tennis task should read `atFloor`, not the all-legs count.
