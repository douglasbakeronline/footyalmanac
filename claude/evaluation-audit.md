# Football evaluation infrastructure audit — 2 October 2026

Branch `audit/eval-infrastructure`. Triggered by an external audit (Julius,
1 Oct 2026; bundle in `football_accuracy_audit/`, gitignored, never
committed). Every finding was re-checked on our own sources and caches, not
the audit's snapshot. No model constant, calibration file, odds input or page
change. Nothing here is merged or deployed by this branch.

## What is and is not shared with the live build

**Shared (one implementation, tested equal):** the per-fixture rating and
pricing step. Given a prior season and the earlier results of the current
season, `replay.replay_league` computes ratings with `strength_from_table`
(this season's goal rate), `blend`, `form_points` / `form_factor` and
`expected_goals`, the same engine functions `build.py` calls, and
`probabilities_from_xg` is the grid `match_probabilities` uses. A test
rebuilds one prediction the way `build.py` does and matches it to 12 dp;
`tune.py` and `backtest.py` agree to 7e-16.

**Not replayed (live-only, so not full pipeline parity):**

- promoted and relegated sides: live transfers the rating from the old
  division (`transfer_rating`); the replay starts them at 1.00 / 1.00;
- partial priors: live picks a complete older season and blends a partial
  newer one (`pick_prior`, `blend_prior_seasons`); the replay uses the prior
  season as given;
- cup ties (`cup_match`, league strengths, `europe.json`);
- internationals, youth sides and the FIFA ranking adjustment;
- absences / adjustments (both empty by rule), Celtic's Law flags, list
  selection and tiers.

Backtest and tuning numbers therefore describe the league model's core, not
every row the site publishes.

## Findings, reproduced

**1. Prior/test overlaps and mis-dated seasons.** On our sources (frozen
snapshot `aa19d05b...`):

| Competition | Problem | Cause |
|---|---|---|
| en.3 | 2025-26 file holds 85 matches dated Jan-Feb 2025 (42 repeat 2024-25 fixtures); season stops in December | corrupt upstream (openfootball) |
| mx.1 | 2025-26 file ends 1 Aug 2026; 21 matches also in `current/` 2026-27 | backfill window ran to 31 July; Liga MX started 17 July |
| ru.1 | ends 31 Jul 2026; 9 duplicates | same; RPL started 24 July |
| dnk.1 | ends 27 Jul 2026; 6 duplicates; also starts 1 Jun 2025 with the 2024-25 European play-off | same, at both ends |
| arm.1, hun.1, nir.1, ukr.1, wal.1 | 2024-25 files hold rows dated 2026 (1 to 101 each) | corrupt years upstream |

**2. Two calculations.** `tune.py` normalised this season by last season's
goal rate; `backtest.py` and the live build by this season's. `tune.py` fits
`calibration.json`.

**3. Same-day updates.** Both harnesses updated after each fixture in file
order; the data holds dates only.

**4. Publish time (found here).** Every push to main deploys; a mid-day
build re-priced games in play and overwrote the day's archive, which
`score.py` grades. Archived rows carried no publish or kick-off time.

## What changed

- `replay.py` (new): `replay_league` (shared, date-batched);
  `validate_split` refuses missing seasons, prior/test overlaps, and rows
  outside a season's calendar window (`season_window`: calendar year, or
  1 June to 31 July for split-year; labels it cannot parse are not checked);
  `coverage` / `report_exclusions`; `--audit`, `--freeze`, `--snapshot`,
  `--include-current` (advisory).
- `engine.py`: `match_probabilities` = `expected_goals` +
  `probabilities_from_xg` (bit-identical, golden test); `venue_multipliers`;
  `form_factor(cap=)`.
- `tune.py`: `lambdas` uses the replay (same signature and outputs);
  private `_strength` / `_form` removed; `exclusions()`; exclusions printed
  and recorded in `tuning-report.json`.
- `backtest.py`: `evaluate` uses the replay and validation; rows carry teams.
- `build.py`: `drop_current_from_prior` (identical matches in both seasons
  removed from the prior, loudly); `archive_predictions` merges into the
  day's file; once a fixture's start has passed (its known kick-off, or the
  earliest instant of its date when the kick-off is unknown) it keeps the
  price archived before it and accepts no new entry; corrects the kick-off
  if it moved; stamps `kickoff` and `published`. Comparisons are
  timezone-aware (`sources.parse_utc`); a time with no zone counts as unknown.
