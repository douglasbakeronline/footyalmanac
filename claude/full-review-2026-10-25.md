# Sports Almanac full review, 25 October 2026

Covers the code on `main` at commit 88cf380 (25 Oct, 17:23 UTC), the project notes, the Actions run history and the four record files. Nothing was edited.

## Verdict

The forecasting core is sound and honest: 7,222 graded football rows quote 48.6% and land 50.3%, the Daily List quotes 81.8% and lands 79.0% (n=119), and the pipeline has not missed a build in the last 100 runs. The betting layer is not: 64 settled groups have returned 40.5 units on 64 staked (-37%, 90% interval -66% to -6%), the Card rules are built to a price target that makes them lose 14-19% per unit if the bookmakers are right, and two record-keeping bugs will flatter the Card as soon as it settles.

The single largest model signal in the live record is that away picks are under-quoted by 7 points (quoted 44.7%, landed 51.7%, n=1,834, z=5.1 on clean rows) while home picks are exactly on quote. The per-league home-advantage refit already queued for Mondays is the right lever; it should be fitted by league family, not only on the core leagues.

Three things are silently stale today: the FIFA rankings file (July), 23 API-Football league seasons, and the API-Football Pro plan itself, which renews on 30 October. Running costs are £89-£164 a month on the Claude Max path, or £149-£414 if the office agents are billed through an API key.

## What the live record says

Football is well calibrated at every tier and beats both baselines (log loss 1.0125 against 1.0742 for the long-run 45/26/29 split). Figures below are strict: a pick counts only when it won.

| Football, graded to 25 Oct | n | Quoted | Won | Log loss |
|---|---|---|---|---|
| All rows | 7,222 | 48.6% | 50.3% | 1.0125 |
| Strong (70%+) | 300 | 77.7% | 78.3% | 0.662 |
| Firm (62-70%) | 441 | 67.7% | 69.2% | 0.824 |
| Lean (55-62%) | 755 | 59.6% | 58.7% | 0.950 |
| No read | 5,726 | 44.2% | 46.3% | 1.054 |
| Daily List | 119 | 81.8% | 79.0% | 0.635 |
| Reserve | 319 | 67.8% | 65.5% | 0.872 |
| Clean rows | 5,204 | 48.9% | 51.3% | 1.006 |
| Celtic's Law rows | 2,018 | 47.9% | 47.8% | 1.030 |

**Away picks are under-quoted, home picks are not.** On verified rows, home picks quote 50.2% and land 50.2%. Away picks quote 44.7% and land 51.7% (n=1,834; clean rows n=1,167, z=5.1). The gap is in every band below 60%: 30s band +6 points, 40s +7.5, 50s +9. The mean quoted triple is 0.443 / 0.266 / 0.291 against an actual 0.436 / 0.253 / 0.311, so the model gives about 2 points too much to home and draw and takes it from away. The calibration line cannot fix this because it acts on the top probability only (`engine.py:872`).

**Drift.** By fortnight, 60%+ football picks landed 94%, 77%, 82% (Aug-Sep, n 16-27), then 69.0%, 69.4%, 65.5% on n 287, 591, 148 since the coverage expansion, against quoted 70.1%, 68.7%, 67.6%. The wider leagues land on quote; the early figures were small-n luck, not a decline.

**Other sports** (graded picks, voids excluded):

| Sport | n | Quoted | Landed | Last 14 days n / landed | On the List |
|---|---|---|---|---|---|
| ATP | 376 | 62.8% | 61.2% | 167 / 57.5% | Off (reserve only) |
| WTA | 560 | 63.0% | 61.4% | 308 / 66.2% | Off (reserve only) |
| Rugby | 59 | 68.2% | 76.3% | 23 / 69.6% | 22 at 82.3% landed 95.5% |
| NFL | 47 | 64.0% | 57.4% | 28 / 57.1% | 7 at 82.6% landed 85.7% |
| College football | 173 | 69.2% | 63.0% | 119 / 60.5% | 41 at 82.0% landed 73.2%, now off |
| NBA | 36 | 61.9% | 61.1% | 36 / 61.1% | none yet |
| MLB | 37 | 55.4% | 67.6% | season over | none |

Tennis 70-75% picks land under quote on both tours (ATP 68.4% of 38, WTA 63.0% of 54); the "tested" chip on those rows still shows 81-90% because it comes from an archive walk with true surfaces and main-draw matches only. College football 65-70% landed 47% of 17 and 80-90% landed 70% of 27: the Elo is over-confident there and dropping it from the list was right.

