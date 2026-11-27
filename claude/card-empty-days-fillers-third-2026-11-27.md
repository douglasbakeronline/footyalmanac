# Empty Card days, fillers asked a third time (27 Nov 2026)

Planner task: 9 of 26 days since 29 Oct had no full-rule group (9 Nov, then 19, 20,
23, 24, 25, 26, 27 Nov); test opp7, short and a Championship-tier filler.

## Why nothing ships

No new evidence since `claude/card-fillers-2026-11-10.md`,
`claude/card-fillers-closed-2026-11-17.md` and
`claude/card-empty-days-fillers-again-2026-11-20.md`:

- `fillopp7` and `fillshort` fill zero empty days; `fillrule5` built 4 groups on
  the pool (12 legs, +12%, p(worse) 0.30), far under the 100-leg gate;
  `fillwide` 2 of 12 v 4.14 expected. The filler is `CARD_FILLER` False by the
  owner's call (11 Nov: "the groups must win at all costs").
- The Championship tier is already inside the Card's pool (rule 11 admits the
  wider leagues; rule 14 returned to core leagues only by the owner's call on
  19 Nov). A league-tier filler is not the model's own pick.
- What the page's own log says (`groupings-archive/card-short.json`): the recent
  empty days are `few` (0 or 1 pick clear of the rule: 26 Nov none, 27 Nov Werder
  Bremen alone at 1.72/62%, 30 Nov none) or `long` (27 Nov, 4.13 at best, over the
  2x top). There is no near-miss pool for a filler to draw on; a filler would
  have to lower the 60% floor or the price floor, which `card-filler-like-almere`
  and `card-m7legs2` showed costs return.
- The run of empties from 19 Nov is rule 14 (rule 8's tighter constants) doing
  what it was chosen to do. `rule13` and `span2` replay what was switched off;
  the 30 Nov review reads them (`claude/card-review-agenda-2026-11-30.md`).

## Decision

Documentation only, no code change, no gates run. Revisit at the 30 Nov review,
or if the owner reverses 11 Nov (then `fillrule5` is the one to pre-register).
