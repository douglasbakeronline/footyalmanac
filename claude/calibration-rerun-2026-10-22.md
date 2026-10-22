# Calibration by band and sport, rerun (22 Oct 2026, Andrew)

Task: calibration by confidence band for football and by sport for the rest,
from history, bootstrapping the gaps. `python3 calibration_bands.py` (5 Oct,
extended 7 Oct, rerun 12 Oct) does exactly this, so no code changed. This is
the 10-day refresh on the same method. `record.json` was not read (Rule 1);
`calibration.json` and `sports.json` untouched. Gap = landed minus quoted,
90% bootstrap (2000 resamples of calls).

## Football (live curve a 1.135, b -0.30)

Fit season 6,474 calls (in-sample), check season 1,491 (was 1,428 on 12 Oct).

| Band | Fit gap [90%] | Check n | Check gap [90%] |
|---|---|---|---|
| 55%+ | +1.7 [-0.2,+3.7] | 315 | +2.7 [-1.7,+7.0] |
| 62%+ | -0.4 [-3.1,+2.1] | 149 | +4.8 [-1.5,+10.5] |
| 70%+ | +0.5 [-3.1,+4.2] | 54 | +2.5 [-7.1,+11.5] |
| 75%+ | -1.8 [-6.5,+3.1] | 20 thin | |
| 85%+ | **-19.6 [-32.4,-7.0]** (88.8 v 69.2) | 2 thin | |
| span 60-70% | +0.6 [-2.5,+3.9] | 134 | **+7.5 [+1.1,+13.5]**, P(gap<=0) 0.03 |

- Nothing moved on the fit season. Every cumulative bar from 55% to 80% is
  inside its interval; the line is fine.
- **New since 12 Oct: the 60-70% span in the check season is now
  under-confident outside its interval** (71.6% landed v 64.1% quoted, 134
  calls). Own bands: 60-65% +7.3, 65-70% +7.9, both with intervals touching
  zero. Pooled over both seasons it is +1.9 [-0.9,+4.8], so it is a
  this-season effect, not a fault in the curve. It agrees with
  `midband-calibration-2026-10-21.md` (core-league 65-75% calls landing
  above quote on the scoreboard), here seen independently on the replay,
  which Rule 1 allows. Under-confidence is the safe side: no list pick is
  overstated. Rule 3 needs the fit season to agree too, and it does not
  (-3.0 at 65-70%), so a refit would fail the gates. Not changed.
- The 85%+ tail is still the one real over-confidence (41 pooled calls, 68%
  landed v 89% quoted) and still unconfirmed out of sample (2 check calls).
  Unchanged open question from 12 Oct.

## Other sports, check window (out of sample), 55%+ / 62%+ / 70%+ / list bar

| Sport | n (check) | Gaps | Reading |
|---|---|---|---|
| NFL | 378 | -1.9 / -4.5 / -3.9 / 80%+ -2.7 | within noise, leaning over-confident |
| NBA | 1,336 | +1.8 / +2.2 / +2.1 / 75%+ +0.6 | calibrated |
| Rugby union | 788 | +2.9 [+0.2,+5.7] / +2.1 / +2.5 / 70%+ bar +2.5 | conservative |
| College football | 1,218 | +1.3 / +2.4 / +2.5 / 70%+ +2.5 | conservative |
| College basketball | 5,814 | -1.4 / -1.8 (both exclude 0) / -0.6 | over at 60-70% and 80-85%; 70%+ bar inside noise |
| WNBA | 538 | +1.8 / -1.3 / -2.5 / 80%+ -4.0 [-10.6,+2.4] | inside noise; 75%+ -4.6 [-9.7,+0.7] to watch |
| Baseball | 3,678 | -2.6 / **-4.8 [-8.1,-1.5]** / +2.2 | over-confident at 55-70% (as 5 and 12 Oct) |
| Hockey | 1,539 | **-5.0 [-7.6,-2.4]** / **-5.5 [-9.8,-1.1]** / +3.2 | over-confident; fit window was fine |
| NRL | 298 | +0.4 / -0.6 / +3.7 | within noise |

Sports with a Daily List place are calibrated or conservative at their bars.
NFL check gaps are all negative but none excludes zero (n 378); WNBA at
its 80% bar is the same. Baseball and hockey, without list places, remain
over-confident at 55-70% and unchanged since 12 Oct: their tab tiers are
inflated, not a list pick. Fixing them is `sports.py --tune` territory
(refit on the combined window or drop hockey's curve), not a hand-edit.

## Not done

No model number moved, no code. Candidates for a human or the gates: the
85%+ football display cap, the hockey and baseball refit, and a core-league
60-70% curve (expected to fail Rule 3 on the fit season; see the 21 Oct note).
