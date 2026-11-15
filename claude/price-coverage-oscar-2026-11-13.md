# Pricing more Odds tab legs: no change shipped (13 Nov 2026, Oscar)

Task: price more legs (free source or a better API-Football match).

## What was checked
- `groupings.price_football` matches a leg to an API-Football fixture on the leg's
  date, a 90-minute kick-off window and `same()` on both names; bulk day prices
  (`odds.af_prices`) are read first, one call per fixture as the fallback.
- Pool archive 9-13 Nov (`groupings-archive/pool-*.json.gz`): football legs 19, 6, 15,
  16, 30; **zero** unpriced. The archive keeps priced legs, so the unpriced
  candidates cannot be counted from it, and this sandbox has no
  `API_FOOTBALL_KEY` (no before/after on a live build was possible).
- `claude/card-price-gaps-2026-11-12.md` already measured the lever: since 10 Nov a
  missing price cost the Card four legs over two days (football 3, tennis 1), and
  no day was one leg short of a group.

## Decision
No change. A neighbouring-UTC-day fixture lookup is the one plausible match gain
(late kick-offs crossing midnight), but it would add API-Football day and odds
calls and cannot be measured here; the measured gap is four legs. Not building
what won't deliver (Rule 10). Prices still never feed a model.

## To reopen
When `card_funnel.price_gaps` shows started-day losses above about 10 legs a
week, test the ±1 day lookup on a build with the key.
