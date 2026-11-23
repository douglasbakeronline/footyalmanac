# The Daily 2x built on its own day (23 Nov 2026)

## What was wrong

`build_list_card` held a full Daily 2x as first built until its first start.
The builds look `DAYS_AHEAD` (3) days forward, so every day's slip was first
built one to three days early, on the picks priced then and at those prices,
and then never looked at again. From the archive (`groupings-archive/<day>.json`):

| Day | First built | Tiers | Price | Picks |
|---|---|---|---|---|
| 17 Nov | 17 Nov 02:43 UTC | reserve | 2.47 | 3 |
| 18 Nov | 17 Nov 02:43 | list, reserve | 2.31 | 4 |
| 19 Nov | 18 Nov 22:59 | list, reserve | 2.23 | 4 |
| 20 Nov | 17 Nov 07:07 | reserve, football | 3.47 | 3 |
| 21 Nov | 18 Nov 01:42 | reserve | 2.34 | 4 |
| 22 Nov | 19 Nov 01:02 | list, reserve | 2.26 | 4 |
| 23 Nov | 20 Nov 00:09 | reserve | 2.35 | 2 |

Mostly reserve picks, one slip at 3.47, and 23 Nov's showing "price at
lock, read Thu 19:30" on a Monday, with ten Daily List picks on the day
that it never saw. The rule the page states (the Daily List first) and the
ledger replay that put it live (`claude/daily-2x-2026-11-17.md`, 14 of 28,
+22%) are built from the day's own list, so the live slip was not the rule
replayed.

## The change

A Daily 2x that has not started is rebuilt on every build until its day's
own start, 07:00 UK (the Card's day window, `lock_time(date, "Day")`); from
the first build after that it is held as first built until its first start,
as before. A short slip is still rebuilt until it starts. The 07:40 UTC
build (the morning briefing and the Daily List email) is the first to hold
it, so the email and the page show the slip that is graded. Only locked
slips are archived, so nothing in the record changes.

## The replay (the archived pool, first real price, days to 23 Nov)

`daily_group` on each pool day's settled legs, built as at 07:00 UK:
25 slips, 12 won v 10.16 expected, +10.4% at the first price (+9.7% at the
last pre-start price). Tiers: list 19 slips, football 16, any 8, reserve 2.
On 17 to 22 Nov the on-the-day slips won 2 of 6, as the live slips did
(20 and 22 Nov): the change is about the slip being the rule, not a claim
of a better return. The pool's list flags are as first written, so this is
approximate; the 50-slip review in the note of 17 Nov stands.

## Not changed

No constant, no tier, no price floor, no record. The List 2x and List long
are still held as first built (the List card's own trial, read at 30
settled groups); the same early build applies to them and is worth the
same fix if its review keeps it.
