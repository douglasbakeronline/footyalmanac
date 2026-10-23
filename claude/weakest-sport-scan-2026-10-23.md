# Weakest sport scan, 23 Oct 2026 (Theo) — no change shipped

Live records, read-only, nothing fitted on them (Rule 1).

| Segment | n | Landed | Quoted | Gap | z |
|---|---|---|---|---|---|
| NFL (all graded) | 47 | 57.5% | 64.0% | -6.5 | -0.9 |
| College football | 124 | 65.3% | 69.3% | -4.0 | -1.0 |
| Tennis Strong tier (70%+) | 189 | 74.1% | 78.1% | -4.0 | -1.3 |
| WTA main draw 70%+ | 88 | 70.5% | 77.8% | -7.3 | -1.6 |
| ATP main draw 70%+ | 67 | 76.1% | 77.6% | -1.5 | -0.3 |
| WTA qualifying 70%+ | 25 | 72.0% | 80.3% | -8.3 | small n |

No segment is beyond 2 sigma. NFL has the biggest gap but 47 games; its
tuning check (332 games) shows 70%+ calls landing at or above quote and a
calibration curve that fails the gate (delta +0.0038, p(worse) 0.80).
Tennis was tested on the archive: 75%+ landed 84.6-86.4% for WTA, and the
shrink under-quotes there. Tightening the WTA shrink to match the live gap
would contradict that out-of-time evidence, and fitting it to the live gap
would be tuning on the scoreboard. Only the live list/Strong gap suggests the
archive-to-live difference (ESPN results as hard court, four-month ratings
gap fixed 8 Oct) is the cause, not the shrink constant.

Recommendation: revisit WTA when the 70%+ main-draw sample passes ~200 and
test a shrink change by replay on `history-tennis/` ESPN results, not the
record. Nothing shipped.
