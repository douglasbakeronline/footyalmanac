# The Card by payout: 1.5x, 2x, 2.5x, 3x and the ladder (11 Nov 2026)

Douglas, 11 Nov 2026: "Preferably 3x or more. Then 2.5x. Then 2x. Then
1.5x ... I need the groups to win every time. But ultimately this has to be
a profitable business."

## What was tested

Pre-registered in `tools/card_replay.py` (`PAYOUT_BANDS`, `PAYOUTS`) before
any result: the rule 8 Card (the model's own picks, its most likely
combination) with the 2x swapped for one payout band, up to three groups a
day, two units each: `pay15` (1.45-1.99, two or three picks), `pay25`
(2.40-2.99), `pay3` (3.00-4.60), and `ladder` (one group a band a day, 3x
first, Douglas's order). Also in `tools/card_legs_history.py` `cardM7`.

## Five football-data seasons (football only, return per unit)

| season | 2x (live) | 1.5x | 2.5x | 3x | ladder |
|---|---|---|---|---|---|
| 2022-23 | +28.7% (45) | +13.0% (67) | +15.6% (46) | +39.8% (55) | +38.8% (76) |
| 2023-24 | -36.6% (16) | +4.9% (23) | -56.3% (13) | -50.1% (22) | -29.8% (34) |
| 2024-25 | -0.4% (56) | -11.3% (84) | -14.2% (56) | -20.4% (79) | -15.4% (97) |
| 2025-26 | +22.0% (44) | +1.0% (67) | +8.7% (46) | -17.1% (58) | -7.1% (80) |
| pooled, four full seasons | **+10.3%** on 322 units | +0.6% on 488 | -2.5% on 322 | -7.1% on 428 | -0.4% on 574 |
| groups won | 73 of 161 (45%) | 141 of 244 (58%) | 59 of 161 | 60 of 214 | 108 of 287 |

2026-27 so far: one to four groups each, nothing to read.

## The pool (every sport, 30 Oct to 14 Nov, `--recover`)

| variant | days | groups won | return | paired v live |
|---|---|---|---|---|
| live (2x) | 10 | 8 of 12 | +69% | |
| pay15 | 13 | 16 of 19 | +47% | +0.11 a day, p(worse) 0.43 |
| pay25 | 10 | 7 of 13 | +46% | p(worse) 0.85 |
| pay3 | 14 | 5 of 20 | -19% | p(worse) 0.99 |
| ladder | 16 | 8 of 23 | -13% | p(worse) 0.99 |

## Reading

- The 2x stays the Card. It is the only band ahead pooled, though it swings
  (-37% to +29% by season).
- The 1.5x wins most often (58% on football, about as priced) and is the
  steadiest (ahead in three seasons of four, positive in 2023-24 when the 2x
  lost 37%), but it makes about nothing (+0.6%). Short groups win more
  often; they do not beat the price by more.
- The 3x loses pooled, and the ladder with the 3x first is flat at best.
- None passes the gate against live. Nothing on the page changes.

## Next

The variants replay nightly in the Card review and weekly on football-data.
The 1.5x is the one to watch on the pool: if it keeps building on days the
2x cannot and its own legs reach 100 with p(worse) <= 0.30 against live, it
earns a place as a second, labelled group.
