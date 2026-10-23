# Does the model beat the bookmakers' price? (23 Oct 2026)

**Result: no edge. Rejected. Do not build a group rule that prefers "value" legs.**

Method: `tools/odds_edge_test.py` takes every home / draw / away leg of every
priced football match in the fit season (2025-26, 12,510 legs, ~4,170 matches)
and the check season (2026-27 so far, 1,749 legs), football-data.co.uk average
prices (the closing-price file), model chance exactly as the site quoted it
(live calibration, `odds.model_probs`). Fair chance = margin removed (`odds.fair`).
Statistic: mean(hit - fair chance), paired per leg, bootstrapped (2,000 resamples).
Positive means the leg landed above the bookmaker's fair chance. Never touched
`record.json`; no prices feed any model. Football only: there are no free
historic prices for the other sports, so nothing can be said about them.

## Where the model is above the market, legs landed BELOW the fair chance

| Legs with model minus fair at least | Fit n | Fit gap | p(gap<=0) | Check n | Check gap | p(gap<=0) |
|---|---|---|---|---|---|---|
| 2 points, all legs | 4,133 | -2.0 pts | 1.00 | 682 | -1.9 | 0.88 |
| 4 points, all legs | 2,586 | -2.8 | 1.00 | 473 | -1.9 | 0.85 |
| 6 points, all legs | 1,584 | -2.2 | 0.98 | 319 | -1.7 | 0.78 |
| 4 points, model favourite (p 50%+) | 549 | -3.6 | 0.95 | 52 | -6.5 | 0.83 |

Same sign on both seasons at every threshold. By outcome (4+ points): home
-3.3 / -3.8, away -2.7 / -0.6, draw -0.8 / -0.2 (all below fair). By price,
2.2-4.0 (the bulk): -3.1 / -3.4. Model band 50-65%: -3.8 / -14.6 (n 383 / 40).
Control: legs where the model is 4+ points BELOW the market landed above fair
(+2.5 pts fit, +0.4 check): the market knows more than the model, the
"edge" is the model's error. This matches `odds.py`'s own report (log loss
model 1.0164 v market 0.9945; closing line value -3.5 pts, p 1.00).

## The cells that look positive do not hold

- Model 75%+ and 4+ points above fair: fit +3.1 pts (n 70, p 0.26), check n 4.
  Not testable on the check season and not significant on the fit season.
- Model 65-75%, 4+ points above: fit -7.4 pts (n 96), check +30 pts on n 8
  (p 0.01, but 8 legs: noise). Opposite signs, fails the "both seasons" rule.
- Price 1.3-1.6: -0.4 pts fit (n 89), +19 pts check on n 6.

Rule 3 gates need 250+ check fixtures; the check season has 52 model-favourite
legs at 4+ points, so no positive subgroup can pass. Nothing was fitted.

## What it means for groups

- The 21 Oct finding (legs 5+ points above the market landed 70% against 82%
  for legs at or below it) is the same effect: more disagreement with the
  market means a worse leg. `MAX_ABOVE_BOOK` (5 points) is right and could be
  tighter; a rule that prefers value legs would do the opposite of what works.
- Groups lose the bookmakers' margin on average, and there is no edge to win
  it back. Better odds are only worth having where the price is higher for the
  same landed rate, which this test says never happens on football.
- The one thing that does work is the existing veto: leg chance = min(tested
  rate, model, fair), with the model not above the market.

Open (needs more data, not a rule): re-run on 2026-27 after Christmas for the
75%+ cell; the cup and AF-priced leagues have no history for it.
