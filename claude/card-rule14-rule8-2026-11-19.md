# The Card back on rule 8's constants: rule 14 (19 Nov 2026)

Douglas, 19 Nov 2026, shown every Card rule rebuilt on the same days
(`claude/card-rules-timeline-2026-11-19.md`) and asked which card had the
most successful return: "let's then group to rule 8 for what we're showing
on the live site at the moment, please. And let's have any data viz just
specific to rule 8 on the bets cards."

## What changed

`CARD_RULE` 14 sets rule 8's constants live, which undoes the three
widenings of 11 to 19 Nov and the two-day groups:

| Constant | Rule 13 (17 to 18 Nov) | Rule 14 |
|---|---|---|
| `CARD_MODEL_EDGE` | None (no value demand) | 0.0 (the model at or above the bookmakers) |
| `CARD_CORE_ONLY` | False (wider leagues) | True |
| `CARD_SPORT_MIN` tennis | 0.85 | 0.75 |
| `CARD_SPAN` | True | False |
| `CARD_MODEL_OPP_MIN` | {} | {} (unchanged) |
| `CARD_BUILD` | 2x alone | 2x alone (unchanged) |

Rule 8 was measured without two-day groups (they came in on 12 Nov, after
it), so rule 14 runs without them; `span2` replays them on top.

The replay (`tools/card_replay.py`): `live` is now rule 8's patch, so
`rule8` is identical to live and `m7core`, `tennis75`, `m7value`, `m7noopp`
and `nospan` all equal live too. Rules 10 to 13 are pinned in full (they had
relied on live carrying the wider leagues, the 85% floor and two-day groups)
and `rule13` is a named variant. `RULES` carries rule 13's dates (17 to
18 Nov) and rule 14 from 19 Nov.

The Bets tab's scoreboard ("Is it working?") headlines the live rule's own
groups (`cardLive`, `cardLiveRule`, `cardLiveLegsBySport` in
`groupings-record.json`: the record tallied for groups built under
`CARD_RULE`), with the rule named and dated (`RULE_WHAT`, `RULE_FROM` in
`index.html`) and the by-sport table on its legs; the Card over every rule
and each rule's line sit under More numbers. The Card's rule text reads
`coreOnly`, `sportMin` and `span` from `rules.card` rather than hard-coding
the 11 Nov wording.

## The evidence at the switch (the pool, 30 Oct to 19 Nov, every rule rebuilt on the same days)

Rule 8: 8 groups, 5 won against 3.2 expected, +64%; 24 legs, 83% landed
against the model's 73% and the bookies' 68%, +14% a leg. Rule 13: 46
groups, 19 won against 17.4, -4%; 138 legs, 72% landed, -3% a leg. Rule 8 v
live paired by day +0.51 units a day, p(worse) 0.15, under the 0.30 bar but
on 8 groups and 24 legs, well under the 100-leg sample the gate asks for.
The five-season football-data replay agrees in direction: the model's picks
at or above the bookmakers, core leagues, 2x alone was +9.6% pooled and
ahead in four seasons of five; dropping the value demand was behind in all
five.

The owner's call on a small sample, made knowing it. The cost is volume:
rule 8 built a group on about one day in three on the pool (8 groups over
21 days); rule 13 on most days. The Daily 2x (every day) and the List card
are unchanged, so the Bets tab still has a slip every day.

## What to expect and when to read it

At 0.35 groups a day rule 14 reaches 30 groups around the new year and 100
in the spring. Read it at 30 Nov beside `rule13` and `rule12` on the same
days, and do not change it before then: every rule change resets the clock
(`claude/card-rules-timeline-2026-11-19.md`). Roll back to rule 13 with the
`rule13` variant's constants and `CARD_RULE` 15.

## Files

`groupings.py` (the constants, `card_legs_by_sport(rule=)`, `cardLive`,
`cardLiveRule`, `cardLiveLegsBySport`), `tools/card_replay.py` (`span2`,
rules 10 to 13 pinned, `rule13`, `RULES`), `index.html` (`tbRecord`,
`RULE_WHAT`, `RULE_FROM`, `.tb-rule-line`, the rule copy), tests re-pinned
(`test_card_span`, `test_card_legs_history_span`, `test_card_replay_live_span`,
`test_card_rule12_recheck`, `test_card_m7wide`, `test_card_m7cap160`,
`test_card_replay_coverage`, `test_card_replay_rule6_family`,
`test_card_m7_paired`, `test_card_model_rule`, `test_card_m7opp`,
`test_card_rule13`, `test_card_rules_table`, `test_groupings_card`).
