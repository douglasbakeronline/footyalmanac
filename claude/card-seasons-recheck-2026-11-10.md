# Card over 2022-23 to 2024-25: task already done (10 Nov 2026)

The HQ planner asked for the Card's leg rule and whole Card to be replayed on
2022-23, 2023-24 and 2024-25 football-data.co.uk prices, by season: legs landed
v quoted, singles return, the Card's return and losing months, by gap band and
by the opposition's price band. That was done on 9 Nov 2026 (issue #153,
`tools/card_legs_history.py --seasons 2022-23,2023-24,2024-25`, CI run
42543472973, then 42546496524 for the whole-Card variants). Nothing new was
run here: the sandbox cannot reach openfootball or football-data, and a rerun
would reproduce the same numbers.

Where each requested table lives, all in `claude/card-seasons-2026-11-09.md`
(raw output in `claude/card-seasons-2026-11-09-output.txt`):

| asked for | section |
|---|---|
| legs landed v quoted, singles return | "The legs" (under-market cut lands 70.9-73.3% v 68.0-69.1% quoted; singles -1.0% to +0.8% at average price, +1.7% to +3.3% at best) |
| gap band | "By how far the model sits under the market" (no band positive in every season) |
| opposition's price band | "By the opposition's price" (9+ lands ~5 points over quote in all five seasons, +4% pooled; 4-6 loses in all five) |
| Card return, losing months | "The whole Card" (rule 5: 93 groups, 37 won v 31 expected, +4.4%, 3-5 losing months a season) |

Answer to "does the rule hold across seasons": the opposition condition
(rule 6) does; the gap cap (rule 5) is not supported; the football-only Card
is too thin (0 to 1 group a season under rule 6) to earn a bankroll alone.
No gate was met by any new variant, so no rule changes. Open decisions stay
as recorded in CLAUDE.md: `uncapped` and `opp7` at the 30 Nov review, on the
pool.
