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

## Live archive rerun (12 Oct 2026)

The 5 Oct note said to wait for about 100 settled groups. The archive now holds 31 groups, 30 settled (`groupings-record.json`, 4 to 12 Oct). Still no archived tested rate or bookmaker price in `predictions/`, so a historical replay of the 65% / 30 bar remains impossible. This is the live comparison of stated chance against outcome.

| Band | Settled | Won | Stated (expected wins) | Returned per 1 staked |
|---|---|---|---|---|
| Steady | 13 | 3 | 4.97 | 8.17 |
| Balanced | 8 | 5 | 2.50 | 20.87 |
| Stretch | 9 | 1 | 2.04 | 7.11 |
| All | 30 | 9 | 9.51 | 36.15 |

Overall 9 won against 9.51 expected. Bootstrap over groups (5000 resamples) of won minus expected: -0.51, 90% interval -4.5 to +3.5. Consistent with the stated chances. The band differences (Steady under, Balanced over) are inside noise at these counts.

Legs, settled: 106 of 140 won against 110.4 expected. By sport: football 61 of 81 (62.6 expected), tennis 18 of 26 (21.1), NFL 9 of 12 (8.7), college football 12 of 14 (11.9), rugby 6 of 7 (6.1). Estimated-price legs 37 of 49 (40.3 expected), priced legs 69 of 91 (70.2). The only visible gap is tennis, about 3 legs short, which matches the known tennis shortfall (`claude/tennis-hit-rate-2026-10-12.md`) and is the same legs' tested rate, not a group rule.

Lost groups: 10 lost on one leg, 9 on two, 2 on three. A single-leg-loss group is where a looser or tighter spread rule could matter, but 10 cases cannot separate any rule from luck.

## Verdict

No rule change. No candidate rule beats the current one on a paired, gated comparison, and the data cannot support one: 30 groups, correlated by day, with no historical prices. Rules 2 and 3 apply. Revisit at about 100 settled groups, or once each leg's tested rate and price are archived at publish time. Prices never feed a model.
