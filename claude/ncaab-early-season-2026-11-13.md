# College basketball: early-season calibration (13 Nov 2026)

Theo, from the HQ planner: college basketball landed 373 of 453 (82%) v 77% quoted, z +2.7. The live record only located the gap (Rule 1).

## Where the gap is (history replay, current `sports.json` params: k 32, hfa 100, regress 0.25, mov 1)
Landed v quoted, by window:

| Window | 55%+ | 70%+ | 80%+ |
|---|---|---|---|
| 2024-25 Nov-Dec | 76.4 v 74.0 | 85.9 v 82.1 | 91.2 v 87.8 |
| 2025-26 Nov-Dec | 78.7 v 76.2 | 87.6 v 83.3 | 92.8 v 88.4 |
| 2024-25 Jan-Mar | 72.7 v 73.8 | 80.2 v 82.1 | 85.4 v 87.5 |
| 2025-26 Jan-Mar | 70.1 v 74.0 | 78.0 v 82.2 | 83.1 v 87.5 |

Under-quoted Nov-Dec in both seasons, over-quoted Jan-Mar in both. The year-round check bands average the two, which is why the whole-season test looked on quote. The live record is all November.

## Test (Rule 3 split)
Two-parameter logistic curve on log-odds (`sports.fit_calibration`), fitted on Nov-Dec 2024, checked on Nov-Dec 2025, paired bootstrap.
- Nov-Dec: a 0.2921, b 1.0497. 2,264 check games, -0.0022 log loss, sd 0.0028, p(worse) 0.20. Passes (250+, <= 0.30, >= 0.0005). Honesty guard: 65%+ gap 3.0 points under quote before, 1.3 over after, narrower.
- Reverse (fit 2025, check 2024): -0.0065, p(worse) 0.00.
- Jan-Apr (fit 2024, check 2025): -0.0026, p(worse) 0.0007, but reverse +0.0008 p 0.72, so not shipped. The over-quote Jan-Apr is open: the same split in both directions is needed first.

## Shipped
`sports.SEASON_CAL["ncaab"]` applies the Nov-Dec curve to games dated November or December; `calibrate_for` in `sports.build`. Elo params, `sports.json`, list bars (own-band admission) unchanged. Effect: early-season 70%+ calls quote higher, so more reach the list. Daily list college basketball still shows only at a William Hill price of 1.05+.

## Not done / to check
- The list bar (70% own band) rests on year-round bands; Nov-Dec bands after the curve are not separately gated.
- Refit by hand at the end of 2026-27 with the same split (fit last completed, confirm current). Roll back: remove the `SEASON_CAL` entry.
