# College basketball: a flatter slope at neutral sites, rejected (28 Nov 2026)

HQ's backlog, "Reserve (other sports) landing below its quotes" (z -3.2, 301 of 452 over 28 days). Located on `sports-graded.json` (tally only, rule 1), reserve-only picks from 31 Oct:

| group | picks | landed | quoted | z |
|---|---|---|---|---|
| ncaab, no venue mark | 488 | 74.2% | 74.3% | -0.05 |
| **ncaab, neutral** | **112** | **55.4%** | **71.2%** | **-3.8** |
| ncaab, away | 15 | 60% | 71% | -1.0 |
| cfb | 196 | 77.6% | 76.8% | +0.2 |
| nba | 109 | 71.6% | 69.7% | +0.4 |
| nfl / rugby | 38 | 63% | 70% | -0.6 |

So the whole gap is college basketball at neutral sites (tournament fortnight), the one already read on 27 Nov (`ncaab-neutral-intercept-2026-11-27.md`). No band, no other sport carries it. Excluding neutral picks from the reserve is a display rule on a gap the model should price; the shipped `NEUTRAL0` intercept fix is still waiting for Douglas's `sports.py --tune --only ncaab` (rule 5), and the Neutral mark and Caution tier already flag these rows.

## New idea tested: a flatter slope at neutral sites

After `NEUTRAL0`, 58% v 73% remained. Variant: neutral games get their own slope on the calibrated log-odds (no intercept), fitted on the fit season 2024-25 (early months only: 376 games, slope 0.71; all months 737 games, slope 0.98). `tools/ncaab_neutral_slope_eval.py`, live parameters, paired and bootstrapped, against the `NEUTRAL0` curve:

| variant | window | games | gain | p(worse) |
|---|---|---|---|---|
| early only (0.71) | fit | 5,776 | +0.0004 | 0.14 |
| | **check 2025-26** | 5,814 | **+0.00028** | 0.24 |
| | this season | 1,241 | +0.0033 | 0.009 |
| all months (0.98) | check | 5,814 | +0.00004 | 0.07 |

Fails rule 3's gain bar (0.0005) on the check season, though the sign agrees on all three windows and this season is clearly better. Not shipped; no code or number changes.

## What would settle it

More neutral early-season games (each November adds about 250). Re-run the tool after the next tournament fortnight or once `NEUTRAL0` is refitted live; if the check gain reaches 0.0005, ship the slope as a second `neutral` term in the cal.
