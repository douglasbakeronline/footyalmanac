# The pool's order-of-play flag, and the Card's tennis legs (14 Nov 2026)

Build session, 14 Nov 2026, 15:17. HQ's backlog led with "Card tennis legs:
8/15 against 12 expected". Reading the pool for it turned up a replay
fidelity fault, fixed here. No Card rule changed.

## The fault

A tennis match that ESPN dates before its order of play is out takes its
tournament's usual first start (`tennis_starts`) and `timeEst`. The live Card
refuses such a leg ("no order of play yet") and re-reads it on every build;
once the real time arrives it can be admitted. The pool archive
(`archive_pool`) keeps every row as first written except the last-price
fields, so `timeEst` stayed True for good. The replay (`card_replay.pool_legs`)
and the funnel (`card_funnel.pool_days`, `unpriced_ok`) read the row through
the live `card_fault`, so those legs were refused as "no order of play" for
ever: the funnel's tennis "no-time" column (19 legs from 6 Nov in the
14 Nov review) counted matches that had a real time hours before they began.

At 14 Nov: 21 tennis pool rows carry `timeEst`, every one on a day already
played, every one with a later real start in history-tennis/ (Casper Ruud v
Shevchenko, estimated 10:00, played 17:05 on 11 Nov; Andreescu's four
matches at the DIRECTV Open).

## The fix

`archive_pool` stamps `timeSet` (the build) and `whenSet` (the start it read)
once, from the first pre-start build whose leg has a real time. `timeEst` as
first written is never changed. `groupings.pool_time_est(row)` reads the pair
and the replay, the funnel and the price-gap count use it.

Forward only: the 21 rows written before today carry no `timeSet` and keep
their flag (the archive is bot-written, never edited by hand). None of them
would have reached the live Card anyway: the highest is 0.86 tested, the
model 0.80 or under on every one, and the Card's tennis floor is 85%
(`CARD_SPORT_MIN`, rule 10). The fix matters for the `tennis75` variant
(which reads tennis down to 75%) and for the funnel's honesty.

A replay leg is still taken at its first real price, which can precede the
order of play; a live build at that price would have refused it and taken
the leg at a later price. Small (tennis prices moved little in the price
timing read) and noted, not modelled.

## The Card's tennis legs on the pool

177 settled tennis pool legs from 30 Oct, by the model's number:

| model | legs | landed | model said | z |
|---|---|---|---|---|
| under 60% | 50 | 50.0% | 57.5% | -1.07 |
| 60-70% | 80 | 58.8% | 64.6% | -1.10 |
| 70-80% | 40 | 77.5% | 74.6% | +0.42 |
| 80-85% | 3 | 3 of 3 | 81.0% | |
| 85%+ | 4 | 4 of 4 | 86.0% | |

By the bookmakers' fair chance (71 priced): 60-70% landed 12 of 27 (44%,
quoted 65%), under 60% 6 of 17; 70%+ 22 of 27. The shortfall HQ ranks first
sits in matches both the model and the market price under 70%, which the
Card has not admitted since 29 Oct (75%) and 11 Nov (85%). At 85% the pool
holds four tennis legs in 15 days, all won: tennis is now a rare Card leg,
so the tripwire (50 legs at two standard errors under) will be slow to
reach. Nothing to change; the floor already does what the shortfall asks.
