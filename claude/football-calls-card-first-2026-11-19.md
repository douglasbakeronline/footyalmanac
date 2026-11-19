# The capped football price calls go to Card picks first (19 Nov 2026)

## What the 11:05 UTC build showed (deploy run 44511549028)

football unpriced: noOdds 170, **capped 97** (Premier League 5, Serie D
Girone A 4, 2. Lig 4), moved 8, noFixture 7, kickoff 4.

`capped` is a mid-priced leg (`multOnly`: its leg chance under `WIDE_MIN`,
65%) that the bulk day prices missed and that came after the build's
`FB_CALLS_MULT` (150) one-fixture calls were spent. The calls went in board
order, so which legs got them was an accident of the order the board lists
leagues in. A `multOnly` leg can still reach the Card: the Card asks for the
model at 60%+ (`CARD_FAIR_MIN`), and a 62% pick with a 70% tested rate has a
leg chance of 62%, so it is `multOnly`. Unpriced, it is off the Card.

The pool archive shows the scale on the weekend ahead: football legs at 60%+
in a league the Card takes with no real price, 40 of 73 on 21 Nov and 31 of
46 on 22 Nov (16 and 8 of them `multOnly`). Most are `noOdds` (no book prices
the game) and cannot be fixed; the pool does not say which were capped.

## What changed

`price_football` spends its calls in `call_order`: legs the Card could reach
once priced (`card_reach`: football, the model at `CARD_FAIR_MIN`+, a
`card_league`, clean of the Daily List's blind spots), then list and reserve
picks, then the rest; within each the nearest day, then the strongest pick.
The cap, the calls and every leg's price are as before; only who gets the
calls changes. `card_reach` is a price-order test only: `card_fault` and
`model_fault` still decide the Card.

## Not changed

`FB_CALLS_MULT` (API-Football Pro is 7,500 calls a day across every build and
the markets sweep; raising it is a budget decision), any `CARD_*` constant,
`CARD_RULE`, the replays, the page.

## What to read next

The next CI build's "football unpriced:" line: `capped` should hold roughly
steady while the capped legs move to weak picks in the wider leagues. If
Card-reachable legs are still capped on a Saturday, the evidence for a
higher `FB_CALLS_MULT` is a count of them, which `missComps` can carry.

Tests: `tests/test_football_unpriced.py` (two new, the first fails on the old
code), full suite 1,221 passing, `nametest.py` clear.
