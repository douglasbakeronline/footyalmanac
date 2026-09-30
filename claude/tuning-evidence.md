# What the constants are actually worth — 9 September 2026

Method: walk-forward on 2025/26 (5,281 fixtures) to fit, 2026/27 to date
(545 fixtures) to check. Every comparison paired and bootstrapped, because an
unpaired comparison of two log losses around 1.016 has a noise band of ±0.005,
which is wider than every real effect in this model.

## Result of sweeping every constant

| Constant | Shipped | Best found | Δ log loss | Verdict |
|---|---|---|---|---|
| TEMPERATURE | 1.15 | 1.00–1.05 | −0.0012 | wrong *shape*, see below |
| RHO | −0.06 | −0.06 | 0.0000 | already optimal |
| BLEND_K | 6 | 8 | −0.0001 | already optimal |
| form window | 5 | 5 | −0.0001 | already optimal |
| home advantage scale | 1.0 | 0.9 | −0.0001 | already optimal |
| SHRINK_FULL_SEASON | 6 | 2–3 | −0.0016 | **evaporates after calibration** |
| FORM_MAX | 0.05 | 0.15–0.20 | −0.0013 | **evaporates after calibration** |

Total gain available from re-tuning all seven: about 0.3% of log loss. The
constants are not where the problem is.

## The one real finding: the model is under-confident at the top

Calibration on the fit season, shipped T = 1.15:

| Quoted band | n | Quoted | Landed |
|---|---|---|---|
| ≥70% | 170 | 76.0% | 84.7% |
| 62–70% | 287 | 65.3% | 72.1% |
| 55–62% | 567 | 58.0% | 64.7% |
| <55% | 4257 | 44.0% | 44.6% |

One temperature applies the same correction to a 40% call and an 85% one, and
those need opposite corrections. Replaced with `calibration.json`:
**T = 1.075 − 0.45 × (confidence − 0.45)**, fitted on 2025/26, checked on
2026/27 (−0.0017 log loss, p(worse) 0.195, all three gates passed).

Effect is on volume, not accuracy:

| | Shipped | Calibrated |
|---|---|---|
| Strong (≥70%) fixtures | 170 (3.2%) | 317 (6.0%) |
| Strong hit rate | 84.7% | 79.2% |
| Strong quoted vs landed | 76.0 vs 84.7 | 78.1 vs 79.2 |
| Fixtures at 55%+ | 1,024 | 1,321 |

Expected correct Strong calls per season: 144 → 251.

Tier labels in index.html updated to the recalibrated backtest: Strong 79%,
Firm 66%, Lean 61%, No read 44%. Headline figures now 5,281 fixtures,
49.5% correct, 43.7% baseline, top decile 75.0%.

## Tested and rejected

- **Separate home/away ratings per team** (roadmap item 5): clearly worse,
  +0.0124 log loss, p(worse) 1.00, confirmed on holdout. Halving the sample per
  rating costs more than the venue split adds. Remove from the roadmap.
- **Rest days** (roadmap item 4): no effect at any coefficient from −0.008 to
  +0.020. Δ 0.0000. Remove from the roadmap.
- **Ten free per-band temperatures**: fits better, generalises worse than the
  two-parameter line. Rejected in favour of the line.

## The trap worth remembering

SHRINK_FULL_SEASON and FORM_MAX both looked like real wins in isolation
(p(worse) 0.01 and 0.04). After the calibration curve went in, both fell to
Δ ≈ 0.0000 on the fit season. They were compensating for the miscalibration,
not adding information. Fit one thing, then re-test everything else.

## The machinery

`tune.py` — `--report` sweeps every constant, `--fit` refits calibration.json
behind three gates: ≥250 check-season fixtures, p(worse) ≤ 0.30, gain ≥ 0.0005.
Standard library only. `.github/workflows/tune.yml` runs it Mondays 04:40 UTC.
Calibration auto-applies when it passes; structural constants are advisory
output only and never move on their own.

Rules that keep it honest, in priority order:

1. Nothing is ever fitted on record.json. The live record is the scoreboard.
2. Every comparison is paired on the same fixtures and bootstrapped.
3. Anything fitted on the last completed season must survive on the current one.

## Still untested

The 74 league strength coefficients, which the roadmap calls the single largest
weakness. A league-only walk-forward cannot test them: within a league they
cancel out entirely. Testing them needs a cross-competition harness built on
European ties and cross-division cups. That is now the highest-value open item.


## Re-test, 29 September 2026: a form-led model

Douglas asked for the model to be led by this season's form after Needham
Market (a league not covered) won on form. Every setting was scored with the
calibration curve refitted for it, on 2025/26 (6,272 fixtures) and 2026/27
(789; ESPN-sourced leagues were not reachable from the cloud session).

| Setting | 2025/26 | 2026/27 | Verdict |
|---|---|---|---|
| FORM_MAX 0.10 | -0.0003, p 0.12 | -0.0006, p 0.17 | wash on fit |
| FORM_MAX 0.30 | +0.0011 | +0.0009 | worse |
| FORM_MAX 0.50 | +0.0050 | +0.0050 | worse |
| form 0.30, last 3 | +0.0029 | +0.0020 | worse |
| BLEND_K 3 (season takes over after 3 games) | +0.0017 | +0.0027 | worse |
| Form-led: shrink 2, blend 3, form 0.30 | +0.0049 | +0.0059 | worse |
| SHRINK_FULL_SEASON 3 | -0.0004, p 0.14 | -0.0009, p 0.23 | passes |
| **SHRINK_FULL_SEASON 4** | **-0.0004, p 0.04** | **-0.0007, p 0.18** | **shipped** |
| shrink 3 + form 0.10 | -0.0004, p 0.20 | -0.0009, p 0.29 | no better than shrink alone |

Heavy form weighting chases noise: a five-game run is mostly luck at these
goal rates. What holds up is letting this season's full record count sooner,
which is the honest version of "this season's form". calibration.json was fit
at shrink 6; Monday's tune.yml refits it on the full data.


## Re-test, 30 September 2026: table-position and goal-record penalties

Douglas asked for clubs in the bottom 10% of their table playing away, and
clubs substantially low for goals scored and high for goals conceded
(z <= -1 and z >= +1 against their league), to be weighted to lose. Tested as
multipliers on the flagged side's expected goals (and the inverse on the
opponent's), calibration refitted per setting, both seasons.

| Setting | Flagged (fit / check) | 2025/26 | 2026/27 |
|---|---|---|---|
| bottom-10% away x0.90 | 495 / 34 | +0.0010, p(worse) 0.98 | +0.0017, 0.94 |
| bottom-10% away x0.80 | | +0.0030, 1.00 | +0.0047, 0.99 |
| bottom-10% away x0.70 | | +0.0053, 1.00 | +0.0083, 1.00 |
| weak attack and defence x0.90 | 447 / 27 | +0.0009, 0.98 | +0.0019, 0.98 |
| weak attack and defence x0.80 | | +0.0029, 1.00 | +0.0048, 1.00 |
| both x0.85 | | +0.0036, 1.00 | +0.0062, 1.00 |

Worse at every strength. The ratings are built from goals scored and
conceded, so these sides are already priced to lose; a second penalty counts
the same evidence twice. Rejected.
