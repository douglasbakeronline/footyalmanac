# Isthmian League Premier (en.7i) v its quotes, 26 Oct 2026

HQ planner flagged en.7i: 24 of 45 landed against 30.6 expected, z -2.1. Result: no fix tested, none shipped.

## What the gap is

- The planner's "landed" is `ok`, which also credits draw reads (a pick where the model's draw read applies). `expected` for such rows is the win-or-draw chance, not the pick's win chance. Three of the 24 are draw-read credits (`ok` true, `won` false).
- Strictly (the pick won): 21 of 45 (46.7%) against 22.6 expected (mean pick confidence 50.3%). z = -0.49. Inside noise.
- Results: 21 home wins, 6 draws, 18 away wins. Mean model chances: home 47.2%, draw 23.8%, away 29.0%. Observed home 46.7%, draw 13.3%, away 40.0%. The away side is under-quoted, as on the wider record (`claude/home-away-tilt-2026-10-26.md`); the sample (18 away wins) is too small to say more.
- Most rows are "No read" (under 55%), which is why the 68% quote on the planner line is high: it mixes in draw-read expectations.
- en.7i is board only (`sources.AF_BOARD_ONLY`, `build.NO_LIST`), so none of these are Daily List picks.

## Why no fix was tested

- `history/` holds no en.7i season, and the data comes from API-Football only. This unattended run has no `API_FOOTBALL_KEY` (api-sports returns 403), so no history could be fetched and no replay run.
- Even with data, a league-level fix needs 250+ check games (Rule 3). A step 7 league has about 24 clubs x 2 seasons of games, and the existing step-3 replay (1,818 fixtures over four leagues) showed the step as a whole at log loss 1.034 with bands on quote (`build.ACCURACY_BANDS_STEP3`).
- Fitting on the 45 live rows would break Rule 1.

## What would settle it

Replay en.7i on 2024-25 (fit) and 2025-26 (check) from API-Football with a key (a workflow run, not this sandbox), then test the existing per-league home advantage refit (`tools/model_ideas.py --fit-home`) or a larger `ha_scale` for tier 7. Expect it to miss the gates on sample size alone.

Nothing changed in the model, bands, calibration or grading.
