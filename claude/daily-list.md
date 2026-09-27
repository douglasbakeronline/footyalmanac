# The Daily List, and what actually predicts a game — 27 September 2026

## What Douglas asked for

A daily list of the obvious wins across world football, nothing else. Higher
bar, wider pool, and it must stay the model's own independent read: **no
bookmaker input**, by his decision. If a game is not obvious it is not served.

## What predicts whether a pick lands (predictability.py)

Question tested: among games quoted at the same probability, does anything
separate the calls that land from the ones that don't? Binary target (did the
pick land), baseline is a two-parameter recalibration of the model's own
confidence, candidate adds one signal. Fit 2025/26 (5,648), judged on 2026/27
(789), paired bootstrap, tune.py gates.

| Signal | Δ log loss | p(worse) | |
|---|---|---|---|
| Fewest games played | 0.0000 | 0.70 | nothing |
| New to the division | −0.0001 | 0.31 | nothing |
| Rating drift off the prior | +0.0001 | 0.69 | nothing |
| Form against the pick | 0.0000 | 0.49 | nothing |
| Last season's head-to-head | −0.0004 | 0.03 | fails the gain gate |
| Draw probability | −0.0001 | 0.45 | nothing |
| Total expected goals | −0.0011 | 0.22 | marginal |
| Away pick | −0.0010 | 0.22 | marginal |
| League record | −0.0014 | 0.16 | marginal |
| All of the above | −0.0032 | 0.07 | the ceiling of self-derived signals |
| Bookmaker agreement (470 priced) | −0.0217 | 0.02 | real, ~7x everything else |

Conclusion: the model's own probability already contains everything it can
compute. Form and head-to-head, the things a person checks by hand, add
nothing measurable. What a person actually adds is team news and context,
which is what the market prices. Douglas ruled the market out to keep the
list independent, so it is not used. `predictability.py --market` still
reports it as evidence, and changes nothing.

## Threshold evidence (league walk-forward, pick landed)

| Model ≥ | 25/26 n | hit | 26/27 n | hit |
|---|---|---|---|---|
| 60% | 920 | 71.0% | 112 | 78.6% |
| 70% | 348 | 78.7% | 36 | 77.8% |
| 75% | 211 | 81.0% | 18 | 77.8% |
| 80% | 120 | 85.0% | 9 | 88.9% |
| 85% | 52 | 76.9% | 2 | 50.0% |

Hit rate stops climbing around 75-80% and falls back at 85%: the model's most
extreme numbers are its least calibrated. Internationals (separate fit,
tune_international.py, calibrated through engine.temper) on the 2026 holdout:
75%+ landed 81.6% of 49 (82.6% quoted), 80%+ 86.7% of 30. So 75% is the bar.

## What was built

- **build.py** `LIST_MIN = 0.75`, `LIST_BACKTEST`, `list_eligible(g)`. A row
  is on the list when: win pick (never a draw), ≥75%, no Celtic's Law flag, not
  unrated, and every club has a prior season on file (`team["last"]`). That
  last gate is not on the board: a club in a league with no history counts as
  rated once it has played, which is how El Salvador got through (below).
  National teams need only a rating. `g["list"]` is set per row, archived in
  `predictions/<date>.json`, and `data.json` carries `list: {min, backtest}`.
- **score.py** `record.list` (summary of archived list rows only) and
  `record.listDays`. Membership is read from the archive, never recomputed, so
  the list is graded on what it said before kick-off. Empty until the first
  list plays out.
- **index.html** "Daily List" is the first nav item and the default view.
  States the rule and the backtest, shows the live record once it exists,
  reuses `appendFixture` for the rows, says plainly when nothing qualifies,
  and lists recent list results. The rule lives only in build.py.

## Data-integrity fixes found on the way

1. **El Salvador was published as Slovenia.** `svn.1` pointed at ESPN
   `slv.1`, which is El Salvador's league. Salvadoran fixtures appeared as
   PrvaLiga from 10 September, rated from their own season. Never graded
   (not in `record.byLeague`). Slug removed.
2. **Evening kick-offs in the Americas were dropped.** ESPN's `dates=` is a
   US Eastern day; rows carry the UTC date; `fetch_espn` clipped to the
   window. Backfill lost about half of every Americas season (MLS 2025: 259
   of 541). `fetch_espn(clip=False)` for backfill; `score.live_results` now
   queries the day before as well, so late kick-offs get graded.
3. **ESPN slugs probed for real.** 52 competitions answered 400 (no such
   league) on every slug and were deleted, plus `svn.1` above. ESPN does not carry Poland, Croatia, Serbia, Ukraine, Hungary,
   Korea, the UAE, Germany's 3. Liga, Liga Portugal 2 or most smaller European
   leagues at all; no slug will fix those. Cup and international slugs were
   corrected from ESPN's own index
   (`sports.core.api.espn.com/v2/sports/soccer/leagues?limit=1000`).
   Date ranges (`dates=A-B`) are rejected by ESPN; probe day by day.
4. **The probe picked an international break.** `backfill.py --probe --on
   2026-09-20,2026-09-13` now takes explicit club dates.

## Backfill

Prior seasons walked for the 14 leagues with a working slug: calendar-year
`us.1 us.2 cl.1 uy.1 pe.1 ec.1` (2025) and split-year `mx.1 sa.1 ru.1 nl.2
dnk.1 au.1 in.1 sco.2` (2025-26). Libertadores, Sudamericana and the
CONCACAF Champions Cup rate clubs through their domestic leagues.

| Season | Matches | Release |
|---|---|---|
| us.1 2025 | 541 | release-2026-09-27 |
| us.2 2025 | 375 | release-2026-09-27 |
| cl.1 2025 | 240 | release-2026-09-27 |
| uy.1 2025 | 300 | release-2026-09-27 |
| pe.1 2025 | 332 | release-2026-09-27 |
| ec.1, mx.1, sa.1, ru.1, nl.2, dnk.1, au.1, in.1, sco.2 | pending | next release |

MLS and USL are not round robins: `"games"` on their LEAGUES entries (34,
30) lets `sources.completeness` judge a season with no older one on file.
Without it every MLS row was flagged "rated from a partial season".

## Local environment

This Mac has Python 3.7.3 only; Homebrew cannot install 3.12 on this macOS.
`nametest.py` was made 3.7-compatible (one walrus removed). `eurotest.py`
still needs 3.8+. CI runs 3.12.

## Open

- The list's backtest is league fixtures plus internationals. Cup ties are
  mostly excluded by Celtic's Law; continental ties between fitted leagues are
  not, and have no list-specific backtest yet.
- The 14 backfilled leagues have no walk-forward of their own (the harness
  needs two prior seasons). Their list picks rely on the global evidence.
