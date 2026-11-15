# Serie D Girone C (af.428): test not run, no history available (13 Nov 2026)

Task: the league shows 30% over 54 graded games (home 33%, 19 drawn out). Find why and test one change (league home advantage or draw handling) under Rules 2 and 3.

## Outcome: no test, no change

- The only per-game data for this league in the checkout is `predictions/` and `record-graded.json`, i.e. the scoreboard. Rule 1 forbids fitting on it, so it was not used.
- The fit season (2025-26) and the check season (2026-27) for af.428 come from API-Football through `sources.AF` / `AF_EXTRA`. `history/` has no `af.*` files and `cache/` holds no raw API-Football pages, and the unattended run has no `API_FOOTBALL_KEY`. A paired, bootstrapped fit/check could not be built.
- 54 games is inside the noise for a three-way market: at 33% a game (home rate 33%) the standard error is about 6.4 points, so 30% against a quote near 55-60% is a real shortfall, but the sample cannot say whether the cause is home advantage, draws or ratings built from thin data.

## What was not done, on purpose

- No `HOME_MULT` or per-league home-advantage entry. `home-advantage.json` is refitted by `tools/model_ideas.py --fit-home` only through the weekly gates; a hand entry from 54 scoreboard games would break Rules 1 and 5.
- No draw lift. The Championship draw lift (`claude/championship-draw-lift-2026-10-22.md`) was league-specific and needed its own replay.

## What would settle it

Run the replay on af.428 with a key (from a workflow): fit on 2025-26 with 2024-25 as prior, check on 2026-27; compare calibrated log loss (current vs `ha` scaled, vs a draw lift) paired and bootstrapped, gates >= 250 check fixtures, p(worse) <= 0.30, gain >= 0.0005. Serie D girones are one level under `en.5`-style amateur leagues: promotions and relegations between 18-team groups each summer leave priors thin, so a shrink-to-league-mean on early-season ratings is the likelier lever than home advantage. Also worth checking whether 2026-27 gironi membership changed from 2025-26 (the prior then rates the wrong peer group).
