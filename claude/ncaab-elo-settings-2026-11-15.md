# College basketball Elo settings and the neutral-court curve, 15 November 2026

HQ planner task: college basketball lands 515 of 646 (80%) against 76% quoted,
z +2.0 on the live record. Used only to locate the gap (Rule 1). All tests on
`history-sports/` with `sports.replay`, fit 2024-25, check 2025-26 to the
archive start (5,814 warm decided check games), paired bootstrap, Rule 3 gates
(250+ games, p(worse) <= 0.30, gain >= 0.0005) and `tune_sport`'s own
65%+ gap guard.

## Already settled (do not repeat)

K, home advantage, season carry-over (`regress`) and margin of victory are
already fitted by `--tune` (k 32, hfa 100, regress 0.25, mov on) and the
November-December curve is live (`PHASE_MONTHS`,
`claude/ncaab-season-phase-2026-11-05.md`). The side split is in
`claude/college-side-mark-2026-11-15.md`.

## Tested now

1. **Is HFA or K pinned at the grid edge?** hfa 100 was the top of the grid.
   Extended to 125-200 (K 24 and 32), calibration refitted each time: check
   log loss 0.5499 live, 0.5517 at 125, 0.5538 at 150, 0.5587 at 200 (p(worse)
   1.00 each). Higher HFA is worse. Not binding. K 24 at hfa 100: +0.0004,
   p(worse) 0.73. Nothing to change.
2. **Neutral-court calibration curve.** The live curves' intercepts are fitted
   on all games, neutral included, and a positive early intercept is home
   advantage a neutral game does not have. Fitting the curves on home-court
   games only and one curve on neutral games (737 fit games, a +0.27, b 0.92):
   - fit season -0.0012 log loss, p(worse) 0.007;
   - check season -0.0005 (gain 0.00055), p(worse) 0.15, 5,814 games;
   - neutral curve alone (home curves unchanged): check -0.00015, p(worse)
     0.38, fails the gain bar.
   The 65%+ gap guard then refuses the full variant: quoted minus landed at
   65%+ on the check season widens from 0.0218 (live) to 0.0232, 0.0101 above
   raw against a 0.01 allowance. The gain is at the edge of the bar and the
   guard fails, so it is not shipped. Code reverted, `sports.json` unchanged.

## What the gap is

On the replay's check season college basketball is quoted *over* what it
lands (65%+: 78.9% landed v 80.2% quoted), the opposite of the live record's
+4 points. The live surplus sits in home picks in the early season (replay
home 88.8% v 83.5%, `college-side-mark`), and the early-season curve already
lifts those by fitting the previous season. The live excess is a feature of
this season's schedule (a z +2.0 on one season), not a mis-set K or HFA: a
fix fitted on the replay cannot add what the replay does not show. Under-quoting
here costs nothing on the List: college basketball picks need William Hill
1.05+ to show.

## If reopened

Neutral-curve variant needs one more season in the check window (or the gap
guard loosened by Douglas) before it passes cleanly. Re-run
`fit_phase_calibration` on home-only games plus a `neutral` curve in
`calibrate(p, cal, when, neutral)`.
