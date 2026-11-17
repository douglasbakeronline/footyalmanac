# The football-data Card replay spans two days too (17 Nov 2026)

## What was wrong

Since earlier today the pool replay's `live` builds two-day groups, as the
page has since 12 Nov (`claude/card-replay-live-span-2026-11-17.md`). The
football-data side of the gate (`tools/card_legs_history.py`, `card_season`)
still built day by day. So the gate compared each variant against two
different lives: the page's Card on the pool, a Card with no two-day groups
on the five football-data seasons.

## What changed

`card_season` uses `card_replay.spans` and `card_replay.build_span`, the
same rule as the pool: every live-machinery variant spans while
`CARD_SPAN` is on; the rule 6 family and the paper Model card do not.
`nospan` (the rollback, `CARD_SPAN = False`) joins the `cardM7` list, so
every season carries the before and after side by side.
`tests/test_card_legs_history_span.py`.

## The read (CI run 44128924620, five seasons, rule 13 live)

The two-day group on football-data, live v `nospan`:

| season | live groups, won, return | nospan groups, won, return | nospan v live a day, p(worse) |
|---|---|---|---|
| 2022-23 | 118, 52, 1.040 | 98, 42, 0.974 | -0.13, 0.77 |
| 2023-24 | 82, 32, 0.911 | 59, 22, 0.869 | -0.01, 0.51 |
| 2024-25 | 145, 50, 0.795 | 125, 47, 0.857 | +0.20, 0.14 |
| 2025-26 | 109, 46, 1.010 | 92, 38, 0.964 | -0.08, 0.67 |
| 2026-27 | 22, 13, 1.345 | 17, 10, 1.320 | -0.15, 0.67 |
| pooled | 476, 193, 0.950 (1,430 legs) | 391, 159, 0.933 | -0.01, 0.55 |

Two-day groups add about a fifth more groups at the same or a slightly
better return in four seasons of five. `CARD_SPAN` stays.

The variants against the spanning live, pooled over five seasons:

| variant | groups | return | v live a day | p(worse) | seasons ahead |
|---|---|---|---|---|---|
| rule12 | 218 | 1.026 | +0.14 | 0.11 | 3 of 5 (behind 2022-23, 2026-27) |
| m7value | 229 | 1.024 | +0.14 | 0.11 | 3 of 5 |
| m7opp5 | 455 | 0.969 | +0.05 | 0.21 | 3 of 5 (2025-26 now -0.12, p 0.82) |
| comp3 | 479 | 0.955 | +0.01 | 0.28 | 2 of 5 |
| pay15 | 803 | 0.975 | +0.01 | 0.44 | 2 of 5 |
| pay3 | 526 | 0.944 | -0.02 | 0.58 | 2 of 5 |

No variant passes the gate (ahead on both recent football-data seasons and
the pool, p(worse) 0.30 or under on 100+ legs). `m7opp5`, which led on
2025-26 against the day-by-day live (+0.10, p 0.32), is behind the spanning
live there (-0.12, p 0.82).

For the 30 Nov review: over five football-data seasons the rule 13 Card
(the model alone, Douglas's call today) returns 0.950 a unit; rule 12 (the
value demand and the 5.0 opposition floor) 1.026, ahead in three seasons
of five. The pool reads the other way on 14 to 18 days (rule 12 -1.09 a day,
p(worse) 0.90). Neither side settles it; rule 13 stays live as the owner's
call, and the numbers go to Douglas with the review.

No Card rule changed; nothing on the page. The Monday `tune.yml` run
commits these numbers to `card-legs-history.json` (fit and check seasons).
