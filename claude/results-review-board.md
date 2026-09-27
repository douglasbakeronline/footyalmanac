# Results review board — 9 September 2026

## What was added

**index.html** — a second top-level board, "How it went", beside "What's coming".
- Day picker across the last 14 graded days, each showing correct/graded.
- Scoreline strip per day: top picks correct vs always-back-home baseline, "drawn out"
  (picked a winner, got a draw), exact scorelines, log loss.
- Full graded fixture list for the day: probability bar, tier label, predicted score,
  final score, tick or cross, Celtic's Law rail.
- Permanent explainer: the confidence ladder with backtest vs live hit rates, the band
  calibration table, and the settled-vs-flagged gap.
- Controls, honesty note and readbar hide on this board (`.controls[hidden]{display:none}`
  is needed because the class sets `display:flex`).

**score.py**
- `live_results()` — ESPN fallback for fixtures played in the last 6 days that openfootball
  has not backfilled. Runs only on what openfootball left ungraded. Both team names must
  match the same fixture or nothing is recorded.
- `tier_of()` / `tier_table()` — the Strong/Firm/Lean/No read ladder duplicated from
  index.html, with the Celtic's Law one-tier demotion. **Change one, change the other.**
- `summarise()` now also emits `drawnOut`, `picks` and `actuals`.
- record.json gains `tiers` (overall) and `days` (last 14 days, every graded fixture).

## Live calibration at the time of writing (232 graded)

| Tier | Threshold | Backtest 25/26 | Live n | Live hit |
|---|---|---|---|---|
| Strong | ≥70% | 79% | 8 | 100% |
| Firm | ≥62% | 67% | 12 | 83% |
| Lean | ≥55% | 63% | 23 | 87% |
| No read | <55% | 46% | 189 | 41% |

Overall 115/232 = 49.6% against a 41.8% home baseline. The model picked a draw **once**
in 232 fixtures; 54 finished level. 53 of the No-read misses were draws — the single
largest category of miss.

## Open items

- The tier ladder is defined twice (index.html `TIERS`, score.py `TIERS`). Worth moving
  into data.js if it changes again.
- TEMPERATURE (1.15) was fitted at ~20 leagues, now 74. Live bands show under-selling
  above 50% and over-selling below it, so a re-fit or a proper calibration map is the
  next highest-value change after fitting the 74 strength coefficients.
- A "Lean or better only" filter on the fixtures board would make the actionable subset
  one tap away; not built.

Model reference doc (every variable, with live figures):
https://claude.ai/code/artifact/dcd9cb9e-0a95-4c6a-bcaa-531ed9bff60f
