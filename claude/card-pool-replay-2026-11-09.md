# The Card replayed on the archived pool (9 Nov 2026)

Issue #154, first slice, by the scheduled build session. Douglas's objective
(9 Nov 2026): consistent returns on the group accumulators. The Card is chosen
from the priced pool, every sport; `tools/card_replay.py` rebuilt it from the
football-data-priced archive rows only (a few dozen football legs a day), so
the nightly review compared variants on legs the Card never saw and missed
the tennis, NBA and rugby legs it really chose. This note is what the pool
holds, what it could not hold, and what changed.

## What the pool held, 30 Oct to 9 Nov

`groupings-archive/pool-<date>.json.gz`, 14 files, 2,113 legs (read only):

| state of the leg as archived | legs |
|---|---|
| real bookmaker price at first write (`fair`, `bookOdds`, `opp` where the source gave it) | 564 (27%) |
| first written as the model's estimate, a real price later (`lastOdds`, `lastBest`, `lastOpp`) | 810 (38%) |
| estimate only, never priced before the start | 739 (35%) |
| carrying a first-write `opp` | 16 |
| carrying `lastOpp` (from 6 Nov) | 604 |

The pool is written up to three days ahead, before most books price a game
(ESPN's NBA prices appear on the day; API-Sports' free plan stops at
tomorrow). `archive_pool` wrote each leg once with the numbers it first
carried and then moved only `lastOdds` / `lastBest` / `lastAt` / `lastOpp`.
So for 810 legs the pool kept no bookmakers' chance, no books and no first
real opposition price: the Card rule (`card_fault`) cannot be applied to
them. Nearly every NBA and tennis leg the live Card took is in that set.
Pool rows also carried no `id`, so tennis and US-sport legs could not be
settled by `groupings.settle` at all.

Replay of 30 Oct to 8 Nov on the pool as it stood (first real prices only,
football by names, tennis and US sport by names): 509 settled legs, live
rule no groups on any day, `rule5` 4 groups. The real Card published 18
full-rule groups over those days. The pool could not reproduce the Card it came from.

## What changed

- `groupings.archive_pool`: a leg first written as an estimate takes a
  `priced` block once, from the first build that carries a real price
  before its start (`PRICED_KEYS`: odds, best, bestBook, bookOdds, margin,
  src, pricedAt, fair, implied, p, edge, opp, draw, plus `at`). `lastFair`
  joins the last-price fields. `POOL_KEYS` gains `id`, `listOff` and
  `timeEst`, so tennis and US legs settle and `card_fault` sees the flags.
  Nothing first written changes.
- `tools/card_replay.py`: from `POOL_FROM` (30 Oct 2026) the legs come from
  the pool (`pool_legs`): the row's own market when it was priced at first
  write, else its `priced` block; estimate-only legs are left out and
  counted; results through `groupings.settle` with name fallbacks for rows
  that predate `id`. Football-data archive rows stand before 30 Oct.
  `--no-pool` is the old behaviour; `--closing` prices each pool leg at its
  last pre-start price; `--recover` also admits the 810 estimate-first legs
  at their last price with the typical margin (`groupings.MARGIN`), as the
  live pipeline prices a one-sided source. The JSON report carries `source`
  (legs by sport, what was left out) and the review issue prints it. A
  variant identical to live now says so instead of p(worse) 0.00.
- `tools/card_integrity.py`: `pool-unpriced`, a leg first archived from
  10 Nov as an estimate that later took a real price but has no `priced`
  block, so a regression in `archive_pool` opens an issue the next night.
- `tests/test_card_pool_replay.py`: the block written once and never for a
  real-first leg, the replay on a synthetic pool file (row, block,
  estimate-only, closing, recover, pending, tennis by id and by names, NBA
  by names), the integrity check.

## The recovered read, 30 Oct to 8 Nov (approximate, not evidence for a rule)

`python3 tools/card_replay.py --since 2026-10-29 --recover`: 1,266 settled
legs (football 684, college basketball 253, tennis 141, college football 96,
NBA 58, rugby 17, NFL 17), 810 of them at their last price with an assumed
5% margin. Live rule: 5 days, 9 groups, 4 won (39% expected), +5% on 16
units, legs 19 of 28 (68% v 74% quoted). `short` (1.15-1.35): 7 groups, 4
won, +29%, legs 20 of 24. `rule5` (no opposition rule): 7 days, 18 groups,
8 won, 0%. Football legs before 6 Nov carry no `lastOpp`, so the live rule
is sport-only on those days. Closing prices and an assumed margin: read the
direction, and only once the `priced` block has three weeks of real first
prices (the 30 Nov review) does the pool replay carry weight.

## What is next on #154 and #155

- Once `priced` has accumulated, the nightly review's pool section is the
  comparison the issue asks for; nothing else to wire.
- #155 (empty-day fillers) can measure empty days from the record now and
  test `opp7`, `short` and the Championship-tier leagues on the pool replay
  from mid-November; before that, `--recover` gives the approximate read.
- Pool rows written before 10 Nov will never carry `priced`; the
  football-data archive rows and `--recover` are the only reads on them.
