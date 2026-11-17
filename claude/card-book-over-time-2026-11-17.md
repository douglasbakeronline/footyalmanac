# The Card's bookmaker and price timing, by week and hour (17 Nov 2026)

Issue #156 again. `tools/price_timing.py` already had the book ranking, the
paired `book_vs`, leads and the settled return (notes of 10 and 13 Nov). This
adds the two cuts the issue still named: each book against `CARD_BOOK` by
week (`book_weekly`, `bookWeekly`), and the move to the start by first-price
hour and sport (`hours_by_sport`, `hoursBySport`). Pool legs under the live
rule, 30 Oct to 17 Nov, 211 legs (152 football, 59 NBA, no tennis, none
dropped for a post-start last price).

## Which book

Paired on the picks both priced, day-resampled, football only (NBA and tennis
legs carry one source's price, so no book comparison is possible there):

| v William Hill | first price | last pre-start price | settled singles, Hill v book |
|---|---|---|---|
| Bet365 | +1.41% a pick, 82 paired, 13 days, p 0.000 | +0.89%, 64, p 0.000 | -4.24% v -2.67% (82) |
| BetVictor | -1.09% (71) | -0.35% (51) | -1.20% v -2.20% |
| Betfair | -1.08% (89) | -0.25% (57) | -1.91% v -2.98% |
| best UK price | +1.79% (91), p 0.000 | | |

By week against Hill (Bet365): W44 +1.28% (35), W45 +1.32% (31), W46 +2.11%
(15), W47 -1.96% (1 pick). Steady, not one week. BetVictor and Betfair are
behind Hill in every week (3 of 3, 4 of 4). Against the average Bet365 is best
on 79% of its priced legs, Hill 50%, Betfair 20%, BetVictor 12%.

Bet365 is the best-paying book on every cut, by 1.4% a pick (about 4% on a
three-pick group) at the first price and 0.9% at the last. It is a price edge
on football picks, which are 82 of the 211 legs with two books priced. It does
not turn the Card's return positive on its own.

## When

All Card-rule legs: first to last pre-start price +1.06% mean (83 drifted, 89
shortened, 39 flat), p 0.088 (read "take late"); settled singles 200 legs, 147
won, return -0.53% at the first price and +0.31% at the last, gain +0.84,
p(late no better) 0.29: **no clear read**, as on 12 Nov. By sport: football
+0.33% (p 0.27, no read), NBA +2.97% (59, p 0.14, no read). The NBA drift sits
in the 00 UTC first-price hour (22 legs, +8.7%), the football in 00 UTC too
(58, +1.4%) against 19 UTC (56, +0.07%); both are the two daily pricing
passes, not hours a person could choose. The last price sits a median 1.3 h
before the start (167 of 211 within 3 h). Nothing supports moving a push time
in `notify.py` either way.

## Not changed

`CARD_BOOK` stays William Hill. Bet365 passes every price test (paired,
settled, both pricing times, weekly), but the book is where Douglas bets
(the Hill chips were built at his request), and this is a choice of account,
not a leg rule, so the delegated Card-return decisions do not reach it. If he
wants the Card written for Bet365 the one-line change is `CARD_BOOK =
"Bet365"` in `groupings.py` (the page's combined price, copy slip and the
paper cards follow it). `notify.py` push times unchanged.

## Files

`tools/price_timing.py` (`book_weekly`, `hours_by_sport`), `tests/test_book_vs.py`.
