# Calibration by band and sport, full-data rerun (12 Oct 2026, Andrew)

Task: check calibration by confidence band for football and by sport for the
rest, from history, bootstrapping the gaps. `python3 calibration_bands.py
--json` (written 5 Oct, extended 7 Oct) already does exactly this, so no code
changed. The new thing is that this run had the **full data**: 6,474 football
fixtures in the fit season and 1,428 in the check season (the 5 Oct run had
5,262 and 866 because the sandbox could not reach API-Football). `record.json`
was not read (Rule 1). `calibration.json` and `sports.json` untouched.

## Football (live curve a 1.135, b -0.30), gap = landed minus quoted, 90% bootstrap

| Band | Fit n | gap [90%] | Check n | gap [90%] |
|---|---|---|---|---|
| 55%+ | 1504 | +1.7 [-0.2,+3.7] | 296 | +2.7 [-1.7,+7.1] |
| 62%+ | 773 | -0.4 [-3.1,+2.1] | 142 | +5.5 [-0.5,+11.1] |
| 70%+ | 344 | +0.5 [-3.1,+4.2] | 53 | +2.0 [-7.9,+11.4] |
| 75%+ | 189 | -1.8 [-6.5,+3.1] | 20 thin | |
| 80%+ | 94 | -3.1 [-10.3,+3.7] | 11 thin | |
| 85%+ | 39 | **-19.6 [-32.4,-7.0]** (88.8 quoted, 69.2 landed) | 2 thin | |

- Every bar from 55% to 80% is inside its interval in both seasons. The curve
  is fine; nothing to refit (and Rule 3 gates would stop a refit anyway).
- **The 85%+ tail is still the one real miscalibration**, now on 41 pooled
  calls with the full data (68% landed against 89% quoted). The 5 Oct figure
  (39 calls, 69%) barely moved, so the extra coverage did not dilute it. It is
  in-sample and the check season has only 2 calls, so it is not yet confirmed
  out of sample. Open question for Douglas, unchanged: cap displayed
  confidence near 85% (a display decision that would need the tune gates).
  Most likely cause is that 85%+ in football is a handful of mismatched
  fixtures in leagues where one side is unrated or a heavy favourite is
  rested, which the Poisson grid cannot see. Not tested here.

## Other sports, check window (out of sample), 55%+ / 62%+ / 70%+ gaps

| Sport | listMin | Reading |
|---|---|---|
| NFL | 0.80 | within noise everywhere (-0.9 / -3.2 / -3.5) |
| NBA | 0.75 | within noise, slightly under-confident (+1.8 / +2.1 / +2.2) |
| Rugby union | 0.70 | under-confident, 55%+ +2.9 [+0.2,+5.7]; higher bars inside noise |
| College football | 0.70 | under-confident +3 at 62%+ to 85%+, intervals exclude 0; safe side |
| College basketball | 0.70 | over-confident at 55%+ (-1.4) and 62%+ (-1.8), intervals exclude 0; 70%+ and up inside noise (-0.6 to +0.9), so the list bar is unaffected |
| WNBA | 0.80 | within noise, but 75%+ is -4.6 [-9.7,+0.7] and 80%+ -4.0 [-10.6,+2.4]: leaning over-confident at its list bar, watch as the season fills |
| Baseball | none | over-confident: 55%+ -2.6, 62%+ -4.8 [-8.1,-1.5]. Matches 5 Oct |
| Hockey | none | **over-confident in check: 55%+ -5.6 [-8.2,-3.0], 62%+ -6.2 [-10.7,-1.7]**, fit window was fine (-0.3 / +1.4). Despite a live calibration |
| NRL | none | within noise |

- Sports with a Daily List place (NFL, NBA, rugby, CFB, NCAAB, WNBA) are
  calibrated or conservative at their list bars, WNBA's 80%+ the one to watch.
- **Hockey is new.** Its calibration (a 0.0878, b 0.6417) was fitted on the fit
  window and the check window then lands 6 points under the quote at 55-70%.
  It has no list place, so no list pick is overstated, but its tab tiers are
  inflated. This is the same pattern as baseball. Not changed: sports
  calibration goes through `sports.py --tune` and its own guards, and a
  hand-edit would break Rule 5. Suggest the next `sports.py --tune` is looked at
  for hockey specifically (refit on the combined window, or drop the curve).

## What was not done

No model number moved. No code. The 85%+ football cap and the hockey refit are
decisions for a human or for the tune gates.
