# Calibration by band and sport, rerun (22 Nov 2026, Andrew)

Task: calibration by confidence band for football and by sport for the rest,
from history, bootstrapped. `python3 calibration_bands.py` (about 3 minutes)
does it; no code changed. `record.json` was not read (Rule 1);
`calibration.json` and `sports.json` untouched. Gap = landed minus quoted, 90%
bootstrap (2000 resamples). Football = walk-forward replay with the live curve
(a 1.135, b -0.30); sports = `sports.py`'s replay. Previous run:
`claude/calibration-rerun-2026-11-15.md`.

## Football (check season 2026-27: 2,396 calls, 811 results filled from ESPN)

| Band | Check n | Check gap [90%] | Fit n | Fit gap [90%] |
|---|---|---|---|---|
| 55%+ | 471 | +6.6 [+3.2,+10.2] | 1,399 | +2.8 [+0.8,+5.0] |
| 62%+ | 223 | +5.4 [+0.7,+10.2] | 709 | +1.1 [-1.6,+3.8] |
| 70%+ | 73 | +2.5 [-4.7,+10.4] | 313 | +1.1 [-2.8,+5.0] |
| 75%+ | 34 | -0.1 [-12.1,+11.5] | 168 | +0.2 [-5.0,+5.1] |
| span 60-70% | 218 | +8.6 [+3.7,+13.5], P(gap<=0) 0.005 | 552 | +2.1 [-1.3,+5.2] |

Pooled: 55%+ +3.8 [+2.1,+5.6]; span 60-70% +3.9 [+1.2,+6.8]. Own bands on the
check season: 65-70% is the one clearly high band (86 calls, 81.4% v 67.5%).
The 85%+ tail is over-confident in the fit season (35 calls, 65.8% v 88.8%,
-23.1 [-37.4,-10.8]) and has only 3 calls in the check season, so it still
cannot be confirmed out of sample.

Reading: same as 15 Nov. The mid band is under-confident on the check season
and on quote on the fit season, so a refit fails Rule 3's two-season
agreement; under-confident is the safe side. The weekly `tune.py --fit`
stays the only route to `calibration.json`.

## Other sports, check window (out of sample), 55+ / 62+ / 70+ / 75+

| Sport | n | Gaps | Reading |
|---|---|---|---|
| NFL | 318 | -1.4 / -3.2 / -5.4 / -3.5 | inside noise |
| Baseball | 3,626 | -1.8 / -0.8 / +2.8 / thin | span 60-70% -3.1 [-6.2,-0.3]; fit window on quote |
| NBA | 1,322 | +1.8 / +2.1 / +2.2 / +0.6 | calibrated |
| Rugby union | 744 | +2.5 / +1.5 / +2.1 / +1.3 | calibrated |
| Ice hockey | 1,394 | -6.1 / -6.1 / +2.2 / thin | over at 55-70% (span -8.3 [-12.5,-4.3]); fit window on quote |
| College football | 1,032 | +2.5 / +3.7 / +3.6 / +3.1 | conservative; off the list |
| College basketball | 5,814 | -2.0 / -2.0 / -1.8 / -1.4 | over at 60-70% (-3.6 [-5.9,-1.4]); 85%+ on quote (+1.0); fit window on quote |
| WNBA | 519 | +1.0 / -1.7 / -2.7 / -4.6 [-9.7,+0.7] | inside noise |
| Rugby league | 296 | +0.5 / -0.4 / +3.7 / thin | calibrated; small |

Reading: unchanged from 15 Nov to within a point. Ice hockey and college
basketball remain the two sports under quote on the check window and on quote
on the fit window; a fit-versus-check split is what Rule 3 guards against, so
no refit is proposed. Both are `sports.py --tune` jobs by hand (Rule 5).
College basketball's weakness is already shown to readers by the Behind .500
mark (`claude/ncaab-early-k-2026-11-16.md`).

## Decision

Report by nature; the evidence fails the gates for any change. Nothing in
code, `calibration.json` or `sports.json` moved. Gates: n/a. Re-run when the
hockey check window passes 2,000 calls or the football 85%+ check tail passes
20 calls.
