# Pricing more Odds tab legs: no change shipped (28 Nov 2026, Oscar)

Task: price more legs (free source or a better API-Football match). Second read after `price-coverage-oscar-2026-11-13.md`.

## Measured
Football rows in the pool archive, files 26 to 29 Nov (`groupings-archive/pool-*.json.gz`, 518 rows):
- 142 priced when first written, 184 first written as estimates and priced later, **192 never priced**.
- The 192 are almost all leagues no UK book lists: Zambia, Lesotho, Tajikistan, Moldova, Burundi, Tunisia, Senegal, Iraq, Myanmar, Tanzania, Spain's Tercera RFEF groups, Germany's Oberligen, Italy's Serie D. 60 of them carry a model chance of 60%+ but none is a league the Card admits (`CARD_CORE_ONLY`).
- No `noFixture` cluster in a core league showed up in the archive; spellings already go through `AF_SPELLINGS`, `odds.ALIASES` and `sources._norm`.

## Decision
No change (this is the evidence failing the case, not a gate). The gap is `noOdds`: no bookmaker prices the game, so a better match or a second source cannot fill it, and a free source with such coverage does not exist (`claude/free-prices-2026-11-11.md`). The sandbox has no `API_FOOTBALL_KEY`, so a live before/after was not possible. Prices still never feed a model.

## To reopen
When the nightly review's `football Card unpriced` line names core-league legs with `noFixture`, add the spelling to `AF_SPELLINGS` with a test.
