# Paid data and new sports: the plan, 30 September 2026

Douglas bought **API-Football Pro** ($19/month, 7,500 calls/day, active to
30 Oct 2026; confirmed by `.github/workflows/apiprobe.yml`). Keys live in two
places, never in chat or the repo:

- GitHub Actions secret `API_FOOTBALL_KEY` (the daily build).
- The cloud environment variable `API_FOOTBALL_KEY` (sessions started after
  30 Sep 2026). The environment also allows `v3.football.api-sports.io` and
  the ESPN hosts, so cloud builds are no longer partial.

Header: `x-apisports-key: $API_FOOTBALL_KEY`. Never print the key, and never
the `/status` account block (it carries Douglas's email; logs are public).

## Why

Douglas wants every division worldwide scanned so top-v-bottom games surface,
proper U21 modelling, and MMA and boxing trials. Free sources stop at English
step 2 and senior internationals only. He will pay for data that earns picks;
cost-effective first, trial before committing.

## Order (each step its own release, rules unchanged)

1. **Coverage check.** `/leagues` (with `current=true` and per country):
   which divisions, U21/youth competitions and past seasons Pro includes;
   English steps 3-4 (Southern, Isthmian, NPL) and U21 qualifying in
   particular. Budget the daily calls. Report to Douglas before building:
   keep Pro or cancel.
2. **Lower leagues onto the boards.** New source in `sources.py` in the shape
   of `sources.FDX`: one source per league, so one spelling; `nametest.py`
   extended; a prior season per league. Board only, not the list.
3. **Replay test** (walk-forward, calibrated, paired, as `tune.py`) per new
   league group. Only groups whose calls land at the 80% bar reach the Daily
   List (`sports.list_threshold`). Expect lower divisions to be less
   predictable than they look.
4. **U21 ratings** from U21 results (the `tune_international.py` method, fit
   on the holdout, ship refitted to date). Today U21 is priced off senior
   ratings (`ageProxy`) and flagged off the list.
5. **UFC via ESPN** (free): `site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard`.
   Fighter Elo like tennis, replay test. API-Sports MMA ($10/month) only if
   UFC passes and wider promotions are wanted.
6. **Boxing**: free tiers (boxing-data.com via RapidAPI, bigballsdata.com,
   history only from Jan 2025). First check history depth; under ~2 years,
   tell Douglas it will not work yet.
7. **Weekly automation**: add `tune_international.py --fit` (and U21) to
   `tune.yml`.

Rejected up front, with reasons given to Douglas: the $99 all-sports bundle
now (buy per sport after its free-tier check), horse racing and golf (many
runners, no pick reaches the 80% bar; golf would relay DataGolf's model),
F1 (same), ice hockey (expected to fail like baseball; test only if asked).

## Standing guardrails for this work

No bookmaker input into any model. Nothing fitted on `record.json`. A new
league or sport is on its board at once but off the Daily List until its
replay passes. A name mismatch fails loudly.
