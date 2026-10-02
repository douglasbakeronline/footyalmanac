# Football evaluation infrastructure audit — 2 October 2026

Branch `audit/eval-infrastructure`. Triggered by an external audit (Julius,
1 Oct 2026, bundle in `football_accuracy_audit/`, not committed). Every
finding was re-checked on our own sources and caches rather than the audit's
snapshot. No model constant, calibration file, odds input or page change.

## Findings, reproduced

**1. Prior/test overlaps.** On our sources (`tune.load`):

| Competition | Split | What overlaps | Cause |
|---|---|---|---|
| en.3 | fit (2024-25 -> 2025-26) | 85 matches dated Jan-Feb 2025 in openfootball's 2025-26 League One file; 42 repeat 2024-25 fixtures | corrupt upstream file (season also stops in December) |
| mx.1 | live build | `history/mx.1-2025-26.json` ends 1 Aug 2026; 21 matches also in `current/` | `backfill.season_window` ran split-year seasons to 31 July; Liga MX started 17 July |
| ru.1 | live build | ends 31 Jul 2026; 9 duplicates | same (RPL started 24 July) |
| dnk.1 | live build | ends 27 Jul 2026; 6 duplicates | same (Superliga started 24 July) |

The audit saw mx.1/ru.1/dnk.1 in its check split because it read `current/`
directly. Our harness never reads `current/` (see open question 1), so those
three were silently missing from our check season instead. In the live build
the duplicates were counted twice (prior and current season).

**2. Two calculations.** `tune.py` normalised this season's ratings by last
season's goal rate (`_strength(tbl, mu, ...)` with the prior `mu`);
`backtest.py` and the live build use this season's (`strength_from_table`).
`tune.py` fits `calibration.json`, which the live build applies. On 8,218
identical fixtures the two harnesses differed on 7,797 (mean 0.011, largest
0.101 probability; top pick different on 48).

**3. Same-day updates.** Both harnesses updated after each fixture in file
order; the data holds dates only. Date batching changes 5,109 of 8,218
fixtures, by 0.0007 on average (largest 0.016); top pick changes on 3.

**Also found:** the live build re-priced games already in play on any
mid-day rebuild (every push to main deploys) and overwrote that day's
archive file, which score.py grades; a fixture finished since the morning
also vanished from the day's file, so the previous day's price was graded.
Archived rows had no kick-off or publish time to check against.

## What changed

- `replay.py` (new): `replay_league`, the one walk-forward used by
  `backtest.py` and `tune.py`, built from the live build's engine functions
  and batched by date; `validate_split` / `coverage` / `report_exclusions`,
  which refuse overlapping or missing seasons and say why;
  `python3 replay.py --audit`.
- `engine.py`: `match_probabilities` = `expected_goals` +
  `probabilities_from_xg` (bit-identical, golden test); `venue_multipliers`;
  `form_factor(cap=)`.
- `tune.py`: `lambdas` uses the replay (same outputs and signature for
  `odds.py` / `predictability.py`); private `_strength` / `_form` removed;
  `exclusions()`; exclusions printed and written to `tuning-report.json`.
- `backtest.py`: `evaluate` uses the replay, reports exclusions, rows carry
  home/away.
- `build.py`: `drop_current_from_prior` removes matches present in both the
  prior and the current season, loudly; `archive_predictions` merges into the
  day's file, never replaces a price for a fixture that has kicked off (or
  archives a first price after kick-off), keeps the day's first price for a
  date-only fixture, and stamps `kickoff` and `published`.
- `score.py`: skips a prediction published at or after its kick-off (older
  rows without the fields are graded as before).
- `backfill.py`: split-year window ends 30 June.
- `tests/test_evaluation.py` + `tests/golden_match_probabilities.json`:
  17 tests. `python3 -m unittest discover -s tests -v`.

## Before / after on identical fixtures (same data snapshot)

| | Fit 2025/26, 6,832 | Check 2026/27, 1,386 |
|---|---|---|
| old tune.py | 1.02364, 48.70% | 1.02630, 48.34% |
| old backtest.py | 1.02365, 48.76% | 1.02568, 48.20% |
| new (both) | 1.02362, 48.74% | 1.02564, 48.20% |

New tune and backtest agree to 7e-16. Old tune minus old backtest on check:
+0.00063 (95% [-0.0016, +0.0030]). Date batching alone: -0.00002 (fit),
-0.00004 (check), inside noise. en.3 (356 fit fixtures) is now excluded.

Accuracy barely moves; the point is that the number tuning fits, the number
the backtest reports and the number the site publishes are now one
calculation, and no evaluation can see a result from its own match day.

## Coverage the harness can use (from `replay.py --audit`)

Fit: 36 competitions, 6,832 fixtures, 84 excluded. Check: 17 competitions,
1,386 fixtures, 103 excluded. Excluded for missing data: every international
and women's competition, most ESPN-only leagues (no 2024/25 prior), and every
league whose 2026-27 season exists only in `current/`.

## Open questions

1. **The check season covers 17 competitions.** `tune.load` reads
   history/openfootball/FDX/AF, never `current/`, so 36 leagues with a live
   current season (en.3, en.4, es.2, de.2, tr.1, mx.1, the Nordics...) are not
   in the calibration check. Reading `current/` would widen it a lot, but
   changes what calibration is fitted and judged on; worth a separate,
   gated change.
2. **Should the four affected history files be repaired?** The build now
   drops the duplicates at run time; the files still hold them.
   Re-walking mx.1/ru.1/dnk.1 2025-26 with the fixed window would make the
   data itself clean.
3. **en.3 2025-26** is corrupt upstream. It still feeds the live League One
   prior (via `pick_prior`, as a partial season). Exclude it there too, or
   take League One history from ESPN/AF?
4. **The replay is not the whole live build.** Promoted sides (live:
   transfer from their old division; replay: neutral 1.00), partial priors,
   cups, internationals and the FIFA adjustment are live-only. The per-fixture
   rating and pricing step is shared; prior construction is not.
5. **The existing calibration** was fitted on the old tune calculation. The
   next Monday refit (tune.yml) will fit on the corrected one; the gates
   decide whether it ships.
