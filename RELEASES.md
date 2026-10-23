# Releases

Newest first. Every release is an annotated git tag (`release-YYYY-MM-DD`,
with `-2`, `-3` for a second release the same day) and an entry here.

## Leg-property scan, no rule found (tag pending)

**What changed:** nothing a reader sees. Added `tools/leg_property_test.py` and a dated note recording which leg properties were tested against landed-v-quote and found not to separate.
**Evidence:** football replay, 2025-26 (321 pool legs) and 2026-27 (44): legs landed +7.4 / +11.8 pts above chance. No cut by home/away, price, chance band, tier or league holds on both seasons; model-at-or-below-market (+11.1 / +14.1 v +5.3 / -6.1) is already the 5-point cap. Cap 5 -> 0 would drop 54% of eligible legs (limit: a fifth), check season 44 legs against the 250 gate.
**Files:** claude/leg-property-scan-2026-10-23.md, claude/odds-groupings.md, tools/leg_property_test.py, RELEASES.md.
**Not changed:** groupings.py, every model constant.
**Roll back:** `git revert` the commit.

## Edge over bookmaker prices tested, none found (tag pending)

**What changed:** nothing a reader sees. Added `tools/odds_edge_test.py` and a dated note recording that the model has no edge over the price.
**Evidence:** football, 2025-26 (12,510 legs) and 2026-27 (1,749). Legs 2/4/6+ points above the bookmaker's fair chance landed below it: -2.0/-2.8/-2.2 pts (fit), -1.9/-1.9/-1.7 (check); model-favourite legs at 4+ points -3.6 / -6.5. Legs below the market landed above fair. 75%+ cell +3.1 pts on n 70 (p 0.26), 4 legs on check.
**Files:** claude/odds-edge-test-2026-10-23.md, claude/odds-groupings.md, tools/odds_edge_test.py, RELEASES.md.
**Not changed:** groupings.py, every model constant.
**Roll back:** `git revert` the commit.

## Weakest-sport scan, no model change (tag pending)

**What changed:** nothing a reader sees. Added a dated note on which sport or tour sits furthest below quote.
**Evidence:** WTA main-draw 70%+ landed 70.5% of 88 v 77.8% quoted (z -1.6); NFL 57.5% of 47 v 64.0%; college football 65.3% of 124 v 69.3%. None past 2 sigma; archive tests say the tennis shrink under-quotes and NFL calibration fails its gate. A change would mean fitting on the record (Rule 1).
**Files:** claude/weakest-sport-scan-2026-10-23.md, RELEASES.md.
**Not changed:** every model constant, shrink and list threshold.
**Roll back:** `git revert` the commit.

## 2026-10-22 Odds tab group rules backtest (tag pending)

**What changed:** nothing for readers. Double and Treble rules unchanged.
**Evidence:** replay of 44 groups on the full graded history: 32 won against about 30.2 stated (68.6% stated, 72.7% actual). Main groups 19 of 30 (stated 71.3%), alternatives 13 of 14. No settled live Double or Treble yet; retired bands 11 of 59 against 19.02 expected.
**Files:** `claude/odds-groupings.md` (note added), `RELEASES.md`.
**Not changed:** any code, rule or model number.
**Roll back:** `git revert` the commit; docs only.

## 2026-10-22 Daily List bar replay rerun (tag pending)

**What changed:** nothing for readers. The 80% league bar stays.
**Evidence:** `tools/list_bar_replay.py` rerun: 2025/26 identical to 12 Oct (80%: 94 picks, 81.9%; 75%: -2.4 pts, -7.5 to +2.5; 85%: -12.5 pts, -21.3 to -4.4). 2026/27 only 11 calls at 80% (81.8%); no league near 30 calls, so no per-league bar.
**Files:** `claude/daily-list.md` (note added).
**Not changed:** any code, bar or model number.
**Roll back:** `git revert` the commit; docs only.

## 2026-10-22 Calibration by band and sport, rerun (tag pending)

**What changed:** nothing in the model or site. A dated note re-running `calibration_bands.py` (football and nine other sports) on current history.

**Evidence:** football fit season 6,474 calls, bars 55-80% inside their intervals; 85%+ still over-confident (88.8% quoted, 69.2% landed, 39 calls). Check season (1,491 calls) 60-70% span now under-confident, 71.6% landed v 64.1% quoted, +7.5 [+1.1,+13.5], but the fit season disagrees so a refit would fail Rule 3. Baseball (-4.8 at 62%+) and hockey (-5.5) remain over-confident; list-bar sports calibrated or conservative.

**Files:** `claude/calibration-rerun-2026-10-22.md`, `RELEASES.md`.

**Not changed:** any constant, `calibration.json`, `sports.json`, code.

**Roll back:** `git revert` this commit.

## 2026-10-22 Championship gap-dependent draw lift tested and rejected (tag pending)

**What changed:** nothing in the model or site. A dated note and a reproducible script for the last untested Championship idea: extra draw mass when the sides are close.

**Evidence:** replay of en.2, 2023-24 to 2026-27, paired bootstrap 1500 reps. On the fit season (2025-26, 557 games) every lift is worse (k 0.1 +0.0012, k 0.3 +0.0044 log loss, p(worse) 0.92 to 0.97). 2023-24 is worse too; 2024-25 is flat; 2026-27 (95 games) gains at most 0.0010 at p(worse) 0.40. Predicted draw share already matches actual (27.5% v 26.8% in 2025-26).

**Files:** `claude/championship-draw-lift-2026-10-22.md`, `tools/championship_draw_lift.py`, `RELEASES.md`.

**Not changed:** any constant, `engine.py`, `calibration.json`.

**Roll back:** `git revert` this commit.

## 2026-10-22 Tennis hit rate: gap checked, surface weighting tested and kept (tag pending)

**What changed:** nothing in the model or site. A note recording why tennis (61.0% landed v 62.7% quoted, 828 matches) is not yet a real shortfall, and the surface-weight sweep behind keeping 0.3.

**Evidence:** gap z = -1.03 overall (ATP -0.32, WTA -1.06); worst slices (70%+ calls z -1.57, WTA September -1.46) are under 2 standard errors. Sweep of `surface_weight` 0 to 1.0 on the 2026 check set: 0.3 is best or within noise on both tours (WTA 0.2 is -0.0005 log loss, p(worse) 0.28, under the gain bar). The live record cannot be cut by surface: ESPN has none and every live match is priced as Hard.

**Files:** `claude/tennis-hit-rate-check-2026-10-22.md`, `RELEASES.md`.

**Not changed:** any constant, `tennis.json`, `build_tennis.py`, football.

**Roll back:** `git revert` this commit.

## 2026-10-22 Odds tab: Wider Fourfold so the strongest picks reach 2.00 (tag pending)

**What changed:** a fourth Wider kind, **Wider Fourfold** (four picks, 30%+ together), so the day's strongest picks can form a group at 2.00 or more. Three 80% picks pay about 1.69 after the bookmakers' margin, so the first 2.00 build left them out and made only 1, 2 and 3 groups for Fri to Sun. The fill still takes whichever kind is most likely to land.

**Evidence:** live build at 23:38 on 22 Oct: Fri 1 group, Sat 2, Sun 3. Four 80% picks pay about 2.0 and land about 41%, as often as a Treble of 75% picks. Tests updated in `tests/test_groupings_return.py`.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_return.py`, `RELEASES.md`.

**Not changed:** the 2.00 floor, leg rules, any model.

**Roll back:** `git revert` this commit.

## 2026-10-22 Odds tab: every group pays at least double the stake (tag pending)

**What changed:** every group's combined price must now be 2.00 or more (`MIN_RETURN`). The fill takes the most likely group of either Wider kind rather than Doubles first. A strict Double cannot reach 2.00 (two 75%+ picks pay about 1.6), so strict groups are now Trebles from picks at about 75%, floor 40%; Wider Treble floor 30%. Estimated prices (no bookmaker price) now carry a typical 5% bookmaker margin, so a group shown at 2.00+ should pay that when placed. Wider groups from the previous rule are rebuilt (`WIDE_RULE` 3). Odds tab wording explains the trade.

**Evidence:** Douglas, 22 Oct: "make all groups return at least double of stake". With a 5% margin per leg, 2.00 needs two picks of about 67% or three of about 75%; each group then lands about 43-48% of the time. `tests/test_groupings_return.py` (7 tests); older mechanics tests run with the floor off. Scratch run built Trebles at 2.02 and 2.09; page checked at 400px and 1200px.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_return.py`, `tests/test_groupings*.py`, `claude/odds-groupings.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** leg rules, any model, pricing sources, the record.

**Roll back:** `git revert` this commit, or set `MIN_RETURN = 1.0`.

## 2026-10-22 Odds tab: Wider groups use the strongest Daily List picks first (tag pending)

**What changed:** Wider groups now take the strongest legs whether or not a bookmaker has priced them. Before, priced legs went first and unpriced Daily List picks only when no priced group could be made, so Friday's groups used 71% priced legs while Cham (83%), Vipers (81%), Royal Vision (78%) and Connacht (89%) sat out. An unpriced leg's chance is its tested rate capped by the model, and its price is an estimate, marked with *. Wider groups published under the old rule are rebuilt on the next build, with the reason logged, not held.

**Evidence:** Douglas, 22 Oct: "why are you not using stronger picks from the daily list". Graded record: Daily List picks won 84.8% of 79 (wider leagues 82.0% of 61); clean 65-75% picks off the list won 70.9% of 220. Two new tests in `tests/test_groupings_minimum.py`.

**Files:** `groupings.py`, `tests/test_groupings_minimum.py`, `claude/odds-groupings.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the strict Double and Treble (still bookmaker-priced only), the 65% priced-leg rule, any model.

**Roll back:** `git revert` this commit.

## 2026-10-22 Replay test: core-league 65-75% calls, this season only (tag pending)

**What changed:** nothing in the product. `tools/core_midband_replay.py` (advisory) and a dated section in `claude/midband-calibration-2026-10-21.md`.

**Evidence:** walk-forward replay, core leagues, win picks. 65-75% calls: 2025/26 landed 67.3% of 343 against 69.1% quoted (on quote); 2026/27 (partial, cloud session) 82.3% of 51 against 69.0% (interval +1.5 to +23.4 points). Confirms the live finding for this season only, so rule 3 blocks a change. Re-run in December with the full check season. The lower leagues were already replayed on both seasons on 30 Sep.

**Files:** `tools/core_midband_replay.py`, `claude/midband-calibration-2026-10-21.md`, `RELEASES.md`.

**Not changed:** any model, curve, band or list rule.

**Roll back:** `git revert` this commit.

## 2026-10-22 Odds tab: at least three groups a day, with Wider groups to fill (tag pending)

**What changed:** every day on the Odds tab now gets at least three groups (`MIN_GROUPS`), today and each day ahead, where the legs exist. The strict Double and Treble are built first, unchanged. When they make fewer than three, **Wider Double** (two legs, 40%+ together) and **Wider Treble** (three, 27%+) fill the gap, Doubles first: legs with tested rate, model and bookmaker all 65%+ and the model at most 8 points above the market (`wide_leg`); failing that, Daily List picks with no bookmaker price yet (tested and model 75%+, estimated price, marked). They carry a red "Higher risk" label, say how often they should land, are re-checked on every build by their own rule, and are graded on their own line. The record headline is now the current kinds only (Doubles and Trebles; Wider groups beside it), with the retired Banker, Steady, Balanced and Stretch folded away ("11 won of 59").

**Evidence:** Douglas, 22 Oct: "always make sure there are 3 groups minimum every day and for the two days ahead". The board on 22 Oct had 9 priced legs at 65%+ on both reads for Friday, 9 for Saturday and 10 for Sunday, against 4, 3 and 0 at the strict 75%. A Wider Double of two 70% legs lands about half the time; the cards say so. `tests/test_groupings_minimum.py` (8 tests). A scratch run of the real `groupings.main()` built a strict Double and two Wider Doubles for one day; page checked at 1200px and 400px, no console errors.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_minimum.py`, `claude/odds-groupings.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the strict Double and Treble rules, any model, pricing sources. A day with fewer than four usable legs still gets fewer than three groups: there is nothing to build them from.

**Roll back:** `git revert` this commit, or set `MIN_GROUPS = 0` to stop the fill.

## 2026-10-22 Bookmaker prices from API-Football for every fixture it lists (tag pending)

**What changed:** the fixture board's bookmaker line and "Against the bookmakers" panel now draw on API-Football as well as football-data.co.uk. Each build reads every Match Winner price API-Football carries for today and the next four days (`/odds?date=`, ten fixtures a page, `odds.af_odds_day`), cached in `.afcache` for 90 minutes (today, tomorrow) or 4 hours (further out), and matches each to a board fixture on both team names and a kick-off within 90 minutes (`odds.match_af`; ambiguous matches are dropped). football-data.co.uk still prices first where it has the game. The Odds tab reads the same prices before falling back to its one-fixture call, so it spends fewer calls and finds more legs. Each panel says which source and how many bookmakers.

**Evidence:** on 22 Oct, 0 of 2,188 upcoming fixtures carried a price (football-data.co.uk covers 22 divisions, updated Friday and Tuesday; it peaked at ~180 fixtures on Fridays). The API-Football plan allows 7,500 calls a day and the builds used under 100. Expected cost: about 100-250 calls a build, inside the allowance. `tests/test_af_odds.py` (8 tests: parsing, paging, cache, stale copy kept, matching). A local build with simulated API-Football answers priced 56 of 66 fixtures (the other 10 had no kick-off time); page checked at 1100px and 400px.

**Files:** `odds.py`, `sources.py` (records API paging), `build.py`, `groupings.py`, `index.html`, `tests/test_af_odds.py`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** no price feeds any model, the Daily List or the reserve. The value tag still comes only from football-data.co.uk prices, the source its gate was tested on. The group leg rules are unchanged.

**Roll back:** `git revert` this commit. Prices go back to football-data.co.uk only.

## 2026-10-21 Odds tab: rugby legs priced from any union market (tag pending)

**What changed:** a rugby leg whose competition is not named in any of The Odds API's market titles (URC and Top 14 this week) now tries every active rugby union market instead of none. The event is still matched on both team names and kick-off, so a wrong market prices nothing, and calls stay inside the existing daily (15) and monthly (480) credit caps. The build report now lists the API's active rugby markets (`rugbyKeys`) and any rugby competition with no market (`noKey`), so a gap shows in the next build's output.

**Evidence:** the 19:11 build on 21 Oct had five rugby legs at 81-91% (Connacht, Stormers, Leinster, Ospreys, Toulouse) and made no Odds API calls for them: no market title matched. That left Saturday one safe leg short of a Double. Two new tests: a URC leg is priced from an unnamed union market; a market without the right teams prices nothing.

**Files:** `groupings.py`, `tests/test_groupings.py`, `RELEASES.md`.

**Not changed:** the leg and group rules, football pricing, any model.

**Roll back:** `git revert` this commit.

## 2026-10-21 Odds tab: groups three days ahead, re-checked on every build (tag pending)

**What changed:** the Odds tab now builds groups for today and the next three UK days (`DAYS_AHEAD`), not today and tomorrow. Every build (six a day) first reads the groups the last build published and re-checks each one against the current board and prices (`recheck()`). A group that still passes every rule keeps its place, marked "Still holds", so a group someone has placed does not reshuffle under them. One that fails is dropped, the reason is logged in plain words under that day ("Stade Toulousain: price 1.40, the bookmakers now give 68%, under 75%"), and its slot is rebuilt from the legs left ("Replacement"). A group with a leg already kicked off is kept as published ("Underway"). Each leg shows its price when the group was first shown ("was 1.04"). If a price source fails for one build the last confirmed price stands, marked "last price", rather than the group being dropped. When a first choice fails with nothing to replace it, the second choice is promoted. Day buttons are now short (Today, Tomorrow, Fri 23) with a count of groups.

**Evidence:** `tests/test_groupings_review.py` (11 tests: hold, price move, drift replacement with reason, game leaving the board, underway, no game reused, failed price source, previous-build reading). End-to-end on a local build's real board with synthetic prices: build 1 published two Saturday Doubles; build 2, with one leg drifted to 1.40, dropped the first with that reason, held the second and promoted it. Odds tab checked in Chromium at 1280px and 400px, no console errors.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_review.py`, `claude/odds-groupings.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any model, the leg and group rules (`safe_leg`, floors, odds ranges), pricing sources, grading, the archive or the record. The record still grades each day's groups as they stood at that day's first build. API-Football use rises to cover four days of odds, about 20 to 80 calls a build against 7,500 a day.

**Roll back:** `git revert` this commit. The next build goes back to two days and rebuilds every group from scratch.

## 2026-10-21 Odds tab rebuilt: Double and Treble, groups built to land (tag pending)

**What changed:** the Odds tab now builds two kinds of group, each labelled with its risk. **Double**: two picks, at least 60% to land together, "Lowest risk". **Treble**: three, at least 50%, "Low risk". Each card says how often it should land ("about 7 in 10"). A pick needs its tested rate, the model and the bookmaker's fair chance all at 75%+, the model no more than 5 points above the market, and (football) none of the Daily List's blind-spot exclusions. No group on a day when nothing clears. Groups sit above the accumulator. Banker, Steady, Balanced and Stretch are retired and stay in the record as "(retired)". Separately, an advisory study of whether 60-80% calls land above quote.

**Evidence:** 4-21 Oct the groups won 11 of 58 (18.7 expected); legs landed 72.4%, the bookmakers' fair rate. Legs at 1.45-1.60 landed 61%, 1.80+ 47%; legs the model rated 5+ points above the market 70%, at or below it 82%. Archived legs that pass the new gate landed 42 of 49 (85.7%, average 1.15). Replay on the full graded history: 31 of 43 groups won. Mid-band study: 60-80% calls on quote overall (68.3% v 66.8%, n=783); core-league 65-75% calls landed 87% of 83 against about 69% quoted, this season only. `claude/odds-groupings.md`, `claude/midband-calibration-2026-10-21.md`.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings.py`, `tests/test_groupings_banker.py`, `tools/groupings_backtest.py`, `tools/midband_calibration.py`, `claude/odds-groupings.md`, `claude/midband-calibration-2026-10-21.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any model, calibration, the Daily List, pricing sources, grading rules, the archive or record files. Bookmaker prices only veto legs; they never feed a model.

**Roll back:** `git revert` this commit. The next build rebuilds the old groups; archived Double and Treble days stay graded under their names.

## 2026-10-21 Odds tab pricing re-check: no further free source found (tag pending)

**What changed:** nothing in the product. A dated section in `claude/odds-pricing-coverage-2026-10-12.md`.

**Evidence:** today's pool in the sandbox (no API-Football or Odds API key): 8 football legs, 8 priced by ESPN soccer (10 calls). ESPN tennis (ATP 162 matches, WTA 124) and the rugby scoreboards carry 0 odds blocks, so ESPN cannot price either. Of 291 grouped legs 4-21 Oct, the football legs still unpriced were small leagues no book lists (Lebanon, Lesotho, Myanmar, Burundi, Latvia 1. Liga, Cambodia, Russia second tier, Tercera RFEF) plus Al Ittihad v Shabab Al-Ahli, whose ESPN names match the existing matcher, so it was not a matching gap. Looser matching would add wrong-match risk (Rule 6) for no gain. Tennis and rugby depend on the Odds API key.

**Files:** `claude/odds-pricing-coverage-2026-10-12.md`, `RELEASES.md`.

**Not changed:** any source, matcher, model, group rule, record or archive.

**Roll back:** `git revert` this commit.

## 2026-10-21 Ratings test: capping blowout goals, rejected (tag pending)

**What changed:** nothing in the product. A dated note in `claude/tuning-evidence.md` and the harness `tools/goal_cap_eval.py`.

**Evidence:** goals per side per match capped at 5, 4 and 3 when building ratings, paired and bootstrapped under the live curve and with the curve refitted per cap. 2025/26 fit (6,474): cap 5 -0.0002, cap 4 +0.0005, cap 3 +0.0025. 2026/27 check (1,490): +0.0005, +0.0011, +0.0031, p(worse) 0.94-0.98. Fails the gain gate and rule 3.

**Files:** `claude/tuning-evidence.md`, `tools/goal_cap_eval.py`, `RELEASES.md`.

**Not changed:** any constant, model, calibration or record.

**Roll back:** `git revert` this commit.

## 2026-10-21 Free-source check for uncovered leagues: none feasible (tag pending)

**What changed:** nothing in the product. `claude/data-expansion-plan.md` gains a dated progress line.

**Evidence:** the five top flights previously without a source (Croatia, Hungary, Serbia, Ukraine, Korea) are now on the board via `sources.AF_NEW`. football-data.co.uk `new/` still lists the same 16 leagues, all already in `sources.FDX` or covered by ESPN at matching volume. TheSportsDB's free key was truncated on 12 Oct. Nothing free covers Poland 2, the 3. Liga or the UAE.

**Files:** `claude/data-expansion-plan.md`, `RELEASES.md`.

