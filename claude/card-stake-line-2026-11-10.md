# The Bets page stake line: why it is not built (10 Nov 2026)

Kofi (Value Analyst), HQ task `hq-card-stake`: one line on the Bets page, the
unit size for a stated bankroll that keeps a 95%-worst season's drawdown to
half, from the replay, never the live record (Rule 1).

## What the replay holds

`tools/card_legs_history.py` re-run on 10 Nov (so `groupList` exists, which the
9 Nov file lacked), fit and check seasons:

| replay | fit 2025-26 | check 2026-27 |
|---|---|---|
| current rule (`card`, rules 5 and 6) | 0 groups | 0 groups |
| `cardRule5` (no opposition rule) | 22 (10 won v 7.0 expected) | 0 |
| `cardUncapped` | 6 | 4 |
| `cardOpp7` | 3 | 0 |

Under rule 6 the football-only Card makes no group on either season (one in
five seasons, `claude/card-seasons-2026-11-09.md`). The live Card is tennis and
NBA, which football-data cannot replay. So `tools/staking.py`'s replay row is
still "too few groups" and there is nothing to state a bankroll from.

## The closest read, not shipped

`cardRule5` groups, page stakes (2 units a 2x, 1 a 3x), 4000 bootstrap draws:
a season of 66 groups has a 95%-worst drawdown of 23.4 units, so a bankroll of
47 units keeps that drawdown to half; the median profit is +20.5 units. That
is one season of one superseded rule with 22 real groups (10 won v 7.0
expected, a lucky run). Presenting it as "unit = bankroll / 47" would be a
number the evidence does not carry, and the live Card at 2.5 groups a day
(tennis, NBA) has a far larger drawdown (live read 480 units a season, which
is not to be used as the answer either).

## Decision

No page line, no code change (Rule 10: do not build what will not deliver).
`tools/staking.py` already prints the month and season bankroll the moment the
replay side holds 10+ groups. Build the line when the pool replay
(`card_replay.py` from 30 Oct, real prices, every sport) holds 100+ groups of
the current rule, which is also the 30 Nov review's sample; the line then reads
`units = ceil(2 x p95 season drawdown in units)` from that replay, and the
bankroll is the user's stated figure divided by it.

Not changed: `CARD_STAKE`, `CARD_RULE`, any record, the Bets page.
