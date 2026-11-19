# Every Card rule on the same days (19 Nov 2026)

Douglas, 19 Nov 2026: "I would have hoped that the idea for the card rule
has been tracked the entire time since it was incepted ... which rule has
performed the best over the entire timeline."

It had been, by parts: every rule change left a replay variant behind
(`rule6`, `m7core`, `m7value`, `rule12` ...) but under the names of the
changes, not the rules, and the pre-model rules 1, 4, 7, 8 and 10 had no
variant of their own. Now `tools/card_replay.RULES` names every `CARD_RULE`
the page has run, with its live dates, and builds each on the whole pool
(30 Oct to today, every sport, first real price), so every rule is read on
the same days. The replay prints the table, `card-replay.json` carries it
(`rules`), and the nightly Card review has a section (`rules_section`) with
the live record beside it (`cardByRule`, the days each rule ran).

What each variant is: rules 1, 4 and 5 sit on the rule 6 base (`RULE6`:
core leagues, tennis 75%, 2x and 3x, no two-day groups) with the later
conditions taken off (rule 1 any league, no gap cap, no opposition floor;
rule 4 core leagues; rule 5 the cap). Rules 7, 8 and 10 are the model's picks
with the value demand on, no two-day groups, core leagues, tennis 75% then
85%, 2x and 3x then the 2x alone. Rule 11 is `m7value` with two-day groups,
rule 12 adds the football opposition floor, rule 13 is live. Rule 9, the
context veto, cannot be rebuilt on days it did not read; rules 2 and 3
changed only the windows and the page.

## The read at 19 Nov (54 pool days with legs, 30 Oct to 19 Nov)

| Rule | Live | Groups | Won / expected | Return | v live a day | p(worse) | Live record |
|---|---|---|---|---|---|---|---|
| 1 bookmakers' favourites, any league, 2x and 3x | 25 to 28 Oct | 55 | 20 / 17.8 | -6% | -0.06 | 0.53 | 16, 4 won, -24% |
| 4 core leagues only | 29 to 30 Oct | 29 | 14 / 9.8 | +23% | +0.48 | 0.19 | 5, 3 won, +30% |
| 5 gap capped at 10 under | 31 Oct to 5 Nov | 15 | 9 / 5.2 | +42% | +0.52 | 0.17 | 10, 2 won, -52% |
| 6 opposition 9+ | 6 to 10 Nov | 4 | 2 / 1.6 | +12% | +0.16 | 0.39 | 5, 3 won, +33% |
| 7 the model's picks, 2x and 3x | 11 Nov | 17 | 6 / 5.7 | +20% | +0.32 | 0.22 | 0 |
| 8 the 2x alone | 11 Nov | 8 | 5 / 3.2 | +64% | +0.51 | 0.15 | 0 |
| 10 tennis 85%+ | 11 Nov | 7 | 4 / 2.7 | +56% | +0.42 | 0.21 | 0 |
| 11 wider leagues, two-day groups | 11 to 15 Nov | 26 | 9 / 10.5 | -14% | -0.14 | 0.62 | 4, 1 won, -19% |
| 12 football opposition 5.0+ | 16 Nov | 25 | 10 / 10.2 | -3% | +0.08 | 0.46 | 0 |
| 13 the model alone (live) | 17 Nov on | 46 | 19 / 17.4 | -4% | | | 4, 1 won, -40% |

How to read it. No rule is ahead of live at p(worse) 0.30 on 100 legs, the
bar a rule change needs; the best-looking rows (5, 8, 10) are 7 to 15 groups
and move by several points with each day's results (rule 12 was +34% on 20
groups two days ago and is -3% on 25 today). What the table does say, and
has said in every read since 9 Nov: the rules that build few groups from
the core leagues on the bookmakers' favourites sit above their expectation,
and every widening (rule 1, rule 11, rule 13) sits at or under it. Volume
and return have pulled against each other at every step.

## Where it lives

- `tools/card_replay.py`: `RULES`, the variants `rule1`, `rule4`, `rule7`,
  `rule8`, `rule10`, `rule11` (the others existed), `rules_table`, printed at
  the end of every run and written to the report as `rules`.
- `tools/card_review_post.rules_section`: the nightly issue's table, with
  `cardByRule` beside it.
- `tests/test_card_rules_table.py`.

A rule that starts (rule 14) is added to `RULES` with its dates and the
previous live rule's patch becomes a named variant, so the table never
loses a row.
