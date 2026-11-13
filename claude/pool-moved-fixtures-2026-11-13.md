# The pool counted moved fixtures twice (13 Nov 2026)

Found while checking the context check's read of Drina Zvornik v Velež
Nevesinje (a Card-rule candidate for 13 Nov): "the date is listed as 14 Nov
(not 13 Nov) on several sites". The predictions archive had it on 14 Nov from
10 to 12 Nov, then on 13 Nov from the 22:38 build of 12 Nov. The pool held it
in both `pool-2026-11-13.json.gz` and `pool-2026-11-14.json.gz`.

## Why

`archive_pool` keys rows by (event, pick) inside one day's file. When the
source moves a fixture to another day, the next build writes a new row in the
new day's file and the old row stays, with its old start and no later price.
Nothing first written is ever changed, which is right; the readers were not
told.

At 13 Nov, 68 of 2,650 pool picks sat in more than one file: 38 tennis (most
placed a day early, then on their real day: Rune v Paul, Rublev, Djokovic,
Svitolina v Sabalenka on four days with one id), 25 football, 4 college
basketball, 1 NBA. Seven pairs more than three days apart are rematches, not
moves (New Zealand v India, Le Messager Ngozi, Ontinyent).

What each reader did:

| reader | before | effect |
|---|---|---|
| `card_replay.pool_legs` (every replay variant, `list_accas`, `edge_sports`, the nightly review) | no dedup | a moved leg settled twice, once on a day it was not played |
| `card_funnel.pool_days`, `price_gaps` | kept the first (event, pick) | kept the stale row, often the estimate-only one, and merged NBA rematches |
| `price_timing.legs` | no dedup | one leg twice |
| `list_at_book` (`listAtBook` on the page) | no dedup | three list picks twice |
| `context_record` | keyed by date | each placement once |

## The fix

`groupings.pool_rows` reads every pool file and keeps one row a fixture: rows
of one (sport, event, pick) are the same fixture when both carry the same id,
or, without ids, when their starts are within `POOL_MOVE_DAYS` (3); the kept
row is the latest placement (latest `firstAt`, then the later file), the
start the builds last judged by, priced before that start. Different ids, or
starts more than three days apart, stay two fixtures. Every reader above now
goes through it. Nothing in the archive changes.

## Numbers, before and after (pool from 30 Oct, local results index)

- Replay, first real prices: 759 to 756 settled legs (football -2, NBA -1).
  Every variant's groups unchanged.
- Replay `--recover`: 1,533 to 1,511 (tennis -17, football -3). Every
  variant's groups unchanged.
- Funnel from 6 Nov: 729 to 740 legs at a real price, 881 to 872 estimate
  only (the moved row was priced, the stale one was not; rematches no longer
  merged). Days with a live 2x unchanged.
- Price timing: 228 to 227 Card-rule legs.
- `listAtBook`: at William Hill 18 of 18 (+9.3%) to 17 of 17 (+8.5%); not at
  Hill 33 to 32, unchecked 18 to 17.
- Context tally unchanged.

No Card rule moved and no replay verdict changes: the duplicates were few and
mostly tennis under the 85% floor. The point is that the 30 Nov review reads
each fixture once, on the day it was played.

## Not changed

`archive_pool` (rows first written stay as written), the live Card (built
from the build's own legs, not the pool), `card_integrity` (looks a leg up
across the day before and after, so a move is already covered).

Tests: `tests/test_pool_rows.py`.
