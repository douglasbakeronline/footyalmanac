# Southern League Premier Central (en.7sc) v its quotes, 9 Nov 2026

HQ planner (8 Nov) flagged en.7sc: 43 of 74 landed against 51.3 expected (69% quoted), z -2.1. Result: no fix tested, none shipped. Same position as `claude/isthmian-gap-2026-10-26.md`.

## What the gap is (record used only to locate it, Rule 1)

- The planner's "landed" is `ok`, which credits draw reads (10 rows) and measures against a win-or-draw `expected`. Strictly (the pick won): 33 of 74 (44.6%) against 39.0 expected (mean pick confidence 52.7%), z -1.44. Inside noise.
- Results: 30 home, 17 draws, 27 away (40.5% / 23.0% / 36.5%). Mean model chances: home 48.5%, draw 23.9%, away 27.6%. Draws are on quote; the away side is under-quoted by about 9 points, the same direction as the wider record (`claude/home-away-tilt-2026-10-26.md`). 60 of 74 picks were home.
- Celtic's Law rows (32): 18 won. Others (42): 15 won. Promoted/unrated sides are the weaker half of the sample but 32 rows cannot separate it from chance.
- en.7sc is board only (`sources.AF_BOARD_ONLY`, `build.NO_LIST`): none of these are Daily List picks.

## Why no fix was tested

- `history/` holds no en.7sc season; the data comes only from API-Football. This unattended run has no `API_FOOTBALL_KEY`, so no history could be fetched and no replay run.
- A league-level fix needs 250+ check games (Rule 3). One step-7 league has about 24 clubs, roughly 550 games a season, so one season would clear the count, but p(worse) and gain on one league are a long shot, and a per-league home-advantage refit already exists (`tools/model_ideas.py --fit-home`, `home-advantage.json`).
- Fitting on the 74 live rows would break Rule 1.

## What would settle it

A workflow run with the key: replay en.7sc on 2024-25 (fit) and 2025-26 (check), then test one thing: tier-7 home advantage lowered (an away lift), through the same gates. Expect the replay's step-3 calibration (bands on quote, log loss 1.034) to hold.

Nothing changed in the model, bands, calibration or grading.
