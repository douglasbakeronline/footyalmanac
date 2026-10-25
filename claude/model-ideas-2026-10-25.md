# Douglas's model ideas, tested, and weekly learning — 25 October 2026

Douglas: "Home teams have an advantage. Teams at the bottom end of the table
have a disadvantage. Goals for and against is a big one. We need to find
greater recent form variables. Please make some tweaks ... I also want to make
sure the model is learning and changing each week."

## What the model already had

- **Home advantage:** one per tier (`engine.HOME_MULT` / `AWAY_MULT`, about
  1.33 home/away goal ratio in the top tier).
- **Goals for and against:** they *are* the ratings. Each side's attack and
  defence come from goals scored and conceded, this season blended with last.
- **Recent form:** last-5 points, a capped nudge (`FORM_MAX` 0.05). Heavier
  form, a form-led model and bottom-table / weak-goal penalties were all tested
  in September and made it worse (`claude/tuning-evidence.md`).
- **Learning:** ratings update from every result on every build (six a day);
  the calibration curve refits every Monday when it passes the gates.

## What was tested (`tools/model_ideas.py`)

Each idea on top of the live model, one strength k fitted on the last
completed season (5,262 fixtures), checked on the current season (902),
paired and bootstrapped, live calibration applied. Gates as CLAUDE.md.

| Idea | Best k | Fit Δ log loss | Check Δ | Check p(worse) | Verdict |
|---|---|---|---|---|---|
| A home advantage per league | 0.5 | −0.0010 (p 0.05) | −0.0007 | 0.33 | close: fails notWorse only |
| B table position | 0 | worse at every k | | | rejected |
| C recent goals for/against v season average | ~0 | 0.0000 | −0.0001 | 0.26 | nothing to add |
| D last-5 goal difference | 0 | worse | | | rejected |
| E last-3 points | 0 | worse | | | rejected |

B, D and E make it worse at any strength: the ratings already carry where a
team sits and how many it scores and concedes, so adding them again counts the
same thing twice. C is flat. Only A, each league's own home advantage, helps
on the season it was fitted on and points the same way on the current one,
but the current season is still too short to pass the p(worse) gate.

## What shipped: home advantage per league, learning weekly

- `home-advantage.json` (absent today) holds a factor per league: its own
  home/away goal ratio in its last completed season against its tier's
  default, raised to k/2. `engine.league_home(code)`, applied in the live
  build's league path (`adj_h` / `adj_a`) and in the replay (`home_s`).
- `tools/model_ideas.py --fit-home` runs in `tune.yml` every Monday: refit k
  on the last completed season, check against the live k on the current one,
  write the file only if every gate passes. Today it does not, so nothing has
  changed in any prediction. It will switch itself on when the evidence holds.
- `tools/model_ideas.py` (no flags) re-tests all five ideas every Monday in
  the same job, advisory, for a human to read.
- This is a deliberate, owner-requested exception to rule 5 for one
  structural parameter, gated exactly like `calibration.json`.

Tests: `tests/test_league_home.py`.
