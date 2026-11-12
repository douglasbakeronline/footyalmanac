# The rule 6 replay kept the live tennis floor (12 Nov 2026)

**Finding.** `tools/card_replay.py` builds the rule 6 family (`rule6`, `under8`,
`uncapped`, `rule5`, `opp7`, `notennis`, `tennis80`, ...) on `RULE6`, which
pinned the rule 6 Card's own constants but inherited `CARD_SPORT_MIN`. When
`CARD_RULE` 10 raised the live tennis floor to 85% on 11 Nov evening, rule 6
silently replayed at 85% too. No pool tennis leg reaches 85%, so `rule6`,
`notennis` and `tennis80` came out identical ("identical to rule6" in the
pairings), and `rule6` fell from 11 groups to 3 on `--recover` and to none at
first real prices. The two tennis variants are the evidence for the tennis
tripwire and the 30 Nov review, so they were reading nothing.

**Fix.** `RULE6` pins tennis at 75%, the floor rule 6 ran with (29 Oct to
11 Nov), as `CARD_CORE_ONLY` was pinned on 11 Nov. Live, `tennis75` and every
rule 7/8 variant are unchanged. Test: `tests/test_card_replay_rule6_family.py`
`test_rule6_keeps_its_tennis_floor`.

**Numbers after the fix**, pool 30 Oct to 14 Nov:

| read | variant | groups | won | return | paired |
|---|---|---|---|---|---|
| `--recover` | live (rule 11) | 27 | 15 | +38% | |
| `--recover` | rule6 | 11 | 5 | +8% | v live -1.26 units a day, p(worse) 0.96 |
| `--recover` | notennis | 3 | 2 | +65% | v rule6 +0.23 a day, p(worse) 0.42 |
| `--recover` | rule5 | 24 | 13 | +30% | |
| first real price | rule6 | 1 | 1 | +141% | v live -0.05 a day, p(worse) 0.52 |

`rule6` at +8% matches the 11 Nov morning read (`claude/card-replay-rule6-family-2026-11-11.md`),
so the family is back to what was registered. All under the 100-leg gate;
nothing to act on, no rule changed. Before the fix `rule5` read 19 groups
+43%; with tennis back at 75% it reads 24 groups +30%.

**Rule for later pins.** Every constant a later `CARD_RULE` changes, and that
the rule 6 Card reads, needs pinning in `RULE6` in the same release; the test
above is the pattern.
