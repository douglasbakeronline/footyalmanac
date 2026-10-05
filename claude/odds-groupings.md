# Odds tab group rules: backtest (5 Oct 2026)

Task: replay the group rules (65% tested rate over 30 games, spread rules, three bands) on past days and compare each band's win rate with its stated chance.

## What can be replayed

The Odds tab launched 4 Oct 2026. `groupings-record.json` holds 7 groups, 5 settled: 1 won, 4 lost, expected 1.49 wins. Steady 1 of 2 (expected 0.70), Balanced 0 of 2 (0.52), Stretch 0 of 1 (0.26). Legs: 13 of 18 won. Too few to say anything.

History cannot rebuild the groups faithfully. `predictions/` stores the model's confidence but not the tested rate the board showed that day (the rule's 65% / 30 bar), and no bookmaker price is archived anywhere. A faithful replay needs both, so it has to wait for the live archive to grow, or for the tested rate to be archived with each prediction.

## Approximate replay

`python3 tools/groupings_backtest.py` runs `groupings._best` unchanged on the 14 graded football days in `record.json`. A leg is a non-draw, non-Celtic pick with calibrated confidence of 65%+, its chance is that confidence, its price is the fair price (1 / confidence), the estimate cap is lifted.

Result: 3 groups, all Steady and all first choice, 3 won, stated chance 35% on average. No Balanced or Stretch group could be built: priced fairly, 65%+ picks are 1.0 to 1.5 and five of them rarely multiply past 4 while meeting the "one leg 1.60+" spread rule. In the live tab those bands exist only because real bookmaker prices run longer than fair ones, or because mixed sports add longer legs.

## Verdict

No rule change. Three groups is noise (3 wins at 35% stated is p about 0.04 by itself but on 3 correlated-by-day samples, not evidence of under-stated chances), and the live record points the other way. Rules 2 and 3 apply: no change without a paired, gated comparison.

Next steps if Douglas wants this answered: (1) archive each leg's tested rate and price in `predictions/` or keep `groupings-archive/` going until about 100 settled groups; (2) re-run `groupings.grade()` and compare stated against actual per band, with a bootstrap. Prices never feed a model.
