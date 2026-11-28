# Log-space (geometric) rating shrinkage, 28 Nov 2026 (Ben): rejected

Idea not in `tuning-evidence.md`: `engine.strength_from_table` shrinks attack and
defence linearly toward 1.0 (`w*raw + (1-w)`). Tested the geometric version,
`raw**w`, which treats a ratio of 2.0 and 0.5 symmetrically (raw floored at 0.05).

Harness `tools/log_shrink_eval.py` (`tune.load`, `tune.raw_probs`), fit 2025/26
(6,474 fixtures), check 2026/27 (2,496), paired change in log loss against the
shipped model (negative better), 1,000-draw bootstrap p(worse). "Refit" = best
(a, b) on the fit season for that setting.

| Shrink k | Calibration | 2025/26 | 2026/27 |
|---|---|---|---|
| 4 (live k) | live | +0.0002, p 0.88 | +0.0001, 0.60 |
| 4 | refit 1.10 / -0.30 | +0.0002, 0.85 | +0.0002, 0.68 |
| 3 | live | +0.0005, 0.96 | -0.0009, 0.05 |
| 3 | refit 1.15 / -0.30 | +0.0004, 0.96 | +0.0003, 0.75 |
| 6 | live | +0.0003, 0.84 | +0.0024, 1.00 |
| 6 | refit 1.05 / -0.30 | +0.0001, 0.65 | +0.0011, 0.99 |

Never better on the fit season, so no setting clears the gain gate (0.0005) or
Rule 3. The k=3 check-season gain is not backed by the fit season and vanishes
under refit. Rating ratios this close to 1.0 make linear and log shrinkage
nearly identical. Rejected; nothing shipped in the model.
