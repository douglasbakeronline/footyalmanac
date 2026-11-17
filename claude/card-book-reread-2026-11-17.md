# Which book to write the Card for: re-read at 17 Nov 2026

HQ planner task, a repeat of #156 / `claude/card-book-paired-2026-11-13.md`. Same
tool (`tools/price_timing.py`, `book_vs`), pool to 17 Nov, Card-rule legs, all football
bar one NBA leg. Paired on the picks both books priced, day-resampled.

| v William Hill | first price: picks / a pick / p | last pre-start price: picks / a pick / p | settled singles, Hill v book |
|---|---|---|---|
| Bet365 | 102 / +1.11% / 0.000 | 66 / +0.86% / 0.000 | -3.19% v -1.94% |
| Betfair | 107 / -0.97% / 0.999 | 59 / -0.24% / 0.916 | -0.58% v -1.40% |
| BetVictor | 88 / -1.24% / 1.000 | 53 / -0.41% / 0.946 | +1.37% v +0.15% |
| best UK price | 111 / +1.64% / 0.000 | 67 / +1.39% / 0.000 | -2.09% v -0.32% |

Against the average (all legs each book priced): Bet365 +0.94% and best on 76%,
William Hill -0.09% (55%), Betfair -1.28% (26%), BetVictor -1.50% (14%).

Read: Bet365 is clearly the best single book, at the first price and at the
last pre-start price (the push time sits between). A three-pick group at Bet365
pays about 3.4% more than at Hill. The best UK price beats Hill by 1.64 points
a pick (4.99% a three-pick group): under the 2-point bar, so nothing is added
to the Bets page. Settled singles are too few to say anything about returns:
the gain is the price difference, not a result.

Not changed: `CARD_BOOK` stays William Hill. CLAUDE.md and the 13 Nov note make
that Douglas's call (the book he bets at; the page already shows every UK book's
combined price per group, `ogBooks`), and no gate applies to a display
preference. If he wants it: set `CARD_BOOK = "Bet365"` in `groupings.py`
(note the `listAtBook` record and Hill chips key on the same constant).
This is a write-up, not a code change.
