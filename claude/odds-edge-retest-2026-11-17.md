# Edge over the price, fourth run (17 Nov 2026)

**Result: no edge. No value-leg group rule.** Rejected a fourth time (23 Oct, 31 Oct, 9 Nov, now). Gates failed, nothing shipped but this note.

Method: `tools/odds_edge_test.py` unchanged; bootstrap (2,000 resamples, seed 1) of mean(hit - fair chance) per cell. Football-data.co.uk average prices, fit 2025-26 (12,510 legs), check 2026-27 (3,576 legs, up from 1,749 on 9 Nov: the 3,000-leg re-run trigger in the 9 Nov note is met). Football only; no free price history exists for other sports. Never `record.json`; no price feed enters a model.

Gap = landed minus the bookmakers' fair chance, points.

| Cell | Fit n | Fit gap | p(<=0) | Check n | Check gap | p(<=0) |
|---|---|---|---|---|---|---|
| Model above fair by 2+ | 4,188 | -1.8 | 1.00 | 1,460 | -1.8 | 0.95 |
| 4+ | 2,539 | -2.1 | 0.99 | 964 | -1.9 | 0.92 |
| 6+ | 1,510 | -1.5 | 0.92 | 639 | -1.1 | 0.76 |
| 4+, model 65%+ | 131 | 0.0 | 0.49 | 18 | +19.1 | 0.03 |
| 4+, price under 2.0 | 298 | -3.0 | 0.86 | 44 | +2.6 | 0.35 |
| 4+, price 2.0-4.0 | 1,314 | -2.3 | 0.97 | 390 | -2.4 | 0.84 |
| 4+, price 4.0+ | 927 | -1.6 | 0.90 | 530 | -1.9 | 0.87 |
| 4+, home | 1,183 | -3.0 | 0.99 | 380 | -0.5 | 0.58 |
| 4+, draw | 407 | +1.3 | 0.25 | 285 | -2.6 | 0.88 |
| 4+, away | 949 | -2.6 | 0.98 | 299 | -2.9 | 0.91 |
| 4+, model 50-65% | 313 | -3.4 | 0.88 | 59 | -4.2 | 0.75 |
| Control: model 4+ below fair | 2,387 | +2.3 | 0.005 | 831 | +2.8 | 0.05 |

Reading: legs the model rates above the price land below the price on both seasons at every cut by gap, price range, side and band; legs the model rates below the price land above it on both (the market knows more than the model). The one positive check cell (65%+, +19.1) has 18 legs and is 0.0 on 131 fit legs: it fails the 250-leg gate and does not hold across seasons. The 5-point cap on model over market (`MAX_ABOVE_BOOK`) stays.

Other sports: not testable here (no free price history); the pool-based Edge tests are in `claude/edge-sports-2026-11-10.md`.

Next re-run: only if a free price history for another sport appears, or the check season passes ~8,000 legs (about the new year). Do not repeat before.
