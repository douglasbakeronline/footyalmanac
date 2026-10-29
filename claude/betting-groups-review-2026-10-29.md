# Betting groups review, 29 October 2026

Source: `groupings-record.json` at `3dd77b9` (4 to 29 Oct, 24 days with settled
groups), Daily List rebuilt per day as `daylist.py` pins it (latest archived
price before start), results from `record-graded.json`, `tennis-record.json`
and `sports.graded_games()`. Nothing refitted; the figures reproduce from the
record files alone. Douglas's three questions: how the groups have done, how
the Daily List's top picks compare over the same days and counts, and whether
the time windows play a part.

## 1. The groups

90 settled groups, 23 won (26%), 33% expected from the quoted leg chances.
71.0 units back on 90 staked (-21%), 75.2 at best price (-16%). Expected wins
29.3, actual 23: 1.4 standard deviations short, not proven, but every point of
the shortfall sits in the non-football legs (below).

| Kind | Groups | Won | Expected | Return |
|---|---|---|---|---|
| Steady (retired) | 25 | 4 (16%) | 39% | -57% |
| Balanced (retired) | 17 | 5 (29%) | 30% | +23% |
| Stretch (retired) | 15 | 1 (7%) | 24% | -53% |
| Banker (retired) | 2 | 1 | 38% | -9% |
| Wider Treble / Fourfold | 7 | 3 (43%) | 38% | -18% |
| Multiplier | 3 | 1 | 28% | -2% |
| Card 2x | 11 | 4 (36%) | 37% | -19% |
| Card 3x | 10 | 4 (40%) | 27% | +29% |

The Card (25 Oct on, locked groups only): 15 settled, 4 won (27%) against 31%
expected, -19%. Too few to judge; the 25 Oct review said mid-December at ~300
locked legs, and that still holds. Card 3x is ahead of quote on 10 groups,
which is noise.

### Did the 25 Oct rebuild improve wins?

Before 25 Oct: 63 groups, 11 won (17%), 19.4 expected (31%). Since: 27
groups, 12 won (44%), 8.8 expected (33%). So the wins doubled, but the quoted
chance barely moved: the rebuild lifted the record to its quote rather than
above it. Two things happened at once. The rule change took out the forced
1.60+ legs (the retired five-leg kinds went 0 for 32 across 12 to 18 Oct) and
dropped the model-above-market picks, which is the real and lasting part.
The rest is a good weekend: 25 to 27 Oct landed 12 of 21, 28 to 29 Oct 0 of 6.
The Card on its own, the only kind still built, is 4 of 15. Call the rebuild
an improvement from "well under quote" to "on quote", not an edge.

### Legs, 379 settled

| | Legs | Landed | Quoted | Gap |
|---|---|---|---|---|
| All | 379 | 72.3% | 76.8% | -4.5 |
| Football | 223 | 75.8% | 75.3% | +0.5 |
| Rugby | 10 | 90.0% | 86.1% | +3.9 |
| NBA | 8 | 75.0% | 72.6% | +2.4 |
| Tennis | 91 | 64.8% | 78.0% | -13.2 |
| College football | 27 | 70.4% | 85.4% | -15.1 |
| NFL | 20 | 60.0% | 73.0% | -13.0 |

Football legs land exactly as quoted. The groups' shortfall is tennis, college
football and NFL: 138 legs, 90 landed (65%) against 79% quoted, 19 wins short.
Had those legs landed as quoted the record would be near its expected 33%.
On the Card itself tennis legs are 19 of 32 (59%, quoted 69%), NFL 1 of 3,
football 16 of 19, NBA 6 of 8.

Closing line: 75 legs with a last price, mean move -0.3% (31 shortened, 27
drifted). The market did not move against the picks; they just lost.

## 2. The Daily List, same days, same number of picks

For each day, N = that day's settled legs, and the top N of the Daily List by
confidence (list first, then the reserve by confidence when the list was
shorter than N). The groups take priced legs down to 60%, so the list ran out
on most days: 185 of the 379 slots came from the reserve. Mean quoted chance
is the same on both sides (76.8% legs, 76.7% list), so this is a fair pairing.

