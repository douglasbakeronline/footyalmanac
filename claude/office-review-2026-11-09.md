# Office review, 9 Nov 2026 (Luke, Chief of Staff)

Covers `RELEASES.md` and the `claude/` notes since the 31 Oct review. Record
numbers are read only, never fitted (Rule 1). Follows `office-review-2026-10-31.md`.

## What the office shipped
- **Card rules** (31 Oct to 6 Nov): the 10-under cap (rule 5), college basketball
  off, the Model card on paper, the opposition priced 9+ (rule 6).
- **Card review machinery** (9 Nov): nightly `card-review.yml`, integrity checks
  (`card-leg-unreplayable`), `cardLegsBySport` and the tennis tripwire in the
  record, a corrected staking bankroll, `flatstake`, `notennis` and `tennis80`
  variants, price timing by lead (`whenLast`), every UK book on every card.
- **Decisions delegated** (Douglas, 9 Nov): Card 3x stays, cap on probation,
  tennis stays with a tripwire, no Reports page, rule 6 stays.
- **Weekly Sunday report** (`tools/weekly_report.py`), site analytics, home / draw /
  away prices on every row, retry on ESPN fetches.
- **Grading audit** (9 Nov): four tennis wins graded as losses (de Minaur,
  "de" v "De") fixed in `score_tennis.py`; sports scores at neutral sites now
  read in priced order. 93 of 94 football and 15 of 15 NBA/NFL results agreed
  with ESPN.
- **Office doubled**: four sprints a day, 28 pull requests a day cap, `MAX_OPEN` 12.

## What it learned, including rejected tests
- **Edge over the bookmakers' price, third run: none.** Legs 2 / 4 / 6 points above
  fair landed 1.5-2.1 points under fair on fit (n 4,188 / 2,539 / 1,510) and check
  (689 / 476 / 323). Gates failed.
- **Card over five seasons**: the under-market cut lands 2-5 points over quote
  but is about break-even at the average price; no gap band holds in every
  season (rule 5 cap unsupported over 2022-25); opposition 9+ holds in all five
  (83.8% v 76.2%, 511 legs). Under rule 6 football alone makes one group in five seasons.
- **Leg properties, third look**: no cut holds on both seasons; pool has 45
  real-priced football 65%+ legs against the 250 Rule 3 needs.
- **Tennis surface**: no source (Sackmann 404, tennis-data 403, ESPN has none);
  every remaining 2026 event is hard court, so no price would change before April 2027.
- **Weakest other sport**: none two standard errors under on 50+ games (college
  football z -1.23, ATP -0.73). ATP 55-65% bands run under quote (z about -1.3).
- **Southern League Premier Central**: strict 33 of 74 v 39.0 expected, z -1.44; no history to replay.
- **Book and timing**: Bet365 +0.30% v average, William Hill -0.04% on 107 legs; not a push-time case.

## Where accuracy stands (read only)
| Group | n | landed | quoted |
|---|---|---|---|
| Football, all graded (reads) | 7,752 | 67.8% | 66.5% |
| Football Daily List | 165 | 80.6% (won) | 81.8% |
| Football reserve | 526 | 64.5% | 67.9% |
| Card, all rules | 35 groups | 11 won | 11.7 expected (z -0.25) |
| Card, returned | | 30.7 on 35 staked | |
| Model card (paper) | 14 | 6 won | 5.3 expected |
| Card legs: tennis | 40 | 22 (55%) | 71% (z -2.23) |
| Card legs: NBA / football | 32 / 30 | 24 / 22 | z +0.51 / +0.71 |

The football list is 1 point under quote on 165 picks, inside noise; the
reserve is 3.4 points under on 526 (the known away under-quote). The Card is on
expectation. Tennis Card legs are the one leak, ten legs short of the 50-leg
tripwire. Data quality: one grading fault found and fixed (tennis name case);
no name-match faults; risks remain API-Football allowance and football-data as
sole source for five leagues. Card legs first written as estimates (42 of 59
to 8 Nov) cannot be replayed; the `priced` block fixes this from 10 Nov.

## Three tasks for next week
1. **Kofi (value): the 30 Nov Card review, pre-registered.** Fix thresholds
   (z, groups, return, p(worse) 0.30 on 100+ legs) now for `uncapped`, `opp7`,
   `notennis`, `tennis80`, `flatstake` on the pool from 10 Nov. Do not change a
   rule before then.
2. **Hannah (legs): act on the tennis tripwire.** At 50 Card tennis legs and two
   standard errors under quote, the sport goes into `CARD_SPORTS_OFF`
   (rule bump, note, release). Until then, check nightly that tennis
   legs carry real `priced` blocks.
3. **Susie (auditor): grading consistency after the tennis spelling fix.**
   Regrade check on the tennis record after the next score run (883 of 1,395
   before), and scan football, sports and tennis names for other case or
   accent mismatches between ESPN and the pool.