**Not changed:** any source, model, name map, Daily List rule, record or archive.

**Roll back:** `git revert` this commit.

## 2026-10-21 A failed ESPN day no longer counts as walked (tag pending)

**What changed:** `sources.topup_current` marked every day up to yesterday as walked even when ESPN failed on it (all hosts, after the retry), so a one-day outage silently lost that day's results from the season-so-far cache for good, beyond the 3-day rescan. Now `through` stops just before the first failed day, so the next build asks again, and the failure is logged. A competition that has never answered (dead slug, no cache) is saved as before, so it does not re-walk the season every build.

**Evidence:** `tests/test_topup_failures.py` (fake failing source): a failed day holds the marker back, a clean walk advances it, a total outage keeps the old marker, a dead slug is saved as before. nametest and the source-failure tests pass.

**Files:** `sources.py`, `tests/test_topup_failures.py`, `RELEASES.md`.

**Not changed:** any model, constant, retry policy, or committed cache.

**Roll back:** `git revert` this commit.

## 2026-10-21 Fixture audit: double-booked clubs and case-variant spellings, no fix (tag pending)

**What changed:** nothing in the product. A dated section in `claude/data-integrity.md` records the audit of `predictions/2026-10-21.json`.

**Evidence:** 1,999 rows, no exact, reversed or case/accent-folded duplicates, no unrated rows, no early kick-offs, `nametest.py` passes. Real source faults: Tanzania (af.567, 24 Oct) and Leatherhead (en.7i, 27 Oct) have clubs in two games at one kick-off; 9 rescheduled games leave a stale earlier row; the 18 Oct archive holds four fixtures twice under upper-case spellings priced differently. None is on the Daily List and none has recurred since 18 Oct.

**Files:** `claude/data-integrity.md`, `RELEASES.md`.

**Not changed:** `sources.py`, `LIVE_NAMES`, the archive key, any model, record or archive. The source could not be re-read here and a guessed fix would risk a wrong match.

**Roll back:** `git revert` this commit.

## 2026-10-21 Rugby union home advantage tested at the grid edge, not shipped (tag pending)

**What changed:** nothing in the product. A dated note, `claude/rugby-home-advantage-2026-10-21.md`, records a test of rugby's Elo settings after the planner flagged 33 of 40 landed v 68% quoted.

**Evidence:** history only. Rugby's fitted home advantage (100) sits on the edge of the search grid. Widened to 150 (k 16) it beats the live setting on the check season by 0.007 log loss (p(worse) ~0.07, 773 games), but strong calls turn from underquoted to overquoted by 2-3 points (80%+: 83.8% landed v 87.3% quoted) and the list bar would rise to 85%. That fails the honesty guard, so no change. K and season carry-over: flat or worse.

**Files:** `claude/rugby-home-advantage-2026-10-21.md`, `RELEASES.md`.

**Not changed:** any model, constant, `sports.json`, the Daily List, records or archives.

**Roll back:** `git revert` this commit.

## 2026-10-20 Croatia, Hungary, Serbia, Ukraine and Korea: current season actually reaches the board (tag pending)

**What changed:** the five top flights added this morning showed no fixtures and no current season. Their current season reads the shared API-Football date pool, whose rows pass through the day cache (`_compact` / `_expand`), and the cache kept no country. The new country guard in `af_rows` then saw an empty country, called every row "wrong country" and dropped the whole league. Prior seasons come from a separate call that keeps the country, so they arrived and ratings moved, while this season stayed empty. Visible symptom: Shakhtar Donetsk went into Inter v Shakhtar (Champions League, 21 Oct) with "form: not yet available" and no "This season" row. The cache now keeps the country as a tenth field; nine-field day files written earlier still read, and their rows are judged by the rows that carry a country. A feed with no country at all, or any wrong one, is still dropped loudly.

**Evidence:** reproduced offline: a Ukrainian fixture through `_compact` / `_expand` and the pool returned no rows before the fix and both rows after. Archives since the 12:13 UTC build hold 0 rows for all five leagues, while their second divisions from the same pool (af.334, af.287, af.272, af.293) hold 80-99 each. Open days refetch within `AF_DAY_TTL` (45 min), so the first build after merge carries countries. Three new tests fail on the old code. `nametest.py` and 321 unit tests pass. Not run end to end: no API key in this sandbox.

**Files:** `sources.py` (`_compact`, `_expand`, guard in `af_rows`), `tests/test_af_new_leagues.py`.

**Not changed:** any probability, constant, calibration, the List bar, `NEW_BOARD_ONLY`, records or archives. Expect Champions and Europa League ties involving clubs from these five countries to reprice once their current form arrives.

**Roll back:** `git revert` this commit.

## 2026-10-20 Accumulator calculator on the Odds tab (tag pending)

**What changed:** the Odds tab has an accumulator calculator above the groups. Type a selection and its price in fractional (1/7, 2/11), decimal (1.14), evens or American (+150) form, add as many rows as needed, and it shows the combined odds (decimal and nearest fraction), the return and profit at the tab's stake, and the chance the combined price implies. Each group leg has an "Add to acca" link that drops it in. Rows persist in the browser (`og-acca`). A price it cannot read is marked and left out of the total.

**Evidence:** checked in a headless browser at 1280px and 400px with test groupings: 1/7, 2/11, evens and 1.14 give 3.08, £30.79 from £10, matching the hand calculation (8/7 x 13/11 x 2 x 1.14). No console errors. `nametest.py` passes.

**Files:** `index.html` (calculator styles, `accaDec` / `accaMount` / `accaAdd`, mount in `renderOdds`, leg button in `ogCard`).

**Not changed:** any model, probability, the groups, `groupings.py`, records or archives. Typed prices stay in the viewer's browser and never feed anything.

**Roll back:** `git revert` this commit.

## 2026-10-20 Tests for rankings.py (tag pending)

**What changed:** nothing a reader sees. `rankings.py` (FIFA and ATP adjustments, FIFA name mapping, release refresh, ESPN tennis rank parsing) had no tests; `tests/test_rankings.py` adds 22, offline (`_get` and the FIFA file are patched).

**Evidence:** the module was the largest untested one that feeds a model number (0 of 169 lines covered). Tests pin the formulas to `FIFA_W` / `ATP_W`, the missing-ranking fallbacks, the 151 cap, the 21-day refresh rule, newest-id selection and the failure paths. All pass; no bug found, so no code changed. `nametest.py` and the full unittest suite pass.

**Files:** `tests/test_rankings.py`.

**Not changed:** any model constant, `rankings.py`, records or archives. Left as is: `rankings.py` opens files without closing them (harmless ResourceWarning).

**Roll back:** `git revert` this commit.

## 2026-10-20 Log why tennis tournaments miss an Odds API key (tag pending)

