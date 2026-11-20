# Card tennis legs, 8 of 15 v 12 expected: re-read (19 Nov 2026)

Task (HQ planner, 18 Nov): tennis Card legs since 29 Oct 8 of 15 (53%) v 11.5 expected, z -2.1; find the kind of leg and replay a rule, or propose `CARD_SPORTS_OFF`.

## What the record says now (`groupings-record.json` `cardLegsBySport.tennis`)

- 41 legs, 23 landed, 29.1 expected (56% v 71%, z -2.13). Unchanged since 14 Nov: no tennis leg has been added.
- Legs the live floor admits (`atFloor`, 85%+ on model and tested rate): 0. Every settled tennis leg ran under a rule with no 85% floor (30 under rule 1, `claude/card-tripwire-at-floor-2026-11-14.md`).
- The planner's 15-leg window sits inside those 41 legs, so it is the same pre-floor population, not new evidence.

## Why no rule was replayed

The cuts asked for (competition, price, side, opposition price) were read on 13 Nov (`claude/tennis-legs-gap-2026-11-13.md`): no attribute separates the misses, the market's own implied chance sums as high as the model's, and no tennis price history exists to replay a leg rule on (pool starts 30 Oct). Cells of 8-27 legs would be fitting on the scoreboard (Rule 1); the Rule 3 gates cannot be run.

`CARD_SPORTS_OFF` is not proposed: the tripwire needs 50+ legs at the floor and there are none, and graded tennis overall lands on quote from 70% up. The 85% floor (`CARD_RULE` 10) is the standing treatment.

## Standing

No code change. Re-read when tennis Card legs at 85%+ reach 30 (`tennis75` replay), or at the 30 Nov review.

## Later the same day (20 Nov 2026, build session)

Rule 14 (19 Nov 2026) put the tennis floor back to 75% (`CARD_SPORT_MIN`), so `atFloor` now counts legs at 75%+: the 19 Nov Card review reads 15 such legs, z -0.57, against the 50-leg tripwire. The reasoning above (no attribute separates the misses, no replay possible) stands; the tripwire, not this note, decides.
