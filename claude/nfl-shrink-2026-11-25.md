# NFL confidence shrink (25 November 2026): rejected

Task: lift the weakest of the other sports. Live record (`sports-record.json` bySport, `tennis-record.json`
byTour) at 25 Nov: NFL 73 of 116 (62.9%) v 65.9% quoted, the furthest under quote and still only about
-0.8 standard errors; college football 68.9% v 70.6% (n 424); NBA, rugby, college basketball, ATP and WTA
on or above quote. ATP 55-60% (54% v 57%) is the only other soft band. WTA was handled on 24 Nov
(`tennis-wta-shrink-2026-11-24.md`), college basketball on 16 Nov, so NFL is the one left.

The tuner's own NFL check bands sit 3-5 points under quote from 60% up (65-70%: 71% v 75%), so one
parameter was tested: pull the home probability to 0.5 + (p - 0.5) x s on the live NFL params
(k 20, hfa 50, regress 0.33), paired bootstrap against live on log loss (negative = better):

| s | fit 2024-25 (n 285) | check 2025-26 (n 317) |
|---|---|---|
| 0.80 | +0.0065, p(worse) 0.92 | -0.0007, 0.44 |
| 0.85 | +0.0043, 0.90 | -0.0011, 0.37 |
| 0.90 | +0.0025, 0.86 | -0.0012, 0.31 |
| 0.95 | +0.0010, 0.82 | -0.0008, 0.24 |
| 1.10 | -0.0006, 0.40 | +0.0033, 0.89 |

The fit season wants no shrink (slight sharpening), the check season wants a little, and no setting
clears p(worse) <= 0.30 with gain >= 0.0005 on the check. The sign flips by season, so it is noise, as
the earlier two-parameter calibration (p(worse) 0.80) and the refit of k / hfa / regress (usedFitted False)
also found. Nothing shipped. NFL stays at 80% on the Daily List bar. Revisit with a third NFL season or at
200 live graded picks (116 now).