| | Picks | Landed |
|---|---|---|
| Group legs | 379 | 274 (72.3%) |
| Daily List top N, by confidence | 379 | 291 (76.8%) |
| Daily List top N, by tested rate (the old order) | 379 | 278 (73.4%) |

Paired bootstrap by day, list minus legs: +4.5 points, 90% band -0.7 to +9.7,
p(list worse) 0.07. Same picks in both sets: 176 of 379, so the gap comes from
the other 203.

Group-shaped: walking the top N through each day's group sizes (a 3-leg
group takes the next three picks, and so on), the list would have landed
32 of 88 groups (36%) against the groups' 23 of 90 (26%). The old tested-rate
order gives 28 of 88.

The reasons are the ones already on file. The list order is confidence; the
groups weigh the market, which pulls in the sports that under-land, and the
Daily List excludes college football (since 19 Oct) and excluded tennis for
most of the period. 25 to 28 Oct, Card era: legs 58 of 80 (73%), list top N
71 of 80 (89%), list in group shapes 18 of 27 against 12 of 27.

Over the period the full list (not top N) landed 153 of 193 (79%) against
82% quoted: football 74 of 90 (82%), rugby 14 of 15, tennis 27 of 38 (71%),
college football 29 of 40 (73%).

## 3. Time zones

No. Windows by UK kick-off, every settled leg:

| Window | Legs | Landed | Quoted |
|---|---|---|---|
| Overnight 00-09 | 56 | 71.4% | 78.9% |
| Daytime 09-17 | 161 | 72.0% | 77.1% |
| Evening 17-24 | 162 | 72.8% | 75.8% |

z for overnight against the rest: -0.16. No band of the day separates either
(the worst, 03-06 UK, is 9 of 14; the best, 12-15 UK, 53 of 68 on 78% quoted).

What looks like a time-of-day effect is sport mix. Overnight is the Asian
tennis swing plus US college football; evening is NFL and college football:

| Window | Football | Tennis | Cfb / NFL |
|---|---|---|---|
| Overnight | 8 of 9 | 20 of 34 (59%, quoted 78%) | cfb 9 of 10 |
| Daytime | 81 of 108 (75%, on quote) | 34 of 51 (67%, quoted 79%) | |
| Evening | 80 of 106 (75.5%, on quote) | 5 of 6 | cfb 10 of 17, NFL 12 of 20 |

Football is on quote in all three windows (z +0.9 overnight v rest, 9 legs).
Tennis is under in both windows it plays in. The Card's Overnight window
(1 of 6 won, -48%) is 13 tennis legs landing 6; its one football and two NBA
legs all landed.

The Daily List shows the same picture: 82.9% overnight, 78.2% daytime, 78.5%
evening, all on quote, with tennis under in each window and college football
carrying the evening miss (13 of 22).

Lock timing: Overnight groups lock at 21:00 the evening before, so their
prices are 3 to 9 hours staler than the other windows' 07:00 lock. Mean
closing move on overnight card legs -0.4%, daytime -1.4%, evening -0.1%: no
sign the earlier lock costs anything.

## What changed (same day, Douglas: "make changes")

- `groupings.CARD_SPORTS_OFF = {"nfl", "cfb"}`: `card_fault` refuses them.
  College football was already out through `listOff`; NFL was not.
- `groupings.CARD_SPORT_MIN = {"tennis": 0.75}`: a tennis leg needs the model
  and its tested rate (`hit`) both at 75%+. The 60-75% band is where tennis
  has not been tested live in volume and where its Card legs lost.
- `CARD_RULE` 1 -> 2, so unlocked groups rebuild under the rule; locked
  groups stand. The Bets page states it; the avoid list marks a tennis pick
  under the floor as caution ("thin") and an NFL pick at 70%+ as avoid.
- Not changed: the Daily List (tennis stays on at 75%), windows, lock times,
  the 60% bookmaker floor for football, rugby and the NBA, grading, any
  model number. The retired Multiplier rule (`mult_fault`) is untouched.

Tests: `tests/test_groupings_card.py` `SportRule`. Review the Card again at
~300 locked legs (mid-December), as the 25 Oct review set out.
