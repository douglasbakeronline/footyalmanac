# MLB above quote, re-check, 19 Nov 2026

The planner raised the same gap as on 12 Nov (`claude/mlb-elo-k-2026-11-12.md`): 27 of 40 landed, 22.15 expected, z +1.5. Recomputed from `sports-graded.json`: identical 40 games (first 29 Sep 2026), so the MLB regular season has added nothing since. Not significant (z under 2), and it is the live record, which Rule 1 bars from fitting.

History says the opposite direction: check window (1 Jul 2025 on, 3,626 games) 60%+ landed 61.4% v 64.0% quoted; 55%+ 58.2% v 60.0%. The settings were already refitted on 12 Nov (K 3, hfa 15, regress 0, calibration refit; gain 0.0015, p(worse) 0.09 on the check).

Not re-tested: K below 3 and regress below 0 (the grid's edge). The 12 Nov note advised against chasing them, baseball being mostly noise, and with no new games there is nothing new to confirm on. Decision: no code change. Revisit at 200+ graded MLB games, i.e. after the 2027 season starts.
