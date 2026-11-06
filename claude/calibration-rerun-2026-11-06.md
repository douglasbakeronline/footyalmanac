# Calibration by band and sport, rerun (6 Nov 2026, Andrew)

Task: calibration by confidence band for football and by sport for the rest,
from history, bootstrapping the gaps. `python3 calibration_bands.py` (about 2
minutes) already does this, so no code changed. `record.json` was not read
(Rule 1); `calibration.json` and `sports.json` untouched. Gap = landed minus
quoted, 90% bootstrap (2000 resamples). Football = walk-forward replay with
the live curve (a 1.135, b -0.30); sports = `sports.py`'s replay.

## Football

Check season 1,557 calls (1,523 on 29 Oct).

| Band | Check n | Check gap [90%] |
|---|---|---|
| 55%+ | 306 | +5.7 [+1.3,+10.1] |
| 62%+ | 140 | +2.4 [-3.9,+8.6] |
| 70%+ | 45 | +2.4 [-8.5,+12.2] |
| 75%+ | 20 thin | |
| span 60-70% | 137 | +7.0 [+0.6,+13.2], P(gap<=0) 0.03 |

Fit + check pooled: 55%+ +3.4 [+1.5,+5.2], 62%+ +1.3, 70%+ +1.3, 75%+ -0.3.
Own band 65-70% in the check season: 78.7% landed v 67.4% quoted (n 61).
The 85%+ tail is still the one over-confidence: 37 pooled calls, 64.9% v
88.6%, only 2 in the check season, so it cannot be confirmed out of sample.

Reading: unchanged from 29 Oct. Mid bands run under-confident on the check
season only; the fit season is on quote (60-70% +2.1, interval spans zero),
so Rule 3 is not met and a refit would fail the gates. Under-confident is
the safe side. `tune.py` stays the only route to `calibration.json`.

## Other sports, check window (out of sample), 55+ / 62+ / 70+ / 75+

| Sport | n | Gaps | Reading |
|---|---|---|---|
| NFL | 318 | -1.4 / -3.2 / -5.4 / -3.5 | inside noise |
| Baseball | 3,626 | **-2.9** / **-5.0** / +1.8 / thin | over at 55-70%, fifth check running |
| NBA | 1,322 | +1.8 / +2.1 / +2.2 / +0.6 | calibrated |
| Rugby union | 744 | +2.5 / +1.5 / +2.1 / +1.3 | calibrated |
| Ice hockey | 1,394 | **-6.1** / **-6.1** / +2.2 / thin | over at 55-70% (span -8.3 [-12.5,-4.3]); fit window was on quote (+0.8) |
| College football | 1,032 | **+2.5** / **+3.7** / **+3.6** / **+3.1** | conservative, off the list anyway |
| College basketball | 5,814 | **-1.4** / **-1.8** / -0.6 / -1.1 | over at 60-70% (-4.6 [-6.8,-2.3]); 70%+ inside noise |
| WNBA | 519 | +1.0 / -1.7 / -2.7 / -4.6 [-9.7,+0.7] | inside noise |
| Rugby league | 296 | +0.5 / -0.4 / +3.7 / thin | calibrated; small |

Identical to 29 Oct to within a few calls. Hockey and baseball over-state
55-70% picks; their 70%+ calls are fine, and the list bar (80% tested rate,
`sports.list_threshold`) is set on calls at the pick's own level. Hockey and
baseball refits are `sports.py --tune` jobs by hand (Rule 5), and hockey's
fit window disagrees with its check window, so none is proposed.

## Decision

Report by nature; the evidence does not pass the gates for any change.
Nothing in code, `calibration.json` or `sports.json` moved.
