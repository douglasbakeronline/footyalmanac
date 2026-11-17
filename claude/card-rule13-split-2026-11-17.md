# Rule 13's groups split by what rule 12 would have said (17 Nov 2026)

## Why

Rule 13 (17 Nov 2026, Douglas: "just drop both of those") put the Card on the
model alone. Every Card leg built under it carries `rule12Fault`, rule 12's
verdict on the pick (`groupings.fault_under(l, RULE12_PATCH)`), but nothing
read the field: the graded record dropped it, so the 30 Nov review could only
compare the two rules by replay. Item 6 of
`claude/card-rule13-model-only-2026-11-17.md` asked for the split.

## What

- `groupings.grade` keeps `rule12Fault` on every graded leg, with `r12`
  (False when the leg was built before the field existed).
- `groupings-record.json` `cardRule13Split` (`card_rule13_split`), over the
  rule 13 Card (full rule, not wide, not late):
  - `rule12`: groups where rule 12 would have admitted every pick, the full
    `tally()` (won, expected, z, return at average, best and the page's
    stakes);
  - `rule13only`: groups holding at least one pick only rule 13 admits;
  - `unknown`: rule 13 groups with a leg built without the field;
  - `legs`: each settled pick once a day, landed against the model's chance,
    by its own verdict.
- The nightly Card review prints it as a table
  (`card_review_post.rule13_split_section`), silent until a rule 13 group exists.

At the time of writing the split is empty: no rule 13 group has locked yet
(the first are for 17 Nov).

## How to read it at the 30 Nov review

This is the live record, so it decides nothing alone (Rule 1, nothing is
fitted on it). Read it beside the `rule12` replay: if `rule13only` groups land
under their expected count while `rule12` groups hold, the switch is what is
costing the Card, and that goes to Douglas with the numbers, as the rule 13
note says. A `rule13only` group can still win on its rule 12 picks, so the leg
line is the sharper read: picks only rule 13 admits, landed v the model's chance.

## Not changed

Any Card rule, `CARD_RULE`, the page. Display in the review and the record only.
Roll back: `git revert`.
