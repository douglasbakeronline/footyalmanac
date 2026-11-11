# The Card's price move by the hour it was first priced (10 Nov 2026)

Oscar (Odds Analyst), HQ planner task "When to take the Card's prices".
Advisory; nothing in `notify.py` or the build times changed.

Already done: the move first to last by lead (`claude/price-lead-time-2026-11-09.md`)
and the settled return first v last (`claude/price-timing-read-2026-11-10.md`).
The one cut not made was by the hour of first pricing and sport.

## Method

`tools/price_timing.legs()` on the pool, Card-rule and wider-rule legs with a
first and a last real price, started only: 107 legs, 13 days. Hour is London
time of the first real price (`priced.at`, else `firstAt`). Move is
last / first - 1; p is the day-resampled bootstrap that the mean is at or
under zero. The live record located nothing here; no fit was made.

## Numbers

| first priced (London) | legs | mean move first to last | p(no drift) |
|---|---|---|---|
| 00:00-06:59 (the 00:10 / 05:15 builds) | 54 | +2.41% | 0.034 |
| 16:00-20:59 (the 17:00 build) | 53 | +1.11% | 0.011 |

No leg was first priced in any other window: the pool's first price is
written by the first build that sees the leg, and only those two builds
price it (07:40 to 12:00 builds find legs already priced). So "by hour" has
two buckets, not five.

By sport and window: football 48 legs +2.05% (early) and 45 legs +1.24%
(evening); NBA 6 and 6 legs, +5.3% and +0.65%; tennis 2 legs, -0.44%.
NBA and tennis are far under the 50-leg read bar.

## Read

Prices drift (lengthen) from the first price to the last in both windows,
so there is no case for publishing or pushing the Card earlier. The early
window drifts more (+2.4% v +1.1%), consistent with the lead-time table: the
longer before the start the first price, the more it lengthens. This
supports the standing read, take prices nearer the start, and nothing
more: it is the same 13 days and mostly football, a mean carried by a few
10-28% drifts (median 0), and `last` is a median 2h before the start, not
the close. No Rule 3 gate test applies (no model or rule changed).

## Not done

No change to `SLOTS`, the build times or the push. Revisit at 200+ settled
legs with an NBA read (see `price-timing-read-2026-11-10.md`, Next).
