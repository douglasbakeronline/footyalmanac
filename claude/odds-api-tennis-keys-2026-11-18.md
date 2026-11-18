# Tennis tournaments with no Odds API key: third look (18 Nov 2026)

Set a third time by the HQ planner (Almaty, European Open, Japan Open, 19 Oct).

- Logging is already shipped (#55, 20 Oct): `groupings.py --probe` prints `oddsApi.tennisKeys`, `rugbyKeys`, `noKey` (`price_odds_api`). `tests/test_groupings.py` pins `noKey` for an unmatched tournament.
- No `ODDS_API_KEY` in this sandbox; no committed file holds an `oddsApi` report (`groupings.json` is not committed), so the live key list is still unseen.
- No matcher change: without the list a looser `_odds_keys` cannot be tested, and a wrong key only costs credits. Prices never feed a model, so the Rule 3 log-loss gates do not apply; guessing breaks Rule 10.
- Still open: the first CI build log with the key reads `oddsApi.noKey` against `tennisKeys`. Listed but unmatched: fix `_odds_keys` with a test. Absent: the API does not carry the event; close the item.
- Planner: do not re-issue until a build report holding the key list is committed or attached.
