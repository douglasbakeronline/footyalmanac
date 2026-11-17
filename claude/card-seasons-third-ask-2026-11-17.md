# Card over 2022-23 to 2024-25: asked a third time, already done (17 Nov 2026)

The planner asked again for the Card's leg rule and whole Card replayed on the
three past seasons. It was done on 9 Nov 2026 (issue #153, CI run
42543472973) and confirmed as done on 10 Nov. Nothing new was run: the cloud
sandbox cannot reach openfootball or football-data, and `history/` holds only
2025-26 files for non-core leagues, so the past seasons are built in CI by
`tools/card_legs_history.py --seasons 2022-23,2023-24,2024-25` (`tune.yml`
Mondays and `card-legs-history.yml`), not from `history/`.

Where each table lives: `claude/card-seasons-2026-11-09.md` (legs landed v
quoted, singles return, gap bands, opposition bands, whole Card and losing
months; raw output in `claude/card-seasons-2026-11-09-output.txt`) and
`claude/card-seasons-recheck-2026-11-10.md` (index). The live
`card-legs-history.json` (16 Nov retune) is cardRule 11 only; its verdict
reads "the under-market cut does not hold on both seasons".

Answer to "does the rule hold across seasons": the opposition condition does,
the gap cap does not, the football-only Card is too thin to carry a bankroll.
Open question the planner should ask instead: the model-only rule 13 has no
past-season replay of its own beyond `cardM7` (football-data 2025-26 and
2026-27); a three-season rule 13 whole-Card replay needs CI, the pre-registered
`rule12` / `m7value` variants are where that belongs (30 Nov review).
No gate met, no rule changed.
