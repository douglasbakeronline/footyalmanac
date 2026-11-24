# The List card built on its own day, one kind a day (24 Nov 2026)

## What was wrong

The List 2x and List long (`groupings.build_list_card`, on trial since 17 Nov)
were held as first built until their first start, the same early hold the
Daily 2x lost on 23 Nov (`claude/daily-2x-on-its-day-2026-11-23.md`). The
builds look three days ahead, so a List slip could be fixed on the picks
priced days before. And the rule "the List long only when the 2x cannot be
made" was checked one way only: a held List long never stopped a List 2x
being built later beside it.

The whole List card record (`groupings-record.json` `cardList`,
`cardListLong`, four groups) is two days, each with both kinds:

| Day | Kind | First built | Price | Picks | Shared with the other |
|---|---|---|---|---|---|
| 21 Nov | List long | 20 Nov 22:41 UTC | 2.02 | 5 | 2 (Cosmos, Esperança d'Andorra) |
| 21 Nov | List 2x | 21 Nov 04:43 | 2.27 | 4 | |
| 22 Nov | List long | 19 Nov 16:49 | 2.22 | 5 | 3 (Beerschot VA, Chicago Bears, Denver Broncos) |
| 22 Nov | List 2x | 21 Nov 11:08 | 2.24 | 4 | |

Each long was built when the day's list could not yet reach 2x at 1.15+
(later prices had not arrived), then the 2x formed and was published beside
it. The record so far (List 2x 1 of 2, List long 2 of 2) is these slips;
nothing in it is changed.

## The change

- A List 2x or List long that has not started is rebuilt on every build
  until 07:00 UK on its day, as the Daily 2x is; from the first build after
  that it is held as first built until its first start, as before.
- One List kind a day: a List 2x is no longer built beside a List long that
  is held or archived. Before 07:00 the rebuild gives the 2x its priority;
  after it, the slip published stands.

`tests/test_list_card.py` `ListOnItsDay` (four tests, each failing on the old
code): a long built early gives way to the 2x before the day; a long held
from the day keeps its place and no 2x is added; an archived long blocks a
2x; a 2x is rebuilt until the day.

## Not changed

`LIST_KINDS`, the price floors, the legs cap, the tiers, the Card, any
record or archive. Only locked slips are archived, so the rebuilds leave no
trace. The 30-settled-group read in `claude/list-card-2026-11-17.md` stands;
it now reads slips built on the stated rule.
