# The briefing chain: each build starts the wait for the next slot (16 Nov 2026)

## What happened

The watchdog (`briefing-watch.yml`, 15 Nov) runs on crons, nine a window
around each slot. GitHub shed those too: from its merge on 15 Nov to 08:36
UTC on 16 Nov it ran on schedule twice (21:21 and 23:53 UTC on 15 Nov) and
not once in the 06:05-08:45 UTC morning window. The only scheduled deploy
that morning was the 05:15 cron, which started at 06:14 UTC, 46 minutes
before the 07:00 slot. At 08:36 UTC the morning push was still unsent, 96
minutes after its hour (`tools/briefing_watch.py --dry-run` against the live
run list). The 09:17 build session dispatched a deploy by hand to send it.

So cron frequency is not the fix: on this repo at busy hours GitHub starts
none of them. What does run, late or not, is the deploy itself.

## What changed

- `tools/briefing_watch.py --wait`: sleeps until the next unsent slot's hour
  plus `GRACE_MIN` (10) if that is at most `MAX_WAIT_MIN` (300) minutes away,
  then checks every `POLL_MIN` (5) minutes for up to `LOOP_MIN` (45),
  reading `briefed.json` and the deploy runs fresh from the API each time,
  and dispatches a deploy under the existing rule (`decide`: unsent, past
  the grace, no deploy queued or running, at most `MAX_KICKS` 2 a slot).
  `next_wait` picks the slot; a slot more than `LOOP_MIN` past its hour is
  left to the next build.
- `deploy.yml` `briefing-next`: the last job of every deploy run (built or
  held) dispatches `briefing-watch.yml` with `wait=true`. A GITHUB_TOKEN
  dispatch does start a run. Two minutes' timeout, continue-on-error: it can
  never fail a deploy.
- `briefing-watch.yml`: the `wait` input, a 355-minute timeout for a wait
  run (5 otherwise), and a concurrency group per mode, so a cron run arriving
  while one sleeps cannot cancel the pending wait the next deploy queued.

The deploy that sends one slot starts the wait for the next: 07:10 to 11:10
is 4h, 11:20 to 16:10 and 16:20 to 21:10 about 4h50, inside the 300-minute
reach. The overnight gap (21:00 to 07:00) still rests on the 00:10 and 05:15
deploy crons, one of which has run every night so far. The crons stay as a
backstop.

## Cost

A wait run holds one runner, asleep, for up to about 5h45; the repo is
public, so Actions minutes are free, and the free plan's 20 concurrent jobs
leave room. It dispatches nothing that the cron watchdog would not.

## Tests

`tests/test_briefing_watch.py`: `next_wait` (16 Nov's 06:21 case waits 49
minutes for the morning slot, the grace, a sent slot moving to the next,
lunch to evening in reach, too far ahead, a long-missed slot skipped, the
job limit), and `wait_and_kick` with a fake clock and API (sleeps then
dispatches, dry run, a running build left to send it, gives up after the
loop).

## What to watch

The nightly Card review's briefing table (`card_review_post.briefing_section`):
morning, lunch, evening and night medians under 20 minutes from 17 Nov. If
the morning slot is still late, the overnight crons are the gap.

Roll back: remove the `briefing-next` job from `deploy.yml`; the crons and
the plain watchdog carry on as on 15 Nov.
