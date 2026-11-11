# The rule 6 family replays on rule 6 again (11 Nov 2026)

## What was wrong

When the Card became the model's own picks (`CARD_RULE` 7, then 8), the
replay variants pre-registered for the 30 Nov review stayed as patches on
`live`. Rule 7/8 reads none of `CARD_UNDER_MARKET`, `CARD_UNDER_MAX`,
`CARD_OPP_MIN` or `CARD_CORE_ONLY`, and builds no 3x, so `under8`, `under10`,
`four3x`, `wider`, `uncapped`, `rule5`, `opp7` rebuilt live exactly. The
11 Nov Card review (#235) shows them all "identical to live", p(worse) None,
and the fillers `fillrule5`, `fillopp7`, `fillshort` built nothing. The
football-data side (`tools/card_legs_history.py` `cardRule5`,
`cardUncapped`, `cardOpp7`, `cardFillRule5`, `cardFillOpp7`) goes through
the same `card_replay.build`, so Monday's `tune.yml` run would have written
live's numbers under those names. The 30 Nov review would have read every
pre-registered question as "no difference".

## The fix

`tools/card_replay.py`: `RULE6` (the rule 6 Card: model rule off, rule 6,
2x and 3x) and `RULE6_FAMILY` (`rule6`, `under8`, `under10`, `four3x`,
`wider`, `uncapped`, `short`, `rule5`, `opp7`, `notennis`, `tennis80`).
`patch_of(v)` lays a family variant's one change on `RULE6`, as it was
registered. The fillers call the family variants, so `fillrule5` is now live
(rule 8) plus a rule 5 group on a day live leaves empty. Family variants are
paired against live as before and also against `rule6`, their own base
(`vsRule6PerDay`, `pWorseVsRule6`, `base: "rule6"`); the nightly review
prints a "Rule 6 family" line. The `m7*` variants, `comp3`, `flatstake`,
`with3x` and `modelcard` stay on live.

## The numbers on the pool (11 Nov, `--recover`, 30 Oct to 14 Nov)

Approximate: 781 legs archived before `priced` existed are read at their
last price. Under every gate (100+ legs); nothing to act on.

| variant | groups | won | return | v live a day | p(worse) | v rule6 a day | p(worse) |
|---|---|---|---|---|---|---|---|
| live (rule 8) | 12 | 8 | +69% | | | | |
| rule6 | 11 | 5 | +8% | -1.35 | 0.97 | | |
| rule5 | 24 | 13 | +30% | -0.33 | 0.69 | +0.95 | 0.05 |
| uncapped | 12 | 6 | +15% | -1.19 | 0.96 | +0.24 | 0.26 |
| short | | | | -1.05 | 0.96 | +0.62 | 0.19 |
| notennis / tennis80 | | | | -1.32 | 0.95 | +0.23 | 0.41 |
| opp7, under8, under10 | | | | | | identical to rule6 | |
| fillrule5 | 15 | 11 | +82% | +0.62 | 0.00 | | |
| fillwide | 25 | 17 | +56% | +0.51 | 0.06 | | |

Read: on these 13 days rule 8 is ahead of every rule 6 variant; within the
old rule, dropping the opposition condition (rule 5) would have helped it.
The fillers are ahead of an empty day, as before on few legs; the
pre-registered drop-the-filler rule (`fillwide` 100 own legs) is unchanged.

## Not changed

Any Card rule, the page, the record. Rule 7/8's own variants and their
numbers are unchanged.
