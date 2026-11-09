# Which legs land at their quote? Third look, no rule, no change (9 Nov 2026)

**Result: no leg-selection change shipped. A note only, because the evidence cannot pass the gates, not because a test failed.**

Not repeated: the football-data.co.uk scans of 23 Oct (`leg-property-scan-2026-10-23.md`) and 31 Oct (`leg-property-rescan-2026-10-31.md`). Eligible legs land above quote on both seasons (fit +9.3 pts on 310, check +8.8 on 42); no cut by sport, tier, home or away, price, chance band or league keeps a lead on both seasons; the one rule replayed (model at or below market) removes about half the fit legs (limit one fifth) and its lead does not hold on check. The edge test (`odds-edge-retest-2026-11-09.md`) was rerun today on unchanged data with the same answer. I did not rerun the leg scan: its inputs are unchanged and it would print the same table.

## What was new to check

The 31 Oct note left two properties open: tested rate and Celtic's Law flag, which history does not carry. `groupings-archive/pool-<date>.json.gz` has kept the tested rate (`pTested`) per leg since 30 Oct. Counted on the 10 pool days to 8 Nov: 1,847 legs, of which only 45 are real-priced, not `multOnly`, football and 65%+. The pool rows hold no outcome, so landing would have to be joined from the graded records, which is descriptive only (Rule 1). 45 legs is far below the 250 check fixtures Rule 3 needs, and 38% of early legs were estimates (`card-pool-coverage-2026-11-09.md`).

## Verdict

Nothing to replay on the pool yet. Re-cut tested rate and Celtic's Law at the 30 Nov review, when the pool has a month of real prices (`tools/card_replay.py`). Until then do not rerun the football-data leg scan or the tighter model-over-market cap: three runs, one answer.
