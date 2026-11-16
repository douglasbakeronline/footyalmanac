# The Card at rule 12 (opposition 5.0+) and the List 2x on paper, 16 Nov 2026

Douglas, 16 Nov 2026, after a run of lost Card 2x groups: "The daily list and reserve performance had been really great today ... the performance of the group betting is terrible ... what can you do here to actually win - look at the daily list and reserve - why are not mirroring that's success". On the two proposals put to him: "Yes."

## Why the list's success does not carry into groups

- The Card to 16 Nov: 40 groups, 13 won against 13.66 expected. Legs landed 81 of 120 (68%). Returns were −9.5% flat and −14% at the page's stakes. The groups landed as their chances said.
- The Daily List on the results ledger: 592 graded picks, 87.5% won. 239 were priced, at an average of 1.107, and returned −1.6% a pick. The reserve returned −5.9%.
- A 2x from list picks needs about seven of them. Seven 88% picks land together about 41% of the time, so the group pays about −11% after the margin compounds. A group's return is roughly the product of its legs' returns. Only legs that land above their price can win over time; landing often is not enough.

## Rule 12: the opposition at 5.0+

- `CARD_MODEL_OPP_MIN = {"football": 5.0}` and `CARD_RULE` 12. `model_fault` refuses a football pick whose opponent is priced under 5.0, or has no price at all.
- This is the pre-registered `m7opp5` (`claude/card-m7opp-2026-11-15.md`). Across five football-data seasons it pooled +17.5% against +9.6% on 450 legs, p(worse) 0.014, and was ahead in all five. It was set live before its 100-pool-leg gate, as the owner's call.
- The pool on 16 Nov (`tools/card_replay.py`, first prices):

| Variant | Days | Groups | Won | Return | Legs landed v quoted |
|---|---|---|---|---|---|
| live (rule 12) | 12 | 20 | 11 | +34% | 81.7% v 68.5% |
| m7noopp (rule 11) | 14 | 23 | 9 | −4% | 72.5% v 67.7% |

  Paired rule 11 − live: −1.11 units a day, p(worse) 1.00, over 14 days.
- **Cost:** two fewer days with a group on the pool. NBA and tennis picks are unaffected.
- `m7opp5` now equals live. `m7noopp` replays rule 11 on the pool and on football-data (`cardM7`).
- `card_integrity.needs_opp` again flags a rule 12 football leg with no opposition price.
- **Roll back:** `{}` and `CARD_RULE` 11.

## The List 2x (paper)

- `build_list_card` and `list_group`: the Daily List's picks with a real price of `LIST_ODDS_MIN` (1.15)+, not started, one per fixture, sorted by the model's number. They are taken until the slip reaches 2.0, with at most `LIST_LEGS_MAX` (6) picks. The day has none if 2.0 is not reached.
- Built once a UK day and held as first built until its first start, as the Model card was, then archived and graded. Stake 0; nothing is pushed (`notify.py` reads Card groups only).
- The record line is `groupings-record.json` `cardList`. The page shows the "On paper: the List 2x" fold on the Bets tab and "List 2x on paper (from 16 Nov)" under More numbers.
- **Read at 30 settled groups:** if it lands above its expected chance and beats the live Card's return, put it to Douglas as a staked kind. If not, switch it off.
