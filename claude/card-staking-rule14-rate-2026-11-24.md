# The live bankroll's rate read from the live rule's start (24 Nov 2026)

Build session, 24 Nov 2026, 09:17. The nightly Card review's "Staking, live"
lines sized the month's and season's bankroll at 0.85 groups a day, the rate
since `staking.RATE_FROM` (11 Nov). Since `CARD_RULE` 14 (19 Nov: core
leagues, the value demand, no two-day groups) the Card builds fewer groups
than rules 11 and 13 did.

## The numbers (groupings-record.json to 23 Nov)

| span | groups | days | a day |
|---|---|---|---|
| 11 to 23 Nov (`RATE_FROM`, rules 11, 13, 14) | 11 | 13 | 0.85 |
| 19 to 23 Nov (rule 14 only) | 3 | 5 | 0.60 |

So the review's month put about 25 groups and 43 units staked into the
bankroll where the live rule makes about 18. The outcomes behind the
bootstrap are unchanged (every settled full-rule group); only the count of
groups a month and a season moves.

## The change

`tools/staking.py` `groups_from_record` now takes its rate from the live
rule's first day, read from the same review run's `card-replay.json` (`rules`,
the row whose variant is `live`, from `card_replay.RULES`), once that span has
`RATE_MIN_DAYS` (7) days to the record's last day. Until then, or without the
file, `RATE_FROM` stands as before. Rule 14 reaches seven days on the record
dated 25 Nov, so the review of 26 Nov is the first to read it. A future
`CARD_RULE` needs only its `RULES` row, which every rule change already adds.

Tests: `tests/test_staking.py` (the live rule's start once it has a week,
`RATE_FROM` before that and without the file); the first fails on the old code.

Advisory only. No Card rule, stake or record changed.
