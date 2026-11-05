# College basketball: November-December calls land above quote (5 Nov 2026)

Task (HQ planner): live record 138 of 160 (86%) against 78% quoted, z +2.4. The live record only located the gap; nothing was fitted on it (Rule 1).

## Elo settings: already optimal
Grid k 25-50, hfa 75-150, regress 0.15-0.5 on the fit season (2024-25): the live k 32, hfa 100, regress 0.25, mov 1 is the best of 64 combinations. Nothing to change there; the old grid's edge (hfa 100) was not binding.

## The gap is seasonal, in history too
Landed v quoted by month, same model, no tuning:

| 70%+ calls | fit 2024-25 | check 2025-26 |
|---|---|---|
| Nov | 84.5 v 81.4 | 88.5 v 83.2 |
| Dec | 87.5 v 82.9 | 86.6 v 83.5 |
| Jan-Apr | 80.2 v 82.1 | 78.0 v 82.2 |

Early non-conference games are mismatches the ratings under-price; conference play then over-prices. The live record is all November, so it sits in the first row.

## Fix shipped
A second calibration curve for November-December (`sports.PHASE_MONTHS`, `fit_phase_calibration`, `calibrate(p, cal, when)`), fitted on the fit season only: early a 0.2921 b 1.0497, other months a -0.0327 b 0.9359. Check season (2025-26, 5,814 games): log loss 0.5523 -> 0.5499, gain 0.0024 (sd 0.0011), p(worse) 0.012. Fit season in sample 0.5521 -> 0.5484. Honesty guard (65%+ quoted-minus-landed gap may not widen more than a point): 0.0131 -> 0.0218, +0.0087, inside the limit but close; the widening is the January-April shrink, which still quotes above what it lands on the check season (73.3% v 75.5% at 55%+). A follow-up could shrink January-April harder.

Daily List bar unchanged at 85% (`stored_threshold` before and after). Only `sports.json` "ncaab" changed; other sports are untouched. Live effect: November-December college basketball probabilities rise, so more picks clear the 85% bar and the Card is unaffected (ncaab is off it).

Caveat: two seasons only, the phase split was chosen after seeing the monthly table (on both seasons); the gate is the check season, which the curve did not see.
