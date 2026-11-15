# Scale reviewed: what lands, what does not, and rule 3 (15 Nov 2026)

Follows `claude/scale-2026-11-15.md` and `claude/scale-tiers-2026-11-15.md`.

Douglas: "we need to find a winning pattern in this scale feature. Review and
optimise."

## The short answer

There is a pattern in what **lands**. There is no evidence yet that any of it
**pays**, because four of the five Scale bets have no price on file and the
one that had (football to win with both teams scoring) is the worst-priced
market on the feed. Rule 3 moves the tab onto the pattern that lands and
drops the part that cannot win.

## What the record says (every graded pick at 55%+)

**1. Football: winning with both teams scoring does not get likelier as the
winner gets stronger. Winning with over 2.5 goals does.** 2,645 picks:

| Winner confidence | Picks | Won | Win and both score | Win and over 2.5 | Win to nil |
|---|---|---|---|---|---|
| 55-62% | 1,318 | 59% | 28% | 41% | 31% |
| 62-70% | 755 | 67% | 30% | 47% | 37% |
| 70-75% | 251 | 73% | 37% | 51% | 35% |
| 75-80% | 159 | 81% | 38% | 63% | 43% |
| 80-85% | 92 | 78% | 30% | 59% | 48% |
| 85%+ | 70 | 93% | 36% | 77% | 57% |

Strong favourites win by scoring, and more often to nil than with both
scoring. Win and both score is a one-in-three bet whoever the pick is. The
model's own win-and-both-score number did not sort picks in the leagues
William Hill prices (27% to 36% landed across its bands, no slope).

**2. William Hill keeps about 16% a leg on win and both score.** On 69
priced fixtures its price times the bookmakers' own fair chance averaged
0.843, against 0.942 for win to nil, 0.927 for both teams to score and draw
no bet, 0.936 for double chance. Three legs at 0.843 return 60% of fair
before the model has been right or wrong, and the model has no edge to spend
(its number averaged 19.1% against the bookmakers' 21.3%). A win-and-both-score
accumulator at William Hill cannot be expected to win.

**3. In every sport the Scale bet lands for the strongest winners and is a
coin toss below them.**

| | 55-65% | 65-75% | 75-85% | 85%+ |
|---|---|---|---|---|
| Tennis, straight sets (1,052) | 36-45% | 45-51% | 56-67% | 73-83% |
| NBA by 10+ (157) | 31% | 47% | 61% | few |
| NFL by 7+ (69) | 38% | 35% | 65% | few |
| Rugby by 8+ (69) | 38% | 69% | 64% | 70% |

**4. The tier says it more simply.** Across the five sports, whole record:

| Tier | Picks | Won | Scale bet landed |
|---|---|---|---|
| Daily List picks | 344 | 84% | 63% |
| Reserve | 1,107 | 68% | 48% |
| Everything else at 55%+ | 2,765 | 64% | 44% |

Three legs at 63% land together about one time in four. Three at 48%, about
one in nine. Five: one in ten against one in forty. A reserve leg inside an
accumulator is the leg that loses it.

**5. Not on the tab, but the strongest landing rate in the data:** college
basketball Daily List picks by 10 or more, 85% of 202 (by 15+, 74%). Left
off because UK books rarely price the games. Worth a price check before
anything else is added.

## What changed (`scale.py` `RULE` 3)

- **Football's bet is to win with over 2.5 goals** (`FOOTBALL_MARKET`
  `wo25`; `FOOTBALL` holds `wbtts` and `wtn` too, so a pick archived under an
  earlier rule grades by its own bet and the bet can be switched back in one
  line). The chance is the model's own number for the fixture
  (`markets.py`): it knows the expected goals, where a tally by confidence
  alone put a 77% away favourite in a low-scoring qualifier at 61% when the
  model said 46%. On 2,645 picks the model's number and the confidence tally
  predict the outcome equally well (AUC 0.59 each) and the model's number is
  on quote from 40% up. The price is William Hill's when it prices the bet,
  else the best UK price on the feed, named: today William Hill's is on none
  of 115 priced fixtures, so the price shown is another book's. A football
  fixture still needs William Hill's win-and-both-score price to be listed,
  the sign that it offers the game's result-and-goals bets.
