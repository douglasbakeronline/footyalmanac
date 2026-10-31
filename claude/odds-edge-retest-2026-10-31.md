# Edge over the price, re-tested (31 Oct 2026)

**Result: still no edge. Rejected again. No value-leg group rule.** Confirms `claude/odds-edge-test-2026-10-23.md`; do not repeat without a new data source.

Method: `tools/odds_edge_test.py` (unchanged), football-data.co.uk average prices (closing file), fit season 2025-26 (12,510 legs) and check season 2026-27 so far (1,749 legs), model chance as the site quoted it, fair chance with margin removed. Statistic: mean(hit - fair), bootstrapped (2,000 resamples), p(gap<=0) is the chance the true gap is not positive. Never `record.json`; no price feeds a model. Football only (no free history for other sports).

| Model minus fair at least | Fit n | Fit gap | p(<=0) | Check n | Check gap | p(<=0) |
|---|---|---|---|---|---|---|
| 2 pts, all | 4,188 | -1.8 | 1.00 | 689 | -1.9 | 0.89 |
| 4 pts, all | 2,539 | -2.1 | 0.99 | 476 | -2.1 | 0.87 |
| 6 pts, all | 1,510 | -1.5 | 0.92 | 323 | -0.6 | 0.60 |
| 4 pts, model 50%+ | 444 | -2.4 | 0.85 | 41 | -4.5 | 0.73 |
| 4 pts, model 65%+ | 131 | 0.0 | 0.48 | 11 | +8.7 | 0.26 |

By outcome (4+ pts): home -3.0 / -3.2, away -2.6 / -2.7, draw +1.3 / +0.1 (fit / check; draws are not backable as picks and neither is significant). By price (4+ pts): 1.5-2.0 -6.3 / -0.9; 2-3 -2.6 / -8.8; 3-5 -1.9 / -2.0; 5+ -1.5 / +0.8. 1.0-1.5 is +5.2 on fit (n 85, p 0.14) but n 4 on check. Control, model 4+ pts below the market: +2.3 fit (p 0.01), +1.0 check: the market knows more than the model.

Every cell that looks positive is either under 30 legs on the check season or not significant on fit, and none is positive on both seasons. The Rule 3 gate (250+ check fixtures) cannot be met by any positive subgroup. Nothing was fitted or changed. The existing veto (leg chance = min of tested rate, model, fair; model no more than 5 points above the market) stays.

Open: re-run after Christmas when the check season is larger (the 65%+ cell has 11 legs).
