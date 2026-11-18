# Rule 13's split had no groups: the re-check dropped `rule12Fault` (18 Nov 2026)

## What was wrong

Under `CARD_RULE` 13 every Card leg is meant to carry `rule12Fault`, what
rule 12's two bookmaker conditions (the value demand, the football opposition
at 5.0+) would have said of it, so the record can split the rule 13 groups
(`cardRule13Split`, `claude/card-rule13-split-2026-11-17.md`). `best_card`
set it, but `recheck_card` rebuilds every leg from the build's board on each
build, and the board's legs never had it. A group is re-checked on the build
after it is first published, so the field was gone before any group locked.

At the 18 Nov 12:14 Card review the split read 0 and 0 with "2 rule 13
groups built before `rule12Fault` was kept"; by the next grading all four
rule 13 Card groups (17 Nov, three on 18 Nov) were `unknown`. No archived
rule 13 leg carries the field.

## The fix

- `recheck_card` asks rule 12 again on each rebuilt leg (`keeps_rule12`, the
  same condition as `best_card`), so the archived leg holds the verdict on its
  numbers at the start.
- `grade` reads an archived rule 13 Card leg without the field from the leg
  as frozen (`rule12_fault`: the value demand and the opposition floor alone,
  at `RULE12_PATCH`'s values; the other conditions are not asked again, as
  the live rule passed them) and marks it `r12: "derived"`. The split counts
  those groups (`derived`) and the nightly review says so in a line.
- Nothing hand-edited: the archive files are untouched.

Tests: `tests/test_card_rule12_recheck.py` (fails on the old code: the field
lost on the re-check, the derived reading, rule 11 groups left alone).

## What the four groups say (derived, n tiny)

| day | group | picks rule 13 alone admits | result |
|---|---|---|---|
| 17 Nov | Tonbridge, Spurs, Lakers | Tonbridge (opp 3.65), Spurs (model 69% v bookmakers 78%) | lost on Spurs |
| 18 Nov | Isparta 32, Raptors, Thunder | Isparta (opp 4.41), Thunder (69% v 70%) | lost on Isparta |
| 18 Nov | Şanlıurfaspor, Pistons, Lakers | Şanlıurfaspor (62% v 62%) | pending |
| 18 Nov | Cotonsport, Rockets, Suns | Cotonsport (63% v 69%), Suns (70% v 70%) | pending |

Every rule 13 group so far holds at least one pick rule 12 would have
refused, and both settled groups lost on one of them. Four groups is nothing
to act on (the gate is 100+ legs and the switch was Douglas's call); it is
what the split now records, read at the 30 Nov review or 50 settled groups
beside the `rule12` replay, as pre-registered.
