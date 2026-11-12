# The value demand's relief on five football-data seasons (12 Nov 2026)

Build session, 12 Nov 2026 (12:35 UTC). Advisory: nothing here changes a rule.

## Why

The live Card (CARD_RULE 11) takes a pick only when the model rates it at or
above the bookmakers' fair chance (`CARD_MODEL_EDGE` 0). `m7under5`, the model
up to 5 points under, was pre-registered on the pool on 11 Nov
(`claude/card-funnel-rule7-2026-11-11.md`) and read worse then (p(worse) 0.97
on 42 legs). By the 12 Nov nightly review it read the other way: +40% v live
-17%, p(worse) 0.014, 45 legs. A swing that size on a few days is the reason
to look at seasons, not to act. It had never been run on football-data, so
the gate in CLAUDE.md (beat live on both football-data seasons and the pool,
p(worse) at most 0.30 on 100+ legs) had no football-data side for it.

## What was added

`tools/card_legs_history.py`: `m7under5` and `m7core` in `cardM7`; every
rule 7 variant paired by day against live in each season (`cardM7Paired`:
units a day, bootstrap p(worse), legs) and pooled over every season replayed
(`cardM7Pooled`, with how many seasons the variant was ahead). Each group in
`groupList` now carries its leg count. Tests: `tests/test_card_m7_paired.py`.

## The read

Pool, 30 Oct to 15 Nov (local `tools/card_replay.py`, live = rule 11):

| prices | live | m7under5 | paired | p(worse) |
|---|---|---|---|---|
| first real | 19 groups, +4%, 57 legs | 28 groups, +21%, 84 legs | +0.75 a day | 0.10 |
| `--recover` | 28 groups, +33% | 36 groups, +26%, 108 legs | +0.01 a day | 0.51 |
| closing | 18 groups, +8% | 26 groups, +1% | -0.17 a day | 0.63 |

Football-data, five seasons (CI run 43219897861, `--seasons 2022-23,2023-24,2024-25`):

| season | live | m7under5 | paired a day | p(worse) | legs |
|---|---|---|---|---|---|
| 2022-23 | 45 groups, +28.7% | 83 groups, +5.9% | -0.25 | 0.84 | 249 |
| 2023-24 | 16 groups, -36.6% | 42 groups, -15.7% | -0.04 | 0.55 | 126 |
| 2024-25 | 56 groups, -0.4% | 101 groups, -14.8% | -0.44 | 0.94 | 303 |
| 2025-26 | 44 groups, +22.0% | 74 groups, -3.7% | -0.41 | 0.96 | 222 |
| 2026-27 | 1 group, lost | 4 groups, -42% | -0.34 | 0.62 | 12 |
| pooled | 162 groups, 73 won v 67.5, +9.6% | 304 groups, 120 won v 120.5, -6.9% | -0.31 | 0.99 | 912 |

`m7under5` is behind live in all five seasons. The extra groups land exactly
as the bookmakers price them (120 v 120.5), so they carry the margin and no
edge. The value demand stays; the pool's first-price lead is the noise it
looked like. `m7under5` keeps replaying nightly.

`m7core` is identical to live on every football-data season: football-data's
leagues are all core leagues, so the wider-leagues question (CARD_RULE 11)
can only be read on the pool. The 30 Nov review should not count this as a
football-data pass for either side.

The pooled table also lists every rule 7 shape variant against live for the
first time; none is ahead pooled (m7edge3 p(worse) 0.91, m7short 0.80,
m7legs2 0.98, pay15 0.83, pay25 0.98, pay3 0.91, ladder 0.76). The Card's
shape (the 2x alone, 3-5 picks, value demand 0) is the best of those tried.