**What changed:** `groupings.py --probe` (and every build's `sources.oddsApi`) now lists the active `tennis_*` keys from the free /sports list and the tour + tournament of every unpriced tennis leg that matched no key (`tennisKeys`, `noKey`). Matching also reads the key's own words, not only the title. Prices still never feed a model.

**Evidence:** no model number changed. Not tested against the live list: no key in this sandbox, so the cause of the 19 Oct misses (Almaty, European Open, Japan Open) is not yet known. Likely suspect: The Odds API carries mainly Slams and Masters, so ATP 250/500 events may have no key at all, and no matching fix could price them. The next CI probe will show it. `nametest.py` and the unit tests pass.

**Files:** `groupings.py`, `tests/test_groupings.py`.

**Not changed:** any probability, the ledger caps, the matching of rugby or NRL, records or archives.

**Roll back:** `git revert` this commit.

## 2026-10-20 Croatia, Hungary, Serbia, Ukraine and Korea top flights from API-Football (tag pending)

**What changed:** HNL, NB I, SuperLiga, Ukrainian Premier League and K League 1 had ratings slots but no source (openfootball 404s, no football-data file, ESPN has none), so no fixture ever appeared. They now read from API-Football (ids 210, 271, 286, 333, 292). Board only: off the Daily List and the reserve (`build.NEW_BOARD_ONLY`), out of the calibration fit (`tune.codes`), until a replay earns a place. A feed whose country is not the expected one is dropped with a warning, because the ids were set by hand and could not be checked from this sandbox (no key). The UAE is not added: its Pro League already arrives as `af.301`, and the other divisions of all six countries are in `af-leagues.json`.

**Evidence:** no model number changed. API allowance: current seasons ride the shared date pool, so 0 extra calls per build; the two finished seasons each are 5 x 2 = 10 one-off calls, then on disk. Not replayed: no API key here, so no hit-rate claim is made. Neighbouring ids in `af-leagues.json` (NB II 272, Prva Liga 287, Persha Liga 334, K League 2 293) fit the pattern. `nametest.py` and 295 unit tests pass; a fast build runs.

**Files:** `sources.py` (`AF_NEW`, country guard in `af_rows`), `build.py`, `tune.py`, `tests/test_af_new_leagues.py`.

**Not changed:** any probability, constant, calibration, strength, the List bar, UAE, records or archives. Replaying these five (and the first-day name check of their clubs against `LIVE_NAMES`) is the next step before any List place.

**Roll back:** `git revert` this commit.

## 2026-10-20 Own-band Daily List admission for the other sports (tag pending)

**What changed:** a rugby, basketball, NBA or WNBA pick now reaches the Daily List only if its own 5-point band landed 80% in testing, not only "this level and everything above it". Bars: rugby 70% -> 80%, college basketball 70% -> 85%, NBA 75% -> 80%, WNBA 80% -> 85%. NFL and college football (off the List) unchanged. Picks that miss go to the reserve if 62%+. Probabilities are unchanged.

**Evidence:** held out (bar set on Jul 2024-Jun 2025, applied to games since Jul 2025): rugby 451 picks landing 79.6% -> 247 landing 84.2% (dropped 204 landed 74.0%, p(worse) 0.002); college basketball 3,792 at 78.9% -> 1,884 at 87.4% (dropped 1,908 landed 70.5%, p 0.000). NBA and WNBA are unchanged on the fit season alone; their move rests on the reverse direction only. Cost is volume: roughly 40-60% fewer picks per sport. Full tables in `claude/own-band-admission-2026-10-20.md`.

**Files:** `sports.py` (`own_bands_clear`, `list_threshold`, `stored_threshold`), `tests/test_sports.py`, `tools/own_band_replay.py`, `claude/own-band-admission-2026-10-20.md`, `RELEASES.md`.

**Not changed:** any probability, calibration, `sports.json`, football, tennis, records or archives.

**Roll back:** `git revert` this commit.

## 2026-10-20: College football List shortfall located; no change (tag pending)

**What changed:** a note only. The planner's 30 of 41 against 33.6 on the college football Daily List was already acted on (80% bar on 13 Oct, off the List on 19 Oct). No code or model change.

**Evidence:** the shortfall is a uniform 4 to 11 points under quote in every band (70-75%: 6/10 v 73%; 75-80%: 5/7 v 77%; 80-85%: 8/11 v 83%; 85%+: 11/14 v 91%), home picks 23/31 and away 7/10, 12 picks at the 80% bar 9 landed. No cut isolates it, and at n=41 it is z -1.5. Live record used only to locate, never fitted. Full table in `claude/cfb-list-shortfall-2026-10-20.md`.

**Files:** `claude/cfb-list-shortfall-2026-10-20.md`, `RELEASES.md`.

**Not changed:** probabilities, `LIST_FLOOR`, `LIST_OFF`, the tested-rate display on rows.

**Roll back:** `git revert` this commit.

## 2026-10-20 Elena answers and acts; the Groups & Odds Desk opens (tag pending)

**What changed:**
- **Elena, the CEO, is a working agent.** `ceo.yml` runs when Douglas opens or comments on an issue labelled `ceo`. Claude, as Elena, reads the whole repository and the office's data, answers on the issue, ships a change herself through `agents/open_pr.sh` and the merge gate (so only if every check and the Evaluation pass), and delegates bigger work as `office-backlog` issues for named agents, which the next sprint works before anything else. `agents/ceo_prompt.py` passes her only Douglas's words and her own earlier replies; the repository is public. She runs on Opus with 80 turns.
- **Groups & Odds Desk.** Two new working agents join Oscar and Jade: Kofi, Value Analyst (does the model have any edge over bookmaker prices, measured on history?), and Hannah, Leg Selector (which legs land at or above their quote?). Each has a standing task, the HQ planner gives the desk tasks by sport, price range and group band, and one desk member works every sprint (`pick_task.DESK`).
- **Bigger sprint:** `SPRINT_SIZE` 4 to 5, plus the desk's place: up to six agents a day.
- Oscar's standing task updated for the 19 Oct rule (unpriced legs are never grouped).
**Evidence:** dry runs of the picker with HQ up and down; `tests/test_ceo_prompt.py` (strangers' comments and Elena's status lines never reach the prompt, delegation drops unknown owners and caps at five) and new sprint-selection tests; full suite and `nametest.py` pass. `ceo.yml` validated as YAML; its first real run is the check that matters.
**Files:** `.github/workflows/ceo.yml` (new), `agents/ceo_prompt.py` (new), `agents/pick_task.py`, `tests/test_ceo_prompt.py`, `tests/test_pick_task.py`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the merge gate, the Evaluation, protected paths, any model or record. Prices still never feed a model.
**Roll back:** `git revert` this commit. To pause Elena alone, remove the `ceo` label from an issue or disable `ceo.yml` in Actions.

## 2026-10-20 Office sprint works HQ's ranked backlog, four agents a day (tag pending)

**What changed:** the office agents now work on what the live record says is wrong, every day, instead of all fourteen running generic standing tasks on one day and then resting for a week. Each morning HQ's planner (footyalmanac-hq `scripts/planner.py`) measures every gap between quoted and landed: the Daily List by sport, football 5-point bands, leagues, tennis tours, the other sports and the Odds tab's legs, each as a z-score so small samples don't shout. It publishes the ranked tasks, each with its evidence and the testing rules, as `data/backlog.json` on HQ's Pages; the README's priority list (own-band admission, tennis surface, coverage, Odds API keys) sits below the measured gaps until an agent ships each one. `agents/pick_task.py` reads it after owner issues and pipeline health, and the sprint runs the four agents whose best free task ranks highest (`SPRINT_SIZE`). When HQ is down or its backlog is over 48 hours old, the picker uses its own scoreboard picks as before.
**Evidence:** no agent pull request from 13 to 19 Oct: every sprint planned, found nobody with work (all fourteen ran on 12 Oct, then the 7-day rest) and stopped. Of the 14 agent pull requests on 12-13 Oct, none changed a model; nine were notes or scripts. Today's backlog (dry run): college football List 30 of 41 against 33.6 expected, rugby union landing above its quotes, then the four priorities; football is on its quotes in every band (widest 65-70%, z +1.4). `tests/test_pick_task.py` (new), full suite and `nametest.py` pass.
**Files:** `agents/pick_task.py`, `tests/test_pick_task.py`, `.github/workflows/office-agents.yml` (comment only), `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the merge gate, the evaluation gate, the cooldown, any model or record. Every task still ships only through the same checks.
**Roll back:** `git revert` this commit; `SPRINT_SIZE=14` in the job environment restores the old breadth without a revert.



## 2026-10-19 Fixture rows tidied: status boxes fit, form in green / yellow / red, final and predicted scores, plain ratings (release-2026-10-19-7)

**What changed:**
- The middle cell of every row is wider (72px to 96px), so status boxes such as RESULT DUE are no longer cut off on the right, and scores no longer trail off.
- Form squares: green win, yellow draw, red loss.
- A settled football pick shows "Final 1–0" and, under it, the model's "Pred 2–0"; other sports show the score, tennis "Golubic won".
- Ratings read "rating 1917" instead of "Elo 1917 · 252 played". The match count shows only when a rating rests on few results ("only 15 matches"); hovering the rating explains the scale (about 1500 for a newcomer; 100 points higher wins about 64% of the time), and each sport's row detail says the same.
- On a phone, the day header's "So far" line wraps instead of running off the edge.
**Evidence:** checked in headless Chrome at 1280px and a true 400px on today's Daily List and reserve. `nametest.py` passes.
**Files:** `index.html`, `RELEASES.md`.
**Not changed:** any number, rule or record.
**Roll back:** `git revert` this commit.

## 2026-10-19 Honest cup numbers: domestic cup ties carry their own calibration (release-2026-10-19-6)

**What changed:** domestic cup ties (API-Football cups) now quote what cups actually deliver. A second calibration curve, on top of the league one, pulls confident cup favourites down: a raw 75% favourite now shows about 59%, a close tie barely moves. The cup replay's Daily List gate reads the same calibrated numbers (cups stay off the list unless it passes). Continental cups (Champions League and others) are unchanged: there is no replay evidence on them.
**Evidence:** `tools/cup_calibration.py` on the cup replay's 1,968 priced ties, fitted on 747 before 1 Jul 2026, checked on 1,221 after, paired against no cup adjustment: -0.0047 log loss, p(worse) 0.164, all tune.py gates passed. Check ties quoted 60%+: 62.0% landed against 69.9% quoted before, 66.7% against 63.9% after. A single temperature was tried first and failed (p(worse) 0.43). `tests/test_cup_calibration.py`; full suite and `nametest.py` pass.
**Files:** `engine.py`, `build.py`, `tools/cup_calibration.py`, `tests/test_cup_calibration.py`, `claude/tuning-evidence.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** league football, the league calibration, internationals, continental cups, every other sport.
**Roll back:** `git revert` this commit, or set `engine.CUP_CALIBRATION = None`.

## 2026-10-19 Recent form on football rows; the cup replay keeps every tie (release-2026-10-19-5)

**What changed:** every football row (boards and the Daily List) shows each side's last five league results as W / D / L squares, oldest first, on a line of their own, and a yellow **Hot** badge when the side won each of its last three. The expanded team sheet adds last-three points. Display only, Douglas's choice: the model's numbers are unchanged, because favourites on three straight wins landed 68.2% against 70.8% quoted (`claude/tuning-evidence.md`). The cup replay (`build.cup_replay`, version 4) now keeps every priced tie's probabilities and result in `current/af-cup-replay.json`, so a cup calibration can be fitted on one half-year and checked on the other; nothing is fitted yet.
**Evidence:** checked in headless Chrome at 1280px and a true 400px (Dortmund four wins and Hot; Roma WWWWD, not Hot). Full suite and `nametest.py` pass.
**Files:** `index.html`, `build.py`, `RELEASES.md`.
**Not changed:** any probability, the list, grading.
**Roll back:** `git revert` this commit.

## 2026-10-19 Hot form, big clubs and cups tested against the quoted chance: nothing shipped (release-2026-10-19-4)

**What changed:** nothing a reader sees; a dated section in `claude/tuning-evidence.md`.
**Evidence:** frozen snapshot, both seasons, favourites quoted 60%+ (1,121). Won all of last 3: 68.2% landed against 70.8% quoted; won 0-1 of last 3: 66.7% against 66.4%. Big clubs (last season's top four): 72.3% against 70.1% (inside noise), 78.1% against 77.6% at 70%+. Cups: live 60%+ 56.5% against 69.7%, replay clean 75%+ 47% and 80%.
**Files:** `claude/tuning-evidence.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any model number.
**Roll back:** `git revert` this commit.

## 2026-10-19 Football team news (injuries, suspensions) tested: nothing shipped (release-2026-10-19-3)

**What changed:** nothing a reader sees. Two tools: `tools/af_team_news.py` (fetches API-Football injury lists and player minutes; run from a workflow, output kept out of the repo) and `tools/team_news_eval.py` (backtest), and a dated section in `claude/tuning-evidence.md`.
**Evidence:** 8 leagues, 730 calls, 2025-26 fit (2,919 fixtures) and 2026-27 check (470), live calibration, paired. Players missing by count: no effect. By last season's minutes: -0.0002 on the fit season (under the 0.0005 bar), -0.0010 on the check (p(worse) 0.16), with a wrong-signed attack effect, found after widening the search. New absences since the previous match: no effect. Not shipped; revisit at about 1,500 check fixtures.
**Files:** `tools/af_team_news.py`, `tools/team_news_eval.py`, `claude/tuning-evidence.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any model number, the live build, the API budget (730 of 7,500 calls used once).
**Roll back:** `git revert` this commit.

## 2026-10-19 Football form by stage of season: tested, nothing shipped (release-2026-10-19-2)

**What changed:** nothing a reader sees. A dated section in `claude/tuning-evidence.md` and a line in `CLAUDE.md`'s tested-and-rejected list.
**Evidence:** frozen snapshot `aa19d05b`, live calibration, paired. The model is weakest at games 4-6 of a season in both seasons (log loss 1.055 / 1.053 against about 1.02 elsewhere; top pick 45-46% against 49%). Counting this season faster or adding more form makes it worse; counting it slower helps games 4-6 on 2025/26 (-0.0031, p 0.01) but not on 2026/27 (+0.0013), so it fails the confirm-on-the-current-season rule; ignoring this season is far worse (+0.0138 / +0.0068). Team news (injuries, line-ups, transfers) is the untested lever.
**Files:** `claude/tuning-evidence.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any model number.
**Roll back:** `git revert` this commit.

## 2026-10-19 Odds groups rebuilt after the 13-18 Oct collapse; tennis grading fix; college football off the Daily List (release-2026-10-19)

**What changed:**
- **Odds groups:** legs come from football and rugby only; tennis, college football and NFL legs landed far under their tested rates. A leg's chance is also capped at the model's own number (it used to be the tested rate pulled toward it), on top of the bookmaker fair-chance cap merged earlier today (#47): the lowest of the three counts. A new **Banker** group, three legs paying 1.5 to 2.5, is built first each day: the group built to land most often. Legs settle from each sport's full graded history, so days older than two weeks no longer revert to Pending (5 Oct now reads lost, 4 of 5).
- **Tennis grading:** a match is graded only if both priced players played it. ESPN reuses a match id when a draw slot changes hands; 7 of 765 stored grades were against someone else's match (5 losses, 2 wins, including Daily List pick Jovic on 12 Oct) and are now void.
- **Daily List:** college football is off it, as tennis has been since 15 Oct; its Firm+ picks go to the reserve.
**Why:** Douglas, 19 Oct: the groups won 0 of 25 from 13 to 18 Oct against about 8 expected.
**Evidence:** legs 12-18 Oct: football 73.1% landed against 77.2% quoted (78), tennis 61.8% against 85.4% (34), college football 53.8% against 85.7% (13), NFL 40.0% against 75.7% (5). Whole archive (234 legs): 73.1% against 79.8%, shortfall in legs quoted 80%+. College football on the Daily List won 30 of 41 against 33.6 expected. Tennis re-tested on 1,096 Sep-Oct main-draw matches: 75%+ landed about 85%, live prices match the replay, a confidence refit fails the tennis gates, so no tennis model change. Write-up: `claude/odds-groupings.md`. Tests: `tests/test_groupings_banker.py`, `tests/test_tennis_slot.py`, `tests/test_groupings.py` updated; full suite passes; `nametest.py` passes. Odds tab checked at 1280px and 400px.
**Files:** `groupings.py`, `score_tennis.py`, `sports.py`, `index.html`, `tests/`, `claude/odds-groupings.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any model, rating, calibration or tested band; football's Daily List; prices never feed a model.
**Roll back:** `git revert` this commit; `sports.LIST_OFF = set()` restores college football to the list alone.

## 2026-10-19: Odds tab groups use honest chances (tag pending)

**What changed:** each leg's chance in a group is now the lower of its tested rate and the bookmaker's fair chance (1 / price, less the book's margin, worked out from every outcome's price where the source gives them, otherwise 5%). Legs with no bookmaker price are never grouped, with no fallback. The bonus for legs whose tested rate beat the bookmaker is gone. HQ regroups with these same rules from the same pool, so it follows.

**Evidence:** from 4 to 18 Oct, 8 of 48 settled groups won against 15.9 expected (about 2.4 standard deviations short), and 48 staked returned 33.38. Legs won 73.1%, while the tested rates said 79.8% and bookmaker prices implied 75.7%, about 72% without their margin. Legs priced 10+ points under the tested rate won 66.7%. Estimated tennis legs won 68.5% against 83.4% stated, and college football 63.6% against 84.7%. A replay on the archived legs gave 4.4 expected and 4 won under the new rules (22 groups), against 14.6 expected and 8 won under the old ones (43 groups). That's directional only: a small sample, chosen by the old rules.

**What a reader sees:** lower chances. Today's pool gives Steady 2.96 at 25% (the old rules said 30–35% at similar odds), and fewer groups on days with few priced legs. These are honest figures, and at bookmaker prices they still imply a loss on average.

**Files:** `groupings.py`, `index.html` (the group chance label and the "How the groups are picked" note), `tests/test_groupings.py`, this entry.

**Not changed:** any model, probability, the Daily List, or past groups and their record.

**Roll back:** `git revert` the commit.


## 2026-10-19: The Odds API prices tennis and rugby on the Odds tab (tag pending)

**What changed:** when the `ODDS_API_KEY` secret is set, the Odds tab prices tennis, rugby union and rugby league legs that API-Football and ESPN did not price, using the average of UK bookmakers' match odds from The Odds API. Without the key, nothing changes. HQ already reuses the Odds tab's priced pool, so it picks these prices up without a change of its own.

**Credits:** the free plan has 500 a month. The free `/sports` list picks only the tournaments and leagues with an unpriced leg, at one credit each (UK region, match odds). Each one is cached for 4 hours in `.afcache`. A ledger caps spending at 15 credits a UK day and 480 a month, and calls stop when the API reports fewer than 20 left.

**Files:** `groupings.py`, `index.html` (the Odds tab's price note), `tests/test_groupings.py`, this entry.

**Not changed:** any model, probability, the Daily List or the records. Prices never feed a model.

**Roll back:** delete the secret, or `git revert` the commit.


## 2026-10-15: Tennis off the Daily List (tag pending)

**What changed:** no tennis match makes the Daily List, on either tour. Main-draw calls from 62% with both players rated go to the reserve instead, graded as their own group. The site's List note names tennis among the sports not on the list. `build_tennis.LIST_ON` turns a tour back on, and `LIST_MIN` (75%) is kept.

**Evidence:** tennis List picks won 39 of 51, against 42.1 expected from their quoted chances. WTA won 18 of 27 (mean quote 83%, 22.3 expected) and ATP 21 of 24 (19.8 expected). A higher bar doesn't help: across all graded tennis calls, 85%+ won 22 of 27 (81.5%) at a mean quote of 89%, and 90%+ produced only 9 calls in three weeks. The backtest bands (WTA 75%+ landing 89.9%) overstate live tennis.

**Files:** `build_tennis.py`, `daylist.py` (the coverage reason for tennis is now "boardOnly"), `index.html`, `tests/test_tennis_names.py`, this entry.

**Not changed:** tennis ratings, probabilities, the board, records or archives. Past tennis List picks stay in the record.

**Roll back:** `git revert` the commit, or set a tour in `LIST_ON` to True.


## 2026-10-13: College football Daily List bar 70% -> 80% (tag pending)

**What changed:** college football picks need 80% confidence to make the Daily List, up from 70%. Picks from 62% to 80% sit in the reserve. Every other sport keeps its bar. A new `sports.LIST_FLOOR` raises a sport's backtest threshold, and never grants a sport a place it has not earned.

**Evidence:** the 70% bar clears 80% cumulatively (fit 80.9%, check 84.2%), but its own bands miss: 70-75% landed 71.3% (fit, n=101) and 78.0% (check, n=168); 75-80% landed 73.8% (n=84) and 76.9% (n=108). 80-85% landed 87.7% and 87.4%. On the live List, 7-11 Oct, college football at 70-80% won 11 of 17, and at 80%+ 10 of 12. Probabilities are unchanged: only List membership moves.

**Files:** `sports.py`, `tests/test_sports.py`, this entry.

**Not changed:** any model number, calibration, `sports.json`, record or archive. Tennis bars stay at 75%: WTA 75-80% landed 88.4% in testing (n=95), and 12 of 14 live across the board.

**Roll back:** `git revert` the commit.


## 2026-10-13: Tennis surface by tournament name tested, rejected (tag pending)

**What changed:** nothing a reader sees. A new advisory tool and a dated note. Pricing WTA/ATP results since June by tournament-name surface (clay / grass / hard) instead of all-Hard is worse, so `surfaceWeight` 0.3 and the all-Hard feed stay.

**Evidence:** walk-forward on every ESPN result since the archive ended, paired bootstrap, nothing fitted, scoreboard untouched. WTA: 2,686 matches, +0.0024 log loss worse (p(worse) 0.88); WTA clay events 631, +0.0060 worse (0.86). ATP: 1,523, +0.0031 worse (0.95); ATP grass +0.0142 worse; ATP clay -0.0099 (p(worse) 0.13, n=187, under the 250 gate). 75%+ main draw hit rate no better.

**Files:** `tools/tennis_surface_eval.py`, `claude/tennis-surface-test-2026-10-13.md`, this entry.

**Not changed:** any model number, `tennis.json`, `build_tennis.py`, record or archive.

**Roll back:** `git revert` the commit.


## 2026-10-12: Office review and next week's priorities (tag pending)

**What changed:** nothing a reader sees. A dated review note: what the office shipped since 28 Sep, rejected tests, accuracy by group, data quality, three tasks for next week (Susie, Theo, Andrew).

**Evidence:** record summaries read only. Football Daily List 60 of 72 (83.3%), Strong 79.9% v 78.3% quoted, tennis 59.5% v 61.7% (n=526), sports 70.3% v 65.1% (n=158).

**Files:** `claude/office-review-2026-10-12.md`, this entry.

**Not changed:** any code, model number, record or archive.

**Roll back:** `git revert` the commit.


## 2026-10-12: Grading audit, extra-time scores no longer graded (tag pending)

**What changed:** ESPN football results after extra time or penalties are not graded or used as live results, because the board prices 90 minutes. Tennis voids on ESPN's walkover status as well as the `w/o` note.

**Evidence:** 168 sampled graded games (51 football, 60 tennis, 157 other sports checked in full) all match ESPN, 0 mismatches. 12 AET / PEN games in 29 days carried the 120-minute score; none was in the graded record, so no published number changes.

**Files:** `sources.py`, `score_tennis.py`, `tests/test_grading.py`, `claude/results-review-board.md`, this entry.

**Not changed:** any record file, `history/`, any model constant or calibration.

**Roll back:** `git revert` the commit.


## 2026-10-12: Odds tab group rules backtest rerun, no change (tag pending)

**What changed:** nothing a reader sees. A dated section added to `claude/odds-groupings.md`.

**Evidence:** 30 settled groups, 4 to 12 Oct: 9 won against 9.51 stated. Steady 3 of 13 (4.97 expected), Balanced 5 of 8 (2.50), Stretch 1 of 9 (2.04). Bootstrap of won minus expected: -0.51, 90% interval -4.5 to +3.5. Legs 106 of 140 against 110.4 expected; tennis 18 of 26 against 21.1 is the only gap. Historical replay still impossible: no archived tested rate or price.

**Files:** `claude/odds-groupings.md`, this entry.

**Not changed:** `groupings.py`, any model number, any record or archive.

**Roll back:** `git revert` the commit; nothing depends on it.


## 2026-10-12: Odds tab price coverage measured, no change (tag pending)

**What changed:** nothing a reader sees. A dated note on which legs lack bookmaker prices.

**Evidence:** archived groups 4-12 Oct: football 81 priced / 12 estimated, tennis 0 of 29, rugby 0 of 7, NFL 12 of 12. Football gaps are unlisted small leagues, not name or date mismatches. No new source could be tested (ESPN 403, no API key in the sandbox).

**Files:** `claude/odds-pricing-coverage-2026-10-12.md`, this entry.

**Not changed:** `groupings.py`, any model number, any record or archive.

**Roll back:** `git revert` the commit; nothing depends on it.


## 2026-10-12: Daily List bar replay rerun, no change (tag pending)

**What changed:** nothing a reader sees. Replay script saved and the 5 Oct result confirmed.

**Evidence:** league win picks, walk-forward. 2025/26 hit: 75% 79.4% (n=189), 77.5% 81.4% (140), 80% 81.9% (94), 82.5% 80.0% (60), 85% 69.2% (39). Paired bootstrap v 80%: 75% -2.4 pts (-7.5 to +2.5), 85% -12.5 (-21.3 to -4.4). 2026/27 still thin (11 picks at 80%). No league has 30 calls at 80%, so no per-league bar.

**Files:** `tools/list_bar_replay.py`, `claude/daily-list.md`, this entry.

**Not changed:** `build.py` `LIST_MIN`, any model number, any record or archive.

**Roll back:** `git revert` the commit; nothing depends on it.


## 2026-10-12: Tennis hit-rate second look, no model change (tag pending)

**What changed:** nothing a reader sees. Tennis showed 59.5% against 61.7% quoted over 526 matches; this checks by tour and surface. No model number changed.

**Evidence:** the gap is 1.07 standard errors overall. ATP 63.1% v 62.3% (n=225, on target). WTA 56.8% v 61.3% (n=301, z -1.63), main draw 55.5% v 60.9%. By tournament-name surface, WTA hard main draw 59.8% v 62.7% (n=174), WTA clay main draw 41.8% v 55.4% (n=55, z -2.04, one of seven cells, found after looking). ESPN has no surface so clay events are priced on hard ratings. The surface-weighting test could not run: the Sackmann archive is unreachable from the sandbox. Descriptive only, nothing fitted on the record.

**Files:** `claude/tennis-hit-rate-2026-10-12.md`, this entry.

**Not changed:** `tennis.json`, `build_tennis.py`, `tune_tennis.py`, `surfaceWeight`, football, any record or archive.

**Roll back:** `git revert` the commit; nothing depends on it.

## 2026-10-12: Calibration by band and sport, full-data rerun (tag pending)

**What changed:** nothing a reader sees. A dated note with the calibration tables run on full data.

**Evidence:** football 55-80% inside noise in both seasons; 85%+ over-confident (41 pooled calls, 68% landed vs 89% quoted). Hockey check window over-confident by 5.6-6.2 points at 55-62%+ (intervals exclude 0), as is baseball; list sports calibrated or conservative at their bars.

**Files:** `claude/calibration-rerun-2026-10-12.md`.

**Not changed:** `calibration.json`, `sports.json`, any code or model number.

**Roll back:** `git revert` the commit.

## 2026-10-12: Championship shrink test, rejected (tag pending)

**What changed:** nothing a reader sees. A dated note and the harness for a
rejected test: a league-specific rating shrink / prior blend for the England Championship.

**Evidence:** paired bootstrap, live curve. On the fit season 2025-26 the best
setting gains 0.0002 log loss (gate 0.0005, p(worse) 0.41); the sign flips
across 2023-24 to 2026-27; 2026-27 has 95 fixtures against 250. Fails Rule 3.

**Files:** `claude/championship-shrink-2026-10-12.md`, `tools/championship_shrink.py`.

**Not changed:** `engine.py`, `calibration.json`, any model number.

**Roll back:** `git revert` the commit.

## 2026-10-12 Goal cap in the ratings: tested, rejected (tag pending)

**What changed:** write-up only: `claude/goal-cap-test-2026-10-12.md` and the advisory script `tools/goal_cap_test.py`. No model, constant or data changed.
**Evidence:** clipping each side's goals per match at 5, 4 or 3 before ratings, paired bootstrap, live curve and a per-setting refit. Fit 2025/26 (6,474 fixtures): cap 5 -0.0002, cap 4 +0.0005, cap 3 +0.0025. Check 2026/27 (1,428): +0.0004, +0.0009, +0.0026, p(worse) 0.90 or more. Nothing passes the gain gate on both seasons.
**Files:** `claude/goal-cap-test-2026-10-12.md`, `tools/goal_cap_test.py`, `RELEASES.md`.
**Not changed:** `engine.py`, `calibration.json`, anything live.
**Roll back:** `git revert` this commit.

## 2026-10-12 Free source for uncovered leagues: re-checked, none exists (tag pending)

**What changed:** write-up only, an addendum to `claude/free-source-search-2026-10-05.md`. No code, model or data changed.
**Evidence:** TheSportsDB free key for Hungary NB I returns 5 events per season, 5 of 6 games per round and 5 of 12 table rows; football-data.co.uk has no file and ESPN no scoreboard for Croatia, Serbia, Ukraine, Hungary or Korea. A truncated round would be a wrong price, not a missed one.
**Files:** `claude/free-source-search-2026-10-05.md`, `RELEASES.md`.
**Not changed:** `sources.py`, any league, the Daily List rules.
**Roll back:** `git revert` this commit.

## 2026-10-12 ESPN fixtures retry a blip instead of dropping the day (tag pending)

**What changed:** `sources._espn_day`, the one-day ESPN fetch behind live fixtures and top-ups, tried each host once and returned an empty day on any error, so one timeout silently lost a whole competition-day. If every host fails on something transient (timeout, reset, 5xx, 429) it now waits 1s and goes round once more. A 4xx such as 404 is not retried. After 20 consecutive days fail outright ESPN is treated as unreachable and the retry is skipped, so a blocked network costs one pass, not two. Persistent failures are still appended to `errs` and reported in the build log, never swallowed.
**Evidence:** four new tests in `tests/test_source_failures.py` with a fake failing source: blip then success (3 calls, no error), persistent 503 (4 calls, one error reported), 404 (2 calls, no retry), blocked-network breaker (2 calls). `nametest.py` passes. No build run: ESPN is unreachable from this sandbox, so the live effect is for CI to show.
**Files:** `sources.py`, `tests/test_source_failures.py`, `RELEASES.md`.
**Not changed:** any model, rating, threshold, name matching, other source (openfootball, football-data, API-Football already retry via `_open`), or the fall-through of `fetch_season`.
**Roll back:** `git revert` this commit.

## 2026-10-12 Fixture audit of predictions/2026-10-12.json: matching clean (tag pending)

**What changed:** write-up only, in `claude/data-integrity.md`. No code, model or data changed.
**Evidence:** 2,014 rows, 84 dated 12 Oct and the rest 13-18 Oct. No exact or reversed duplicates within a date, no club twice on one date in one league, no unrated rows, no row whose kick-off falls before its row date. 19 rows have no kick-off (Brazil, dated by day). Same-name clubs on one date (Santos, Platense, Liverpool, Barcelona, San Miguel, Sandviken, Atenas) are different clubs in different leagues, each priced inside its own league. `nametest.py` passes. One real finding: 2 fixtures (Llerenense v Puebla Calzada, Atletico Mineros v Velarde, Spanish Tercera RFEF) sit under both 17 and 18 Oct because the source moved the date and the archive keys on date. Across 2026 archives 46 such stale pairs, 4 touching a list or reserve flag. Not fixed: the archive merge and grading are bot-owned and tied to the scoreboard.
**Files:** `claude/data-integrity.md`, `RELEASES.md`.
**Not changed:** matcher, `LIVE_NAMES`, archive merge, grading.
**Roll back:** `git revert` this commit.

## 2026-10-12 Tests for odds.py, the untested price module (tag pending)

**What changed:** new `tests/test_odds.py` (26 tests) covering `odds.py`, the largest module with no test: CSV parsing and row rejection, margin removal (`fair`), the stale-max cap (`best`), club-name matching and the one-price-one-fixture rule (`match`), the value gate and ROI/CLV in `evaluate`, the bootstrap, and report staleness.
**Evidence:** all 26 pass; full suite 249 tests OK; `nametest.py` passes. The tests exposed no bug. One minor observation, not changed: `_num` accepts the string "inf" as a price.
**Files:** `tests/test_odds.py`, `RELEASES.md`.
**Not changed:** `odds.py` or any model, page or data. Prices never feed a model.
**Roll back:** `git revert` this commit.

## 2026-10-08 Julius review export: every graded prediction as CSVs (release-2026-10-08-6)

**What changed:** new `tools/julius_export.py` writes `julius/julius.ai.review.<date>/` and a `.zip` of it: `all_picks.csv` (every graded pick, all sports), `daily_list.csv`, `reserve.csv`, `by_sport/<sport>.csv`, `summary.csv`, `by_day.csv`, `calibration_bands.csv` and a `README.md` data dictionary. Each row carries ✓ / ✗ / – as on "How it went", the group (Daily List, Reserve, Board), publish time, verification, and `quoted_chance` so hit rates compare against the site's own rule (football counts draw readings). To make the football history complete, `score.py` now also writes `record-graded.json` (every graded fixture; `record.json` keeps 14 days for the page), committed by `deploy.yml` as a bot file and protected from agents. `score.py` and `sports.py` expose their graded rows (`graded_rows()`, `graded_games()`); their outputs are unchanged (record.json and sports-record.json compared identical before and after on the same data).
**Why:** Douglas wants the grading history reviewed in Julius AI.
**Evidence:** `tests/test_julius_export.py`; full suite in CI; `nametest.py` passes. First export from CI's grading: see the folder.
Also fixes a flaky existing test (`test_af_single_flight`: asserted the newest day was the very first of 4 parallel requests; failed 15 of 40 runs, now 0 of 60) that failed CI on Python 3.13.
**Files:** `tools/julius_export.py`, `score.py`, `sports.py`, `tests/test_julius_export.py`, `tests/test_af_single_flight.py`, `.github/workflows/deploy.yml`, `agents/policy.json`, `agents/pick_task.py`, `agents/open_pr.sh`, `CLAUDE.md`, `julius/`, `RELEASES.md`.
**Not changed:** any model, grading rule, threshold or page.
**Roll back:** `git revert` this release's commits; `record-graded.json` and `julius/` can be deleted.

## 2026-10-08 Daily List shows every pick that clears the bar; the reserve folds under each day (release-2026-10-08-5)

**What changed:** the Daily List no longer stops at 20 a day. Every pick that clears the bar is shown, and the reserve sits in a fold under each day: open by itself when fewer than 20 picks clear the bar (so a thin day still offers a full slate), folded on a full day, and remembered once opened or closed. The fold carries the day's reserve tally once results land. "How the list works" and `CLAUDE.md` updated.
**Why:** Douglas noticed Saturday and Sunday had no reserve. The live data had 36 picks clearing the bar on Sat 10 Oct (18 college football) and 23 on Sun 11 Oct, so the 20-a-day cap filled both days with list picks, left no room for the reserve, and hid 16 qualifying picks on Saturday that the records (`daylist.py`, `score*.py`) grade all the same.
**Evidence:** checked in headless Chrome at 1280px and a true 400px: Fri 9 Oct 7 clear the bar with 16 reserve open; Sat 10 Oct every list pick shown with the 26-pick reserve folded (local build). `nametest.py` passes; full suite in CI.
**Files:** `index.html`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** what qualifies (bar, reserve floor, exclusions), grading, ordering.
**Roll back:** `git revert` this commit.

## 2026-10-08 How it went: the reserve under each Daily List day; boards in two rows of six on desktop (release-2026-10-08-4)

**What changed:** the Daily List review on "How it went" has a **Reserve** section under each day's list picks, folded away until opened: the day's reserve picks, how many landed, and the reserve's own record across every day shown. It stays a separate group and never counts in the list's record. A day with reserve picks but no list pick now appears, marked "–" in the day picker, and the "last 7 list days" tile counts list days only. The board picker above (Daily List, Football, Tennis and the nine other sports) is two rows of six on desktop; phones keep three to a row. `score.py` now carries each football row's reserve flag into the day review (it already graded the reserve as a group).
**Evidence:** checked in headless Chrome at 1280px and at a true 400px (inside a 400px frame; headless lays out at 500px minimum): 8 Oct shows 3 list picks and 15 reserve, 6 of 9 settled reserve landed, 54 of 86 across every day. Regraded locally: 19 football day rows carry the reserve flag. `nametest.py` passes; full suite passes in CI.
**Files:** `index.html`, `score.py`, `RELEASES.md`.
**Not changed:** any model, threshold, list rule or grading; the main navigation.
**Roll back:** `git revert` this commit.

## 2026-10-08 Tennis ratings carry every result since June, not the last six days (release-2026-10-08-3)

**What changed:** tennis ratings now include every completed ESPN result since the fitted archive stops (1-2 June 2026). Until now a build added only the last six days, so Wimbledon, the North American swing, the US Open and most of the Asian swing never reached anyone's rating. New `history-tennis/<tour>.json` keeps the results, topped up each build and committed by `deploy.yml` like `history-sports/`. `tennis.json` gains each tour's archive boundary (`tune_tennis.py --boundary`, ratings untouched) so no archive match counts twice. Walkovers are skipped, as in the archive. Agents may not edit `history-tennis/` (`agents/`).
**Why:** Daily List pick 13, Muchova 77.4% v Bartunkova (China Open QF, Bartunkova won). Bartunkova's ~30 matches since June were missing. With them, Muchova is 73.6%: still the favourite, but a reserve pick, not a list pick.
**Evidence:** every match since the archive, priced from earlier days only, paired bootstrap (`tools/tennis_gap_eval.py`): WTA 2,563 matches, log loss -0.0042, p(worse) 0.023; ATP 1,470, -0.0035, p(worse) 0.095 (Aug-Oct -0.0109, p 0.016; Jun-Jul +0.0041 worse: ESPN has no surface, so grass results go in as hard court, an open item). Hot-form signals tested on top and rejected: K x 1.5 worse on both tours, a wins-in-this-tournament term fits to zero. Today's tennis list 8 -> 6 (Andreeva, De Minaur to reserve). First walk 3,091 ATP / 4,305 WTA results; repeat build identical. `tests/test_tennis_history.py` (8 tests); `nametest.py` passes; full suite passes except the four modules that need `zoneinfo` (Python 3.9+), which cannot run on this Mac's 3.7 and run in CI. Write-up: `claude/tennis-ratings-gap-2026-10-08.md`.
**Files:** `build_tennis.py`, `tune_tennis.py`, `tennis.json` (boundary only), `history-tennis/`, `tools/tennis_gap_eval.py`, `tests/test_tennis_history.py`, `.github/workflows/deploy.yml`, `agents/pick_task.py`, `agents/open_pr.sh`, `agents/policy.json`, `CLAUDE.md`, `claude/tennis-ratings-gap-2026-10-08.md`, `RELEASES.md`.
**Not changed:** tennis ratings, constants, bands, list bar and reserve floor; football and the other sports (their histories were already current); grading.
**Roll back:** `git revert` this commit. Builds then fall back to the six-day window (an old `tennis.json` has no boundary). `history-tennis/` can stay.

## 2026-10-08 Domestic-cup replay: cups join the Daily List only if it passes (release-2026-10-08-2)

**What changed:**
- `build.cup_replay` (inside `build.py main`): once a day, every played API-Football domestic-cup tie in the day files already on disk (up to 330 days back, no API calls) is priced the way the board would have priced it on the morning of the tie. Each club gets its prior season, which must have finished before the tie or the tie is skipped, blended with its division's results before that date, then `tie_strength` and `cup_match` as live. Women's and youth ties are left out. Results go in `current/af-cup-replay.json`.
- `build.cup_gate` applies the list's own rule: the lowest of 75% / 80% at which clean win picks landed at least 80% in every half-year window with 30+ calls, with at least one such window, and no small window clearly failing. Cross-division ties (the Celtic's Law cup flag) are judged separately and list only if they pass on their own.
- `list_reason`: an API-Football cup stays "cup" until the replay passes, and it never lists a women's or youth tie. Reserve unchanged: cups stay out.
- `sources.af_cached_fixtures`: reads day files from disk only.
**Why:** Douglas (8 Oct 2026): build and test the domestic-cup replay so the cups that pass can join the Daily List.
- Board fix found by the replay: every API-Football wider league carries the same placeholder strength (0.5) whatever its level, so a cup tie between, say, a Belarusian third and second division side was priced as level frames and shown without the cross-division flag (Drut Belynichi 88% at home to Orsha, lost 0-7; Nykobing 95% against Middelfart, 4-4). `cup_placeholder`: a tie across two divisions where either has only the placeholder now carries the cross-division Celtic's Law flag, on the board and in the replay. Probabilities unchanged.
**Evidence:** first real run (8 Oct 2026, no API calls): 6,203 cup ties on disk, 1,846 priced in 106 cups (1 Jan to 7 Oct 2026). Skipped: 3,434 with a side not rated, 515 where a prior season had not finished, 408 women's/youth. Clean win picks at 75%+ landed 47.4% of 19 (Jan-Jun) and 88.9% of 18 (Jul-Oct), 67.6% of 37 overall, against 80.7% quoted. At 80%+: 50.0% of 10 and 100% of 9. Cross-division ties at 75%+: 38.7% of 31 and 66.0% of 47. Bands for clean picks: 55%+ landed 57.3% (260) against 65.5% quoted, 70%+ landed 68.2% (66) against 77.0%. Result: fail. Cups stay off the Daily List, and the gate reruns daily. `tests/test_cup_gate.py` covers the gate, windows, flags, the placeholder rule, women's/youth sides and `list_reason`; full suite and `nametest.py` pass.
**Files:** `build.py`, `sources.py`, `tests/test_cup_gate.py`, `RELEASES.md`.
**Not changed:** the model, prices, the reserve, grading, workflows.
**Roll back:** `git revert` the four commits of this release; cups go back to board-only.

## 2026-10-08 Tennis rated from qualifying, Challenger and ITF matches; list bar 75% (release-2026-10-08-1)

**What changed:**
- `tune_tennis.py` feeds the Elo walk with the archive's qualifying/Challenger (ATP) and qualifying/ITF (WTA) files as well as tour level (`EXTRA`). Tuning and the check are still scored on tour-level matches only, the same test set as before. `tennis.json` refitted: 3,173 ATP and 10,175 WTA players rated (was 998 and 954).
- `build_tennis.match_player` also matches a name written in another word order when exactly one rated player has those words (ESPN writes "Shang Juncheng", the archive "Juncheng Shang").
- Tennis bands and list bar re-read with the new tool `tools/tennis_bands.py` (it reproduces the old bands exactly on the old pool). Daily List bar 80% -> 75% on both tours; reserve unchanged (62%).
- The ATP ranking layer is off (`ATP_RANK_LAYER = False`): refitted on 2025 over the new ratings it no longer passes (2026 -0.0020 log loss, p(worse) 0.077 against 0.05). Rankings are still shown.
- `build.py`: a cup with no tie in the window no longer counts as a missing feed in `health`.
**Why:** Douglas asked (7 Oct 2026) for the list to be drawn from the whole day's data. About 45% of the week's ESPN tennis matches were dropped with "no rating on file for a side".
**Evidence:** clean 2026 check, tour level: ATP log loss 0.6241 -> 0.6055, accuracy 64.2% -> 66.0%; WTA 0.6115 -> 0.5983, 65.1% -> 68.0%; paired against the old ratings on the same matches, p(worse) 0.00 (ATP) and 0.0025 (WTA). At 75%+: ATP 83.0% (499) / 83.5% (243), WTA 84.8% (415) / 89.9% (227), 2025 / 2026. This week's feed: unpriceable matches 65 of 381 -> 19. Local build: 39 priced, 8 on the list (was 0 at 80%). `tests/test_tennis_names.py`; full suite and `nametest.py` pass.
**Files:** `tune_tennis.py`, `tennis.json`, `build_tennis.py`, `tools/tennis_bands.py`, `build.py`, `tests/test_tennis_names.py`, `RELEASES.md`.
**Not changed:** football, the other sports, grading, the reserve floor.
**Roll back:** `git revert` this commit.

## 2026-10-07 Daily List coverage: what each day's list was chosen from, and any gap (release-2026-10-07-4)

**What changed:**
- `build.list_reason` gives each football fixture off the Daily List one reason code (cup with no replay yet, new competition, under-21, step 3, draw pick, below the bar, Celtic's Law, unrated, ranking-only, no prior season). `list_eligible` is now `list_reason(g) is None`: the same tests in the same order, so no pick moves. The code is archived with each prediction (`why`).
- `data.json` gains `health`: API-Football calls this build, whether the allowance was gone, and the window's days with no fresh API-Football day file (`sources.af_days_missing`), plus the count of missing feeds.
- `daylist.py` writes `coverage` into `daylist.json`: every game priced for the UK day, per sport, in how many competitions, how many made the list and reserve, why the rest did not; and gaps (a board not rebuilt for 12 hours, API-Football days not fetched, the allowance gone). Each gap is a `::warning::` on the run page.
- The Daily List lede says what today's list was chosen from ("chosen from 94 games: 52 football in 24 competitions, 36 tennis in 4 …"), and shows any missing data in red.
**Why:** Douglas asked (7 Oct 2026) that every day's list be drawn from the whole day's data: all leagues, cups and friendlies, every sport. The list already considered every published fixture; this makes each day's coverage, and any data the board did not get, visible instead of passing as a quiet day.
**Evidence:** `tests/test_coverage.py`; full suite and `nametest.py` pass; Daily List checked at 1400px.
**Files:** `build.py`, `sources.py`, `daylist.py`, `index.html`, `tests/test_coverage.py`, `RELEASES.md`.
**Not changed:** which games make the list or reserve, any probability, grading. Domestic cups, FA Cup qualifying and under-21 ties stay off the list until a replay passes (standing rule).
**Roll back:** `git revert` this commit.

## 2026-10-07 API-Football: one call per question, and the cache kept when a build fails (release-2026-10-07-1)

**What changed:**
- `sources._af_get` makes one call per API path however many threads ask at once: a per-path lock, and a waiting thread reads the answer the first one got.
- `sources.af_day_pool` builds each pool once, under a lock; the other league threads wait for it rather than each fetching every day of the year. Days are fetched newest first, so if the allowance runs out part way the days the board prices and grades are already in hand.
- Once the allowance is refused, the usage line reads "0 left today" (it read "7499 left today; allowance used up").
- `deploy.yml` and `tune.yml` restore the `.afcache` cache at the start and save it with `if: always()`, so a failed build keeps the days it paid for.
**Why:** the first builds of 7 Oct spent the whole 7,500-call allowance by about 14:00 UTC, against ~290 expected: 2,717 calls (05:48 build, failed), 2,198 (11:46, failed), 2,831 (13:55). Parallel league threads each built the same year-long day pool, and the two failed builds saved no cache, so each refetched the year. Douglas asked (7 Oct 2026) for every global fixture without wasted calls.
**Evidence:** `tests/test_af_single_flight.py` (eight threads, one call; a ten-day pool asked for by eight threads makes ten calls, newest first; a refusal reads 0 left); full suite and `nametest.py` pass.
**Files:** `sources.py`, `.github/workflows/deploy.yml`, `.github/workflows/tune.yml`, `tests/test_af_single_flight.py`, `RELEASES.md`.
**Not changed:** which leagues, cups or days are read; any probability; grading.
**Roll back:** `git revert` this commit.

## 2026-10-07 Daily List results refresh six times a day (tag pending)

**What changed:** `deploy.yml` adds four scheduled rebuilds (12:00, 17:00, 19:30, 22:15 UTC) to the existing 00:10 and 05:15, timed to when results land rather than every four hours. Docs and the Analysis page copy updated to match.
**Evidence:** owner request, 7 Oct 2026: a 09:58 Daily List still showed no result for a 01:00 game. Each run costs roughly 10-25 API-Football calls through the shared date pool (7,500 daily allowance); no AI credits; GitHub Actions minutes are free on a public repository.
**Files:** `.github/workflows/deploy.yml`, `DEPLOY.md`, `README.md`, `CLAUDE.md`, `analysis.html`, `RELEASES.md`.
**Not changed:** predictions, grading, Daily List membership rules (a game is frozen at its start), the push trigger, the sprint hold.
**Roll back:** `git revert` this commit.

## 2026-10-07 60-70% band checked: noise, no model change (tag pending)

**What changed:** `calibration_bands.py` prints a bootstrapped 60-70% span under each football table; dated note `claude/calibration-60-70-2026-10-07.md`.
**Evidence:** from history, not `record.json`. Fit season 2025-26: 603 games, quoted 64.2%, landed 64.8% (+0.6). Check season 2026-27: 124 games, 64.1% vs 73.4% (+9.3, interval +2.5 to +15.7, one-sided p 0.013, about 0.13 after allowing for the bands examined). Pooled 727: +2.1 (-0.8 to +5.1). `tune.py --fit --dry-run`: best candidate a 1.155 / b -0.30, check log loss +0.0001, P(worse) 72%, `notWorse` and `worthIt` fail, nothing written.
**Files:** `calibration_bands.py`, `claude/calibration-60-70-2026-10-07.md`, `RELEASES.md`.
**Not changed:** `calibration.json`, any constant, the tier ladder.
**Roll back:** `git revert` this commit.

## 2026-10-07 Strong tier below expectation checked: noise, no model change (tag pending)

**What changed:** a dated note only (`claude/strong-tier-check-2026-10-07.md`).
**Evidence:** 59 graded Strong games, 76 to 78% landed vs 79% quoted; one standard deviation at that size is 5.3 points. Splits by draw risk (82% vs 84% quoted at P(draw) under 15%, 68% vs 73% above), pick side and league show nothing that survives the number of cuts looked at; AFCON qualifying 5 of 9 is the largest deviation and would be expected to turn up across 15 league groups. No Strong pick carries Celtic's Law (demoted a tier). Backtest quoted 78.1 vs landed 79.2.
**Files:** `claude/strong-tier-check-2026-10-07.md`, `RELEASES.md`.
**Not changed:** any model constant, calibration, tier ladder.
**Roll back:** `git revert` this commit.

## 2026-10-07 Daily build no longer fails on a racing API-Football day-cache write (tag pending)

**What changed:** `_af_day` (`sources.py`) wrote each cached day through one shared temp name (`day-DATE.json.gz.tmp`). Two date-window pools running at once (the build fetches leagues in parallel) can ask for the same day; the first `os.replace` moved the file and the second raised `FileNotFoundError`, which killed the whole build (run 37616405304, day 2026-05-13). The temp name is now unique per process and thread, and a failed cache write is swallowed (rows are already in hand) with the temp removed.
**Evidence:** traceback in the run log: `os.replace(tmp, path)` at `sources.py` `_af_day`, `FileNotFoundError` on the shared `.tmp`. Nothing else in the pipeline touches that file.
**Files:** `sources.py`, `RELEASES.md`.
**Not changed:** any model number, the refuse-if-empty and keep-yesterday's-site safety (an upstream fetch failure still fails the build), cache contents or TTLs.
**Roll back:** `git revert` this commit.

## 2026-10-06 "How it went" opens on a Daily List review, with a board for every sport (release-2026-10-06-17)

**What changed:**
- "How it went" now opens on "The Daily List, day by day": every pick that made the Daily List, across all sports, for today and each earlier day, with the pick, its chance, the result and a tick or cross. Tiles show the last seven list days, every list day on file, and the chosen day. Today's rows come from the pinned list (`daylist.js`), so picks still to play, in play or awaiting a result show as such; earlier days come from `record.json`, `tennis-record.json` and `sports-record.json`.
- The three-button switcher is replaced by a grid of boards, three to a row: Daily List, Football, Tennis, then each sport in `sports.json` (NFL, Baseball, Basketball, Rugby, Ice hockey, College football, College basketball, WNBA, Rugby league). Each shows its graded record; a sport with nothing graded is greyed.
- Each of the other sports has its own board (its record, its Daily List record, its days), replacing the single "Other sports" board.
**Why:** Douglas asked (6 Oct 2026) for "How it went" to review the daily picks from the day and the days before, then let him browse each sport on its own tab, in a grid.
**Evidence:** read-only use of the existing record files; nothing regraded; the list total matches the header's list record (52 of 61); checked at 1400px and 400px; tests pass.
**Files:** `index.html`, `RELEASES.md`.
**Not changed:** grading, any probability, the football and tennis boards.
**Roll back:** `git revert` this commit.

## 2026-10-06 Tested rates by a pick's own band; fair odds labelled; sport and time on the slip (release-2026-10-06-16)

**What changed:**
- The "tested" or "landed" rate beside every pick (football, tennis, the other sports) is now the rate for picks at its own level, not every call at that level or above. `bands.band_rate` derives it exactly from the cumulative bands already on file (the difference of two counts and hit totals); a band with fewer than 30 calls is widened upward until it holds 30. Each row's `accuracy` gains `to`, `cumHit` and `cumN`. Chips and lines read "Calls at 60–65% landed 57%".
- Daily List ordering (`index.html`, `daylist.py`) and the Odds tab groupings (`groupings.py`) keep the cumulative rate, so neither the order nor the groupings move with this release.
- The slip's prices are labelled "fair" (1 / the model's chance, not a bookmaker's price), with the nearest fraction a bookmaker would print ("1.29 fair (3/10)", not "1.29 (1/3.4)").
- Each slip row shows its sport, competition and UK start time ("Tennis · WTA · China Open · Round 4 · Wed 7 Oct, 06:00"). On a phone the pick takes the full width, with chance and tested rate below.
- The Daily List lede now says the bar is set on calls from that level up, and that a pick just over the bar can show less than 80%.
**Why:** Douglas asked (6 Oct 2026) after a slip showed Sasnovich (WTA, 62%) as "72% tested" while calls at 60–65% had landed 57%.
**Evidence:** `tests/test_bands.py` (Sasnovich's band, the open top band, widening a thin band); `tests/test_sports.py` updated to the band rate; full suite and `nametest.py` pass; slip checked at 1400px and 400px.
**Files:** `bands.py`, `build.py`, `build_tennis.py`, `sports.py`, `groupings.py`, `daylist.py`, `index.html`, `tests/test_bands.py`, `tests/test_sports.py`, `RELEASES.md`.
**Not changed:** any probability, the Daily List bar, the reserve floor, grading.
**Roll back:** `git revert` this commit.

## 2026-10-06 Five more sports from ESPN's free feeds (release-2026-10-06-15)

**What changed:**
- `sports.py` gains ice hockey (NHL), college football (NCAA FBS), college basketball (all of Division I, `groups=50`), WNBA and rugby league (NRL). Each is its own sport with its own fitted constants, so the NBA and union rugby do not move. History from July 2023 on ESPN; the CI build walks it once (about three minutes), then tops up daily.
- `sports.json`: the five new entries, fitted and gated by `sports.py --tune --only nhl,cfb,ncaab,wnba,nrl`; the four existing entries are unchanged.
- `index.html`: a tab for each; a sport tab with no games this week and nothing graded is hidden (off-season), so the bar does not crowd. `groupings.py` prices the new US sports from ESPN's moneylines like the NFL, MLB and NBA.
**Backtest (check window from July 2025, never fitted on):**
- College football: 1,097 games, winner 72.3% v 58.4% backing home, PASS. 70%+ calls landed 84.2% (538). Daily List from 70%.
- College basketball: 5,814 games, 71.3% v 64.4%, PASS. 70%+ landed 82.1% (3,172). Daily List from 70%.
- WNBA: 531 games, 69.7% v 53.9%, PASS. 80%+ landed 81.2% (101). Daily List from 80%.
- Rugby league: 298 games, 63.4% v 55.2%, PASS. No band earns a list place: board only.
- Ice hockey: 1,429 games, 54.9% v 56.5% backing home, FAIL. Not published: no NHL games are shown until a model beats backing the home side.
**Why:** Douglas wants every sport's games collected so the most accurate can be picked (6 Oct 2026).
**Evidence:** the tune output above; `tests/test_sports_feeds.py`; full suite passes; checked at 1400px and 400px (College football tab, Daily List).
**Files:** `sports.py`, `sports.json`, `index.html`, `groupings.py`, `tests/test_sports_feeds.py`, `RELEASES.md`.
**Not changed:** football, tennis, the NFL, MLB, NBA and union rugby models, grading rules, workflows.
**Roll back:** `git revert` this commit.

## 2026-10-06 One rebuild per agent sprint, no idle runners (release-2026-10-06-14)

**What changed:**
- `office-agents.yml` plan: only agents with something to pick now get a runner (`agents/pick_task.py --active-agents`, the same choice `--agent` makes). If nobody has work, no runner starts. Before, all 14 started every morning; this afternoon none had work.
- `office-agents.yml` publish: rebuilds the site only if a commit reached main during the sprint (archive commits marked `[skip ci]` not counted). This afternoon a sprint with nothing merged still started a full build.
- `deploy.yml`: a new `gate` job holds a push build while an office sprint is running or queued; the sprint's publish job does the one rebuild at the end. Scheduled and manual builds are never held. On 5 Oct one sprint's merges started a build each.
**Why:** Douglas asked to optimise credit use across the whole project (6 Oct 2026, owner approval for these workflow changes).
**Evidence:** both workflows parse; `--active-agents` against the live queue returns ["ratings", "calib"], and `--agent` for engineer, sports and chief says "Nothing new to work on today", which matches. Full test suite passes.
**Files:** `.github/workflows/office-agents.yml`, `.github/workflows/deploy.yml`, `agents/pick_task.py`, `RELEASES.md`.
**Not changed:** predictions, grading, the daily 00:10 and 05:15 builds, the merge gate.
**Roll back:** `git revert` this commit.

## 2026-10-06 API-Football spend guards (release-2026-10-06-13)

**What changed:**
- When API-Football says the day's allowance is gone, `sources` leaves a marker for the UTC day in `.afcache` (kept by the Actions cache). The next script in the run, and every later build that day, makes no call to hear it again. It clears itself at 00:00 UTC, when the allowance resets.
- A day of fixtures whose cached copy has expired, and which cannot be fetched again (allowance spent, network), now uses the last copy instead of coming back empty. On the afternoon of 6 Oct the board fell to 471 games for this reason.
- Each script prints one line at the end: how many API-Football calls it made and, from the API's own header, how many are left today. The overnight check reads it.
**Why:** Douglas asked for every call, run and token to be checked for waste (6 Oct 2026).
**Evidence:** `tests/test_af_spend.py` (marker stops calls before any request; a stale day beats an empty one); `tests/test_af_allowance.py` now keeps its marker in a temp folder. Full suite and `nametest.py` pass.
**Files:** `sources.py`, `tests/test_af_spend.py`, `tests/test_af_allowance.py`, `RELEASES.md`.
**Not changed:** ratings, calibration, grading rules, workflows.
**Roll back:** `git revert` this commit.

## 2026-10-06 U21 sides rated from Premier League 2 (release-2026-10-06-10)

**What changed:**
- The build finds Premier League 2 and the EFL Trophy on API-Football (`sources.af_refresh_u21`, one `/leagues?country=England` call a week, kept in `current/af-u21.json`) and rates U21 sides from their own PL2 results (`engine.register_u21`, codes `afu.<id>`). PL2's games are on their board, off the Daily List.
- `build.fit_u21` sets PL2's strength against the senior game: one number, grid 0.20-0.80, chosen on last season's EFL Trophy U21 v League One/Two ties, with the build's own ratings. It must beat the outcome-share baseline on the same ties by 0.005 log loss, on 30+ ties, not at a grid edge. Kept in `current/u21-fit.json`, refitted weekly. Ratings are the prior season, so they have seen the season the ties were played in; one parameter, so the leak is small, and the file says so.
- Until a fit passes, a U21 side is never priced against a senior club (`build.u21_cup_ok`) and its EFL Trophy ties stay off the board, as since release-2026-10-06-7. With a pass, they come back, flagged `u21Side`, board only: off the Daily List and the reserve until their live results are checked.
**Why:** Douglas approved rating academy sides properly (6 Oct 2026) after "Sunderland U21" turned out to be priced as Sunderland's first team.
**Evidence:** `tests/test_u21.py`: on ties drawn from the model at a known strength 0.40 the fit returns 0.43 and passes; too few ties fails; senior v senior and U21 v U21 ties are ignored; unfitted U21 sides are refused against seniors. Full suite and `nametest.py` pass. A local build without the key is unchanged (nothing registers without it).
**Files:** `engine.py`, `sources.py`, `build.py`, `tests/test_u21.py`, `RELEASES.md`.
**Not changed:** any senior rating, calibration, list threshold, grading rule or workflow.
**Roll back:** `git revert` this commit.

## 2026-10-06 FA Cup qualifying on the board; tuning run keeps the API cache (release-2026-10-06-9)

**What changed:**
- New competition `en.faq`, FA Cup qualifying, from ESPN (`eng.fa_qual`, 40 ties on 3 Oct 2026). Ties are priced like the FA Cup, each club in its own division, in a frame at steps 1-2 (strength 0.42, tier 6). Clubs at step 4 and below have no rating, so their ties are dropped at the unrated gate. Board only (`build.NEW_BOARD_ONLY`): off the Daily List and the reserve until replayed.
- `tune.yml` restores and saves `.afcache` like the daily build, so the Monday run reads the shared API-Football day pool instead of refilling the year (~290 calls).
**Why:** Douglas asked whether FA Cup qualifying is covered (it was not), and approved the tune.yml cache on 6 Oct 2026.
**Evidence:** full suite and `nametest.py` pass.
**Files:** `engine.py`, `sources.py`, `build.py`, `.github/workflows/tune.yml`, `RELEASES.md`.
**Not changed:** any existing prediction, rating, grading rule or list threshold.
**Roll back:** `git revert` this commit.

## 2026-10-06 API-Football calls cut from ~700 a build to ~10 (release-2026-10-06-8)

**What changed:**
- Current seasons of every API-Football league (steps 1-3 and the 227 wider leagues) are read from one shared date pool, `/fixtures?date=D` (`sources.af_season_pool`), instead of one `/fixtures?league&season` call per league per script. One date call answers for every league. A finished day is kept on disk for good (`.afcache/day-*.json.gz`, gzipped and trimmed to the fields read); an open day (yesterday, today, the week ahead) for 45 minutes, so the two build passes, `score.py` and `groupings.py` in one run share it.
- A season that is over is fetched once and kept (`_af_season`), and a finished season the API has nothing for is asked again weekly, not every build.
- The Odds tab (`groupings.py`) no longer pages through `/odds?date=` (ten fixtures a page, up to 60 pages a date). Legs are matched to fixtures from the day pool and only those fixtures are priced, one call each, cached 90 minutes. Same prices, same averaging.
**Why:** the 7,500 daily allowance ran out by 15:30 on 6 Oct. ~234 leagues x three passes a run (two build passes and score.py) is ~700 calls a deploy, and there were 23 deploys on 5 Oct. Every API-Football league dropped off the board for the rest of the day. Douglas: "reduce all calls that aren't necessary".
**Evidence:** tests in `tests/test_af_cups.py` (season window, current league read from the pool with no per-league call, finished season one call then disk, odds one call per leg then cached); full suite and `nametest.py` pass. Expected cost: one-off ~290 calls to fill this year's days, then ~10 a deploy plus one per newly priced leg.
**Files:** `sources.py`, `groupings.py`, `tests/test_af_cups.py`, `claude/data-expansion-plan.md`, `RELEASES.md`.
**Not changed:** any rating, model, rule, grading rule, price source or workflow. The same matches reach the build; only how they are fetched changed.
**Roll back:** `git revert` this commit.

## 2026-10-06 Every domestic cup; academy sides no longer priced as first teams (release-2026-10-06-7)

**What changed:**
- Domestic cups worldwide from API-Football. The build finds every current senior domestic cup with one `/leagues?type=cup&current=true` call, at most every three days (`sources.af_refresh_cups`), and keeps the list in `current/af-cups.json` (written by the build, committed with the archive). Youth, women's, super cups, shields, friendlies and qualifying are left out, and so is any country with no rated league (every tie there would be dropped at the unrated gate).
- Fixtures and results for all cups come from one shared pool, `/fixtures?date=D` for 12 days back and 8 ahead (`sources.af_cup_pool`): about ten calls a build after the first, not one per cup. Finished days stay on disk in `.afcache/`.
- Each cup is priced like the native cups: clubs rated in their own country's leagues (`engine.eligible_league`, now through `engine.canon_country` so API-Football's country spellings meet ours), in a frame 0.03 below the country's top flight (`engine.cup_strength`).
- A tie a native feed already carries (FA Cup, Copa del Rey, the ESPN cups) is dropped from the API-Football copy (`build.dedupe_cups`), so nothing is priced twice.
- New cups are board only: off the Daily List and the reserve until a replay earns a place, no backtest band quoted.
- `score.py` keeps API-Football cup results in `current/settled-results.json` as they land, so they stay graded after leaving the 12-day pool.
- `sources.match_team`: a containment match now needs the same youth/reserve markers on both names. "Sunderland U21" (EFL Trophy) had matched "Sunderland" and was priced as the Premier League first team, 54% away at Sheffield Wednesday.
**Why:** Douglas asked whether the EFL Trophy is predicted (it is: 19 ties on 6 Oct) and for every domestic cup in the world.
**Evidence:** `tests/test_af_cups.py` (11 tests); full suite and `nametest.py` pass. Before/after local build, two days, same cache: the only change was the four EFL Trophy ties with a U21 side, now unrated and dropped at the publish gate; every other prediction identical.
**Files:** `engine.py`, `sources.py`, `build.py`, `score.py`, `tests/test_af_cups.py`, `claude/data-expansion-plan.md`, `RELEASES.md`.
**Not changed:** calibration, list thresholds, grading rules, workflows.
**Roll back:** `git revert` this commit; `current/af-cups.json` is then ignored.

## 2026-10-06 Copyright notice (release-2026-10-06-6)

**What changed:** added `LICENSE`, a proprietary all-rights-reserved notice in Douglas Baker's name, and a Copyright section at the end of `README.md`.
**Why:** Douglas asked for a copyright licence notice so nobody may lawfully copy or reuse the code.
**Evidence:** documentation only; tests unchanged and passing.
**Files:** `LICENSE`, `README.md`, `RELEASES.md`.
**Not changed:** any code, model, rule, grading rule, prediction or workflow.
**Roll back:** `git revert` this commit.

## 2026-10-06 Analysis: day by day by bracket; no link emojis (release-2026-10-06-5)

**What changed:** the Analysis page's day-by-day table now shows one confidence bracket, opening on 70% and above, with quick picks (All, 50%+, 60%+, 70%+, 80%+, 90%+) and a from/to picker for any 5-point range, plus a bracket summary line. `score.py` adds `b5` to each `byDay` entry (games, won, read right, quoted sum and draws per 5-point band) so any bracket sums exactly. The 🔗 marks are gone from the Analysis and HQ links on both pages.
**Why:** Douglas asked for 70%+ by default with a choice of bracket, and no link emojis.
**Evidence:** tests in `tests/test_bands5.py`; bracket totals match `bands5` at 50%, 70% and 80%; checked at 1280px and 400px.
**Files:** `analysis.html`, `score.py`, `index.html`, `tests/test_bands5.py`, `RELEASES.md`.
**Not changed:** any model, rule, grading rule, prediction or workflow.
**Roll back:** `git revert` this commit.

## 2026-10-06 Almanac Analysis page; 🔗 on the cross-site links (release-2026-10-06-4)

**What changed:** a new page, `analysis.html` (linked as "Analysis 🔗" in the board bar), in the almanac's own masthead and styles. It shows the banding table from 50% to 100% in 5-point bands (games, top pick won, quoted, gap, draws, read right, Daily List), each band opening its recent games; a quoted-against-landed chart; every graded day; the model's seven stages with its live settings; why it is built that way; how it is graded; and what it cannot see. `score.py` adds `bands5`, `byDay`, `range` and `model` (read from engine.py, calibration.json and data.json) to `record.json`. The HQ link reads "HQ 🔗"; the twelve desktop nav labels are a touch smaller so none wraps. The deploy copies `analysis.html` into the site.
**Why:** Douglas asked for one page that makes the predictions and results clear: the what, how and why.
**Evidence:** tests in `tests/test_bands5.py`; checked at 1280px, 900px and 400px.
**Files:** `analysis.html`, `score.py`, `index.html`, `.github/workflows/deploy.yml` (one copy line), `tests/test_bands5.py`, `README.md`, `RELEASES.md`.
**Not changed:** any model, rule, grading rule or prediction.
**Roll back:** `git revert` this commit.

## 2026-10-06 Football results kept once settled: the list record stops shrinking (release-2026-10-06-3)

**What changed:** results the live source (ESPN) settles are now kept in `current/settled-results.json` and reused on every build; openfootball still wins where it has the game. The live chase window goes from 6 to 10 days, so the games already lost come back on the next build.
**Why:** the record is rebuilt from scratch each run, and a fixture openfootball never backfills (internationals, most ESPN-only competitions) was graded only while it sat inside the 6-day window. On 6 Oct, 29 Sep dropped out: 46 graded games went to 6, and 14 Daily List picks (AFCON qualifiers, Nations League, CONCACAF) left the list record, 22 to 16 (8 newer picks graded since only partly made up for it).
**Evidence:** local re-grade with the change: 29 Sep back to 46 graded, its 14 list picks back in the list record. The file uses the key `settled`, not `rows`, so `replay.py --freeze` (evaluation snapshots) does not read it. Tests in `tests/test_settled_results.py`.
**Files:** `score.py`, `tests/test_settled_results.py`, `RELEASES.md`.
**Not changed:** any model, rule, grading rule or workflow.
**Roll back:** `git revert` this commit.

## 2026-10-06 Archive push fixed: the record updates again (release-2026-10-06-2)

**What changed:** the deploy's archive commit (and the retune push) now drop actions/checkout's workflow-token header before pushing with the office App token.
**Why:** since main was protected, every archive push went out as github-actions[bot] and was refused (GH013), so `record.json`, the prediction archives and grading stopped being kept after the morning of 5 Oct, and each build reset to the old record. The App token was minted fine; git sent the checkout header instead.
**Files:** `.github/workflows/deploy.yml`, `.github/workflows/tune.yml`, `RELEASES.md`.
**Not changed:** any model, rule or file content.
**Roll back:** `git revert` this commit.

## 2026-10-06 Draw readings count as right; every played row opens; link to HQ (release-2026-10-06)

**What changed:**
- **Draw readings.** A football game now counts as right when the top pick landed, or when the predicted scoreline was a draw and the game finished level (Douglas's decision). That applies everywhere the record is read: How it went ticks, tier and band tables, the list record, the day list's Won/Lost, the office. The quoted side of every quoted-vs-landed comparison adds the draw chance for those games (`score.expected`), so calibration stays a fair test. New `drawReads` count; `drawnOut` now counts only the draws that were not read.
- **Started and played rows open.** Started Daily List picks are drawn by the same row code as upcoming ones (`daylist.py` carries each pick's full object forward from the last pre-start build), so they open the same detail: team sheets, form, Google links. Every How it went row (football, tennis, other sports) opens too: Google links (match report, highlights, head to head, table or draw) and, for football, each side's last five in that competition (`score.team_form`, from the results and `current/`).
- **HQ link.** "HQ ↗" in the board bar opens FootyAlmanac HQ; HQ links back.
**Evidence:** local re-grade on 6 Oct: 710 graded, 505 right (71.1%), 141 draw readings, 35 drawn out. Bands stay close to quoted (e.g. 70%+: 80.4% landed against 79.3% quoted). Tests `tests/test_draw_reads.py`, `tests/test_daylist.py`. Checked in a browser at 420px and 1280px.
**Not changed:** any model, threshold, list rule or the tested "landed" rates (`backtest.py` still grades the top pick). Odds tab groups settle on the result as before: a draw still loses a win leg.
**Roll back:** `git revert` this commit; the next build re-grades.

## 2026-10-05 Today's Daily List stays put: started picks show In play, Won or Lost (release-2026-10-05-22)

**What changed:** today's section of the Daily List no longer empties as the day is played. A pick that has started stays in place, frozen at the price published before its start, with a status: In play, Result due, Won, Lost or Void, plus the score or winner. The day header adds "So far: list W won, L lost · reserve ...". The office reads the same file, so its Today tab matches the site.
**Why:** on 5 Oct the site opened with 2 list and 4 reserve tennis picks (plus Aruba). By 18:00 both the site and the office showed "0 picks", because the live data files only carry games that have not started.
**How:** new `daylist.py`, run in `deploy.yml` after the rebuild, writes `daylist.json` / `daylist.js` for the UK day. Membership is the latest archived price published before each start (`predictions*/`), the rule the record grades by. Results are read from `record.json`, `tennis-record.json` and `sports-record.json`. Nothing is priced, fitted or graded anew. Results arrive with each site build, not live.
**Evidence:** replayed 5 Oct from the archive: list 3 (Alcaraz, Swiatek, Aruba), all won; reserve 4, 2 won and 2 lost. Tests in `tests/test_daylist.py` (pre-start rule, late prices ignored, legacy unpublished prices skipped, UK day not UTC day, won/lost/void). Checked in a browser at 420px and 1280px.
**Files:** `daylist.py`, `index.html`, `.github/workflows/deploy.yml`, `.gitignore`, `tests/test_daylist.py`, `claude/daily-list.md`, `RELEASES.md`.
**Not changed:** any model, threshold, list rule, record or archive.
**Roll back:** `git revert` this commit.

## 2026-10-05 Grading audit: ties void, abandoned games ungraded (tag pending)

**What changed:** the other-sports record no longer counts a tie as a miss (it is void), abandoned, suspended and forfeited games are never graded, and tennis no longer labels Berrettini's matches "retired".
**Evidence:** 36 of 36 football scores match openfootball; 52 of 52 sports scores match history; 2 of 52 sports picks were ties graded as misses; 2 tennis records mislabelled by a substring test. ESPN unreachable from the audit sandbox. Tests in `tests/test_grading.py`.
**Files:** `sports.py`, `sources.py`, `score_tennis.py`, `tests/test_grading.py`, `claude/results-review-board.md`, `RELEASES.md`.
**Not changed:** any model, football draw grading, record files (they update at the next CI run).
**Roll back:** `git revert` the merge commit.

## 2026-10-05 Weakest-sport check: WTA, no change (tag pending)

**What changed:** nothing a reader sees. Appended a re-read to `claude/tennis-hit-rate.md`.
**Evidence:** `tennis-record.json` read only. WTA 55.3% of 190 against 60.7% quoted; main draw 56.8% of 169 against 60.9% (1.1 standard errors); qualifying 42.9% of 21. ATP main 60.2% of 98 against 63.1%. NFL, MLB, rugby have 15-20 graded games each, too few to rank. The thin-player shrink was already rejected today; the surface lookup has no clay sample to test.
**Files:** `claude/tennis-hit-rate.md`, `RELEASES.md`.
**Not changed:** any code, model constant, record or archive.
**Roll back:** `git revert` the merge commit.

## 2026-10-05 Eredivisie accuracy test: rejected, write-up only (tag pending)

**What changed:** nothing a reader sees. Added `claude/eredivisie-test-2026-10-05.md`.
**Evidence:** history only. nl.1 home rate 43-45% over three full seasons (30% only in 63 games of 2026-27); model accuracy 52.6% and 50.8%, log loss 0.9715 and 0.9854. Home advantage x0.7-0.9 is worse on both full seasons. RHO -0.12 gains ~0.001 on both (p worse 0.18, 0.25) but the check season has 63 games against the 250 gate, so it cannot ship.
**Files:** `claude/eredivisie-test-2026-10-05.md`, `RELEASES.md`.
**Not changed:** any code, model constant, calibration, record or archive.
**Roll back:** `git revert` the merge commit.

## 2026-10-05 Office review and next week's priorities (tag pending)

**What changed:** nothing a reader sees. Added `claude/office-review-2026-10-05.md`: what shipped since 21 Sep, rejected tests, record standing, three priorities (Raj, Andrew, Mia).
**Evidence:** `record.json` read only: football Strong 79.2% of 48 (79.4% expected), List 72.7% of 22, tennis 57.5% of 294 (61.3% expected), sports List 85.7% of 14.
**Files:** `claude/office-review-2026-10-05.md`, `RELEASES.md`.
**Not changed:** any code, model number, record or archive.
**Roll back:** `git revert` the merge commit.

## 2026-10-05 Every AI ships more, checks kept (release-2026-10-05-20)

**What changed**
- `agents/merge_gate.py`: a model- or calibration-class change whose
  evaluation was scored and found the candidate's predictions identical to the
  baseline on the snapshot (a grading or data fix with no model effect) now
  merges like any other passing change. An unscored n/a still does not count,
  and any change to predictions still needs an evaluation pass. Tests added.
- `agents/pick_task.py --platform-tasks`: each sprint opens one task per other
  AI platform (MyClaw, Perplexity) as a labelled `office-backlog` issue;
  office agents leave platform-claimed objectives alone.
- `office-agents.yml`: the plan job runs it.

**Why** Douglas, 5 Oct: every AI should be able to make changes, with checks
kept. Susie's grading fix (#18) was held only because it did not change any
prediction.

**Roll back** `git revert` this commit.

---

## 2026-10-05 Archive and retune pushes use the office App (release-2026-10-05-16)

**What changed** `deploy.yml` and `tune.yml` mint an office App token and push
to `main` with it (commit messages carry `[skip ci]` so the push does not
rebuild the site again). Needed because `main` is now protected by the
"Protect main" ruleset: only the owner and the office App may push directly;
everyone else, including other AI platforms, goes through a pull request.

**Roll back** `git revert` this commit and delete the ruleset first.

---

## 2026-10-05 Other AI platforms can work on the project (release-2026-10-05-15)

**What changed** `AGENTS.md` gains "Other AI platforms": one shared queue
(`office-backlog` issues claimed with a `platform:` label), branches only,
`main` protected, the same checks and merge gate for everyone. New issue
template "Office task". Office agents skip issues another platform has
claimed. The merge window now runs at 10:00, 16:00 and 22:00 BST.

**Roll back** `git revert` this commit and delete the `main` ruleset.

---

## 2026-10-05 Protect the API allowance and the daily build (release-2026-10-05-14)

**What changed**
- `sources.py`: when API-Football says the day's allowance is used up
  (`errors.requests`), the build stops calling it for the rest of the run
  instead of retrying every call six times. Burst limits (`rateLimit`) are
  still retried. Tests: `tests/test_af_allowance.py`.
- `deploy.yml`: rebuilds queue instead of cancelling each other; pushes that
  only touch `claude/`, `RELEASES.md`, `tests/`, `tools/` or `agents/` no
  longer rebuild; a new 00:10 UTC build runs just after the allowance resets.
- Office agents and their checks run without `API_FOOTBALL_KEY`.
- Raj's source retries (#7) restored: the earlier revert blamed it wrongly.

**Why** On 5 Oct the allowance ran out by 01:43 UTC after several rebuilds and
agent builds, every call was then retried, the build took 3 hours instead of
7 minutes, and later merges cancelled the scheduled build. Today's Daily List
was built with little football data.

**Roll back** `git revert` this commit.

---

## 2026-10-05 Odds tab group rules backtested, unchanged (tag pending)

**What changed:** nothing a reader sees. The group rules stay as they are. A replay script and a write-up only.
**Evidence:** the live record is 7 groups (5 settled: 1 won, 4 lost, expected 1.49 wins). Archived predictions hold neither the tested rate shown that day nor bookmaker prices, so the replay (`tools/groupings_backtest.py`) uses the 14 graded football days in `record.json`, a pick's calibrated confidence as its chance and the fair price as its price. It produced 3 Steady groups (3 won, stated 35%) and no Balanced or Stretch groups at all: with fair prices on picks of 65%+ the products rarely reach 4. Three groups cannot support any rule change.
**Files:** `tools/groupings_backtest.py`, `claude/odds-groupings.md`, `RELEASES.md`.
**Not changed:** `groupings.py`, any model, the 65% / 30 bar, the bands, the spread rules.
**Roll back:** `git revert` the merge commit.

## 2026-10-05 Odds tab: ESPN soccer prices for unpriced football legs (tag pending)

**What changed:** football legs API-Football does not price now try ESPN's soccer scoreboards (DraftKings three-way moneyline), matched on the competition's ESPN slug, kick-off within 90 minutes and both team names. Fewer legs fall back to the model's fair price. Prices never feed any model.
**Evidence:** today's published pool (generated 2026-10-05 04:23Z): 24 football legs, 0 priced by API-Football in that run; ESPN priced 12 of 24 (15 calls). Unmatched: friendlies, U21 and Africa/Concacaf qualifiers ESPN carries no odds for. Rugby and tennis checked: ESPN rugby and tennis scoreboards carry no odds, so they stay estimates (at most two per group). Tests in `tests/test_groupings.py`.
**Files:** `groupings.py`, `tests/test_groupings.py`, `RELEASES.md`.
**Not changed:** any model, calibration, group rules, tennis and rugby pricing, API-Football matching.
**Roll back:** `git revert` the merge commit.

## 2026-10-05 Daily List bar replayed, unchanged (tag pending)

**What changed:** nothing a reader sees. The league bar stays at 80%. Write-up only.
**Evidence:** walk-forward replay, win picks. 80%+: 81.9% of 94 (2025/26), 81.8% of 11 (2026/27). 75%+: 79.4% of 189, the extra 95 picks landed about 77%; bootstrap change vs 80% +2.5 points, 90% interval -2.4 to +7.5, so no real difference. 85%+: 69.2% of 39, change -12.4 points, interval -21.6 to -4.6, clearly worse. Per-league bars: no league reaches 30 picks at 80%, so nothing to fit.
**Files:** `claude/daily-list.md`, `RELEASES.md`.
**Not changed:** `build.py`, `LIST_MIN`, any model number.
**Roll back:** `git revert` the merge commit.

## Rolling back

The bot commits the daily archive to `main` between releases, so never
`git reset` past a release: that deletes graded predictions. Revert instead,
which leaves the bot's commits alone:

```
git log --oneline release-2026-09-27^..release-2026-09-27   # the release's commit(s)
git revert --no-edit <commit>                               # one commit
git push                                                    # deploy.yml rebuilds the site
```

A release with several commits: revert them newest first, or
`git revert --no-edit <first>^..<last>`. If a revert conflicts on a
bot-written file (`predictions/`, `record.json`, `current/`), keep the
current copy: `git checkout --ours <file>`.

---

## (tag pending) — Calibration by confidence band: new advisory tool and findings

**What changed for a reader:** nothing on the site. Adds `calibration_bands.py`,
which measures landed versus quoted by confidence band from history (never
`record.json`) with a bootstrap 90% interval on each gap, for football and for
NFL, baseball, basketball and rugby. Findings are in
`claude/calibration-bands-2026-10-05.md`.

**Evidence:** football's cumulative bands from 62% to 80% sit inside their
intervals (e.g. 70%+: 77.4% quoted, 78.4% landed, n 310); the 85%+ tail is
over-confident (40 calls, 89% quoted, 70% landed, in-sample). Baseball is
over-confident out of sample (62%+: 65.8% quoted, 61.0% landed, n 608,
interval -8.1 to -1.5); NFL, basketball and rugby are within noise. Football
ran on openfootball and `history/` only (the sandbox could not reach the other
sources): 866 check fixtures rather than 1,309.

**Files:** `calibration_bands.py`, `tests/test_calibration_bands.py`,
`claude/calibration-bands-2026-10-05.md`, `RELEASES.md`.

**Not changed:** `calibration.json`, `sports.json`, `sports.py` gates, any
model constant or displayed number. Proposals (baseball calibration guard, an
85% display cap) are written up for Douglas.

**Roll back:** `git revert` the merge commit; nothing else depends on the tool.

## (tag pending) — Championship misses broken down; carrying promoted/relegated ratings held, not shipped

**What changed for a reader:** nothing on the site. A dated note records where
the Championship's misses sit and one new test, so nobody repeats it.

**Evidence:** history only, live model and calibration, paired bootstrap.
Draws (about 27%) and the small-gap middle games carry the loss; big-gap games
are fine. Carrying promoted/relegated clubs' ratings across divisions (the live
path) scored worse than a neutral 1.00 start in all three seasons: +0.0040
(2024-25, p(worse) 0.998), +0.0018 (2025-26, 0.831), +0.0088 (2026-27, 95
fixtures, 0.941). The 2026-27 confirm sample is under the 250-fixture gate and
only 3 clubs a source a season, so held, not applied.

**Files:** `claude/championship-newcomers-2026-10-05.md`,
`tools/championship_newcomers.py`, `replay.py` (optional `extra_prior`
parameter, off by default, no behaviour change).

**Not changed:** `engine.py`, `build.py`, calibration, any model number.

**Roll back:** `git revert` the merge commit.

---

## (tag pending) — Premier League home-advantage test: rejected, write-up only

**What changed:** nothing a reader sees. Added `claude/premier-league-test-2026-10-05.md`
recording a rejected en.1 home-advantage test so nobody repeats it.

**Evidence:** the model over-states Premier League home wins (46-48% vs 41-43%
actual) and under-states draws in 2024-25 and 2025-26. A lower en.1 home tilt
(ha_scale 0.8) gained 0.0007 log loss on the fit season 2025-26 with p(worse)
0.36 (limit 0.30), and the 2026-27 check has 50 fixtures (needs 250). Gates not
passed, so no change.

**Files:** `claude/premier-league-test-2026-10-05.md`, `RELEASES.md`.

**Not changed:** `engine.py`, `calibration.json`, any model constant.

**Roll back:** `git revert` the commit; no behaviour depends on it.

---

## (tag pending) — Ratings test: between-season carry-over and a prior for new sides (rejected / deferred, notes only)

**What changed:** nothing in the model. Dated note added to `claude/tuning-evidence.md`.

**Evidence:** paired bootstrap under the live curve, 2025/26 (6,474) and 2026/27 (1,386). Carry-over c 0.7 / 0.85: worse on both (+0.0020 / +0.0008; +0.0041 / +0.0017). c 1.1 / 1.25: -0.0003 on the fit season, below the 0.0005 gain gate. A 0.90/1.10 prior for sides with no prior season: -0.0014 fit, -0.0011 check (p(worse) 0.18), but measured in a replay that gives promoted sides 1.00 where live carries a transferred rating, and calibration was not refitted. Not shipped.

**Files:** `claude/tuning-evidence.md`, `RELEASES.md`.

**Not changed:** engine.py, replay.py, calibration.json, any site output.

**Roll back:** `git revert` the commit; docs only.

---

## (tag pending) — Tennis hit-rate check: no model change (write-up and advisory test)

**What changed:** nothing a reader sees. Tennis showed 57% against 61% quoted over 294 matches; this checks why and tests one fix. No model number changed.

**Evidence:** ATP 61.9% landed vs 62.2% quoted (n=118); WTA 54.5% vs 60.6% (n=176), concentrated in sub-tour-level events and thin-history players (WTA under 20 rated matches: 47.6%, n=42). The gap is 1.3 standard errors. All 738 archived prices are labelled Hard (ESPN has no surface). Test: shrinking picks that involve a thin-history player, fit 2025, checked on 2026 with tune_tennis.py data, best log-loss gain 0.0012 against the 0.005 gate. Rejected.

**Files:** `claude/tennis-hit-rate.md`, `tools/tennis_thin_test.py` (advisory, writes nothing), this entry.

**Not changed:** `tennis.json`, `build_tennis.py`, `tune_tennis.py`, football, any record or archive.

**Roll back:** `git revert` the commit; nothing else depends on it.

## (tag pending) — Independent evaluation layer and a merge gate that fails closed, without owner review

**Merged 5 Oct 2026 on Douglas's approval, adapted to his 4 Oct instruction
(no owner review).** `agents/policy.json` now lets every class except
workflow/security merge without review, with no waiting period; model and
calibration changes need an evaluation verdict of pass (n/a is not enough),
so they hold until an approved snapshot exists. Agents cannot touch
`agents/`, `CLAUDE.md` or `AGENTS.md`, so workflow/security changes only
come from people. The office sprint opens each pull request with the
footyalmanac-office App token and calls `merge_gate.py --pr N --wait`, which
waits for Tests and Evaluation on the head commit before deciding. Bot paths
now include the groupings archive and the other bot-written files.
`tests/test_merge_gate.py` updated (25 cases).

The original description follows.


**What changed** Nothing on the site and nothing in the model.

- **The office merge gate** now decides from evidence instead of labels:
  - required checks green on the current head commit
  - evaluation evidence from the verified run
  - confirmed mergeability
  - no non-bot changes on main since the evaluation
  - Douglas's approval of that exact commit for anything beyond docs

  Merges are pinned to the head commit.
- **A new Evaluation check** runs on every pull request. Main's harness compares main against the pull request on an
  approved frozen snapshot, on identical fixtures, and posts log loss, Brier, accuracy and a paired bootstrap.
  Insufficient evidence holds the pull request.
- **Agent pull requests** are opened with a GitHub App token so their checks actually run, and the script
  that opens them can no longer be edited by the agent.

**Evidence**
- `python3 -m unittest discover -s tests`: 69 tests pass, including 22 new gate cases (stale labels, stale CI,
  other-app checks, unknown mergeability, approvals of older commits, bot approvals, base drift) and 10 scorer cases.
- End-to-end run of `predict.py` and `score_pair.py` on a synthetic snapshot: a changed `RHO` was detected and,
  with 132 check fixtures, correctly returned `insufficient`.

**Files**
- `agents/merge_gate.py`, `agents/policy.json`, `agents/open_pr.sh`
- `evaluation/`
- `.github/workflows/evaluation.yml`, `.github/workflows/evaluation-freeze.yml`, `.github/workflows/office-agents.yml`, `.github/workflows/office-merge.yml`
- `tests/test_merge_gate.py`, `tests/test_score_pair.py`
- `claude/evaluation-layer.md`, `claude/office-agents.md`, `CLAUDE.md`

**Not changed** `engine.py`, `calibration.json`, `tune.py`, `replay.py`, `build.py`, `deploy.yml`, `tune.yml`, any data.

**Roll back** `git revert` the merge commit.

---

## 2026-10-05: free source search for uncovered leagues, nothing to add (tag pending)

**What changed.** Nothing a reader sees. Documented that no free automatable source exists for Croatia, Serbia, Ukraine, Hungary or South Korea (`claude/free-source-search-2026-10-05.md`).

**Evidence.** football-data.co.uk has no file for those leagues, and its other 11 extra leagues match ESPN's volumes already (e.g. China 208 v 208, Norway 168 v 168, Sweden 176 v 176). ESPN has no scoreboard for them. TheSportsDB's free key returns 5 events per season in every league tried.

**Files.** `claude/free-source-search-2026-10-05.md`, `RELEASES.md`.

**Not changed.** No code, no model numbers, no sources, no Daily List rule. Suggested next step: API-Football ids for the five top flights, replayed before any list place.

**Roll back.** `git revert` the merge commit.

---

## 2026-10-05: openfootball and football-data.co.uk retry, and an outage is no longer remembered as "no data" (tag pending)

**What changed.** Two sources had no retry. `_get` (openfootball, the source for most leagues) failed on the first timeout. `_fdx_text` (football-data.co.uk, the sole source for Poland, Switzerland, Romania, Finland and Ireland) swallowed every error and cached an empty string for the rest of the build, so one blip silently dropped a league's history and fixtures. Both now go through `sources._open`: 3 tries, 1.5s then 3s backoff, retrying timeouts, resets, 5xx and 429. A 4xx such as 404 is raised at once (openfootball callers rely on it to fall back to the plain-text schedule). A final failure prints a warning to stderr. `_fdx_text` no longer caches an outage; a genuinely missing file (4xx) is still cached as empty. Existing Rule 9 behaviour is unchanged: a build that comes out empty is still refused.

**Evidence.** New `tests/test_source_failures.py` (5 tests, fake failing source): retry then success, 404 not retried, loud give-up, outage not cached, missing file cached. Full suite 93 tests pass, `nametest.py` all clear, fast build wrote 123 fixtures across 2 days.

**Files.** `sources.py`, `tests/test_source_failures.py`, `RELEASES.md`.

**Not changed.** No model numbers, no ESPN or API-Football paths (API-Football already retries), no output on a healthy build. Worst-case added latency per dead URL is about 4.5s plus timeouts.

**Roll back.** `git revert` the merge commit.

---

## (tag pending) — Data quality: Turkish Super Lig was fed twice

**What changed** Four of the five Super Lig fixtures on 9-10 Oct appeared twice
on the board, once from `tr.1` and once from API-Football's `af.203`, priced
with different ratings (Galatasaray v Kasimpasa 61.6% vs 64.1%, the second a
reserve pick). The build now skips `af.203` (`engine.AF_DUPLICATES`); `tr.1`
stays the single feed. `af.203` remains in `LEAGUES` so archived rows still
grade. `nametest.py` now fails if a listed duplicate feed is built again.

**Evidence** Audit of `predictions/2026-10-04.json` (1,512 rows): no exact
duplicates, no reversed fixtures, no unrated rows, every row has a kickoff.
Names differ in spelling (Kasimpasa / Kasımpaşa) so the repeat only showed by
kickoff time. Checked all 227 `af-leagues.json` entries against native leagues:
`af.203` is the only one duplicating a feed that is live (af.144 Belgium and
af.202 Tunisia are top flights too, but `be.1` / `tn.1` carry no fixtures, so
nothing doubles today). Dates: 42 rows have a UTC kickoff on a different day
from their row date (Americas evening games, 4 with kickoff 00:00-00:30Z the
next day); consistent with the documented convention of local-day rows, so left.
Cost: Samsunspor v Trabzonspor was only in `af.203`, so it drops off the board
(a missed fixture rather than a doubled one).

**Files** `engine.py`, `build.py`, `nametest.py`, `RELEASES.md`,
`claude/data-integrity.md`.

**Not changed** Any model number, `af-leagues.json`, Belgium and Tunisia
(re-check if `be.1` / `tn.1` ever get fixtures).

**Roll back** `git revert` the commit.

## (tag pending) — Tests for sports.py, and one Elo fix

**What changed** `sports.py` (707 lines, the NFL / baseball / basketball / rugby
model) had no tests. `tests/test_sports.py` adds 34: Elo update and margin
step, the off-season regression, `replay` warm flag, calibration fit,
`losses` / `bands` / `paired`, `list_threshold` (the Daily List gate),
`accuracy_for`, ESPN event parsing and the form / record / head-to-head
summaries. They exposed one bug: `Elo.get` regressed a team towards 1500 after a
break of more than 90 days but left the team's last-game date alone, so each
further `predict` for that team regressed it again. In `build`, a team with two
upcoming games in the 7-day window after a break (MLB or NBA opening week) was
priced from a doubly shrunk rating. `get` now stamps the date when it regresses.

**Evidence** The new regression test fails without the fix and passes with it.
History replay is unchanged: `update` already stamps the date straight after
`predict`, so the tuned parameters and `sports.json` are untouched. Only
repeated predictions without an update (the upcoming slate) change, and only
after a break. No model constant moved.

**Files** `sports.py` (one line), `tests/test_sports.py`, `RELEASES.md`.

**Not changed** `sports.json`, calibration, thresholds, any record or archive.
`nametest.py` could not complete in the sandbox (it fetches, and the network is
blocked); CI is the check.

**Roll back** `git revert` the release commit.

---

## (tag pending) — England Championship: home advantage and draw handling tested, rejected

**What changed** Nothing a reader sees. A league-specific home advantage and a
different draw correlation for the Championship were tested and rejected; a
dated note records it so nobody repeats it.

**Evidence** Paired bootstrap on history only. Fit season 2025-26 (557): ha 0.8
-0.0019 log loss, p(worse) 0.13. Extra season 2024-25: +0.0027, p(worse) 0.95
(sign flips). Confirm 2026-27 (95 fixtures, gate needs 250): -0.0002, p(worse)
0.47. Rho from 0 to -0.10 moves log loss by 0.001 at most. Fails the gates.

**Files** `claude/championship-test-2026-10-04.md`, `RELEASES.md`.

**Not changed** `engine.py`, calibration, any model number.

**Roll back** `git revert` the commit; nothing else depends on it.

## release-2026-10-04-3 — Office agents: daily sprint for every agent, merging without owner review

**What changed** On Douglas's instruction the office agents no longer wait for
his review. `office-agents.yml` runs a sprint: all fourteen agents
(`agents/pick_task.py` SPRINT, including Priya, Oscar and Jade) work one at a
time on their most urgent task or their standing task, each starting from the
latest main. `agents/open_pr.sh` now also runs the unittest suite, opens the
pull request and closes it (report kept) if checks failed, a model change did
not pass every gate, or the agent would not ship it; otherwise
`agents/merge_gate.py --pr` merges it at once and tags it. The site redeploys
once at the end. The 22:00 window keeps merging leftovers, without the 12-hour
wait. The Claude token is trimmed of pasted whitespace and branches are pushed
with the workflow token (earlier today's fixes).

**Evidence** Workflow and scripts parse; `pick_task.py --agent` returns a task
for every agent locally; first sprint dispatched straight after release.

**Not changed** Protected files, the model, calibration, the Daily List.

**Roll back** `git revert --no-edit <commit>`, or disable "Office agents" in
the Actions tab to stop everything.

---

## release-2026-10-04-2 — Odds tab: daily record of the groups, and a Google link on every pick

**What changed** The Odds tab now reports how its groups did. The first build
of each UK day archives that day's groups to `groupings-archive/<date>.json`
(never overwritten), and every build grades every archived group from the
site's own results: each leg Won, Lost, Void or Pending; a group Lost as soon
as one leg loses, Won when every leg has won or been voided (a void leg drops
out of the price). A "How the groups did" panel under the cards shows groups
won against the number expected from their tested chances, first choices,
legs won, the return on 1 unit a group, each band, and the last 14 days with
every leg and its score. Every pick on the tab, in the cards and in the
record, has a "Google predictions" link that searches "<home> vs <away>
prediction <date>" in a new tab.

**Seeded** `groupings-archive/2026-10-04.json` is the groups as published on
the live tab at 13:12 UTC on 4 Oct (the tab's first day), so today's groups
are graded tomorrow morning.

**Evidence** `tests/test_groupings.py` adds leg grading (football by date and
names, tennis by key with voids, other sports by id). Suite OK. Checked in a
browser at 1366px and 400px.

**Not changed** No model, list, record or grading change elsewhere; prices
still never feed a model.

**Files** `groupings.py` (archive, `grade()`, `--grade`), `index.html`
(record panel, Google links), `.github/workflows/deploy.yml` (groupings step
moved before the archive commit; `groupings-archive/` and
`groupings-record.json` committed by the bot), `groupings-archive/`,
`groupings-record.json`, `tests/test_groupings.py`, `CLAUDE.md`.

**Roll back** `git revert --no-edit <commit>`; keep the bot's archive files.

---

## release-2026-10-04 — The Odds tab: groups of five with a spread of prices

**What changed** A new **Odds** tab, second in the nav after the Daily List,
at Douglas's request (4 Oct 2026). Each day (today and tomorrow) it shows up
to six five-leg groups, none sharing a pick: Steady (combined odds 2.5-4),
Balanced (4-7) and Stretch (7-14), each with an alternative. Every card shows
the combined price, what a stake returns (stake box, remembered on the
device), the chance all five land on tested rates, the bookmakers' implied
chance when every leg is priced, a strip showing the spread of prices, and
each leg with its kick-off, price and tested chance. Legs already under way
are greyed and the card says so.

**How a group is picked** (`groupings.py`, docstring has the detail) A leg
must be the model's pick (no draws, no tennis qualifying) with a tested rate
of at least 65% over at least 30 games. Its chance is that tested rate,
shrunk toward the model's number on small samples. Each group needs a short
price (<1.30) and a middle one (1.30-1.60), Balanced and Stretch also one at
1.60+, at most two under 1.15, at most two estimated prices, at most two legs
from one competition; then the highest joint chance in the band, with a small
preference for mixed sports and for legs whose tested rate beats the
bookmaker's implied chance.

**Prices** Football: API-Football `/odds` (Match Winner, average across
bookmakers), matched by date, kick-off within 90 minutes and both names,
about 50 calls a day on the Pro plan. NFL, baseball, basketball: ESPN
scoreboards (DraftKings moneyline) by ESPN id. Tennis and rugby: the model's
fair price, marked *, until a price source is added. Probe on 4 Oct: 47 of 76
qualifying football legs and 10 of 10 NFL legs priced.

**Evidence** `tests/test_groupings.py` (7 tests: tested-rate rule and
shrinkage, band and spread, short and estimate limits, one competition at
most twice, no shared legs). Full suite 53 tests OK. Checked in a browser at
1366px and 400px.

**Not changed** No model, calibration, Daily List, record or grading change.
Bookmaker prices never feed a model or the list; they only price the groups.
The owner's standing decision stands; the Odds tab is a separate board.

**Files** `groupings.py` (new), `index.html` (Odds tab, styles, view switch),
`.github/workflows/deploy.yml` (build groupings after the rebuild, allowed to
fail; copy `groupings-data.js` and `groupings.json` to the site),
`.gitignore`, `tests/test_groupings.py`, `CLAUDE.md`.

**Roll back** `git revert --no-edit <commit>`; the tab disappears on the next
deploy and nothing else moves.

---

## (tag pending) — Calibration refits must beat the live curve

**What changed** Nothing on the page and no calibration change. `tune.py
--fit` now gates a candidate curve against the calibration the site is using
(`calibration.json`, or the flat 1.15 only when the file is missing), scored
on the same fixtures. Before, it was always gated against the flat 1.15, so a
curve that beat 1.15 but not the live curve could replace it. The `--report`
sweep's baseline is the live configuration too. The fit report and
`tuning-report.json` name the baseline and candidate parameters, the fixture
counts and the exclusions. New `--snapshot FILE` runs either on a frozen
snapshot and writes nothing.

**Evidence** Frozen snapshot `aa19d05b...`, live curve 1.135 / −0.30: old
gate passes candidate 1.155 / −0.30 (−0.0006 against 1.15, p(worse) 0.09);
new gate fails it (+0.0001 against the live curve, p(worse) 0.75). Same
fixtures, fit 6,474, check 1,386. Openfootball-only snapshot `cc08a335...`:
candidate 1.13 / −0.30, gain 0.0000, fails minimum gain. 9 new tests in
`tests/test_calibration_gate.py` (46 in all).

**Files** `tune.py`, `tests/test_calibration_gate.py`, `CLAUDE.md`,
`claude/tuning-evidence.md`.

**Not changed** `calibration.json`, the gates' thresholds (250 fixtures,
p(worse) 0.30, gain 0.0005), the bootstrap, every model constant,
`tune.yml`, `deploy.yml`.

**Roll back** `git revert` the merge or commit.

---

## release-2026-10-03-2 — Football evaluation infrastructure (audit fixes)

**What changed** Nothing on the page. Underneath, the harnesses that judge the
football model and fit its calibration were fixed after an external audit
(Julius, 1 Oct 2026), reviewed at commit `6ab010b` and merged without
rewriting history:

- `tune.py` (which fits `calibration.json`) and `backtest.py` now share one
  walk-forward replay (`replay.py`) built from the live build's engine
  functions. Before, `tune.py` normalised this season by last season's goal
  rate while `backtest.py` and the live build used this season's.
- The replay is batched by date: a match sees only results from earlier
  days, never a same-day result that came first in the file.
- Seasons that overlap, are missing, or hold rows outside their calendar
  window are refused and listed, not silently used (`replay.py --audit`).
  Excluded today: en.3 (corrupt 2025-26 file), mx.1 fit, and five 2024-25
  files with rows dated 2026.
- The live build drops matches that appear in both a prior and the current
  season (mx.1 21, ru.1 9, dnk.1 6), loudly.
- The prediction archive stamps `published` and `kickoff` and accepts no new
  entry once a fixture's start has passed (known kick-off, or 10:00 UTC the
  day before when unknown). `score.py` labels every row `verified`,
  `verified-by-date`, `legacy-unverified` (graded), or `late` /
  `timing-unverifiable` (not graded, counted apart). `record.json` gains a
  `verification` block. All 11,874 earlier rows are legacy, still graded,
  prices untouched.
- `backfill.py` uses evidenced season bounds for mx.1, ru.1 and dnk.1 and
  stops each walk before the next season's first result.
- 37 regression tests (`tests/`), run on Python 3.12 and 3.13 by
  `.github/workflows/tests.yml` for pull requests and branch pushes.

**Evidence** Identical fixtures, frozen snapshot `aa19d05b...`: fit
2025-26 (6,474) old tune 1.02402, old backtest 1.02398, new both 1.02395;
check 2026-27 (1,386) 1.02630 / 1.02568 / 1.02564. New tune and backtest
agree to 7e-16. Openfootball-only snapshot `cc08a335...` reproduces the same
pattern. Golden test: engine outputs unchanged to 1e-12. Julius verified
`ed33bdc` independently (36 tests, Python 3.13). On the merged main: 37
tests pass, `nametest.py` passes, fast build 99 fixtures. Full write-up:
`claude/evaluation-audit.md`.

**Files** `replay.py`, `engine.py` (refactor only), `tune.py`, `backtest.py`,
`build.py`, `score.py`, `sources.py`, `backfill.py`, `tests/`, `tools/`,
`.github/workflows/tests.yml`, `.gitignore`, `claude/evaluation-audit.md`,
`claude/proposals/`, `CLAUDE.md`, `AGENTS.md`.

**Not changed** `calibration.json`, every model constant, odds (still out of
every prediction), the site, `tune.yml`, `deploy.yml`. Not included: the
history repairs, the League One prior and the cache-expanded calibration
coverage (`claude/proposals/`, each awaiting a decision). No refit was run.
The next Monday refit (5 Oct, 04:40 UTC) will be the first on the corrected
calculation, under the same gates.

**Roll back** `git revert -m 1 <merge commit>` (the merge of
`audit/eval-infrastructure`), then `git push`. Archive rows written in the
meantime keep their extra `published` / `kickoff` fields; the old `score.py`
ignores them.

---

## release-2026-10-03 — Office agents develop the project unattended

**What changed** Nothing on the site. Two scheduled workflows let the
Footyalmanac HQ agents do real development work. Each morning at 06:30 UTC,
one agent takes the most important objective that is behind (weakest league,
calibration gap, unrated fixtures, a failed build and so on) and works on it
with Claude under CLAUDE.md's rules. The workflow then runs `nametest.py`
(plus a fast build if pipeline code changed) and opens a labelled pull
request. Each evening at 21:00 UTC, the merge window ships pull requests that
pass every gate, tags them and redeploys. Everything else waits for Douglas.

**Evidence** `agents/pick_task.py` run against today's record picks "Lift
accuracy in England Championship" (37% over 76 games) for Mia. Both workflows
skip quietly until an `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` secret
is added.

**Files** `.github/workflows/office-agents.yml`, `.github/workflows/office-merge.yml`,
`agents/`, `claude/office-agents.md`, `CLAUDE.md`, `AGENTS.md`.

**Not changed** The model, the data, the site, `deploy.yml`, `tune.yml`, `claude.yml`.

**Roll back** Disable the two workflows in the Actions tab, or `git revert` this commit.
Stop a single change by adding the `hold` label to its pull request.

---

## release-2026-10-01 (tag pending) — Daily List can be ordered by kick-off

**What changed** The Daily List has an "Order by" switch: Strongest (as
before, the default) or Kick-off time, in UK time. Ordering by kick-off keeps
the bar: each day's picks that clear 80% still come first, then the reserve,
each group in time order. The same 20 a day are chosen either way; only the
order they are shown in changes. The choice is remembered on that device.
The fixtures board already had a Time order and is unchanged.

**Evidence** Checked in Chromium at 1280px and 400px: the switch, the
headline ("by kick-off"), times ascending within each group, no script errors.

**Files** `index.html` only.

**Not changed** Which games make the list, any number, any rule.

**Roll back** `git revert` this commit.

---

## release-2026-09-30-10 (tag pending) — Competition filter collapses

**What changed** The competition chips took up most of a phone screen once
the 227 wider leagues arrived. They now sit behind one compact control,
"Competition [All ▾]", which opens a scrollable panel with a finder box:
type a country or league ("spain", "national league") and only matching
chips stay. The control shows what is picked (All, the league name, or
"n selected"). Wider-league chips show their full name, since their short
codes meant nothing. Picking works exactly as before.

**Evidence** Checked in Chromium at 1280px and 400px: closed, open,
filtered, and after a pick. No script errors.

**Files** `index.html` only.

**Not changed** Any model number, pick or filter rule.

**Roll back** `git revert` this commit.

---

## release-2026-09-30-9 (tag pending) — Fix: clubs matched only within gender, country and continent

**What changed** Every club name resolved through one shared pool, with no
notion of men's and women's football or of a cup's country or continent,
and whichever league came last won a name clash. So a Women's Champions
League Roma v Barcelona was priced with Roma's men's Serie A record and
Ecuador's men's Barcelona SC: Roma 76%. A club is now resolved only among
leagues of the same gender and, for a cup, of its own country (domestic) or
confederation (continental); a league fixture uses the club's own league
first; a remaining clash takes the stronger league. A club nothing fits is
unrated, so the fixture is withheld, not guessed.

**Evidence** Full build: Roma v Barcelona withheld (neither side has a
women's league record to rate from); no other row moved more than 3 points;
1,230 fixtures, 21 on the Daily List; `nametest.py` exit 0.

**Files** `engine.py` (`WOMEN_CODES`, `eligible_league`), `build.py`
(`team_leagues`, `domestic_of`).

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-30-8 (tag pending) — Fix: API-Football calls paced, all wider leagues fetched

**What changed** The first live build of the wider leagues fetched them ten
at a time; the plan allows five calls a second, the refused calls came back
as errors, and 46 of the 66 leagues playing this week were read as "no data"
(safe: they were left off, not guessed). Calls are now paced at four a
second, a refused call is retried with back-off, and a failure is never
remembered as an empty answer.

**Evidence** 40 calls fired ten at once: 10 seconds, none refused; the three
empty answers are leagues whose 2026 season API-Football has not opened.

**Files** `sources.py`.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-30-7 (tag pending) — Fix: big clubs matched again after the wider leagues

**What changed** The wider leagues added clubs such as "Benfica Castelo
Branco" and "Arronches e Benfica" to the pool the spelling matcher searches,
so a bare "Benfica" in a European tie became ambiguous and `nametest.py`
failed, which stops the deploy (the live site stayed as it was). The
API-Football wider leagues are single-source and found by exact name, so
their clubs are now kept out of the fuzzy pool, in `build.py` and
`nametest.py` alike. release-2026-09-30-6 was pushed with this test failing:
my check read only the test's last line. It never reached the live site.

**Files** `build.py`, `nametest.py`.

**Roll back** `git revert --no-edit <release commit>` (restores the failure).

---

## release-2026-09-30-6 (tag pending) — 227 more leagues worldwide

**What changed for a reader** The Football board now covers 227 more
leagues from API-Football: second and third tiers across Europe, regional
divisions (Spain, France, Italy, Germany, Sweden, Australia...), and top
flights the free sources missed. Their strongest calls can make the Daily
List: a pick from these leagues needs 75%, the level whose calls landed 80%+
in testing, and each row shows these leagues' own tested rate.

**Evidence** Discovery replay of every senior API-Football league the site
did not cover (357 with data, 105,000 fixtures), priced walk-forward with the
live calibration curve. Kept only leagues where the model beat a baseline on
2025 (247), then removed duplicates of covered leagues (Spain Segunda,
Greece, Peru, South Africa, El Salvador, Argentina, Paraguay, Wales, Belarus,
Spain Primera RFEF) and nine women's leagues my first filter missed
(England's WSL among them): 227. As a group, win picks at 75%+ landed
82.3% of 2,236 (2025) and 80.0% of 765 (2026 so far); at 70%+
79.1% / 75.8%, so the bar is 75%.

**Files** `af-leagues.json` (new: the league list), `engine.py` (registers
them: tier 2, strength 0.5, as replayed), `sources.py` (added to `AF`; finished
seasons cached in `.afcache/`), `build.py` (their bands and 75% bar),
`tune.py` (kept out of the shared calibration fit), `deploy.yml` (Actions
cache for finished seasons), `.gitignore`.

**Not changed** Any existing league, the calibration, the other sports.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-30-5 (tag pending) — National League, North and South on complete history

**What changed for a reader** Every club in the National League, National
League North and National League South is now rated from complete seasons.
The free sources held 296 of 552 National League games for 2025/26 and none
at all for North or South, so those clubs had been rated off half a season,
or off 2024/25 alone. All three now come from API-Football, history and
fixtures both, one source and one spelling per league. Numbers on those rows
move; team sheets read "2025/26" instead of "2024/25 + 2025/26 so far".

**Evidence** API-Football: 556, 557 and 557 played games for 2025/26, and
the current season to date. `nametest.py` passes; the build shows no new
unrated clubs (see the check in this session's notes).

**Files** `sources.py` (three leagues added to `AF`; `AF_BOARD_ONLY` now
names the step-3 set), `build.py`, `tune.py` (both read `AF_BOARD_ONLY`).

**Not changed** List eligibility: these three leagues stay on the shared
league bands and rule, as before. Step 3 is still board and reserve only.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-30-4 (tag pending) — English step 3 on the board (API-Football)

**What changed for a reader** The Football tab now carries the four step-3
leagues of the English non-league pyramid: Southern League Premier Central
and South, Isthmian Premier and Northern Premier (Needham Market, Rushall
Olympic and the rest), from API-Football, the first paid source. Each row
shows step 3's **own** tested rate. They are **not on the Daily List**: they
can appear in its reserve, tagged, and are graded like everything else.

**Evidence** Replay of 2025/26 (1,818 fixtures) and 2026/27 so far (388),
each priced from what was known the morning before, the live calibration
applied: log loss 1.034 (the covered leagues run ~1.016); win picks at 70%+
landed 79.0% of 105, at 75%+ 78.6% of 56, at 80%+ 88.0% of 25. No level
lands 80% with 30+ calls, so the shared rule gives no list place. Step 4 is
not carried by API-Football this season.

**Files** `sources.py` (AF source), `engine.py` (four leagues, tier 7 home
advantage = tier 6), `build.py` (step-3 bands, off the list), `tune.py`
(step 3 kept out of the shared calibration fit), `deploy.yml` and `tune.yml`
(the key from secrets), `claude/data-expansion-plan.md`.

**Not changed** Any existing league's numbers, the calibration, the list bar.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-30-3 (tag pending) — Run your starred picks

**What changed for a reader** The Starred tab has a **Run** button. It works
out the chance that every starred pick lands, on the site's own numbers,
shown as a percentage, "about 1 in N" and fair odds (1 ÷ the chance, not a
bookmaker's price), plus how often the slip loses. Each leg gets a verdict:
**Strong** (clears the Daily List bar), **Reserve** (below it, Firm or
better) or **Wary**, with the reason: the FIFA ranking carried it past the
model's own number, a draw pick, under Firm (62%), a Celtic's Law flag, an
unrated side, or a tennis qualifying round. It names the weakest leg and what
the rest are worth without it.

**Evidence** Checked in a browser at desktop and phone width with strong,
reserve and wary legs (a ranking-carried international at 59% on the model's
own number, and a draw pick).

**Files** `index.html`.

**Not changed** Any number on any row, the list, the record. No bookmaker
prices are used.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-30-2 (tag pending) — Every time in UK time

**What changed for a reader** Every kick-off and start time, in every sport,
now shows in UK time (GMT or BST as the date falls), whatever time zone the
phone or computer is set to, and each game sits under its UK calendar day.
Column headings read "UK time". Kick-offs from 35 more countries' fixture
files are converted instead of printed as the local time; the rare fixture
whose source gives no zone at all is marked "local".

**Evidence** Checked in a browser set to London, New York and Tokyo: the
same instants print the same UK times and days in all three.

**Files** `index.html`, `sources.py` (KICKOFF_TZ).

**Not changed** Any number, the list, the record.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-30 (tag pending) — Reserve picks, research links, fresh international ratings

**What changed for a reader**

- **Daily List reserve.** Below the picks that clear the 80% bar, each day
  fills out to 20 with games under the bar but otherwise clean, Firm (62%)
  or better, behind a "Reserve" divider. Each keeps its strength tag and
  tested rate. The reserve is graded as its own group, by tag, and never
  counts in the list's record. A ranked international must be Firm on the
  model's own number too.
- **Head to head and Predictions links** at the top of every expanded row,
  in every sport.
- **International ratings now include 2026.** The shipped ratings had been
  the holdout fit, frozen at 1 January; they are now refitted on every match
  to 30 Sep (10,091) with the same tested method. Men's and women's.

**Tested, not shipped** Bottom-10%-away and weak-goal-record penalties:
worse at every strength on both seasons (up to +0.008 log loss). Table in
`claude/tuning-evidence.md`.

**Recalibration** Sports (`sports.py --tune`): no parameter, calibration or
list-bar change; tested bands refreshed. Tennis (`tune_tennis.py --report`):
constants unchanged, both tours pass. International: refitted as above.
Football calibration: `tune.yml` dispatched on push, full data in CI.

**Files** `build.py`, `build_tennis.py`, `sports.py`, `score.py`,
`score_tennis.py`, `index.html`, `tune_international.py`,
`tune_international_women.py`, `international.json`,
`international-women.json`, `sports.json`, `CLAUDE.md`,
`claude/tuning-evidence.md`.

**Not changed** List bars, tiers, club football model, the record.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-29-3 (tag pending) — This season's results count sooner

**What changed for a reader** Club ratings now lean on this season's results
earlier: a side's current record overrides last season after fewer games.
Most rows move by a point or less. Internationals, tennis and the other
sports are untouched.

**Evidence** Douglas asked for a recent-form-led model. Tested properly
(calibration refitted per setting, paired bootstrap, fit 2025/26, confirmed
2026/27): a form-led model is about 0.005 log loss worse on both seasons,
ten times the smallest change the gates accept, in the wrong direction.
SHRINK_FULL_SEASON 6 -> 4 passed: -0.0004 (p(worse) 0.04), then -0.0007
(p(worse) 0.18) on 789 current-season fixtures. ESPN leagues could not be
fetched from the cloud session; CI builds with them. Table in
`claude/tuning-evidence.md`.

**Files** `engine.py`, `tune.py` (sweep values), `CLAUDE.md`,
`claude/tuning-evidence.md`.

**Not changed** FORM_MAX, BLEND_K, calibration.json (refitted by Monday's
tune.yml), list bars, the record.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-29-2 (tag pending) — Daily List bar raised to 80%

**What changed for a reader**

- Every pick on the Daily List now comes from a level whose calls landed at
  least **four in five** in testing (was three in four), in every sport.
  Football leagues 80%, internationals 75%, tennis 80%, NFL 80%, basketball
  75%, rugby 70%. Baseball still has no place.
- An international re-scored by the FIFA ranking must also reach 75% on the
  model's own number before the ranking. Burundi v Algeria (57% before the
  ranking) could not make the list now.
- This week's football list goes from 35 picks to 10 on the same fixtures.
  The list is shorter on purpose.

**Evidence** The shared rule re-run at 80% on the stored test bands of every
sport (`sports.list_threshold`). Ranked internationals, 2022-24
(`ranktest.py`): both reads 75%+ landed 88.2% of 288; picks the ranking alone
carried to 75%+ landed 74.4% of 195. See `claude/ranking-review.md`.

**Files** `build.py`, `build_tennis.py`, `sports.py`, `sports.json`
(listMin only), `index.html` (list copy), `README.md`, `CLAUDE.md`,
`claude/ranking-review.md`.

**Not changed** Any percentage on any row, the tiers, the full boards, the
graded record (past list picks keep their grades).

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-29 (tag pending) — Ranked internationals: goals line fixed, list bar 65%

**What changed for a reader**

- On an international re-scored by the FIFA ranking, the expected goals and
  likeliest score now agree with the percentage on the row. Burundi v
  Algeria showed Algeria at 79% over a 1-1 scoreline; it would now read
  0.68-2.63, likeliest 0-2. The percentages themselves are unchanged.
- Internationals re-scored by the FIFA ranking now need 65% to make the
  Daily List (was 60%). Fewer, stronger international picks.

**Evidence** `ranktest.py`, new: the ranking adjustment with its weights
frozen, re-checked on Oct 2022 - Oct 2024 (2,024 picks never seen by weights
or ratings). It still helps (-0.0099 log loss, p(worse) 0.012) but runs 3-5
points high; 60%+ landed 73.7% of 949, 65%+ 76.5% of 791. The shared rule
(75% in every window) puts the bar at 65%. Full write-up in
`claude/ranking-review.md`.

**Files** `build.py`, `ranktest.py` (new), `README.md`, `CLAUDE.md`,
`claude/ranking-review.md` (new), `claude/world-rankings.md`.

**Not changed** FIFA_W, the published split, BTTS, over 2.5, club football,
tennis, the other sports. Nothing in `record.json`.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-9 — A flag for every competition

The football competition chips and fixture rows showed flags for only 13
countries. All 71 remaining countries and regions used by the leagues now
have one, drawn as simple flat flags to match the originals (colours and
layout exact, emblems simplified at 15px). Europe's club competitions show
the circle of stars; international, CONMEBOL and CONCACAF competitions show
a globe mark. `index.html` only (the inline flag sprite).

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-8 — Ready for AI agents

No change to the site or models. Documentation and tooling so any AI agent
(claude.ai/code, the Claude GitHub agent, Copilot and others) can add value
without undoing earlier work:

- `README.md` rewritten: the old one described one sport, 20 competitions,
  manual injury entry and overrides, all long gone.
- New `AGENTS.md`: guardrails, how to verify, how to ship (unattended agents
  open pull requests; a push to `main` deploys).
- `CLAUDE.md`: "Working as an AI agent" section (local vs cloud vs GitHub
  agent, the owner's standing decisions), title and intro now multi-sport,
  brand drift corrected.
- New `.github/workflows/claude.yml`: `@claude` on an issue or PR, owner and
  collaborators only (public repo). Needs the `ANTHROPIC_API_KEY` secret.
- New `.github/copilot-instructions.md` and `.gitignore`.
- Banners on the two partly stale `claude/` notes; their content is kept.
- Learned from the first claude.ai/code test (release -6): cloud sessions can
  push branches and commits but not tags, and cannot reach ESPN. The agent
  docs now say so; cloud work goes through pull requests and a local session
  adds the tag.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-7 — Hairline outlines

No dark border is thicker than 1px any more. Reduced to 1px: the cover
outline (3px), tab bar outline and the "How it went" sport switcher (3px),
section headings on "How it went" (3px double), star banner edge, corner
flash, day headers, football filter bar, expanded-row edge and "Show all"
(all 2px), and the old list box rail (6px). Keyboard focus rings stay 2px
for accessibility; the amber flagged-row rail is not a dark colour and is
unchanged. Also removes a duplicated stat-panel rule. `index.html` only.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-6 — README competition count

The README's opening line said the model rates twenty competitions. A
fast local build on today's `main` rates 71 (154 defined in
`engine.LEAGUES`), so it now says "more than seventy". The rest of the
README, including the older backtest figures and the Coverage section, is
unchanged and still stale. This release also tests committing, tagging
and deploying from a Claude Code cloud session. `README.md` only; no
model, data or page change.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-5 — Flush cover header

The star banner, 2026 year band and red stat panel now run edge to edge of
the cover instead of sitting inside a grey margin; the wordmark and
strapline stay on the grey, unchanged. The football record line no longer
runs under the yellow corner. The Daily List headline and "How the list
works" dropdown are kept as they are. `index.html` only.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-4 — The cover header is back

Reverts only the masthead from release-2026-09-28-3, at Douglas's request:
star banner, grey cover, stacked SPORTS / ALMANAC wordmark, strapline,
2026 year band and red stat panel, exactly as before. Kept from -3: the
stat panel's whole-site figures, the sticky tab bar, the Daily List
headline and toggles, the refreshed footer. `index.html` only.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-3 — Slim masthead, sticky tabs, lighter copy

**What changed for a reader**

- The book-cover masthead (~600px) is now a slim dark band that keeps the
  identity: red slab SPORTS, white ALMANAC, the three stars and a one-line
  promise. The first pick now sits about 440px down on desktop, not 820px.
- The stat strip covers the whole site, not football alone: this week's
  window, Daily List picks, games priced across every sport, the list's live
  record, and the football record.
- The tab bar stays pinned while you scroll on desktop (football's filters
  pin just beneath it). On phones both scroll away so they don't eat the
  screen.
- The Daily List opens with a headline ("76 picks this week, strongest
  first") and one sentence explaining "landed"; the full rules sit behind a
  "How the list works" toggle. Sport and tennis tabs get the same headline.
- The football notes are one line plus a "Tiers and flags" toggle.

**Stale copy removed** The "Complete sports statistics" strapline and the
"& more soon" flash; the football tier figures from an old backtest (79%,
66%, 61%); the footer's 2025/26-only backtest numbers and its ~90-league
"no fixtures" list. The footer now describes every sport's model and all
sources.

**Files** `index.html` only.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28-2 — Cleaner rows, one layout for every sport

**What changed for a reader**

- Every row in every sport now uses one column layout: the probability bar
  is the same width in the same place for football, tennis, NFL, baseball,
  basketball and rugby (football's predicted score sits in a narrow middle
  column the other sports keep aligned).
- No more overlapping text: team stat lines truncate cleanly instead of
  running into the bar or the confidence column, "international rating"
  filler removed, tennis lines shortened ("Elo 1815 · 508 played").
- More readable: small labels darkened site-wide to 4.8:1 contrast (from
  3.4:1, below the accessibility minimum), larger names, confidence number
  and bar labels, more space per row, a wider confidence column so
  "94% landed" always fits.
- Column headers now sit exactly over their columns (they ignored the
  bookmark star and sat 30px to the left).

**Files** `index.html` only.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-28 — World rankings in the model

**What changed for a reader**

- Men's international football is now re-scored with the **FIFA world
  ranking**, and ATP tennis with the **ATP ranking**. Both were tested on
  2026 games the model never saw and made the calls measurably more
  accurate: FIFA -0.036 log loss (p(worse) 0.00, the largest gain any
  signal has shown on this site; the strongest 20% of calls went from
  80.9% to 84.3% landed), ATP -0.0037 (p(worse) 0.03).
- Rankings are shown on the rows: FIFA #, ATP #, WTA #. The expanded row
  says when a ranking changed the number.
- WTA rankings are shown but do not move the number: in testing they did
  not beat the ratings. World Rugby rankings have no reachable source.
- Adjusted rows have their own tested accuracy and list thresholds
  (internationals 60%, ATP 65%, by the same 75%-landed rule).

**Files** New `rankings.py`, `fifa-rankings.json`, `claude/world-rankings.md`.
Changed `build.py`, `build_tennis.py`, `index.html`, `deploy.yml` (commits
the FIFA file when a new release is fetched).

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-27-7 — A fuller Daily List, strongest first

**What changed for a reader**

- The Daily List rule is now the same for every sport: a pick is on it only
  if calls at its level landed at least 75% of the time in testing on games
  the model was never tuned on (every test window with 30+ such calls must
  clear it). Each row already shows its own tested rate.
- Resulting thresholds: football leagues 75%, internationals 55% (the
  international fit under-quotes itself: 55%+ landed 75.7% of 177), tennis
  70% (ATP 79.1%/78.1%, WTA 78.1%/80.2%), basketball 70%, rugby 60%
  (78.0%/75.1%), NFL 75%. Baseball still does not qualify.
- Each day is one list across all sports, ranked by tested hit rate, then
  confidence: the strongest pick always leads.
- Football now builds 7 days, like the other sports, so the weekend's club
  football is on the list alongside the weekend's rugby.
- On this week's slate: about 67 picks across 7 days (was about 13), every
  day covered.
- One live record line for the list across every sport.

**Trade-off, stated plainly** The old bar was ~78-80% landed; the new one is
75%. More picks, each a little less certain on average. The ranking puts
the most certain first and every row shows its tested rate.

**Fixes** A hung SSH connection could stall a pull for ever: this repo's
SSH now times out (`core.sshCommand`, local config). The tennis threshold
text handles an older tennis file kept after a failed fetch.

**Files** `sports.py` (`list_threshold`), `sports.json`, `build.py`
(`LIST_MIN` per league/international), `build_tennis.py` (`LIST_MIN` per
tour), `index.html` (ranked list), `deploy.yml` (`--days 7`), `CLAUDE.md`.

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-27-6 — Tested accuracy on every row; football's row features on every sport

**What changed for a reader**

- Every row in every sport now shows how often calls at that level actually
  landed on games the model was never tuned on: a "82% landed" chip under
  the confidence number, and in the expanded row the band, hit rate and
  number of games. That is the figure to judge a pick by.
- NFL, baseball, basketball, rugby and tennis rows now work like football's:
  bookmark star (and they appear on Starred), tap to expand the reasoning,
  each side's season record and last five results, the last meetings, and
  search links for your own research.

**Optimised**

- Tennis confidence shrink re-tested (was a flat 0.8 judgement call):
  ATP 0.9, WTA 0.95. Both beat 0.8 on 2026 (p(worse) 0.03 / 0.04) and cut
  the quoted-vs-landed gap at 65%+ from ~5 points to 1.5. 0.8 was
  under-quoting (75% calls landed 85%). More tennis now reaches the list at
  the same ~81% hit rate.
- Two-parameter calibration tested per sport, with a new honesty guard: it
  ships only if it improves log loss AND does not widen the top-end gap.
  Applied to basketball. Rejected for NFL (the correction flipped direction
  between seasons), baseball and rugby (inflated their strongest calls).
- Football's Daily List backtest line refreshed to the current calibration:
  78.9% of 242 (2025/26), 76.2% of 21 (2026/27), 81.6% of 49 internationals.

**Files** `sports.py` (calibration, honesty guard, per-game accuracy, form,
record, head-to-head), `sports.json` (re-tuned), `build_tennis.py`
(per-tour shrink, accuracy bands), `build.py` (football accuracy bands,
refreshed list backtest), `index.html` (shared two-sided row, accuracy
chips, Starred for all sports).

**Roll back** `git revert --no-edit <release commit>`.

---

## release-2026-09-27-5 — NFL, baseball, basketball, rugby, and an all-sports Daily List

**What changed for a reader**

- Four new tabs: NFL, Baseball, Basketball, Rugby (Premiership, URC, Top 14,
  European cups, Six Nations, Rugby Championship, tests, Super Rugby).
- The Daily List now takes the most likely results from every sport that
  has earned a place: football (75%), tennis main draw (75%), basketball
  (75%), rugby (75%), NFL (80%). Baseball is shown on its tab but kept off
  the list: its strongest calls did not land often enough in testing.
- "How it went" gains an "Other sports" board, grading each pick against
  the result from the day it is first published.
- Fixed: the tennis fixtures tab layout, broken by the previous release's
  results styles.

**Evidence** (games the model was never fitted on, since 1 Jul 2025)

Basketball 67.5% of 1,322 picked the winner (home 54.5%), 75%+ landed
82.9%. Rugby 70.6% of 731 (home 68.9%), 75%+ 84.0%. NFL 63.5% of 317 (home
54.7%), 80%+ 80.7%. Baseball 55.0% of 3,629 (home 52.7%). Tennis 75%+
landed 84.6-86.4% across ATP/WTA 2025-26. Details: `claude/multi-sport.md`.

**Files**

New `sports.py`, `sports.json` (fitted by hand), `history-sports/`.
Changed `index.html`, `build_tennis.py` (list flag), `score_tennis.py`
(list summary), `.github/workflows/deploy.yml` (`sports.py --daily`,
archives, publishes `sports-data.js` / `sports-record.js`).

**Not changed** Football model, tennis ratings.

**Roll back** `git revert --no-edit <release commit>`. The four tabs and
the other sports on the list disappear; if the bot has since committed
`predictions-sports/` or `sports-*`, remove them in the revert.

---

## release-2026-09-27-4 — Poland, Switzerland, Romania, Finland, Ireland

**What changed for a reader**

Five leagues that had no working source now appear and are rated:
Poland's Ekstraklasa, Switzerland's Super League and Romania's Superliga
(ESPN does not carry them), plus Finland and Ireland (no fixture source).
All five come from football-data.co.uk's extra-league files: complete
prior seasons (Poland 306, Switzerland 228, Romania 321, Finland 177,
Ireland 180 matches) and this season's results to date. The rated club
pool goes from 1,063 to 1,275, none resolving to the wrong club.

**Limits**

Their upcoming fixtures come from a weekly next-round file (refreshed
around Friday), so they mostly fill weekends. Only the result and fixture
columns are read; the bookmaker columns in the same files are ignored.

**Files** `sources.py` (`FDX`, `fdx_rows`, `fdx_upcoming`; `fetch_season`
and `fetch_fixtures` route those five leagues there; `kickoff_utc` honours a
row's `tz`, since football-data times are UK time).

**Roll back** `git revert --no-edit <release commit>`. The five leagues go
back to having no fixtures.

---

## release-2026-09-27-3 — Prior seasons for four more leagues

**What changed for a reader**

Russia, the Netherlands' Eerste Divisie, Denmark and the Scottish
Championship now have a prior season on file, so their clubs are rated from
last season instead of from this season's first few games, and their
fixtures can qualify for the Daily List.

| Season | Matches |
|---|---|
| ru.1 2025-26 | 249 |
| nl.2 2025-26 | 380 |
| dnk.1 2025-26 | 200 |
| sco.2 2025-26 | 180 |

This completes the backfill of the 14 leagues ESPN carries (see
`claude/daily-list.md`).

**Files** `history/` only.

**Roll back** `git revert --no-edit <release commit>`. Those four leagues go
back to being rated from this season alone.

---

## release-2026-09-27-2 — Tennis graded on "How it went"

**What changed for a reader**

- The Tennis side of "How it went" now checks every tennis pick against who
  actually won: the match, who the model picked and at what confidence, who
  won and the score, a tick or cross, and hit rates by tier and by tour.
- The record starts on 22 Sep, rebuilt from the 18 versions of
  `tennis-data.js` the site actually published (in git history), with the
  commit time as the publish time. 626 prices qualified; 89 that were
  published after their match had already started were dropped.
- First reading, 105 graded matches: 53% picked the winner against 59%
  quoted. ATP 63% of 43 (quoted 60%), WTA 47% of 62 (quoted 58%). Small
  sample, not fitted on.
- Mexico, Saudi Arabia, Ecuador, Australia and India now have a prior season.

**Fixes**

- `build_tennis.py` priced matches already in play (anything not "post").
  It now prices only matches that have not started.
- A rescheduled tennis match was priced once per date it was listed for;
  it is graded once, on the latest price published before it began.

**How grading works** (`score_tennis.py`)

Only prices published before the scheduled start count. Walkovers and
cancellations are void, retirements count and are marked. New predictions
match their result by ESPN match id; older ones by the two players within
two days, and only when exactly one match fits. Graded matches persist in
`tennis-record.json`, so a failed ESPN day loses nothing.

**Files**

New `score_tennis.py`, `predictions-tennis/` (archive), `tennis-record.json`,
`tennis-record.js`. Changed `build_tennis.py` (archive, id, publish time in
UTC, no in-play pricing), `index.html` (tennis results view, loads
`tennis-record.js`), `.github/workflows/deploy.yml` (runs `score_tennis.py`
after the tennis build, commits the archive and record, publishes
`tennis-record.js`). New `history/` for ec.1, mx.1, sa.1, au.1, in.1.

**Not changed**

Tennis ratings, `CONFIDENCE_SHRINK`, tennis tiers, anything football.

**Roll back**

`git revert --no-edit <release commit>`. The Tennis results tab returns to
"not tracked yet". If the bot has since committed to `predictions-tennis/`
or `tennis-record.*`, the revert may conflict there: delete those files in
the revert (`git rm -r predictions-tennis tennis-record.json tennis-record.js`)
and continue.

---

## release-2026-09-27 — The Daily List

**What changed for a reader**

- The front page is now the **Daily List**: only the fixtures where the model
  gives one side 75% or more to win, never a draw, nothing flagged by
  Celtic's Law, and every club rated from a full prior season. The model's
  own read, no bookmaker input. Empty on days when nothing clears the bar.
  The full board is the Football tab, unchanged.
- The list is graded separately in `record.json` (`list`, `listDays`) from
  its first published day. Membership is archived with each prediction, so
  it is judged on what it said before kick-off.
- Slovenia no longer shows El Salvador's fixtures (see below).
- MLS, USL Championship, Chile, Uruguay and Peru now have a prior season, so
  their clubs are rated instead of dropped.

**Evidence behind the 75% bar** (details in `claude/daily-list.md`)

League walk-forward: 81.0% of 211 landed in 2025/26, 77.8% of 18 in 2026/27.
Internationals, 2026 holdout: 81.6% of 49. Above about 80% the hit rate
stops climbing. Form and last season's head-to-head were tested as extra
signals and add nothing measurable.

**Data fixes**

- `sources.ESPN_SLUGS`: `svn.1` pointed at `slv.1`, El Salvador. Salvadoran
  fixtures were published as Slovenian PrvaLiga from 10 Sep (never graded).
  52 competitions whose every slug returns 400 from ESPN removed; cup and
  international slugs corrected from ESPN's own league index.
- `sources.fetch_espn(clip=False)`: ESPN days are US Eastern, rows are UTC,
  so evening kick-offs in the Americas were clipped out. Backfill lost about
  half of each Americas season (MLS 2025: 259 of 541).
- `score.live_results` also queries the day before, so late kick-offs get
  graded.
- `sources.completeness(games=)` and `"games"` on `us.1`/`us.2`: MLS and USL
  are not round robins, and complete seasons read as 62% done.

**Files**

`build.py` (`LIST_MIN`, `LIST_BACKTEST`, `list_eligible`), `score.py`,
`index.html`, `sources.py`, `engine.py`, `backfill.py` (`--probe --on`),
`tune.py` (`lambdas(features=True)`, off by default), `nametest.py`
(Python 3.7 compatible, same checks), new `predictability.py` (advisory
only), new `history/` (5 seasons), `CLAUDE.md`, `claude/daily-list.md`.

**Not changed**

`engine.py` model constants, `calibration.json`, tier ladder, the full
board's ranking.

**Roll back**

`git revert --no-edit <release commit>`. The site returns to opening on the
Football board; `history/` files go with it and those leagues drop back to
unrated.
