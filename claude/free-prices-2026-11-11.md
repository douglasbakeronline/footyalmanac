# Free price sources (11 Nov 2026)

Douglas, 11 Nov 2026: "Every single game needs odds attached. If I type that
game into William Hill I find the odds. So why can't you!?" then "Find as
many free sources as you can before we look at increasing costs" and "build
it all".

## Why the site cannot read William Hill directly

Hill publishes no price feed and its site blocks automated reading; reading
it anyway would breach its terms. Hill's prices reach the site through
API-Football (football, paid) and The Odds API (UK region, free 500 credits a
month). The free credits are the bottleneck: about 16 sport slates a day
against the 60 to 80 a day every game would need.

## The free sources found (11 Nov 2026)

| source | free terms | covers | Hill |
|---|---|---|---|
| Betfair Exchange, delayed key | free with an account, prices 1-180 s late | nearly every football league and tennis match, US sports | no (exchange) |
| Matchbook | free default tier with an account | football, tennis, US sports | no (exchange) |
| SportsGameOdds Amateur | 2,500 games a month, 10 a minute, 10-minute refresh | NFL, NBA, MLB, NHL, CFB, NCAAB, Champions League, MLS | listed, possibly the US brand |
| OddsPapi | 250 requests a month, one fixture each | 300+ books | yes; too small for every game |
| The Rundown | 750 requests a month | US sports | not stated |
| API-Sports, PinnWire, ESPN | already used | | |

Ruled out: Odds-API.io (new free keys paused), OddsRelay (14-day trial).
Most free plans say personal or development use; the site is public, so
Douglas reads each one's terms.

## What shipped (`free_prices.py`)

- `price_betfair`: interactive login with the delayed application key,
  `listMarketCatalogue` (MATCH_ODDS, the build's dates, one call a sport),
  `listMarketBook` (best back price) only for markets a wanted leg could
  match, 40 a call. 30-minute cache of prices.
- `price_matchbook`: login, the sports lookup, `/edge/rest/events` with
  prices, one call a sport. 30-minute cache.
- `price_sgo`: `/v2/events` by league, moneyline per bookmaker (American
  odds converted), an even daily share of `SGO_MONTH` (2,400) objects, a
  ledger in the cache. Its William Hill is kept apart in `sgoBooks` until
  `SGO_HILL_IS_UK` is set after a check against the UK site.
- Order in `groupings.price`: every bookmaker source first, then
  SportsGameOdds, Betfair, Matchbook; each fills only legs still unpriced and
  says where the price came from. An exchange price is the best back price
  (no bookmaker margin, a commission on winnings) and shows as **Exch** on
  the row.
- Sessions are never written to disk: `.afcache` is an Actions cache on a
  public repository.
- `deploy.yml` passes the six secrets to the groupings step; each source is
  silent until its secrets exist.

Tests: `tests/test_free_prices.py` (shaped replies, no network).

## Risks to check on the first build with keys

- Betfair and Matchbook refuse logins from some countries, the US included,
  and GitHub's runners are usually in the US. If the build report says
  `BETTING_RESTRICTED_LOCATION` or a login error, the exchanges need a UK
  machine to fetch from; the code is unchanged either way.
- SportsGameOdds league IDs (`NCAAB`, `NCAAF`) are from its docs; an empty
  reply for a league means the ID needs adjusting.

## First builds with keys (11 Nov 2026, evening)

- SportsGameOdds: 47 games matched ours by name and every one came with no
  per-book prices on the free plan (`noBooks`). Since #260 its consensus line
  (`bookOdds`) prices them, labelled "SportsGameOdds consensus": 39 of 128
  legs priced on the first build; legs priced 163 -> 189 of about 390.
- Betfair: the login answers GitHub's runners with Betfair's HTML "Forbidden"
  page, a location block (Betfair does not serve the US). Nothing in code can
  fix it from CI; it needs a runner in a served country or nothing. Left in
  place, silent apart from the log line.
- Matchbook: no key added.
- The build log prints a line per source (`  prices:`) and, when
  SportsGameOdds matches nothing, its miss detail (`  sgo miss:`).
