# The Card's day after midnight (26 Nov 2026)

## What was wrong

The Card's day runs 07:00 UK to 07:00 UK the next morning (`CARD_WINDOWS`,
`("Day", 7, 31)`, since 29 Oct 2026), and a group is open until its first
kick-off, when it locks and is archived (`archive_locked`). But `groupings.main()`
built only the board's dates, starting at today's UK date. From midnight to
07:00 the day before was no longer built. A group whose picks all started in
those hours was held by every build of its day, then dropped by the first
build after midnight: never locked, never archived, never in the record.
The List card and Daily 2x had the same gap.

The case: on 25 Nov the page built a Card 2x of Golden State Warriors,
Memphis Grizzlies and Toluca on every build from 08:58 to 21:07 UTC
(`groupings-archive/card-short.json`). Their starts were 01:00 to 03:00 UTC on
26 Nov. The 00:10 build dropped the day, and the 26 Nov Card review read 25 Nov
as the third empty day in a row. The group was published and bettable, and it
is missing from the record.

How often: none of the 35 archived Day-window Card groups (29 Oct to 25 Nov)
has a first kick-off after midnight, which is what the bug would produce. On
the pool replay (30 Oct to 25 Nov) no variant built a group whose picks all
start after midnight (the replay places legs by `uk_slot` and has no build
clock, so it never had the gap), so it is occasional: nights where the NBA or
the Americas make the whole group. It biases the record, though, because only
the groups that happen to include a daytime pick ever settle.

## The fix

`groupings.card_dates(dates, now)`: the board's dates, led by the day before
while its window is still open (`now < window_end(day before)`, i.e. before
07:00 UK). `main()` builds the cards, the context candidates and the two-day
hold (`span_held`) over those days. Nothing else changes: `build_card` already
holds a published group past midnight, locks it at its first kick-off and
builds nothing new once the window ends; `build_list_card` already holds paper
slips after the day's 07:00. The price, pool, closing-price and grading steps
still use the board's dates.

On the page, the Bets tab's day ribbon shows Yday until 07:00 UK, and opens on
Today as before.

## What was not done

The 25 Nov group is not added to the record by hand (Rule 1: the archive is
written by the build only). No Card constant changed; `CARD_RULE` stays 14.

## Tests

`tests/test_card_overnight.py`: the day before is kept until 07:00 UK and
dropped at 07:00; a group of three picks starting 01:00 to 03:00 the next day
is built in the evening, holds at 00:10, locks after its first kick-off and is
archived under its own day; nothing new is built once the window has ended.
`main()` run offline at a frozen 00:10 UTC on 26 Nov carries 25 Nov in
`groupings.json`; the Bets tab checked at 1280 and 400 wide.

## How many were lost (26 Nov 2026, second read)

The deploy logs print, for each day a build covers, how many of its groups
are holding, new, replaced and underway. A group still holding at the last
build of its day could never lock, so it never reached the archive. From
28 Oct to 25 Nov, for the last build of each day:

| day | open at the last build | kind (by elimination against the day's archive) |
|---|---|---|
| 2 Nov | 1 | Model 3x (paper; the Model 2x was archived) |
| 4 Nov | 1 | Model 3x (paper) |
| 13 Nov | 1 | Card 2x (staked; the day has no archive file) |
| 17 Nov | 1 | List 2x or List long (paper; Card 2x and Daily 2x archived) |
| 25 Nov | 1 | Card 2x (staked): Warriors, Grizzlies, Toluca |

Five groups in 29 days: two staked Card groups, three paper slips. Only 25
Nov's picks survive (card-short.json); 13 Nov's picks are not kept anywhere.
Scale and the slip were not affected: they write their archive on every
build, so the last published version is always on file. Edge picks are in
predictions/.

## The second fix: a day stays until its groups lock

The first fix kept the day before only until 07:00 UK. A group whose first
pick starts after the last build before then (a 06:30 start before the 07:40
build, or a build GitHub runs late or sheds) would still be lost.
`card_dates(dates, now, prev)` now also keeps any earlier day the last build
showed with a group not yet locked (`open_group`), at any hour, until each
one locks (and is archived) or is withdrawn by its re-check.

## The publication log (`publog.py`)

Every build, after slip.py, logs every item the page put forward to
`groupings-archive/published/<day>.json`: every group (Card, Daily 2x, List,
Model), every Scale pick and group, the slip, every Edge pick. Each item
keeps its first and last sight, how many builds showed it, its first and last
snapshot (picks, prices, chances, status), each status or price change, and
`gone` when a build that still covered the day stopped showing it. Seeded
once from everything kept (154 archived groups, 665 Scale picks and groups,
9 slips, 59 Edge picks, and the five lost groups as `build-log` entries).
`python3 publog.py --day YYYY-MM-DD` prints a day. Nothing is graded from it.

The nightly integrity check now raises `group-unarchived` for any group a
build logged, not withdrawn, whose first pick started two hours ago or more
and which is not in the archive.
