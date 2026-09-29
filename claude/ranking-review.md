# Review of the FIFA ranking adjustment: 29 September 2026

Burundi 2-2 Algeria (AFCON qualifying, 29 Sep) was on the Daily List as
Algeria to win at 79%, "Strong", "84% landed". Douglas lost a four-fold on
it and asked whether it should have been there, given the row's own
scoreline read 1-1.

## What happened

- The international ratings priced Algeria at **56.6%** (xG 0.96-1.86,
  likeliest score 1-1). The FIFA points gap (1577 v 1078, 499 points) re-scored
  the pick to **79.4%** (`rankings.adjust_fifa`), a 23-point lift.
- The adjustment changes the pick's probability only. The xG and the scoreline
  stayed on the unadjusted model, so the row said 79% Algeria over a 1-1.
  **That was a display bug**, fixed below. It was not a wrong pick under the
  rules as they stood: 79% cleared the 60% bar for ranked internationals.
- The other legs were list picks at 90.9%, 86.9% and 85.0%. By the model's
  own numbers the four-fold landed 53% of the time; the price (0.98/1) implied
  51%. Losing it was close to a coin flip, not a surprise.

## The out-of-time check (`ranktest.py`)

The original test (fit 2025, judged 2026) was not in the repo, and this
cloud session cannot reach FIFA's API for 2025-26 releases. FIFA's public
history (Dato-Futbol) runs to Sep 2024, so the check uses Oct 2022 - Oct 2024
with FIFA_W frozen as shipped and the ratings refitted each quarter: 2,024
ranked win picks, neither weights nor ratings having seen them.

| | Result |
|---|---|
| Pick log loss, raw v adjusted | 0.6206 -> 0.6107 (-0.0099, p(worse) 0.012). It helps. |
| Calibration | Quotes 3-5 points high from 60% to 85%: 75-80% landed 71.4% of 133 |
| 60%+ (old list bar) | 73.7% of 949. Fails the shared 75% rule in this window |
| 65%+ | 76.5% of 791. Passes, as does 2026 (79.9% of 144) |
| Lifted 20+ points | 65.0% of 40, quoted 72.5% |
| Raw under 62%, adjusted 75%+ (Algeria-like) | 74.1% of 27 |
| Misses at 75%+ | 62 of 84 were draws |

The gain is a quarter of the -0.036 measured on 2026. Either 2026 is kinder
to the ranking or the ratings here (quarterly refit) differ from the live
hand-refitted ones. Both windows agree it helps.

## Changed

1. **Goals line agrees with the row** (`build.py`, `solve_goals`). On a
   ranking-adjusted international the pick's xG is scaled up and the other
   side's down by one factor until the grid gives the adjusted probability.
   Burundi v Algeria would have read 0.68-2.63, likeliest 0-2. The published
   split, BTTS and over 2.5 are unchanged.
2. **Ranked internationals need 65% for the Daily List** (was 60%), by the
   existing shared rule applied to both windows. Algeria at 79% would still
   have qualified.

## Not changed, open

- **Big lifts.** Picks the ranking lifted 20+ points landed 65% of 40 in
  2022-24. One window and 40 games is not enough to exclude them (rules 2-3).
  Confirm on 2026 in a local session that can fetch FIFA's releases; if it
  holds, treat a 20+ point lift like Celtic's Law (flag, off the list).
- **"84% landed" on a 79% pick.** Row rates are cumulative bands ("calls at
  75%+"), so a 79% call borrows the record of 90%+ calls. In this window
  75-80% calls landed 71%. Showing the row's own band would be more honest
  but changes every sport's rows and the list order. Douglas's call.
- FIFA_W was not refitted. It passed its own test on 2026; one older window
  running high is not grounds to move a structural constant (rule 5).
