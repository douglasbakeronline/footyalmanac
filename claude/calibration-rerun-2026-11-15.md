# Calibration by band and sport, rerun (15 Nov 2026, Andrew)

Task: calibration by confidence band for football and by sport for the rest,
from history, bootstrapping the gaps. `python3 calibration_bands.py` (about 2
minutes) already does this, so no code changed. `record.json` was not read
(Rule 1); `calibration.json` and `sports.json` untouched. Gap = landed minus
quoted, 90% bootstrap (2000 resamples). Football = walk-forward replay with
the live curve (a 1.135, b -0.30); sports = `sports.py`'s replay.

What is new since 6 Nov: the football check season is now 2,320 calls (1,557
on 6 Nov), because `tune.load` fills the lagging openfootball fixtures from
the ESPN cache (`claude/replay-check-season-lag-2026-11-15.md`).

## Football

| Band | Check n | Check gap [90%] | Fit n | Fit gap [90%] |
|---|---|---|---|---|
| 55%+ | 451 | +6.7 [+2.9,+10.2] | 1,399 | +2.8 [+0.8,+5.0] |
| 62%+ | 212 | +5.7 [+0.7,+10.6] | 709 | +1.1 [-1.6,+3.8] |
| 70%+ | 68 | +4.0 [-4.2,+11.7] | 313 | +1.1 [-2.8,+5.0] |
| 75%+ | 31 thin | +4.4 [-6.0,+14.6] | 168 | +0.2 [-5.0,+5.1] |
| span 60-70% | 210 | +8.6 [+3.5,+13.5], P(gap<=0) 0.002 | 552 | +2.1 [-1.3,+5.2] |

Pooled (fit part in-sample): 55%+ +3.8 [+2.0,+5.6], 62%+ +2.2, 70%+ +1.6,
75%+ +0.8, span 60-70% +3.9 [+1.0,+6.7]. The 85%+ tail is the one
over-confidence: 38 pooled calls, 65.8% v 88.6%, only 3 in the check season,
so it cannot be confirmed out of sample (it is tiny and the list bar keeps
those picks honest through the tested-rate test).

Reading: the mid band is under-confident on the check season and the gap grew
as the check season filled out (+7.0 on 6 Nov, +8.6 now), but the fit season
is on quote (+2.1, interval spans zero). Rule 3 wants the fit season to
agree, so a refit would not clear the gates, and under-confident is the safe
side. `tune.py --fit` stays the only route to `calibration.json`; it runs
every Monday and needs two consecutive passes. Watch: if the fit season's
mid band moves positive as well, the weekly fit will pick it up by itself.

## Other sports, check window (out of sample), 55+ / 62+ / 70+ / 75+

| Sport | n | Gaps | Reading |
|---|---|---|---|
| NFL | 318 | -1.4 / -3.2 / -5.4 / -3.5 | inside noise |
| Baseball | 3,626 | -1.8 / -0.8 / +2.8 / thin | span 60-70% -3.1 [-6.2,-0.3]; mild over, fit window on quote |
| NBA | 1,322 | +1.8 / +2.1 / +2.2 / +0.6 | calibrated |
| Rugby union | 744 | +2.5 / +1.5 / +2.1 / +1.3 | calibrated; fit window +6 (under-confident) |
| Ice hockey | 1,394 | **-6.1** / **-6.1** / +2.2 / thin | over at 55-70% (span -8.3 [-12.5,-4.3]); fit window was on quote (+0.8-1.4) |
| College football | 1,032 | **+2.5** / **+3.7** / **+3.6** / **+3.1** | conservative, off the list anyway |
| College basketball | 5,814 | **-2.2** / **-2.4** / **-2.1** / **-1.3** | over at 60-70% (-3.4 [-5.6,-1.1]); 85%+ on quote; fit window on quote |
| WNBA | 519 | +1.0 / -1.7 / -2.7 / -4.6 [-9.7,+0.7] | inside noise |
| Rugby league | 296 | +0.5 / -0.4 / +3.7 / thin | calibrated; small |

Reading: unchanged from 6 Nov except that baseball's over-statement has
eased (55%+ -2.9 to -1.8; the 62%+ gap -5.0 to -0.8) and college basketball's
has widened slightly. Ice hockey and college basketball are the two sports
where the check window is clearly under quote and the fit window was not; a
fit-versus-check disagreement is exactly what Rule 3 guards against, so no
refit is proposed. Both are `sports.py --tune` jobs by hand (Rule 5).

## Decision

Report by nature; the evidence does not pass the gates for any change.
Nothing in code, `calibration.json` or `sports.json` moved. Gates: n/a.