Draws: the model picked a draw 100 times in 7,222 and 25.1% of fixtures finished level. By design, but it is the largest single miss category and worth stating on the page.

## Bugs

Twenty-two found, none fatal to the daily build. The high ones are about honesty of the record or silent staleness.

| # | Sev | Where | What happens | Fix |
|---|---|---|---|---|
| 1 | High | `groupings.py:1640-1682` | `grade()` drops the `wide` and `late` flags, so wider-rule and post-lock groups are tallied as the full Card and `cardWide` can never fill. All four Card groups archived on 25 Oct are `late` (built 14:50Z, lock 07:00Z). | Copy `wide`, `late`, `locked`, `lockAt` into the graded row; tally `late` on its own line. |
| 2 | High | `odds.py:310` | `bestBook` / `returnedBest` take the max over every API-Football book; the 25 Oct card names 1xBet, Betano, Dafabet. A UK punter cannot bank it (+3.0% over average, max +11.8%, n=177) and one stale book sets the max unchallenged. | Whitelist UK-licensed books for best price, or require two books within 2%. |
| 3 | High | `score.py:204-208`, `index.html:1426` | `correct()` counts a predicted draw scoreline on a draw as right. 4,658 rows carry a level likely-score; their ok rate is 71.6% while their pick won 44.8%. The Football lede says "read right 67.6%"; strict is 50.3%. | Headline, tiers and bands on `pick == actual`; keep "reads" as a labelled secondary. |
| 4 | High | `rankings.py:75-112`, `fifa-rankings.json` | File holds release 15175 (20 Jul 2026), which is also the hard-coded seed id, so the scan never finds a newer release; every exception is swallowed. Internationals since August have been scored on a July ranking. | Fetch the dateless overview for the latest id; log the exception; warn when the file is over 45 days old. |
| 5 | High | `engine.py:350-353`, `sources.py:1114-1127`, `af-leagues.json` | 23 wider leagues have static seasons that have rolled (17 at 2025-26, 6 at 2024-25, 3 at 2024). The finished season is fetched, nothing is flagged, the league just vanishes from the board. | Take `season` from the API's `seasons[].current`, as `af_refresh_cups` already does. |
| 6 | High | `build.py:20-21`, `engine.py:32-188` | 90 hand-written season strings. Calendar-year leagues (MLS, Brazil, Nordics, Japan, Korea) go stale on 1 Jan 2027 and silently price on last year's ratings, against rule 6. | Derive the season per competition type from today's date; unit test that every entry contains the current year. |
| 7 | High | `deploy.yml:114-123, 172, 197` | The refuse-if-empty guard covers football only. If ESPN is down `sports.py` writes an empty board and it is committed back as the new baseline; a partial API-Football day publishes a degraded site rather than yesterday's. | Guard sports and groupings like tennis; refuse when fixture count is under 40% of yesterday's. |
| 8 | Med | `groupings.py:1316, 382-387` | `recheck_card` has no stale-price fallback and `_odds_for` bypasses the quota marker, so a quota-exhausted 200 with an empty response is cached 90 min as "no prices" and drops every unlocked Card group. | Route through `sources._af_get`; add the `stale` path from `recheck`. |
| 9 | Med | `groupings.py:1350-1358, 1489-1504` | A locked group survives only via the published `groupings.json`. If Pages lags, the next build builds a fresh `late` group and the archive gets two for one slot. | Read `groupings-archive/<date>.json` as the source of truth for locked slots. |
| 10 | Med | lock logic, `deploy.yml` schedule | Prices come from the last build before lock (05:15Z for a 07:00 lock), but scheduled runs start a median 1.96 h late (max 6.6 h), so Daytime and Evening groups are often priced from the 00:10 run. | Add a 06:00Z price-only job, or archive `lockPrice` from the first post-lock build and grade at that. |
| 11 | Med | `build.py:955, 1329-1341` | A club with no prior season loses its unrated flag after one match and sits on the board unflagged. | Flag when `prow is None` until `played >= 6`. |
| 12 | Med | `build.py:124-142` | Native cups and continental ties quote the core-league tested rate though cup favourites land far under it (56.5% v 69.7%). | Return None unless the family has its own bands. |
| 13 | Med | `build_tennis.py:222-244` | Retirements enter ratings at full weight; `tennis.json` says 0.5. 89 WTA and 41 ATP since June. | Scale by `retirementWeight`. |
| 14 | Med | `build_tennis.py:494-498` | Results against unrated players are dropped: 30% of ATP and 15% of WTA Sep-Oct results. | Seed unmatched players at a provisional qualifier rating. |
| 15 | Med | `score_tennis.py:48-65` | Publish-before-start uses ESPN's placeholder midnight New York time: 254 of 1,078 prices (24%) refused as late, 63 of them published before the real start. | Hold the price to the real start when the archived time is the placeholder. |
| 16 | Med | `sports.py:58` | `CHECK = (2025-07-01, None)` is open-ended; the "never seen" window now includes Sep-Oct live-graded games. | Cap CHECK at the first archived prediction (2026-09-27). |
| 17 | Med | `office-agents.yml:15-63` | The 09:30 backup cron usually starts before the delayed 06:30 run; works by accident. | Drop the backup or key the check on the plan job's conclusion. |
| 18 | Med | `ceo.yml:10-39` | Triggers on `opened` and `labeled`; HQ opens issues already labelled, so Elena runs twice per brief (2 x Opus x 80 turns). | Drop `opened`, or `cancel-in-progress: true`. |
| 19 | Med | `agents/policy.json:12` | `auto_merge_classes` includes `unknown` with `min_age_hours: 0`, so any path outside the class map merges without review. `home-advantage.json` is not in `PROTECTED`. | Remove `unknown`; protect `home-advantage.json`. |
| 20 | Med | `tune.py:47` | Weekly calibration gate is p(worse) <= 0.30; over a season of Mondays one false pass is likely. | Tighten to 0.10 or require two consecutive passes. |
| 21 | Low | `engine.py:486, 916-942` | `MAX_GOALS = 10` leaves up to 31% of Poisson mass off the grid in lopsided ties (scorelines, BTTS, over 2.5 affected; 1X2 not). | `MAX_GOALS = 15` or cap lambda at 5. |
| 22 | Low | `build.py:674`, `score.py:170` | `date.today()` is UTC; the 00:10Z build in summer anchors on yesterday's UK date. | Use `datetime.now(ZoneInfo("Europe/London")).date()`. |

