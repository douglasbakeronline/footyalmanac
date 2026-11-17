# The Card integrity check on slim legs, and the review's timing (17 Nov 2026)

Build session, 17 Nov 2026, 09:17 London.

## The crash

`tools/card_integrity.py` failed on today's `groupings-record.json` with
`KeyError: 'date'` in `groupings.settle()`. The record keeps a slim leg
(`pick`, `event`, `sport`, `comp`, `when`, prices, `status`, `result`, no
`date`, `home`, `away`, `side` or `id`). The pending-with-result check passes
any leg pending 24h+ after its start to `settle()`, which reads those fields.
Until now no slim football leg had sat pending that long; Pistoiese v Coriano
(Serie D, 15 Nov 13:30 UTC, in 14 Nov's two-day group and a 15 Nov group,
both already lost on another leg) has no result on file and was the first.

The review runs the check with `continue-on-error` and opens an
office-backlog issue when it fails, so the day's review would have sent the
engineer a crash, not a finding. Tennis and US-sport legs had the same blind
spot without crashing: with no `id` they always settled "pending", so a
tennis leg's `pending-24h` finding could not tell a missing result from a
present one.

`full_leg(day, leg)` takes the full leg from `groupings-archive/<day>.json`
(or the day before, for a two-day group), keyed by event and pick, with the
record's values on top; failing that, the date from `when` and the sides
from `event`. Run on today's files: 0 findings, 15 of 15 Card legs since
10 Nov replayable at a real price.

## What else changed in the check

- `staked(name)`: the pending checks read the Daily 2x, List 2x and List
  long (17 Nov 2026, staked by Douglas) as well as the Card. The Model card,
  the filler and the retired kinds stay out. The pick-twice and coverage
  checks stay Card only.
- `needs_opp`: rule 13 shows the opposition's price and never reads it, so a
  rule 13 football leg without one is no finding. Only rules 6 and 12
  (`OPP_RULES`) ask for it.

## The review's timing

The review's 03:40 UTC cron ran at these times (UTC): 9 Nov 12:07, 10 Nov
11:46, 11 Nov 11:26, 12 Nov 11:50, 13 Nov 11:32, 14 Nov 10:55, 15 Nov 11:29,
16 Nov 12:02; the 09:25 backup came in the evening. So the 03:17 and 09:17
London build sessions read the day before's review. deploy.yml's
`card-review-next` job (after a successful build) dispatches `card-review.yml`
when it is 03:40 UTC or later, the UTC day has no "Card review <day>" issue,
and no review run is queued or running. The crons stay as backups;
`card_review_post` posts one issue a day and refreshes it on a later run
when its files changed.

To check it worked: tomorrow's review issue should be created in the morning,
by a `workflow_dispatch` run.
