# Edge over the price, third run (9 Nov 2026)

**Result: no edge, identical to 31 Oct. No value-leg group rule.** Rejected a third time; see `claude/odds-edge-test-2026-10-23.md` and `claude/odds-edge-retest-2026-10-31.md`. Do not run again before the check season has grown (see below).

Method: `tools/odds_edge_test.py` unchanged, bootstrap (2,000 resamples) of mean(hit - fair chance) per cell. Football-data.co.uk average prices, fit 2025-26 (12,510 legs), check 2026-27 (1,749 legs, the same count as 31 Oct: the free file has not grown since). Football only; no free price history exists for other sports. Never `record.json`; no price feeds a model.

| Model minus fair at least | Fit n | Fit gap (pts) | p(<=0) | Check n | Check gap | p(<=0) |
|---|---|---|---|---|---|---|
| 2 pts | 4,188 | -1.8 | 1.00 | 689 | -1.9 | 0.89 |
| 4 pts | 2,539 | -2.1 | 0.99 | 476 | -2.1 | 0.87 |
| 6 pts | 1,510 | -1.5 | 0.92 | 323 | -0.6 | 0.60 |
| 4 pts, model 65%+ | 131 | 0.0 | 0.48 | 11 | +8.7 | 0.26 |
| control: model 4+ below fair | 2,387 | +2.3 | 0.01 | 398 | +1.0 | 0.34 |

Every table cell matches 31 Oct to the decimal. Legs where the model is above the price land below the fair chance on both seasons; legs where the model is below it land above (the market knows more than the model). The only positive cell (65%+) has 11 check legs, far under the 250 gate of Rule 3. Gates: failed, nothing shipped. The 5-point cap on model over market (`MAX_ABOVE_BOOK`) stays.

Re-run only when the check season passes about 3,000 legs (roughly after Christmas) or a free price history for another sport appears.
