# The Card review's Coverage line, read by the rule each day ran (24 Nov 2026)

Build session, 24 Nov 2026, 15:17 London. No Card rule changed; `CARD_RULE`
stays 14 until the 30 Nov read.

## What was wrong

The nightly review's Coverage line set every live Card group the record holds
over the replay's window (29 Oct on, rules 1 to 14) against the replay's
`live` row, which is rule 14 alone, and put the gap down to legs archived
only as estimates. On 24 Nov it read, in bold, "the record holds 33 live Card
groups; the replay rebuilt 10". Most of that gap is the rule, not the
archive: the record's 33 were built under seven rules, the replay's 10 under
one. Read cold before the 30 Nov review, it says the pool replay misses two
thirds of the Card, which overstates how little the replay can see.

## The fix

`tools/card_replay.py` writes `groupDays` (groups by day) for every variant
and on each `rules` row. `card_review_post.rule_coverage` counts the record's
settled full-rule Card groups by the rule each ran under and sets them beside
that rule's own replay on its own live days (`RULES` spans), settled days
only, today left out. Groups dated outside their rule's span (built the day
before a switch) are named. The estimate-era explanation is kept only for
groups before 10 Nov, from when every pool leg carries its first real price.
A replay file without `groupDays` falls back to the old line.

## The read on 24 Nov (local replay, first prices, window 29 Oct to 23 Nov)

| rule | record groups | replay of that rule, same days |
|---|---|---|
| 1 | 2 (both dated after its span) | 0 |
| 4 | 5 (2 after its span) | 0 |
| 5 | 10 | 1 |
| 6 | 5 | 1 |
| 11 | 4 | 5 |
| 13 | 4 | 2 |
| 14 | 3 | 4 |
| all | 33 | 13 |

21 of the 33 fall before 10 Nov, where the replay rebuilt 1: that is the
estimate-only archive, as the old line said. From 10 Nov the record holds 12
and the replay of the day's rule 12 (rule 6 1 v 1, rule 11 4 v 5, rule 13
4 v 2, rule 14 3 v 4): the pool sees the Card's volume once the
archive carries real prices, and the remaining differences are which picks
(the price read, `claude/card-replay-price-fidelity-2026-11-24.md`).

## For the 30 Nov read

The replay is a fair read of rules 11 to 14 on their own days; for rules 1
to 6 it is not, and their replay rows should be read as what the rule would
do on today's archive, not as a reproduction of what was staked.

Tests: `tests/test_rule_coverage.py` (five).
