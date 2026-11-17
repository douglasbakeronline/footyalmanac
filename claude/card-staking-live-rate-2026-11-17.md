# The live Card's bankroll at its current rate (17 Nov 2026)

Build session, 17 Nov 2026 evening. Advisory tool only; no Card rule, page or record changed.

## What was wrong

`tools/staking.py` sizes the bankroll for a month and a season of live Card groups at the
page's stakes. It took the live rate from every settled group in `groupings-record.json` over
the span of days that had one: 40 groups from 26 Oct to 15 Nov, 1.9 a day. Most of those came
from the Card of late October (a 2x and a 3x in up to three windows, up to six groups a day).
Since `CARD_RULE` 8 (11 Nov 2026) the Card builds the 2x alone, and many days build nothing;
empty days were not counted at all. So the nightly review told Douglas a month meant 57 groups
and a 98-unit bankroll.

## The fix

`groups_from_record` now takes the rate from `RATE_FROM` (2026-11-11) to the record's last day,
empty days counted and a pending group counted as published (`rateFrom` in `staking.json`,
printed in the review's month and season lines). The outcomes are still every settled group:
more groups to resample, at the same stakes. A span under `RATE_MIN_DAYS` (7) falls back to the
old rate.

| live, 17 Nov | before | after |
|---|---|---|
| groups a day | 1.9 | 0.71 (5 groups, 11 to 17 Nov) |
| month: groups, 95%-worst drawdown, bankroll | 57, 48.7 units, 98 units | 21, 24.6 units, 50 units |
| month: median, staked | -19.9 on 95.5 | -7.3 on 35.2 |

The median is still negative: the live groups landed 0.95 times the bookmakers' expectation.
That is the record's read, not a forecast.

## Limits

The resampled outcomes still include the 3x groups of October at one unit, so the average stake
reads 1.68 units where the Card now stakes two on every group. Restricting the sample to the 2x
would leave about 25 settled groups; revisit when the 2x alone reaches 40 settled.

Files: `tools/staking.py`, `tools/card_review_post.py`, `tests/test_staking.py`.
