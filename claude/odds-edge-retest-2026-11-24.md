# Edge over the price, fifth run (24 Nov 2026)

**Result: no edge. No value-leg group rule.** Rejected a fifth time (23 Oct, 31 Oct, 9 Nov, 17 Nov, now). Gates failed; only this note shipped.

Method as 17 Nov: `tools/odds_edge_test.py` unchanged (football-data.co.uk average prices; fit 2025-26, 12,510 legs; check 2026-27, 3,861 legs, up from 3,576), bootstrap of mean(hit - fair chance), 2,000 resamples, seed 1. Football only (no free price history for other sports). Never `record.json`; no price enters a model. Gap = landed minus the bookmakers' fair chance, points.

| Cell | Fit n | Fit gap | p(<=0) | Check n | Check gap | p(<=0) |
|---|---|---|---|---|---|---|
| Model above fair by 2+ | 4,120 | -1.5 | 0.99 | 1,523 | -1.4 | 0.92 |
| 4+ | 2,555 | -2.1 | 0.99 | 1,013 | -1.6 | 0.88 |
| 6+ | 1,555 | -1.5 | 0.90 | 675 | -1.0 | 0.74 |
| 4+, model 65%+ | 157 | +0.1 | 0.47 | 20 | +21.2 | 0.01 |
| 4+, price under 2.0 | 355 | -2.2 | 0.80 | 53 | +2.7 | 0.35 |
| 4+, price 2.0-4.0 | 1,342 | -2.5 | 0.98 | 407 | -1.2 | 0.71 |
| 4+, price 4.0+ | 858 | -1.2 | 0.84 | 553 | -2.2 | 0.92 |
| 4+, home | 1,255 | -2.9 | 0.99 | 410 | +0.4 | 0.41 |
| 4+, draw | 364 | +1.6 | 0.25 | 292 | -3.1 | 0.92 |
| 4+, away | 936 | -2.3 | 0.96 | 311 | -2.7 | 0.88 |
| 4+, model 50-65% | 376 | -3.0 | 0.88 | 78 | -2.3 | 0.68 |
| Control: model 4+ below fair | 2,353 | +2.3 | 0.01 | 884 | +2.3 | 0.07 |

Reading: legs the model rates above the price land below it on both seasons at every cut that has the sample; legs it rates below the price land above it on both. The one positive check cell (65%+, +21.2) has 20 legs and +0.1 on 157 fit legs: under the 250-leg gate and not consistent across seasons. The 5-point cap `MAX_ABOVE_BOOK` stays. Sports other than football: see `claude/edge-sports-2026-11-10.md` (pool).

Do not repeat before the check season passes ~8,000 legs or a free price history for another sport appears.