Also: `claude.yml` has skipped all 24 triggers since 4 Oct; `sports.py` archives "if necessary" MLB/WNBA games that never settle (16 pending forever); postponed football legs never void in the groupings record (5 pending); `engine.py:1135` mutates `HOME_MULT` globally; the strength scale mixes fitted and hand-set values when only one side of a continental tie is in `europe.json`.

## Gaps and opportunities, ranked by expected gain

Log-loss on football unless stated, against a live 1.0125 with a noise band of about 0.005.

| # | Change | Expected gain | Evidence needed |
|---|---|---|---|
| 1 | Home/away tilt by league family (core, AFX, international) as `ha_scale` in the replay, gated | 0.001-0.002 overall, more on away rows | Replay 2025 and 2026 by family, paired bootstrap |
| 2 | Per-league home advantage (Monday refit already queued) | 0.0007-0.0010 | Passes once the check season reaches ~1,500 fixtures (December) |
| 3 | Fit the domestic strength coefficients (`tune_strengths.py`, never applied) | 0.003-0.005 on cup and promoted rows | `--fit`, check on the 2025-26 cup replay |
| 4 | Tennis: provisional ratings, retirement weighting, own-band live chip | Removes the 70-75% under-quote | `tools/tennis_gap_eval.py` |
| 5 | Second prior season for the 14 ESPN-backfilled leagues | ~0.0005 | `backfill.py --season 2024`, replay |
| 6 | Stage-of-season shrink for core leagues | 0.0005-0.0010 | Re-run in December at 250+ fixtures |
| 7 | A surface source for tennis before April 2027 | Avoids clay ratings frozen at June 2026 | 40% of WTA Sep-Oct results were clay rated as hard |
| 8 | Market blend into the Daily List | 0.02-0.03 (measured) | Your standing decision is no; the evidence stands |
| 9 | xG ratings | 0.005-0.010 | No free licensed feed; not actionable |
| 10 | Draw modelling for the list | none | A selection rule only |

Coverage: ESPN serves `football/cfl`, `basketball/nbl`, women's college basketball and Super League in the same shape as feeds already used, none fed. NHL is fed but rightly not published. Rugby World Cup months are hard-coded to Sep-Oct; RWC 2027 runs 1 Oct to 13 Nov.

