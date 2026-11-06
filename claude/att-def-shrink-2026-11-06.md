# Test, 6 November 2026: separate shrinkage for attack and defence (Ben)

Idea not tested before: `strength_from_table` shrinks attack and defence by
the same `SHRINK_FULL_SEASON` (4). Defence is often called the noisier half,
so a larger k for defence (or smaller for attack) might help.

Method: `tools/att_def_shrink_eval.py`. Frozen fetch via `tune.load`, 2025/26
fit (6,474 fixtures), 2026/27 check (1,557). Paired change in log loss
against the shipped model under the live curve (negative better), 1,000-draw
bootstrap, p(worse) beside it. "Refit" picks the best (a, b) on the fit season
for that setting and applies it to the check (rule 4).

| att k / def k | live: fit | live: check | refit: fit | refit: check |
|---|---|---|---|---|
| 4 / 6 | -0.0001, 0.26 | +0.0006, 0.93 | -0.0003, 0.07 | 0.0000, 0.48 |
| 4 / 8 | 0.0000, 0.48 | +0.0012, 0.95 | -0.0005, 0.08 | +0.0003, 0.66 |
| 4 / 12 | +0.0004, 0.76 | +0.0023, 0.97 | -0.0004, 0.25 | +0.0009, 0.80 |
| 4 / 2 | +0.0006, 0.99 | -0.0008, 0.13 | +0.0006, 0.99 | -0.0007, 0.13 |
| 2 / 4 | 0.0000, 0.53 | -0.0001, 0.46 | 0.0000, 0.55 | 0.0000, 0.52 |
| 3 / 4 | -0.0001, 0.32 | -0.0001, 0.33 | -0.0001, 0.37 | -0.0001, 0.37 |
| 6 / 4 | +0.0004, 0.97 | +0.0005, 0.87 | +0.0002, 0.78 | -0.0001, 0.40 |
| 8 / 4 | +0.0009, 0.99 | +0.0011, 0.92 | +0.0005, 0.93 | +0.0001, 0.55 |
| 2 / 8 | -0.0002, 0.32 | +0.0010, 0.87 | -0.0003, 0.24 | +0.0007, 0.78 |

No setting passes the gates (gain >= 0.0005, p(worse) <= 0.30) on both
seasons. The only fit-season gain at the bar (4 / 8 refit, -0.0005) is
slightly worse on the check season. Attack and defence want the same
shrinkage; the single constant is already right. Rejected; nothing shipped.
