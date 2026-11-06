# The opposition's price (6 Nov 2026)

Douglas, 6 Nov 2026: his own winning hand-picks off the Daily List were
favourites at about 1.40 whose opposition was priced 10-12, and his losers
favourites whose opposition was priced about 4. "I want to work out how to
leverage that."

## Why it can carry information

A favourite's price says what the bookmakers think of the favourite. In a
three-way market the opposition's price says where the rest sits: at 12 the
away side is about 8% and the draw about 24%; at 4 the away side is about
24% and the draw is squeezed. Same favourite price, a different game. With two
outcomes (tennis, NFL, NBA, rugby) the opposition's price is the arithmetic
complement of the favourite's and carries nothing, so the rule is football
only; the price is captured and shown for every sport.

## The test

`tools/card_legs_history.py` (`lopsided`, run on PR #143 by the new
`card-legs-history.yml`): every leg passing the Card's price (1.15-1.90) and
60% gate on football-data.co.uk prices, bucketed by the opposition's price.

2025-26, all 852 legs:

| opposition | legs | landed | quoted | singles, avg price | at best |
|---|---|---|---|---|---|
| 4-6 | 171 | 63.7% | 61.8% | -4.4% | -1.8% |
| 6-9 | 449 | 71.0% | 66.8% | -0.6% | +2.2% |
| 9+ | 232 | 84.1% | 76.0% | +3.3% | +5.8% |

Same favourite band (1.15-1.35): 6-9 landed 71.6% v 70.9% (-6.0%), 9+ landed
83.9% v 76.0% (+3.0%). So it is the opposition's price, not the favourite's,
that separates them.

With the Card's under-market rule (5 to 10 under): 2025-26, 106 legs at 9+
landed 86.8% v 75.4%, +7.5% (+10.1% at best); 2026-27 to 6 Nov, 39 legs,
84.6% v 76.5%, +3.7% (+6.5%). Both seasons positive. Opposition 4-6 is
negative on both (-3.9%, -25.9%).

Caveats. Nearly every 9+ leg is a favourite at 1.15-1.35: in these leagues a
1.40 favourite's opposition sits at 5-8, so Douglas's 1.40 v 12 games were
most likely William Hill's own prices in cups or lower leagues, which the
replay does not cover. 106 + 39 legs is enough to act on, not settled.

## What shipped (CARD_RULE 6)

- `groupings.py`: every price source writes the opposition's average price
  (`opp`) and, where three-way, the draw (`draw`) onto the leg: API-Football
  bulk and per-fixture, ESPN (US sports and soccer), The Odds API,
  API-Sports, PinnWire. Both go into the pool archive (`POOL_KEYS`), the
  bench, the stale copy, the record's legs and the page's slip-checker pool
  (`check_pool` `p` / `w`).
- `CARD_OPP_MIN = {"football": 9.0}` in `card_fault`: a football leg needs
  the opposition priced 9+; unpriced opposition fails. Wide groups and the
  Model card are not judged on it.
- The page shows the opposition's price on every Bets leg and substitute,
  on football Daily List rows (from the market block, red when 9+) and on
  other sports' rows from the pool.
- `tools/card_replay.py` variants `rule5` (no opposition rule, the Card as
  it ran 31 Oct to 6 Nov) and `opp7`, for the 30 Nov review. Pool legs
  archived before 6 Nov carry no `opp`, so the live rule is empty on those
  days; `rule5` is the comparison there.
- `tools/card_legs_history.py` carries `opp` and `draw` on replay legs, so
  the weekly whole-Card replay in `tune.yml` runs the live rule.

## What it means for the Card

The 9+ legs are short (1.15-1.35), so a Card 2x needs four of them and a
Card 3x five: `CARD_LEGS` is now (3, 4, 5). The pool also keeps each leg's
last pre-start opposition price (`lastOpp`). Watch the group count over the
first week. If the Card goes empty most days,
the choice is between `opp7` and the `short` variant with more legs.