- `score.py`: `verification()` per row, five categories:

  | Category | Rule | Graded |
  |---|---|---|
  | `verified` | published before a known kick-off | yes |
  | `verified-by-date` | no usable kick-off; published before the date's earliest instant | yes |
  | `legacy-unverified` | no publish time (archived before 2 Oct 2026) | yes, as before, labelled |
  | `late` | a known kick-off proves it was published at or after kick-off | no, counted |
  | `timing-unverifiable` | no usable kick-off, and published at or after the date's earliest instant, so lateness can be neither proved nor ruled out | no, counted |

  A row with a publish time is never legacy. `late` is evidence of a late
  price; `timing-unverifiable` is only the absence of evidence that it was
  early, so the two are counted apart (`record.json` `verification.late`
  and `verification.timingUnverifiable`) and both kept out of verified
  grading. `record.json` also gains verification counts overall and for the
  Daily List. Historical prices are never rewritten.
- `sources.py`: `parse_utc`, `earliest_start`.
- `backfill.py`: `SEASON_BOUNDS` sets 1 July to 30 June for mx.1, ru.1 and
  dnk.1 only, from the evidence below; every walk also stops the day before
  the next season's first cached result (`clip_to_next_season`).
- `tools/capture_predictions.py`, `tools/compare_predictions.py`:
  reproducible before/after on a frozen snapshot.
- `tests/`: 37 tests. Numeric golden outputs compared to 1e-12 (CPython
  builds differ by one ulp in exp/pow: 1.1e-16 seen on 3.13), discrete
  outputs exact, golden values not regenerated.
- `.github/workflows/tests.yml`: tests and `nametest.py` on Python 3.12 and
  3.13 for every pull request and non-main push. Tests only, no deploy.

## Fixture-date convention

A fixture's `date` is the calendar date its source gives, with no zone
guaranteed (openfootball local, ESPN UTC). With no kick-off time it is read
as the first instant that date exists anywhere: 00:00 at UTC+14, i.e.
10:00 UTC the day before (`sources.earliest_start`). A price counts as
published before kick-off only if it came before that. Conservative by
design: it can refuse an honest price, never pass a late one. Review case:
fixture dated 2026-10-01, no kick-off, archived 2026-10-02T12:00Z: refused
by the archive, and `timing-unverifiable` (not graded) if such a row exists.
The same row with a known kick-off of 2026-10-01T19:00Z would be `late`.

## Season-boundary evidence for the backfill cutoff

| Code | 2025-26 real end | 2026-27 starts | Gap | 30 Jun inside gap | 31 Jul inside gap |
|---|---|---|---|---|---|
| mx.1 | 2026-05-25 | 2026-07-17 | 53 d | yes | no |
| ru.1 | 2026-05-17 | 2026-07-24 | 68 d | yes | no |
| dnk.1 | 2026-05-21 | 2026-07-24 | 64 d | yes | no |
| nl.2 | 2026-04-24 | 2026-08-07 | 105 d | yes | yes |
| sa.1 | 2026-05-21 | 2026-08-13 | 84 d | yes | yes |
| sco.2 | 2026-05-01 | 2026-08-01 | 92 d | yes | yes |
| au.1, in.1 | May 2026 | no data yet | | unverified | unverified |

Only the three failing competitions get tighter bounds; the rest keep the
default window, and the next-season clip guards all of them.

## Archive verification today

40 files (20 Aug to 2 Oct 2026), 11,874 rows: all `legacy-unverified`
(archived before times were recorded). They stay graded as before,
labelled as such, prices untouched.

## Before / after on identical fixtures (snapshot aa19d05b...)

| | Fit 2025/26, 6,474 | Check 2026/27, 1,386 |
|---|---|---|
| old tune.py | 1.02402, 48.53% | 1.02630, 48.34% |
| old backtest.py | 1.02398, 48.58% | 1.02568, 48.20% |
| new (both) | 1.02395, 48.56% | 1.02564, 48.20% |

Old tune vs old backtest: 6,202 of 6,474 fit fixtures differ (max 0.067);
1,245 of 1,386 check (max 0.101). Date batching alone: 4,077 / 800 fixtures
change, mean 0.0007, max 0.016, top pick changes on 3. Excluded by the new
checks: en.3 and mx.1 (fit).

Reproduce:

```
python3 replay.py --freeze audit-out/snapshot.json
git worktree add /tmp/fa-main main
python3 tools/capture_predictions.py --code-dir /tmp/fa-main --snapshot audit-out/snapshot.json --out audit-out/before.json
python3 tools/capture_predictions.py --code-dir . --snapshot audit-out/snapshot.json --out audit-out/after.json
python3 tools/compare_predictions.py audit-out/before.json audit-out/after.json
python3 replay.py --audit --snapshot audit-out/snapshot.json
python3 -m unittest discover -s tests -v
```

A fresh freeze fetches today's sources, so its numbers can differ from these;
the snapshot hash says which data a result belongs to.

