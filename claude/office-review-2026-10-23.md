# Office review, 23 Oct 2026 (Luke, Chief of Staff)

Covers `RELEASES.md` since 12 Oct (the last fortnight in detail) and the
`claude/` notes dated 12-23 Oct. Record numbers are read only, never fitted
(Rule 1). Follows `office-review-2026-10-12.md`.

## What the office shipped
- **Tennis off the Daily List** (15 Oct) and **college football bar 70% -> 80%,
  then off the List** (13 and 19 Oct), both on their live record. Their Firm+
  picks go to the reserve.
- **Honest cup numbers** (19 Oct): domestic cups carry their own calibration
  (`CUP_CALIBRATION`); a raw 75% cup favourite shows about 59%.
- **Recent form on football rows**, status boxes, final and predicted scores.
- **Coverage**: Croatia, Hungary, Serbia, Ukraine and Korea top flights from
  API-Football (20 Oct); API-Football prices for every fixture it lists (22 Oct).
- **Odds tab, rebuilt three times** (Douglas): Double and Treble built to land,
  three days ahead and re-checked each build; at least three groups a day
  (Wider Double, Treble, Fourfold fill); every group pays at least 2.00.
- **Office**: the sprint works HQ's ranked backlog; Elena (CEO) and the
  Groups & Odds Desk opened (20 Oct).
- **Grading audit** (Susie, 23 Oct): openfootball extra-time scores parsed as
  90 minutes; 88 graded games re-checked on ESPN, 0 mismatches, no published
  number moved.

## What it learned, including rejected tests
- **Team news** (injuries, suspensions): nothing passes cleanly. **Form by
  stage of season**: no weighting fixes games 4-6. **Hot form, big clubs**:
  land as quoted or under; cup favourites far under (56.5% v 69.7%), hence the
  cup curve.
- **Championship draw lift** by gap: rejected, worse on the fit season for
  every k (+0.0012 to +0.0044 log loss, p(worse) 0.92-0.97).
- **Tennis surface weight** 0.3 kept; tennis gap z -1.03, inside noise.
- **Daily List bar**: 80% stays (2025/26: 81.9% at 80%, 75% is -2.4 pts, 85%
  is -12.5 pts). 2026/27 has only 11 calls at 80%.
- **Calibration rerun**: football 55-80% inside intervals on the fit season;
  85%+ still over-confident (88.8% quoted, 69.2% landed, 39 calls). Check
  season 60-70% runs +7.5 pts above quote but the fit season disagrees, so
  Rule 3 blocks a refit. Core-league 65-75% replay says the same (2026/27
  82.3% of 51 v 69.0%, partial).
- **Edge over bookmaker prices**: none. Legs 2/4/6 points above the fair
  chance landed 2-3 points *below* it on both seasons (12,510 and 1,749 legs).
- **Leg-property scan**: no cut by home/away, price, band, tier or league holds
  on both seasons; the 5-point model-v-market cap is already the finding.
- **Weakest sport scan**: WTA 70%+ (70.5% v 77.8%, z -1.6), NFL, cfb: none past
  2 sigma; a change would mean fitting on the record.

## Where accuracy stands (read only, 21 Aug to 23 Oct)
| Group | n | landed | expected |
|---|---|---|---|
| Football, all graded | 5,931 | 67.8% | 66.7% (tier-weighted) |
| Football Strong | 244 | 78.7% | 78.1% |
| Football Firm | 378 | 70.4% | 67.9% |
| Football Lean | 601 | 65.1% | 64.6% |
| Football Daily List | 103 | 81.6% | 80% bar |
| Football reserve | 258 | 67.1% | Firm 62%+ |
| Sports overall | 269 | 67.3% | 65.8% |
| Sports Daily List | 65 | 80.0% | 81.8% |
| Tennis overall | 848 | 61.6% | 62.7% |
| Tennis (old) list / reserve | 53 / 193 | 79.3% / 67.9% | 82.4% / 69.5% |
| Odds tab, all kinds (mostly retired) | 59 settled | 11 won | 19.0 expected |

Football tiers are on or above quote.
Sports by sport: rugby 82.5% v 68.4% (n=40), MLB 65.7% v 55.2% (35), NFL 57.5%
v 64.0% (47), cfb 65.3% v 69.3% (124). Tennis is the only group under quote
all along (ATP 62.2% v 62.8%, WTA 61.1% v 62.7%), inside one standard error
each.

## Data quality
- Football verification: 5,044 `verified`, 5 `verified-by-date`, 882
  `legacy-unverified` (unchanged since the fix, shrinking share), 0 late.
  Daily List: 79 verified, 24 legacy.
- Grading re-checked against ESPN on 88 games: 0 mismatches. One parser fault
  (extra-time score) fixed, none in the record.
- Stale rescheduled-fixture rows (46 pairs, 12 Oct) remain unresolved in the
  notes; check the 12 Oct priority 1 outcome before relying on list counts.
- Check season 2026-27 is still under 250 fixtures for most tests, so several
  results are held, not rejected. Revisit in December.
- Odds tab: the old record (11 of 59) is dominated by retired kinds. The new
  Double, Treble and Wider kinds have no settled group yet (2 pending): the
  2.00 floor and Wider rules are unproven live.

## Three most valuable tasks for next week
1. **Jade (accas): settle and report the new Odds tab kinds.** First live
   evidence for Double, Treble and the Wider kinds under the 2.00 floor. Report
   landed v stated by kind once 20+ settle; if Wider groups land under their
   stated chance, propose a higher `WIDE_MIN` (the note's own rule), not a
   lower floor.
2. **Susie (auditor): the rescheduled-fixture duplicates.** Still open from
   12 Oct: do any of the 46 stale pairs (4 touching a list or reserve flag)
   get graded twice? Quantify the effect on the 103-pick Daily List and
   propose an archive key fix if real.
3. **Andrew (calib): prepare the December check-season test.** The 60-75%
   band is running +7.5 to +12 pts above quote on the current season but not
   the last. Stage `tools/core_midband_replay.py` and the 85%+ tail test to
   re-run the day the check season reaches 250 fixtures; until then, decide
   whether the 85%+ row display should carry the 69% tested rate.

Held: WTA 70%+ and NFL gaps (under 2 sigma, wait for more games); tennis and
college football return to the List only if their live record holds.
