# The Daily List by confidence band, and the tabs tidied (27 Nov 2026)

Douglas, 27 Nov 2026, after a review of the Daily List page: Group A had an
"85% or better" label, Group B and "the rest" had none, and the reserve sat in
a fold below. "Should they be clearer and staggered by percentage banding?"
Then: make the changes, plus the further recommendations, across every page.

## The evidence

On the results ledger at 27 Nov (every list and reserve pick graded so far):

| Confidence | List | Reserve |
|---|---|---|
| 90%+ | 93.8% of 176 | 93.8% of 16 |
| 85-89% | 89.5% of 239 | 82.9% of 41 |
| 80-84% | 84.4% of 154 | 84.1% of 189 |
| 75-79% | 75.8% of 128 | 77.0% of 300 |
| 70-74% | 71.4% of 14 | 70.0% of 514 |

At a given confidence a pick lands alike on the list or the reserve, so the
band is what tells a reader most. Group A's cap of five pushed 85%+ picks down:
over 59 days, 120 of Group B's picks were 85%+ (94.2% landed) and 203 of the
rest (90.6%).

## What shipped (releases 2026-11-27-list-bands to 2026-11-27-tabs-tidy)

- **Daily List** (`bandedDay`, `bandChips`, `lbRecord`, `LBANDS` in
  `index.html`): each day by band, 90%, 85% and 80% open, 75% open on a thin
  day (under 10 picks above it), the rest folded. Band headers pin under the
  tab bar (`--lbstick`, `lbStick`) and carry the band's record from
  `daylist.band_records` ("pick": list and reserve; "every": the whole board,
  for the sport tabs): landed v quoted, and a level stake's return at the
  price published before the start when 20+ picks were priced. Reserve picks
  sit in their band marked Reserve and are still graded apart. One strength
  rank across the day. Settled picks drop to the foot of their band. A price
  under 1.05 is marked Short (`SHORT_PRICE`). Past days use the same bands.
- **Email** (`mailer.bands_of`, `band_line`, `is_short`): the same bands and
  records; the welcome guide explains them. The morning push (`notify.py`)
  still says Group A; not changed.
- **How it went**: `bandTable` (every sport by band, landed v quoted, cells
  under 30 picks lighter, a band 2 SE or more under quote on 30+ picks marked)
  and each day by band (`reviewBands`).
- **Sport tabs, the football winner board, Tennis and Starred** (`bandBoard`):
  by band in strongest order; by kick-off a day stays one run.
- **Bets**: the day's slips first; the Card's rule, old and paper groups, the
  re-check log, the scoreboard and the October rules in one fold
  ("Rules, logs and the scoreboard"). **Scale**: `scHonest` (live group record,
  estimates said plainly). **Horse racing**: the feed note as a marked box.
  **Mailer**: the last seven emails above the form.
- **First paint**: `scale.js` and `racing.js` load after it (`LATE_FILES`,
  `loadLate`); `SCALE` is a `let`; the open tab redraws when they land.
- Issue #569: replay the Daily 2x and the List card choosing by confidence
  band, for Douglas to decide on the numbers.

## The morning's outage (read before touching anything run on load)

#560 (the At William Hill filter removed, college basketball's floor on any
price) made `listShown` call `pickPrice`, which reads `lbKey`. The masthead's
list count calls `listShown` while the page is still loading, before `lbKey`
(a const further down) exists: "Cannot access 'lbKey' before initialization",
the whole script stopped, no rows, tabs dead. Reverted (#562), fixed and
re-landed (#563): `itemPrice` reads the price files itself and calls only
hoisted functions; `tests/test_early_list_count.py` guards it. The lesson:
anything the masthead or top-level code calls must not reach a `const` or
`let` declared later in the script, and a change to it is checked by loading
the whole page, not only the function.

## Checking a page change locally

The cloud sandbox cannot reach the live site or the data sources, but a fast
offline build makes a realistic page: `python3 build.py --days 7 --no-topup
--no-odds`, then `daylist.py`, `groupings.py`, `scale.py`, `slip.py`,
`mail_page.py` in a copy of the repo (`sports-data.js` and `tennis-data.js`
are committed). Load `index.html` from that copy in Chrome (Playwright, the
network blocked) and open every tab at 1100px and 400px, collecting page
errors.
