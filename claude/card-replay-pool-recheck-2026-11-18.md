# Card replay on the pool: rechecked, nothing to build (18 Nov 2026)

The planner task (make the archived pool the replay's source from 30 Oct 2026)
was shipped on 9 Nov and confirmed on 16 Nov (`card-replay-pool-already-2026-11-16.md`).
Rechecked on 18 Nov: `tests/test_card_pool_replay.py` 13 tests pass;
`tools/card_replay.py --since 2026-10-29` reads 1,217 settled priced pool legs
over 20 days (football 584, ncaab 299, cfb 154, tennis 86, nba 62, nfl 32; left
out: estimate only 1,613, pending 195, void 2). Live: 26 groups, 13 won v 39%
expected, +15%, 59 of 78 legs landed 75.6% v 70.1% quoted. Every variant is
built from the pool from `POOL_FROM` and paired against live by day. The
football-data rows only stand before 30 Oct. Planner gap is stale: its source
text predates the 9 Nov change. Nothing fitted on record.json; no model number
changed. Do not reassign this task.
