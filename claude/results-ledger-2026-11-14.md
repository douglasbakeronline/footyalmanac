# The results ledger, 14 November 2026

Douglas, 14 Nov 2026: "are we storing every result against our prediction so we
can learn from it?" Then: build a permanent graded file for the other sports,
a weekly ungraded report, and prices beside each result.

## What was missing

- `sports-record.json` keeps 14 days of game rows. `graded_games` regrades
  everything from `history-sports/` on each build, but only totals survived,
  so an October rugby, NFL or college football pick could not be read on its own.
- About 650 predictions had no result 3+ days after the start, unseen.
- No file held a pick's result beside the price it could have been backed at.

## What now exists

- `sports-graded.json` (`sports.write_graded`): every graded and void pick of
  the other sports, form and rating detail dropped, merged by id, never trimmed.
- `results-ledger.json.gz` (`ledger.py`, after `groupings.py` in deploy.yml):
  one row a prediction, every sport.
  - Prediction: the latest archived copy published before the start. A moved
    football fixture (same pairing, starts within `MOVE_DAYS`) is one row, its
    latest placement; US sports group by the feed's id (an MLB series is three
    games); tennis by pairing within `TENNIS_MOVE_DAYS` with ids that agree
    (old tennis archives have no id; the same players met twice a week apart).
  - Result: `record-graded.json`, `tennis-record.json`, `sports-graded.json`.
    Football rows from before publish times (882 `legacy-unverified`) stay out.
  - Price: `first` (earliest) and `last` (latest before the start), each
    `{o: average or pool price, b: best, bb: best book, h: William Hill, n: books,
    src, t}`. From the football archive's `market` (picked side only), the pool
    (`groupings.pool_rows`; estimates never kept) and this build's
    `groupings.json` `prices` for games not yet started.
  - `summary`: by sport, list / reserve / board, band: n, won, rate, quoted,
    and flat return `ret` (recorded price), `retBest`, `retHill`, each over the
    picks priced that way only. `priceCover` says how thin each is.
  - `ungraded`: pending 3-14 days (`chase`, by competition, list picks named)
    and 14+ days (`stale`). Printed every build; `::warning::` on the first
    build of each UK Monday.

## First read (local run on the repo's archives, 14 Nov)

15,983 predictions; 186 ungraded 3-14 days (1 list pick: Istiqlol v
Istaravshan, 7 Nov), 466 past 14 days.

Price coverage of settled picks: football 4,615 of 11,077 (104 with Hill),
tennis 136 of 1,440, college basketball 449 of 598, NBA 96 of 183. Hill is thin
everywhere: it is only read for Card candidates and list picks since 10 Nov.

Daily List picks with a recorded price:

| Band | Priced | Landed | Quoted | Avg price | Break-even | Return |
|---|---|---|---|---|---|---|
| 75-85% | 65 | 86% | 80% | 1.19 | 84% | +2.2% |
| 85%+ | 145 | 92% | 91% | 1.06 | 94% | -2.2% |

The 85%+ priced picks are 124 college basketball at about 1.03. Small samples;
the point is that landing more often does not mean winning money, because the
price shortens faster than the hit rate rises. Read again at the month's end.

## Not done

- Hill prices for every game: the build reads UK slates only for Card
  candidates and list picks (The Odds API credits).
- The page does not read the ledger.
