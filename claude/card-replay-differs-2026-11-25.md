# The Card replay: how many days a variant differs from live (25 Nov 2026)

Build session, 25 Nov 00:34 London slot. Five days before the 30 Nov review.

## The finding

The nightly Card review's archive table gives each variant a `p(worse)` against
live and gates it on 100+ legs. Both were read on every day and leg the
variant built, but most variants build the same groups as live on most days,
and a shared day adds nothing to the comparison. The 24 Nov review showed
`m7cap160` at +0.22 a day, **p(worse) 0.0**, on 27 legs: it differs from live on
two days and three legs. No other variant reads 0.0, so a reader of the table
could take it as the strongest result on the page.

## What changed

`tools/card_replay.py` `pair_days(a, b)`: the pairing loop factored out, plus
the days whose groups differ from live's (by picks, event and stake) and the
variant's legs on them, written as `daysDiffer` / `legsDiffer` on every
variant paired with live. The review's archive table has a "differs: days /
legs" column, and the "Ahead of live but under the 100-leg gate" line names
them. `flatstake` differs on every day by stake alone, so stake counts.

## The read on 25 Nov (pool from 29 Oct, first prices, 28 days)

| variant | v live / day | p(worse) | legs | differs: days / legs |
|---|---|---|---|---|
| m7cap160 | +0.22 | 0.0 | 27 | 2 / 3 |
| comp3 | +0.13 | 0.351 | 36 | 2 / 9 |
| fillrule5 | +0.44 | 0.208 | 48 | 4 / 18 |
| pay15 | +0.79 | 0.095 | 28 | 11 / 28 |
| ladder | +0.16 | 0.316 | 40 | 11 / 40 |
| span2 | +0.23 | 0.395 | 39 | 12 / 33 |
| rule12 | +0.09 | 0.463 | 72 | 17 / 69 |
| rule13 | +0.23 | 0.324 | 120 | 21 / 120 |
| m7opp5 | -0.08 | 0.668 | 30 | 2 / 6 |

Rule 13, the one variant at the 100-leg gate, differs from live on 21 days and
every one of its 120 legs, so its read stands as printed. `m7cap160`'s 0.0 is
two days. `pay15` (+0.79, p 0.095) is the strongest result with real
evidence behind it, on 28 legs, well under the gate.

## Not changed

The gate (`candidates`: p(worse) at most 0.30 on 100+ legs, the variant's
legs) is as CLAUDE.md states it. Whether it should count `legsDiffer` instead
is a question for the 30 Nov review; today nothing passes it either way
(rule 13's legs are all differing legs, p 0.324). No Card rule, no record, no
replay number moved.
