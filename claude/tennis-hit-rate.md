# Tennis below its expected hit rate — 5 October 2026

Alert: 57% picked winners against 61% quoted over 294 graded matches.

## What the record shows (not fitted on, rule 1)

| | n | landed | quoted |
|---|---|---|---|
| ATP | 118 | 61.9% | 62.2% |
| WTA | 176 | 54.5% | 60.6% |
| WTA qualifying | 19 | 42.1% | 59.9% |
| ATP qualifying | 24 | 70.8% | 59.3% |
| Retirements | 7 | 28.6% | 61.1% |
| WTA, a player with under 20 rated matches (where the build stored ratings) | 42 | 47.6% | 57.5% |

ATP is on target. The gap is WTA, and mostly WTA events below tour level
(Adana, Tolentino, Porto, Jingshan: 13 to 35 matches each, 29% to 57%
landed). The 294 are 14 days; the standard error on 294 matches is about
2.9 points, so 57.5% against 61.3% is 1.3 standard errors. Against the
64% to 65% that tune_tennis.py measures on 2026 tour-level data it is 2.2.
Sackmann's files carry tour-level matches, so the live feed's lower-level
events are a population the Elo never trained on.

## Surface

Every archived price is `Hard` (738 of 738). ESPN has no surface field
and `build_tennis.py` hard-codes it. This is a known, documented gap, not a
new one. A tournament-name lookup would fix it but needs a maintained list;
not built here (no manual data entry, and the live sample has no confirmed
clay week to test against). Surface weight itself is already swept in
tune_tennis.py (0.3 chosen for both tours).

## Test: shrink picks with a thin-history player

`tools/tennis_thin_test.py`: fit 2025, check 2026, live constants, one
change (probability pulled toward 0.5 by 0.8 or 0.6 when the lesser-rated
player has under 20 or 40 matches).

| | 2025 | 2026 check |
|---|---|---|
| ATP baseline log loss | 0.6297 | 0.6241 |
| ATP 0.8 under 20 | 0.6289 | 0.6236 |
| ATP 0.8 under 40 | 0.6286 | 0.6229 |
| WTA baseline | 0.6294 | 0.6115 |
| WTA 0.8 under 20 | 0.6292 | 0.6113 |
| WTA 0.8 under 40 | 0.6295 | 0.6105 |

Best gain 0.0012 (ATP, 2026), against a gate of 0.005 (`MIN_GAIN`). 0.6
shrink is worse than none. **Rejected: tour-level history shows no thin-player
effect worth correcting.** Nothing in `tennis.json`, `build_tennis.py` or
`tune_tennis.py` changed.

## Open

- The live shortfall is probably lower-level WTA events. The only real
  fix is data for them (a second source, or rating those players from
  ITF/125 results), not a constant. Re-check at 500+ graded matches.
- Surface hard-coding matters from clay season; plan the lookup before April.
- Retirements are graded (7 matches, 2 landed); tiny, leave.

## Re-read, 5 October 2026 (Theo, weakest-sport task): no change

Record read only (rule 1), 330 rows, 1 void-excluded set: 

| | n | landed | quoted |
|---|---|---|---|
| WTA all | 190 | 55.3% | 60.7% |
| WTA main draw | 169 | 56.8% | 60.9% |
| WTA qualifying | 21 | 42.9% | 59.6% |
| WTA main, quoted 62%+ | 54 | 68.5% | 72.5% |
| ATP main | 98 | 60.2% | 63.1% |

WTA is still the weakest sport, but main draw is 1.1 standard errors under
quote (SE about 3.7 points on 169) and the 62%+ band is 4 points under on 54
matches, 0.7 SE. Other sports have 15-20 graded games each, too few to rank.
The one candidate improvement not already tested today (thin-player shrink,
above) is the surface lookup, which needs a maintained tournament list and has
no clay sample to test on. Nothing met the bar to ship, so nothing changed.
Re-check at 500+ graded WTA matches.
