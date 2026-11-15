# Briefing pushes arrive late (13 Nov 2026)

Build session, 13 Nov 2026, 12:40 UTC. Health finding, not a Card rule.

## What was seen

The four briefings (`notify.py` `SLOTS`: 07:00, 11:00, 16:00, 21:00 UK) go
out from the first build at or after each slot's hour. The builds are
deploy.yml's crons, and GitHub runs scheduled workflows late at busy times
(and sometimes not at all). From `groupings-archive/briefed.json` in git
history, and the deploy runs' queue times:

| slot | 11 Nov | 12 Nov | 13 Nov |
|---|---|---|---|
| morning 07:00 | | 07:06 | 07:24 |
| lunch 11:00 | | 13:18 (2h18 late) | not sent at 12:40; a deploy was dispatched by hand |
| evening 16:00 | 16:03 | 16:18 | |
| night 21:00 | 21:46 | 22:40 (1h40 late) | |

The 12:00 UTC cron queued at 11:43 to 13:53 UTC from 7 to 12 Nov (13:53 on
9 Nov) and had not queued by 12:40 on 13 Nov. Scheduled deploys on 12 Nov
queued at 01:36, 02:56, 07:01, 13:45, 16:11, 19:13 and 22:35 UTC against
crons at 00:10, 05:15, 07:40, 12:00, 17:00, 19:30 and 22:15: the times do not
line up one to one, so some runs came up to two hours late and others were
dropped. `due_slot` sends only the latest due slot, so a build late enough
would skip a slot altogether.

A late briefing is a late price: Douglas bets at those times, and the push
is what tells him the Card and the list are ready.

## What shipped

- `notify.mark_sent` now keeps a `log` in `briefed.json` (21 days): each
  slot's send time and lateness in minutes after its hour, and a `skipped`
  entry for an earlier slot of the day that never went. `due_slot` is
  unchanged.
- The nightly Card review prints a "Briefing pushes" table (sent, median and
  worst minutes late, skipped, by slot) and names in bold any slot whose
  median is over 60 minutes or that was skipped
  (`card_review_post.briefing_section`).
- Tests: `tests/test_briefing_log.py`.

## What needs the owner

The fix for lateness is in `.github/workflows/deploy.yml`, which a build
session cannot merge: backup crons a few minutes after the 11:00, 16:00 and
21:00 UK slots, the way `card-review.yml` got a second schedule on 10 Nov
when its 03:40 run was dropped. Opened as a separate pull request with
`needs-owner`. Each extra build costs 10-25 API-Football calls of 7,500 a
day; the Odds API and context-check spends are capped per day in code, so
extra builds do not raise them.