- **Win and both score stays visible**: under each football bet, the model's
  number for it and William Hill's price; in the week's table, whether both
  scored.
- **Groups take Daily List picks only** (`GROUP_TIERS`), most likely to land
  first: a double, threefold, fourfold and fivefold as far as those picks go.
  The reserve never fills one. A day with fewer than two Daily List picks
  still to start has no group, and says so.
- **The football threefold is gone.** It was three legs of the bet in
  finding 2: 0 of 5 in the replay.
- The replay of the days before the tab reruns under rule 3 by itself (a
  replay file is rebuilt when `RULE` moves).

## The groups, replayed

`replay_day` over 5 Oct to 14 Nov (41 days), chosen from what was published
before each start, tallied chances from results dated before each day:

| | Rule 3 (Daily List picks only) | Rule 2 (tier order, reserve filling) |
|---|---|---|
| Double | 13 of 31 (42%) | not built |
| Threefold | 7 of 24 (29%) | 13 of 41 (32%) |
| Fourfold | 6 of 21 (29%) | 11 of 41 (27%) |
| Fivefold | 5 of 18 (28%) | 5 of 41 (12%) |

Over those days the Daily List picks on the tab landed their Scale bet 108
of 167 times (65%), everything else 320 of 663 (48%).

Read it straight: forty-one days cannot separate two sensible rules at the
threefold, and rule 3 builds on fewer days. What it does is stop filling
groups with reserve legs, which is where the fivefold's losses were (the
same five wins from 18 bets, not 41). The case for rule 3 rests on findings
1 to 4, which are thousands of picks, not on this table.

On the 14 days the glance shows (1 to 14 Nov): doubles 7 of 14, threefolds 3
of 12, fourfolds 2 of 10, fivefolds 1 of 7.

## What would make it a winning pattern

Prices. A Daily List threefold landing three times in ten needs to pay 3.4.
Legs that land 63% are worth about 1.59 each at a fair price; with a
bookmaker's 6-8% a leg a threefold of them pays about 3.2. That is the same
arithmetic as any accumulator: it wins only if the model's strong picks beat
the bookmaker's line, and nothing on file can say whether they do.

1. **The price feed for the handicap and set-betting lines** (the NBA -9.5,
   the NFL -6.5, rugby -7.5, tennis 2-0) and for college basketball. A probe
   on `odds-probe-run`, names and counts only, then prices into the archive
   so every leg and group is graded at a real price.
2. **Football's win and over 2.5 is already tracked with prices** by
   `markets.py` under its pre-registered gate (150 priced picks, landed above
   the bookmakers, best-price return positive, p(loss) <= 0.10). That gate is
   the test of whether the football leg pays.
3. **A gate for Scale groups**, to pre-register once prices exist: 50 priced
   groups, return positive at the price shown, day-resampled p(loss) <= 0.10.
   Until then the tab says "On trial".

## Tested and rejected here, do not reopen without new evidence

- Legs chosen by a 60% chance threshold whatever the tier: on the shipped
  code path threefolds 6 of 19, no better than the tier, and the tallies
  behind the threshold were thin in October.
- The confidence tally for football's chance: equal to the model's number on
  the record, wrong on individual fixtures (above).
- Tennis by tour: WTA picks at 85%+ landed straight sets 52 of 62 against 7
  of 14 for the ATP; the ATP sample is too small to split the tally on.

## Not changed

Any model, the Daily List, the reserve's rule, the tiers and their order on
the page, the ten-a-day top-up, the other four sports' bets, the Card, the
slip.

Roll back: `git revert` the merge; or `FOOTBALL_MARKET = "wbtts"` and
`GROUP_TIERS = TIERS` with a `RULE` bump for either half alone.
