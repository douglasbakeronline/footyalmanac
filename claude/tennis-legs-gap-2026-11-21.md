# Tennis legs in the groups, 36 of 59 v 43 expected: fourth read (21 Nov 2026)

Task (HQ planner, 20 Nov): tennis legs in the Odds tab's groups since 19 Oct, 36 of 59 (61%) v 42.9 quoted (73%), z -2.0. Find the kind of leg and replay a rule that leaves it out.

## Already answered

- `claude/tennis-legs-gap-2026-10-30.md`, `-11-06.md`, `-11-13.md` and `claude/tennis-card-legs-recheck-2026-11-19.md` cut these same legs by model band, price, gap to the market, round, tour, side, opposition price and Card rule. No cut separates the misses; every cell is 8-50 legs (standard error 8-15 points); the bookmakers' own implied chance sums as high as the model's.
- The shortfall is mostly legs built before the 29 Oct 75% floor (rule 1: 19 of 34); 1-13 Nov legs were on quote (11 of 14). The planner's 59 legs are the same population plus a handful, so this is not new evidence.
- Graded tennis overall lands on quote from 70% up (1,422 picks); the model is not over-confident, the shortfall sits in the Card-selected legs.

## Why no rule was replayed

No tennis price history exists (the pool starts 30 Oct), so a leg rule on price, gap or opposition cannot be replayed on history under the Rule 3 gates (250+ check games, p(worse) <= 0.30, gain >= 0.0005). A model-only floor is already live (`CARD_SPORT_MIN` tennis 0.75) and tested on the graded record. Choosing a cut from 59 live legs would be fitting on the scoreboard (Rule 1).

## Standing

No code change. The tripwire decides: `cardLegsBySport.tennis` `atFloor` (75%+ on model and tested rate) 11 of 15, z -0.57 at the last read, against the 50-leg bar. Do not re-run this task until at-floor legs reach 30 or a tennis price history of 250+ matches exists.
