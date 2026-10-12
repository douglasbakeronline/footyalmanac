# Office review, 12 Oct 2026 (Luke, Chief of Staff)

Covers `RELEASES.md` since 28 Sep (the last fortnight in detail: 28 Sep to 12 Oct)
and the `claude/` notes dated 5-12 Oct. Record numbers are read only, never
fitted (Rule 1). Follows `office-review-2026-10-05.md`.

## What the office shipped
- **Grading audit** (Susie): ESPN extra-time and penalty scores are no longer
  graded or used as live results (the board prices 90 minutes); tennis voids
  on ESPN's walkover status. 168 sampled graded games matched ESPN, 0
  mismatches; none of 12 AET / PEN games was in the record, so no published
  number moved.
- **ESPN fixture retry** (Raj): one transient failure no longer drops a
  competition-day; 4xx is not retried, a blocked network costs one pass.
- **Tests** (Allan): coverage for the least-tested module; a racy
  `test_af_single_flight` assertion fixed (failed 15/40, now 0/60).
- **Daily List and reserve**: every pick that clears the bar is shown (no
  cap), reserve fold under each day, in "How it went" too (8 Oct, by Douglas).
- **Tennis ratings** now use qualifying, Challenger and ITF matches; list bar 75%
  (8 Oct), after the June to October results gap (`tennis-ratings-gap-2026-10-08.md`).
- **Coverage**: hockey, college football, WNBA, NRL and basketball from ESPN;
  every domestic cup via API-Football (board only); U21 sides via Premier League 2.
- **Six rebuilds a day**, timed to when results land.

## What it learned, including rejected tests (all 12 Oct)
- Daily List bar: 80% stays. 2025/26 league picks landed 79.4% at 75% (n=189),
  81.9% at 80% (94), 69.2% at 85% (39). 75% v 80%: -2.4 pts (-7.5 to +2.5);
  85% v 80%: -12.5 (-21.3 to -4.4). 2026/27 has 11 picks at 80%; too thin.
- Goal cap in the ratings: rejected. Cap 5/4/3 on the fit season: -0.0002,
  +0.0005, +0.0025 log loss; nothing passes the 0.0005 gate on both seasons.
- Championship league-specific shrink: rejected. Best gain 0.0002 (gate 0.0005,
  p(worse) 0.41), sign flips across seasons.
- Calibration full-data rerun: football 55-80% inside noise in both seasons;
  85%+ over-confident (41 pooled calls, 68% landed v 89% quoted). Hockey and
  baseball over-confident in their check windows.
- Tennis 59.5% v 61.7% quoted is 1.07 standard errors; WTA clay main draw
  41.8% v 55.4% (n=55, one of seven cells found after looking). ESPN has no
  surface, so clay is priced on hard ratings; the fix test was blocked
  (Sackmann unreachable).
- Odds tab: 30 settled groups won 9 against 9.51 expected (bootstrap -0.51,
  90% interval -4.5 to +3.5); tennis legs 18 of 26 v 21.1. Price coverage:
  football 81 priced / 12 estimated, tennis 0 of 29, rugby 0 of 7.
- No free source exists for Croatia, Serbia, Ukraine, Hungary or Korea
  (TheSportsDB free key returns 5 of 12 table rows).

## Where accuracy stands (`record.json` etc., read only, 21 Aug to 12 Oct)
| Group | n | landed | expected |
|---|---|---|---|
| Football, all graded | 3,624 | 68.0% | n/a |
| Football Strong | 164 | 79.9% | 78.3% |
| Football Firm | 222 | 69.4% | 68.2% |
| Football Lean | 379 | 64.6% | 64.4% |
| Football Daily List | 72 | 83.3% | 80% bar |
| Football reserve | 141 | 66.0% | Firm 62%+ |
| Celtic's Law rows | 988 | 65.2% | n/a |
| Sports Daily List | 50 | 82.0% | 80.5% |
| Sports overall | 158 | 70.3% | 65.1% |
| Tennis overall | 526 | 59.5% | 61.7% |
| Tennis Daily List | 30 | 83.3% | 83.3% |

Football tiers and the Daily List are on target, a clear improvement on 5 Oct
(list was 16 of 22). Sports beat expectation, helped by rugby (82% v 68%, n=39);
cfb is slightly under (67.2% v 68.5%, n=58). Tennis is the one group below
expectation, driven by the WTA (56.8% v 61.3%, n=301). The reserve's Firm tier
is under its quote (63.0% v 65.9%, n=100), within noise.

## Data quality
- Verification: 2,740 of 3,624 football rows are `verified`, 882
  `legacy-unverified` (pre-fix, was 589 of 734), 0 late. Tennis has 110
  published late, counted apart.
- Fixture audit of 2,014 rows: no duplicates, no unrated rows. One real fault:
  rescheduled games leave stale rows under the old date (46 pairs in 2026
  archives, 4 touching a list or reserve flag). Not yet checked whether they
  inflate the scoreboard.
- Check seasons stay thin (2026-27 under the 250-fixture gate for most tests),
  so several tests are held rather than rejected.

## Three most valuable tasks for next week
1. **Susie (auditor): do stale rescheduled-fixture rows reach the record?**
   4 list or reserve flagged pairs exist; confirm whether either copy was
   graded or double counted, and propose a fix for the archive key if so.
2. **Theo (sports): tennis surface.** WTA clay is 41.8% v 55.4% and ESPN gives
   no surface. Find a free surface source (tournament-name map is the fallback)
   and run the paired surface-weight test before the grass/clay seasons matter.
3. **Andrew (calib): the 85%+ tail.** 68% landed v 89% quoted on 41 calls.
   Test a cap or flatter top of the curve under Rule 3 gates when the check
   season reaches 250 fixtures; until then, decide whether the row display
   should say so.

Held for later: Mia's rated-from-scratch Championship ideas wait on sample
size; Raj and Ava have nothing left on free sources.
