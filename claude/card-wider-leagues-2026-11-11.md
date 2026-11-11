# The Card takes the wider leagues (CARD_RULE 11, 11 Nov 2026, late evening)

## What Douglas asked

On Sutjeska Foča v Leotar (Bosnia RS 1st League, Leotar 1.52 at Hill, model
67%, bookmakers 59%, the opposition 5.20), off the Card: "There are still
games that should of made a card." Told the league limit was the only thing
keeping it off and what the replay says, he replied: "This should have been
on. So relax all rules that would of said otherwise."

## What kept it off

Only the league. Under rule 10 `model_fault` admits football from the core
leagues alone (`CARD_CORE_ONLY` True); Bosnia RS is an API-Football wider
league (`af.317`). Price (1.15-1.90), the model at 60%+, the model at or above
the bookmakers, and a clean Daily List reason all pass.

## What changed

- `groupings.CARD_CORE_ONLY` False, `CARD_RULE` 11. Wider means `card_league`:
  API-Football leagues in; cups, internationals and new leagues still out.
  `CARD_CORE_NUDGE` still puts a core pick first at an equal chance.
- `tools/card_replay.py`: `m7core` replays core only beside live; the rule 6
  family's base now pins `CARD_CORE_ONLY` True so `rule6` replays unchanged.

## The evidence he was shown, against

The replay on the pool (`claude/card-m7wide-2026-11-11.md`): core only 12
groups, 8 won, +69%, legs 32 of 36; wider 28 groups, 15 won, +32%, legs 67 of
84 (`--recover`, p(worse) 0.44); first real prices +82% v +19%. More groups,
lower return. The owner's call, not a gate pass.

## What would reverse it

At the 30 Nov review, if `m7core` beats live on the legs from 10 Nov with
p(worse) at most 0.30, the league limit goes back. The record splits by
`CARD_RULE`, so rule 11's groups are graded apart.
