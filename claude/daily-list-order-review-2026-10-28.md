# Daily List order review, 28 October 2026

Question from Douglas: fixtures with a higher score sometimes sit lower in the
"Strongest" order. Review of the ordering since the 80% bar (29 Sep), with a
view to taking two groups of five from the top 10, and whether tennis and
college football were right to come off.

## How the order worked until today

`index.html` `renderList` and `daylist.py` sorted by **tested rate first**
(`accuracy.cumHit`, the cumulative band rate, falling back to the own-band
`hit`), confidence second. So the order was a ranking of band tables, not of
picks.

## Two reasons a stronger pick sat lower

1. **Band rates are not comparable across families and are not monotone.**
   Core leagues quote the 2025-26 fit bands (80%+ = 84%), wider leagues the
   2025 AFX bands (85%+ = 90%), NFL its own 31-game band (80%+ = 81%),
   ranked internationals a band where 80-85% (84%) sits below 75-80% (84%).
   25 Oct: Minnesota Vikings at 81% (NFL, tested 81%) sat ninth under three
   75% football picks quoting 82%. A 97% Brighton (core, 84%) ranked under an
   80% Kyrgyz league pick (AFX, 85%).
2. **Bug: a started football pick sorted last.** `daylist.football_item` read
   `accuracy` off the football archive row, which `build.py` never wrote
   (the `flat` keys in `archive_predictions` omitted it). Tennis and the
   other sports archive theirs. So every pinned football pick had strength 0
   in `daylist.json` and on the page (the pinned row is sorted on
   `p.accuracy`, though drawn from `full`, which has the chip). A 90%
   football pick dropped under every 75% rugby or NFL pick the moment it
   kicked off. Same in the reserve fold.

## What the record says (pinned lists rebuilt as daylist.py builds them)

29 Sep to 27 Oct: 218 settled Daily List picks over 27 days, 177 landed (81%).

Landed by **confidence**: 80-85% 63/77 (82%), 85-90% 38/44 (86%), 90-95%
12/14 (86%), 95%+ 6/6. Monotone.
Landed by **tested rate** (the old sort key): under 82% 14/16, 82-85% 45/60
(75%), 85-88% 41/48 (85%), 88-92% 60/72 (83%), 92%+ 17/22 (77%). Not monotone.

Top 10 on the 7 days with 10+ picks, paired bootstrap on top 5 (90% band
about ±11 points, so none of this separates):

| Order | top 5 | 6-10 | top 10 |
|---|---|---|---|
| As shipped (tested, started football at 0) | 29/35 | 25/35 | 54/70 |
| Tested rate, then confidence (intended) | 30/35 | 25/35 | 55/70 |
| Confidence only | 29/35 | 28/35 | 57/70 |
| min(confidence, tested) | 29/35 | 28/35 | 57/70 |
| Own-band rate, then confidence | 29/35 | 27/35 | 56/70 |

Nothing beats confidence. The tested rate earns its place as the gate (the
80% rule) and the chip on the row, not as the sort key. This is a check of
which existing key is monotone on the record, not a fit (Rule 1).

## Tennis and college football

**College football, off since 19 Oct: right.** All 80%+ calls graded: 26/35
(74%) against 86% quoted, z -2.1. Since removal its 75%+ calls landed 12/20
in the reserve; every band since sits under quote; 85%+ since removal 3 of 5.
No bar fixes it. It stays off, and its reserve picks should stay out of any
top-10 scheme.

**Tennis, off since 15 Oct: the evidence for removing it was noise.** The
decision rested on list picks winning 39 of 51 against 42.1 expected, about
1.1 standard errors (WTA 18 of 27 did the damage; ATP on quote). At the bar
itself, 75%+ before 15 Oct landed 61/75 (81%, quoted 83%, z -0.3): on quote
and over the 80% rule. Since removal, 75%+ landed 78/88 (89%) in the reserve:
ATP 26/28, WTA 52/60, 85%+ 24 of 24. Whole record 139/163 (85%). Caveat: the
post-removal run is partly indoor hard courts, the surface the ratings know
best. Back on both tours at 75% (Douglas, 28 Oct); review at 300 graded list
picks.

**Rule for taking a sport off, so one bad week does not decide it:** landed
under quote by two standard errors or more on 50+ picks at the bar. College
football meets it; tennis never did.

## The two-groups-of-five plan

Since 19 Oct, with tennis and college football off, the list never reached
10 picks in a day: 36 picks in 9 days, 31 landed. With tennis back, 6 of
those 9 days would have had 10.

Top 10 by confidence, list first then reserve, 19-27 Oct (9 days):
72/90 landed (80%); first five 37/45, next five 35/45. All five landed on
5 of 9 days for the first group and 3 of 9 for the second (at 80% a five-fold
lands about 1 in 3). Reserve picks at 75%+ landed 60/74 (81%); at 62-75%,
145/234 (62%), so a top 10 should not reach below 75%.

On "near perfect at the top": across the list, 85%+ calls landed 56/64 (88%)
and 90%+ 18/20. Confidence is the only key that climbs; nothing in the
model's own numbers gives 100% at the top, and the bookmaker signal that would
help (`claude/daily-list.md`) is ruled out by Douglas's decision.

## What shipped (28 Oct 2026)

1. `build.py` writes `accuracy` into every football archive row;
   `daylist._accuracy` recomputes it with `build.accuracy_for` for older
   archives. Test: a started 90% football pick keeps its place above an 81%
   tennis pick.
2. `daylist.strength` and `index.html` `byStrength`: confidence first, tested
   rate second. One key, documented in both places.
3. Group labels on the list in strongest order: Group A (1-5), Group B (6-10),
   The rest, each with a "landed" tally once the pinned rows have results;
   `daylist.json` summary carries `groupA` / `groupB`. The list only; the
   reserve is unchanged.
4. Tennis back on the list, both tours, `build_tennis.LIST_ON`.
5. `tools/list_order_replay.py` reproduces the tables above.

Not done: a persistent record for the two groups (daylist.json is one day;
a `groups` line in `score.py` from the archive's rank would do it) and a
pull of 75%+ reserve picks into a day with fewer than 10 list picks.
