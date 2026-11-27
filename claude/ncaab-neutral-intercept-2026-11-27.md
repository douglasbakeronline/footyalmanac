# College basketball: the neutral court and the calibration's home term (27 Nov 2026)

Build session, 27 Nov 21:17 London slot. HQ's backlog had "Reserve (other
sports) landing below its quotes" at z -3.1. Read on `sports-graded.json`
(tally only, rule 1) the gap is college basketball since 13 Nov: reserve
211 of 328 landed v 240.2 expected (z -3.7); the list (85%+) 198 of 216 v
197.7, on quote; NCAAB board picks on quote. By venue at 70%+ on the live
record (`sports-record.json` `bySide`): home 585 of 672 (z +1.4), away 11 of
24 (z -3.7), neutral 48 of 76 (z -3.4). The week from 16 Nov is the
tournament fortnight: neutral courts.

## Is it the faster early K (16 Nov)?

No. On the replay `sports.py --tune` uses, this season's games from 3 Nov
(1,175, never used to fit anything), the early K beats the old setting:
log loss 0.5003 to 0.4932, p(worse) 0.001. The replay reproduces the live
shortfall with or without it (65-85% calls 69% v 76%), so the live record is
not a pipeline fault.

## The home term at a neutral site

The season-phase curve is `a + b * logit(p_home)`. College basketball's
November-December intercept is +0.31 in log-odds: early-season home sides
win more than the Elo's 100 points say. `p_home` already drops the home
advantage on a neutral court, but the curve still gave +0.31 to whichever
team ESPN lists first. On this season's replay, neutral picks of the listed
"home" side at 65%+ landed 46 of 83 v 63.0 expected (z -4.5); of the listed
away side 18 of 25 v 18.5.

Variant (`sports.NEUTRAL0`): the curve fitted on venue games only, applied
without its intercept at a neutral site. `tools/ncaab_neutral_eval.py`, live
parameters, curve fitted on 2024-25, paired:

| window | games | log loss | gain | p(worse) | 65%+ gap |
|---|---|---|---|---|---|
| fit 2024-25 (in sample) | 5,776 | 0.5478 -> 0.5480 | -0.0002 | 0.64 | 0.001 -> 0.000 |
| **check 2025-26** | **5,814** | **0.5475 -> 0.5466** | **+0.0009** | **0.03** | **0.020 -> 0.020** |
| this season to 27 Nov | 1,197 | 0.4914 -> 0.4893 | +0.0021 | 0.15 | 0.028 -> 0.028 |

It passes rule 3's gates on the check season (250+ games, p(worse) at most
0.30, gain 0.0005+) and the honesty guard, and this season agrees. The fit
season is level, as it should be: the old curve was fitted there with the
neutral games in it.

It mends only part of the gap. This season, neutral picks at 65-85% go from
54% landed v 73% quoted (96 picks, z -4.2) to 58% v 73% (89, z -3.1).
Neutral-court tournament games are harder to call than the ratings say for
a reason the intercept is not: early-season ratings meet teams from other
conferences for the first time. No further variant is proposed here.

## Shipped, inert

- `sports.calibrate(p, cal, when, neutral)`: a cal carrying `"neutral0"`
  drops `a` at a neutral site. `fit_phase_calibration(..., neutral0=True)`
  fits on venue games and sets the flag. `tune_sport` passes it for the
  sports in `NEUTRAL0` (college basketball alone); `losses` and the board
  pass each game's `neutral`.
- `sports.json` is unchanged, so the board's numbers do not move until a
  `python3 sports.py --tune --only ncaab` run writes the flag (rule 5:
  that refit is Douglas's by-hand step, `sports.py` line 70). The refit
  should print the check calibration line with the new `a` (early 0.3151,
  b 1.0099) and the list bar should stay 85%.
- `tests/test_sports_neutral_cal.py` (5): an old cal is unchanged at a
  neutral site, the flag drops the intercept only there, swapping the listed
  sides swaps the chance, the fit leaves neutral games out.

## Not changed

The Card (college basketball never reaches it), the Daily 2x (college out),
the Neutral mark and its wording, `WARY_TRIP_*` (the tripwire reads away
picks only; neutral picks at 76, z -3.4, carry no pre-registered rule, so
none is set from the record).
