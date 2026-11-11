# The Edge flag's opposition floor lowered to 4/1 (11 Nov 2026)

Douglas, 10 Nov evening (`claude/plan-decision-2026-11-10.md`): "9-1 is too
high - reduce", to 4/1. On 11 Nov, after being shown the five-season bands
below, he confirmed: "Yes ... build and go".

## The evidence he was shown

Under-market football favourites, singles at the average price, by the
opposition's price (`claude/card-seasons-2026-11-09.md`):

| opposition | 2022-23 | 2023-24 | 2024-25 | 2025-26 | 2026-27 |
|---|---|---|---|---|---|
| 4-6 | -5.6% | -0.9% | -8.7% | -3.9% | -25.9% |
| 6-9 | +1.5% | -0.9% | +0.9% | -2.5% | -7.0% |
| 9+ | -3.5% | +4.0% | +7.3% | +7.5% | +3.7% |

So the new floor adds picks from the bands that lost (4-6) or broke even
(6-9). The five-season Edge numbers (singles +5.4%, doubles +4.6% at best)
describe 9+ only.

## What shipped

- `groupings.EDGE_OPP_MIN` 5.0 (4/1), the flag's own floor; `EDGE_RULE` 2.
  The Card keeps `CARD_OPP_MIN` 9.0 (rule 6): its rule is a delegated
  decision on the evidence and is not changed by this.
- `score.edge_of` carries `rule` (a flag published before rule 2 counts as
  rule 1); `edge_record` adds `byRule`, and the page quotes the current rule's
  line. Rows before 10 Nov are replayed under the current rule.
- `tools/card_legs_history.py` `edge_legs` reads `EDGE_OPP_MIN`, so the next
  weekly `tune.yml` run (and any `card-legs-history.yml` run) measures the
  Edge singles and accumulators at 4/1 on every season. That is the real test.
- The page says 4/1 wherever it said 9, and the Edge picks section states
  plainly that its five-season figures were at 9+ and that 4-9 did worse.

## What would reverse it

If the replay at 4/1 is under the 9+ line on both football-data seasons, or
the live `byRule["2"]` sits under its quote, say so to Douglas with the
numbers; the floor is his call.
