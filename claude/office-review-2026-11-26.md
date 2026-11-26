# Office review, 26 Nov 2026 (Luke, Chief of Staff)

Covers `RELEASES.md` from 18 to 26 Nov. A report by nature: no code or model
change, nothing fitted on the record (Rule 1). Follows `office-review-2026-11-18.md`.

## What the office shipped
- **Card:** rule 14 (rule 8's constants, 19 Nov, Douglas's call); decisions table
  reads the live rule; replay read at the last pre-start price; Fidelity "why";
  `card-short` log; `replay-differs` day counts; two-legged tie table; staking at
  rule 14's own rate.
- **Cards and slips:** List card and Daily 2x rebuilt until 07:00 UK on their day;
  one tracker for every card (UX 6) and a Cards board; slip tracker.
- **Site:** UX 1 to 7 (segmented control, filter bar, day ribbon, address bar,
  one row, ledger, Analysis shell); Daily List default band changes (60%+, then
  70%+, 60-69% filter back); research links on Edge and slip legs.
- **Mailer:** Daily List email 07:00 UK, Weekly Record Saturdays, sent emails on
  the Mailer tab.
- **Data:** nominal-date and round-date grading fixes (duplicates graded once),
  postponed-game moves (Portugal, Scotland, Greece, Czechia), kick-off retime
  lists (Championship, Serie A), AF spellings, results cross-check vs
  API-Football, slip and ledger postponed handling, markets spread read.

## What it learned, including rejected tests
- **NFL confidence shrink** and **WTA shrink 0.95-1.0**: tested, nothing ships.
- **Football 50-55% band over quote**, **Edge over the price (5th run)**,
  **tennis surface (5th check)**, **leg properties (5th)**: no change.
- **Football markets gate passes** (23 Nov over/under 2.5): the unders alone,
  lost on both football-data seasons, so not offered.
- **Tennis Card legs, third read (26 Nov):** 41 legs, 23 landed v 29.1 expected
  (z -2.13), unchanged since 14 Nov, all pre-floor; at the 75% floor 15 legs,
  11 v 11.9 (z -0.57). Tripwire needs 50+ at the floor. Not triggered.
- **Kick-off board v API-Football:** the board was right twice (Palermo,
  Iraklis); a league joins `AF_RETIME` only when a published listing agrees.

## Where accuracy stands (read only, `groupings-record.json` at 26 Nov)
| Card rule | groups | won | expected | units returned / staked |
|---|---|---|---|---|
| 13 | 4 | 1 | 1.39 | 4.80 / 8 |
| 14 (live) | 3 | 1 | 1.23 | 4.98 / 6 |
| Daily 2x | 9 | 3 | 3.46 | 8.08 / 9 |
| List card | 2 | 1 | 0.86 | 2.24 / 2 |

Football overall (15,360 graded): reads landed 67.8% v 66.6% quoted. Daily List
215 picks, 82.3% won v 82.1% quoted; reserve 688, 67.0% v 68.3% (the known
small under-quote).

Card legs by sport: NBA 36 of 48 (z +0.42), football 33 of 47 (z +0.31),
tennis 23 of 41 (z -2.13). Samples are far too small for any group-level
claim; the first real read is the 30 Nov review. Data quality: no open
name-match faults; open risks are sole-source leagues (API-Football,
football-data), nominal kick-off times in openfootball, and the Claude API
allowance (context check paused until 1 Dec).

## Three tasks for next week
1. **Kofi (value): the 30 Nov Card review.** Rule 14 v `rule13`, `rule12`,
   `span2` on the pool (price-fidelity read at first and last price) and both
   football-data seasons, p(worse) 0.30 on 100+ legs. No rule change before then;
   a reversal goes to Douglas with the numbers.
2. **Susie (auditor): grading integrity of the newer records.** Daily 2x, List
   card, slip, Scale and mailer "as sent" archives: no orphaned or doubled legs
   after the date-handling changes; `card-pick-twice` and `result-disagrees`
   clean; ledger `moved` counts sane.
3. **Hannah (legs): tennis at the 75% floor and the context check's return
   (1 Dec).** Count floor-admitted tennis legs towards 50; when the API allowance
   returns, confirm the veto's tally (30 "against" picks) is reading.
