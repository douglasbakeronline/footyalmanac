# Empty Card days, fillers asked again (20 Nov 2026)

Planner task: 3 of 18 days since 29 Oct had no full-rule group (5, 9 and 19 Nov);
test opp7, short and a Championship-tier filler, ship the one that keeps the return.

## Why nothing ships

Same idea as `claude/card-fillers-closed-2026-11-17.md` and
`claude/card-fillers-2026-11-10.md`; no new evidence since:

- `fillopp7` and `fillshort` built nothing on any empty day (zero days filled).
- `fillrule5` built 4 groups on the pool (12 legs, +12%, p(worse) 0.30), far
  under the 100-leg gate; `fillwide` 2 of 12 v 4.14 expected.
- The Championship tier is already admitted to the Card's pool under rule 11 and
  a league-tier filler is a bookmaker/tier choice outside the model's own picks,
  which Douglas ruled out on 11 Nov (`CARD_FILLER` False, "the groups must win
  at all costs").
- 5 and 9 Nov fall under rules 5 and 6 (pre rule 7); 19 Nov is the day rule 14
  went live on rule 8's constants (value demand on, core leagues only), where a
  few empty days are the price of the tighter rule, chosen by the owner.
  3 of 18 days empty (17%) is not a gap in the record's sense: no group was
  published, so nothing was lost.

## Decision

Documentation only, no code change, no gates run (no new test). Revisit only if
the owner reverses 11 Nov, or at the 30 Nov review beside `rule13` and `span2`.
