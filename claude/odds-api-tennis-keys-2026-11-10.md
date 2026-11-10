# Tennis tournaments with no Odds API key: second look (10 Nov 2026)

Same task as `odds-api-tennis-keys-2026-10-30.md`, set again by the HQ planner.

- The logging is already in place: `groupings.py --probe` reports `oddsApi.tennisKeys`, `rugbyKeys` and `noKey` (`groupings.py` near line 727). Nothing to add.
- Still no `ODDS_API_KEY` in this sandbox (the /sports list answers 401) and no committed file holds an `oddsApi` report, so the live key list was not seen. No tournament can be shown to be in the list and unmatched.
- No code change: a looser `_odds_keys` matcher could not be tested without the list, and prices never feed a model, so the Rule 3 log-loss gates do not apply. Guessing would break Rule 10.
- Decision rule stands: read `noKey` against `tennisKeys` in the next CI build report. Listed but unmatched: fix `_odds_keys` with a test. Absent from the list: the API does not carry the event (likely for ATP/WTA 250 and 500 weeks); close the item.
- Planner note: this item should not be re-issued until a build report with the key list exists.
