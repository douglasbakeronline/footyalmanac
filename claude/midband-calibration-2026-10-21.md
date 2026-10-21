# Do 60-80% calls land more often than quoted? (21 Oct 2026)

Douglas's question: games around 60-80% seem to come in more often than the
model says. Tested on every graded football win pick in `record-graded.json`
(5,713, 21 Aug to 21 Oct 2026) with `tools/midband_calibration.py`.
Advisory: rule 1, nothing here is fitted.

## A grading trap first

`score.py`'s `ok` also counts a "draw read" as correct. On that measure 35-40%
calls "landed" 69%. For anything bet as a win (the Odds tab, a reader's
single) the test is strictly "the pick won". All figures below use that.

## Overall: on quote

| Band | n | Landed | Quoted |
|---|---|---|---|
| 60-65% | 352 | 65.3% | 62.2% |
| 65-70% | 226 | 66.8% | 67.4% |
| 70-75% | 133 | 72.2% | 72.2% |
| 75-80% | 72 | 80.6% | 77.3% |

All 60-80%: 68.3% landed against 66.8% quoted (z +0.9). Across the whole
slate the model is not under-selling these games.

## Where it is: the core leagues

| 60-80%, by family | n | Landed | Quoted | z |
|---|---|---|---|---|
| Core leagues (openfootball / ESPN top flights) | 173 | 75.7% | 66.2% | +2.7 |
| Wider API-Football leagues (227) | 460 | 65.9% | 66.9% | -0.5 |
| Internationals | 55 | 63.6% | 68.9% | -0.9 |
| European and cup ties | 25 | 56.0% | 67.4% | -1.2 |

Inside the core leagues the gap sits at 65-75%: 65-70% landed 84.6% of 52
(quoted 67.4%), 70-75% landed 90.3% of 31 (quoted 72.3%). 60-65% is on quote.
It holds in both halves of the record (to 4 Oct 77.5% of 80, since 5 Oct
74.2% of 93) and in most top flights (Portugal, Spain, England, Brazil,
Italy), not in the Eredivisie (7 of 14) or the Bundesliga (7 of 12).

It agrees with the build's own 2026/27 check bands (`build.ACCURACY_BANDS`
league "check": 60-65% landed 74.6% v 67.6%, 65-70% 77.7% v 71.5%), and
disagrees with the 2025/26 fit season, where the same bands are on quote.
So it looks like a this-season effect in the core leagues, not a fault in
the calibration line.

Also seen, smaller: Celtic's Law flagged 60-80% calls land under quote
(64.5% v 66.9%), clean ones over (69.5% v 66.7%). The Odds tab now keeps
flagged fixtures out of groups.

## What it means and what it does not

- The groups gate stays at 75% on the model's own number. Lowering it for
  core leagues on the strength of the scoreboard would break rule 1.
- The likely cause is early-season shrinkage holding strong core-league
  sides close to last season's ratings while they pull away, or a single
  calibration line that the wider leagues (most of the volume) dominate.
  Neither is tested.

## Next step

Test on the walk-forward replay, which rule 1 allows: `replay.py` on 2026/27
for the core leagues only, 65-75% band, landed against quoted, paired
against the live curve. If it confirms, the candidate fix is a second
calibration curve for the core leagues (as the cups have one), fitted on
2025/26 and gated on 2026/27. Because 2025/26 looks calibrated, expect it to
fail rule 3; if so, the honest change is shrinkage by stage of season, which
was tested on 19 Oct without the league split.