Page: the build inlines `record.json` (3.66 MB) and loads `sports-record.js` and `tennis-record.js` before first paint, ~7.7 MB raw / 1.1 MB gzipped, roughly 3-5 s to interactive on 4G. Only "How it went" needs them. No sticky navigation on phones: 13 tabs wrap into five rows. Tap targets 26-29 px against 44. Prices on the Bets tab carry no read-at time; estimated prices share a column with real ones; the Card's "Lands about 7 in 10" is the bookmakers' number restated.

## The betting layer

Not profitable so far, not expected to be at these margins, too few bets to prove either way.

| Kind | Settled | Won | Rate | Avg odds | Expected wins | Return | ROI avg | ROI best |
|---|---|---|---|---|---|---|---|---|
| Steady (retired) | 25 | 4 | 16% | 3.11 | 9.7 | 10.7 | -57% | -55% |
| Balanced (retired) | 17 | 5 | 29% | 4.61 | 5.1 | 20.9 | +23% | +33% |
| Stretch (retired) | 15 | 1 | 7% | 7.57 | 3.6 | 7.1 | -53% | -50% |
| Banker (retired) | 2 | 1 | 50% | 1.93 | 0.8 | 1.8 | -10% | -4% |
| Wider Treble / Fourfold | 4 | 0 | 0% | 2.05 | 1.5 | 0 | -100% | -100% |
| Multiplier | 1 | 0 | 0% | 2.89 | 0.3 | 0 | -100% | -100% |
| Card 2x / 3x | 0 | 0 | | 2.11 / 3.04 | | | | |
| All | 64 | 11 | 17% | 4.20 | 20.8 | 40.5 | -37% | -32% |

Eleven wins against 20.8 implied: the retired five-leg kinds overstated their chances by nearly half. The only positive stretch was 9-11 Oct; cumulative P&L is -23.5 units at average price.

Legs (305 graded, 72.5% landed): priced legs landed 72.1% against 70.4% fair (n=201, 90% interval -3.4 to +6.8 points), flat ROI -2.3% (-9.8% to +5.2%). Legs passing today's Card rule landed 74.1% against 73.4% fair (n=85), ROI -4.7%.

Why the Card rules lose if the market is right: `best_card` maximises combined fair chance subject to a price floor, so it takes the shortest legs that still reach 2.0 or 3.0. With a 5% margin per leg the ceiling is 43% for a three-leg 2x and 28% for a 3x; the 25 Oct groups show exactly that. EV per unit at average price is -14% (three legs) to -19% (four). A positive edge needs about +5 points a leg over fair, sustained. Singles on the same legs lose about 5% a unit instead.

What would make the test mean something: fix bugs 1, 2, 8, 9, 10; price from UK-licensed books and record the price at lock; make landed-minus-fair per leg the headline with an interval; freeze the rules until ~300 locked legs exist (6-8 weeks); no staking advice while the edge is at or below zero. If you place at a UK book at 07:00, record that price; it is the only number that answers your question.

## Reliability

Deploy 100/100 over 16-25 Oct; Tests 100/100; merge window 100/100.

| Workflow | Cron (UTC) | Runs/week | Health |
|---|---|---|---|
| deploy.yml | 00:10, 05:15, 12:00, 17:00, 19:30, 22:15 + every push | 42 + 25-40 push | 100% |
| office-agents.yml | 06:30 and 09:30 (one works) | 14 | 90% of 51 |
| office-merge.yml | 09:00, 15:00, 21:00 | 21 | 100% |
| tune.yml | Mon 04:40 | 1 | 80% of 10 |
| evaluation / tests | per PR | ~27 | 88% / 100% |
| ceo.yml | on `ceo` issues | 0-n | fires twice per brief |
| claude.yml | on @claude | 0 | all skipped since 4 Oct |

Scheduled runs start late (deploy median 1.96 h, sprint 4.2 h, tune 6.1 h): GitHub's queue, not the repo. Push builds are a third of deploys (five on 25 Oct between 15:01 and 17:20), each spending API-Football calls. The App token path fails open: if token creation fails the day's archive is lost with only a warning. Season rollover is the biggest unmonitored risk (bugs 5 and 6). API-Football Pro renews 30 Oct; without it 227 leagues, the cups and every football price go, and the site shows "no prices" rather than an error.

## Costs

Rate $1 = £0.75. Repo figures quoted; list prices as of Oct 2026, check against invoices.

