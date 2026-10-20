# Own-band Daily List admission, replayed for every sport (20 Oct 2026)

Nina, from the HQ planner. Question: a sport's List bar is the lowest cumulative
threshold ("calls at X% or more") that landed 80%. A strong tail (90%+) can
carry a weak 70-80% band over that line (college football, rugby, college
basketball). Does admitting a pick only when its own 5-point band also landed
80% hold up on games the bar was not set on?

Tool: `python3 tools/own_band_replay.py` (advisory, writes `audit-out/own-band.json`).
History only (`history-sports/`, shipped `sports.json` parameters and
calibration); the live record was not read (Rule 1). Probabilities do not
change, so the log-loss gate does not apply; the test is hit rate of admitted
picks, paired bootstrap of admitted v all picks the old rule admitted (2,000
resamples).

## Held out: bar set on the fit season (Jul 2024-Jun 2025) only, applied to the check season (since Jul 2025)

| Sport | old bar | new bar | old picks, hit | new picks, hit | dropped picks, hit | p(new worse) |
|---|---|---|---|---|---|---|
| Rugby (union + intl) | 65% | 75% | 451, 79.6% | 247, 84.2% | 204, 74.0% | 0.002 |
| College basketball | 65% | 80% | 3,792, 78.9% | 1,884, 87.4% | 1,908, 70.5% | 0.000 |
| NFL | 70% | 75% | 128, 73.4% | 76, 77.6% | 52, 67.3% | 0.10 |
| NBA, WNBA, college football | unchanged by the rule on the fit season alone | | | | | |
| MLB, NHL, NRL | no place either way | | | | | |

Rugby and college basketball clearly pass: 250+ check games, p(worse) far under
0.30, and the dropped picks landed 5 to 9 points under the kept ones.

## What ships: the rule on both windows (as the bar is set today)

`sports.list_threshold` now also requires every own band from the threshold up
to clear 80% in each window (the fit season and the check season), a band under
30 calls after widening not vetoing. Bars from the saved bands in `sports.json`:

| Sport | bar before | bar now | check-season picks, hit before | after |
|---|---|---|---|---|
| Rugby | 70% | 80% | 356, 82.0% | 152, 90.1% |
| College basketball | 70% | 85% | 3,172, 82.1% | 1,258, 91.6% |
| NBA | 75% | 80% | 298, 82.2% | 165, 86.7% |
| WNBA | 80% | 85% | 101, 81.2% | 47, 87.2% |
| NFL, college football (off the List) | 80% | 80% | unchanged | |

This second table is descriptive, not held out (the check season is inside the
rule). The NBA and WNBA moves have no held-out confirmation (on the fit season
alone the rule changes nothing for them); their support is the reverse
direction (own bands from the check season applied to the fit season: NBA
dropped 128 picks landing 81.3% against 86.9% kept; WNBA dropped 28 landing
75% against 89% kept). The cost is volume: the List shrinks, rugby by 57% and
college basketball by 60% of check-season picks. College basketball's 80-85%
band landed 81.6% (fit) and 79.1% (check), which is why its bar is 85%, a step
above the held-out 80%.

## Not done

- No cap on tail bands: 85%+ stays admitted wherever it clears.
- Tennis and football have their own admission (tested bars, `build_tennis`,
  `build.LIST_MIN`) and were not touched.
- Picks that miss the new bar but are 62%+ go to the reserve as before, graded
  as their own group.
- `sports.json` was not rewritten: `build()` derives the bar from its saved
  bands via `stored_threshold`, and `--tune` writes the same number.
