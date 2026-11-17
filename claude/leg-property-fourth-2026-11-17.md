# Which legs land at their quote? Fourth look, no rule, no change (17 Nov 2026)

**Result: no leg-selection change shipped. A note only: the evidence still cannot reach the Rule 3 gates.**

Not repeated: the football-data scans of 23 and 31 Oct (`leg-property-scan-2026-10-23.md`, `leg-property-rescan-2026-10-31.md`) and the 17 Nov edge retest (`odds-edge-retest-2026-11-17.md`: no cell above fair is positive on both seasons; model-below-market +2.3 / +2.8, which is the same "model at or below market" cut already rejected for removing half the legs).

## What was new: the pool's tested rate

`groupings-archive/pool-*.json.gz`, 22 days. Legs: football, real price (not `est`), not `multOnly`, model 65%+, no draws. Outcomes joined from the ledger (descriptive only, Rule 1; nothing fitted).

- 81 distinct fixtures, 74 settled. Landed 56 (75.7%) against 50.7 expected at min(model, fair) summed (68.5%).
- Tested rate at or above the model: 31 of 47 landed. Tested below the model: 25 of 27. The sign is the opposite of what a tested-rate filter would want, on 27 and 47 legs.
- Celtic's Law is not carried per pool leg, so it still cannot be cut.

74 legs against the 250 Rule 3 needs, one season, no fit/check split possible. Nothing to replay.

## Verdict

Four looks, one answer: the eligible legs land above quote as a group, and no property (sport, tier, tested band, side, price, rating gap) holds on both seasons. Do not rescan before the pool holds 250 settled real-priced football legs; cut tested rate and Celtic's Law then, via `tools/card_replay.py`.
