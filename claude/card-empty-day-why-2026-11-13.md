# Why a day has no Card group, and the two-day group's search (13 Nov 2026)

Since rule 7 (11 Nov) the Card has built no group on 11, 12 or 13 Nov. Two
things were found reading the pool for those days with the live functions
(`tools/card_funnel.pool_days`, first real prices).

## 1. The two-day group gave up too early (bug, fixed)

`build_card`'s `CARD_SPAN` pass asked `best_card` for the best group of the
day's picks and the next day's together, then refused it if it held none of
the first day's. When the next day's own picks made the best group, the span
built nothing, even where a group holding a first-day pick existed. That is
not what was asked for ("look to the next day ahead to combine fixtures to be
able to create a card", Douglas, 12 Nov) or what `claude/card-span-2026-11-12.md`
describes.

`best_card` now takes `need`, a test at least one pick must pass, applied
inside the search; a needed pick ranked past the `CARD_POOL` cut still
competes. The span pass and `card_replay.build_span` (`span2`) pass it. Tests:
`tests/test_card_span.py` (`test_best_group_holding_its_own_pick` failed on
the old code). No `CARD_*` constant changed; the span is the owner's rule,
now built as he described it.

On the pool to 15 Nov the overall best group already held a first-day pick
on 13 Nov (Knicks with VVV-Venlo and the Timberwolves, 2.69), so the fix
changes no group on these days; it closes the case for the next.

## 2. The empty-day message was wrong

The Bets tab said "too few picks clear the rule so far ... a group appears
as soon as three picks qualify". On 13 Nov three picks qualified (Karbon
Cherkasy 1.67, Ospitaletto 1.50, Knicks 1.40) and together paid 3.51, over
the 2x group's 3.00 top. 15 Nov reads the same: three picks, cheapest set
3.19.

| day | picks clearing the rule | why no group |
|---|---|---|
| 10 Nov | 1 | few |
| 11 Nov | 7 | (a group builds on the replay; rule 11 shipped after its picks started) |
| 12 Nov | 1 | few |
| 13 Nov | 3 | long: cheapest set 3.51 |
| 14 Nov | 6 | (a group builds) |
| 15 Nov | 3 | long: cheapest set 3.19 |

`groupings.card_short` (per day in `groupings-data.js` as `cardShort`, only
on a day with no Card group) names the reason: few, spread (too many from one
competition), long, short or chance (under the floor), with the cheapest or
dearest set. `cardShortText` in `index.html` says it in a line. Display only.

## What this does not change

The 2x band (2.00 to 3.00) is rule 8's, on the payout-band replay
(`claude/card-payout-bands-2026-11-11.md`: the 2.5x and 3x bands lost). The
"long" days are the 3x the Card stopped building; `with3x` keeps replaying
it (pool to 14 Nov: -12.4% v live -16.6%, p(worse) 0.59). Nothing here is a
reason to widen the band.
