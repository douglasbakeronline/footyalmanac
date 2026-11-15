# The Card's bookmaker, paired: Bet365 v William Hill (13 Nov 2026)

Issue #156 asked which UK book the Card should be written for. Until today
`tools/price_timing.py` ranked each book against the average price, each on
its own set of legs (Bet365 +0.93% on 108, William Hill -0.16% on 103), which
cannot say whether one book beats another on the same pick. `book_vs` now
pairs each book with `CARD_BOOK` on the picks both priced, day-resampled
(both tails, so equal prices read as neither), at the first and the last
pre-start price, with the settled singles return at each book's first price.
A side is read only on 50+ paired picks at p <= 0.10, the price-timing rule.

## The read, Card-rule legs in the pool, 30 Oct to 13 Nov

| book v William Hill | paired picks | days | a pick | ahead / behind | p | a three-pick group | settled singles, Hill v the book |
|---|---|---|---|---|---|---|---|
| Bet365 | 88 | 11 | +1.06% | 48% / 24% | 0.000 | +3.2% | -2.25% v -1.11% (87) |
| Betfair | 94 | 12 | -0.95% | 12% / 44% | 0.996 | -2.8% | -0.36% v -1.16% (92) |
| BetVictor | 79 | 11 | -1.27% | 13% / 54% | 1.000 | -3.8% | +1.90% v +0.67% (78) |
| best UK price | 97 | 13 | +1.58% | 49% / 0% | 0.000 | +4.8% | -1.06% v +0.62% (95) |

Bet365 is ahead on 10 of the 11 days. Every paired pick is football (one
NBA pick for BetVictor): the NBA and tennis legs rarely carry both books'
first prices, and the last-price pairs (`lastBooks`, 12-16 legs, mostly NBA)
are too few to read. William Hill is the second-best of the four, ahead of
Betfair and BetVictor.

## What it means for the return

At the Card's 2x, a three-pick group at Bet365 pays about 3% more than the
same group at William Hill, on the football picks; taking the best UK price
pick by pick about 5%. On the live Card's record (36 groups, 51 units
staked, landed/expected 0.994), if every pick gained it, 3% is the difference between losing about
14% and losing about 11%: worth having, not an edge on its own.

## Not changed

`CARD_BOOK` stays William Hill. It is the book Douglas bets at (the Daily
List's Hill chips were built at his request for that reason), so switching
it is his call, not a gate's. The nightly Card review prints the paired
lines and says in bold when a book pays more than `CARD_BOOK` on both the
first price and the settled singles. The page already shows each group's
combined price at every UK book (`ogBooks`).

## Files

`tools/price_timing.py` (`book_vs`, `_read_pair`, `vsBook` in the report),
`tools/card_review_post.py` (`book_vs_lines`), `tests/test_book_vs.py`.
