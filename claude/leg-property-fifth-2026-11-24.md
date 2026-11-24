# Which legs land at their quote? Fifth look, no rule, no change (24 Nov 2026)

**Result: no leg-selection change shipped. A note only: the pool still holds under the 250 settled legs the Rule 3 gates need.**

Not repeated: the football-data scans (`leg-property-scan-2026-10-23.md`, `leg-property-rescan-2026-10-31.md`), the edge retests (latest `odds-edge-retest-2026-11-24.md`: no cell above fair positive on both seasons) and the fourth look (`leg-property-fourth-2026-11-17.md`).

## Pool read (29 daily files from 30 Oct)

Legs: football, real price (not `est`), not `multOnly`, no draws, model 65%+. 105 distinct fixtures, 98 settled in the results ledger (read descriptively, Rule 1; nothing fitted).

- Landed 76 (77.6%) against 66.5 expected at min(model, tested, implied) (67.9%). The eligible legs land above quote as a group.
- Tested rate at or above the model: 45 of 64 landed (42.4 expected). Tested below the model: 31 of 34 (24.1 expected). Same direction as 17 Nov (the tested-below cell lands better), the opposite of what a tested-rate filter would want, on 34 legs.
- Celtic's Law is still not carried per pool leg, so it cannot be cut.

98 legs, one window, no fit/check split: the 250-leg gate cannot be met and a replay would be noise. The "no more than a fifth of legs lost" condition is moot with no rule to test.

## Verdict

Five looks, one answer: no property (sport, tier, tested band, side, price, rating gap) holds on both seasons, and the pool is too small to add Celtic's Law or tested rate. Rescan when the pool holds 250 settled real-priced football legs (about 3 more weeks at this rate), via `tools/card_replay.py`.
