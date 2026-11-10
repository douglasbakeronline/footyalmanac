# Football reserve landing below its quotes (10 Nov 2026)

Planner task: football reserve, last 28 days, 242 of 379 landed (63.9%) v 256.8 expected (67.8%), z -1.64. Located on `record-graded.json` (location only, nothing fitted, Rule 1).

## Where the gap sits

Reserve picks from 13 Oct (379):

| Cut | n | Landed | Expected | z |
|---|---|---|---|---|
| Band 60-65 | 118 | 71 | 74.8 | -0.73 |
| Band 65-70 | 151 | 97 | 101.8 | -0.84 |
| Band 70-75 | 98 | 64 | 70.9 | -1.55 |
| Band 75+ | 12 | 10 | 9.3 | +0.48 |
| Home picks | 327 | 203 | 222.0 | -2.26 |
| Away picks | 52 | 39 | 34.8 | +1.24 |
| AF_EXTRA (`af.*`) | 262 | 161 | 176.7 | -2.08 |
| en / eu / de / us | 30 / 13 / 10 / 10 | 21 / 9 / 6 / 7 | 20.5 / 9.1 / 6.8 / 6.6 | all within 0.6 |

Reserve since 30 Sep (526): 339 v 356.9, z -1.68. Before 13 Oct it was 97 v 100.1 (z -0.55), so the shortfall is concentrated in the last four weeks. No single league has 12 reserve picks in the window (largest 8), so no competition carries it; the gap is spread across the wider-league home picks (all-time AF reserve home picks 183 v 205.9, z -2.81; away 39 v 36.2).

## Why no exclusion ships

- The same wider-league home calls outside the reserve are on quote: all graded AF_EXTRA home picks in the 60-75% bands (reserve and list together) landed 463 v 479.6 expected (z about -1.2), 75%+ home above quote, the AF list picks 93 v 93.6. A gap that appears only in the reserve slice and only in the last month looks like selection plus noise, not a miscalibrated band.
- AF_EXTRA is not in the replay (`tune.codes` leaves it out; see `claude/home-away-tilt-2026-10-26.md`). There is no history on which a home tilt or a league exclusion for these leagues could be fitted on 2025-26 and confirmed on 2026-27. Excluding them from the live-record evidence alone would be fitting on the scoreboard.
- Away picks in the same family are over quote (+1.2 z), the mirror of the home gap already seen on 26 Oct. A global tilt was tested and failed the gates (p(worse) 0.36+).

## Decision

No code change; the Rule 3 gates cannot be run. What would settle it: a prior-season replay for the wider leagues (API-Football has it), then a home-advantage scale by family gated paired and bootstrapped. Revisit if the reserve's z passes -2 on 50+ more picks at 28 days, or when that replay exists.
