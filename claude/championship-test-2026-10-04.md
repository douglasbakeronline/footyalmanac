# England Championship: league-specific home advantage and draw handling (rejected, 4 Oct 2026)

Task (Mia, Experiment Lead): the Championship (en.2) is the weakest league
with 30+ graded games on the live record. History only was used; record.json
was not read (Rule 1).

## What the history says

Championship, openfootball, 557 matches a season, live model and live
calibration (tune.live_baseline), walk-forward via replay.replay_league:

| Season | Home | Draw | Away | Goals/game | Log loss | Accuracy |
|---|---|---|---|---|---|---|
| 2023-24 | 44.5% | 23.5% | 32.0% | 2.67 | | |
| 2024-25 | 45.6% | 28.0% | 26.4% | 2.45 | 1.0346 | 48% |
| 2025-26 | 41.5% | 26.8% | 31.8% | 2.59 | 1.0633 | 44% |
| 2026-27 (95 so far) | 41.1% | 30.5% | 28.4% | 2.92 | 1.0895 | 36% |

The league is simply high-entropy: about 27% draws, and a home share that
swings 41% to 46% from season to season. Log loss near 1.04-1.09 against about
1.0 for the big leagues. The live-record 37% over 76 games sits inside what
the 2026-27 sample (36% over 95) and the 44-48% full-season rates allow for
sampling noise, with the early-season window the worst part of the year.

## Tests

1. **League-specific home advantage**: `ha_scale` (existing replay parameter,
   tilts the tier-2 home/away multipliers) at 0.8 to 1.3, en.2 only.
2. **Draw handling**: the Dixon-Coles rho at 0, -0.03, -0.06 (live), -0.10.
   The model's mean draw probability is already close: 27.5% predicted vs
   26.8% actual in 2025-26; 25.8% vs 28.0% in 2024-25.

## Result (paired bootstrap, 1500 reps, vs live ha 1.0)

| Test season | Change | n | Delta log loss | p(worse) |
|---|---|---|---|---|
| 2025-26 (fit) | ha 0.8 | 557 | -0.0019 | 0.126 |
| 2025-26 (fit) | ha 0.9 | 557 | -0.0011 | 0.083 |
| 2024-25 (extra season) | ha 0.8 | 557 | +0.0027 | 0.945 |
| 2024-25 (extra season) | ha 0.9 | 557 | +0.0011 | 0.912 |
| 2026-27 (confirm) | ha 0.8 | 95 | -0.0002 | 0.474 |
| 2026-27 (confirm) | ha 0.9 | 95 | -0.0003 | 0.443 |

Home advantage: the best value flips sign between seasons (2024-25 prefers a
bigger home edge, 2025-26 a smaller one), which is what a fit to one season's
home share looks like. The confirm season has 95 fixtures against the 250
gate, and its gain (0.0002-0.0003) is below the 0.0005 gate with p(worse)
about 0.45. Fails Rule 3 on two of three gates.

Draw handling: rho moves log loss by at most 0.001 in either direction and in
different directions by season. Nothing to ship.

## Verdict

Rejected. No model number changed. Do not repeat a league-specific
`ha_scale` or rho for en.2 on this evidence. Revisit only when 2026-27 has
250+ Championship fixtures (about November) AND the sign of the effect has
held across at least two completed seasons, which 2024-25 vs 2025-26 shows it
has not.

The practical reading: the Championship is honestly hard to call. The model's
tier ladder and flagging already say so (low confidence, rarely above Lean),
and the Daily List excludes it unless calls at its level clear the 80% tested
bar.

Reproduce: a throwaway script calling `replay.replay_league` for en.2 with
`params={"ha_scale": x}`, scored with `tune.raw_probs(rows, rho)` and
`tune.score_under(..., tune.live_baseline())`, compared with `tune.paired`.
