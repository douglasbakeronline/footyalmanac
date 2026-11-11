# The Card funnel under rule 8 (11 Nov 2026)

Build session, 11 Nov 2026 (04:30 UTC). Advisory: nothing here changes a rule.

## What was wrong

`tools/card_funnel.py` (10 Nov, #155) maps each leg's first failing condition
to a key by matching `card_fault`'s messages. From CARD_RULE 7 (the model's
own picks, `model_fault`) the messages changed, and the funnel kept rule 6's
patterns, reliefs and both kinds. Tonight's nightly Card review would have
said, on the pool from 6 Nov:

- football: 337 legs "price-range", 79 "other". In fact 217 were outside the
  core leagues and 120 outside 1.15-1.90; the "other" were model-floor and
  no-value faults.
- reliefs for the under-market band and the opposition's price, which are no
  longer conditions, and a Card 3x column for a kind the Card no longer
  builds (CARD_RULE 8).
- a "first group" count per day, when the Card now takes up to three 2x.

`tools/card_integrity.py` would also have raised `no-opposition-price` on any
rule 7 football leg without an opposition price, which opens an
`office-backlog` issue for a condition the rule no longer reads.

## The fix

- The funnel reads whichever rule is live: under rule 7 its own keys
  (`MODEL_PATTERNS`: sport-off, no-time, no-price, league, list-excluded,
  price-range, sport-floor, model-floor, no-value) and reliefs (`MODEL_RELIEF`:
  wider price range, no tennis floor, model floor 55%, the model up to 5
  points under the bookmakers, three legs a competition). The league limit is
  hard-coded in `model_fault`, so it has a key and no relief.
- Only the kinds the Card builds (`built_kinds`), and the days table counts
  every group a day can take, in `build_card`'s order, beside days with one.
- `card_integrity.needs_opp`: the opposition check applies to rule 6
  full-rule groups only.
- Tests: `tests/test_card_funnel_model.py` (every `model_fault` branch, the
  live kinds, three 2x from nine legs, the opposition check by rule). The
  rule 6 tests are unchanged.

## The read (pool 6 to 14 Nov, 9 days, 783 legs at a real price, 559 estimate only left out)

| rule | days with a 2x | groups |
|---|---|---|
| live (rule 8) | 3 | 4 |
| no price-range condition | 3 | 4 |
| no tennis floor | 3 | 5 |
| model floor 55% | 3 | 4 |
| model up to 5 points under | 4 | 8 |
| three legs a competition | 3 | 4 |

Football's faults: 217 outside the core leagues, 120 price, 59 model under
60%, 20 no value; 13 clear. Legs kept off by one condition alone: the value
demand 14 football, 7 NBA, 2 tennis; the tennis floor 7. Days from 11 Nov are
not fully priced yet.

## Does the extra volume pay? No

The value demand is the one condition that costs groups, so its relief was
pre-registered as `m7under5` in `tools/card_replay.py` (`CARD_MODEL_EDGE`
-0.05) before reading the result. On the pool and archive (13 days of
settled legs):

- live: 6 groups, 4 won v 38% expected, +82%, legs 16 of 18 v 66.8% quoted
- m7under5: 14 groups, 6 won v 37% expected, +0%, legs 32 of 42 v 69.9%
- paired by day: -0.98 units a day, p(worse) 0.97

The picks the model rates under the bookmakers dilute the Card. The value
demand stays; `m7under5` is replayed nightly with the other variants. On 42
legs this is a read, not a gate.
