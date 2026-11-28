# Prime: a Show filter on the Daily List (28 Nov 2026)

Douglas, 28 Nov 2026, after a week of lost accumulators and a read of the last
month's Daily Lists: "Can you kind of just add a tab on the filters? ... Maybe
by the percentage bracketing ... give it a name. Something short and cool."

## What it is

**Prime**, an on/off button at the end of the Daily List's **Sport** row
(`FVIEWS.list.show`, `SHOW_LABEL.prime`). On the branch it was first a Show
row of its own, then the end of the Order by row; Douglas's last word the same
evening: "move it into the sports filter". The Sport row is already a row of
on/off buttons ("tap more than one to combine"), so it sits there naturally:
it combines with any sports, a second tap turns it off (`showtoggle` in the
bar's click handler), and the choice is the same `FILT.show` (`showIn:
"sport"` on the list's `filterBar` call draws a page's Show options in the
Sport row, which is then drawn even with one sport). A pick is Prime (`primeOk` in `index.html`, constants in `PRIME`) when it is

- on the Daily List, never the reserve;
- 80%+ as the row reads (rounded, as the bands are);
- not a college sport (`ncaab`, `cfb`);
- priced 1.10 to 1.40, both ends in, at the price the row shows (`itemPrice`:
  William Hill, else the average, else football's best). No price on file: not
  Prime.

## Every day, and the glance

Douglas: "Make sure it will update the data vis too to meet the rules, and on
all previous days too." The list's one keep test (`keepIt` in `renderList`)
carries Prime, and At a glance (`GL_KEEP`), the day ribbon's counts and a past
day's rows all read that test, so they already followed it. What was missing
was the price: `groupings-data.js` holds prices for today and yesterday only,
so on the days behind nothing could be Prime.

`daylist.py` now gives every pinned and past pick `px`, its pre-start price on
the results ledger (`ledger_prices`, `price_of`, `attach_prices`): the same
sport, pair and picked side, the copy starting nearest the pick's start within
`PX_NEAR_DAYS` (2), read as the page reads a price (William Hill, else the
average; the last read before the start, else the first). A pick with no
ledger price has no `px` key. `primePrice` reads `px` first on a past day (the
page's price for that pair could be a later meeting's) and after the page's
own price on today's rows. daylist.py runs after ledger.py in deploy.yml, so
it reads the same build's ledger. Display only: nothing is graded, ranked or
listed from `px`.

First read on the real files, 21 to 27 Nov: 120 of 139 list picks carry a
price; Prime picks by day 4, 3, 1, 3, 1, 2, 1 (15, of which 14 won).

Chosen, it behaves as every other filter: a removable chip, the count, Clear
filters, the address (`#list?show=prime`), the glance and the day ribbon's
counts. A line under the bar says what it is and how it has landed. The
button is always drawn on the list, with its count even at 0 (`keep` on a
Show option, new in `filterBar`). The college left-off line is hidden under it.
`FILT.show` is shared across tabs, and no other page lists `prime`, so every
other tab shows its own default and the choice comes back on the list.

Display only. No pick, list flag, order, record or grade changes; no chip on
the row; nothing in the emails, the cards or any model.

## Why these lines

The month's read, `results-ledger.json.gz` as built 28 Nov 16:47 UTC, list
picks by UK day of the start, 29 Oct to 27 Nov (the full table is in the
claude.ai Project doc `claude/daily-list-month-replay-2026-11-28.md`, not in
this repo):

| List picks | Landed | Flat return |
|---|---|---|
| All 590 | 90.7% | -2.0% (424 priced, average 1.10) |
| College basketball under 1.05 | 197 of 201 | -0.8% |
| College basketball at 1.10+ | 40 of 61 (66%) | -15.8% |
| Other sports, 1.10 to 1.40 | 72 of 83 (86.7%) | +3.3% |
| ... of those, 80%+ | 49 of 54 (90.7%) | +6.9% |
| ... of those, under 80% | 23 of 29 (79.3%) | -4.3% |

Read exactly as the page reads it (rounded confidence, Hill else the average
at the last pre-start price): 49 of 54 over the month at an average 1.17,
first half 26 of 27, second half 23 of 27 (-0.9%). The whole ledger to 27 Nov:
53 of 61 (86.9%), +2.6%; before 29 Oct only seven such picks were priced, 4 won.

Each line had support before this read: college out of the List card since 17
Nov (`LIST_SPORTS_OFF`) and the 14 Nov review's warning that college
basketball's early run would fade; 80%+ is the 14 Nov review's line between
the list's strong and weak tiers; 1.40 is the star's football line
(`WIN_FB_MAX`) and the 23 Nov proof; 1.10 is Douglas's own floor ("picks under
1.10 pointless", 17 Nov).

## What it is not

A tested rule. It is a read of the scoreboard (Rule 1: nothing is fitted on
it), 61 picks, one month carrying it, and the second half of that month was
flat. The page says so. Before Prime becomes a card, a chip, a mailer section
or a staking rule it needs the same treatment as the others: a pre-registered
variant in `tools/list_card_replay.py` on the ledger and the pool, at the gate.

One slip a day of the top two or three Prime picks was the best of the fixed
bets tried on the month (doubles 11 of 14, trebles 7 of 9 at 80%+), paying
1.25x to 1.6x. Nine to nineteen slips a rule: inside luck.

## Checked

`nametest.py`; the unit suite (1,566, plus `tests/test_prime_filter.py`); the
fast build (football-data and ESPN partly blocked in the sandbox, so no
football list picks locally and no `groupings-data.js`: prices were seeded for
the check, never committed). In Chrome at 1280 and 400, with `daylist.js`
built from the real archives and ledger: Prime at the end of the Sport row;
on each of the seven past days the rows, the ribbon's count (4/4, 2/3, 1/1,
3/3, 1/1, 2/2, 1/1) and the glance's dots all equal the Prime picks counted
from the ledger, and today's three; a second tap turning it off (24 Nov back
to 34 dots); chosen on the days ahead, exactly the eight seeded picks at 1.10 to
1.40 (1.05 and 1.55 left out, the ends kept, college and reserve picks at 1.20
left out); chip, note, count "8 of 198 picks", `#list?show=prime`; held over a
reload; Tennis shows its default with `prime` still stored; the chip clears
it; no page errors, no sideways scroll.

## Roll back

`git revert` the merge. A stored `show: "prime"` then reads as Every pick
(`fClean`).
