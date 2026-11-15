# Scale rule 4 and Starred rows drawn as the Daily List draws them (15 Nov 2026)

## What Douglas asked for

"I don't want the [Scale] bets just for the football just to be built from
daily list picks only. I want you to scour all football fixtures and pick from
those. We need to widen the pool, otherwise there's not enough to choose
from." And: "the fixture rows in starred match that of the daily list. They
need all the information, all of the icons. They need to look identical."

## Scale rule 4 (`scale.py`)

- `GROUP_ANY_TIER = ("football",)`: a group's football legs come from every
  football candidate still to start, any tier (list, reserve or the rest at
  `FLOOR` 55%+), wherever William Hill offers the game's result-and-goals
  bets. Other sports keep `GROUP_TIERS` (Daily List only).
- Legs are ranked with everything else by the chance their own bet lands; for
  football that is the model's number for win and over 2.5 at that fixture, so
  a weaker winner with a low-scoring outlook ranks low by itself.
- `with_group_legs`: groups are built from the day's picks plus those
  candidates, and any leg taken from outside the picks joins them (archived,
  shown and graded like any other). `RULE` 4, so the days before the tab are
  replayed under it.

### The replay (1 to 14 Nov, estimated prices)

| | Rule 3 (list only) | Rule 4 (football from every fixture) |
|---|---|---|
| Double | 7 of 14, -15% | 6 of 13, -23% |
| Threefold | 3 of 12, -29% | 3 of 12, -29% |
| Fourfold | 2 of 10, +8% | 2 of 13, -41% |
| Fivefold | 1 of 7, -60% | 1 of 12, -77% |

Wider pool, more groups (fourfolds and fivefolds on 3 and 5 more days), the
same number of wins. The replay can only see football at Hill by proxy (9
"everything else" football picks over the fortnight), so live will draw on
more fixtures than this. Read it again at 30 live groups; if the extra groups
keep losing, `GROUP_ANY_TIER = ()` with a `RULE` bump goes back to rule 3.

## Starred (`index.html`)

Starred used the football board's row with the board's mode (on the Both to
score board it dropped the tested rate, Edge, Hill and context chips), a
column ruler the list does not have, and lost a pick at its start. Now
`renderStarred` reads the list's own items (`listCollect`: list, reserve, the
picks left off for want of a Hill price, started picks pinned from the archive
with their results) and draws each with the list's row function (`listPut`,
shared with `renderList`) in the list's strength order (`listByStrength`). A
bookmarked board game that is on neither list is drawn the same way.
`starIdOf` gives the id each row's star uses. Checked in a browser at desktop
and 400px: the first starred row's markup is identical to the list's.

## Not changed

Any model, the Daily List, the tiers, the other sports' group legs, the star
ids (bookmarks already saved still match), the slip checker (`runSlip`).
