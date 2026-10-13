# Tennis surface by tournament name: tested, rejected (13 October 2026)

Follow-up to `claude/tennis-hit-rate-2026-10-12.md`, which flagged WTA clay
main draws (41.8% landed v 55.4% quoted, n=55) and left the honest test for a
session that could reach the Sackmann archive. The archive was reachable today.

## Test

`tools/tennis_surface_eval.py` (copy of `tennis_gap_eval.py`'s walk). Every
ESPN result since the archive ends (ATP 1 Jun, WTA 2 Jun 2026) is priced from
earlier days only, two ways: B = production (everything Hard), D = surface by
tournament-name lookup (clay / grass / hard), used for both pricing and rating
updates. No parameter is fitted: `surfaceWeight` stays 0.3, so there is no
fit window to leak. The scoreboard (`tennis-record.json`) is not used. Paired
bootstrap, log loss, D minus B (negative = D better).

| Cut | n | B | D | D-B | p(worse) |
|---|---|---|---|---|---|
| ATP all | 1523 | 0.6257 | 0.6288 | +0.0031 | 0.952 |
| ATP clay events | 187 | 0.6364 | 0.6266 | -0.0099 | 0.134 |
| ATP grass events | 465 | 0.6143 | 0.6285 | +0.0142 | 0.996 |
| WTA all | 2686 | 0.5984 | 0.6008 | +0.0024 | 0.883 |
| WTA clay events | 631 | 0.5902 | 0.5962 | +0.0060 | 0.862 |
| WTA grass events | 514 | 0.6170 | 0.6241 | +0.0071 | 0.826 |
| WTA hard events | 1541 | 0.5955 | 0.5950 | -0.0005 | 0.199 |

Both halves (Jun-Jul, Aug-Oct) are worse for D on both tours. The 75%+ main
draw hit rate is no better (WTA 88.7% of 311 v 87.9% of 331; ATP 80.5% of 128
v 80.9% of 152).

## Reading

The mechanism looked right but the data says no: on WTA clay events a named
surface is slightly worse, not better, so the live clay shortfall is not
explained by hard-court ratings. It is more likely noise (z -2.0 in one of
seven cells chosen after looking) plus the thin per-player surface ratings
(`surfaceWeight` 0.3 on few clay matches). ATP clay alone improves (-0.0099)
but p(worse) 0.13 on 187 matches fails the 250-fixture gate and is outweighed
by the ATP grass loss.

Nothing shipped. Tournament-to-surface mapping is hand-kept and was written
from the autumn/summer calendar, so it would also need maintenance. A real
surface source remains an open item before June 2027.

Caveat: the name lists are my own reading of the calendar; a mis-assigned
event would dilute D. They are in the tool for inspection.
