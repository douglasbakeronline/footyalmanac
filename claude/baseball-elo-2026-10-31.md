# Baseball Elo settings, 31 October 2026

Task: MLB landed 27 of 40 against 22.1 expected (z +1.5). Live record used only to locate the gap (Rule 1).

Finding: history disagrees with the live gap. Before this change the check window (2025-07 to 2026-09-27, 3,626 games) showed MLB over-confident (55%+ landed 57.4% v 60.3% quoted; 65%+ 65.0% v 68.4%). 40 live games is within noise (z 1.5).

Test: K 3-8, hfa 15/25/35, regress 0.15/0.25/0.35/0.5, no margin of victory, fitted on 2024-07..2025-07 and confirmed on the check window. Old K 8 was the edge of the shipped grid. Best fit K 4, hfa 25, regress 0.15: fit 0.6814 to 0.6800; check 0.6859 to 0.6841, gain 0.0018, p(worse) 0.008. Shipped (gates passed). K 4/hfa 15 gave similar gain but p(worse) 0.045; K 5 variants gain 0.0011-0.0014, p(worse) 0.007-0.07.

After: check bands 55%+ 58.3 v 59.6, 60%+ 62.5 v 63.7, 65%+ 71.8 v 67.9 (n 188), 70%+ 83.3 v 72.2 (n 36). Calibration refit +0.0003 p(worse) 0.78, not applied. List bar: none (75%+ n=3).

Caveat: the grid search was local and the gain is small; `sports.GRID` itself was not changed, so a future `--tune` over the old grid will propose K 8 again. Extend the grid (K 4-6, regress 0.15) before the next by-hand run.
