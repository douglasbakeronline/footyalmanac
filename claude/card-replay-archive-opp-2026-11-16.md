# The pool replay's missing opposition prices (16 Nov 2026)

Build session, 16 Nov 2026 (15:17 London).

## What was wrong

The pool archive (`groupings-archive/pool-<date>.json.gz`) kept no
opposition price for football legs until `opp` joined its keys on 6 Nov.
Every football pool leg from 30 Oct to 9 Nov that was priced but carried no
`opp` (382 of them) faulted in any variant with an opposition condition:
`card_fault` and `model_fault` both return "no bookmaker price for the
opposition" when `opp` is empty. So `rule6` and its family (`opp7`,
`uncapped` and the rest that keep `CARD_OPP_MIN`) and the rule 7+ variants
`m7opp5` and `m7opp9` (`CARD_MODEL_OPP_MIN`) were starved on those days by
missing data, not by their rule, and the nightly review read them on fewer
days than live. The `m7opp` note (`claude/card-m7opp-2026-11-15.md`) said so
in passing ("pool legs archived before 6 Nov carry no opposition price");
nothing filled the gap.

## The fix

The football archive (`predictions/<date>.json`) holds `market.avg`, the
API-Football average 1X2 prices, on every row the build priced, written when
the row was published. `tools/card_replay.py` now builds an index of those
(rows published before their kick-off only, the latest such copy standing,
`archive_opp_index`) and gives a football pool leg with no `opp` the other
side's average and the draw's (`archive_opp`), marked `oppFrom: "archive"`.
A leg's own price, bookmakers' chance and result are unchanged; only the
opposition's price is added. The count shows in the replay's source line and
in the nightly review ("opposition price from the football archive: N legs"),
apart from the legs left out. A synthetic pool in a test reads no
predictions/ (`pred_dir` defaults to predictions/ only for the live pool).

How close is the archive's price to the pool's own? On the 246 football pool
legs that carry both, the median difference is 0 (10th to 90th percentile
-14% to +29%, the archive's copy being a different moment's price) and the
two agree on both the 5.0 and the 9.0 line 91% of the time. Approximate, as
`--recover` is, but a real pre-start bookmaker price, not an estimate.

381 of the 382 legs matched an archive row on league, date and names; 362
of them are settled and enter the replay.

## What it changes (`tools/card_replay.py --since 2026-10-29`, the review's window)

| variant | before: groups, legs, return, p(worse) v live | after |
|---|---|---|
| live | 12, 36, -25% | unchanged |
| m7opp5 | 4, 12, -42%, 0.24 | 11, 33, +2%, 0.00 |
| m7opp9 | 2, 6, +27%, 0.11 | unchanged |
| uncapped | 3, 9, +50%, 0.07 | 4, 12, +62%, 0.03 |

Whole window, archive rows from 11 Sep plus the pool: `m7opp5` 13 groups on
39 legs (7 won, +38%, p(worse) 0.03) becomes 20 groups on 60 legs (11 won,
+34%, p(worse) 0.00, +1.11 units a day v live). The rule 6
family is otherwise unchanged: its other conditions (core leagues, the
under-market cut) keep the same legs off.

## What it does not change

No Card rule. `m7opp5` is still under the gate's 100 legs on the pool side
(33 in the review's window, 60 over the whole archive), so the pre-registered
action in `claude/card-m7opp-2026-11-15.md` (set `CARD_MODEL_OPP_MIN`
football 5.0 live when both sides pass) is not reached. The football-data
side, from Monday's `tune.yml` (16 Nov, two seasons): `m7opp5` ahead in both,
pooled 123 legs, p(worse) 0.244. When the pool side reaches 100 legs at
p(worse) 0.30 or under, the next session acts without asking. The
funnel (`tools/card_funnel.py`) reads `pool_market` directly and is not
changed: no live condition reads the opposition under rule 11.

## Files

`tools/card_replay.py` (`PRED_DIR`, `archive_opp_index`, `archive_opp`,
`pool_legs`), `tools/card_review_post.py` (the source line),
`tests/test_card_pool_replay.py` (two tests).
