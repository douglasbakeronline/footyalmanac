# The Bets page stake line: still not built (18 Nov 2026)

Kofi (Value Analyst), HQ task `hq-card-stake`, set again by the planner on 17 Nov.
Follows `card-stake-line-2026-11-10.md`, whose build condition was: the pool
replay (`tools/card_replay.py`, real prices, every sport, from 30 Oct) holds 100+
settled groups of the current rule. Re-checked against that condition.

## Numbers today

- Pool replay of the live rule (`card-replay-pool-recheck-2026-11-18.md`):
  26 groups over 20 days, 13 won v 39% expected. Gate for a stake line: 100.
  At 1.3 groups a day that is about 55 more days, so around mid January.
- `tools/staking.py` replay row (football-data, `card-legs-history.json`):
  33 groups, 17 won v 13.4 expected, but these are superseded rules (the
  `card` key is rule 5/6 football only; check season holds 1 group). At the
  page's stakes a season of 16 groups has a 95%-worst drawdown of 14 units
  (bankroll 28), a month of 4 groups 8 units (16). That source is not the
  Card the page builds (2x alone, tennis, NBA and the wider leagues, the
  model's own picks), so it is not used for a stated unit.
- Live record (read only, Rule 1): 40 groups, 13 won v 13.7 expected, used
  here only to locate the gap: the live Card's drawdown per group is far
  above the football replay's, so a football-only figure would understate it.

## Decision

No page line, no code change (Rule 10). Printing "unit = bankroll / N" from 26
groups, or from a superseded football-only replay, would state a precision the
evidence does not carry, and the line is meant to protect people's money.
`tools/staking.py` already prints the month and season bankroll in the nightly
Card review on the live-rate basis; the page line is built when the pool
replay holds 100+ groups, as `units = ceil(2 x p95 season drawdown)` and a
stated bankroll divided by it. Do not reassign until then.

Not changed: `CARD_STAKE`, `CARD_RULE`, `tools/staking.py`, any record, the page.
