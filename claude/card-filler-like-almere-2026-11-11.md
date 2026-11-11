# The Card's filler, more like Almere City (11 Nov 2026)

Douglas, 11 Nov 2026, on Saturday 14 Nov's Card: "I don't fancy Luton or
Southend at all. I really like Almere City. Make sure all picks are more like
Almere and less like Luton and Southend."

## What Saturday's Card was

The full rule built nothing for 14 Nov, so the page showed the empty-day
filler (the wider rule): a Card 3x at 3.25, a 24% chance.

| pick | league | price | bookmakers | model | opposition | why the full rule refused it |
|---|---|---|---|---|---|---|
| Luton Town v Cambridge | League One | 1.66 | 56% | 60% | 4.48 | model not 5 under the market |
| Southend v Aldershot | National League | 1.38 | 66% | 59% | 6.27 | opposition under 9 |
| Almere City v Helmond | Eerste Divisie | 1.42 | 65% | 68% | 5.88 | model not 5 under the market |

## The test

Every football leg the wider rule admitted on the site's archive and pool
(30 Sep to 14 Nov, `--recover`), by the shape of each pick:

| band | legs | landed | bookmakers | singles | best price |
|---|---|---|---|---|---|
| bookmakers under 60% (Luton) | 107 | 57.9% | 57.3% | -6.3% | -4.3% |
| 60%+, model within 5 points (Almere) | 82 | 73.2% | 68.2% | +0.9% | +3.0% |
| 60%+, model 5-10 under (Southend) | 55 | 78.2% | 67.8% | +7.4% | +9.5% |
| 60%+, model 10+ under | 77 | 72.7% | 70.3% | -3.2% | -0.9% |

Luton's shape is the worst band. Southend's is the best one. A cut on the
site's own tested chance (Luton and Southend both 54%, Almere 65%) was also
tried and points the other way: legs under 60% on it returned +13.4% on 43.

## What changed

`CARD_WIDE_FAIR_MIN` 0.55 to 0.60 (`CARD_WIDE_RULE` 2): the filler takes only
picks the bookmakers make 60%+ favourites, like Almere and like the full rule.
Wider-rule groups now carry `wideRule`, and `groupings-record.json` tallies
each version in `cardWideByRule`. The page's two lines on the filler read the
floor from the rules instead of saying 55%.

The whole filler replayed (`tools/card_replay.py`, `fillwide`): 43 groups,
17 won, +0% (+7% best) before; 33 groups, 13 won, -1% (+5% best) after, legs
landing 75.0% v 69.7% quoted (from 72.9% v 68.3%). No measurable change in
the groups' return, fewer groups, legs a little further above quote. This is
the owner's call with the leg evidence pointing the same way, not a change
that passed the Card's gate.

## Not changed

Southend's shape is not refused: the evidence says it is the best band.
The full rule, `CARD_RULE`, the stakes, the pre-registered drop-the-filler
decision (CLAUDE.md), the record of past wider-rule groups (version 1).

Saturday with the change, on the pool at 01:00 UTC 11 Nov: Luton is off; no
filler group builds yet (Almere and Southend alone do not make one). Each
build re-checks it as more prices arrive.
