# Calibration by band and sport, rerun (29 Oct 2026, Andrew)

Task: calibration by confidence band for football and by sport for the rest,
from history, bootstrapping the gaps. `python3 calibration_bands.py` already
does this (5, 7, 12, 22 Oct), so no code changed: this is the 7-day refresh
on the same method. `record.json` was not read (Rule 1); `calibration.json`
and `sports.json` untouched. Gap = landed minus quoted, 90% bootstrap
(2000 resamples of calls). Football = walk-forward replay with the live curve
(a 1.135, b -0.30); sports = `sports.py`'s replay with `sports.json`.

## Football

Fit season 6,474 calls (in-sample), check season 1,523 (was 1,491 on 22 Oct).

| Band | Fit gap [90%] | Check n | Check gap [90%] |
|---|---|---|---|
| 55%+ | +1.7 [-0.2,+3.7] | 322 | +3.1 [-1.1,+7.5] |
| 62%+ | -0.4 [-3.1,+2.1] | 152 | +5.3 [-0.7,+11.2] |
| 70%+ | +0.5 [-3.1,+4.2] | 55 | +2.9 [-6.7,+12.3] |
| 75%+ | -1.8 [-6.5,+3.1] | 20 thin | |
| 85%+ | **-19.6 [-32.4,-7.0]** (88.8 v 69.2) | 2 thin | |
| span 60-70% | +0.6 [-2.5,+3.9] | 136 | **+7.9 [+1.3,+14.2]**, P(gap<=0) 0.03 |

- Same picture as 22 Oct, no movement beyond one more week of data. Every
  cumulative bar from 55% to 80% is inside its interval on the fit season.
- The check-season 60-70% under-confidence persists (72.1% landed v 64.2%
  quoted, 136 calls; own bands 60-65 +7.6, 65-70 +8.4, both touching zero).
  Fit season is -3.0 at 65-70%, so Rule 3 (fit on the completed season,
  confirm on the current one) is not met and a refit would fail the gates.
  Under-confident is the safe side. Not changed.
- The 85%+ tail remains the one real over-confidence (41 pooled calls, 68.3%
  landed v 88.8% quoted) with only 2 check-season calls, so it cannot be
  confirmed out of sample. Same open question as 12 and 22 Oct. The list bar
  never reaches it as a headline claim worth more than 85% (`GROUP_A_MIN`).

## Other sports, check window (out of sample)

Cumulative gaps at 55%+ / 62%+ / 70%+ / 75%+ (points, 90% interval on the
first two where it excludes zero).

| Sport | n | 55+ / 62+ / 70+ / 75+ | Reading |
|---|---|---|---|
| NFL | 318 | -1.4 / -3.2 / -5.4 / -3.5 | leaning over, all inside noise (70%+ [-12.9,+1.4]) |
| Baseball | 3,626 | **-2.9 [-4.7,-1.2]** / **-5.0 [-8.2,-1.6]** / +1.8 / thin | over at 55-70%, as 5, 12, 22 Oct |
| Basketball (NBA) | 1,322 | +1.8 / +2.1 / +2.2 / +0.6 | calibrated |
| Rugby union | 744 | +2.5 / +1.5 / +2.1 / +1.3 | calibrated to conservative |
| Ice hockey | 1,394 | **-6.1 [-8.8,-3.4]** / **-6.1 [-10.8,-1.4]** / +2.2 / thin | over at 55-70%, span 60-70% -8.3 [-12.5,-4.3] |
| College football | 1,032 | **+2.5 [+0.2,+4.8]** / +3.7 / +3.6 / +3.1 | conservative (off the list anyway) |
| College basketball | 5,814 | **-1.4 [-2.4,-0.5]** / **-1.8** / -0.6 / -1.1 [-2.2,+0.1] | over at 60-70% (-4.6 [-6.8,-2.3]); 70%+ bar inside noise |
| WNBA | 519 | +1.0 / -1.7 / -2.7 / -4.6 [-9.7,+0.7] | inside noise; 75%+ to watch |
| Rugby league | 296 | +0.5 / -0.4 / +3.7 / thin | calibrated; small |

- **Ice hockey is the largest sports gap** and is stable in sign: fit window
  was fine (span 60-70% +0.8), check window -8.3. Its 70%+ calls (47) landed
  74.5% v 72.3% quoted, so a list bar of 70%+ would be unaffected; only the
  55-70% band is overstated. The list rule (`sports.list_threshold`, 80% tested) is set by calls at the
  pick's own level, so a 55-70% hockey pick should not reach the list; I did
  not verify that here. Reserve and board rows in that band quote about 6
  points too high. A refit of the hockey curve is a
  `sports.py --tune` job (by hand, Rule 5): flagged, not done here.
- **Baseball** unchanged at -5 on 62%+ for the fourth consecutive check.
- Nothing in NBA, rugby union, rugby league or the WNBA/NFL (inside noise)
  needs attention. College basketball's gap is large in n but small in size.

## Not done and why

No constant, curve or `sports.json` was changed. Football would fail Rule 3
(fit season disagrees); the sports tunings are by-hand `--tune` runs with
their own check. Raw output: `python3 calibration_bands.py` (about 15 min).