| Service | Used for | Price | Monthly GBP |
|---|---|---|---|
| API-Football Pro | 227 extra leagues, cups, every football price | $19/mo, 7,500 calls/day; renews 30 Oct | £14 |
| Claude, Max path | office sprint (up to 6 Sonnet agents x 50 turns daily), Elena (Opus x 80 turns per brief), @claude | $100 or $200/mo; the notes say the Max OAuth token is set | £75-£150 |
| Claude, API-key path (instead of Max) | same workloads per token | Sonnet $3/$15 per M, Opus $15/$75; 15k in/2k out per turn, 90% cache: sprint $145-$360, CEO $35-$135, @claude $0-$40 | £135-£400 |
| GitHub Actions | ~78 scheduled runs/week + push builds | free on public repos | £0 |
| GitHub Pages | site and footyalmanac-hq | free | £0 |
| The Odds API | tennis/rugby prices, 15/day | free tier | £0 |
| API-Sports (rugby, NBA, NHL, NFL odds) | 85 of 100 free calls/day per product | free | £0 |
| PinnWire | Pinnacle prices | free, inactive without the secret | £0 |
| ESPN, openfootball, football-data.co.uk, FIFA, Google Fonts | data and type | free | £0 |

| Total a month | Low | High |
|---|---|---|
| Max path | £89 | £164 |
| API-key path | £149 | £414 |

API-Football usage runs 1,000-4,000 calls/day against 7,500. What can run away: Elena double-firing (bug 18); the sprint has no daily spend guard.

## Timeline

**Tomorrow, Mon 26 Oct (one release, no model change)**
1. Groupings record: carry `wide`, `late`, `locked`, `lockAt` into graded rows; grade `late` apart (bug 1). UK-only best price (bug 2). Quota marker and stale fallback for the Card (bug 8). Locked slots from the archive (bug 9).
2. FIFA rankings refresh fixed and warning added (bug 4); rebuild.
3. Confirm the API-Football renewal on 30 Oct.
4. `ceo.yml` double-fire (bug 18); merge policy `unknown` class and `home-advantage.json` protection (bug 19).

**This week, 27-31 Oct**
1. Deploy guards for sports and groupings; refuse under 40% of yesterday's count; fail on empty App token (bug 7).
2. Price-only job at 06:00Z or `lockPrice` archived and graded (bug 10).
3. Strict headline on `pick == actual` (bug 3).
4. Season strings derived from the date and the API, with the unit test (bugs 5 and 6).
5. Unrated-club flag to six games (bug 11); native cups return no tested rate (bug 12).

**2-13 Nov (the model change)**
1. Home/away tilt by league family, replayed on 2025 and 2026 under the three gates. Expected 0.001-0.002 log loss and away picks in the 40-60% bands moving from 7 points under quote to on quote.
2. Tennis: retirement weight, provisional ratings, real-start rule, live own-band chip (bugs 13-15).
3. Cap `sports.py` CHECK at 27 Sep and re-tune (bug 16).
4. `tune_strengths.py --fit`, checked on the cup replay.

**16-27 Nov (the page)**
1. Load the three record files only when "How it went" opens (~4.2 MB off first paint).
2. Sticky compact bar on phones; 44 px tap targets.
3. Read-at time on every price, stale state after two hours, estimated prices in their own column, three labelled figures per group.
4. Open on the next unlocked window with a countdown.
5. One tier-ladder definition emitted by `build.py`.

**December**
1. Judge the Card on ~300 locked UK-priced legs; change the rules or retire it as a profit instrument.
2. Let the Monday refit switch on `home-advantage.json` when it passes.
3. Re-run the stage-of-season shrink test at 250+ fixtures.
4. Calibration gate to p(worse) 0.10 or two consecutive passes (bug 20).

**Before April 2027**
1. Tennis surface source, or `surfaceWeight` 0 for live pricing until one exists.
2. November added to the Rugby World Cup months; probe CFL, NBL, women's college basketball, Super League.
3. Second prior season for the 14 backfilled leagues.

**How you are stronger tomorrow.** Tomorrow's release does not change a forecast; it makes the record trustworthy, stops a stale ranking feeding every international, keeps the paid data flowing and halves the most expensive agent workload. The forecasting gain lands in the second week of November from the one signal the live record shows at five standard deviations, tested the way the rules require. The page work after that turns a correct site into one you can place bets from at 07:00 on a phone.
