# Horse racing, on trial (19 Nov 2026)

Douglas, 19 Nov 2026: testers said the site is good but not accurate enough,
and asked for horse racing. On the mock-ups ("Horse Racing tab mockups"
canvas, five boards in the live site's design): "it's important to actually
... surface like what we believe is going to be accurate for that day, or the
most accurate", "I'm happy to have it marked as trial somewhere, but I want it
published", no timestamp on tips, UK and Ireland first ("I'll lean to your
suggestion"; the US and Dubai considered).

## What shipped

- `racing.py`, standard library only. The Racing API (`api.theracingapi.com/v1`,
  HTTP basic auth, `RACING_API_USERNAME` / `RACING_API_PASSWORD`): today's and
  tomorrow's racecards (`racecards/standard`, `day=today|tomorrow`), results
  for archived days not yet graded (`results`, paged by `skip`). Region filters
  `CARD_REGION_PARAM` / `RESULT_REGION_PARAM`; a 422 drops the filter and keeps
  GB and IRE locally. Field names are read with fallbacks (`_first`);
  `--probe` prints the live feed's keys on the first build with keys.
- The chance (Benter 1994, Bolton and Chapman 1986): a racecard score of
  within-race z-scores (`FACTORS`: official rating 0.55, form of the last three
  runs 0.45, trainer's 14-day strike rate 0.15, time since the last run 0.10),
  softmax per race; then `fund^ALPHA x market^BETA` (0.30, 0.85), renormalised,
  where the market is the average UK price with the margin removed. Starter
  values: refit by hand once `FIT_MIN` (500) races are graded, on the logged
  runners, checked on later days (never on the record, Rule 1).
- Place chance by Harville (exact to three places, four approximated). Each-way
  terms by UK rules from the runners left (`ew_terms`), so a non-runner can
  change them.
- A tip (`tip_for`): the top-rated horse at 22%+, best UK price x chance at
  least 1.08, a field of 3 to 16, two runs of form. Each-way when the chance is
  under 33%, the price 4.0+ and the place chance 45%+. "Take at" is the lowest
  price still 4% over the chance. The day keeps the six most likely
  (`MAX_TIPS`); every other race carries its reason (`skip_reason`).
- Each race frozen at its off in `predictions-racing/<date>.json`; graded into
  `racing-record.json` (every runner for calibration, every tip settled at the
  price published, one point a tip, each-way half and half; a horse that did
  not run is void; beat-the-starting-price against `bsp` else `sp_dec`).
  Results are kept in the record so a race is fetched once.
- The tab (`renderRacing` in `index.html`): Tips, Every race, Racecards,
  Record, drawn with the site's row, bar, record, tracker dots, honest charts
  and ladder. The bar: yellow win, grey place without winning, red out.
- `deploy.yml`: the "Horse racing" step after the slip, allowed to fail;
  archive and record committed with the others; `racing.js` published.

## Open

- The first build with the secrets: run `--probe`, check every field the
  reader expects (`ofr`, `form`, `last_run`, `trainer_14_days`, `odds`
  with `decimal`, results `position`, `sp_dec`, `bsp`) and fix the names.
- Whether The Racing API's plan includes bookmaker odds on `standard`
  racecards. Without odds there are no tips (the model alone is never tipped);
  Betfair exchange prices are the fallback (`free_prices.py` has the client,
  location-blocked from GitHub's runners on 11 Nov 2026).
- The refit of `ALPHA`, `BETA` and `FACTORS` at 500 graded races: conditional
  logit on the logged runners, fit on the earlier days, confirm on the later.
- The Racing API's terms on showing its data on a public site.
- Course and distance winners, draw, going preference: not on the standard
  card as far as known; add when the probe shows them.
