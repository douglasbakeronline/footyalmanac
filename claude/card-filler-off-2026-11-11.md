# The Card's empty-day filler switched off (11 Nov 2026)

## The request

Douglas, on the screenshot of 8 and 9 Nov (Mon 9 Nov: two wider-rule groups
lost, 2.01 and 3.07; Sun 8 Nov: the Card 2x lost on Detroit, the paper
Model 2x and 3x lost): "The groups must win at all costs. The source of
truth is my model. But the groups need to surface games that will win."

## What the record said

`groupings-record.json` at 11 Nov, the Card by rule:

| Rule | Groups | Won | Expected | Units staked | Returned |
|---|---|---|---|---|---|
| 1 | 16 | 4 | 5.02 | 16 | 12.22 |
| 4 | 5 | 3 | 1.53 | 8 | 10.40 |
| 5 | 10 | 2 | 3.56 | 17 | 8.19 |
| 6 | 5 | 3 | 1.97 | 10 | 13.28 |
| Filler (`cardWide`) | 3 | 1 | 1.08 | | |

Rule 6's full-rule Card, 6 to 10 Nov, was ahead (3 of 5, +33% at the page's
stakes). The bad screen of 9 Nov was the filler. The paper Model card was
never staked.

The filler on the replay (`claude/card-fillers-2026-11-10.md`): pool 2 of
12 won v 4.14 expected (-54%, 36 legs); football-data at or under the price.

## The decision

`groupings.CARD_FILLER = False`. The filler is the only part of the Card
chosen on the bookmakers' numbers rather than the model's, which runs against
"the source of truth is my model", and it is the weakest part on every
sample. An empty day stays empty.

The pre-registered gate (100 pool legs, p(worse) 0.70+) was not reached, so
this is the owner's call, with every sample pointing the same way.

## What it costs

Volume. Rule 7 / 8 builds no group on many days: on 11 Nov no priced pick in
the pool passed `model_fault`, mostly for want of a price or a sport off the
Card. Expect empty days. The cure for volume is more legs priced (the
funnel's first failing condition is "no bookmaker price"), not looser picks.

## What "win at all costs" can and can't mean

The chooser (`best_card`) already takes the combination with the highest
combined chance, on the model's own numbers since rule 7, among those paying
2.0 to 3.0. A group paying 2.0 can't be made to win much more than half the
time at a fair price: the payout sets the chance. Winning more often means a
lower payout (a 1.5x group), which is Douglas's call to make, and a new kind
would need replaying before it shows.

Also on record: picks the model rates well above the market have landed at
the market's rate (`tools/market_check.py`, `claude/card-seasons-2026-11-09.md`),
so the model's number is the chooser but the price is still the better
guide to how often a group lands.

## Roll back

`CARD_FILLER = True` (tests: `WiderRule` runs with it on, `FillerOff` off).
