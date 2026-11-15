# The briefing watchdog (15 Nov 2026)

Build session, 15 Nov 2026, 16:30 UTC. Health, not a Card rule. Follows
`claude/briefing-lateness-2026-11-13.md`.

## What was seen

The backup crons of 13 Nov (#286: 11:07, 16:07, 21:07 UTC) did not mend it.
Scheduled deploy runs, from the Actions run list:

| day | scheduled runs | first after 07:00 UTC |
|---|---|---|
| 10 Nov | 7 | 07:07 |
| 11 Nov | 7 | 12:42 |
| 12 Nov | 7 | 07:01 |
| 13 Nov | 7 | 13:05 |
| 14 Nov | 8 | 12:10 |
| 15 Nov | 4 by 16:30 | 12:43 (cancelled), 14:56 |

Ten crons a day, never more than eight runs. The morning runs (05:59 to
07:07) are the 05:15 cron an hour or more late: the 07:40 cron did not run
once in six days, and there is no morning backup. The briefing log
(`briefed.json`): morning 123 and 138 minutes late on 14 and 15 Nov, lunch
74 and 84, both sent by agent-merge push builds, not by a cron. At 16:38 UTC
on 15 Nov the evening briefing was still unsent, the 16:07 backup not run.

More crons on deploy.yml do not help: GitHub sheds them.

## What shipped

`tools/briefing_watch.py`, run by `.github/workflows/briefing-watch.yml`
every 20 minutes (:05, :25, :45) in the UTC hours around each slot (06-08,
10-12, 15-17, 20-22, which cover GMT and BST). It dispatches `deploy.yml`
only when all hold:

- a slot is due today and not in `briefed.json` (`notify.due_slot`);
- 10+ minutes past the slot's hour (`GRACE_MIN`);
- no deploy run is queued or running;
- fewer than two (`MAX_KICKS`) dispatched deploys since the slot's hour.

The build then sends the briefing as any build would; nothing can send twice.
At most two extra builds a slot (eight a day, in practice far fewer), each
10-25 API-Football calls of 7,500; the Odds API and context spends are capped
per day in code. A watch run that does nothing takes seconds.

The watchdog's own crons can be shed too, but nine chances a window, off the
hour, at a light workflow, is a far better bet than one deploy cron.

Dry run against the live run list at 16:38 UTC: "evening: unsent 38 minutes
after its hour, no deploy running", so it would have dispatched.

Tests: `tests/test_briefing_watch.py` (the decision, GMT and BST, and that
every slot hour sits inside a cron window of the workflow file).

## What to watch

The nightly Card review's briefing table: medians should fall under 30
minutes from 16 Nov. If they do not, the watchdog's own runs are being
shed; the next step is an outside trigger (a claude.ai scheduled task that
dispatches the deploy), which is Douglas's account setting, not the repo's.

Roll back: delete the workflow (or disable it in Actions).
