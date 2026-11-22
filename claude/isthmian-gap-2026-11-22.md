# Isthmian League Premier (en.7i) v its quotes, second read, 22 Nov 2026

HQ planner: 59 of 101 landed against 68.5 expected, z -2.0. Result: no fix tested, none shipped. Follows `claude/isthmian-gap-2026-10-26.md`.

## What the gap is (located on the live record, never fitted on)

- The planner's 59 is `ok`, which credits 10 draw reads; `expected` (68.5) is the win-or-draw chance on those rows. Not comparable with a win test.
- Strictly (the pick won): 49 of 101 (48.5%) against 51.9 expected from mean confidence (51.4%). z -0.59. Inside noise. The -2.0 is the draw-read bookkeeping, as on 26 Oct (z -0.49 then).
- Results 46 home, 18 draws, 37 away. Mean model chances: home 48.7%, draw 23.4%, away 27.9%. Observed 45.5% / 17.8% / 36.6%. Away still under-quoted (about 9 points), draws over-quoted (about 6), as on the wider record (`claude/home-away-tilt-2026-10-26.md`). The model picked home 81 times, away 20.
- 68 of 101 rows are "No read"; 5 Strong, 9 Firm, 19 Lean. Board only (`AF_BOARD_ONLY`, `NO_LIST`), so no Daily List picks.
- Dates 30 Sep to 21 Nov 2026: one season, so no early-season or promoted-side split is possible.

## Why no fix was tested

- `history/` and `current/` still hold no en.7i season; data comes from API-Football only and this run has no `API_FOOTBALL_KEY`. No 2024-25 fit or 2025-26 check can be built, so Rule 3's 250 check games cannot be met.
- Fitting on the 101 live rows would break Rule 1.
- The one candidate, an away-side/draw tilt for tier 7, is the already rejected global `ha_scale` idea at league level; the per-league home advantage refit (`tools/model_ideas.py --fit-home`) covers it once a league has history.

## What would settle it

A workflow run with the key that backfills en.7i 2024-25 and 2025-26, then the gated per-league home advantage fit. Do not reopen on the live record alone.

Nothing changed in the model, bands, calibration or grading.
