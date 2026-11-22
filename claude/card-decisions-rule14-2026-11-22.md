# The decisions table reads rule 14 (22 Nov 2026)

The nightly Card review's pre-registered decisions table
(`tools/card_review_post.decisions_section`,
`claude/card-decisions-table-2026-11-18.md`) still read rule 13's decisions
three days after rule 14 (19 Nov, `claude/card-rule14-rule8-2026-11-19.md`)
set rule 8's constants live. The 21 Nov issue asked "Rule 13 (the model
alone) v rule 12" about a rule no longer staked, and kept "Tennis floor back
to 75%" and "Core leagues only again" waiting on changes rule 14 had already
made (`tennis75` and `m7core` identical to live).

## What changed

From the record's live rule (`groupings-record.json` `cardLiveRule`) 14 on:

- One row, **Rule 14 (rule 8's constants) v rule 13 and rule 12**: trigger
  30 Nov, read beside `rule13` and `rule12` on the same days, no Card rule
  change before then; now: the live rule's own groups (`cardLive`) and both
  variants' pool reads; who acts: Douglas (the switch was his). When
  `rule13` sits ahead of live on the pool at p(worse) 0.30 or under, the
  row says so in bold, with the football-data caveat beside it.
- The tennis 75% and core-league rows are retired, with one line under the
  table saying rule 14 settled them.
- The opposition-floor rows name Douglas with "no Card rule change before
  the 30 Nov read" rather than rule 13.

Before rule 14 (`cardLiveRule` under 14 or absent) the table is unchanged.

## What the table shows tonight (21 Nov's replay)

`rule13` v live +0.52 units a day, p(worse) 0.219, 102 legs on the pool
(34 groups, 17 won v 12.95 expected, +18.9%; live 6 groups, 3 won v 2.39,
+25.3%). On the pool alone that clears the gate's p(worse) and leg count,
so the 30 Nov read has something to decide. The gate also asks for both
football-data seasons, and the five-season read had dropping the value
demand behind in all five (`claude/card-rule14-rule8-2026-11-19.md`), so
nothing is due and no rule changed. `rule12` v live -0.47 a day, p(worse)
0.742, 51 legs. The live rule 14 Card had two groups on 21 Nov, none
settled.

## Files

`tools/card_review_post.py`, `tests/test_review_decisions.py`
(`test_rule14_rows`, `test_rule14_opposition_owner`).

## Roll back

`git revert` the merge.
