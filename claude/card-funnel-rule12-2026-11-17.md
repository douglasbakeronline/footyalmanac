# The Card funnel under rule 12 (17 Nov 2026)

Build session, 17 Nov 2026 03:17 London. No Card rule changed.

## What was wrong

Rule 12 (16 Nov 2026, `CARD_MODEL_OPP_MIN` `{"football": 5.0}`) added two
messages to `groupings.model_fault`, but `tools/card_funnel.py`, which the
nightly Card review prints, had no key for either:

- "no bookmaker price for the opposition" carries "no bookmaker price", so it
  was read as `no-price`, a key the rule 7 table has no column for: the leg
  vanished from the table.
- "the opposition is priced 4.50, under 5" matched nothing and fell to
  `other`.
- `price_gaps` stands an unpriced leg in at a price inside `CARD_ODDS` and asks
  whether it would otherwise qualify. The stand-in had no opposition price, so
  every unpriced football leg now failed on the opposition and the gap count
  fell from 46 (37 football, the 16 Nov review) to 3, with no football at all.
- The funnel read the pool's `opp` only, while the replay
  (`card_replay.pool_legs`) fills a missing one from the football archive
  (`archive_opp`, 16 Nov 2026).

## What changed

- `MODEL_PATTERNS` reads the opposition first; `MODEL_KEYS` has an
  `opposition` column; the relief `{"CARD_MODEL_OPP_MIN": {}}` joins the leg
  and days tables while the floor is live (`rule_sets`).
- `unpriced_ok` stands an unpriced leg's opposition in at the floor, so the
  gap count is again the most a fuller price feed could add.
- `pool_days` fills a football leg's missing opposition price from the
  archive, as the replay does (149 legs from 6 Nov; a test pool reads no disk).

## The read on the pool, 6 to 17 Nov (under rule 12, `--recover`)

| | before the fix | after |
|---|---|---|
| football legs clear | 32 | 44 |
| football faults shown as opposition | 0 (22 vanished, 21 "other") | 31 |
| legs kept off by the opposition alone | not read | 31 football |
| groups with no opposition condition | not read | 13 v 12 live (6 days of 15 either way) |
| price gaps from 10 Nov | 3 | 63 (39 on started days, 38 football) |

The opposition floor costs one group in fifteen days on the pool, against the
value demand's five (17 v 12). Volume only: whether those groups pay is the
replay's question (`m7noopp` against live).

Tests: `tests/test_card_funnel_model.py` (`OppositionRule12`,
`PoolOppositionFromArchive`), failing before the change.
