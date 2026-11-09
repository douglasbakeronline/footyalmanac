# The Card's prices by lead time, and last prices after the start (9 Nov 2026)

Issue #156, third slice (after #160 by sport and #171 UK books on every card).
Scheduled build session, 9 Nov 2026 14:30 UTC. Advisory: nothing here changes
a rule, `CARD_BOOK` or the push time.

## What was asked

When to take the Card's price: does a leg's price move between the first
real bookmaker price and the last one before the start, and does that depend
on how far ahead the first price was taken? If prices drift to the start,
the push in `notify.py` could wait; if they shorten, it should go early.

## What the pool holds

Card-rule legs (full or wider rule) in `groupings-archive/pool-*.json.gz`
from 30 Oct to 12 Nov with a first and a last real price: 107 after the
guard below (93 football, 12 NBA, 2 tennis). The pool keeps only the first
and the last price, so the move is measured by the lead of the first price
on the start, not price by price over time.

| first price's lead on the start | legs | mean move first to last | drifted | shortened |
|---|---|---|---|---|
| under 6h | 8 | +0.81% | 3 | 1 |
| 6-24h | 25 | +0.79% | 11 | 12 |
| 24-48h | 19 | +0.06% | 6 | 11 |
| 48-72h | 10 | +4.64% | 9 | 1 |
| 72h+ | 45 | +2.04% | 22 | 18 |

A positive move is a drift: the last price was longer than the first. The
last price sat a median 2.0h before the start (68 of 107 within 3h), so
"last" is close to a closing price.

Read: legs first priced two or more days out drift about +2.6% on average
(55 legs), those priced inside two days about +0.5% (52). Football carries
the effect (48-72h +4.64%, 72h+ +2.04%); NBA (12 legs) and tennis (2) are
too few to read. For the Card this says the price taken at the start is no
worse, and on football legs priced early it is better, than the price at
publication. It is one fortnight, mostly one sport, and a mean of moves with
a long tail; it is not enough to move the push in `notify.py`. The nightly
review now prints this table each night, so the 30 Nov review can decide.

## Last prices after the start

48 of 1,394 pool legs with a last price had it stamped after the start on
file (`when`): 45 tennis, 3 football. The tennis ones are mostly matches
listed at their session's first start (`tennis_starts`) and played later in
the session; the football ones were estimate-first legs whose fixture moved.
`archive_pool` judges "started" by the current build's start time but kept
only the first one written, so the pool could not tell a moved start from a
price taken in play. Two changes:

- `archive_pool` writes `whenLast`, the start time the build judged by,
  whenever it differs from the first `when` (from 10 Nov). `when` itself is
  never changed.
- `tools/price_timing.py` leaves out any leg whose last price came after its
  latest known start (`whenLast`, else `when`) and counts it as
  `lastAfterStart`. One Card-rule leg (tennis) to 9 Nov; nothing shows that
  price was pre-start, so it proves nothing about timing.

`update_closing` (the Card's own archive, `lastOdds` on group legs) skips a
leg once its archived `when` has passed, so the CLV tally is not affected.

## Files

`groupings.py` (`archive_pool`: `whenLast`), `tools/price_timing.py`
(`leads`, `lastLead`, `lastAfterStart`, `hours_before`, `lead_bucket`),
`tools/card_review_post.py` (three lines in the price timing section),
`tests/test_price_timing.py`, `tests/test_card_pool_replay.py`.

## Next

The book ranking still has no sport but football with 10 priced legs (#171
added UK books to NBA and tennis Card picks from 9 Nov). Re-read the lead
table and the per-sport books at the 30 Nov review; a push-time proposal
needs 30+ legs a bucket on more than football.
