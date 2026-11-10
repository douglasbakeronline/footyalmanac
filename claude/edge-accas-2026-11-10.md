# Edge picks as accumulators, five seasons (10 Nov 2026)

Douglas bets accumulators of Daily List picks and was losing
(`claude/list-accas-2026-11-10.md`); he asked for the most efficient way to
win big, then for a development that would impress him. This answers the
accumulator question on the one leg with a tested edge: the green Edge flag
(`claude/edge-flag-2026-11-10.md`), football favourites at 1.15 to 1.90, the
bookmakers 60%+, the opposition priced 9+, the model no more than 5 points
above the market.

## The test

`tools/card_legs_history.py` `edge_legs` / `edge_accas`: on each
football-data season (walk-forward, the season before as prior, prices never
tuned on), for each day with at least k flagged legs, the k most likely by
the bookmakers' chance as one accumulator, and every flagged leg of the day
as one slip. Run in CI (`card-legs-history.yml`, run 42751060085) on
2022-23 to 2026-27; the weekly `tune.yml` keeps the fit and check seasons
current in `card-legs-history.json` (`edgeAccas`), which the page reads.

## The result

Pooled over five seasons:

| slip | slips | won | return, average price | return, best price | best price ahead |
|---|---|---|---|---|---|
| single (the day's most likely) | 459 | 388 (84.5%) | +3.0% | +5.4% | 4 of 5 seasons (2026-27 -0.4%) |
| double (two most likely) | 252 | 170 (67.5%) | +0.1% | +4.6% | 4 of 5 (2026-27 -6.3%) |
| treble | 149 | 88 (59.1%) | +8.6% | +16.1% | 3 of 5 (-29% to +51%) |
| four-fold | 78 | 39 (50.0%) | +11.6% | +22.0% | 4 of 5 (-46% to +99%) |
| every Edge pick of the day | 252 | 139 (55.2%) | +2.4% | +9.7% | 4 of 5 (2022-23 -12%) |

By season, best price, every Edge pick of the day: 2022-23 -12.0%, 2023-24
+13.2%, 2024-25 +13.8%, 2025-26 +22.6%, 2026-27 (13 days) +16.0%. Singles:
+5.2%, +3.2%, +5.0%, +9.9%, -0.4%.

## What it means

- The Edge leg carries a small, real edge over the bookmakers' chance in
  every season (83-89% landed against 77-78%), so combining legs compounds an
  edge rather than a margin, which is the opposite of the Daily List accas.
- It needs the best price. At the average price singles make about 3% and
  doubles break even.
- Longer slips raise the pooled return and the swing together: trebles and
  four-folds lose a third to a half of their stake in a bad season. The
  efficient choice is singles (steadiest) or every Edge pick of the day as
  one slip at the best price (more return, one losing season in five).
- Caveats: football-data's best price is the maximum across many books, a
  touch kinder than one account at one book; 2026-27 is 13 days; Edge picks
  are rare (about 50 to 60 days a season with two or more).

## On the page

The Bets tab has an **Edge picks** section under the card for the chosen
day: every flagged fixture with its average and best price, the opposition's
price and both chances; the Edge double and every Edge pick as one slip,
priced at the average and the best price with the bookmakers' chance it
lands; the latest seasons' tested lines (`D.edgeTested`, from
`card-legs-history.json` via `build.edge_tested`), the five-season summary
above, and the flag's own record on this site. Display only; nothing is
staked or pushed, and the Card is unchanged.
