# Backlog #154 is already done: the pool is the Card replay's source (25 Nov 2026)

The task ("make the pool the replay's source from 30 Oct 2026, keep the football-data path for earlier days") shipped on 9 Nov 2026 (`claude/card-pool-replay-2026-11-09.md`). Checked on 25 Nov:

- `tools/card_replay.py` `main()` takes legs from `pool_legs()` from `POOL_FROM` (2026-10-30) and keeps the football-data archive rows for earlier days; `--no-pool` is the old path.
- Pool legs carry first (or `--closing` last) price, `bookOdds`, `opp` (from the football archive before 6 Nov, `archive_opp`) and the result through `G.settle_pool`.
- Every named variant (`rule5`, `opp7`, `short`, `four3x`, `uncapped`, `wider`) is in `VARIANTS`; each reports groups, won, expected, return and empty days, and `pair_days` / `cardM7Paired` pair them against live by day with a bootstrap.
- `tests/test_card_pool_replay.py` (13 tests, all pass) builds a synthetic pool file (`test_legs_settled_and_estimates_left_out`, closing, recover, pending, opposition).

No code change is needed. The backlog item should be closed.
