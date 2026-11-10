# Daily List picks as accumulators (10 Nov 2026)

Douglas, 10 Nov 2026: "I'm losing too much on daily list picks". He bets
accumulators of many list picks. This is the investigation he chose before
anything changes, and the evidence behind the deck "Betting the Daily List"
sent to him the same day. Nothing on the page or in any rule changed.

## The tool

`tools/list_accas.py`. Part 1 reads every sport's graded Daily List picks
(`record-graded.json`, `tennis-record.json`, `sports.graded_games()`), orders
each UK day's picks as the page does (confidence first) and takes the top N as
one accumulator, N = 1 to 10 and the whole day: landed against the product of
the quoted chances. Part 2 reads the priced pool from 30 Oct (list picks with
a real price and a result, `card_replay.pool_legs`) and gives the same
accumulators' return at the average price beside the bookmakers' own
expectation (their fair chance times the price). `--recover` admits legs
before 10 Nov at their last price. Tests: `tests/test_list_accas.py`.

## The read

The picks are honest: 458 graded list picks, 85.8% landed against 84.9%
quoted (football 83.0 v 82.3 on 141, tennis 79.8 v 82.6 on 104, other sports
90.6 v 87.7 on 213).

Combined, they still land as quoted, within the noise (42 days):

| top N | days | landed | quoted |
|---|---|---|---|
| 1 | 42 | 92.9% | 90.5% |
| 3 | 35 | 65.7% | 71.3% |
| 5 | 27 | 48.1% | 58.0% |
| 8 | 20 | 40.0% | 40.3% |
| 10 | 16 | 43.8% | 33.7% |

The loss is the price. 118 priced list picks (`--recover`): average price
1.12, margin 5.3%, singles -0.5%. Under 1.15 (78 picks) landed 92.3% and
returned -4.6%; 1.15-1.30 (31) +4.6%; 1.30-1.50 (7) +15.9%, too few to read.
As accumulators the bookmakers' own expected return is about -5% a leg and
compounds (-14% at 3, -23% at 5, -41% at 10); on ten days of real prices
the outcome was worse (-32% at 3, -55% at 5, -75% at 8), a small sample.

## What it means

There is no data-backed way to win big with long accumulators of list
picks: the list never sees a price, by Douglas's standing decision, so its
legs carry the full margin and every leg adds it again. What the data does
support is the Card's own conditions applied to a short accumulator: legs
priced 1.15+, football favourites whose opponent is priced 9+ (511 legs over
five seasons, 83.8% v 76.2%, +4% average, +7% best), the best UK price, flat
small stakes. An accumulator multiplies whatever each leg has, an edge or a
margin. The deck says so, with the live Card's -12% on 35 groups beside the
replay's +4.4% so the expectation is honest.

## Next, offered to Douglas

Each Daily List pick's bookmaker price on the page with a plain mark (no
value under 1.15; edge when it meets the Card's conditions), display only,
the model still never sees a price. And this tool's accumulator lines in the
nightly Card review so the priced sample grows daily. Neither is built.
