# The Bookies mark as a veto on the Daily 2x and List card (28 Nov 2026)

Build session, 28 Nov 03:17 London slot. `claude/bookies-mark-2026-11-20.md`
named the next step if the mark held: "a rule, not a mark: a 10-point
model-above-market veto on the Daily List 2x / List card legs, replayed on
the ledger first." The mark still holds on the ledger (`tools/market_gap.py`,
28 Nov): 328 marked picks at 60%+ landed 53.7% v the model's 72.0% and the
bookmakers' 53.7%; the other 1,646 landed 75.0% v 72.1%.

## What was built

`tools/list_card_replay.py` gains a pre-registered `nobookies` variant: live,
with every pick the model rates 10+ points (`market_gap.GAP_WARN`) above the
bookmakers' fair chance left out before the slip is built. The fair chance is
the leg's own where the pool kept one, else 1 / price / 1.05 (`market_gap`'s
rule; the ledger keeps the pick's price only). `fair_of`, `marked`. Every
non-live variant is now paired and gated on its own (`paired`, `gate` keyed
by variant). Tests: `tests/test_list_card_replay.py`.

## The read (first price; last pre-start price in brackets)

| Card | Source | Live | nobookies | v live a day | p(worse) | differs: days / legs |
|---|---|---|---|---|---|---|
| Daily 2x | ledger, 3 Oct to 27 Nov | 18/46 v 19.5, -10.5% (22/46, +8.8%) | 18/46 v 19.0, -15.0% (21/46, -3.3%) | -0.05 (-0.12) | 0.68 (0.96) | 11 / 36 |
| Daily 2x | pool, 30 Oct to 27 Nov | 12/29 v 11.5, -1.5% (-2.6%) | 9/29 v 10.6, -26.8% (-28.7%) | -0.25 (-0.26) | 0.90 (0.92) | 12 / 47 |
| List card | ledger | 5/12, -9.0% (8/12, +45%) | 4/10, -13.1% (6/9, +41%) | -0.02 (-0.14) | 0.54 (0.81) | 4 / 7 |
| List card | pool | 3/6, +5.5% (4/7, +24%) | 2/2, +112% (3/4, +55%) | +0.32 (+0.07) | 0.20 (0.41) | 4 / 0 |

The veto loses on the Daily 2x on both sources at both prices. The List
card's pool line is two slips and builds none on the days it differs.

## Why

Marked picks that reach these slips are not the marked picks that lose.
Inside the live slips they landed 7 of 11 (ledger) and 11 of 15 (pool),
v the model's 76-77% and the bookmakers' 60-64%: under the model, above the
price. The mark's losses sit in college basketball (110 picks 15+ above,
46% landed, -14%), which both slips already leave out
(`DAILY_SPORTS_OFF`, `LIST_SPORTS_OFF`). In football the marked bands land
under the model but above the bookmakers (10-15: 58.9% v 55.0%, +0.8%;
15+: 55.8% v 45.4%, +14.2%). Taking a marked pick out means a longer-priced
leg or one more leg to reach 2x, and that costs more than the pick's
overrating.

So the mark says what it says (the model is too high there), and is not a
reason to leave a non-college pick off a slip at its price.

## Decision

Gate not met (100+ differing legs and p(worse) 0.30 or under on both
sources); behind on the Daily 2x everywhere. Nothing changes live; the
Bookies mark stays display only. Re-run with `python3
tools/list_card_replay.py` (and `--closing`) beside the 30 settled-slip reads
of `claude/daily-2x-2026-11-17.md` and `claude/list-card-2026-11-17.md`.
Not to reopen without a sample where marked non-college picks lose at
their price.
