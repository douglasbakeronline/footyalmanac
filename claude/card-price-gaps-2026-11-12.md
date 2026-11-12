# The Card's price gaps: legs a missing price alone keeps off (12 Nov 2026)

## The question

The Card built nothing for 11 or 12 Nov. The funnel (`tools/card_funnel.py`)
reads only legs at a real bookmaker price; every other leg is counted as
"estimate only" and left out (943 from 6 Nov). If many of those would clear
the Card's rule once priced, a fuller price feed is the cheapest way to more
groups. If few would, the price feed is not the lever.

## What was added

- `card_funnel.unpriced_ok(row)`: an unpriced pool leg read with the live
  `card_fault` at a stand-in price inside `CARD_ODDS` and no bookmakers'
  chance (under rule 7+ the price is tested first, and the value demand
  cannot be read without one). Under rule 6 its fault must be the missing
  price itself.
- `card_funnel.price_gaps(since, until, today)`: those legs by day, sport and
  competition, split into days already started (lost) and days still to come
  (may yet be priced: the pool is rewritten every build).
- Printed by `tools/card_funnel.py` and in the nightly Card review, under the
  funnel, from 10 Nov only (when every leg began carrying its first real
  price; before that an estimate is the archive's gap, not the feed's).

## The read at 12 Nov 2026 (morning)

| from | lost (started days) | still to come |
|---|---|---|
| 10 Nov (real prices kept) | 4 (football 3, tennis 1) | 57 (football 56, NBA 1) |
| 6 Nov with `--recover` | 61 (football 59) | 57 |

Since 10 Nov a missing price has cost the Card four legs over two days:
Ýokary Liga (Turkmenistan) 2, Eerste Divisie 1, a DIRECTV Open first-round
tennis match 1. None of those days was one leg short of a group: 11 Nov had
five NBA picks clear and failed on the 2x band (`claude/card-m7legs2-2026-11-12.md`).
The 6-9 Nov figure is the archive gap that `priced` closed on 9 Nov, not the
feed.

The 57 still to come are mostly 14-15 Nov lower-tier football (NB III,
Tercera RFEF, Regionalliga, Oberliga); whether they are priced by kick-off
is what the nightly line will show.

## What it means

Price coverage is not what is starving the Card at present; the 2x band and
the value demand are (`claude/card-funnel-rule7-2026-11-11.md`). Revisit if
the "lost" column grows past a handful a week, or if the weekend's
to-come legs mostly go unpriced. A priced leg must still clear the value
demand, so the column is the most a fuller feed could add.

Nothing here changes a rule or the page. Advisory.
