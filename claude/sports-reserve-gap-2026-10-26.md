# Other-sports reserve below its quotes, 26 Oct 2026 (Nina) - no change shipped

HQ planner (25 Oct): other-sports reserve, last 28 days, 66 of 103 landed
(64%) v 74.0 expected (72% quoted), z -1.8. Live record used only to locate
the gap (Rule 1); nothing fitted on it.

## Where the gap is (sports-record.json, 13-26 Oct, 113 settled reserve picks)

| Sport | n | Landed | Quoted | Short by |
|---|---|---|---|---|
| College football | 68 | 63.2% | 73.7% | 7.1 games |
| NFL | 15 | 46.7% | 68.5% | 3.3 |
| NBA | 20 | 80.0% | 68.7% | +2.3 |
| Rugby | 8 | 62.5% | 68.2% | 0.5 |
| WNBA | 2 | 50% | 66.0% | 0.3 |
| All | 113 | 63.7% | 71.6% | 8.9 |

College football and NFL carry all of it (College football's Firm 62-70% picks: 11 of 22 against 65.7%
quoted; NFL Firm 4 of 9, Strong 3 of 6). NBA and rugby are on or above quote.

## What the history says (sports.json bandsCheck / bandsFit, never tuned on)

- College football, check window (1,097 games): calls at 60%+ landed 78.1%
  v 75.5% quoted, 65%+ 82.1% v 78.2%. Fit window: 74.3% v 74.9%, 76.1% v 77.1%.
  On history the reserve band is on or above quote in both windows. The live
  shortfall (63% on 68, nearly all inside 3 weeks) is not seen there.
- NFL, check (332 games): 60%+ landed 69.5% v 71.8%, 65%+ 71.0% v 75.1%
  (over-confident); fit window the opposite (74.0% v 70.8%, 74.8% v 74.5%).
  A calibration curve for NFL already failed the gate (p(worse) 0.80,
  `multi-sport.md`). Windows disagree, so no consistent direction to exclude.
- College football is already off the Daily List (`LIST_OFF`, 19 Oct) and its
  reserve rides the same probabilities as the history above.

## Decision

Excluding cfb or NFL Firm picks from the reserve would be chosen from the
live record, and the held-out history shows no matching gap: it would fail
Rule 1 and could not pass the Rule 3 gates (no log-loss change, since
probabilities would be untouched; and the two windows disagree for NFL).
Sample is also small: cfb alone is z about -1.6, NFL 15 games z about -1.8,
across several sports looked at after the fact (a selected worst-of-nine).

Nothing changed. Revisit if cfb reserve stays 8+ points under quote past
~150 graded picks, then test a reserve floor (0.62 -> 0.65/0.70) by replaying
`history-sports/` football/college-football, paired and bootstrapped, fit on
2024-25 and confirmed on 2025-26. Not run here: reserve membership is a
filter, not a probability, so the Rule 3 log-loss gate does not apply to
it directly; the test must be hit-rate-v-quote per band on both windows.
