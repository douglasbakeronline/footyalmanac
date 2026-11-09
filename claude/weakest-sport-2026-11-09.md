# Weakest of the other sports, 9 Nov 2026 (Theo): none below the bar, no change

Read only from `sports-record.json` and `tennis-record.json` (Rule 1: nothing fitted on them). Games graded, hits v expected, z = (hit rate - expected) / binomial se.

| Sport / tour | n | hit | expected | z |
|---|---|---|---|---|
| College football | 291 | 193 | 202.7 | -1.23 |
| ATP | 528 | 327 | 335.1 | -0.73 |
| NFL | 88 | 55 | 57.4 | -0.54 |
| WTA | 867 | 556 | 557.3 | -0.09 |
| NBA | 146 | 99 | 94.0 | +0.86 |
| Rugby | 88 | 65 | 60.8 | +0.97 |
| MLB | 40 | 27 | 22.1 | +1.54 |
| College basketball | 352 | 286 | 269.1 | +2.12 |

Nothing is two standard errors under quote on 50+ games, which is the repo's bar for acting on a sport. College football is the furthest under and is already off the Daily List (`sports.LIST_OFF`, 19 Oct). ATP's shortfall sits in the 55-65% bands (100 of 183 v about 110 quoted, z about -1.3; 55-60% alone 50.5% v 57.3%, n 99, z -1.4), while its 70-85% bands land above quote. That is a shape, not a gap: a recalibration would need a walk-forward fit on history (`tools/tennis_bands.py`), and the ATP list bar already moved to 80% on 6 Nov (`tennis-list-own-band-2026-11-06.md`). Re-testing tennis surface was rejected again today (`tennis-surface-recheck-2026-11-09.md`).

Decision: no change; a candidate would have no evidence that passes the gates. Revisit when ATP reaches about 900 graded games (the 55-65% band gap would then be testable at 2 se if it persists) or college football crosses -2 se.
