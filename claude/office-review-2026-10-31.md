# Office review, 31 Oct 2026 (Luke, Chief of Staff)

Covers `RELEASES.md` since 23 Oct and the `claude/` notes dated 23-31 Oct.
Record numbers are read only, never fitted (Rule 1). Follows
`office-review-2026-10-23.md`.

## What the office shipped
- **Daily List order** (28 Oct): confidence first, tested rate second; Group A
  (strongest five at 85%+) and Group B labels; a started-football sort bug
  fixed; tennis back on the list at 75%.
- **The Card** (29-30 Oct, Douglas): one window a day, no clock lock (open until
  first kick-off), up to 6 groups, stake weights, William Hill prices,
  substitutes, tennis legs 75%+, NFL and cfb off, football 5+ points under the
  market, core leagues only again after the two-rule replay, a published group
  holds through price drift (`CARD_DRIFT` 10%), a Placed marker, ntfy pushes.
- **Evidence tools**: `card_legs_history.py`, `goals_value.py` (both weekly,
  advisory), `card_replay.py` variants pre-registered for 30 Nov, and the
  whole priced pool archived daily (`pool-<date>.json.gz`).
- **Reliability**: football-data.co.uk outage keeps the last good copy; the
  API-Football "spent" marker expires after 90 minutes; push-triggered builds
  run `AF_FRUGAL` after 25 builds in two days exhausted the allowance.
- **Audits** (no bug): results grading, 105 games vs ESPN, 0 disagreements;
  new-league coverage already live.

## What it learned, including rejected tests
- **Edge over bookmaker price: none.** Legs 2/4/6 points above fair landed
  1.5-2.1 points below fair on fit (12,510 legs) and check (1,749).
- **Leg-property rescan**: no cut holds on both seasons; the model-not-above-
  market cap fails on check (+7.9 v +8.8 for all legs).
- **Goals market**: market beats model on log loss both seasons; value picks
  lose (ROI -4.6% / -19.0%, CLV negative). No goals bets.
- **Card on past seasons**: leg rule 72.7% v 68.0% quoted (n 417); the edge is
  the favourite-longshot bias, not the under-market filter.
- **Tennis legs (22/40 v 28) and tennis list (39/51 v 42)**: located (model
  under 75%; Wuhan before the 8 Oct fix); nothing to ship, a further cut would
  fit the live record.
- **Daily List bar replay**: 80% stays; 85% is -12.5 points on 2025/26.
- **Calibration rerun**: nothing passes both seasons; ice hockey and baseball
  over-confident, 85%+ football still over-confident.
- **Odds API tennis keys**: cause unconfirmed, no key in the sandbox.

## Where accuracy stands (read only, 21 Aug to 31 Oct)
| Group | n | landed | quoted |
|---|---|---|---|
| Football, all graded | 8,239 | 67.7% (reads) | 66.5% |
| Football Daily List | 127 | 79.5% | 81.6% |
| Football reserve | 358 | 65.4% | 67.8% |
| Sports overall | 438 | 63.7% | 66.0% |
| Sports Daily List | 74 | 82.4% | 82.1% |
| Sports reserve | 166 | 65.1% | 71.1% |
| Tennis overall | 1,145 | 62.5% | 63.8% |
| Tennis list | 68 | 77.9% | 82.5% |
| Tennis reserve | 303 | 69.6% | 70.7% |
| Betting groups, all kinds | 95 | 24 won | 31.0 expected (z -1.56) |
| Card, current rules | 19 | 5 won | 5.9 expected (z -0.46) |

The football list is 2 points under quote on 127 picks, inside noise. The
sports reserve is the one gap worth watching (65.1% v 71.1%, n 166). Betting
groups overall are under expectation; the Card on its current rules is on it,
but 19 groups prove nothing either way.

Data quality: no name-match or grading faults found this fortnight; the open
risks are API-Football allowance (Pro lapsed once on 30 Oct) and football-data
as the single source for five leagues.

## Three tasks for next week
1. **Allan (engineer): API-Football allowance guard.** Count calls per build,
   write them to the build report, and alert before the daily limit, so a lapse
   or a burst of merges cannot leave the board on a stale copy again.
2. **Kofi (value): pre-register the 30 Nov Card review.** Run
   `tools/card_replay.py` variants on the pooled files so far, fix the
   decision thresholds (z, return, groups needed) now, and do not change the
   Card rule before then. Advisory only.
3. **Theo (sports): sports reserve gap.** 108 of 166 v 71.1% quoted, plus ice
   hockey and baseball over-confidence. Test per-sport reserve calibration on
   each sport's replay (fit/check split, Rule 3); report even if rejected.
