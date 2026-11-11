# The Card becomes the model's own picks (11 Nov 2026, CARD_RULE 7)

Douglas, 11 Nov 2026: "I want the model to pick higher than the bookmakers
also - I need wins." Asked to choose between making the Model card the Card,
staking both, or waiting for the 30 Nov review: "The model rules. Then it's
about finding a good edge."

## What changed

`groupings.CARD_MODEL_RULE` True, `CARD_RULE` 7. The Card's full rule is now
the Model card's (`model_fault`): a bookmaker-priced pick at 1.15-1.90 the
model rates 60%+ and at or above the bookmakers' chance; football from the
core leagues and clean for the Daily List; tennis 75%+ on model and tested
rate; NFL, college football and college basketball off. Each pick's chance,
and so each group's, is the model's own (`as_card` -> `as_model`). Groups are
chosen on the highest combined model chance per unit of price, so a bigger
edge (the model above the market) ranks first at an equal price. Stakes,
kinds, windows, bench, drift and the filler are unchanged; the filler is
still chosen on the bookmakers' numbers. The paper Model card stops being
built (it would repeat the Card); its record stays.

## The evidence at the switch (all under the 30 Nov gate)

| sample | rule 6 Card | rule 7 (the model's picks) |
|---|---|---|
| live record | 11 of 35 groups, -12% flat, -19% at its stakes | Model card on paper 6 of 14, +19%; legs 34 of 42 (81%) |
| replay, pool + archive (`--recover`, 14 days) | 10 groups, 4 won, -7% | 23 groups, 10 won, +37% (+41% best); legs 73.9% v 65.1% quoted |
| paired | | rule 6 v rule 7 -1.01 units a day, p(rule 6 worse) 0.93 |
| football-data 2025-26 | 0 groups under rule 6 | -8.2% on 70 groups (the model above the market landed at the market's rate) |

69 replay legs is under the 100-leg gate and football-data disagrees, so
this is the owner's call, not a gate pass. Saturday 14 Nov on the pool at
01:00: Almere City and VVV-Venlo clear the new rule; more legs price later.

## How it is watched

- `cardByRule["7"]` in `groupings-record.json` from the first group.
- `rule6` in `tools/card_replay.py` replays the old Card on the same legs
  every night, so the 30 Nov review still pairs them. `modelcard` now equals
  live.
- The test modules for the rule 6 machinery run under rule 6
  (`setUpModule`); `tests/test_card_model_rule.py` covers rule 7.
- `tools/card_funnel.py` keys card_fault's rule 6 messages; under rule 7
  most faults read as "other" until the funnel learns the new messages.

## Roll back

`CARD_MODEL_RULE = False`, `CARD_RULE = 6` (or revert the merge commit).
