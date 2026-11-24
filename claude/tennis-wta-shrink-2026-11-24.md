# WTA confidence shrink 0.95 to 1.0 (24 November 2026)

HQ planner task: WTA live calls 244 of 349 (70%) v 229.9 quoted (66%), z +1.6. The surface idea
is closed (five checks, last `tennis-surface-fifth-check-2026-11-24.md`: no free surface column,
the map was rejected, every event since 18 Oct is hard court anyway). The planner's own advice was
to try something else on history, so this tests the confidence shrink (`build_tennis.CONFIDENCE_SHRINK`).

## Test (history, never the live record)
Walk-forward on the Sackmann mirror plus extras (`tools/tennis_bands.py` machinery, live constants
sw 0.3, k 250, retirement 0.5), the favourite's probability pulled to 0.5 + (p - 0.5) x shrink.
Paired bootstrap against the live 0.95, log loss (negative = better):

| shrink | 2025 fit (n 2,674) | 2026 check (n 1,286) |
|---|---|---|
| 1.0 | -0.0010, p(worse) 0.010 | -0.0018, p(worse) 0.001 |
| 1.05 | -0.0015, 0.046 | -0.0031, 0.009 |
| 1.1 | -0.0013, 0.182 | -0.0039, 0.025 |

Every 2026 WTA band from 55% up lands above its quote at shrink 1.0 (65-70%: 80.3% v 75.6%;
70-75%: 83.1% v 79.1%). The 2025 best on the old grid (0.8 to 1.0) was already its top edge, 1.0.

## Decision
WTA shrink set to 1.0 (no shrink). Chosen as the conservative step: the sharpening values 1.05 and
1.1 are better on 2026 but 1.1 fails p(worse) on the fit season, so nothing above 1.0 is shipped.
Passes Rule 3 (250+ check games, p(worse) <= 0.30, gain >= 0.0005). It does NOT reach
`tune_tennis.MIN_GAIN` 0.005, the tennis-only bar; the original 0.95 also shipped under 0.005.
ATP untouched (0.9, best 0.95 on 2025 but the ATP live record is not off). Quoted WTA confidences
rise by about 0.8 points on average; the Card's 75% / 85% tennis floors and the list bars read the
new numbers, so slightly more WTA picks clear them. Tennis stays off the list as before.

Roll back: `CONFIDENCE_SHRINK["wta"] = 0.95`.
