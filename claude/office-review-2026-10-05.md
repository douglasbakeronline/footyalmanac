# Office review, 5 Oct 2026 (Luke, Chief of Staff)

Covers `RELEASES.md` since 21 Sep and the `claude/` notes dated 4-5 Oct. Record
numbers are read only, never fitted (Rule 1).

## What the office shipped
- **Odds tab** (4 Oct): five-leg groups, daily archive and record. 5 Oct: ESPN
  soccer prices cover 12 of 24 football legs API-Football left unpriced; the
  group rules were backtested and left alone.
- **Evaluation layer and merge gate** (3-4 Oct): independent paired evaluation
  of every PR; model changes cannot ship without a pass.
- **Source resilience**: openfootball and football-data.co.uk retry, outages no
  longer cached as "no data"; API allowance exhaustion now stops calls
  (release-2026-10-05-14) after the 5 Oct build ran 3 hours instead of 7 minutes.
- **Data quality**: Turkish Super Lig was fed twice (`tr.1` and `af.203`); fixed
  and guarded in `nametest.py`.
- **Calibration bands tool** (`calibration_bands.py`) and tests for `sports.py`
  (one Elo fix).

## What it learned, including rejected tests
- Daily List bar 80% stays: 80%+ landed 81.9% of 94 (2025/26); lowering to 75%
  adds 95 picks at about 77%, difference inside noise; 85%+ landed 69.2% of 39.
- Championship: carrying promoted/relegated ratings is worse than a neutral
  start in all three seasons (+0.0040, +0.0018, +0.0088 log loss). Held, the
  2026-27 sample is under the 250 gate.
- Premier League lower home tilt: gain 0.0007, p(worse) 0.36 over the 0.30 limit.
- Ratings carry-over and a new-side prior: not shipped (calculation mismatch).
- Tennis thin-history shrink: best gain 0.0012 against a 0.005 gate. Rejected.
- No free source exists for Croatia, Serbia, Ukraine, Hungary, Korea.

## Where accuracy stands (`record.json`, read only)
| Group | n | landed | expected |
|---|---|---|---|
| Football, all graded | 734 | 51.9% | n/a |
| Football Strong | 48 | 79.2% | 79.4% |
| Football Firm | 50 | 70.0% | 69.7% |
| Football Lean | 84 | 65.5% | 59.2% |
| Football Daily List | 22 | 72.7% | 80% bar |
| Football reserve | 15 | 60.0% | Firm 62%+ |
| Celtic's Law rows | 163 | 47.9% | n/a |
| Sports Daily List | 14 | 85.7% | 80.6% |
| Sports overall | 52 | 65.4% | 63.2% |
| Tennis overall | 294 | 57.5% | 61.3% |
| Tennis Daily List | 16 | 93.8% | 83.3% |

Tiers are calibrated; the football Daily List is below its 80% bar on 22 picks
(16 of 22), too few to call it either way. Tennis is under by 3.8 points,
concentrated in the WTA (54.5% v 60.6% quoted, n 176). Baseball is
over-confident out of sample (62%+: 65.8% quoted, 61.0% landed, n 608).
Football's 85%+ tail is over-confident (89% quoted, 70% landed, in-sample, 40).

## Data quality
- Verification: only 145 of 734 football picks are `verified`; 589 are
  `legacy-unverified` (published before the archive timing fix). Tennis has 45
  published late. These are counted apart, not hidden.
- 5 Oct's Daily List was built with little football data after the API-Football
  allowance ran out; the fix is live but unproven over a full day.
- Check seasons are thin (2026-27: 50 to 95 fixtures per test), which is why
  several tests are held, not rejected. Samples grow weekly.

## Three priorities for next week
1. **Raj (source)**: confirm the allowance guard and the 00:10 UTC build hold
   over a full week: no day with an empty or partial football board, build
   under 15 minutes. Then API-Football ids for the five uncovered top flights,
   replayed before any list place.
2. **Andrew (calib)**: rerun `calibration_bands.py` in CI with full sources,
   and write up (not apply) a baseball calibration guard and the 85% tail
   display cap for Douglas.
3. **Mia (experiment)**: retest the held items (Championship newcomers,
   Premier League home tilt) once 2026-27 check fixtures pass 250, on the
   existing gates; no change before that.
