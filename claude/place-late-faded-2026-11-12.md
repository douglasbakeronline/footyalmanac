# "Place once, late": the evidence faded, the page now reads it (12 Nov 2026)

The Bets tab's playbook has opened "Place once, late" since 11 Nov (#236),
quoting the 10 Nov read in `claude/price-timing-read-2026-11-10.md`: on 104
settled Card-rule picks the last pre-start price paid about 2 points more
than the first (+1.95, p(late no better) 0.011). The nightly Card review of
12 Nov printed the same test on 174 settled legs: late -0.25 points, p 0.702,
"no clear read". The page was quoting a number the record no longer
supports.

## The read on 12 Nov (`tools/price_timing.py`, pool from 30 Oct)

| leg set | settled | late v first | p(late no better) | read |
|---|---|---|---|---|
| live rule (11), all | 174 (126 won) | -0.25 points | 0.702 | no clear read |
| live rule, dates to 10 Nov | 156 | +0.08 | 0.444 | no clear read |
| live rule, after 10 Nov | 18 | -3.06 | | too few legs |
| live rule, football | 147 | -0.12 | 0.61 | no clear read |
| rule 6 (`patch_of("rule6")`), all | 89 | +0.02 | 0.507 | no clear read |
| rule 6, dates to 10 Nov | 79 | +0.32 | 0.294 | no clear read |
| 10 Nov read (rule 6 + 55% wider-rule legs, as then live) | 104 (69 won) | +1.95 | 0.011 | take the price late |

The leg set follows the live `card_fault`, so it changed with rules 7 to 11
and the wider-rule floor (55% to 60%). Even on the rule 6 legs of the same
days, rebuilt today, the late gain is +0.32, not +1.95: the 10 Nov read was
carried by legs that are no longer in the set and has not held. First to last
price over all 177 legs: 75 drifted, 75 shortened, mean +0.45%, p 0.153.

## What changed

- `tools/price_timing.page_read()` returns the settled read compactly (`n`,
  `won`, `lateGainPct`, `p`, `read`, `lastMedianH`, `at`, `rule`).
- `groupings.timing_page()` puts it in `groupings-data.js` as `timing` on every
  build (0.7s, committed archives only; `None` on any failure).
- `placeHabit` in `index.html` writes the first habit from it: "Place once,
  late" with the gain only when the read is "take the price late" (50+ legs,
  day-resampled p <= 0.10); "Place once, early" when the read goes the other
  way; otherwise "Place once, before the first start", nearer it than not
  because a group can change until its first start, and the price gives no
  reason to wait or hurry. No data: the structural reason alone, no number.

## Not changed

Any Card rule, push or briefing time (`notify.py` never claimed a late gain),
the nightly review's own lines. The unused plan panel (`signalsPanel`, off the
page since 11 Nov) still holds the old line; it is not rendered.

## Next

The habit follows the read on its own. Bookmaker choice is untouched: Bet365
+0.93% v the average on 108 legs, William Hill -0.16% on 103; `CARD_BOOK` is a
preference, and the page already shows every UK book's price.
