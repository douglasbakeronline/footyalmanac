# The opposition's price: the lopsided-market rule (6 Nov 2026)

Douglas, from his own William Hill slips: his winners were favourites near
1.40 whose opposition was priced 10-12; his losers were favourites whose
opposition was priced about 4. "I've got this 1.4 versus 12. This is what
I've noticed is really kind of helped me the most."

## Why it is a real signal

A favourite's price says how likely the bookmakers think the favourite is.
In a three-way market the opposition's price says where the rest sits: at
12.0 the away side is about 8% and the draw about 24%; at 4.0 the away side
is about 24% and the draw has been squeezed. Same favourite price, a
different game. The Card's leg rule only looked at the pick's price and the
model's number.

## The test (`tools/card_legs_history.py`, run in CI on PR #143)

Every candidate leg in the past-season replay (Card price and 60% gate,
football-data.co.uk prices, the model's walk-forward number with the live
calibration), bucketed by the opposition's price within favourite price
bands. Nothing fitted; rule 1 holds.

2025-26, favourite 1.15-1.35 (the only band where opposition 9+ occurs):

| Opposition | n | landed | quoted | return avg | return best |
|---|---|---|---|---|---|
| 6-9 | 109 | 71.6% | 70.9% | -6.0% | -3.3% |
| 9+ | 230 | 83.9% | 76.0% | +3.0% | +5.5% |

All favourite prices, 2025-26: opposition 4-6 landed 63.7% v 61.8% (-4.4%);
6-9 71.0% v 66.8% (-0.6%); 9+ 84.1% v 76.0% (+3.3%, +5.8% best).

With the Card's under-market rule: opposition 9+ landed 86.8% v 75.4%
(n 106, +7.5% avg, +10.1% best) in 2025-26 and 84.6% v 76.5% (n 39, +3.7%,
+6.5%) in 2026-27 to date. Opposition 4-6 under the same rule: -3.9% and
-25.9%. Both seasons agree on both ends.

Caveats: 106 + 39 legs, enough to act on, not settled. Nearly every 9+ leg
is a favourite at 1.15-1.35; a 1.40 favourite's opposition sits at 5-8 in
these leagues, so the 1.40 v 12 games Douglas remembers were most likely
William Hill's own prices in cups or lower leagues, which the replay does
not cover.

## What shipped (CARD_RULE 6)

- Every price source now captures the opposition's average price (`opp`)
  and, in three-way markets, the draw (`draw`): API-Football (bulk and
  per-fixture), ESPN (moneyline, both codes), The Odds API, API-Sports,
  PinnWire. The pool archive keeps `opp` / `draw` (first) and `lastOpp`.
- `card_fault`: a football leg needs the opposition priced `CARD_OPP_MIN`
  (9.0) or longer; no opposition price yet is a fault until a build reads
  one. Two-way markets (tennis, the US sports, rugby) carry no draw, so the
  opposition's price is the mirror of the pick's and the condition is not
  applied there (at 1.15+ it could never be met). The wider rule is
  untouched.
- `CARD_LEGS` (3, 4) -> (3, 4, 5): lopsided legs are short, and a Card 3x
  needs five at 1.25.
- The page: every Card leg shows "v <opposition> · draw <draw>" under its
  price (bold when 9+); every Daily List row, all sports, shows "<pick> v
  <opposition>" under its tested rate from the slip checker's pool, bold
  when the market is lopsided. Display only: nothing ranks by it.
- `tools/card_replay.py` variants `rule5` (the 31 Oct to 6 Nov rule),
  `opp7`, `opp12`, pre-registered for the 30 Nov review;
  `tools/card_legs_history.py` reports the whole Card under the live rule
  and under `rule5`, and the opposition-price table (`lopsided`).
- `.github/workflows/card-legs-history.yml`: the replay on any pull
  request that changes the tool, report as an artifact.

## What to read on 30 Nov

The per-rule record (`cardByRule` 6 v 5), the pool replay under `rule5`,
`opp7` and `opp12`, and whether the Card now goes days without a football
group (the 9+ condition is strict; the wider-rule fallback covers empty
days). If the live record under rule 6 runs under quote by two standard
errors on 50+ groups, the floor line retires it as it would any rule.
