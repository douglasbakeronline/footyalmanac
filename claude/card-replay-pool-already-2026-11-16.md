# Card replay on the pool: already shipped (16 Nov 2026, issue #154)

The backlog task (make the archived pool the replay's source from 30 Oct 2026)
was done on 9 Nov 2026. `tools/card_replay.py` takes legs from
`groupings-archive/pool-<date>.json.gz` from `POOL_FROM` (2026-10-30) through
`pool_legs`, every sport, first real price (or the `priced` block), `opp`,
results through `groupings.settle`; the football-data rows stand before
`POOL_FROM`; `--no-pool`, `--closing` and `--recover` are the switches. Every
variant (live, rule5, opp7, short, four3x, uncapped, wider and the rest) is
reported by groups, won, expected, return and empty days, and paired against
live by day with a 4,000-draw bootstrap (`vsLivePerDay`, `pWorse`). The
nightly `card-review.yml` runs it with `--since 2026-10-29 --json`.

Checked on 16 Nov: `tests/test_card_pool_replay.py` (11 tests, synthetic pool
files) passes; the run reads 1,158 settled priced pool legs over 18 days
(football 567, ncaab 276, cfb 154, tennis 77, nba 53, nfl 31; left out:
estimate only 1,557, pending 184, void 2); live 23 groups, 9 won v 40% expected,
-4%. Nothing left to build. Many variants are thin (2 to 3 groups): read the
direction only.
