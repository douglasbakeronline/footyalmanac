# What keeps groups off the Card (10 Nov 2026)

Scheduled build session, issue #155. Since rule 6 (the opposition priced 9+,
6 Nov 2026) the full rule has built no Card 3x, and on 9 Nov no full-rule
group at all (the wider-rule fill stood in). The replay asks whether a
variant would have won more; this note asks the earlier question, which
condition costs the groups. A volume read only. Nothing changed.

## The tool

`tools/card_funnel.py` reads the pool archive (`groupings-archive/pool-*.json.gz`)
at each leg's first real price and, for every Card day:

- each priced leg's first failing condition, by sport, from the live
  `groupings.card_fault` (so the funnel and the Card cannot drift apart);
- the legs kept off by one condition alone (every other passed);
- whether a first Card 2x and Card 3x can be built (`best_card`, live), and
  the same with one condition relaxed at a time: the under-market band, the
  opposition's price, the tennis 75% floor, the price range (to the wider
  rule's 1.08-2.10), the bookmakers' 60% floor (to 55%), the core leagues.

It needs no results, so it reads days not yet played. `--recover` takes legs
archived as estimates before 10 Nov at their last price (approximate, as
`card_replay.py --recover`). The nightly Card review prints it over the last
two weeks from 6 Nov (`tools/card_review_post.py`, `funnel_section`; no
workflow change). Tests: `tests/test_card_funnel.py` (every `card_fault`
branch has a key, first real price, estimates counted, one condition relaxed
and the constants restored).

## The read, 6 to 12 Nov (pool, `--recover`)

651 legs at a real price over 7 days; 374 estimate-only legs left out.
The funnel reproduces the live Card: a first 2x on 6, 7 and 8 Nov, none on
9 Nov, no 3x on any day.

| sport | priced legs | clear | first condition failed |
|---|---|---|---|
| football | 384 | 0 | league 262, under-market 96, opposition 26 |
| NBA | 29 | 19 | fair floor 5, price 3, model above market 2 |
| tennis | 26 | 3 | 75% floor 22, price 1 |
| rugby | 5 | 1 | price 2, model above 2 |
| NFL, cfb, ncaab | 207 | 0 | off the Card |

Kept off by one condition alone: football opposition 11, core leagues 4,
under-market 3; tennis 75% floor 15; NBA fair floor 3, price 2.

| rule | days with a 2x (of 7) | days with a 3x |
|---|---|---|
| live | 3 | 0 |
| no under-market band | 3 | 0 |
| no opposition condition (rule 5) | 3 | 2 |
| no tennis floor | 4 | 3 |
| wider price range | 3 | 0 |
| bookmakers' floor 55% | 3 | 0 |
| wider leagues | 3 | 0 |

Two more things the tables show. No football leg cleared the full rule in
seven days: the rule 6 Card is an NBA and tennis Card with football as an
occasional third leg (the five-season note found one football-only group in
five seasons). And 9 Nov had five clear NBA legs but no group: `mult_combo`
allows two legs per competition, and every NBA leg is "NBA", so a group needs
a third leg from somewhere else.

## What it means for the return

The two conditions that would bring the 3x back are the two with evidence
behind them. The tennis floor: tennis Card legs are the one leak, 22 of 40
landed against 71% quoted (z -2.23), and the floor keeps out the tennis legs
under 75%, the ones it was set against on 29 Oct. The opposition at 9+: the one condition that holds in every season
(83.8% v 76.2% on 511 legs, 4-6 legs lose in all five). Relaxing either for
volume would add groups the evidence expects to lose. So no change: an empty
3x is the price of two sound conditions, and more groups at a negative edge
is less return, not more.

What would add volume without loosening a leg: more clear legs from a
competition other than the NBA, so a third leg can join two NBA picks
(rugby, and football as the weekend's core fixtures come round), and
college basketball once it has 50 graded games (`CARD_SPORTS_OFF`, Douglas's
call). `opp7` and `rule5` are pre-registered in `tools/card_replay.py` and the
30 Nov review gates them on the pool from 10 Nov; this funnel tells that
review how many groups each would add.

## Addendum, same day: the two-per-competition cap pre-registered

The cap had no test behind it: a spread choice carried from the Odds tab's
`ok_combo` into `mult_combo`. It is now a named constant,
`groupings.COMP_MAX` (2, unchanged), and `comp3` (three legs from one
competition) is pre-registered in `tools/card_replay.py` for the 30 Nov
review. The funnel shows it as a relief row: 6 to 12 Nov, a 2x on 4 days of 7
(live 3) and a 3x on 1 (live 0); 31 Oct to 12 Nov, a 2x on 7 days of 13
(live 6) and a 3x on 3 (live 2). On the pool replay with results
(`--since 2026-10-30 --recover`, approximate before 10 Nov): 12 groups, 5 won
v 4.6 expected, -1% at the average price, against live 10 groups, 4 won,
-7%; paired +0.13 units a day, p(worse) 0.43. Far too few to act on; the
gate is p(worse) 0.30 or under on 100+ legs and the football-data seasons.
The NBA's legs within one night are separate games, so the cap guards
against little correlation there; in one football league on one afternoon
it may guard against more (a shared weather or fixture-congestion effect),
which the replay cannot see.
