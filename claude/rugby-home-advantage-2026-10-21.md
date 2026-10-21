# Rugby union: home advantage at the grid edge, tested and not shipped (21 Oct 2026)

Task: HQ planner flagged rugby union landing 33 of 40 (82%) against 68% quoted (z +1.9) on the live record. The record was used only to locate the question. Everything below is history (`history-sports/`, 2,335 games), fit on Jul 2024-Jun 2025, checked on Jul 2025 onward (773 warm decided games).

## Findings

- The shipped rugby fit (k 12, hfa 100, regress 0, mov on) has **hfa on the edge of `GRID`** (0-100). A wider search is not constrained by the grid.
- Home advantage sweep, k 12, check window, paired against the live setting: hfa 110 -0.0026 (p(worse) 0.00), 125 -0.0052, 150 -0.0063, 175 -0.0033, 200 +0.0032. Optimum about 150. Season carry-over: regress 0 stays best (0.25 worse at every k). K 12-16 is flat (16 marginally better).
- Full `tune_sport` with hfa up to 200: fitted k 16, hfa 150. Check log loss 0.5487 vs 0.5559 live: gain 0.007, p(worse) ~0.06-0.08; gates (n 773, p ≤ 0.30, gain ≥ 0.0005) pass.
- **But the quotes change sign.** Live setting, check bands: 65%+ landed above quoted (the live under-quote the planner saw is the same direction, 2 points here). Fitted k 16 / hfa 150: 65%+ landed 77.5% v 79.6% quoted; 75%+ 82.4% v 84.7%; 80%+ 83.8% v 87.3%; 85%+ 87.8% v 90.4%. The model gets sharper and the strong calls become overquoted by 2-3 points. The Daily List bar (own-band rule) would also move to 85% in `tune_sport`'s output, a large loss of volume. Calibration on top (a 0.02, b 1.03) is a no-op and fails its gate.

## Decision

Not shipped. Log loss improves, but it does so by trading a conservative model for an overconfident one on the picks the List uses, against the site's rule (never inflate a number; the honesty guard says the strong-call gap may not widen). The live 33/40 is 7 games above expectation on a small sample and sits in the same direction as the current conservative quotes, so it is not evidence of a bug the hfa change would fix; the hfa change would push the opposite way.

## Open for Douglas

If rugby is to be re-tuned, widen `GRID["hfa"]` (125-200) and re-fit with an explicit decision on the honesty guard, ideally with a calibration that corrects the top-band overquote (sharper ratings, flatter curve). Not done here because `GRID` is shared and the guard failed. `/tmp`-style scripts used: a sweep over `sports.replay` and `sports.losses`; `sports.tune_sport('rugby')` with `GRID["hfa"]` widened in memory, nothing written.
