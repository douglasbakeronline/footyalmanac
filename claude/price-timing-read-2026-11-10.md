# When to take the Card's prices: the read with its evidence (10 Nov 2026)

Issue #156 asked which bookmaker and when. `tools/price_timing.py` already
printed a "read" on the move from the first real price to the last pre-start
price, but the read was the sign of the mean on any sample: two tennis legs
got "take the price late". This session made the read earn its place and
added the test the question needs, the return itself.

## What changed in the tool

- A read ("take the price late" / "take the price when published") needs
  `MIN_READ` (50) legs and a bootstrap p of the opposite sign at most
  `READ_P` (0.10); otherwise "too few legs to read" or "no clear read".
- The bootstrap resamples whole days (legs on one day share a market): 13
  days at 10 Nov.
- `settled`: singles at one unit on settled Card-rule legs, return at the
  first price v at the last pre-start price, paired by leg. A drift on a leg
  that lost pays nothing, so this is the number a push time should follow.
- Legs not started yet are left out (`notStarted`): their last price so far
  is not their last. The nightly run had been reading the next days' legs as
  closed.

## The numbers (pool 30 Oct to 10 Nov, Card-rule and wider-rule legs)

| | legs | read |
|---|---|---|
| first to last price, mean move | 107 (52 drifted, 41 shortened, 14 unchanged) | +1.76%, day-resampled p(no drift) 0.003 |
| median move | | 0.0% (the mean is carried by drifts of 10-28% on a few legs; trimmed of the top and bottom 5, +1.1%) |
| best price, first to last | 92 | +1.55% |
| by price band | 1.00-1.30: 35, +0.2%; 1.30-1.60: 60, +1.7%; 1.60+: 17, +4.2% | |
| singles, settled | 104, 69 won | -7.21% at the first price, -5.26% at the last; late +1.95 points, p(late no better) 0.011 |
| football | 93 | +1.65%, p 0.002 |
| NBA | 16 | too few legs to read |
| tennis | 3 | too few legs to read |

It agrees with the football-data replay, which never beat the closing line
(CLV -3.4% on the 2025-26 leg rule, `claude/card-seasons-2026-11-09.md`):
prices taken early were shorter than at the close. The margin did not move
(1.052 first, 1.052 last), so the drift is not a change in overround.

## What it means and what it does not

- Taking the Card's legs near the start has paid about 2 points a single,
  mostly on football; on a three-leg group that compounds to roughly 6.
  That is larger than the gap between William Hill and Bet365 (+0.3% v the
  average for Bet365, -0.04% for Hill).
- It is 13 days and one sport. NBA and tennis have no read yet.
- The last price is the last the build saw, a median 1.9h before the start,
  not the true close.
- No Card rule changed, and nothing feeds a model. The page now says it in
  one dated line under Place now; the briefing times in `notify.py` are not
  moved (the night briefing at 21:00 UK already sits close to the evening
  starts, and the Card pushes when a group is made, often a day ahead).

## Next

The nightly Card review prints the settled line from tonight. If it holds on
200+ settled legs and the NBA gets a read, the Card push could carry "place
nearer the start" or a reminder push 2-3h before a group's first start.
That is Douglas's call on how he places, not a rule change.