## Openfootball-only snapshot

The full snapshot mixes four sources. openfootball is public domain; ESPN
and football-data.co.uk carry no redistribution licence. For independent
reproduction on shareable data, `replay.py --filter-snapshot` derives an
openfootball-only copy: it keeps seasons read from openfootball, drops every
other season and the whole `current/` cache, records each dropped season and
its source, and carries the parent's content hash.

| | Content sha256 | File sha256 |
|---|---|---|
| full | `aa19d05b33faf7e5044a78bd5e6cfe13938a4475793e570d66a43b46dd6e7bda` | `20bd6a430450c55fb3d178f230209405d85d5fbca4c7a22b033dd7d5c5d602bb` |
| openfootball-only | `cc08a335d3ace77aeba601c713d57349b47944236e0902f058afe75017b80f34` | `9b9d46165eb7bdf677bb4a1386a7ad5f3586f84e90700614eb2dd37713598153` |

The content hash covers the data (verified on every load); the file hash is
of the JSON as written (1,095,724 bytes) and also covers its creation time.

**Seasons dropped (69):**

- ESPN backfill (`history/`), 14 seasons, 4,027 matches: au.1, dnk.1,
  in.1, mx.1, nl.2, ru.1, sa.1, sco.2 (2025-26); cl.1, ec.1, pe.1, us.1,
  us.2, uy.1 (2025).
- football-data.co.uk, 15 seasons, 2,931 matches: ch.1, pol.1, rou.1
  (2024-25, 2025-26, 2026-27); fin.1, irl.1 (2024, 2025, 2026).
- ESPN `current/` cache, 40 seasons, 5,472 matches. `tune.py` and
  `backtest.py` never read it, so dropping it changes no harness result; it
  matters only for `--include-current`.

**Competitions and fixtures lost against the full snapshot:**

| Split | Full | Openfootball-only | Lost |
|---|---|---|---|
| fit (2024-25 -> 2025-26) | 35 / 6,474 | 28 / 4,899 | au.1 163, dnk.1 200 (ESPN test season); ch.1 228, fin.1 177, irl.1 180, pol.1 306, rou.1 321 (football-data) = 7 / 1,575 |
| check (2025-26 -> 2026-27) | 17 / 1,386 | 12 / 866 | ch.1 54, fin.1 150, irl.1 159, pol.1 78, rou.1 79 (football-data) = 5 / 520 |

Excluded in both snapshots by validation: en.3 (corrupt 2025-26, fit and
check), arm.1, hun.1, nir.1, ukr.1, wal.1 (2024-25 rows dated 2026) and, in
the full snapshot, mx.1 fit (2026-27 rows in 2025-26; in the
openfootball-only copy its 2025-26 season is simply absent). Full lists:
`python3 replay.py --audit --snapshot audit-out/snapshot-openfootball.json`.

**Before / after on identical fixtures:**

| | Fit, 4,899 | Check, 866 |
|---|---|---|
| old tune.py | 1.01489, 49.42%, Brier 0.60778 | 1.02455, 48.04%, 0.61489 |
| old backtest.py | 1.01454, 49.50%, 0.60756 | 1.02429, 48.27%, 0.61478 |
| new (both) | 1.01450, 49.48%, 0.60754 | 1.02431, 48.15%, 0.61479 |

New tune.py and backtest.py agree to 6.7e-16 (fit) and 5.6e-16 (check). Old
tune minus old backtest: +0.00035 [-0.00040, +0.00103] fit, +0.00026
[-0.00115, +0.00170] check. Date batching alone moves 3,248 / 507 fixtures,
mean 0.0007, max 0.016, top pick changes on 1 in each split. Newly excluded:
en.3 (fit). The lower log loss than the full snapshot is the competition
mix (the dropped leagues are harder), not a model difference; compare
numbers only within one snapshot.

Reproduce:

```
python3 replay.py --filter-snapshot audit-out/snapshot.json audit-out/snapshot-openfootball.json
python3 tools/capture_predictions.py --code-dir /tmp/fa-main --snapshot audit-out/snapshot-openfootball.json --out audit-out/of-before.json
python3 tools/capture_predictions.py --code-dir . --snapshot audit-out/snapshot-openfootball.json --out audit-out/of-after.json
python3 tools/compare_predictions.py audit-out/of-before.json audit-out/of-after.json
```

Anyone holding only the openfootball-only file can start at the second
line: `load_snapshot` checks its content hash, and `compare_predictions.py`
refuses captures from different snapshots.

## Follow-ups

Separate proposals, not implemented: `claude/proposals/regenerate-history.md`,
`claude/proposals/league-one-prior.md`, `claude/proposals/cache-expansion.md`.
