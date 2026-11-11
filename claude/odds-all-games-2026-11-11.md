# Odds for every game (11 Nov 2026)

Douglas, 11 Nov 2026, 09:12, on a tennis row with no price: "We need to get a
grip on odds for all games."

## Where it stood (the 08:51 build, read from its log and the pool)

- 152 of 408 legs carried a bookmaker price; the rest were the model's
  estimate less a typical margin.
- Today's pool: tennis 0 of 17 priced (the WTA Finals included), NBA 0 of 5,
  college basketball 2 of 71, football 0 of 14 (midweek, mostly mid-priced
  legs), college football 3 of 3.
- Why: tennis was asked of The Odds API only at the Card's 75% bar or on the
  Daily List; US games only through ESPN's DraftKings line (which skips big
  mismatches) and, for the UK books, only Daily List picks; football legs the
  bulk day prices missed got a call of their own only if they could reach a
  group, though API-Football had about 3,300 calls left for the day.
- The page showed a price only on the Card, the Edge picks and, as a William
  Hill chip, the Daily List. Tennis and sport rows showed nothing.

## What shipped

- **Tennis and US sports, every game** (`groupings.price_odds_api`): every
  unpriced tennis match and every US game nothing else priced is now asked
  for. A sport key's slate costs one credit however many of its games are
  wanted, so this costs no more per key than before; keys with Daily List
  games go first.
- **Credits follow the account** (`odds_api_caps`): on the free plan (500 a
  month) the caps stay 15 a day and 480 a month. When the API reports more
  credits left than the free plan holds, the day's allowance becomes an even
  share of what is left over the days left in the month, so a paid plan
  needs no code change. The report carries `dayCap`.
- **Football, every leg** (`price_football`, `FB_CALLS_MULT` 150 a build):
  a mid-priced leg the bulk day prices missed now gets its own fixture call.
- **Every row** (`groupings.board_prices`, `prices` in `groupings-data.js`;
  `priceChip` in `index.html`): a priced game shows William Hill's price, or
  the bookmakers' average marked Avg with the best book in the tooltip, on
  every tab, the tennis and sport tabs included. The Daily List's Hill / Not
  at Hill / No UK marks are unchanged. Estimates are never shown as prices.

Display only. No model sees a price; the Card's rules are unchanged (more of
its legs now carry real prices, which is what its rules already ask for).

## The limit

The free Odds API plan is 500 credits a month. Pricing every tennis
tournament and every US sport on every build needs more than that: about
six to ten keys, re-read every four hours. On the free plan the most-needed
keys win and the rest wait for the next day's allowance. A paid plan lifts it
with no code change.
