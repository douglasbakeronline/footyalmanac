# Away and Neutral marks on college picks, 15 November 2026

Douglas, 02:54 on 15 Nov, after the review of Saturday's reserve
(`claude/daily-list-losses-2026-11-14.md`): "action a counter to the reserve
pattern losses".

## What the patterns were, and which one the replay supports

Saturday's reserve lost 27 of 103, as quoted (76.0 expected). Two patterns
were named: college football away favourites (four of the eight cfb losses),
and college basketball sides carrying last season's rating (Colorado State,
Winthrop). Before building anything, both were tested on the historical
replay (`sports.replay` with the live parameters, 70%+ picks, fit 2024-25
and check 2025-26, August to December), not on the record (Rule 1).

**The carried-rating pattern is not a signal.** Cutting November picks by
the favourite's record so far: unbeaten sides land 91.2% v 83.5% quoted,
sides with a loss in their first six games land 78-86%, all at or above
quote. Colorado State and Winthrop were anecdotes. No mark for it.

**The side pattern is real, with a twist.** It is not that away picks are
bad; home picks are better than their quote and away and neutral picks are
not:

| sport, Aug-Dec, 70%+ | picks | landed | quoted | z |
|---|---|---|---|---|
| college basketball, home | 2,116 | 88.8% | 83.5% | +6.5 |
| college basketball, away | 125 | 76.0% | 77.3% | -0.3 |
| college basketball, neutral | 227 | 74.9% | 78.3% | -1.3 |
| college football, home | 440 | 84.5% | 81.0% | +1.9 |
| college football, away | 154 | 79.9% | 78.0% | +0.6 |

Live record at 70%+ (a tally, not a fit): college basketball away 11 of 21
(52% v 79%), neutral 9 of 16 (56% v 78%), home 360 of 407 (88.5% v 84.3%);
college football away 36 of 54 (67% v 78%, z -2.0), home 94 of 117 (80% v
81%).

So the honest counter is a mark, not a cut: an away or neutral college pick
is one to weigh; a home one is the model at its best.

## What shipped

- `sports.wary(sport, pick_home, neutral)`: an `Away` or `Neutral` mark on
  every college basketball and college football row (`WARY_SPORTS`), carried
  into the archive as `wary`. Probabilities, bars, list and reserve
  membership unchanged. Nothing hidden.
- `index.html` `sideWary` / `sideWaryChip`: the chip on every sport row (the
  Daily List, the reserve, the sport tabs, pinned rows), computed from the
  row so older archive rows carry it too, with the numbers above in its
  title. The reserve's summary line counts the marked picks of the day.
- `sports.by_side(graded)`: `sports-record.json` `bySide`, landed v quoted by
  side per college sport at 70%+, with a `tripwire` flag.
- **Pre-registered tripwire** (`WARY_TRIP_N` 100, `WARY_TRIP_Z` -2.0): when a
  college sport's away picks at 70%+ reach 100 on the live record and sit
  two standard errors or more under quote, away picks of that sport leave
  the reserve (a release and a note, no further question). College football
  is at 54 and z -2.0; college basketball at 21.

## Not done

- No order change: the list and reserve still sort by confidence.
- No rating change. A faster early-season K and a higher summer regression
  for the college sports are the two model tests left from the review; both
  through `sports.py --tune`'s gates, neither run yet.
- The neutral-site flag check for the tournament week (17-27 Nov) is still
  owed: a wrong flag is 100 Elo points in college basketball.
