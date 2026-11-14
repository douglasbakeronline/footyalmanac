# Why football legs go unpriced (14 Nov 2026)

`groupings.price_football` now counts each football leg it could not price
by reason and competition (#305), printed in the build log as "football
unpriced:" and kept in `groupings.json` (`football.miss`, `missComps`).

Reasons: `noFixture` (API-Football lists no fixture under those names that
day), `kickoff` (names found, kick-offs 90+ minutes apart), `noOdds` (the
fixture is listed, no 1X2 price for the side), `capped` (a mid-priced leg
over `FB_CALLS_MULT`), `error`.

## First read, deploy run 43638966317 (14 Nov, about 21:00 UTC)

- 222 football legs, 118 priced by API-Football.
- noOdds 101: Africa Cup of Nations qualifying 7, CONCACAF Nations League 6,
  international friendlies 6, then fifth-tier regional leagues (NB III,
  Tercera RFEF, Oberliga, Regionalliga).
- noFixture 3 (friendlies 2, Women's Super League 1). Kickoff 0. Capped 0.

## What it means

The gap is games no bookmaker in API-Football's feed prices, not names the
matcher misses, so `LIVE_NAMES` has nothing to gain. Internationals and cups
never reach the Card anyway (`card_league`). The fifth-tier legs the funnel
counts as "unpriced, would pass" (36 for 14-17 Nov) are not offered by UK
books either, which matches `claude/card-price-gaps-2026-11-12.md`: price
coverage is not the lever for Card volume.

If a later read shows `noFixture` clustering in one league, that is a
spelling to fix (rule 6), and the line names the league.
