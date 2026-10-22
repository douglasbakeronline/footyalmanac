# Tennis below its expected hit rate: checked, noise, surface weight kept (22 Oct 2026)

Trigger: tennis record 61.0% (505 of 828) against 62.7% expected.

## Is the gap real?

No. Binomial z on the quoted confidences (`tennis-record.json`, voids excluded):

| Group | n | landed | quoted | z |
|---|---|---|---|---|
| All | 828 | 61.0% | 62.7% | -1.03 |
| ATP | 324 | 61.7% | 62.6% | -0.32 |
| WTA | 504 | 60.5% | 62.7% | -1.06 |
| WTA, September | 116 | 51.7% | 58.3% | -1.46 |
| 70%+ calls | 183 | 73.2% | 78.0% | -1.57 |
| 70-80% calls | 122 | 68.0% | 74.1% | -1.52 |
| Below 60% | 401 | 53.4% | 54.6% | -0.51 |
| October, both tours | 635 | 61.9% | 63.6% | -0.94 |

Every cut is about one standard error under quote; none reaches 2. The 80%+
band (61 calls) landed 83.6% v 85.8% quoted. Main draw 60.2% v 63.0%,
qualifying 63.6% v 61.8%. Direction is consistent (a small over-statement),
so it is worth watching, not acting on. WTA September, before the 8 Oct ratings
fix (`tennis-ratings-gap-2026-10-08.md`), is the weakest slice.

## Surface: cannot be checked on the live record

ESPN carries no surface, and `build_tennis.py` prices and archives every live
match as "Hard". The `surface` field in `predictions-tennis/` is therefore
always Hard, so the record cannot be cut by surface. The window (23 Sep to 22
Oct) is almost all hard court (Asian swing, European indoors), so surface
mislabelling is unlikely to explain the gap. It will matter from clay season.

## Surface weighting, tested (tune_tennis.py method)

`run_elo` on the Sackmann mirror (tour-level, 2026 check set, never used to
choose constants), keeping live k_base and retirement weight, varying
`surface_weight`. Delta is log loss against the live 0.3 (positive = worse):

| surface_weight | ATP 2025 | ATP 2026 delta (p worse) | WTA 2025 | WTA 2026 delta (p worse) |
|---|---|---|---|---|
| 0 | .6222 | +.0048 (.98) | .6118 | +.0016 (.72) |
| 0.2 | .6176 | +.0007 (.82) | .6110 | -.0005 (.28) |
| **0.3 (live)** | .6166 | 0 | .6117 | 0 |
| 0.4 | .6165 | +.0002 (.58) | .6133 | +.0015 (.96) |
| 0.5 | .6173 | +.0012 (.78) | .6156 | +.0041 (.99) |
| 0.7 | .6216 | +.0060 (.97) | .6227 | +.0125 (1.0) |
| 1.0 | .6348 | +.0197 (1.0) | .6394 | +.0328 (1.0) |

The optimum is flat around 0.2-0.4. WTA 0.2 is -0.0005 (p worse 0.28), well
under the 0.005 tennis gain bar (`MIN_GAIN`); not a result. The offline check-set accuracy is 66.0%
(ATP, n=1,437) and 68.0% (WTA, n=1,286), higher than live because the live
board includes qualifying and lower-level matches, ESPN-only results and the
confidence shrink. Surface weighting is not the cause of the live gap.

## Decision

No code or constant changed. Rejected: re-weighting surface (nothing passes
either tour). Do not reopen without a surface source for live results.
Revisit the live gap at ~1,500 graded matches; if it still sits at 2 SE under
quote, look at `CONFIDENCE_SHRINK` (0.9 ATP, 0.95 WTA) on the walk, not on the
record (rule 1).
