# The Card's price move by hour of first pricing and sport, re-read (18 Nov 2026)

Oscar, HQ planner task "When to take the Card's prices". Advisory: no change to
`notify.py`, `SLOTS` or the build times. Earlier reads: `price-by-first-hour-2026-11-10.md`
(107 legs, 2 hour buckets), `price-timing-read-2026-11-10.md`,
`place-late-faded-2026-11-12.md` (the late gain faded). `tools/price_timing.py`
on the pool today; the live record only located the gap, nothing was fitted.

## Numbers (283 Card-rule or wider-rule legs with a first and last real price; last price a median 1.5h before the start, 198 within 3h)

Move = last / first - 1 (positive = prices lengthened). p = day-resampled
bootstrap that the mean is at or under zero.

| first priced (UTC) | sport | legs | mean move | p |
|---|---|---|---|---|
| before 07 (00:10 / 05:15 builds) | all | 142 | +1.89% | 0.037 |
| before 07 | football | 99 | +0.61% | 0.218 |
| before 07 | NBA | 43 | +4.84% | 0.049 |
| 15+ (the 17:00 build) | all | 112 | -0.38% | 0.761 |
| 15+ | football | 90 | -0.08% | 0.622 |
| 15+ | NBA | 22 | -1.57% | 0.813 |
| 07 to 14 | all | 29 | -0.40% | 0.751 |

By lead of first price on the start: 72h+ +1.08% (104), 48-72h +3.04% (44),
24-48h -0.51% (53), 6-24h -0.13% (66), under 6h +0.30% (16).

Settled, first v last price (249 legs, 178 won): -1.12% v -0.47%, late gain
+0.65 points, p(late no better) 0.307: no clear read (unchanged since 12 Nov).

## Read

The 10 Nov finding that early-priced legs drift has shrunk to NBA: football
priced early moves +0.6% (p 0.22), anything priced in the evening does not
drift. The overnight NBA drift (+4.8%, 43 legs, mostly one 00 UTC bucket) is
a first price taken 2-3 days out; it is under the 50-leg read bar for the
sport and a multiple-look cut (hour x sport), so not a basis for moving a push.
The two overall tests that could justify a move (all legs' mean move,
p 0.092; settled late gain, p 0.307) do not reach the read bar (p <= 0.10 on
the late gain). The Card is a frozen group until its first start, and a push
earlier or later changes nothing the model reads, so Rule 3's log loss gate
does not apply; the pre-registered price-timing read is the test, and it says
no clear read.

## Not changed

`notify.py`, `SLOTS`, the build times, `placeHabit` (it follows the read on
its own). Revisit when NBA early-priced legs reach 50+ and the settled late
read reaches p <= 0.10 (or the reverse) on 300+ legs.
