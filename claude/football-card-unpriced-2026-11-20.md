# Football price gaps the Card can feel (20 Nov 2026)

Build session, 20 Nov 2026 00:30 UTC.

## What looked wrong

The 19 Nov 23:24 UTC build logged `football unpriced: noOdds 257 (Premier League 12, ...)`, and the 00:06 build `Premier League 14`. Under rule 14 (core leagues only) an unpriced English Premier League leg is a leg off the Card, so it read like a coverage hole in the Card's best league.

## What it was

`missComps` keyed on the competition's name alone, and "Premier League" names a dozen leagues. The 21 Nov pool's unpriced "Premier League" legs were Russia (CSKA v Akhmat, Rubin v Zenit, Akron v Fakel), Kuwait, Uganda, Hong Kong and five English games: Chelsea v Leeds, Aston Villa v Sunderland, Bournemouth v Forest, Brentford v Everton, Liverpool v Manchester United. API-Football answered the per-fixture calls (109 calls that build, 3,455 left) with no match-winner prices for those five, while Manchester City v Fulham and Newcastle v Arsenal were priced in the same pass.

None of the five could reach the Card: each sits under the model's 60% (`CARD_FAIR_MIN`). Across the pool files for 13 to 23 Nov, core-league football legs at 60%+: 41 priced, 2 unpriced (both France's women's D1). Price coverage is not costing the Card groups under rule 14, as `claude/card-price-gaps-2026-11-12.md` and `claude/card-price-gaps-rule13-2026-11-18.md` found under earlier rules.

## What changed

- `groupings.comp_label`: the price reports name a competition with its country ("Premier League (England)", "Premier League (Russia)").
- `groupings.card_unpriced`: after every source has run, the Card-reachable football legs still unpriced are counted and named, nearest day and strongest first, in `groupings.json` (`football.cardUnpriced`, `football.cardUnpricedLegs`, up to `NOFIXTURE_KEEP`) and the build log ("football Card unpriced: N: ..."). That one line answers whether a price gap cost the Card anything this build; the rest of "football unpriced" is legs it would never take.
- `card_reach` reads the live Card's league test (`core_league` under `CARD_CORE_ONLY`, else `card_league`), as `card_fault` does, so under rule 14 a wider-league 60% pick no longer takes a capped per-fixture call ahead of a list pick.

## Not built

A football fallback through The Odds API's soccer keys (one credit a league slate) for Card-reachable legs API-Football leaves unpriced. With 2 such legs in eleven days it would spend shared credits (15 a day, tennis and the list pass first) for almost nothing. Build it if "football Card unpriced" shows core-league legs on two or more days in a week.

No Card constant changed; `CARD_RULE` stays 14.
