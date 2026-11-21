# Reserve (other sports) below quote: where the gap sits (21 Nov 2026)

Task from the HQ planner: other-sports reserve picks, 28 days, 317 of 449 landed (71%) v 331.8 expected, z -1.6. Read from `sports-graded.json` (`reserve` rows, tally only, nothing fitted, Rule 1).

## Numbers (reserve rows, graded, to 21 Nov)
| Cut | n | landed | quoted | gap | z |
|---|---|---|---|---|---|
| All, last 28 days | 741 | 73.4% | 73.8% | -2.8 | -0.24 |
| All, whole record | 864 | 72.2% | 73.4% | -10.2 | -0.79 |
| CFB all | 214 | 71.0% | 75.6% | -9.7 | -1.57 |
| CFB 68-74% band | 49 | 59.2% | 71.0% | -5.8 | -1.83 |
| CFB away | 72 | 65.3% | 74.4% | -6.5 | -1.79 (28d: +0.6) |
| NCAAB (all in 28d) | 453 | 73.7% | 74.0% | -1.3 | -0.14 |
| NCAAB away | 41 | 56.1% | 71.0% | -6.1 | -2.12 |
| NCAAB home | 364 | 78.0% | 74.8% | +11.8 | +1.44 |
| NBA | 120 | 73.3% | 70.3% | +3.6 | +0.72 |
| NFL | 46 | 60.9% | 69.0% | -3.7 | -1.20 (62-68% band 11 of 23, z -1.76) |
| Rugby | 27 | 70.4% | 67.8% | +0.7 | +0.29 |

My 28-day read (z -0.24) is milder than the planner's -1.6; the planner's window or row set differs, and I did not chase it. The 28-day gap is spread thin: no sport or band is a 2-SE shortfall on 50+ picks except NCAAB away, which is 41 picks.

## Decision
No change. Reasons:
- The only candidate cuts (college away, NFL 62-68%) are under the 50-pick floor for taking something off, or already handled: college away picks carry the Away mark and the pre-registered tripwire (`sports.WARY_TRIP_N` 100 away picks at 70%+, z -2) in `claude/college-side-mark-2026-11-15.md`. NCAAB away is 41 picks.
- Cutting by band after seeing it on the live record would be fitting on the scoreboard (Rule 1). A history test (Rule 3 gates) of "college away leaves the reserve" is the right route and is already queued behind the tripwire; no new evidence arrived today.
- Slicing 5 sports x bands x sides on 864 picks yields a few |z| ~1.8 cells by chance.

What would change this: NCAAB or CFB away reaching 100 picks at z -2 (tripwire), or NFL reserve reaching 50 picks under quote by 2 SE. Next step then: a history replay of the exclusion, paired and bootstrapped.
