# Calibration by confidence band, 5 Oct 2026 (Andrew, Calibration & Market Analyst)

Question: do the quoted confidences land at the rate they claim, band by band,
for football and for the other sports? From history only; `record.json` was
not read (Rule 1). Tool: `python3 calibration_bands.py` (new, advisory, writes
nothing, tests in `tests/test_calibration_bands.py`). Each band carries a
bootstrap 90% interval on landed minus quoted (2000 resamples of the calls,
fixed seed), so a gap inside the noise is not read as a miscalibration. Bands
under 30 calls are marked "thin".

`calibration.json` and `sports.json` were not touched.

## Football (live curve a 1.135, b -0.30)

Replay as `tune.py` fits it. **Coverage caveat:** this sandbox could not reach
API-Football, football-data.co.uk or ESPN, so the run used openfootball and the
committed `history/` only: 30 competitions in the fit season (5,262 fixtures),
12 in the check season (866, against 1,309 in the CI fit). Rerun in CI or
locally for the full set. The fit season is in-sample for the curve; the check
season is the fair test but small.

Cumulative bands (what the site quotes as "landed"):

| Band | Fit n | quoted | landed | gap [90%] | Check n | quoted | landed | gap [90%] |
|---|---|---|---|---|---|---|---|---|
| 55%+ | 1310 | 64.9 | 67.0 | +2.1 [+0.1,+4.2] | 166 | 64.4 | 69.3 | +4.9 [-1.3,+10.4] |
| 62%+ | 687 | 70.9 | 70.5 | -0.5 [-3.3,+2.3] | 93 | 69.3 | 79.6 | +10.2 [+3.4,+16.7] |
| 70%+ | 310 | 77.4 | 78.4 | +0.9 [-2.9,+4.8] | 33 | 76.1 | 81.8 | +5.7 [-6.5,+16.0] |
| 75%+ | 179 | 81.3 | 79.9 | -1.4 [-6.2,+3.5] | 17 | thin | | |
| 80%+ | 90 | 85.1 | 81.1 | -4.0 [-11.1,+2.7] | 9 | thin | | |
| 85%+ | 39 | 88.8 | 69.2 | -19.6 [-32.4,-7.0] | 1 | thin | | |

Findings:

1. **The line is fine through 80%.** Every cumulative band from 62% up is
   inside its interval in the fit season, and the check season, small as it is,
   leans the other way (under-confident, landing 10 points above the quote at
   62%+, interval excludes 0). No evidence for refitting; `tune.py --fit`
   already gates that properly.
2. **Own bands zig-zag** (45-55% over by 3, 55-65% under by 4-5, 65-70% over by
   5) with no monotone pattern: sampling noise of a two-parameter line, not a
   curve shape a better fit would fix. Rule 3 on ten free temperatures stands.
3. **The 85%+ tail is over-confident** (pooled 40 calls, 89% quoted, 70%
   landed, interval -31 to -7). It is in-sample, with only one check-season
   call, so the check cannot confirm or deny it. It matters because the Daily
   List's sort puts the highest quotes first. Open question for Douglas:
   whether to cap displayed confidence at about 85% until the check season
   fills. Not done here: it is a display/model decision, and a cap would need
   the tune gates. What would settle it: rerun on the full CI data, and again
   as 2026-27 fills.
4. Nothing here is a reason to touch `calibration.json`.

## Other sports (sports.py replay, sports.json parameters, warm teams)

Check window = out of sample. Cumulative bands, quoted vs landed, gap [90%]:

| Sport (cal live?) | Band | n | quoted | landed | gap [90%] |
|---|---|---|---|---|---|
| NFL (no) | 55%+ | 273 | 68.5 | 67.4 | -1.1 [-5.6,+3.6] |
| | 70%+ | 119 | 77.4 | 73.1 | -4.3 [-11.2,+2.0] |
| | 80%+ | 35 | 84.5 | 82.9 | -1.6 [-12.7,+8.8] |
| Baseball (no) | 55%+ | 2121 | 60.3 | 57.6 | **-2.7 [-4.4,-0.9]** |
| | 62%+ | 608 | 65.8 | 61.0 | **-4.8 [-8.1,-1.5]** |
| | 70%+ | 75 | 72.5 | 74.7 | +2.2 [-6.0,+10.1] |
| Basketball (yes) | 55%+ | 1108 | 68.9 | 70.8 | +1.8 [-0.3,+4.0] |
| | 70%+ | 475 | 78.2 | 80.4 | +2.2 [-0.8,+5.3] |
| | 80%+ | 165 | 85.0 | 86.7 | +1.7 [-2.7,+5.8] |
| Rugby (no) | 55%+ | 658 | 71.4 | 73.7 | +2.4 [-0.4,+5.2] |
| | 70%+ | 348 | 79.5 | 81.6 | +2.1 [-1.5,+5.5] |
| | 80%+ | 148 | 86.0 | 89.9 | +3.9 [-0.4,+8.0] |

- **NFL, basketball, rugby:** calibrated within noise at every bar that has 30+
  calls. Rugby was under-confident in the fit window (+6 at 55%+) and has
  settled in the check window; the correct reading is "if anything
  conservative". Their rejected calibration candidates were correctly
  rejected: applied to the check window, the rugby candidate would be
  over-confident by 3.8 points at 62%+ (interval excludes 0) and the NFL one
  by 6.4.
- **Baseball is over-confident, and the interval excludes zero in both
  windows** at 62%+ (fit -2.2, check -4.8) and at 55%+. It has no Daily List
  place (`listMin` null), so no list pick is mis-stated, but the tab quotes
  these numbers and tiers them. Strong/Firm labels on baseball overstate by
  about 3 to 5 points.
- **Why baseball has no calibration although it passed the log-loss gate**
  (`sports.json`: delta -0.0009, p(worse) 0.055): the honesty guard in
  `sports.py tune_sport` blocked it because the 65%+ quoted-vs-landed gap
  "widened" from 0.031 to 0.058. That comparison is between different row
  sets: calibrated, only 109 games clear 65% (294 raw), and that thin set
  landed 73.4% against 67.6% quoted (interval -0.9 to +12.9, inside noise).
  Across the larger sets the candidate does what it should: at 55%+ the gap goes
  -2.7 to -0.6 (interval spans 0) and at 62%+ -4.8 to +0.7 (spans 0).
  **Proposal, not made:** compare the guard at a bar with at least 30 calls in
  both versions (or on the gap's bootstrap interval) instead of a fixed 65%.
  That is a change to the sports gate, so it needs Douglas's decision, and
  baseball would then still need `sports.py --tune` run by hand to write it.

## Method notes

- Bootstrapping the gap (not just reporting a rate) is what separates the
  baseball finding (real) from the football own-band zig-zag (noise).
- Football still needs a run with full data. If CI wants it:
  `python3 calibration_bands.py --football --json audit-out/bands.json`.
- Not tested: per-league football calibration (too few calls per league for
  bands), and whether the 85%+ tail is dominated by flagged or unrated rows.
