# The empty-day fillers: issue #155 closed as overtaken (17 Nov 2026)

Backlog task: test opp7, short (1.15-1.35) and Championship-tier fillers on the
replay and ship the one that keeps the return and fills the most days.

## Why nothing ships

The test was done on 10 Nov (`claude/card-fillers-2026-11-10.md`) and the
question it served was settled by the owner on 11 Nov
(`claude/card-filler-off-2026-11-11.md`): `CARD_FILLER = False`, an empty day
stays empty ("The groups must win at all costs. The source of truth is my
model."). Since then the Card is the model's own picks (rules 7 to 12), so the
rule-6 empty-day problem the issue describes no longer exists in that form.

What the earlier read found, for the record:

- `fillopp7` and `fillshort` built nothing on any empty day (pool, 30 Oct to
  9 Nov): they fill zero days, so they cannot be the one that fills the most.
- `fillrule5` (no opposition condition) was the only filler that built:
  pool 4 groups, 2 won v 1.28 expected (+12%, 12 legs; p(worse) 0.30 v live);
  football-data 2025-26 25 groups, 10 won v 7.95 (+2.0%, +10.5% at best).
  Well under the 100-leg gate, so it was never a rule change.
- `fillwide` (the page's own filler): pool 2 of 12 v 4.14 expected (-54%),
  p(worse) 0.95; football-data -0.9% and -11.7%.
- Live `cardWide` at 17 Nov: 3 groups, 1 won v 1.08 expected, 4.18 returned
  on 5 units staked (-16%).
- The Championship-tier idea was not replayed: the 227 wider leagues are
  already admitted to the Card (rule 11), and a filler built on a league tier
  would again be chosen outside the model's own picks, which the owner has
  ruled out.

## Decision

No code change. Documentation only. A filler returns only if the owner reverses
11 Nov; then `fillrule5` is the one to pre-register against, on its own 100
pool legs (`card_replay.py`, `card_review_post.fill_lines` still report it).
