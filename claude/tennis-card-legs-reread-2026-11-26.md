# Card tennis legs, 8 of 15 v 12 expected: third read (26 Nov 2026)

Task (HQ planner, 25 Nov): the same 15-leg window as 18 Nov (`claude/tennis-card-legs-recheck-2026-11-19.md`), same z -2.1.

## Record at 26 Nov (`groupings-record.json` `cardLegsBySport.tennis`)

- All legs: 41, 23 landed, 29.1 expected (56% v 71%, z -2.13). Unchanged since 14 Nov: no tennis Card leg added.
- Legs at today's 75% floor (`atFloor`): 15, 11 landed, 11.9 expected (73% v 79%, z -0.57). Tripwire needs 50+ legs at the floor and z of -2 or worse: not fired.
- The planner's "8 of 15" is the pre-floor population again (the shortfall is rule 1 legs before 29 Oct to 11 Nov), not new evidence.

## Why no rule was replayed

The cuts asked for (competition, price, side, opposition price) were read on 13 Nov (`claude/tennis-legs-gap-2026-11-13.md`): no attribute separates the misses, the market's implied chance sums as high as the model's, and the pool has no tennis price history before 30 Oct to run Rule 3 gates on. Cutting on cells of 8-27 legs would be fitting on the scoreboard (Rule 1). `CARD_SPORTS_OFF` is not proposed: under 50 legs at the floor, and graded tennis overall lands on quote from 70% up.

## Standing

No code change. The tripwire, not this note, decides. Planner suggestion: its tennis task should read `atFloor`, not the all-legs count, or it will re-raise this until a tennis Card leg lands.
