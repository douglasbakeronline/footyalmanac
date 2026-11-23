# Card-reachable football legs unpriced near the start (23 Nov 2026)

## The question

`claude/football-card-unpriced-2026-11-20.md` left one trigger for building a second football price source (The Odds API's soccer keys): "Build it if 'football Card unpriced' shows core-league legs on two or more days in a week." Read literally, that fired this week.

## What the week's builds showed

One scheduled build a day, 19 to 23 Nov, the "football Card unpriced:" line:

| build (UTC) | legs named | the legs |
|---|---|---|
| 19 Nov | 1 | OL Lyonnes v Strasbourg (D1 Arkema, 22 Nov) |
| 20 Nov | 2 | OL Lyonnes; Vancouver Whitecaps v Real Salt Lake (MLS, 23 Nov) |
| 21 Nov | 8 | OL Lyonnes; six National League / North / South games of 24 Nov; Orlando Pirates v Golden Arrows (24 Nov) |
| 22 Nov | 5 | Salisbury v AFC Totton, South Shields v Worksop, Torquay v Chesham, Orlando Pirates (24 Nov); Sportivo Trinidense v Recoleta (25 Nov) |
| 23 Nov 07:24 | 1 | Orlando Pirates v Golden Arrows (24 Nov, about 36h out) |

Core-league legs on every day, so the trigger "fired". But the pool archive shows each one priced by API-Football before its start: OL Lyonnes at 1.02 on 21 Nov (a day before), Vancouver at 1.49 on 21 Nov (two days before), Salisbury at 1.44 on 22 Nov at 23:54 (two days before). They were named because they sat two and three days out, before API-Football's books had opened the market, not because no source carries them. Rebuilt from the pool, none of them was a leg the Card lost to a missing price; the funnel's "legs kept off by a missing price" agrees (2 started-day legs from 10 Nov, none on a day the Card left empty).

## The change

`groupings.card_unpriced_near(L, now)` counts the Card-reachable football legs still unpriced within `CARD_UNPRICED_NEAR_H` (24) hours of a start that has not passed. The build writes it to `groupings.json` `football.cardUnpricedNear`, and the log line reads "football Card unpriced: 5 (0 within 24h of the start): ... (69%, 60h out)". Each named leg carries `hours` to its start.

## The trigger, restated

Build the football fallback when the near count is above zero on two or more days in a week, on builds from the morning of the match day. The full count stays in the log for reference; it is not the trigger.

No Card constant changed; `CARD_RULE` stays 14. No price source or credit spend changed.
