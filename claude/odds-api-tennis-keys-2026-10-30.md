# Tennis tournaments with no Odds API key (30 Oct 2026)

Task: Almaty, the European Open and the Japan Open matched no sport key on 19 Oct.

**State of the code.** The logging asked for already exists (release 2026-10-20, #55): `groupings.py --probe` prints `oddsApi.tennisKeys` (active `tennis_*` keys with titles), `rugbyKeys`, and `noKey` (tour + tournament of every unpriced leg that matched nothing). `_odds_keys` matches on tour prefix plus a shared word between the tournament and the key/title. Tests: `tests/test_groupings.py`.

**What could not be done.** The sandbox has no `ODDS_API_KEY` (the /sports list answers 401 without one), and no committed file holds a previous `oddsApi` report, so the live key list was not seen. The cause is therefore still unconfirmed.

**Likeliest cause (unproven).** The Odds API carries mainly Slams and Masters for tennis; ATP 250/500 events such as Almaty and the Japan Open probably have no key at all. If so, no matching change can price them and a looser matcher would only risk a wrong key (it would still need both player names and kick-off to match, so it would price nothing, not a wrong price).

**Why no fix.** A matching change is untestable without the list, and prices never feed a model, so the log-loss gates (Rule 3) do not apply: nothing here is a model number. Shipping a guess would break "don't build what won't deliver" (Rule 10).

**Next step.** Read `noKey` and `tennisKeys` from the next CI build's report (or `python3 groupings.py --probe` with the secret). If an event is listed in `tennisKeys` but its leg is in `noKey`, fix `_odds_keys` and add that spelling as a test. If it is absent from `tennisKeys`, close the item: the API does not carry it.
