# The Card's bankroll read from the live rule's replays (18 Nov 2026)

Build session, 18 Nov 09:17 London. Follows `card-stake-line-2026-11-18.md`,
which found the nightly review's "Staking, replay" row built from a Card the
page no longer makes.

## The fault

`tools/staking.py` `groups_from_history` read `card-legs-history.json`
`seasons.*.card.groupList`: the rule 5/6 Card, football only, 2x and 3x, 33
groups over two seasons. Since `CARD_RULE` 7-13 the page builds the model's own
picks, the 2x alone, every sport, two-day groups. The bankroll the review
printed for "replay" was that old Card's.

## The change

- `card_legs_history.py` already writes the live rule's replay per season
  (`cardM7.live`, with a `groupList`). Staking reads it first and falls back to
  `card` only for a season without it (`staking._gl`).
- `tools/card_replay.py` now writes the live variant's groups (`groupList`:
  date, kind, chance, price, stake, won, legs) into `card-replay.json`, and
  staking reads them as a third source, `pool` (`groups_from_pool`): the live
  rule on the archived pool, every sport, real prices, the rate its groups over
  the replay's days with empty days counted.
- The review's staking sections are headed by source: football-data the live
  rule, the archived pool the live rule, live.

## Numbers (local run, 18 Nov; bootstrap seed 11)

| source | groups | won v expected | landed/expected | a day | month bankroll | season bankroll |
|---|---|---|---|---|---|---|
| football-data, old `card` (was printed) | 33 | 17 v 13.4 | 1.267 | 0.14 | 16 | 28 |
| football-data, live rule | 47 | 24 v 19.0 | 1.263 | 0.14 | 16 | 34 |
| pool, live rule | 26 | 13 v 10.0 | 1.294 | 1.24 | 44 | 95 |
| live record | 41 | 13 v 14.0 | 0.929 | 0.71 | 50 | 317 |

Bankroll in units at the page's stakes (two units a 2x), the 95%-worst
drawdown doubled. The committed `card-legs-history.json` is from 16 Nov, before
the football-data side built two-day groups (#392); Monday's tune.yml refreshes
it.

## Reading it

The replays of the live rule land about 1.26-1.29 times the bookmakers'
expectation; the live record 0.93. The pool replay rebuilds 26 of the record's
27 groups but on the legs it has (estimate-only legs left out), so the gap is
partly the legs and partly 41 groups of noise. The live row stays the one to
size a bankroll from; the replay rows say what the rule should do. Neither
reaches the 100 groups `card-stake-line-2026-11-18.md` set for a page line.

Not changed: any `CARD_*` constant, `CARD_STAKE`, the record, the page.
