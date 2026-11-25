# Releases

Newest first. Every release is an annotated git tag (`release-YYYY-MM-DD`,
with `-2`, `-3` for a second release the same day) and an entry here.










## 2026-11-25-kickoff-board-right: Bolivia's GV San José priced; Serie B and Greece left off the retime list (tag pending)

**What changed:** board name "GV San José" (Bolivia's División Profesional) is matched to API-Football's "Gualberto Villarroel SJ" (`groupings.AF_SPELLINGS`), so GV San José v Real Potosí (28 Nov) can be priced. A note records that the two kick-off misses on the price log (Palermo v Benevento, Serie B; Iraklis 1908 v Panetolikos, Greece) are API-Football's error, not the board's, so neither league joins `sources.AF_RETIME`.
**Why:** after 20 Nov a named kick-off miss led to a league joining `AF_RETIME`; here the published listings agree with the board (18:30 and 19:00 UTC) and retiming would have moved both games four hours early. The guard left them unpriced, which is right.
**Evidence:** the last 25 deploy logs (Serie B named on 10 builds, Greece on 4); listings in `claude/kickoff-board-right-2026-11-25.md`. `tests/test_football_unpriced.py` `test_af_spelling_bolivia` (fails without the spelling); full suite OK; nametest clear.
**Files:** `groupings.py`, `tests/test_football_unpriced.py`, `claude/kickoff-board-right-2026-11-25.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** `AF_RETIME`, any Card rule (`CARD_RULE` 14), the model, the page.
**Roll back:** `git revert` the merge.

## 2026-11-25-results-crosscheck: graded football results checked against API-Football (tag pending)

**What changed:** `periods.py` already matched every graded football fixture to API-Football's cached day file for its half-time score, and threw away any whose full time disagreed with the graded result, counting it only. It now names each one in `periods/disagree.json` (both scores, API-Football's fixture id and names, how closely the names match) and in the build log, keeps it while the record grades the fixture the same way, and drops it and looks again when the record is regraded (the half time is then kept). The nightly Card review's integrity check raises `result-disagrees` when a settled football leg of a slip Douglas stakes (the Card, the Daily 2x, the List card) is one of them, with both names at 0.8+ similarity.
**Why:** #472 asks for a second source on the graded results. A wrong grade on a Card leg misstates the Card's record, and nothing compared the record with an independent score; the data to do it was already read every build and discarded.
**Evidence:** a check, no rule read. `tests/test_results_crosscheck.py` (three: named, not marked missed, dropped on regrade; raised only for staked, settled, football, closely named legs from today); full suite (1,454) OK; nametest clear; the integrity check on today's record: 0 findings. The sandbox has no API-Football cache, so the first CI build's "periods:" lines are the first read.
**Files:** `periods.py` (`DISAGREE`, `disagreements`, `_write`), `tools/card_integrity.py` (`result_disagrees`, `DISAGREE_FROM`, `DISAGREE_SIM`), the test, `claude/results-crosscheck-2026-11-25.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any grade (nothing regrades from API-Football; a person tells a wrong grade from a wrong match), any Card rule (`CARD_RULE` 14), the page, the model. Disagreements found before today sit in `periods/missed.json` and are not looked at again.
**Roll back:** `git revert` the merge; `periods/disagree.json` can stay or be deleted.

## 2026-11-25-card-short-log: the page keeps its own read of each Card day (tag pending)

**What changed:** every build now logs, for each day it builds, what the page saw of the Card: whether a group stood (and its picks) or `card_short`'s reason (few, spread, long, short, chance), and the picks clear of the rule at that build's prices. A day's entry is added only when that changed, kept 30 days in `groupings-archive/card-short.json` (committed with the archive). The nightly Card review's Fidelity block reads it for every group the replay built and the page did not: whether the page ever had those picks clear together, else how often each was clear, and the last read.
**Why:** on 23 and 24 Nov the pool replay built groups at first prices (Hammarby IF, Oklahoma City Thunder, San Antonio Spurs; Boston Celtics, Salisbury, Torquay) and the page left both days empty, and nothing kept what the page saw build by build. The 30 Nov read of rule 14 against `rule13` rests on how far the replay's live row is the page's Card; this answers it from the page's side from today.
**Evidence:** a logging change, no rule read. `tests/test_card_short_log.py` (nine); full suite OK; nametest clear; a local fast build and `groupings.py` run wrote the log.
**Files:** `groupings.py` (`card_cands`, `short_entry`, `log_short`, `SHORT_LOG*`; `card_short` reads `card_cands`, worked once a day a build), `tools/card_review_post.py` (`_page_read` in `fidelity_why`), the test, `claude/card-short-log-2026-11-25.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any Card rule (`CARD_RULE` 14), the page, the record, the model.
**Roll back:** `git revert` the merge; the log file can stay or be deleted.

## 2026-11-25-settle-rematch: football legs settle only from their own fixture (tag pending)

**What changed:** a football leg (Card, Daily 2x, List card, the pool replay and every tool that settles pool legs) is settled only by a result of the same ordered pair within 3 days of its date, nearest first. Before, a miss fell back to any meeting of the pair in the record: the replay had settled five unplayed MLS and Liga MX play-off games (26 to 28 Nov) from league games up to two months old, and two retired groups (4 and 18 Oct) took the result of a postponed game played weeks later; those legs are now voided by the grader, as a bookmaker would.
**Evidence:** `claude/settle-rematch-2026-11-25.md`. Pool replay from 29 Oct: 2,217 to 2,208 settled legs, the window ends 24 Nov (not 28 Nov); live unchanged (11 groups, 5 won v 4.53, +12.5%); `rule12` 25 to 24 groups; `m7under5` 7 to 8 of 19 won. `tests/test_settle_rematch.py` (six); full suite 1,442 OK; nametest clear.
**Files:** `groupings.py` (`SETTLE_NEAR_DAYS`, `_near_result`, `results_index`, `settle`), the test, the note, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any Card rule (`CARD_RULE` 14), the model, tennis and US-sport settling, the archives (nothing edited by hand).
**Roll back:** `git revert` the merge.

## 2026-11-25-nfl-shrink: NFL confidence shrink tested and rejected (tag pending)

**What changed:** nothing on the site. A dated note only: the weakest other sport on the live record is NFL (73 of 116, 62.9% v 65.9% quoted, about -0.8 standard errors); a one-parameter confidence shrink was tested on history.
**Evidence:** paired bootstrap on log loss against live, shrink 0.8 to 1.1. Fit 2024-25 (n 285) prefers no shrink (+0.0025 at 0.90, p(worse) 0.86); check 2025-26 (n 317) gains only -0.0012 at 0.90 with p(worse) 0.31, over the 0.30 gate and under the fit season's sign. Fails Rule 3.
**Files:** `claude/nfl-shrink-2026-11-25.md`, `RELEASES.md`.
**Not changed:** `sports.py`, `sports.json`, every model number and the Daily List bars.
**Roll back:** `git revert` the merge; no behaviour to undo.

## 2026-11-25-replay-differs: the Card review counts the days a variant differs from live (tag pending)

**What changed:** nothing on the site. The nightly Card review's archive table has a "differs: days / legs" column: the days a replay variant's groups are not live's, and its legs on them. A p(worse) on few differing days is thin: `m7cap160` read p(worse) 0.0 on 27 legs, from two differing days and three legs. Rule 13, the only variant at the 100-leg gate, differs on 21 days and all 120 legs, so its read stands.

**Evidence:** `claude/card-replay-differs-2026-11-25.md` (the pool replay from 29 Oct re-run, numbers identical to the 24 Nov review); `tests/test_card_replay_differs.py` (five).

**Files:** `tools/card_replay.py` (`pair_days`, `daysDiffer` / `legsDiffer`), `tools/card_review_post.py` (`differs`, the column and the watch line), the test, the note, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the decision gate, any Card rule (`CARD_RULE` 14 until the 30 Nov read), the record, the replay's numbers.

**Roll back:** `git revert` the merge.

## 2026-11-24-fidelity-why: the Card review says why the page and the replay differ (tag pending)

**What changed:** nothing on the site. Under the nightly Card review's Fidelity line, each Card group the page published that the replay's live row did not rebuild is now read pick by pick at the first and the last pre-start price (refused at that price, every pick clear, or not in the pool), with when the page first published it; the replay's groups the page did not publish are read at the last price. On 19 to 23 Nov: one of the page's two unrebuilt groups is the price (21 Nov's Ascoli / Lazio / 76ers passed only on the morning's prices), the other is the page's hold (Galatasaray / Mlada Boleslav / Rapid Wien, published the evening before, every pick clear at both prices; the replay grouped the same legs with Alianza Lima instead); 23 Nov's empty page is Hammarby's price shortening out of value.

**Evidence:** `claude/card-replay-fidelity-why-2026-11-24.md`; `tests/test_review_fidelity_why.py` (five).

**Files:** `tools/card_replay.py` (`leg_faults`, `live_rule_from`, `legFaults` on the live variant), `tools/card_review_post.py` (`fidelity_why`, `_why_group`, `_first_published`; the Fidelity line names the hold), the test, the note, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any Card rule (`CARD_RULE` 14 until the 30 Nov read), the record, the replay's numbers.

**Roll back:** `git revert` the merge.

## 2026-11-24-wta-shrink: WTA confidence shrink 0.95 to 1.0 (tag pending)

**What changed:** WTA win chances are no longer pulled toward 50% (`CONFIDENCE_SHRINK["wta"]` 0.95 to 1.0). Quoted WTA confidence rises about 0.8 points on average. ATP unchanged.

**Evidence:** live WTA 28 days 244 of 349 v 229.9 quoted (z +1.6), used only to locate the gap. On history, paired bootstrap v 0.95: fit 2025 (n 2,674) -0.0010 log loss, p(worse) 0.010; check 2026 (n 1,286) -0.0018, p(worse) 0.001; every 2026 band 55%+ lands above quote. Rule 3 gates pass; the tennis-only `MIN_GAIN` 0.005 is not reached (as for the original 0.95). Surface source: still none (fifth check).

**Files:** `build_tennis.py`, `claude/tennis-wta-shrink-2026-11-24.md`, `RELEASES.md`.

**Not changed:** ATP shrink, surface handling, list and Card floors.

**Roll back:** `git revert`, or set `CONFIDENCE_SHRINK["wta"]` back to 0.95.

## 2026-11-24-band-50-55-recheck: Football 50-55% band over its quote, re-read (tag pending)

**What changed:** Nothing in the model or page. A dated note only.

**Evidence:** live 50-55% calls 494 of 875 v 460.2 quoted (z +2.3). Before 17 Nov 432 of 761 v 400.2 (z +2.3); from 17 Nov 62 of 114 v 60.1 (z +0.4), so the gap is October's and is not growing. The 17 Nov bend test (fit 2025-26, check 2026-27, gain -0.0003, p(worse) 0.94) already rejected a band-specific fix; the weekly gated refit moved the line on 23 Nov (a 1.085, b -0.20, gain -0.0009, p(worse) 0.00).

**Files:** `claude/band-50-55-recheck-2026-11-24.md`.

**Not changed:** `calibration.json`, the engine, the page.

**Roll back:** delete the note.

## 2026-11-24-list-70up: the Daily List's default band is 70%+, not 60%+ (tag pending)

**What changed:** Douglas, the same evening: "Actually let's roll that back. Only show 70% and above." The 60%+ choice is now **70%+**, and it is the Daily List's default. List picks are all 75%+, so the visible change is the reserve fold: it opens on reserve picks at 70% or better (60%+ this afternoon, 75%+ before today). A reader with 60%+ saved goes back to the page default. Every other tab still opens on All; All still shows the reserve's 75%+ view.
**Evidence:** display only. Browser check at 1280px and 400px on a local build: 70%+ pressed by default and for a reader with 60%+ saved, no chip, the reserve note reads "every reserve pick at 70% or better". Full test suite passes.
**Files:** `index.html` (`BANDS`, `FVIEWS.list.bandDefault`, the list's `filtered` test, the reserve note), `analysis.html` (`BANDS` copy and its band lookup), `RELEASES.md`.
**Roll back:** `git revert` the merge (back to 60%+), or revert both 24 Nov merges for the old All default.

## 2026-11-24-list-60up: the Daily List opens on every pick at 60%+ (tag pending)

**What changed:** Douglas, 24 Nov 2026: "make the default filter show all banding from 60% upwards as the default". The Confidence filter has a new **60%+** choice, and it is the Daily List's default. The list itself is unchanged (every list pick is 75%+), but the reserve fold now opens on every reserve pick at 60% or better, where until now the default ("All") showed only the reserve's 75%+ picks. Groups A and B stay labelled under 60%+. Every other tab still opens on All. A reader's own choice still holds across tabs; Clear filters (and removing the chip) now go back to each page's default rather than All. Readers who had "All" stored (everyone, as it was the default) are moved once to the default, so the change reaches them; a band chosen before is kept.
**Evidence:** display only, nothing regraded. Checked in a browser at 1280px and 400px on a local build: 60%+ pressed on first visit and for a reader with "All" stored, All then reload holds All (`#list?band=all`), 85-89% shows its chip, Clear returns to 60%+, the football board stays on All. Full test suite passes.
**Files:** `index.html` (`BANDS`, `FVIEWS.list.bandDefault`, `bandOf`, `fClean`/`fBandAuto` with the `almanacFiltersV` flag, the filter bar, `fClear`, `resShown`, the reserve note, `navHash`), `analysis.html` (`BANDS` copy, kept equal by `tests/test_shell_sync.py`; its band lookup skips 60%+), `RELEASES.md`.
**Not changed:** the list rule, the reserve rule (the 75% line is still where the reserve's default display used to stop, and choosing All restores that view), any record.
**Roll back:** `git revert` the merge.

## 2026-11-24-coverage-by-rule: the Card review's Coverage line reads each rule on its own days (tag pending)

**What changed:** nothing on the site. The nightly Card review's Coverage line set every live Card group since 29 Oct (rules 1 to 14, 33 on 24 Nov) against the replay's live row (rule 14 alone, 10) and blamed the gap on estimate-only legs. It now counts the record's groups by the rule each ran under and sets them beside that rule's own replay on its own live days: 33 v 13, with 21 of the 33 before 10 Nov (the estimate-only archive, 1 rebuilt) and 12 v 12 from then on.
**Evidence:** `claude/card-review-coverage-by-rule-2026-11-24.md`; `tests/test_rule_coverage.py` (five).
**Files:** `tools/card_replay.py` (`groupDays` on every variant and `rules` row), `tools/card_review_post.py` (`rule_coverage`, `POOL_REAL_FROM`), the test, the note, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any Card rule (`CARD_RULE` 14 until the 30 Nov read), the record, the replay's numbers.
**Roll back:** `git revert` the merge.

## 2026-11-24-replay-last-price: the Card review reads the replay at the last pre-start price too (tag pending)

**What changed:** nothing on the site. The nightly Card review now runs the pool replay twice, at each leg's first real price (as before) and at its last pre-start price, and the 30 Nov decision row (rule 14 v `rule13` and `rule12`) shows both. A new Fidelity line sets the replay's live row beside the Card the page actually published on the live rule's days.
**Evidence:** the first price is often three days before the start, and rule 14's value demand reads the price: Hammarby (23 Nov) passed at 1.22 and failed at 1.16, so the replay built a group the page refused. `rule13` v live is +0.23 a day (p(worse) 0.32) at first prices and -0.31 (p(worse) 0.69) at last prices. On rule 14's days the last-price replay agreed with the page on every day's having a group; the first-price replay did not (23 Nov). `claude/card-replay-price-fidelity-2026-11-24.md`; `tests/test_review_fidelity.py` (three tests).
**Files:** `.github/workflows/card-review.yml` (a `--closing` replay step), `tools/card_review_post.py` (`fidelity_lines`, `decisions_section(rep_close=)`), `tools/card_replay.py` (`picks` in `groupList`), the test, the note, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any Card rule (`CARD_RULE` 14 until the 30 Nov read), the record, the first-price replay table.
**Roll back:** `git revert` the merge.

## 2026-11-24-mailer-window: the morning email covers 07:00 to 07:00 (tag pending)

**What changed for a reader.** Douglas: "Some of the games on the mailer already played ... can it be a 07.00-07.00 24 hour period for the mailer picks?". The 07:00 email took the whole UK day's list, so overnight US games (00:30, 03:00) were already played when it arrived, with their results shown. It now carries the list picks starting from 07:00 UK that day to 07:00 UK the next: today's from 07:00 on, plus the next night's overnight picks (US basketball and the like). Edge picks follow the same window. Untimed picks stay with their own day. The Daily 2x and the Card already run 07:00 to 07:00.
**Evidence.** `tests/test_mailer.py` `SevenToSeven` (the window, the overnight picks, summer time). On today's files the overnight picks come from `daylist.json`'s new `early` list (23 next-night list picks before 07:00).
**Files.** `mailer.py` (`window`, `in_window`, `list_items`, `edge_picks`), `daylist.py` (`early`), `tests/test_mailer.py`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** The page's Daily List, the Weekly Record, any record.
**Roll back.** `git revert` the merge.

## 2026-11-24-staking-rule14-rate: the Card's bankroll read at the live rule's rate (tag pending)

**What changed:** nothing on the site. The nightly Card review's live bankroll (month and season, at the page's stakes) now counts groups at the live rule's own rate once it has a week on the record, not at the rate since 11 Nov: rule 14 has built 3 groups in 5 days (0.60 a day) against 0.85 a day over rules 11, 13 and 14 together.
**Evidence:** `groupings-record.json` to 23 Nov; `claude/card-staking-rule14-rate-2026-11-24.md`. Three tests in `tests/test_staking.py`, one failing on the old code.
**Files:** `tools/staking.py` (`live_rule_from`, `record_rate_from`), `tests/test_staking.py`, the note, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any Card rule, `CARD_STAKE`, the record, the replay rows.
**Roll back:** `git revert` the merge.

## 2026-11-24-leg-property-fifth: Leg properties, fifth look (tag pending)

**What changed:** nothing on the site. A note recording the fifth look at which legs land at their quote.

**Evidence:** pool 30 Oct to 24 Nov, football, real price, 65%+, no draws: 98 settled, 76 landed v 66.5 expected. Tested rate at or above model 45/64 (42.4 expected); below model 31/34 (24.1). Far under the 250 legs Rule 3 needs; no fit/check split possible.

**Files:** `claude/leg-property-fifth-2026-11-24.md`, `claude/odds-groupings.md`, `RELEASES.md`.

**Not changed:** every leg rule, `groupings.py`, the Card.

**Roll back:** `git revert` the merge.

## 2026-11-24-edge-retest-5: Edge over the price, fifth run: still none (tag pending)

**What changed:** nothing on the site. A dated note records the fifth run of the model-v-bookmaker edge test.
**Evidence:** football-data.co.uk average prices, fit 2025-26 (12,510 legs), check 2026-27 (3,861), bootstrap of landed minus fair chance. Legs 4+ points above fair: -2.1 fit (n 2,555), -1.6 check (n 1,013); 2+ and 6+ the same sign; no cell with 250+ legs positive on both seasons; the below-market control +2.3 on both.
**Files:** `claude/odds-edge-retest-2026-11-24.md`, `claude/odds-groupings.md`, `RELEASES.md`.
**Not changed:** `MAX_ABOVE_BOOK`, the Card, any model or group rule.
**Roll back:** `git revert` the merge commit.

## 2026-11-24-tennis-surface-5: tennis surface, fifth check, nothing to ship (tag pending)

**What changed:** a note only. No source gives ESPN tennis results a surface; the name map was rejected on 13 Oct.
**Evidence:** Sackmann 2026 files 404, tennis-data.co.uk 2026 files 403 (24 Nov); map test WTA +0.0024 (p 0.88, n 2,686), ATP +0.0031 (p 0.95, n 1,523) worse.
**Files:** `claude/tennis-surface-fifth-check-2026-11-24.md`.
**Not changed:** `build_tennis.py`, ratings, the Daily List rule.
**Roll back:** delete the note and this entry.

## 2026-11-24-slip-links: research links on the slip's legs (tag pending)

**What changed for a reader.** Douglas: "add those for the slip as well". Each leg of the slip on the Bets tab now ends with the same one-line links as the Edge picks: H2H, Predictions, Search and Table (Draw for a tennis leg). The bookmaker's name under a slip leg's price is no longer cut off ("William Hi").
**Evidence.** Display only. Checked in a browser at 400 and 1280 wide.
**Files.** `index.html` (`researchLinks`, shared with `edgeLinks`; `.tb-row.st.slip`), `RELEASES.md`.
**Roll back.** `git revert` the merge.

## 2026-11-24-edge-links-short: Edge links on one line, Most nailed on banner removed (tag pending)

**What changed for a reader.** Douglas: "all in one row next to each other ... H2H, Predictions, Search" and "Get rid of the nailed on banner". The Edge picks' links now read H2H, Predictions, Search, Table (the full name on hover and for screen readers) and sit on one line across the row, under the Edge chip on a phone so they fit. The Most nailed on line under each Daily List day's heading is gone; the ⭐ likely-winner marks on rows stay, and the emails are unchanged.
**Evidence.** Display only. Checked in a browser at 400 and 1280 wide.
**Files.** `index.html` (`edgeLinks`, `.tb-links`, the list day head), `RELEASES.md`.
**Roll back.** `git revert` the merge.

## 2026-11-24-edge-links: research links on every Edge pick (tag pending)

**What changed for a reader.** Douglas: "add the standard google search links to every row here". Each Edge pick on the Bets tab now carries the football board's four searches: Head to head, Predictions, Search this fixture and the league table, in the section's small muted type (12px, underlined in the rule colour, the home blue on hover). One line with dots between on desktop; one link a line on a phone, so each is easy to tap.
**Evidence.** Display only. Checked in a browser at 400 and 1280 wide.
**Files.** `index.html` (`edgeLinks`, `.tb-links`), `RELEASES.md`.
**Roll back.** `git revert` the merge.

## 2026-11-24-list-card-day: the List card built on its own day, one kind a day (tag pending)

**What changed for a reader.** The List 2x and List long on the Bets tab were fixed as first built, up to three days early, and a List 2x could be published beside a List long that was already held: 21 and 22 Nov each had both, sharing two and three picks, and those four slips are the List card's whole record. Now an unstarted List slip is rebuilt on every build until 07:00 UK on its day (as the Daily 2x has been since 23 Nov), then held, and a day has one List kind: the 2x, else the long.
**Evidence.** The archive for 21 and 22 Nov (`claude/list-card-on-its-day-2026-11-24.md`). `tests/test_list_card.py` `ListOnItsDay`, four tests that fail on the old code.
**Files.** `groupings.py` (`build_list_card`), `tests/test_list_card.py`, `claude/list-card-on-its-day-2026-11-24.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** `LIST_KINDS`, floors, the Card, the Daily 2x, any record or archive.
**Roll back.** `git revert` the merge.

## 2026-11-24-band60: the 60-69% filter back on the Daily List (tag pending)

**For a reader:** the Daily List's Confidence filter offers 60-69% (and 70-79% counts every reserve pick) again. The reserve fold still opens on 75%+ by default; choose a band and every reserve pick in it shows, so the football reserve at 60-69% (67 picks on 24 Nov's local build) is one tap away. The fold's note says how to reach them.

**Why:** Douglas, 24 Nov 2026: "Can we get the 60-70 filter back in - I think we're going to miss too many football games otherwise". The 23 Nov fold cut (`RESERVE_SHOW_MIN` 0.75) also took the under-75% reserve out of the filter's counts, and a band with no rows is not offered.

**Files:** `index.html` (`resAny`, `resShown` reads `FILT.band`, the list bar's `confs`, the fold's note).

**Not changed:** the default view, the reserve flag, grading, every other tab.

**Roll back:** `git revert` this commit.

## 2026-11-24-list-results-every-sport: Recent list results show every sport (tag pending)

**What changed for a reader.** Douglas: "Why is this just football games shown?". The Daily List's Recent list results read football's record alone, a leftover from before the list covered every sport. It now shows the last 30 graded list picks from every sport (football, tennis, NBA, NFL, college basketball, rugby), newest first, each with its sport's emoji. The score is now written from the pick's side: an away pick read "Tre Penne to beat Pennarossa 3–6" with a tick, which looked like a loss; it now reads 6–3. Tennis shows the sets the same way. Void games are left out.
**Evidence.** On the committed records at 24 Nov the 30 rows are 15 college basketball, 5 football, 4 NFL, 3 tennis and 3 NBA. `tests/test_record_summary.py` (order, sports, pick-side scores, voids and off-list picks left out). Checked in a browser at 400 and 1280 wide.
**Files.** `build.py` (`list_recent_all`, `listRecentAll` in the inlined summary), `index.html` (the panel), `tests/test_record_summary.py`, `RELEASES.md`.
**Not changed.** Any record, grade or the list itself.
**Roll back.** `git revert` the merge.

## 2026-11-23-mailer-design: the emails in the site's own look, a welcome series drafted, click tracking (tag pending)

**What changed:** the emails open with the site's own cover (star banner, SPORTS / ALMANAC, 2026 band; `email-header.png`, published by deploy.yml, colours corrected to the site's CSS) above the yellow strip, and the sections and footer sit flush with no gaps. The bands follow the site's own styles: red section heads as the day heads (Anton 17px, ink offset, mono yellow count), the yellow strip as the sports strip (Barlow Semi Condensed 13px bold), group labels as the list's `.lgrp`; the site's fonts load where mail apps allow (Apple Mail, iOS) and fall back elsewhere. In the email, Group A / Group B / the rest read **Strongest today · 85% or better** (same rule: up to five, never padded) and **Also on the list**; the page keeps its labels. "The model" reads "the Sports Almanac model". The ⭐ is smaller and sits on the line. Each send carries a `kind` tag (daily, weekly, confirm, welcome, guide). `welcome_emails()` drafts three welcome emails (confirm, welcome, how to read); `--preview` writes them, `--to --kind welcome|all` sends test copies; only the confirm email is sent in production, from Supabase.

**Outside the repo (Douglas, 23 Nov 2026):** Resend click tracking through `links.sportsalmanac.bet` (open tracking off: inflated by Apple Mail and a tracking pixel needs consent); a Resend webhook (delivered, clicked, bounced, complained) to the Supabase edge function `almanac-email-events`, which checks Resend's signature (`RESEND_WEBHOOK_SECRET`) and logs through `almanac_log_email_event` into `almanac.email_events` (no addresses; link tokens stripped), summed by day and kind in `almanac.email_kpis`. `almanac.send_confirm` sends the confirm email in this design.

**Tested:** `tests/test_mailer.py` (group order and never-padded updated to the new labels), `nametest.py`; the previews rendered at 680px and 390px on the canvas Douglas approved; test copies of all five emails to Douglas; a delivered and a clicked event landed in `almanac.email_events`.

**Files:** `mailer.py`, `tests/test_mailer.py`, `email-header.png`, `.github/workflows/deploy.yml` (publishes the header), `.github/workflows/mail-test.yml` (previews on every push to `mail-test`; sends test copies to Douglas on `[send]` / `[send-one]`), `claude/mailer-2026-11-23.md`.

**Not changed:** what each email holds, the schedule, the claim, the page's Group A / B labels.

**Roll back:** `git revert` the squash commit; the header image then 404s in any email already sent, harmlessly.

## 2026-11-23-daily2x-day: the Daily 2x is built on its own day (tag pending)

**What changed:** the Daily 2x was built when its day first came into the builds' three-day horizon and then held, so every slip from 17 to 23 Nov was chosen one to three days early, mostly from reserve picks, at prices read then (23 Nov's showed "read Thu 19:30" on a Monday while the day's ten Daily List picks never reached it). Now an unstarted Daily 2x is rebuilt on every build until 07:00 UK on its day, then held as first built until its first start, as before. The 07:40 UTC build (the morning briefing and email) is the first to hold it.

**Why:** the rule the page states, the Daily List first, and the ledger replay that put the slip live were both the day's own list; the live slip was not that rule. On the archived pool, slips built as at 07:00 UK: 25, 12 won v 10.16 expected, +10.4%, list picks in 19 of them and reserve in 2. Over 17 to 22 Nov the on-the-day slips won 2 of 6, as the live ones did, so this is about the slip being the rule, not a claim of more return. `claude/daily-2x-on-its-day-2026-11-23.md`.

**Tested:** `tests/test_daily_2x.py` `test_rebuilt_until_its_day_then_held` (a reserve slip built two days early is replaced by the list slip the evening before, then held after 07:00 UK on the day even when a stronger pick arrives; fails on the old code); the unit suite and `nametest.py`.

**Files:** `groupings.py` (`build_list_card`: the hold condition), `tests/test_daily_2x.py`, `claude/daily-2x-on-its-day-2026-11-23.md`, `CLAUDE.md`.

**Not changed:** no CARD_* constant, no Daily 2x constant, tier or floor, nothing in the record (only locked slips are archived). The List 2x and List long are still held as first built.

**Roll back:** `git revert` the squash commit.

## 2026-11-23-mailer-send: the Daily List by email at 7 every morning, the Weekly Record on Saturdays (tag pending)

**What changed:** the Mailer's sign-ups now get email. **The Daily List** arrives at 07:00 UK every morning about the day: the Daily List as the page shows it (list picks only, never the reserve; Group A, Group B and the rest, strongest first; each with its UK time, sport, competition, the pick against the opponent, the model's chance, the tested rate, William Hill's price or the bookmakers' average labelled Avg, and the ⭐ likely winner; college basketball only at Hill 1.05+ and never a Leave out pick, with a line counting those left off), then the Daily 2x (each pick, the slip's price at Hill, a short-day mark), the Card (each group, its picks, Hill prices and stake, or the page's reason there is none), the Edge picks and, for those who ticked Scale, the day's Scale bets from the Daily List tier and the Scale groups, estimates marked "≈ estimate". An empty day says so in one line. **The Weekly Record** (the form's Sunday Record) arrives on Saturdays at 07:00 UK for the Saturday-to-Friday week just ended: the Daily List landed against quoted, by sport, the five strongest wins and every miss named; each card's week (the Card, the Daily 2x, the List card, the slip, Edge picks, Scale groups) in the ledger's headline pattern; and the list at William Hill's prices since 10 Nov. Every email carries the site's links, the honesty line, 18+ and BeGambleAware, and the reader's own Manage and Unsubscribe links with a one-click List-Unsubscribe header. **The Mailer tab:** the Daily List option reads "every morning at 7" and says what the email holds; "Sunday Record" is now "Weekly Record · Saturday mornings"; the confirmation link (`#mailer?confirm=`) confirms the address and says so, or says plainly that the link failed; the Manage link (`#mailer?manage=`) shows the three emails, a pause (a week or a month) and Unsubscribe from everything.

**Why:** Douglas, 23 Nov 2026: Resend as the sender from list@sportsalmanac.bet; the Daily List at 07:00 UK with the list, the Daily 2x, the Card, Edge picks and Scale for Scale subscribers; the Weekly Record on Saturdays at 07:00.

**Tested:** `tests/test_mailer.py` (20 tests, no network: the 07:00-11:59 window at 06:59, 07:00, 11:59 and 12:00, BST and GMT, Saturday's weekly, the week's dates; list picks shown and the reserve not; Group A, B and the rest in order and Group A never padded; college basketball's Hill floor; the empty-day line; Scale only for Scale subscribers and only its Daily List tier; one email a recipient with its own unsubscribe header and links; batches of 100; retries on 429 and 5xx with one idempotency key, none on a 4xx; a claim refused sends nothing; silent without either secret; no address in the log), with `tests.test_tag_pages`, `tests.test_release_tags`, `tests.test_shell_sync` and `nametest.py`. `python3 mailer.py --preview` on the local files (23 Nov daily, 21 Nov weekly) screenshotted at 600 and 375 wide, no sideways scroll. The Mailer tab at 1280 and 400 with Supabase stubbed: a good and a bad confirm link, a confirm link typed into an open page, manage (load, tick Scale, pause a week, save, unsubscribe); the token gone from the address before Tag Manager loads, never in the page or the dataLayer; the shared check over every tab at both widths, no errors.

**Files:** `mailer.py` (new), `tests/test_mailer.py` (new), `index.html` (a token-reading script at the top of `<head>`, before Tag Manager; the Mailer copy; `#mailerConfirm`, `#mailerManage` and their script, `window.mailerToken`; `navApply` hands a confirm or manage link over and never writes it back; `.m-mgr`, `.m-row`, `.m-quiet`, `.m-ok`), `.github/workflows/deploy.yml` (a step after daylist.py, `continue-on-error`, secrets `RESEND_API_KEY` and `MAILER_SECRET`), `CLAUDE.md`, `claude/mailer-2026-11-23.md`.

**Not changed:** no model, pick, rule, number or record; nothing regraded. The emails read the files the build already writes. The Daily List record still grades every list pick, the college basketball ones the page leaves off included, so the Weekly Record's list line counts them. The sign-up form, its RPC and the sign-up push are as they were.

**Roll back:** `git revert` the squash commit on main (it is one commit). That stops every send from the build. The database side, in the Inbox Innovation project, stays and is harmless without the build: migrations `almanac_mailer_send` and `almanac_confirm_on_rejoin` added `almanac.sends`, `subscribers.confirm_sent_at`, `almanac.mailer_ok`, `public.almanac_mail_list`, `public.almanac_mail_claim`, the confirmation trigger `almanac_send_confirm` (`almanac.send_confirm`, at most one email every 30 minutes an address, sent on a new sign-up, a re-sign-up or a rejoin from the manage page), `almanac.resend_pending_confirms()` and the sign-up push's "Weekly Record" wording; the Edge Function `almanac-unsubscribe` (one-click, a confirm page on GET). To stop confirmation emails too, delete the Vault entry `almanac_resend_key`; to remove the lot, `drop trigger almanac_send_confirm on almanac.subscribers` and drop the functions and table above.

## 2026-11-23-ux7-analysis-shell: Almanac Analysis in the same shell as the Almanac (tag pending)

**What changed:** release 7, the last of the UX programme. Almanac Analysis now wears the Almanac's own tokens, tab bar and segmented control: the same colours, spacing and type scale, the same two-row tab bar (now pinned on scroll, as on the Almanac), its own tab marked as the open one, every tab a link to that board. Day by day picks its games by the Almanac's confidence bands (All, 90%+, 85-89%, 80-84%, 70-79%, 60-69%, under 60%, each with its count) instead of cumulative 50%+ to 90%+ brackets and a from/to range; the band is the same choice as the Almanac's filter, so it opens on the band you last chose there and a band chosen here holds when you go back. The cumulative 60%+, 70%+ and 80%+ figures stay as a "Running figures" line under it. The day-by-day summary and each opened row of the banding table link to today's picks in that band on the Daily List and the football board (`./#list?band=85`). A new test fails CI when the two pages drift.

**Why:** Douglas, 23 Nov 2026: "Every page needs to be able to be navigated in the same way ... Filter and nav options consistent across pages."

**Tested:** the unit suite (with `tests/test_shell_sync.py`) and nametest pass; the new test shown failing on a scratch copy (a token at its old value, an extra tab, the `.seg` selected colour changed), each message naming what differs and where to fix it, then passing; the shared check on `index.html` and on `analysis.html` at 1280 and 400 (no overflow; Analysis's one error is the `file://` record fetch, as before); served over http, `r7-click.js` at both widths: the band labels in the Almanac's order, one pressed, each count equal to its day rows, the shared filter written and read both ways, a bad stored value, reload, the band links opening the Daily List at 85-89%, the open tab's look; screenshots of the cover (unchanged against the base), the tab bar, day by day and an opened band at both widths.

**Files:** `analysis.html` (`:root`, the tab bar CSS block and the `.seg` block copied from `index.html`; the nav as links with `aria-current="page"`; `BANDS`, `filtRead`, `filtBand`, `filtSave`, `bandSlots`, `bandOfFrom`, `bandHref`, `sumDays`, `renderDays`, `renderCum`, `setupBracket`), `index.html` (the tab bar's selected look also on `[aria-current="page"]`, an end-of-block marker, a line in the `BANDS` comment), `tests/test_shell_sync.py`, `CLAUDE.md`, `claude/ux-7-analysis-shell-2026-11-23.md`.

**Not changed:** no model, pick, rule, number or record; nothing regraded (the record bins on the raw chance, so a call at 89.6% is 85-89% here and 90% on an Almanac row; the page says so). The cover, GTM and GA4, the responsible-gambling banner, the banding table's 5-point rows, the calibration chart and the prose are as they were. No link to the repository or HQ.

**Roll back:** `git revert` the squash commit on main (it is one commit). No later UX release builds on this one.

## 2026-11-23-ux6-ledger: one tracker for every card, and a Cards board to compare them (tag pending)

**What changed:** release 6 of the UX programme. Every card's record is drawn the same way: a headline sentence in one pattern ("1 of 3 won v 1.2 expected · −17% at the page's stakes (−1.02 units on 6)", and what is still to settle), a running profit line against the line it was expected to make, ending on a marked dot with its value, a strip of days (won, lost, void, nothing that day, replayed; a tap opens the day) and one range control (All · Live · Last 14 days, Live only where a card has replayed or earlier-rule days). It is used for the Card (open under the card, its live rule by default; a day tapped opens that day in Results, day by day), the Daily 2x, the List card (new: List 2x and List long together, one line each), the slip and Edge picks (each in a closed fold at the foot of its section, the headline on the fold), Scale's groups (under Scale groups, all four kinds together, each kind's line as before) and racing tips (on Tips and Record). The old trackers are gone: the Daily 2x's tile grid, the slip's and Edge's stat tiles (their charts and strips live on in the ledger), Scale's graded-groups panel in its scoreboard, and racing's record strip, dot glance and profit chart. The Card's verdict, picks by sport and More numbers stay under Is it working?. **The Cards board:** How it went has a Cards board (`#results?board=cards`): one table, a row per card (live since, settled, won v expected, return at its stakes, the last 14 days, a profit sparkline), each row taking you to that card's tracker (`#today?card=daily` and the like); Back returns to the board.

**Why:** Douglas, 23 Nov 2026: "Tracking sports and cards to remain consistent", the review's "one tracker for every card".

**Tested:** the unit suite and nametest pass; the shared check opens every tab at 1280 and 400 wide with no page errors and no sideways overflow; `r6-heads.js` runs the old trackers (from the commit before) in the page beside the new ledgers and asserts every headline equal: the Daily 2x (2 of 6, 2.2 expected, −4%), the Card on rule 14 (1 of 3, 1.2, −1.02 on 6, −17%) and on every rule (15 of 47, −12.69 on 73), List 2x and List long, the slip (2 of 16, 5.5, −9.02, −56.4%), Edge (144 of 179, +23.12 best, +17.79 average), Scale's four kinds, racing on a stub; `r6-click.js` at both widths: every ledger's anatomy and fold state, each line ending at its headline, every range button's `aria-pressed`, strip taps opening the day (the Card's fold), the Cards board's seven links each opening its tracker in view and Back returning to the board, a typed `#today?card=edge`. The UX 3 to 5 click-throughs (`r3-click.js`, `r3-racing.js`, `r4-nav.js`, `r5-row.js`) still pass. Screenshots of Bets, Scale and the Cards board at both widths.

**Files:** `index.html` (CSS: `.led-*`, `.cb-*`, the `.dx`, `.sc-side`, `.rc-day` and `.et-s` rules removed; script: `ledger`, `LEDGER_CARDS`, `ledgerFold`, `ledHead`, `ledChart`, `ledStrip`, `ledGroupDays`, `ledFill`, `ledGo`, `cardsBoard`, `ledSpark` after `edgeSection`; `dailyTracker`, `slipTracker`, `edgeTracker`, `rcTracker`, `rcRecordStrip` and `rcProfitSvg` removed; `tbRecord` without its headline; `ogRecord` folds carry `data-date`; `resGrid`, `renderResults`, `navBoards`, `navHash`, `navApply` and the view switch read the Cards board and `?card=`), `CLAUDE.md`, `claude/ux-6-ledger-2026-11-23.md`.

**Not changed:** no model, pick, rule, number or record. Every headline is the record's own tally or the old tracker's own sum (`groupings-record.json`, `slip.json`, `record.json` edge, `scale.js`, `racing.js`); the lines, the strips and the Last 14 days headlines are the day rows behind those tallies, which sum to them. Racing's feed carries no per-day profit and no tip chance, so its line is per tip, for All only, with no expected line; Edge's expected is not carried day by day, so its Last 14 days headline has none. The Card's day folds, its sport table and More numbers are as they were.

**Roll back:** `git revert` the squash commit on main (it is one commit). Release 7 (Analysis) does not build on this one.

## 2026-11-23-ux5-row: one row for a pick, with its star, wherever it appears (tag pending)

**What changed:** release 5 of the UX programme. A pick is the same row, with the same star, on every page. **Stars everywhere:** started rows (the Daily List's started picks, Yday and Today's started games on Football, Tennis and the sport tabs), every leg of a Bets group (the Daily 2x, the Card, the List card, the Model card, their substitutes and the Card's "more picks"), the slip's legs, the Edge picks and Scale's rows now carry the board row's star. It is the same bookmark as the pick's own board row: star a Daily 2x leg on Bets and it is lit on the Daily List, on its sport tab and on Starred; unstar it on Starred and it goes out everywhere. A row whose pick Starred could not draw (a list day older than yesterday, a Scale day long past) has no star rather than a star that leads nowhere. **Bets legs drawn once:** each leg of a group was a summary line (time, pick, teams, sport, price source, opposition price, Google predictions, price, read time, chance) followed by the full board row of the same pick. Now it is the board row, with the leg's own facts in one line under it: the pick to back (when the row does not already mark it), the slip's price with its move, best price, read time and stale mark, the card's bookmaker (William Hill) on Card and paper groups, the price's source, the opposition and draw prices (when the row's Bookies line does not already show them), the leg's chance (when it differs from the row's number), the Google predictions link and, on the Card, the context check. The row's own price chip goes when the line under it gives the same price. A leg no board row can be drawn for keeps its summary line, which says everything. The Daily 2x was also drawn a second time in the closed "groups from the old rules" fold; it is not now. **One chip order:** every row, every sport, shows its chips as the price (Hill, Avg or Exch), the Bookies mark, the context check, then the sport's marks (Edge, Celtic's Law, Under 80, the college venue, tier and Behind .500 marks), then Reserve (before, the football row put Edge first and every row put the Bookies mark last). **Scale rows** take the board row's star, time and competition (mono time over the competition in small capitals, with the sport's emoji) and name type, beside Scale's own columns (winner, the bet and its chance, the price, the status).

**Why:** Douglas, 23 Nov 2026: "Tracking sports and cards consistent", the review's "every pick is the same row, wherever it appears".

**Tested:** the unit suite and nametest pass; the shared check opens every tab at 1280 and 400 wide with no page errors and no sideways overflow; `r5-row.js` (both widths): every drawn Bets leg shows its row and the facts line, never the summary, and each fact once (Google predictions, the price source, the opposition price, the average price), one star a leg; a Bets leg starred and seen lit on the Daily List, Basketball and Starred; a Scale row starred (15 of 15 rows carry a star); a started football row starred; all three drawn on Starred; the leg unstarred from Starred and gone there and on Bets; the chip order checked on every football (96), tennis (13), NBA (53) and Daily List (95) row. `r5-slip.js`: the slip's legs on 24 Nov carry stars, no overflow. The UX 3 and 4 click-throughs (`r3-click.js`, `r4-nav.js`) still pass. Screenshots of Bets, Scale, the Daily List, Starred and the sport tabs at both widths.

**Files:** `index.html` (CSS: `.og-l.st`, `.og-lx`, `.tb-row.st`, the Scale row's grid and `.sc-t` / `.sc-v`; script: `starEach`, `starPool`, `starFor`, `starHtml`, `starSync`, the delegated star handler and `rowChips` after `starIdOf`; `renderStarred` reads `starEach`; `appendFixture` and `sportRow` stars carry `data-star` and call `starSync`, their chips through `rowChips`; `pinnedRow(g, i, date)` with a star and `rowChips`, its callers pass the day; `legStar`, `legFacts`, `ogLegOnce` beside `ogBench` and `ogFill`; `ogCard`, `ogBench`, `cardPicksHtml`, `slipSection`, `edgeSection` and `scRow` draw stars; `renderToday`'s old-rules fold leaves out the Daily 2x), `CLAUDE.md`, `claude/ux-5-row-2026-11-23.md`.

**Not changed:** no model, pick, rule, number or record; no chip changes meaning and none is added to a sport whose data cannot carry it. The star store is unchanged (`almanac-starred`, cleared each day as before). The caution mark stays on the competition name. The slip's and Edge's compact lines stay compact (a star added, no board row). Trackers and records are release 6.

**Roll back:** `git revert` the squash commit on main (it is one commit). Releases 6 (the ledger) and 7 (Analysis) may draw rows with `starHtml` or `rowChips`; revert them first if they do.

## 2026-11-23-ux4-address-bar: the page's place in the address, so Back steps back through the pages turned (tag pending)

**What changed:** release 4 of the UX programme. The address now says where you are in the book: the tab, the day and the filters, e.g. `#fixtures/2026-11-24?band=85&order=time`, `#list?sport=nba,tennis`, `#results/2026-11-20?board=football`, `#scale/2026-11-18`. A link opens the same page with the same day and filters, and a reload keeps the place. Turning a page (a tab, a day on the ribbon, a board in How it went) adds a Back step, so the browser's Back button steps back through the pages you turned instead of leaving the site; a filter tap (sport, confidence, show, order, football's board, Clear filters) updates the address in place and adds no step. Back and Forward keep your filters as they stand, since they are shared and hold as pages turn; a link or a typed address applies its filters, which become your stored choice, so the page and the stored choice never disagree. The plain front page with nothing filtered is still the bare address, and every address the site wrote before (`#today`, `#fixtures`, `#sport:nba`, `#mailer`, `#scale`, `#starred`, `#results`, `#racing`, `#tennis`) opens the same tab. Unknown keys and bad values are ignored. Back and Forward between tabs send the `tab_view` analytics event once per change, as a tap does.

**Why:** Douglas, 23 Nov 2026: "Every page needs to be able to be navigated in the same way. The whole site needs to feel like a familiar book one can navigate and filter through."

**Tested:** the unit suite and nametest pass; the shared check opens every tab at 1280 and 400 wide with no page errors and no sideways overflow; a click-through (`r4-nav.js`, 87 checks at both widths, `window.dataLayer` counted): every old address and some bad ones open the right tab with `tab_view` once; a filtered football day (and a reload of it), NBA on Yday, the list filtered to NBA (and unknown sports dropped), Bets on Tmrw, How it went on Football and on a past Football day, Scale on a past day; three tabs and two days then Back six times, each step's tab and day asserted, `tab_view` once per tab change and none on a day change, Forward; a band tap and Clear filters adding no history entry; a typed `#tennis?band=90`; a How it went board pushed and popped. `r4-extra.js`: Starred's sport set in the address and after a reload, football's Both to score from a link and back, a plain `href="#results"` link.

**Files:** `index.html` (script: `navHash`, `navParse`, `navWrite`, `navFilters`, `navApply`, the `popstate` / `hashchange` listeners, `resBoardClick` for How it went's board picker; writes hooked into the view switch, `setDay`, the filter bar's delegated handler and `data-fclear`, football's board switch, the first draw of How it went after its records load; the landing hash read replaced by `navApply("load")`), `CLAUDE.md`, `claude/ux-4-address-bar-2026-11-23.md`.

**Not changed:** no model, pick, rule, number or record, and nothing on the page looks different. Football's competition choice, the racing board and Scale's ladder sport stay out of the address. No Copy link button: the address bar is the link.

**Roll back:** `git revert` the squash commit on main (it is one commit). Releases 5 to 7 of the UX programme (row, ledger, Analysis) may add keys to the address; revert those first if they do.

## 2026-11-23-ux3-day-ribbon: one day ribbon on every page with days, shared across tabs (tag pending)

**What changed:** release 3 of the UX programme, the review's "turning pages". Every page with days now has one day navigator, the day ribbon, directly above the filter bar: earlier days on the left in muted ink, the selected day in black and yellow, later days to the right, each with its count (a day behind shows landed of settled, "Yday 23/25"), prev and next arrows at the ends; on a phone it scrolls on one line with the selected day kept in view and a fade at the clipped edge. Labels read Yday, Today, Tmrw, then "Wed 25". The day is shared, like a page of a book: Tue picked on the Daily List opens Football, Tennis and every sport on Tue; a page without that day shows its own default and keeps the choice. The Daily List, Football, Tennis, the sport tabs and Starred start on **Week** (every day still to come, as before); a day narrows the page to it. The Daily List reaches back a week: a past day draws that day's list as rows with Won and Lost, and At a glance draws the ribbon's day (its own day tabs went; a swipe across it still turns the day). Football, Tennis and the sport tabs have **Yday** (yesterday's started games with their results) and **Today** (today's started games with their results inside the day, under a Started label), which replace the Played today and Played yesterday sections. Bets, Scale, Horse racing and How it went's four boards keep their single day, now chosen on the ribbon; Scale's glance rows open a day through it, and Scale's day list, bar and groups now sit above its glance. Gone: the glance's tabs, the list's Jump to strip and floating Days button, Bets' day buttons, Scale's day tabs, racing's day buttons and How it went's four Completed day pickers. Arrow keys, Home and End move the day.

**Why:** Douglas, 23 Nov 2026: "The whole site needs to feel like a familiar book one can navigate and filter through."

**Tested:** the unit suite and nametest pass; the shared check opens every tab at 1280 and 400 wide with no page errors and no sideways overflow; a click-through (`r3-click.js`, at both widths): Week by default, Sat 21 on the Daily List drawn as rows with Won and its glance, the day kept across Football and back, Tmrw carried from the list to Football, Tennis and the NBA, Football's Yday (results on 551 rows) and Today (a Started block), Tennis and NBA Yday, arrow keys, Home and the arrows with focus kept, Bets and Scale day switching, a Scale glance row opening Fri 20, How it went's list, football, tennis and NBA boards; racing on a stubbed feed (no racing data off disk). Screenshots of every affected tab at both widths looked at.

**Files:** `index.html` (CSS: the ribbon block under `.seg`, `.og-days .ribbon`, `.sc-sec.sc-day`; the `.gl-nav`, `.gl-tabs`, `.gl-arw`, `.list-days`, `#listDays` and `.to-days` rules removed; script: `DAY`, `setDay`, `dayRibbon`, `dayPick`, `dayLabel`, `dayTally`, `ribbonSync`; `todayGlance(sel)` one day, `glanceSync` the width check only, `listPastDay`, `pastAsPin`; `boardDays`, `playedOf`, `playedTally`, `playedRows`, `playedDaySec` in place of `playedSection` / `playedDay`; `render`, `renderTennis`, `renderSport`, `renderStarred`, `renderList`, `renderToday`, `renderScale`, `renderRacing`, `tennisResults`, `sportsResults`, `listReview` and `renderResults` read the ribbon), `CLAUDE.md`, `claude/ux-3-day-ribbon-2026-11-23.md`.

**Not changed:** no model, pick, rule, number or record. `OG_DAY`, `SC_DAY`, `RC_DAY` and `resState` stay and follow the ribbon for the code that reads them. The filter bar's sport and band chips still count the whole week (the count line follows the day). The day is in memory only; release 4 puts it in the address. A past Daily List day has no reserve, prices or scores (the archive keeps none for it), and At William Hill does not apply to it.

**Roll back:** `git revert` the squash commit on main (it is one commit). Releases 4 to 7 of the UX programme (address bar, row, ledger, Analysis) build on the ribbon; revert those first.

## 2026-11-23-ux2-filter-bar: one filter bar on every page, shared across tabs (tag pending)

**What changed:** release 2 of the UX programme. Every page that filters now has the same bar, in the same order: Sport (Daily List, Starred, Bets, Scale; tap more than one), Confidence (the same bands everywhere), Show (one vocabulary: Every pick, Daily List, Reserve, At William Hill, Edge, Still to start, plus football's Confident only) and Order by (Strongest or Kick-off time everywhere; football keeps Upsets and Goals, Starred Sport and List first), then the page's own controls (football's Board and Competition, Starred's Full details). Under it one line: the active filters as chips you can remove, the count ("12 of 95 picks") and Clear filters. Confidence, Show and Order chosen once hold as you move between tabs and after a reload; a choice a page cannot apply (Edge on tennis) shows that page's default there and comes back where it applies. A returning reader's old choices carry over once. New: Sport on Bets (a group shows whole when any of its picks is in the sports chosen; the Edge list filters its rows), Sport, Confidence and Order on Scale's day list, Daily List and Reserve on Football, Tennis and every sport tab, and Confidence on How it went's Daily List day rows. On a phone the bar folds into one "Filters · n" button beside the chips and Clear, so the Daily List's first pick is no longer five rows of chips down. Football's bar is no longer sticky (it had slid half under the two-row tab bar). Empty results say so with a Clear filters link.

**Why:** Douglas, 23 Nov 2026: "Filter and nav options consistent across pages", with filters shared across tabs.

**Tested:** the unit suite and nametest pass; the shared check opens every tab at 1280 and 400 wide with no page errors and no sideways overflow; a click-through (`r2-click.js`, all pass at both widths) sets 85-89% on the Daily List and sees it on Basketball and Tennis and after a reload, removes chips, clears, filters the list by sport, tennis by Daily List, football by Confident only, order, board and competition, falls back on tennis for a football-only Show while keeping it stored, filters Bets on 24 Nov to Basketball (the football 2x hidden with Clear, the slip with an NBA leg kept) and Scale's rows (15 to 5), opens and closes the phone fold (focus in, Escape out, focus back), migrates seeded old keys and survives corrupt and non-JSON stored values; a second script filters three starred rows by sport and tag. Screenshots of every affected tab at both widths looked at.

**Files:** `index.html` (CSS: the filter bar block, `.controls` static, the old `.band-ctl`, `.tab-order`, `.star-ctl`, `.list-sport`, `.list-order`, `.filt-note` rules removed; script: `filterBar`, `fbarGroup`, `FILT`, `fMigrate`, `FVIEWS`, `fShow`, `fOrder`, `fbEmpty`, `fClear`, `tabBar`, `betsOk`, `betsEmpty`; `render`, `renderList`, `renderStarred`, `renderTennis`, `renderSport`, `renderToday`, `dailySection`, `slipSection`, `edgeSection`, `cardPicksHtml`, `renderScale`, `listReview`; the `#controls` markup), `claude/ux-2-filter-bar-2026-11-23.md`, `CLAUDE.md` (a notes row and the filters sentence), `RELEASES.md`.

**Not changed:** no model, pick, rule, number or record; the ranking, Groups A and B (still unlabelled while the list is filtered by sport or band), the glance, the trackers and the scoreboards. Scale's ladder sport picker stays beside its table. Day pickers are release 3's; filters in the address are release 4's. The old localStorage keys are read once and left in place.

**Roll back:** `git revert` the squash commit on main (it is one commit). Releases 3 to 7 of the UX programme (day ribbon, address bar, row, ledger, Analysis) build on the bar; revert those first.

## 2026-11-23-markets-spread: the football markets' gate passes read for where they come from (tag pending)

**What changed:** under any football market rule that passes its gate, the nightly Card review now says where the pass comes from: each selection's picks and best-price return, how many match days and the share on the busiest three, how many William Hill priced, and that 20 rules are read at p(loss) 0.10 (about two would pass by luck alone). For over / under 2.5 it adds the same value rule on the football-data seasons (`goals-value.json`). The gate and its verdict are unchanged.

**Evidence:** `claude/markets-pass-spread-2026-11-23.md`. Over / under 2.5's pass (222 picks, +11.0%) is the under side alone (160 picks +15.9%, over 62 -1.7%), 82% of it on three days, and Hill prices none of it; on football-data the same value unders lost 7.3% (2025-26, 1,184 bets) and 14.8% (2026-27, 679). The pick's team to score (194 picks, +5.0%, p(loss) 0.088) is even by side but thin. Neither should be offered yet.

**Tested:** two new tests in `tests/test_markets.py` (the gate's spread fields with the verdict unchanged; the review's lines), both failing before the change; the full suite and nametest pass; the section rendered on the committed archive.

**Files:** `markets.py` (`gate`: `days`, `top3`, `bySel`, `hill`; `record`: `tests`), `tools/card_review_post.py` (`market_pass_lines`, `markets_section(rec, goals)`), `tests/test_markets.py`, `claude/markets-pass-spread-2026-11-23.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the gate's thresholds or verdict, the page, any model, any Card rule (CARD_RULE stays 14 until the 30 Nov read).

**Roll back:** `git revert` the merge commit.
## 2026-11-23-ux1-foundations: one segmented control, spacing and type tokens, one empty state (tag pending)

**What changed:** release 1 of the UX programme, nearly invisible on purpose. Every toggle group on the site now has one look, `.seg`: the football Board and Show switches, Order by, the confidence bands, the Daily List's sport filter and jump strip, Starred's controls, the glance's day tabs, the Bets and Scale day pickers, How it went's day pickers, the slip and Edge trackers' ranges and racing's board, day, meeting and race pickers. Separate buttons with a 4px gap, a 1px rule border, ink with yellow text when selected, a count slot in mono, wrapping cleanly on a phone (the glance's tabs scroll on one line, `.seg--scroll`; tracker ranges are the compact `.seg--sm`). The selected look keys off `aria-pressed` (`aria-selected` in the glance's tablist); the tracker ranges, which only set class `on`, now set `aria-pressed` too. Spacing tokens `--s1` to `--s6` (4 to 40px) and a six-step type scale `--t-xs` to `--t-xl` (11, 12.5, 14, 16, 20, 26px) in `:root`; about 200 font sizes moved onto the scale where the move is exact or at most half a pixel smaller (13 to 12.5, 11.5 to 11, 14.5 to 14, 16.5 to 16; the cover and tab bar untouched); `#100e0c` is `var(--cover-ink)` everywhere it was written out (42). One empty state, `.empty`: a boxed note in the surface colour with an optional title line (`.empty-t`, Scale's bold heading), replacing the 40px blank `.empty`, `.tb-empty` and `.sc-empty`; the "not in this build" states read "... in this build yet. It appears after the next build." (tennis no longer tells readers to run a script).

**Why:** Douglas, 23 Nov 2026: "Filter and nav options consistent across pages"; the later releases (filter bar, day ribbon, ledger) build on one control, one scale and one empty state.

**Tested:** the unit suite and nametest pass; the shared check opens every tab at 1280 and 400 wide with no page errors and no sideways overflow; screenshots of the Daily List, Bets, Scale, Football, the sport tabs, How it went and Racing compared with main's at both widths (same layout, the control groups now gapped, text in the ledes half a pixel smaller); a click-through checks the glance tab, the list sport filter, both tracker ranges (aria-pressed and class `on` set, ink background), the Bets and Scale day pickers and How it went's day picker, and that every selected button on the page has the same background.

**Files:** `index.html` (CSS: the `.seg` block under controls, `.empty` above the footer, tokens in `:root`, the phone tap-target rules; markup: `bandCtl`, Starred's `seg`, the list sport filter and jump strip, `todayGlance`, the How it went day pickers, `slipTracker`, `edgeTracker`, the Bets day picker, Scale's days, racing's pickers, the empty states), `claude/ux-1-foundations-2026-11-23.md`, `CLAUDE.md` (a notes row), `RELEASES.md`.

**Not changed:** no model, pick, rule, number or record; no script reads a class that was removed (`.dayseg`, `.boards`, `.et-seg`, `.sc-days`, `.gl-tabs` stay in the markup beside `.seg`, with no look of their own); the cover, the tab bar and the football competition chips. Inline `style=` attributes and the remaining off-scale sizes (12, 10.5, 13.5, ...) are left for later releases.

**Roll back:** `git revert` the squash commit on main (it is one commit). Releases 2 to 7 of the UX programme (filter bar, day ribbon, address bar, row, ledger, Analysis) build on `.seg`, the tokens and `.empty`; revert those first.

## 2026-11-23-leave-out-off-list: Leave out college picks off the Daily List (tag pending)

**What changed:** a college basketball pick tiered Leave out (away, or favoured by under 6 points on the line) no longer shows on the Daily List or in its reserve fold. It stays on the college basketball tab with its red chip; the day's "left off" line and the reserve note count it. Douglas: "remove leave out from daily list".

**Evidence:** `claude/college-tiers-2026-11-23.md`: Leave out picks at 70%+ landed 52% v 78% quoted since 1 Nov, and the William Hill 1.05 rule had been letting them through (6 of 8 Leave out list picks were priced 1.05+ at Hill).

**Tested:** the full suite and nametest; a fast offline build in Chromium at 1280 and 400 wide: no Leave out chip on the Daily List or reserve, the notes count them, no page errors (an initialisation-order error found on the way, the tier constants read by the masthead count before they were declared, fixed by declaring them with `var`).

**Files:** `index.html` (`listShown`, `listCollect`, `itemTier`, `resShown`, the reserve note), `claude/college-tiers-2026-11-23.md`, `RELEASES.md`.

**Not changed:** the pick's list flag, its grading or any record; the Card, the Daily 2x and the List card already leave college sports out.

## 2026-11-23-review-close: the nightly Card review closes the nights before it (tag pending)

**What changed:** once the night's Card review issue is posted, `tools/card_review_post.py` closes every older open `card-review` issue (`close_older`), so the newest review is the one open review. Fifteen had piled up (#169 to #492), one a night since 9 Nov, none ever closed. Closed issues stay readable, and the same-day refresh still finds the day's issue (it reads open and closed).

**Tested:** `tests/test_card_review_post.py` `CloseOlder` (older reviews closed, tonight's and integrity issues left alone, nothing closed when the post failed), the full suite, nametest. The next 03:40 UTC review is the live check: #169 to #492 should close.

**Files:** `tools/card_review_post.py`, `tests/test_card_review_post.py`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the review's content, the integrity issues, any Card rule or number.

**Roll back:** `git revert` the merge.

## 2026-11-23-tag-tips: tap any tag for its explanation; the black sport labels gone (tag pending)

**What changed:** every tag on a row (Banker, Caution, Bookies, Away, Behind .500, Under 80, the tested rate, the William Hill price, the context check, the ⭐, the caution mark) now opens a small card explaining it when tapped, so its explanation can be read on a phone, where the hover text never showed. The tap does not open or close the row; a tap elsewhere, a scroll, Escape or the × closes it. The black sport label on each row (TENNIS, COLLEGE BASKETBALL, NCAA, NBA) is gone: the competition name and the sport's emoji stay (Douglas: "the name and emoji is enough").

**Tested:** the full suite and nametest; a fast offline build in Chromium as an iPhone 13 and at 1280 wide: the card opens on a tap, the row stays closed, a tap outside closes it, no page errors, no sport labels left.

**Files:** `index.html` (`TAG_SEL`, `tagTipOpen`, `tagTipClose`, `#tagtip`; the `.comp` line in `sportRow` and the pinned row), `RELEASES.md`.

**Not changed:** the tags themselves, their rules or any number. Display only.

**Roll back:** `git revert` the merge.

## 2026-11-23-college-tiers: college basketball picks tiered Banker, Solid, Caution, Leave out (tag pending)

**What changed:** every college basketball pick at 70%+ carries one chip under its number: **Banker** (at home, favoured by 12+ points on ESPN's line), **Solid** (at home, no line posted), **Caution** (a neutral court, or favoured by 6 to 12) or **Leave out** (away, or favoured by under 6). It shows on the Daily List, the reserve, the college basketball tab and Starred, replaces the Away / Neutral mark on those rows, and the college basketball tab opens with a key giving each tier's record. A Caution or Leave out pick no longer gets the ⭐. The record tallies each tier on every build (`sports-record.json` `collegeTiers`).

**Evidence:** `claude/college-tiers-2026-11-23.md`: graded college basketball 1 to 23 Nov at 70%+: Banker 95% v 90% quoted (101), Solid 89% v 85% (439), Caution 67% v 81% (57), Leave out 52% v 78% (69).

**Tested:** `tests/test_sports.py` `CollegeTier` (fails on the old code), the full suite, nametest, a fast offline build rendered in Chromium at 1280 and 400 wide on the Daily List and the college basketball tab, no page errors.

**Files:** `sports.py` (`college_tier`, `by_college_tier`, `collegeTiers`), `index.html` (`collegeTier`, `collegeTierChip`, `tierKey`, `.ctier`, `likelyWinner`), `tests/test_sports.py`, `claude/college-tiers-2026-11-23.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the model, its numbers, the Daily List, any grading or Card rule. The line is display only; no bookmaker number reaches a model.

**Roll back:** `git revert` the merge.

## 2026-11-23-unpriced-near: "football Card unpriced" says how many are close to the start (tag pending)

**What changed:** the build log's "football Card unpriced:" line now says how many of the named legs are within 24 hours of their start, and each leg shows its hours out. `groupings.json` carries the count as `football.cardUnpricedNear`. The 20 Nov note's trigger for building a second football price source read the full count, which named core legs two and three days out on every build this week; each was priced by API-Football before its start, so the trigger was firing on legs no price gap had cost.

**Evidence:** `claude/card-unpriced-near-2026-11-23.md`: the week's lines against the pool archive (OL Lyonnes, Vancouver, Salisbury all priced one to two days before the start).

**Tested:** `tests/test_football_unpriced.py` (one new test, fails on the old code), the full suite, nametest, a fast offline build. The next CI build's log line is the live check.

**Files:** `groupings.py` (`CARD_UNPRICED_NEAR_H`, `card_unpriced_near`, `card_unpriced(now=)`), `tests/test_football_unpriced.py`, `claude/card-unpriced-near-2026-11-23.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any Card rule, price source, call order or credit spend. A report only.

**Roll back:** `git revert` the merge.

## 2026-11-23-af-normaliser: the price fallback reads the build's club normaliser (tag pending)

**What changed:** a football game API-Football spells another way, which the build's own club normaliser already joins (CA Mineiro and Atletico-MG, CA Paranaense and Athletico-PR), now takes its price in the one-fixture fallback. The 02:41 UTC build had CA Mineiro v SC Corinthians Paulista (Serie A, 25 Nov) under noFixture beside "Atletico-MG v Corinthians".

**Evidence:** `claude/af-normaliser-fallback-2026-11-23.md`: `sources._norm` reduces both to "mineiro"; on every November board name, no two different clubs in one league share a normalised form.

**Tested:** `tests/test_football_unpriced.py` (two new tests, both fail on the old code), the full suite, nametest. The next CI build's "football noFixture:" line is the live check.

**Files:** `groupings.py` (`af_same`), `tests/test_football_unpriced.py`, `claude/af-normaliser-fallback-2026-11-23.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any Card rule, model number or grading; equality only, never a fuzzy score, and a bare city never counts.

**Roll back:** `git revert` the merge.

## 2026-11-23-reserve75: the Daily List's reserve trimmed to 75%+, every row marked Reserve (tag pending)

**What changed:** the reserve fold under each Daily List day now shows only reserve picks at 75% or better, and each of those rows carries a dashed **Reserve** chip under its confidence, so a reserve pick never reads as a list pick. The fold's note says how many under 75% were left off and why. The Sport filter's counts skip the hidden picks. The list's intro paragraph says the same. Douglas, 23 Nov 2026: "I sometimes struggle with being drawn into the reserves", then option 2 of two offered (trim, rather than collapse behind a tap).

**Evidence:** `claude/daily-list-review-2026-11-14.md`: the reserve landed 952 of 1362 (70%) against the list's 414 of 471 (88%); reserve picks at 75%+ 244 of 288 (85%), the rest about 708 of 1074 (66%).

**Tested:** full unittest suite and nametest; a fast offline build checked in Chrome at 1280px and 400px (chips on every reserve row, no console errors).

**Files:** `index.html` (`RESERVE_SHOW_MIN`, `resShown`, the reserve fold in `renderList`, `.resvtag`), `RELEASES.md`.

**Not changed:** the reserve flag, its grading and record, How it went's reserve fold, Starred, Scale, the Daily 2x or any tab that reads the reserve. Display only.

**Roll back:** `git revert` the merge, or set `RESERVE_SHOW_MIN` to 0.
## 2026-11-23-startrack: the star's record tracked beside an 85% variant (tag pending)

**What changed:** nothing on the page. `tools/star_record.py` tallies the likely winner star on the graded record (replayed from 28 Sep, live from 23 Nov) beside the variant Douglas chose not to ship (football and tennis stars only at 85%+), and the nightly Card review prints it (`star_section`). Douglas, 23 Nov 2026: "No. But keep track".

**Evidence at the start:** stars 585 of 652 (90%); the variant 460 of 496 (93%); the stars it drops 125 of 156 (80%).

**Tested:** `tests/test_star_record.py`, the review tests, the full suite, nametest.

**Files:** `tools/star_record.py`, `tools/card_review_post.py`, `tests/test_star_record.py`, `claude/likely-winner-star-2026-11-23.md`, `RELEASES.md`.

**Roll back:** `git revert` the merge.

## 2026-11-23-winstar: ⭐ likely winners and the day's Most nailed on (tag pending)

**What changed:** a ⭐ now sits beside the picked side's name on every Daily List pick that also passes every check the record backs: football priced under 1.40 (where a price is known), no college pick away, neutral or behind .500, no tennis under 80%, no Bookies mark, no context check "against". It shows on every tab where the row appears. Each day on the Daily List opens with a **Most nailed on** line: the day's strongest starred pick, with its confidence and price; its row's star is a little larger. A key line in the list's intro explains the star. Douglas, 23 Nov 2026, after nine lost slips: "add a ⭐ ... next to all games that meet the likely winner conditions" and "the most nailed on team to win".

**Evidence:** `claude/bet-mistakes-proof-2026-11-23.md`: list 84% v reserve 67% (football); football 1.30-1.40 won 78%, 1.40-1.50 69% (18% drawn); college basketball away 46%, neutral 62%, home 87%; Bookies-marked picks 51% of 193. Nine of the weekend's ten losing legs were off the list, reserve or flagged.

**Tested:** full unittest suite (1,362), nametest, a fast offline build checked in Chrome at 1280px and 400px: 14 stars across the week, three Most nailed on lines, no console errors.

**Files:** `index.html` (`likelyWinner`, `winStar`, `pickPrice`, `computeNailed`, `nailedLine`, `.winstar` / `.nailed` CSS), `claude/likely-winner-star-2026-11-23.md`, `claude/bet-mistakes-proof-2026-11-23.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any model number, the list rule, the reserve, the record or grading. Starred picks are not yet graded apart.

**Roll back:** `git revert` the merge.

## 2026-11-23-lookback-postponed: postponed games dated in the last three days back on the board sooner (tag pending)

**What changed:** a game postponed from a date in the build's three-day look-back (Brazil's CA Mineiro v Corinthians and RB Bragantino v Vasco, 21 Nov) now returns to the board, the Daily List and the Card as soon as API-Football lists it once in the window. Before, it waited until its first date was more than three days old.
**Evidence:** the 23 Nov 00:10 UTC build's unplayed warning; `fill_untimed` matched a look-back row only to a listing within three days of its date and treated it as postponed only beyond the look-back. The "rescheduled ...: 0" lines for Scotland, Greece, Portugal and Czechia are expected (those games are not yet relisted in the window).
**Tested:** `tests/test_untimed.py` `LookBackPostponed` (five cases, two fail on the old code), the full suite, nametest, a fast build (no fetch here). The first CI build is the live check.
**Files:** `build.py` (`fill_untimed`), `tests/test_untimed.py`, `claude/lookback-postponed-2026-11-23.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any Card rule, model constant or grading; under `postponed_only` a look-back row listed close by keeps the league's own date.
**Roll back:** `git revert` the merge.

## 2026-11-22-isthmian: Isthmian League Premier v its quotes, second read: no test possible, no change (tag pending)

**What changed:** nothing in the model. Dated note `claude/isthmian-gap-2026-11-22.md`.

**Evidence:** planner's 59 of 101 (z -2.0) counts 10 draw reads against the win-or-draw expectation. Strictly 49 of 101 won (48.5%) against 51.9 expected, z -0.59. Away wins 36.6% v 27.9% quoted, draws 17.8% v 23.4%. No en.7i history and no API key here, so no paired replay (Rule 3's 250 check games unreachable); fitting on the live rows would break Rule 1.

**Files:** claude/isthmian-gap-2026-11-22.md, RELEASES.md.

**Not changed:** model, calibration, home advantage, grading.

**Roll back:** `git revert` the merge.

## 2026-11-22-split-rescheduled: postponed Scottish, Greek and Czech games back on the board (tag pending)

**What changed:** a postponed game in the Scottish Premiership, the Greek Super League or the Czech First League (Dundee United v Hearts, 31 Oct; Atromitos v AEK, 17 Oct) now returns to the board, the Daily List and the Card when API-Football lists it once in the build window, as #483 did for Portugal.
**Evidence:** openfootball's 2026-27 files hold each league's whole regular season and nothing after the split (sco.1 198 rows to 10 Apr, 66 repeated pairs; gr.1 182 to 20 Mar; cze.1 240 to 24 Apr), and after the ESPN fill one postponed row each is left in sco.1 and gr.1. A move never passes the file's last fixture, so the split's repeat games cannot be taken for the postponed one; pairs repeated inside the file stay refused. "Dundee Utd" reduced to Dundee, which would have refused Scotland whole: now an alias.
**Tested:** `tests/test_untimed.py` `RescheduleSplit` (five cases), the full suite, nametest. No API-Football key here: the first CI build logs "rescheduled sco.1 / gr.1 / cze.1" or names a miss.
**Files:** `sources.py` (`AF_RESCHEDULE`, `AF_SPLIT`, `ALIASES`), `build.py` (`fill_untimed(split=)`), `tests/test_untimed.py`, `claude/rescheduled-postponed-split-leagues-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any model constant, Card rule, or row inside the look-back.
**Roll back:** `git revert` the merge, or take the three codes out of `AF_RESCHEDULE`.

## 2026-11-22-pt-rescheduled: postponed Primeira Liga games back on the board (tag pending)

**What changed:** a postponed Primeira Liga game kept under its first date (Braga v Gil Vicente, 16 Aug; Estoril v Marítimo, 8 Nov) now returns to the board, the Daily List and the Card when API-Football lists it once in the build window, as #480 did for La Liga, the Süper Lig, Brazil and the three retime leagues. Portugal's own dates and times are otherwise left alone.
**Evidence:** the 22 Nov 16:05 UTC build's unplayed warning; Portugal plays each ordered pair once a season (18 clubs, no split), so one listing in the window is the replayed game. All 18 clubs match under API-Football's short forms (unprobed: the first CI build logs "rescheduled pt.1" or names a miss). Scotland, Greece and Czechia left out: their splits repeat pairs.
**Files:** `sources.py` (`AF_RESCHEDULE`), `build.py` (`fill_untimed(postponed_only=)`, the build loop), `tests/test_untimed.py`, `claude/rescheduled-postponed-portugal-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any model constant, Card rule, or row inside the look-back.
**Roll back:** `git revert` the merge, or empty `AF_RESCHEDULE`.

## 2026-11-22-list-bar: Daily List bar replayed again, no change (tag pending)

**What changed:** nothing a reader sees. The league bar (80%) and per-league bars were replayed once more.
**Evidence:** fit 2025/26, 6,451 win picks: 75% +0.0 points v the 80% list (-4.6 to +5.0), 77.5% +0.9 (-3.0 to +4.7), 85% -15.4 (-25.8 to -6.8). Check 2026/27: 77.5% +11.5 (+2.4 to +25.7) on 24 picks only, 70%/75% span zero; fails on the fit season. No league has 30 calls.
**Files:** `claude/daily-list.md`, `RELEASES.md`.
**Not changed:** `LIST_MIN`, any per-league bar.
**Roll back:** `git revert` the commit.

## 2026-11-22-calib: Calibration by band and sport, rerun (tag pending)

**What changed:** a dated note only; nothing on the site moves.
**Evidence:** `calibration_bands.py` on history (not `record.json`). Football check season 2,396 calls: 55%+ +6.6 [+3.2,+10.2], 62%+ +5.4 [+0.7,+10.2], but the fit season is on quote (+2.8, +1.1), so no refit passes Rule 3. Ice hockey check -6.1 [-8.8,-3.4] and college basketball -2.0 [-3.0,-1.0] are under quote while their fit windows are on quote; other sports inside noise.
**Files:** `claude/calibration-rerun-2026-11-22.md`, `RELEASES.md`.
**Not changed:** `calibration.json`, `sports.json`, code.
**Roll back:** `git revert` the merge.

## 2026-11-22-rescheduled-postponed: postponed games back on the board when they are replayed (tag pending)

**What changed for a reader.** A postponed game in La Liga, the Süper Lig, Brazil's Serie A, the Premier League, the Championship or Serie A now reaches the board, the Daily List and the Card on its new date. Before, openfootball kept it under its first date and it never came back.
**Evidence.** The 22 Nov 11:05 UTC build's unplayed warning named Rayo Vallecano v Athletic Club (10 Oct) and Chapecoense v Vasco (29 Jul). `build.fill_untimed` only read rows up to 3 days back. These leagues play each ordered pair once a season, so an older unplayed row whose pair API-Football lists exactly once in the window is the same game rescheduled.
**Tested.** Five cases in `tests/test_untimed.py` (moved; listed before the window, relisted by the source, listed twice, played: all left alone); nametest and the suite pass. No API-Football key in the sandbox: the first CI build is the live check.
**Files.** `build.py` (`fill_untimed`), `tests/test_untimed.py`, `claude/rescheduled-postponed-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Leagues outside `AF_UNTIMED` / `AF_RETIME`, any model constant, Card rule, record or grade.
**Roll back.** `git revert` the merge.

## 2026-11-22-slip-tracker: a performance tracker under the slip (tag pending)

**What changed for a reader.** The slip on the Bets tab now ends with a tracker like the Edge picks one: running profit at one unit a slip against the line its tested chances expected, slips won v expected, All / Live only / Last 14 days, and a strip of slip days to tap for each day's legs. Days before the slip went live are its rule walked forward over the results ledger, marked and dashed.
**Evidence.** Douglas: "is there a visual tracker for performance?" There was none. At 22 Nov: live 1 of 4 won v 1.5 expected (-0.34 units); with the replay, 2 of 15 v 5.2 expected (-8.02 units, expected +3.26). Too few to read; the gate is 100 slips.
**Tested.** `slip.py` tests, the full suite, nametest; the tracker in a browser at 1280 and 400 wide, every range and a tapped day, no page errors.
**Files.** `index.html` (`slipTracker`, `SKT`), `slip.py` (`RECENT_KEEP`, `REPLAY_KEEP`, `chance` on each live slip), `claude/slip-tracker-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** The slip's rule, its gate, any model constant or Card rule.
**Roll back.** `git revert` the merge.

## 2026-11-22-sunday-ghosts-multisport: Saturday games no longer shown on Sunday; pick several sports at once (tag pending)

**What changed for a reader.** Sunday's games no longer include La Liga and Süper Lig matches played on Friday or Saturday (Real Madrid v Celta, Sevilla v Betis, Galatasaray v Samsunspor and others), and Saturday no longer shows Sunday's Premier League games under their nominal date. The Daily List and Starred Sport filters take several sports at once: tap to add or remove a sport, Every sport to clear.
**Evidence.** Douglas: "Some games listed on Sunday were actually Saturday games". The archive held those games under the round's Sunday with no time before 19 Nov and on their real day after; `daylist.pinned` keyed football on the date, so the two copies were two games. Now a football copy gives way to a newer pre-start copy of the same pair within 3 days on another day. On the committed archives: 11 ghost rows off Sunday 22 Nov, 10 off Saturday 21 Nov, none added. Douglas: "I want to be able to select multiple sports on the filters at once".
**Tested.** `tests/test_daylist.py` `RoundDateGhost` (four cases), the full suite, nametest; the filters in a browser at 1280 and 400 wide with no page errors.
**Files.** `daylist.py` (`ROUND_DAYS`), `index.html` (`toggleSport`, `LIST_SPORTS`, `STAR.sports`), `tests/test_daylist.py`, `claude/round-date-ghosts-multisport-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Grading (score.py already grades the right copy), any model constant or Card rule. The results ledger still keeps the ghost copies as ungraded rows; a follow-up.
**Roll back.** `git revert` the merge.

## 2026-11-22-before-window-retime: Sunday's Premier League and Brazilian games back on the board (tag pending)

**What changed for a reader.** A round openfootball dates on its nominal Saturday whose games are played on the Sunday or Monday now stays on the board on the Sunday's build. `build.fill_untimed` (the `AF_RETIME` and `AF_UNTIMED` leagues) also reads unplayed rows up to 3 days before the window and moves one to API-Football's date and time when that date is in the window; a row API-Football still lists before the window (played or postponed) is left alone.
**Evidence.** The 22 Nov 07:05 UTC build warned of 52 unplayed fixtures dated before 22 Nov, among them en.1 Liverpool v Manchester United (22 Nov 16:30), Hull City v Brighton (22 Nov 14:00) and Brentford v Everton (23 Nov 20:00), and br.1 Paranaense v Remo and Botafogo v São Paulo. All five were on the 21 Nov archive with API-Football's real dates and none was on 22 Nov's: the rows are dated 21 Nov in openfootball, and `fill_untimed` only read rows dated from the start, so they were cut with the window before the retime could move them. Core-league games, so the Daily List and the Card lost them for the day.
**Tested.** Four new cases in `tests/test_untimed.py` (nominal Saturday moved into the window, an untimed league's row, a row API-Football still lists before the window left alone, older rows untouched); nametest and the suite pass. The sandbox cannot reach API-Football, so the first CI build is the live check: its "untimed en.1" and "untimed br.1" counts should rise and the three Premier League games leave the unplayed warning.
**Files.** `build.py`, `tests/test_untimed.py`, `claude/before-window-retime-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Any model constant, Card rule, record or grade.
**Roll back.** `git revert` the merge.

## 2026-11-22-round-date-results: a played match on its round's date is scored, not left on the board (tag pending)

**What changed.** A La Liga or Süper Lig match played on Friday or Saturday, which openfootball dates on the round's Sunday, is now scored from ESPN on the Sunday build instead of waiting for the round date to pass. `build.fill_lagging` fills a pair's unplayed row dated up to `AHEAD_DAYS` (3) days into the build window from a result played before it, and re-dates the row to the day it was played; rows before the window still come first.
**Evidence.** The 22 Nov 02:11 UTC build left Athletic Club v Espanyol (played 20 Nov, 0-1) on the 22 Nov board unplayed, asked a price for it (`noFixture`), and logged 5 La Liga and 4 Süper Lig results "with no fixture to fill". On the live openfootball files and the committed ESPN cache: es.1 50 to 55 filled, tr.1 63 to 67, unplaced 9 to 0; br.1, pt.1, en.1, it.1, de.1, fr.1 unchanged. `claude/round-date-in-window-results-2026-11-22.md`.
**Files.** `build.py`, `tests/test_lagging_results.py`, `claude/round-date-in-window-results-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Any model constant, Card rule, record or grade. `tune.load` uses the same rule, so its check season gains the handful of matches played before a round date that sits on or after the day it runs.
**Roll back.** `git revert` the merge.

## 2026-11-22-filters: sport and confidence filters, and a better Starred tab (tag pending)

**What changed for a reader.** Douglas: "the daily list needs filter by sport", "all sports and daily list need a filter by banding", and "the starred page needs improvement to filter and also see all fixture information and links and to be able to sort by time and other tags".
- **Daily List: Sport.** One sport or every sport, each chip with its count of list and reserve picks this week. While a filter is on, Groups A and B are not labelled (they are the day's strongest across every sport), days with nothing left are skipped, and a Clear filters link sits under the controls.
- **Confidence bands on every board**: the Daily List, Football, Tennis and each sport tab: All, 90%+, 85-89%, 80-84%, 70-79%, 60-69%, Under 60%, read on the number the row shows, with a count on each chip and empty bands not offered. Played today / yesterday follow the band too. Football's band shows every fixture in it (no top-50 cap while a band is on).
- **Starred: Order by** Strongest, Kick-off time, Sport, List first; **Sport**; **Show** (Everything, Daily List, Reserve, Board only, At William Hill, Edge, Still to start, each with a count); **Confidence**; and **Full details: Every row open**, which draws every starred row with its read, form and research links. The slip still runs on every starred pick.
- Each tab remembers its choices on this device.

**Checked.** In a browser at 1280 and 400 wide on the committed tennis and sports files and a fixture board built from the 21 Nov archive: chips and counts, filters on each tab, Starred ordering and every row open, no page errors.
**Files.** `index.html` (`BANDS`, `bandCtl`, `inBand`, `LIST_SPORT`, `STAR`, `STAR_TAGS`, `rowOpen`, `OPEN_ALL`), `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Any model, ranking, list membership, record or Card rule. Display only.
**Roll back.** `git revert` the merge.

## 2026-11-22-decisions-rule14: the Card review's decisions table reads rule 14 (tag pending)

**What changed.** The nightly Card review's pre-registered decisions table had kept rule 13's rows since rule 14 went live on 19 Nov. From `cardLiveRule` 14 it now has one row, rule 14 v `rule13` and `rule12`, read on 30 Nov with no change before (Douglas acts, the switch was his), says in bold when `rule13` is ahead on the pool, retires the tennis 75% and core-league rows rule 14 already settled (one line says so), and names Douglas on the opposition-floor rows under rule 14's no-change window.
**Evidence.** On 21 Nov's replay the new row reads `rule13` v live +0.52 units a day, p(worse) 0.219 on 102 pool legs, so the 30 Nov read has a live question; football-data had dropping the value demand behind in all five seasons, so nothing is due. `claude/card-decisions-rule14-2026-11-22.md`.
**Files.** `tools/card_review_post.py`, `tests/test_review_decisions.py`, `claude/card-decisions-rule14-2026-11-22.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Any Card rule, record, replay or page. Before rule 14 the table reads as it did.
**Roll back.** `git revert` the merge.

## 2026-11-21-ledger-moved: postponed fixtures re-listed later are not chased as ungraded (tag pending)

**What changed.** The results ledger's ungraded report (build log, `results-ledger.json.gz` `ungraded`) no longer chases a football fixture that was postponed and re-listed more than 10 days later. `ledger.predictions` marks the earlier copy `movedTo` (the later date) when the pairing has another copy within `RESCHEDULE_DAYS` (45) days, never on a row with a result, and `ungraded` counts it apart (`moved`, `movedByComp`; the log line adds "re-listed for a later date"). A mark only: nothing is graded from the later game.
**Evidence.** On the committed ledger: to chase 99 to 92, stale 418 to 227, moved 199 (2 list, 10 reserve); the later copy is graded for 134 of the 199 and to come for the other 65. The cases behind it: Tajikistan's 7 Nov round re-listed for 27 Nov, and Pistoiese v Coriano (Card leg, 15 Nov, void) listed for 9 Dec. The three list picks left on the chase line are not faults (Pistoiese's 9 Dec copy not archived yet; two college basketball games postponed, voided on 22 Nov by `sports.not_played`). Two tests. `claude/ledger-postponed-relisted-2026-11-21.md`.
**Files.** `ledger.py`, `tests/test_ledger.py`, `claude/ledger-postponed-relisted-2026-11-21.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Any Card rule, record, grade, price or page.
**Roll back.** `git revert` the merge.

## 2026-11-21-order-played: kick-off order everywhere, and started games open up (tag pending)

**What changed for a reader.** Douglas: "The ordering on football by time kick off is not working ... check all other pages" and "Why do some cards not clickable to reveal further info and links".
- **Played today / Played yesterday follow the order chosen.** They sat at the top of every tab in confidence order whatever the Order by said, so on a Saturday evening football's Time order looked broken. With Time chosen they now run in kick-off order (the most confident first when capped, then by time).
- **Tennis and every sport tab have an Order by** (Most confident / Kick-off time), remembered on this device. They had no control and were always strongest first. Tennis matches with no order of play (TBC) go last.
- **Every started game opens.** Started games are drawn from their pre-start copy (Played sections, started Daily List picks, Starred, Card and Bets legs), which had no detail. Tapping one now shows the research links (match report, head to head, predictions, the table or standings, the draw for tennis) and the read: the pick, its confidence and tier, the tested rate and the result.
- Checked: the football board and Daily List kick-off orders were already right; football, NBA and tennis orders and the new detail checked in a browser at 1280 and 400 wide.

**Files.** `index.html` (`TAB_ORDER`, `tabOrderCtl`, `playedByTime`, `playedSection`/`playedDay`, `renderSport`, `renderTennis`, `pinnedRow`, `pinnedDetail`, `PIN_OPEN`), `RELEASES.md`.
**Not changed.** Any model, record or card rule.
**Roll back.** `git revert` the merge.

## 2026-11-21-nwsl-kc-spelling: NWSL's Kansas City Current priced in the fallback (tag pending)

**What changed.** `groupings.AF_SPELLINGS` gains "Kansas City Current" -> "Kansas City W": the 16:05 UTC build named Washington Spirit v Kansas City Current (NWSL, 22 Nov) under noFixture beside API-Football's "Washington Spirit W v Kansas City W". `same()` already reads "Washington Spirit W" as Washington Spirit; "Kansas City W" is too short beside the full name.
**Evidence.** The build log's named noFixture line; a test that fails without the alias and passes with it. The leg is a 46% read, not Card-reachable (NWSL is a wider league and rule 14 is core only), so this is price coverage on the board, not Card volume. The day's other noFixture leg, CA Mineiro v Corinthians (Brazil, no kick-off), has no API-Football fixture sharing either name that day: a moved or postponed game, not a spelling, left alone. Also checked, nothing to change: the Saudi Pro League's ungraded reserve rows (15-16 Oct, 5-7 Nov, every 5-7 Nov kick-off a placeholder 20:00Z) are postponed rounds, Al Ahli v Al Nassr of 15 Oct played on 20 Nov; the sports record has no 0-0 or winner mismatch (#22's Saracens case is gone; three draws, two rugby, one NFL).
**Files.** `groupings.py`, `tests/test_football_unpriced.py`, `RELEASES.md`.
**Not changed.** Any Card rule, the model, the bulk match.
**Roll back.** `git revert` the merge.

## 2026-11-21-reserve-gap: Reserve (other sports) gap located, no rule change (tag pending)

**What changed:** nothing a reader sees. A note records where the reserve's shortfall sits.
**Evidence:** `claude/reserve-other-sports-gap-2026-11-21.md`. 28-day reserve 73.4% v 73.8% quoted (z -0.24, 741 picks); whole record z -0.79. Weakest cells: CFB 68-74% (z -1.83, 49), CFB away (z -1.79, 72), NCAAB away (z -2.12, only 41), NFL 62-68% (z -1.76, 23): none meets the 50-pick, 2 SE rule, and college away already has its Away mark and a pre-registered tripwire.
**Files:** `claude/reserve-other-sports-gap-2026-11-21.md`, `RELEASES.md`.
**Not changed:** the reserve rule, `WARY_*`, any model constant.
**Roll back:** `git revert` the merge.

## 2026-11-21-emoji-clip: sport emoji no longer clipped (tag pending)

**What changed for a reader.** The sport emoji and the caution sign at the end of a row's league name were cut off at the top and bottom (Douglas, a college football row on his phone). The row's ellipsis rule (`.ko .comp span`, overflow hidden) applied to them inside a 10px caps line; they now overflow freely at 11px.
**Evidence.** A Playwright render of the row markup with the page's own styles at 400 and 1280 wide, before and after: the football clipped flat before, whole after; league names still ellipsise.
**Files.** `index.html` (one CSS rule), `RELEASES.md`.
**Not changed.** Anything but the two marks' styling.
**Roll back.** `git revert` the merge.

## 2026-11-21-graded-once: a match archived under two spellings is graded once (tag pending)

**What changed for a reader.** The football record counted 24 matches twice, once under each spelling the archive held (Southend / Southend United, SC East Bengal / East Bengal / EAST BENGAL, Besiktas / Beşiktaş...). Each is now graded once, so How it went, the bands and the league tables count every match one time.
**Evidence.** On the committed `record-graded.json` (13,938 rows): 24 second copies across nine competitions, 13 won v 12.48 expected (so the record barely moves); none on the Daily List, one reserve copy whose twin is reserve too, no Card leg. Managua and UNAN Managua, which the club matcher would join, are kept apart as two clubs (they met on 2 Nov). `claude/duplicate-spellings-graded-once-2026-11-21.md`.
**Files.** `score.py` (`drop_duplicates`, `distinct_names`, `verification.duplicates`, `record-graded.json` `duplicates`), `ledger.py` (`result_of` marks a duplicate copy), `tests/test_score_duplicates.py`, `claude/duplicate-spellings-graded-once-2026-11-21.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** The model, the Card and its grading, the Daily List rule, the prediction archive.
**Roll back.** `git revert` the merge; the next build regrades with both copies.

## 2026-11-21-flags-emoji-caution: a flag on every football row, sport emoji, and a caution mark (tag pending)

**What changed for a reader.** Every football competition now shows its country's flag: 82 wider leagues from 44 countries (Algeria to Zimbabwe, plus North Macedonia and the UAE under their API-Football spellings) had none. Every fixture row ends its league or sport name with the sport's emoji (⚽ 🎾 🏈 ⚾ 🏀 🏉 🏒). A football league whose graded picks landed 1.5+ standard errors under the model's number on 50+ picks carries a small ⚠️ with its record on hover (today Serie B, Liga MX, Colombia Primera B, Turkey 3. Lig Group 1, Serie D Girone C).
**Evidence.** The caution rule is Douglas's choice of 1.5 standard errors (the site's usual bar is 2, which only Colombia Primera B clears); recomputed every build from `record.json` `byLeague`. `claude/flags-emoji-caution-2026-11-21.md`.
**Files.** `engine.py` (`EXTRA_ISO`, `iso_of`, `FLAG_ONLY`), `build.py` (`unpredictable_leagues`, `caution` in the record summary), `index.html` (42 flag symbols, `sportEmoji`, `cautionMark`), `tests/test_flags.py`, `claude/flags-emoji-caution-2026-11-21.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** The model, ratings, club lookups (`FLAG_ONLY` keeps continental-cup eligibility as before), the Card, the Daily List.
**Roll back.** `git revert` the merge.

## 2026-11-21-early-copy-grading: round-date rows graded from the copy published the day before (tag pending)

**What changed:** `score.nearby_results` refused a match played the day before its archived round date when the last build's copy was written on the match day (La Liga's and the Süper Lig's 8 Nov rounds, played 6 and 7 Nov), though the build the evening before had published the same fixture. It now grades that earlier copy (`score.earlier_copy`) and judges the row at that copy's numbers. It also maps names per run of nearby dates, so the Süper Lig, archived under ESPN's spelling until October and openfootball's since, meets its November results, and a result owned by a same-day prediction under another spelling is never graded twice (`_owned`).
**Evidence:** on the committed archive, 66 more predictions graded (Süper Lig 25, La Liga 15, Austria 8, Greece 6, Scotland 5, Brazil 4), 40 won v 32.1 expected; none refused as late (was 22); none lost; none on the Daily List, 4 reserve, no Card leg; none with a graded twin within 3 days under any spelling. `claude/round-date-early-copy-grading-2026-11-21.md`, `tests/test_score_nearby.py`.
**Files:** `score.py`, `tests/test_score_nearby.py`, `claude/round-date-early-copy-grading-2026-11-21.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the model, the Card and its grading, the Daily List, `load_predictions` (27 existing two-spelling duplicates on the record are filed as an issue).
**Roll back:** `git revert` the merge; results already kept in `current/settled-results.json` stay graded unless those keys are dropped too.

## 2026-11-21-af-short-names: API-Football's short club names priced in the fallback (tag pending)

**What changed.** The football price fallback (`groupings.af_same`) now reads `odds.ALIASES`, so API-Football's short names (QPR, Wolves, Sheffield Weds...) match the board's full names. The 03:11 UTC build left Norwich City v Queens Park Rangers (Championship, 24 Nov) unpriced as `noFixture` beside "Norwich v QPR"; a core-league leg like that can cost the Card a pick.
**Evidence.** The build log's named noFixture line; tests for QPR and Wolves through the fallback and a guard that an alias never crosses clubs (QPR is not Queen of the South). `claude/af-short-names-2026-11-21.md`.
**Files.** `groupings.py` (`af_same`), `tests/test_football_unpriced.py`, `claude/af-short-names-2026-11-21.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** Any Card rule, the model, the bulk price match, `AF_SPELLINGS`.
**Roll back.** `git revert` the merge.

## 2026-11-21-edge-tracker: a tracker graph under Edge picks (tag pending)

**What changed for a reader.** The Bets tab's Edge picks section now ends with a **Tracker** (Douglas: "a visual tracker performance graph underneath that section. Either see all time or be able to scroll two weeks back"): picks won, profit at the best and at the average price (one unit on every Edge pick), a running profit line for each, a dashed line where the live record starts (days before 10 Nov are the rule replayed on prices archived before kick-off), an **All time / Last 14 days** switch, a scrolling strip of day tiles (a dot a pick, won or lost, and the day's units), and the chosen day's picks with prices, the opponent's price and live or replayed. Below it the record split by the opponent's price, 9.0+ against 5.0 to 9.0, since the five-season test backs only 9.0+.
**Evidence.** Display only. The numbers are `score.edge_record`'s, unchanged; it now also writes `days` (one entry a graded day, each pick compact), which reaches the page through the inlined record summary (about 10 KB). On the committed record at 21 Nov: 146 graded, 116 won v 99.6 expected, +9.1% at the average price, +12.1% at the best; live alone 3 graded. Checked in a browser at 1280 and 400 wide.
**Files.** `score.py` (`edge_record` `days`), `index.html` (`edgeTracker`, `etDraw`, `etScroll`, `.et-*` styles), `tests/test_edge_record.py`, `CLAUDE.md`, `RELEASES.md`.
**Not changed.** The Edge rule, its record's totals, the model, any card.
**Roll back.** `git revert` the merge.

## 2026-11-21-played-review: review fixes to the played rows

**What changed for a reader.** Found in a review of the last two releases:
- **Show all on Football's played sections did nothing.** The button redrew every view except the football board. Each tab now redraws itself.
- **Football's played sections ignored the board's filters.** They now follow the competition picker and Strong reads only; with Edge only they are hidden (the archive keeps no Edge flag for a started game).
- **An old Card leg could read "Result due".** A leg drawn from an older group, past its start and outside the two played days, was marked Result due; a row is now marked only within 36 hours of its start or when its result is known.
- **Card and Daily 2x legs off the list now show their result.** A started leg that is neither a list nor a reserve pick is drawn from the day's played rows, with Won / Lost and the score.
- **Smaller page data.** `daylist.js` no longer carries a separate `results` map (about 18 KB on a busy day); the page reads the same results from the played rows.

**Files.** `daylist.py` (`board_results` removed, `league` on played rows), `index.html` (`playedResults`, `playedSection` redraw and filters, `boardResult`, `ogFill`), `tests/test_daylist_played.py` (now tests `played_today`), `CLAUDE.md`.

**Roll back.** `git revert` the merge.

## 2026-11-21-same-date-grading: September's lost results graded from the cache (tag pending)

**What changed:** `score.nearby_results` let a prediction take only a result dated a day or two off its own date, never its own date, and mapped every cached result's clubs before using any. So September's ESPN-only results, which fell out of `LIVE_LOOKBACK` before the settled cache existed, stayed ungraded though the committed ESPN cache holds them, and the Segunda was refused whole on Málaga (June's play-offs, since promoted). A prediction now takes its own date's result, and only cached results within `NEAR_DAYS` of an ungraded prediction enter the all-or-nothing name map.
**Evidence:** on the committed archive and record, 778 predictions graded that were not (674 in September; League One and League Two 53 each, the Segunda 37, MLS 31), landing 46.5% v 47.7% quoted; 740 legacy-unverified, 33 verified, 5 verified by date; one Daily List pick, no Card leg; none graded twice. `tests/test_score_nearby.py` (11 tests). `claude/same-date-cache-grading-2026-11-21.md`.
**Files:** `score.py`, `tests/test_score_nearby.py`, `claude/same-date-cache-grading-2026-11-21.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the model, the Card and its record, the Daily List, `live_results`, the guards against late and double grading.
**Roll back:** `git revert` the merge; results already kept in `current/settled-results.json` stay graded unless those keys are dropped too.

## 2026-11-21-played-yesterday: results across the site, after midnight too (tag pending)

**What changed for a reader.** Played today now has a **Played yesterday** section under it on every sport's tab, so last night's results stay in view after midnight instead of vanishing with the UK day. **Starred** keeps a starred game once it starts (it used to drop off with the board), with In play, Won / Lost and the score. Douglas, 21 Nov 2026: "develop this across the whole website to improve data visibility".

**Files.** `daylist.py` (`played_today` covers `PLAYED_DAYS` 2 UK days, each row with its `day` and `id`), `index.html` (`playedSection` / `playedDay`, `starIdOf` for a played row, Starred reads `played`). Display only.

**Also.** Three FIFA ranking tests had a release date written as 2026-10-22, which stopped being newer than their 30-day-old test file on 21 Nov and failed CI; they now use yesterday's date (`tests/test_rankings.py`).

**Roll back.** `git revert` the merge.

## 2026-11-20-played-today: results on every sport's tab (tag pending)

**What changed for a reader.** Every sport's tab (Football, Tennis, the NBA, the NFL, rugby, ice hockey, the college sports) now opens with **Played today**: every game of the UK day that has started, list or not, at its last pre-start price, with Won / Lost and the score once graded (tennis with its set scores), In play or Result due until then. The top eight by confidence, then Show all. A row still on the board after its start shows the same pill in place of the predicted score. Douglas, 20 Nov 2026: "the won or lost tab should be on every tab for each sport listed ... earlier games from this afternoon show nothing".

**Why they had gone.** `data.json` drops a game at its start, so only the Daily List (from `daylist.js`) kept the day's started games.

**Files.** `daylist.py` (`played_today`, `board_results`; `daylist.json` gains `played` and `results`, about 100 KB on a busy day), `index.html` (`playedSection`, `boardResult`; tennis set scores on `pinnedRow`), `tests/test_daylist_played.py`. Display only: nothing is graded or priced differently.

**Roll back.** `git revert` the merge.

## 2026-11-20-czech-grading: the Czech First League is graded again (tag pending)

**What changed:** `score.py` never saw a Czech First League result after openfootball stopped scoring on 20 Sep (ESPN carries none), so 41 fixtures from 9 Oct to 8 Nov sat ungraded and the league had no 2026-27 rows on the record. `score.lag_results` now grades the `sources.AF_LAG` leagues from the same API-Football day pool the build has filled their table from since 18 Nov, all or nothing on names, same-date first and a day or two off through `nearby_results`' guards, kept in `current/settled-results.json` like the cup results.
**Evidence:** the ledger's ungraded report (19:17 UTC build) led with `football|cze.1 8`; `record-graded.json` has no 2026-27 Czech row; the build log reads "lag cze.1: 40 result(s) filled from API-Football". 41 fixtures, 6 reserve picks, 10 at 60%+, none on the Daily List. `tests/test_score_lag.py` (6 tests).
**Files:** `score.py`, `tests/test_score_lag.py`, `claude/czech-grading-2026-11-20.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the model, the Card and its grading, the Daily List, the build's fill, League One's seven 14 Nov games (postponed, not a grading fault).
**Roll back:** `git revert` the merge, and drop the `cze.1` keys it added to `current/settled-results.json`.

## 2026-11-20-bookies-mark: rows say when the bookmakers rate a pick far lower than the model (tag pending)

**What changed:** every row of every sport (the football board, the sport tabs, pinned Daily List rows) carries a **Bookies NN** mark when the model's chance sits 10+ points above the bookmakers' fair chance (`bookGapChip` in `index.html`, `BOOK_GAP` 0.10). The fair chance is the build's own price (`groupings.board_prices` now carries `f`, the leg's fair chance, also on past prices), else the football market line, else ESPN's free moneyline for US games no UK book prices (`mlFair`). The hover says what the bookmakers give and the evidence. `tools/market_gap.py` prints the tally behind it from the results ledger, by band and sport.
**Evidence:** Douglas's hand review of 20 Nov: Stephen F. Austin (model 83%, DraftKings via ESPN 63%) and South Dakota State (81% v 68%) were the picks the market argued against. On `results-ledger.json.gz` (3 Oct to 20 Nov, every sport, 60%+, first price, fair taken as 1 / price / 1.05): the 193 picks 10+ points above the bookmakers landed 51.3% against the model's 71.2% and the bookmakers' 53.0%; the other 1,190 landed 74.2% v 71.9%. College basketball 15+ above: 48 picks, 37.5% v the model's 75.3%. Matches `tools/market_check.py`'s archive read (picks the model rates above the market land at the market's rate).
**Files:** `index.html`, `groupings.py`, `tools/market_gap.py`, `tests/test_market_gap.py`, `claude/bookies-mark-2026-11-20.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** every model, the Daily List and its order (still no bookmaker input), the Card, the Scale, the slip, the context check. Display only.
**Roll back:** `git revert` the merge.

## 2026-11-20-nominal-dates: games played off their archived round date are graded (tag pending)

**What changed:** `score.py` graded a football prediction only from a result on the same date. openfootball dates some leagues by round (the Premier League a nominal Saturday, La Liga and Brazil's Serie A with no time), so a match played a day later was never graded: Crystal Palace v Liverpool, archived 7 Nov, played 8 Nov. `score.nearby_results` now grades such a prediction from the build's committed ESPN cache (`current/`), the one result of the same pair within `NEAR_DAYS` (3) days, names mapped all or nothing; never when a prediction exists on the result's own date, never when two could claim it, never a match played earlier than archived unless the price was published before that day.
**Evidence:** on the committed archive and record, 46 predictions graded that were not (Brazil's Serie A 31, Premier League 5, Ligue 1 4, La Liga 2, four others); none a Daily List pick, one reserve; 22 left out as not shown to be early; 780 nominal copies left alone beside a real-date copy. `tests/test_score_nearby.py` (9 tests). `claude/nominal-date-grading-2026-11-20.md`.
**Files:** `score.py`, `tests/test_score_nearby.py`, `claude/nominal-date-grading-2026-11-20.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the model, the Card and its grading, the Daily List, `live_results`, the build's lagging fill.
**Roll back:** `git revert` the merge; results already kept in `current/settled-results.json` stay graded unless those keys are dropped too.

## 2026-11-20-free-source-check: no free source for the remaining leagues (tag pending)

**What changed:** a dated line in `claude/data-expansion-plan.md`. No code, data or page change.
**Evidence:** openfootball `2026-27/de.3.json` still returns 404; the 13 Nov checks of ESPN, football-data.co.uk `new/` and openfootball are unchanged. 3. Liga, Liga Portugal 2, UAE and Poland 2 have no free automatable fixture source.
**Files:** `claude/data-expansion-plan.md`, `RELEASES.md`.
**Not changed:** every league, source and the Daily List rules.
**Roll back:** `git revert` the merge.

## 2026-11-20-tennis-ranks-fallback: ATP ranks survive an ESPN outage (tag pending)

**What changed:** `rankings.tennis_ranks` returned `{}` on any failure with no retry and no message, so one ESPN blip silently dropped the ATP ranking adjustment from every men's tennis pick in that build. It now retries with backoff (3 tries, 4xx not retried), falls back to the last good copy kept in `.afcache` with a warning, and only returns `{}` (with a warning) when there is no earlier copy. Rule 9.
**Evidence:** `tests/test_rankings.py` `TennisRanksFailure`: retry then success writes the copy, an outage reads the last good copy, an outage with no copy is empty. Football pipeline untouched.
**Files:** `rankings.py`, `tests/test_rankings.py`, `RELEASES.md`.
**Not changed:** the ATP adjustment, its weights, FIFA fetching, every other source (already retry or fall back).
**Roll back:** `git revert` the merge.

## 2026-11-20-belgium-dup: Belgian Pro League no longer priced twice (tag pending)

**What changed:** `af.144` (API-Football's Belgian Pro League) joins `engine.AF_DUPLICATES`, so the build skips it and `be.1` is the one feed. Readers lose the second copy of each Belgian game on the board.

**Evidence:** `predictions/2026-11-20.json` (1,779 rows, 20 to 26 Nov) held 9 Belgian fixtures in both `be.1` and `af.144` at the same kick-off (Genk v RAAL, Mechelen v Club Brugge, Zulte Waregem v Antwerp, Anderlecht v OH Leuven, Beveren v Gent and others), spelled differently and rated separately. The 4 Oct note had predicted this once `be.1` carried fixtures (it has since the 14 Nov undated-rounds fix). Everything else clean: no exact duplicates, no unrated rows, no row whose kick-off day differs from its date, one row without a kick-off. `af.202` (Tunisia) was checked too and stays: `tn.1` has no fixtures. `nametest.py` all clear (2 duplicate feeds skipped), unit tests pass.

**Files:** `engine.py`, `claude/data-integrity.md`, `RELEASES.md`.

**Not changed:** the matcher, `LIVE_NAMES`, archived af.144 rows (they still grade, as `af.203` rows do).

**Roll back:** `git revert` the commit.

## 2026-11-20-cups-tests: tests for tune_domestic_cups.py (tag pending)

**What changed:** nothing a reader sees. `tune_domestic_cups.py` (279 lines, the cup-tie parser, the outcome model, the paired bootstrap and the tier fit) had no test; 16 now pin it.
**Evidence:** it was one of the largest modules with zero test imports (with `tune_strengths.py`, `eurotest.py`, `backtest.py`). Tests cover `parse_clean` (both line shapes, half-time brackets, headers, pens / a.e.t. / aggregates dropped, CRLF), `outcome` (sums to 1, symmetric, rho 0 equals Poisson), `paired` (zero delta, clear loser, fixed seed), `score`, `fit_tiers` (top tier anchored, unseen tier at its prior) and `load_cup_ties` with `fetch` stubbed (a tie with an unresolved side is dropped). No bug found. Full suite 1286 tests OK, `nametest.py` all clear.
**Files:** `tests/test_tune_domestic_cups.py`.
**Not changed:** the module, the model, any constant.
**Roll back:** `git revert` the merge.

## 2026-11-20-fillers-again: empty Card days, fillers asked again, no change (tag pending)

**What changed.** A note only: `claude/card-empty-days-fillers-again-2026-11-20.md`.

**Evidence.** opp7 and short filled zero empty days on the pool; fillrule5 4 groups on 12 legs (+12%, p(worse) 0.30, under the 100-leg gate); fillwide 2 of 12 v 4.14 expected. Filler switched off by Douglas on 11 Nov; the 19 Nov empty day is rule 14's tighter rule.

**Files.** The note, this entry.

**Not changed.** Any Card constant, `CARD_FILLER`, the model.

**Roll back.** `git revert` this merge.

## 2026-11-20-cha-spellings: the Championship's API-Football spellings (tag pending)

**For a reader.** Championship rows now take API-Football's kick-off where the board's was stale (Sheffield United v Watford, 21 Nov, 12:30 to 15:00), so such games can be priced for the Card.

**Evidence.** The 11:05 UTC build after #441: Serie A retimed 13 fixtures, but "en.2: API-Football kick-offs not used, club names unmatched: QPR; Sheffield Utd", so all or nothing left every Championship row as it was. `claude/championship-af-spellings-2026-11-20.md`.

**Files.** `sources.py` (`ALIASES`: `sheffield utd`, `qpr`), `tests/test_untimed.py`, the note, `CLAUDE.md`.

**Not changed.** Any Card constant, the matcher's rules, the 90-minute guard, the model.

**Check.** The next CI build logs "untimed en.2: N fixture(s)" with no warning.

**Roll back.** `git revert` this merge.

## 2026-11-20-retime-cha-sea: the Championship and Serie A take API-Football's kick-offs (tag pending)

**For a reader.** Championship and Serie A rows show API-Football's kick-off where the board's differed (Sheffield United v Watford moves from 12:30 to 15:00 on 21 Nov), and such games can now be priced.

**Evidence.** The 07:01 UTC build's first named "football kickoff:" line: Sheffield United v Watford board 12:30 UTC v API-Football 15:00 (published listings: 3pm), Bologna v Udinese board 17:00 v 14:00. A stale board time under the 90-minute guard is priced and carries the wrong start into the Card. `claude/retime-championship-seriea-2026-11-20.md`.

**Files.** `sources.py` (`AF_RETIME` adds `en.2`, moves `it.1` from `AF_UNTIMED`), `tests/test_untimed.py`, the note, `CLAUDE.md`.

**Not changed.** Any Card constant, the 90-minute guard, the name rules (all or nothing), the model.

**Check.** The next CI build logs "untimed en.2: N fixture(s)" and "untimed it.1: N" with no unmatched-name warning.

**Roll back.** `git revert` this merge.

## 2026-11-20-kickoff-named: kick-off misses named, OL Lyonnes priced, racing says why it has no tips (tag pending)

**For a reader.** The Horse racing tab now says, above its boards, when the feed's plan sends no bookies' prices or results (today: the free plan, so no tips and nothing graded). Nothing else on the page.

**Evidence.** The 03:08 UTC build: "football Card unpriced: 2", one of them OL Lyonnes v Strasbourg (D1 Arkema, 74%) beside "Lyon W v Strasbourg W"; "kickoff 2 (Championship, Serie A)" with no names; racing "racecards from racecards/free", results 401 "Standard Plan required", 0 tips. `claude/kickoff-legs-racing-feed-2026-11-20.md`.

**Files.** `groupings.py` (`AF_SPELLINGS`, `price_football`, the "football kickoff:" log line), `racing.py` (`feed_of`, `feed_note`, `write_page`), `index.html` (`renderRacing`), `tests/test_football_unpriced.py`, `tests/test_racing.py`, the note, `CLAUDE.md`.

**Not changed.** Any Card constant, the 90-minute kick-off guard, the racing model or tip rule, the records.

**Check.** The next CI build logs "football kickoff:" when a kick-off miss occurs, and OL Lyonnes leaves noFixture.

**Roll back.** `git revert` this merge.

## 2026-11-20-card-unpriced: the price log names the Card's own gaps (tag pending)

**For a reader.** Nothing on the page. The build log and `groupings.json` now say how many football legs the Card could take were left unpriced by every source, and name them ("football Card unpriced: N"); the price reports name each competition with its country, so Russia's or Kuwait's Premier League no longer reads as England's. Under rule 14, the Card's capped price calls go to core-league legs first, as the Card can take nothing else.

**Evidence.** The 19 Nov builds' "noOdds (Premier League 12/14)" was a dozen leagues of that name; England's five unpriced games on 21 Nov were all under the model's 60%. Core-league 60%+ legs on the pool 13 to 23 Nov: 41 priced, 2 unpriced. `claude/football-card-unpriced-2026-11-20.md`.

**Files.** `groupings.py` (`comp_label`, `card_unpriced`, `card_reach`, `price`, the log lines), `tests/test_football_unpriced.py`, the note, `CLAUDE.md`.

**Not changed.** Any Card constant, any price source, the matcher, the page.

**Check.** The next CI build logs "football Card unpriced:" and "Premier League (England)" in "football unpriced:".

**Roll back.** `git revert` this merge.

## 2026-11-19-card-mid-band: the Card's 1.30-1.60 legs read, no change (tag pending)

**What changed:** nothing on the page. A dated note, `claude/card-mid-price-band-2026-11-19.md`.
**Evidence:** on the results ledger, 60%+ picks priced 1.30-1.60 landed 266 of 400 v 273.2 expected (z -0.78; football +0.58); the Card's own 30 of 50 is a small sample of a band on quote. The long band (1.60-1.90, z -3.4) is the one under quote, and its caps (`m7cap160`, `m7short`) already replayed behind live on both football-data seasons.
**Files:** claude/card-mid-price-band-2026-11-19.md, RELEASES.md.
**Not changed:** `CARD_ODDS`, `CARD_RULE`, the record, the page.
**Roll back:** `git revert` the merge.

## 2026-11-19-champ-draw-signals: Championship draw signals rejected (tag pending)

**What changed:** nothing for a reader. A dated note and the reproducing tool record two untested en.2 draw ideas, both rejected.
**Evidence:** walk-forward replay, live curve, paired bootstrap 1500 reps. Draw lift by low expected total: worse in all four seasons (delta +0.0015 to +0.0164, p(worse) 0.93 to 0.997). Club draw-rate lift: +0.0023 on the fit season 2025-26 (p 0.98), +0.0016 on 2026-27 (95 fixtures, under the 250 gate), best case -0.0009 in 2023-24 with p 0.28 and a sign flip.
**Files:** `tools/championship_draw_total.py`, `claude/championship-draw-signals-2026-11-19.md`, `RELEASES.md`.
**Not changed:** all model constants, `engine.py`, `replay.py`.
**Roll back:** `git revert` this commit.

## 2026-11-19-tennis-card-recheck: Card tennis legs re-read, no change (tag pending)

**What changed:** nothing on the site. A dated note records that the planner's tennis shortfall (8 of 15) sits inside the 41 pre-floor legs already read on 13 and 14 Nov; no leg at the 85% floor exists.
**Evidence:** `cardLegsBySport.tennis` 23/41, z -2.13, `atFloor` 0 legs; no tennis price history to replay a rule on (Rule 3 gates cannot run).
**Files:** `claude/tennis-card-legs-recheck-2026-11-19.md`, `RELEASES.md`.
**Not changed:** `CARD_SPORTS_OFF`, `CARD_SPORT_MIN`, any rule.
**Roll back:** `git revert` the commit.

## 2026-11-20-results-scores: scores on every How it went row (tag pending)

**What changed:** How it went's Daily List board shows the final score on every settled row, every sport. Today's day comes from the pinned list (`daylist.js`), which stores a score as text ("91-69"); the board read only a pair of numbers, so the current day's football, basketball, NFL, hockey and rugby rows showed no score. Tennis rows show set scores ("6-3 7-6(3)") in place of the full result note. Douglas, 20 Nov 2026: "add the scores for all sports across the how it went page".
**Evidence:** checked in a browser at 1280px and 400px on the 19 Nov records: no settled row without a score on the Daily List, Football, Tennis and Basketball boards.
**Files:** `index.html` (`listReviewDays`), `RELEASES.md`.
**Not changed:** grading, the records, `daylist.py`.
**Roll back:** `git revert` the commit.

## 2026-11-19-tennis-set-scores: tennis set scores on the Daily List (tag pending)

**What changed:** a settled tennis row on the Daily List now shows the set scores under the winner ("Strakhova won · 6-3 7-6(3)"), read from the tennis result's note (winner first, a tiebreak as the loser's points, "ret." or "Walkover" where the note says so). Douglas, 19 Nov 2026: "I'm not seeing the tennis scores applied."
**Evidence:** the parser checked on 30 real notes from `tennis-record.json` (tiebreaks, retirements, walkovers); the list checked in a browser at 1280px and 400px on 19 Nov's list (Erjavec v Strakhova, Fils v Zverev).
**Files:** `index.html` (`tennisSets`, `putPinned`), `RELEASES.md`.
**Not changed:** grading, the records, any other sport's row.
**Roll back:** `git revert` the commit.

## 2026-11-19-pl-times: the Premier League and Serie A take API-Football's kick-offs (tag pending)

**For a reader.** Premier League games now show their real TV kick-offs and days instead of openfootball's Saturday 15:00 placeholder, and Serie A's 29 Nov round, which openfootball gives no time, takes its real day and time as La Liga, Brazil's Serie A and the Süper Lig already do. On 21 Nov that is Manchester City v Fulham and Newcastle v Arsenal priced (both names found, the kick-offs apart) and Liverpool v Manchester United on its Sunday. A Card group can no longer hold a 12:30 game open until 15:00.

**Evidence.** The 19:39 UTC build: `untimed tr.1: 13`, so the Süper Lig fix landed (#417 closed); its pricing line `kickoff 4 (Premier League 2)`, `moved 1 (Premier League)`; openfootball's en.1 file has all 20 games of the 21 and 28 Nov rounds at 15:00 and it.1's 29 Nov round 10 of 10 untimed. `claude/premier-league-nominal-times-2026-11-19.md`.

**Files.** `sources.py` (`AF_UNTIMED` it.1, `AF_RETIME` en.1, `af_untimed_rows`), `build.py` (`fill_untimed` `retime`), `tests/test_untimed.py`, the note, `CLAUDE.md`.

**Not changed.** Any Card constant, the name matcher, `price_football`'s 90-minute guard, the archive.

**Check.** The next CI build should log `untimed en.1: N fixture(s)` with no en.1 warning and no Premier League game under `kickoff` or "football moved:".

**Roll back.** `git revert` this merge, or empty `AF_RETIME` and drop it.1 from `AF_UNTIMED`.

## 2026-11-19-card-rule14: the Card back on rule 8's constants, and the scoreboard on the live rule (tag pending)

**For a reader.** The Card runs rule 8's constants again (rule 14): the model's picks rated at or above the bookmakers, core leagues only, tennis at 75%+, the 2x alone, no two-day groups. Douglas, 19 Nov 2026, shown every rule rebuilt on the whole archive: "let's then group to rule 8". The Bets tab's "Is it working?" box now headlines the live rule's own groups and legs, named and dated, with every rule since 25 Oct under More numbers; the Card's rule text reads the live constants. Fewer cards (rule 8 built one about one day in three), the Daily 2x and List card unchanged.

**Evidence.** On the pool rebuilt rule by rule (30 Oct to 19 Nov): rule 8 8 groups, 5 won v 3.2 expected, +64%, +14% a leg on 24 legs; rule 13 46 groups, -4%. Rule 8 v live +0.51 units a day, p(worse) 0.15 on 24 legs, under the gate's 100; the five-season football replay agrees in direction. The owner's call on a small sample. `claude/card-rule14-rule8-2026-11-19.md`.

**Files.** `groupings.py` (`CARD_MODEL_EDGE` 0.0, `CARD_CORE_ONLY` True, `CARD_SPORT_MIN` tennis 0.75, `CARD_SPAN` False, `CARD_RULE` 14; `cardLive`, `cardLiveRule`, `cardLiveLegsBySport`), `tools/card_replay.py` (rules 10 to 13 pinned, `rule13`, `span2`, `RULES`), `index.html` (`tbRecord`, `RULE_WHAT`, `RULE_FROM`, the rule copy), fourteen test files re-pinned. Checked at 1280 and 400px.

**Not changed.** `CARD_MODEL_OPP_MIN` (empty), `CARD_BUILD` (2x), the context veto (paused), the Daily 2x, the List card, the slip, every record.

**Roll back.** `git revert` this merge, or set the `rule13` variant's constants with `CARD_RULE` 15.

## 2026-11-19-super-lig-times: the Süper Lig takes API-Football's kick-offs (tag pending)

**For a reader.** Süper Lig games now show their real day and kick-off, as La Liga and Brazil's Serie A have since this afternoon. The first build with the untimed fill (#425) moved 15 La Liga and 11 Brazilian games to their real days but refused the Süper Lig whole: API-Football spells BB Erzurumspor "Erzurumspor FK", and the fill is all or nothing on names. Galatasaray v Samsunspor and Kocaelispor v Fenerbahçe (21 Nov, board 22 Nov) went unpriced as "moved", and a leg with no start cannot reach the Card.

**Evidence.** The 16:28 UTC build log (`tr.1: API-Football kick-offs not used, club names unmatched: Erzurumspor FK`); `predictions/2026-11-19.json` (9 of 9 tr.1 rows with no kick-off). `claude/super-lig-untimed-spelling-2026-11-19.md`.

**Files.** `sources.py` (`ALIASES`), `tests/test_lagging_results.py`, the note.

**Not changed.** The fill's rule, the matcher's guards, any Card constant.

**Check.** The next CI build should log `untimed tr.1: 9 fixture(s)` and no Süper Lig games under "football moved:".

**Roll back.** `git revert` this merge.
## 2026-11-19-past-bookies: the Bookies line under the bar on a played Daily List game (tag pending)

**For a reader.** A Daily List row for a game already played now carries the same "Bookies 1.18 / 5.11" line under its probability bar as a game still to come (the pick's price, the draw where there is one, the other side), from the last price read before the start. Douglas, 19 Nov 2026: "I want the odds under the red and yellow bar as well, as they are on the upcoming games ... easier to read that way."

**How.** `groupings.past_prices` now keeps the other side's last price (`opp`) and the draw's (`draw`) with the pick's; `pastLine` in `index.html` draws the line for pinned rows, and `oppLine` falls back to it for a started game that has left the build's pool. Display only.

**Files.** `groupings.py`, `index.html`, `tests/test_past_prices.py`. Checked at 1280 and 400px on the local build.

**Not changed.** Upcoming rows, the chips on the right, the record.

**Roll back.** `git revert` this merge.
## 2026-11-19-card-rules-table: every Card rule replayed on the same days (tag pending)

**For a reader.** The nightly Card review now opens its replay section with one table of every Card rule the page has run (1, 4, 5, 6, 7, 8, 10, 11, 12, 13), each rebuilt on the whole archived pool so they are read on the same days, with its live dates and its own live record beside it. Douglas, 19 Nov 2026: "which rule has performed the best over the entire timeline."

**Evidence.** The read at 19 Nov is in `claude/card-rules-timeline-2026-11-19.md`: no rule beats live at the gate; the few-group core-league rules sit above expectation and every widening at or under it.

**Files.** `tools/card_replay.py` (`RULES`, variants `rule1`, `rule4`, `rule7`, `rule8`, `rule10`, `rule11`, `rules_table`, the `rules` block in `card-replay.json`), `tools/card_review_post.py` (`rules_section`), `tests/test_card_rules_table.py`.

**Not changed.** The live Card, any constant, the existing variants and their pairing.

**Roll back.** `git revert` this merge.
## 2026-11-19-mlb-recheck: MLB above-quote gap re-checked, no change (tag pending)

**What changed:** nothing for a reader. A dated note records that the MLB live gap (27 of 40, z +1.5) is the same 40 games as on 12 Nov, so no new evidence.
**Evidence:** `sports-graded.json` recomputed; history check window lands under quote (60%+ 61.4% v 64.0%, 3,626 games). Gates: not applicable, no model change.
**Files:** `claude/mlb-above-quote-recheck-2026-11-19.md`, `RELEASES.md`.
**Not changed:** `sports.py`, `sports.json`, calibration.
**Roll back:** `git revert` the merge.

## 2026-11-19-untimed-board: La Liga, the Süper Lig and Brazil's Serie A take API-Football's date and time (tag pending)

**What changed.** openfootball dates these three leagues by round and gives no
kick-off, so every row on the 19 Nov board (br.1 10, es.1 10, tr.1 9) had no
start and a date a day either side of the real one (Athletic v Espanyol: board
22 Nov, API-Football 20 Nov). `build.fill_untimed` now gives each such row the
date and UTC time API-Football lists, before the window is cut, so the row
lands on its real day with a real start and the Daily List, archive and
grading use it. Rule: unplayed, no time, dated today or later, exactly one
fixture of the same two clubs within 3 days, TBD stand-in times ignored, all or
nothing on names per league (a club that matches nothing, or two that match
one, changes nothing and logs a warning). Build log: "untimed <code>: N
fixture(s) took API-Football's date and time".

**Evidence.** Unit tests (`tests/test_untimed.py`, 7) for the date move, the
name refusal, played / timed / far rows, a pair listed twice, TBD and country.
The sandbox cannot reach API-Football, so the first CI build with the key is
the live check: read the "untimed" lines and compare `kickoff` on the three
leagues in `predictions/<date>.json`.

**Files.** `build.py` (`fill_untimed`, one block in `main`), `sources.py`
(`AF_UNTIMED`, `af_untimed_rows`, `af_untimed_pick`), `tests/test_untimed.py`.

**Not changed.** `predictions/` and `ledger.py` untouched: a pick moves between
days only through the board row, before it is archived; archives already
written keep their date, and a fixture first archived on the nominal day and
then moved is handled by ledger's existing moved-fixture rule. #416's Card
guard stays as the backstop. No model number, no Card constant.

**Roll back.** `git revert` this commit.

## 2026-11-19-last-price: a started game keeps its last price on the Daily List (tag pending)

**For a reader.** A Daily List row for a game already played (the early-hours NBA and tennis, looked at in the afternoon) kept its won / lost mark but lost its price chip, because the build only prices games still to come. The chip now stays, in grey, showing the last price read before the start (William Hill's where it had one, else the average), with "Last price before the start" in its tooltip. Douglas, 19 Nov 2026: "keep the odds there as we last knew them ... a slight reference point."

**How.** `groupings.past_prices` reads yesterday's and today's pool files (`groupings-archive/pool-<date>.json.gz`) for every game this build no longer carries and takes `lastOdds` / `lastBest` / `lastBooks` (the last pre-start price the archive already keeps), else the first real price; estimates are never used. Merged under this build's own prices in `groupings-data.js` `prices` with `past: true`; `priceChip` in `index.html` adds the `past` class (muted ink) and the tooltip line. Display only; nothing reads it.

**Files.** `groupings.py` (`past_prices`, `PAST_PRICE_DAYS`), `index.html` (`priceChip`, `.bkchip.past`), `tests/test_past_prices.py` (new). Checked at 1280 and 400px on the local build (166 past prices from the 18 and 19 Nov pools).

**Not changed.** The William Hill marks on list rows (`listBooks`, which already read the pool for started list picks), the record, grading, any model.

**Roll back.** `git revert` this merge.
## 2026-11-19-racing-open-on-races: the racing tab opens on its races (tag pending)

**What changed:** Douglas, 21:37: "Why are there no horse races listed?" The tab opened on Tips, and on the free racing plan (no bookmaker prices) there are no tips, so the 72 races sat behind Every race under a message that read as the model finding nothing. The tab now opens on the first day with a race still to run, and on Every race when that day has no tips; the Tips board says plainly when the feed sends no prices; a race with no clear pick still names its top-rated horse (muted, No read).
**Evidence:** deploy runs 44582456256 to 44615154586: "racing: 72 races on 2 day(s), 0 tips"; checked in a browser at 1280px and 400px on that day's archive.
**Files:** `index.html`, `RELEASES.md`.
**Roll back:** `git revert` the commit.

## 2026-11-19-racing-distance: race distances from the free racecards (tag pending)

**What changed:** the free racecards carry the distance only in furlongs (`distance_f`, read from the field list the build now logs); it shows as miles and furlongs ("2m 0½f").
**Files:** `racing.py`, `tests/test_racing.py`, `RELEASES.md`.
**Roll back:** `git revert` the commit.

## 2026-11-19-racing-log-keys: the racing build names the feed's fields (tag pending)

**What changed:** each build prints the racecard's race and runner field names. The free plan's 72 races came with no going, distance, trainer form or prices, and the log shows whether those are missing from the plan or named differently.
**Files:** `racing.py`, `RELEASES.md`.
**Roll back:** `git revert` the commit.

## 2026-11-19-racing-rate-limit: racing calls spaced for the free plan (tag pending)

**What changed:** the racing build now waits 1.2 seconds between calls (`GAP_S`) and, once one racecard endpoint answers, asks only that one for the next day. The 15:32 build (run 44555182414) found the account on the free plan ("Standard Plan required", "Basic Plan required"), took today's free racecards, then had tomorrow's refused: "Rate limit exceeded: 1 per 1 second".
**Evidence:** the log lines above; `tests/test_racing.py` `FeedFallback`.
**Files:** `racing.py`, `tests/test_racing.py`.
**Not changed:** the model, the tip rule, grading, the page.
**Roll back:** `git revert` the commit.

## 2026-11-19-racing-feed-diagnose: the racing feed says why it refused, and falls back by plan (tag pending)

**What changed:** the first build with the secrets was refused (HTTP 401, deploy run 44552853538). The build log now carries The Racing API's own error message, and racecards come from the richest endpoint the plan allows (`racecards/standard`, then `basic`, then `free`, `CARD_PATHS`), with the one that answered named in the log.
**Evidence:** the 401 above; `tests/test_racing.py` `FeedFallback`.
**Files:** `racing.py`, `tests/test_racing.py`.
**Not changed:** the model, the tip rule, grading, the page.
**Roll back:** `git revert` the commit.

## 2026-11-19-horse-racing: the Horse racing tab, on trial (tag pending)

**What changed:** a new sport tab, Horse racing, after Tennis in the sports row (and on the Analysis page's bar). UK and Irish racing from The Racing API. Every runner gets a chance to win and to place; the day's tips are the horses with a clear chance (22%+) whose best UK price pays at least 8% more than it, most likely first, at most six a day, never in fields over 16. Four boards in the site's own styles: Tips (the record, a tracker of every tip by day with a divider per day, the tips grouped by Douglas's betting windows with the price to take and the main danger, changes and races left alone), Every race, Racecards and Record (chance v winners, running profit, by band, what the model is learning by condition). Marked Trial throughout.
**Evidence:** none yet: a new sport with no graded race. The chance follows Benter (1994): a racecard score (official rating, form, trainer's 14 days, time since the last run) blended with the bookies' fair chance, starter weights refitted by hand at 500 graded races. `tests/test_racing.py` pins the reader, each-way terms, the place chance, the tip rule, settlement and the empty states; the tab was checked in a browser at 1280px and 400px on a sample card (no horizontal overflow, no page errors).
**Needs:** the secrets `RACING_API_USERNAME` and `RACING_API_PASSWORD` (theracingapi.com). Until then the tab says the feed is not connected. The first build with them: `python3 racing.py --probe` prints the feed's field names to check against `race_of` / `runner_of`.
**Files:** `racing.py`, `index.html`, `analysis.html`, `.github/workflows/deploy.yml`, `.gitignore`, `tests/test_racing.py`, `claude/horse-racing-2026-11-19.md`, `CLAUDE.md`.
**Not changed:** every other sport, the Daily List, the Card, Scale, any model.
**Roll back:** `git revert` the commit; `predictions-racing/` and `racing-record.json` are harmless if left.

## 2026-11-19-card-calls-first: capped football price calls go to Card picks first (tag pending)

**What changed:** each build makes at most 150 one-fixture price calls for mid-priced football legs the day's bulk prices missed. They went in board order, so a 62% Premier League pick the Card could take was left unpriced (off the Card) behind 45% picks in lower leagues. The calls now go first to legs the Card could take once priced (model 60%+, a league the Card takes, clean), then list and reserve picks, then the rest, nearest day and strongest pick first.
**Evidence:** deploy run 44511549028 (19 Nov 11:05 UTC): "football unpriced: ... capped 97 (Premier League 5, ...)". The pool for 21 and 22 Nov holds 71 Card-reachable football legs with no real price, 24 of them mid-priced. `claude/football-calls-card-first-2026-11-19.md`. Tests: two new in `tests/test_football_unpriced.py` (the first fails on the old code), full suite 1,221 passing, `nametest.py` clear.
**Files:** `groupings.py`, `tests/test_football_unpriced.py`, the note, `CLAUDE.md`.
**Not changed:** `FB_CALLS_MULT`, any `CARD_*` constant or `CARD_RULE`, the replays, the page.
**Roll back:** `git revert` the commit.

## 2026-11-19-no-kickoff: football legs with no kick-off time take API-Football's, and the Card waits for one (tag pending)

**What changed:** La Liga, the Süper Lig and Brazil's Serie A reach the board with no kick-off time (every one of their 29 rows on 19 Nov). A football leg with no time never counted as started, so a Card group holding one could stay open past the real kick-off. A leg matched to an API-Football fixture now takes that fixture's kick-off (`whenSrc`), the Card refuses a leg with no start time (the football twin of the tennis order-of-play guard), and a re-check keeps a published leg's kick-off. Six more API-Football spellings are priced: Union St. Gilloise, Hertha BSC, U. Catolica, LDU de Quito, Atletico Torque, West Ham W.
**Evidence:** deploy run 44478001048 (19 Nov 07:13 UTC): noFixture 14, six of the twelve named beside their fixture under another spelling; `predictions/2026-11-19.json` 29 rows with no kick-off, four of them list or reserve picks. No archived Card leg has lacked a time so far (540 legs). `claude/football-no-kickoff-2026-11-19.md`.
**Files:** `groupings.py`, `tests/test_football_unpriced.py`, `tests/test_context_review.py`, `tests/test_tennis_live_bands.py` (their legs now carry a start), the note, `CLAUDE.md`.
**Not changed:** any `CARD_*` constant or `CARD_RULE`, the replays, the board, the Daily List, `score.py`.
**Roll back:** `git revert` the commit.

## 2026-11-19-af-spellings: four football spellings priced, moved fixtures told apart (tag pending)

**What changed:** football legs whose names API-Football spells another way are now priced: AGF (Aarhus), Inverness Caledonian Thistle (Inverness CT), STVV (St. Truiden), Dux Logroño (Edf Logrono W), via `groupings.AF_SPELLINGS`. A leg with no fixture on its date but listed by API-Football on another day in the window is counted `moved` ("football moved:" in the build log, `football.moved` in `groupings.json`), not `noFixture`, and never priced.
**Evidence:** the first named read (#410, deploy run 44450821083) had noFixture 26; of the twelve named, four were these spellings beside their fixture in `near`, in leagues the Card admits, so each was off the Card for a name alone. Liverpool v Manchester United, Brentford v Everton and five Brazilian Serie A games had no fixture on the board's date. `claude/football-nofixture-names-2026-11-19.md`. Tests: three new in `tests/test_football_unpriced.py` (all fail on the old code), full suite passing, `nametest.py` clear, fast build clean.
**Files:** `groupings.py`, `tests/test_football_unpriced.py`, the note, `CLAUDE.md`.
**Not changed:** `same`, `LIVE_NAMES`, any `CARD_*` constant, the model, the page.
**Roll back:** `git revert` the commit.

## 2026-11-19-own-band-third: own-band List admission already shipped (tag pending)

**What changed:** nothing for a reader. A dated note records that the planner's own-band task is the rule shipped on 20 Oct 2026 and live for every sport.
**Evidence:** `sports.stored_threshold` on `sports.json`: NFL 80%, NBA 80%, rugby 80%, cfb 80% (off the list), ncaab 85%, WNBA 85%. Held-out numbers in the 20 Oct and 11 Nov notes.
**Files:** `claude/own-band-rerun-2026-11-19.md`, `RELEASES.md`.
**Not changed:** all code and constants.
**Roll back:** `git revert` this commit.

## 2026-11-19-nofixture-names: unpriced football legs named in the build log (tag pending)

**What changed:** a football leg API-Football lists under no fixture (`noFixture`) is now named in the build log ("football noFixture: date competition: home v away (near: ...)") and in `groupings.json` (`football.noFixture`, up to `NOFIXTURE_KEEP` 12), with the day's fixtures that share one of its names. Until now the log gave only counts.
**Evidence:** the 18 Nov 23:15 build logged "noFixture 11 (Serie A 5, Premier League 2, Superliga 1)": core-league legs left unpriced, so off the Card and the Edge flag, and CLAUDE.md's rule is that a noFixture cluster in one league is a spelling for `LIVE_NAMES`. Without names no session could tell which, as the sandbox cannot reach API-Football. The next CI build prints them.
**Files:** `groupings.py`, `tests/test_football_unpriced.py`, `CLAUDE.md`.
**Not changed:** which legs are priced, any `CARD_*` constant, the page, the record.
**Roll back:** `git revert` the commit.

## 2026-11-18-decisions-table: the Card review lists every pre-registered decision (tag pending)

**What changed:** the nightly Card review opens, after the live Card's 14 days, with one table of every pre-registered Card decision: the tennis tripwire, the floor line, rule 13 v rule 12, the tennis floor back to 75%, core leagues only, the opposition floor (`m7opp5`, `m7opp9`), the context veto, the Daily 2x, the List 2x and List long. Each row gives the trigger from its note, where it stands tonight, waiting / **due** / **fired**, and who acts; a bold line counts what is due. The opposition floor's auto-adopt now goes to Douglas, since rule 13 dropped it at his call.
**Evidence:** tonight nothing is due or fired (Card 13 of 42 v 14.33 expected, z -0.44; rule 13 0 of 2; `rule12` -0.89 a day on the pool, p(worse) 0.853). The List card has built nothing since 16 Nov because no non-college list pick had a real price of 1.15+ over the international break. `claude/card-decisions-table-2026-11-18.md`. Tests: `tests/test_review_decisions.py` (7), full suite passing, `nametest.py` clear.
**Files:** `tools/card_review_post.py`, `tests/test_review_decisions.py`, the note, `CLAUDE.md`.
**Not changed:** any `CARD_*` constant, the page, the record.
**Roll back:** `git revert` the commit.

## 2026-11-18-rule12-recheck: rule 13's split reads its groups again (tag pending)

**What changed:** the record's split of the rule 13 Card (`cardRule13Split`: would rule 12 have built the group, or does it hold a pick only rule 13 admits) counted every group as unknown. `recheck_card` rebuilt each leg from the board and dropped `rule12Fault` on the first re-check, so no rule 13 group reached the archive with it. The re-check now asks rule 12 again, and the grader reads an archived rule 13 leg without the field from the leg as frozen (`rule12_fault`, marked `r12` "derived"; the review says how many groups were read that way).
**Evidence:** all four rule 13 Card groups to 18 Nov were `unknown`; derived, every one holds a pick rule 12 would have refused, and both settled groups lost on such a pick (Spurs 69% v the bookmakers' 78%; Isparta, opposition 4.41). Four groups: a record, not a reason to act. `claude/card-rule12-fault-recheck-2026-11-18.md`. Tests: `tests/test_card_rule12_recheck.py` (fails on the old code), full suite 1,204 passing, `nametest.py` clear.
**Files:** `groupings.py`, `tools/card_review_post.py`, `tests/test_card_rule12_recheck.py`, the note, `CLAUDE.md`.
**Not changed:** any `CARD_*` constant, which picks the Card takes, the archive files, the page.
**Roll back:** `git revert` this merge (the split goes back to unknown).

## 2026-11-18-office-review: office review and next week's priorities (tag pending)

**What changed:** `claude/office-review-2026-11-18.md`: what shipped 9 to 18 Nov, what was learned (including rejected tests), where accuracy stands, three tasks for next week (Kofi, Hannah, Susie). A report by nature.

**Evidence:** read from `record.json`, `groupings-record.json` and `RELEASES.md`; nothing fitted.

**Files:** `claude/office-review-2026-11-18.md`, `RELEASES.md`.

**Not changed:** code, model numbers, the site.

**Roll back:** `git revert` the commit.

## 2026-11-18-grading-audit: Grading audit against ESPN, no bug (tag pending)

**What changed:** nothing a reader sees. A dated audit in `claude/results-review-board.md`.

**Evidence:** 1,133 football, 508 sports and 57 tennis rows from 11-17 Nov checked against ESPN's scoreboards: 269 football, 188 sports and about 55 tennis matched to a completed game, 0 mismatches. Walkovers (54 in the live feed) void, retirements (42) graded, as documented. 12 of 53 graded tennis retirements came before the first set finished (5 landed, 7 not): a policy question, recorded for Douglas.

**Files:** `claude/results-review-board.md`, `RELEASES.md`.

**Not changed:** all code, models, record files.

**Roll back:** `git revert` the merge.

## 2026-11-18-group-bands: Group bands against their stated chance, backtest write-up (tag pending)

**What changed:** nothing in the site. A dated section in `claude/odds-groupings.md` reads every group band in `groupings-record.json` against its stated chance. Findings only: the evidence fails the gates (2 to 36 groups a band, 100 needed), so no rule change.
**Evidence:** retired kinds 136 settled, 39 won v 46.2 expected (z -1.3); Steady 4 of 25 v 9.7, Stretch 1 of 15 v 3.6, Balanced 5 of 17 v 5.0; Card 2x 11 of 36 v 13.7, Card 3x 7 of 16 v 4.2.
**Files:** `claude/odds-groupings.md`.
**Not changed:** `groupings.py`, any constant, any record file.
**Roll back:** `git revert` the commit.

## 2026-11-18-tennis-keys-3: Tennis keys with no Odds API match, third look (tag pending)

**What changed:** nothing in the site. A dated note records that the logging asked for already exists and that the key list still has not been seen.
**Evidence:** `groupings.py --probe` already reports `tennisKeys` and `noKey` (#55); no `ODDS_API_KEY` here and no committed report holds the list, so no fix can be tested.
**Files:** `claude/odds-api-tennis-keys-2026-11-18.md`.
**Not changed:** `_odds_keys`, any model, any price rule.
**Roll back:** delete the note.

## 2026-11-18-czech-af: the Czech First League scored from API-Football (tag pending)

**What changed:** the Czech First League's table (`cze.1`) had stopped at 20 Sep: openfootball's 2026-27 file stopped scoring and ESPN's `cze.1` slug answers nothing, so since 14 Nov every Czech fixture has been flagged under Celtic's Law (41 results missing from 9 Oct). The build now scores its blank fixtures from the API-Football day pool it already reads for the wider leagues (`sources.AF_LAG`, `af_lag_results`, `af_lag_pick`; `build.fill_lagging(source="apifootball")`), under openfootball's spelling, all or nothing on names and on country. No extra API calls, nothing written to `current/`. Czech letters (ň ř ý ů ě ť ď) now fold in `sources._base`, and `plzen` is an alias of Viktoria Plzeň. When the fill lands, the stale flag clears itself and Czech favourites can reach the Daily List and the Card again on a current table.
**Evidence:** cannot be run here (the sandbox reaches no API-Football); the first CI build prints `lag cze.1: N result(s) filled from API-Football`, or a warning naming the unmatched clubs or the wrong country, and fills nothing. Tests: `tests/test_af_lag.py` (the 16 openfootball spellings against API-Football's short ones, one club each; season, country and played filters; the fill under openfootball's names). `claude/czech-results-api-football-2026-11-18.md`.
**Files:** `sources.py`, `build.py`, `tests/test_af_lag.py`, the note, `CLAUDE.md`.
**Not changed:** any model constant, any `CARD_*` constant, the stale-league rule, the record.
**Roll back:** `git revert` this merge (Czech rows go back to flagged).

## 2026-11-18-staking-live-rule: the Card's bankroll read from the live rule's replays (tag pending)

**What changed:** the nightly Card review's staking sections. The "replay" bankroll was the rule 5/6 Card (football only, 2x and 3x); it now reads the live rule's football-data replay (`cardM7.live`), and a new "pool" section reads the live rule rebuilt on the archived pool, every sport (`card-replay.json` now carries the live variant's `groupList`).
**Evidence:** football-data live rule 47 groups, 24 won v 19.0 expected, season bankroll 34 units (was 28 from the old Card); pool 26 groups, 13 v 10.0, 1.24 a day, 95 units; live record 41 groups, 0.929 of expected, 317 units. `claude/card-staking-live-rule-2026-11-18.md`.
**Files:** `tools/staking.py`, `tools/card_replay.py`, `tools/card_review_post.py`, `tests/test_staking.py`, the note, `CLAUDE.md`.
**Not changed:** any `CARD_*` constant, `CARD_STAKE`, the record, the page.
**Roll back:** `git revert` this merge.

## 2026-11-18-price-gaps-rule13: the Card review's price gaps read under rule 13 (tag pending)

**What changed:** the nightly Card review's "Legs kept off by a missing price" section no longer says a priced leg must clear the value demand (there is none under `CARD_RULE` 13), and now names the started days the live Card left empty that held such legs.
**Evidence:** 108 legs pass every condition but the price since 10 Nov, 39 on started days; 6 of those on 4 empty days (11, 12, 13, 16 Nov), at most 2 a day against the 3 a group needs, all lower leagues no UK book prices. Price coverage is still not the lever. `claude/card-price-gaps-rule13-2026-11-18.md`.
**Files:** `tools/card_funnel.py`, `tools/card_review_post.py`, `tests/test_card_funnel_gaps.py`, `tests/test_empty_card_days.py`, the note, `CLAUDE.md`.
**Not changed:** any `CARD_*` constant, the record, the page.
**Roll back:** `git revert` this merge.

## 2026-11-18-weakest-sport: no other sport is under quote by two standard errors (tag pending)

**What changed:** a dated note only, `claude/weakest-sport-read-2026-11-18.md`.
**Evidence:** NFL 61.5% v 65.0% (104), college football 67.3% v 70.0% (358; 70%+ z about -1.4), baseball 50% v 55.9% (54), ATP 63.2% v 63.5% (551), WTA 64.2% v 64.3% (916); NBA, college basketball, rugby above quote. None reaches z -2, so no test was run.
**Files:** `claude/weakest-sport-read-2026-11-18.md`, `RELEASES.md`.
**Not changed:** any model, rule or code.
**Roll back:** `git revert` the commit.

## 2026-11-18 Croatia, Serbia, Ukraine, Hungary, Korea, UAE: already covered, third check (tag pending)

**What changed:** a dated note only, `claude/af-new-leagues-recheck-2026-11-18.md`. No code, model or rule changed.
**Evidence:** all six countries are already in the build (`sources.AF_NEW`, `af.301`, lower divisions in `af-leagues.json`); the 17 Nov archive holds 5-8 fixtures for each top flight; extra API allowance per build 0; `nametest.py` clear. Rule 3 replay needs the API key and prior-season history, unavailable here, so the leagues stay off the List.
**Files:** `claude/af-new-leagues-recheck-2026-11-18.md`, `RELEASES.md`.
**Not changed:** `sources.py`, any model number, the Daily List.
**Roll back:** `git revert` the commit.

## 2026-11-18-price-timing-hour: when to take the Card's prices, re-read by hour and sport (tag pending)

**What changed.** A dated note only.
**Evidence.** 283 pool legs: early-priced +1.89% (p 0.037) but football +0.61% (p 0.22), NBA +4.84% on 43 legs; evening-priced -0.38%; settled late gain +0.65 points on 249 legs, p 0.307, no clear read. `claude/price-timing-hour-sport-2026-11-18.md`.
**Files.** The note.
**Not changed.** `notify.py`, `SLOTS`, build times, any rule.
**Roll back.** `git revert` this merge.

## 2026-11-18-pool-recheck: the Card replay already runs on the pool (tag pending)

**What changed.** A dated note only.
**Evidence.** 13 pool-replay tests pass; the replay reads 1,217 settled priced pool legs over 20 days; live 26 groups, 13 won v 39% expected. `claude/card-replay-pool-recheck-2026-11-18.md`.
**Files.** The note.
**Not changed.** Any code, rule or record.
**Roll back.** `git revert` this merge.

## 2026-11-18-cap160: the Card's long legs read, a 1.60 cap pre-registered (tag pending)

**For a reader.** Nothing on the page. The nightly Card review and the Monday football-data read gain one variant, `m7cap160`: the Card with its price range capped at 1.60.

**Evidence.** Results ledger, 60%+ picks at the first price: football 1.60-1.90 landed 50.0% v the model's 63.5% (76 legs, z -2.45, -14.9%); NBA and tennis the same way on few legs; under 1.60 on quote. The Card seldom picks such legs: pool replay `m7cap160` +0.03 units a day v live, p(worse) 0.41 on 123 legs. Football-data (CI on #394): behind live in both seasons, pooled -0.15 units a day, p(worse) 0.91 on 370 legs: rejected. `claude/card-m7cap160-2026-11-18.md`.

**Files.** `tools/card_replay.py`, `tools/card_legs_history.py`, `tests/test_card_m7cap160.py`, the note, `CLAUDE.md`.

**Not changed.** `CARD_ODDS`, `CARD_RULE`, the Daily 2x, the record, the page.

**Roll back.** `git revert` this merge.

## 2026-11-18-stake-line: Card stake line re-checked, still not built (tag pending)

**What changed:** a note only, `claude/card-stake-line-2026-11-18.md`. No page change.
**Evidence:** the pool replay of the live rule holds 26 groups (13 won v 39% expected) against the 100 the 10 Nov note set as the condition; the football-data replay's 33 groups are superseded football-only rules. A stated unit from either would be false precision.
**Files:** `claude/card-stake-line-2026-11-18.md`, `RELEASES.md`.
**Not changed:** `CARD_STAKE`, `CARD_RULE`, `tools/staking.py`, any record, the page.
**Roll back:** `git revert` the merge commit.

## 2026-11-17-staking-rate: the Card's bankroll read at its current rate (tag pending)

**For a reader.** Nothing on the page. The nightly Card review's live bankroll lines now count the groups the Card makes today (the 2x alone since 11 Nov, empty days included), not October's six-a-day Card.

**Evidence.** Live rate 1.9 a day (40 groups over the 21 days that had one) becomes 0.71 (5 groups, 11 to 17 Nov). A month: 57 groups, 48.7-unit drawdown, 98-unit bankroll becomes 21 groups, 24.6 units, 50 units. `claude/card-staking-live-rate-2026-11-17.md`.

**Files.** `tools/staking.py` (`RATE_FROM`, `RATE_MIN_DAYS`, `rateFrom`), `tools/card_review_post.py`, `tests/test_staking.py`, the note.

**Not changed.** Any Card rule, `CARD_STAKE`, the record, the page.

**Roll back.** `git revert` this merge.

## 2026-11-17-fd-span: the football-data Card replay builds two-day groups, like the page (tag pending)

**For a reader.** Nothing on the page. The football-data side of the Card's gate now replays the Card the page builds, two-day groups included, as the pool side has since earlier today; both sides of the gate read the same live.

**Evidence.** Five football-data seasons (CI run 44128924620): live 476 groups, return 0.950 v day by day (`nospan`) 391 groups, 0.933; two-day groups ahead in four seasons of five. Against the spanning live no variant passes the gate; `rule12` pooled 1.026 (+0.14 a day, p(worse) 0.11) but behind on 2026-27 and the pool. `claude/card-legs-history-span-2026-11-17.md`.

**Files.** `tools/card_legs_history.py` (`card_season` uses `card_replay.spans` / `build_span`; `nospan` in `cardM7`), `tests/test_card_legs_history_span.py`, `tests/test_card_comp3.py` (source check loosened), `claude/card-legs-history-span-2026-11-17.md`, `claude/card-replay-live-span-2026-11-17.md`, `CLAUDE.md`.

**Not changed.** Any Card rule or `CARD_RULE`; the pool replay; the record; the page.

**Roll back.** `git revert` this merge.

## 2026-11-17-card-book-reread: Which book to write the Card for, re-read (tag pending)

**What changed:** nothing on the site. A dated note re-reading the paired book comparison to 17 Nov.
**Evidence:** Bet365 pays +1.11% a pick over William Hill at the first price (102 paired, p 0.000) and +0.86% at the last (66, p 0.000); Betfair and BetVictor are behind Hill. Best UK price +1.64% a pick, under the 2-point bar for a page statement.
**Files:** `claude/card-book-reread-2026-11-17.md`.
**Not changed:** `CARD_BOOK` (William Hill), the owner's call per CLAUDE.md.
**Roll back:** delete the note.

## 2026-11-17-card-seasons-third: Card over three past seasons, asked a third time (tag pending)

**What changed:** nothing on the page. A dated note points to the 9 and 10 Nov replays, which already answer the ask.

**Evidence:** none new; the sandbox cannot fetch football-data. Existing: under-market cut 70.9-73.3% landed v 68.0-69.1% quoted over 2022-25, no gap band positive in every season, opposition 9+ holds.

**Files:** `claude/card-seasons-third-ask-2026-11-17.md`, this entry.

**Not changed:** the Card's rule, any constant, the tool.

**Roll back:** `git revert` the merge; docs only.

## 2026-11-17-opp-under6: Card legs with the opposition under 6, read against the seasons (tag pending)

**What changed:** nothing on the page. A dated note records the check the planner asked for.

**Evidence:** football-data legs (model 60%+, 1.15-1.90): opposition under 6 landed 64.5% v 64.4% modelled on 76 legs in 2025-26 (-4.3% at price) and 88.2% on 17 in 2026-27 (+29.8%). The live 18 of 21 matches the current season, not last season's; pooled 93 legs, +2.7%, signs opposite by season. Gates not met, no rule change; the Card does not read the opposition since rule 13. `claude/card-opp-under6-live-2026-11-17.md`.

**Files:** `claude/card-opp-under6-live-2026-11-17.md`, this entry.

**Not changed:** the Card's rule, `CARD_OPP_MIN`, `CARD_MODEL_OPP_MIN`, any model constant.

**Roll back:** `git revert` the merge; docs only.

## 2026-11-17-band-50-55: Football 50-55% band over its quote: tested, rejected (tag pending)

**What changed:** nothing on the site. A note only.

**Evidence:** live 50-55% calls landed 408 of 721 v 379.0 quoted (z +2.2), spread across wider leagues, other leagues, Celtic's Law and not (all z +1.4 to +1.7). On the replay the fit season is on quote (52.3% v 52.4%, n 815); the check season lands over quote in every band (50-55: 56.5% v 52.3%, n 308), so it is a season-wide shift. A 50-55 bend fitted on 2025-26 and checked on 2026-27 (2,320): gain -0.0003, p(worse) 0.94. Fails rule 3.

**Files:** `claude/band-50-55-2026-11-17.md`.

**Not changed:** `calibration.json`, the engine.

**Roll back:** delete the note.

## 2026-11-17-card-return-locate: The Card's 0.831 return located, no rule change (tag pending)

**What changed:** a note only (`claude/card-return-locate-2026-11-17.md`). Nothing a reader sees.
**Evidence:** landing is on quote (9 of 27 v 9.7 expected). Flat return a leg: football +0.074 (43), NBA +0.129 (33), tennis -0.19 (14, all under today's 85% floor), college basketball -0.50 (3, off the Card), rugby -0.16 (6). Weekday and price-band slices are noise on under 50 legs.
**Files:** `claude/card-return-locate-2026-11-17.md`, `RELEASES.md`.
**Not changed:** every Card constant, `tools/card_replay.py`.
**Roll back:** `git revert` the merge.

## 2026-11-17-replay-span: the Card replay's live builds two-day groups, like the page (tag pending)

**For a reader.** Nothing on the page. The nightly Card review's `live` row is the Card the page builds again: since 12 Nov the page has made two-day groups (`CARD_SPAN`), but the replay built `live` day by day and ran the two-day Card as a variant (`span2`), so every variant was paired against a Card nobody runs.

**Evidence.** Pool, 29 Oct to 18 Nov: live 25 groups, 11 won, +0.5% becomes 26, 13, +15.0% (the old `span2`). `m7under5` (+0.50 a day, p(worse) 0.00 before) and `tennis75` drop off the watch list (-0.17, 0.59 and +0.08, 0.48); `pay3` stays ahead on 88 legs; `rule12` reads -1.09 a day v live (p(worse) 0.90). `claude/card-replay-live-span-2026-11-17.md`.

**Files.** `tools/card_replay.py` (`spans`, `build_span` under a variant's constants, `nospan` replaces `span2`), `tests/test_card_replay_live_span.py`, `groupings.py` (comment only), `claude/card-replay-live-span-2026-11-17.md`, `CLAUDE.md`.

**Not changed.** Any Card rule or `CARD_RULE`; the football-data replay (still day by day); the record; the page.

**Roll back.** `git revert` this merge.

## 2026-11-17-6: a half-time score is looked up again when its result is corrected (tag pending)

**For a reader:** nothing visible. The QA follow-up on 17 Nov found the half-time backfill working (12,355 football fixtures kept, August and September still filling at 25 days a build) and one entry disagreeing with the record: Quindio v Real Cartagena was kept while both sources had it 0-1, and the result was later corrected to 0-2. `periods.py` never looked at a kept entry again. Now an entry whose full time no longer matches the graded result is dropped and looked up afresh; it comes back only when the day file agrees.

**Files:** `periods.py`, `tests/test_data_capture.py`.

**Roll back:** `git revert` the merge commit.

## 2026-11-17-integrity-slim: the Card integrity check no longer crashes on the record's slim legs, reads every staked slip, and the review arrives in the morning (tag pending)

**For a reader.** Nothing on the page. The nightly Card review's integrity check works again and now watches the Daily 2x, List 2x and List long as well as the Card; the review should post in the morning instead of around noon.

**Evidence.** `tools/card_integrity.py` on today's `groupings-record.json` died with `KeyError: 'date'`: the record keeps a slim leg (no date, home, away or id) and the first football leg pending 24h+ (Pistoiese v Coriano, 15 Nov, no result on file) reached `groupings.settle()`, which needs them. The check runs with continue-on-error, so the review would have opened an office-backlog issue for a crash, not a finding. `full_leg` takes the full leg from the day's archive (or the day before, for a two-day group), else the date from the start and the sides from the event: 0 findings, 15 of 15 Card legs since 10 Nov replayable. The no-opposition-price check also asked rule 13 legs for an opposition price rule 13 never reads; it now asks rules 6 and 12 only (`OPP_RULES`). The review's 03:40 UTC cron fired between 10:55 and 12:07 UTC on every day from 9 to 16 Nov; deploy.yml's new `card-review-next` job dispatches it from the first build at or after 03:40 UTC that finds no review issue for the day and none running (the crons stay as backups; `card_review_post` posts one issue a day).

**Files.** `tools/card_integrity.py` (`full_leg`, `staked`, `OPP_RULES`), `.github/workflows/deploy.yml` (`card-review-next`), `tests/test_card_integrity_staked.py`, `tests/test_card_funnel_model.py`, `claude/card-integrity-slim-2026-11-17.md`, `CLAUDE.md`.

**Not changed.** Any Card rule or `CARD_RULE`; the record; the page.

**Roll back.** `git revert` this merge.

## 2026-11-17-rule13-split: rule 13's groups split by what rule 12 would have said (tag pending)

**For a reader.** Nothing on the page. The record now tells apart the Card groups rule 12 would also have built from those holding a pick only rule 13 (the model alone) admits, so the 30 Nov review can see what dropping the bookmaker conditions added, from the live record rather than only the replay.

**Evidence.** None needed: a tally. Every rule 13 leg already carried `rule12Fault`; `grade()` dropped it. The split is empty until the first rule 13 group locks (17 Nov).

**Files.** `groupings.py` (`rule12Fault` and `r12` on graded legs, `card_rule13_split`, `cardRule13Split` in `groupings-record.json`), `tools/card_review_post.py` (`rule13_split_section`), `tests/test_card_rule13_split.py`, `claude/card-rule13-split-2026-11-17.md`, `CLAUDE.md`.

**Not changed.** Any Card rule or `CARD_RULE`; the page.

**Roll back.** `git revert` this merge.

## 2026-11-17-5: Card bookmaker and price timing, by week and hour (#156) (tag pending)

**What changed:** nothing on the site. `tools/price_timing.py` now also reports each UK book against `CARD_BOOK` by week and the move to the start by first-price hour and sport; a dated note records the read.
**Evidence:** `claude/card-book-over-time-2026-11-17.md`. Bet365 pays +1.41% a pick over William Hill at the first price (82 paired football picks, 13 days, p 0.000) and +0.89% at the last, ahead in 3 of 4 weeks (the fourth is one pick); Betfair and BetVictor behind in every week. Timing: settled singles late v first +0.84 points on 200 legs, p 0.29, no clear read; football and NBA none either; the last price sits a median 1.3 h before the start.
**Files:** `tools/price_timing.py`, `tests/test_book_vs.py`, `claude/card-book-over-time-2026-11-17.md`.
**Not changed:** `CARD_BOOK` (William Hill is Douglas's account), `notify.py` push times, any rule.
**Roll back:** `git revert`.

## 2026-11-17-card-rule13: the Card on the model alone, rule 13 (tag pending)

**For a reader.** The Card's picks are now chosen on the model's number alone. Until today a pick also had to be rated by the model at or above the bookmakers' chance (since 11 Nov) and, for football, have the opposition priced 5.0 or longer (since 16 Nov). Both conditions are off, at the owner's instruction (17 Nov 2026: "forget about comparison to bookies... let's just follow the model", then "just drop both of those"). The rule still needs a bookmaker price of 1.15 to 1.90 (so a 2x comes in three to five picks), the model at 60%+, tennis at 85%+, NFL and the college sports off. The rule text on the Bets tab and each group's footer say so from today, and the record tallies rule 13 on its own line.

**Evidence.** None for the change; the record argued against it, and the note says so. On the pool (every sport, first real price, 30 Oct to 17 Nov) rule 13 builds 41 groups on 21 days, 17 won (41%), -4% at a flat stake; rule 12 on the same days 20 groups, 11 won (55%), +34%; paired by day rule 12 +0.79 units a day, p(worse) 0.09. The nearest football-data proxy (`m7under5`) was behind the value-demand Card in all five seasons. The estimate given to Douglas: about 40 to 45% of rule 13 groups won over a month, -5% to -10% on turnover, 90% band roughly -30% to +20%. `claude/card-rule13-model-only-2026-11-17.md`.

**Files.** `groupings.py` (`CARD_MODEL_EDGE` None switches the value demand off, `CARD_MODEL_OPP_MIN` {}, `CARD_RULE` 13; `RULE12_PATCH`, `fault_under`, and each Card leg carries `rule12Fault`, rule 12's verdict, so the review can split the groups without a replay; `rules.card.modelEdge` / `modelOppMin` for the page), `index.html` (the rule copy reads them), `tools/card_replay.py` and `tools/card_legs_history.py` (`rule12` and `m7value` variants), `tools/card_funnel.py` (the `no-value` relief joins only while the demand is live, `MODEL_VALUE_RELIEF`), tests (`tests/test_card_rule13.py` new; four Card tests re-pinned to rule 13, the rule 12 behaviour kept under a patch).

**Not changed.** The Daily 2x (the every-day slip, shipped earlier today), the List card, the slip, the Edge flag, the price band, the model's 60% floor, the tennis floor, the sports off, the context veto, two-day groups, `COMP_MAX`. No model input.

**Roll back.** `git revert` this merge, or set `CARD_MODEL_EDGE = 0.0` and `CARD_MODEL_OPP_MIN = {"football": 5.0}` with `CARD_RULE` 14.

## 2026-11-17-daily-2x-rebuild: a short Daily 2x is rebuilt until it starts (tag pending)

**For a reader.** A later day's 2x built before its prices are in (19 and 20 Nov were 1.64 and 1.44) now rebuilds on every build until it reaches 2x or starts; a slip at 2x is held as first built. **Files.** `groupings.py` (`build_list_card`), `tests/test_daily_2x.py`. **Roll back.** `git revert` this merge.

## 2026-11-17-daily-2x: the Daily 2x, one slip every day, and its tracker (tag pending)

**For a reader.** The Bets tab now opens with **Today's 2x**: one slip a day, the model's strongest picks priced 1.10 or more, added until it pays 2x. Picks come from the Daily List first, then the reserve, then the day's strongest football (model 65%+), then other sports (65%+); college sports are left out. As many picks as it takes, up to eight. A day that cannot reach 2x still gets its strongest slip, marked short. Under it, a tracker: a tile a day with each pick as a dot (green landed, red lost, grey to come), the slip's price and result, and the running tally (slips won v expected, return, picks landed), with what the replay taught.

**Evidence.** Replayed on the results ledger, 3 Oct to 16 Nov, list and reserve picks with a real price, college basketball out: strongest first at 1.10+, 28 slips in 33 days, 14 won (50%), +22% at the recorded price, 3.9 picks a slip. At any price 16 of 28 (57%, +40%), but Douglas rules out picks under 1.10. Ordering the same picks by shortest price instead: 10 of 28 (36%, -22%). Above 1.15 every price band of list and reserve picks landed 3 to 6 points under its price (college basketball 15 to 20 under), so the slip rests on the model's ordering, not on value. 28 slips is a small sample. Douglas, 17 Nov: "we have to have one card every day ... aiming for above a 2x is our benchmark".

**Files.** `groupings.py` (`daily_group`, `DAILY_*`, `is_daily`, `cardDaily`, `reserve` and `tier` carried on legs), `index.html` (`dailySection`, `dailyTracker`, CSS), `tests/test_daily_2x.py`, `tests/test_list_card.py`, `claude/daily-2x-2026-11-17.md`, `CLAUDE.md`.

**Not changed.** The rule 12 Card, the List 2x and List long, the slip, every model and the Daily List.

**Roll back.** `git revert` this merge; the Daily 2x stops being built and its archived slips stay graded in `groupings-record.json`.
## 2026-11-17-legs4: Leg properties, fourth look (tag pending)

**What changed:** nothing on the site. A dated note records a fourth leg-property look: no rule shipped.

**Evidence:** pool of 22 days, 74 settled real-priced football 65%+ legs landed 56 v 50.7 expected; tested-rate cut 31/47 v 25/27, far under the 250 legs Rule 3 needs. Earlier football-data scans stand.

**Files:** `claude/leg-property-fourth-2026-11-17.md`, `claude/odds-groupings.md`, `RELEASES.md`.

**Not changed:** `groupings.py`, any model or constant.

**Roll back:** `git revert` the merge.

## 2026-11-17-edge-retest: Edge over the price, fourth run, no edge (tag pending)

**What changed:** nothing on the site. A dated note records the fourth run of the value test on a check season that has doubled.

**Evidence:** football-data.co.uk prices, fit 2025-26 (12,510 legs), check 2026-27 (3,576). Legs the model rates 2 / 4 / 6 points above the bookmakers' fair chance land -1.8 / -2.1 / -1.5 below it on fit and -1.8 / -1.9 / -1.1 on check (bootstrap p(<=0) 0.76 to 1.00); no cut by price, side or band is positive on both seasons; the opposite control lands +2.3 / +2.8 above. Gates failed.

**Files:** `claude/odds-edge-retest-2026-11-17.md`, `claude/odds-groupings.md`, `RELEASES.md`.

**Not changed:** `MAX_ABOVE_BOOK`, the Card and group rules, every model.

**Roll back:** `git revert` the merge; docs only.

## 2026-11-17-tennis-surface-4: tennis surface, fourth check, note only (tag pending)

**What changed:** nothing a reader sees. A dated note records that the surface idea has no new evidence to test.
**Evidence:** Sackmann 2026 files 404 and tennis-data.co.uk 403 again on 17 Nov; ESPN has no surface field; the hand-kept map was rejected on 13 Oct (WTA +0.0024 log loss, p(worse) 0.88; ATP +0.0031, 0.95).
**Files:** `claude/tennis-surface-fourth-check-2026-11-17.md`.
**Not changed:** `build_tennis.py`, ratings, the Daily List rule.
**Roll back:** delete the note.

## 2026-11-17-4: the empty-day fillers (#155) closed as overtaken (tag pending)

**What changed:** nothing on the site. A dated note records that the filler test was done on 10 Nov and the filler switched off by the owner on 11 Nov.
**Evidence:** `fillopp7` and `fillshort` fill no empty day; `fillrule5` 4 pool groups, 2 won v 1.28 expected (12 legs, far under the 100-leg gate); `fillwide` pool 2 of 12 v 4.14 expected; live `cardWide` 1 of 3, 4.18 back on 5 units.
**Files:** `claude/card-fillers-closed-2026-11-17.md`.
**Not changed:** `CARD_FILLER` stays False, `CARD_RULE` 12.
**Roll back:** delete the note.

## 2026-11-17-3: no links to the code; Analysis opens with About the Sports Almanac

**What changed:** every link from the site to the code repository and to HQ is gone (the HQ tab, the Analysis footer, the release-log link), and README.md is no longer published with the site (Douglas: the code is not for the public). Analysis now opens with **About the Sports Almanac**: what the site does, the sports and how a call is made, how it is checked, a plain risk warning (the model is in beta), and the Daily List, the Card and Scale each with its risk level and the last seven days and today as day tiles. The rest of the page is brought up to date (API-Football and prices named correctly, the college basketball early-season K and Behind .500 mark, no references to code files).
**Files:** `analysis.html`, `index.html`, `groupings.py` (the published groupings file read from sportsalmanac.bet), `.github/workflows/deploy.yml`.
**Not changed:** the repository's own visibility (Douglas's decision; see the session note).
**Roll back:** `git revert`.
## 2026-11-17-2: The List card in the open, with a List long for thin days

**What changed:** Douglas: "at least one or two cards a day just made up of the daily list picks ... just having no cards is awful", and a review of what wins on the list. The List 2x comes out of its "on paper" fold onto the Bets tab as **The List card**, and gains a second kind: when the 2x cannot be made from legs at 1.15+ in six, the **List long** takes the list's picks at any price, up to ten, to 2x. College sports are left out. Each group shows a Tested chance (the ledger's landed rates by sport and price band) beside the model's. The record keeps the two kinds on their own lines (`cardList`, `cardListLong`).

**Evidence:** `claude/list-card-2026-11-17.md`. The pattern review of 592 graded list picks: landed as quoted in every cut (sport, side, band, price, family, weekday, window, model v price); no cut beats the price. On the ledger's 23 priced days a List 2x could be built on 5 (5 won), a List long on 7 (3 won). Tests in `tests/test_list_card.py` (11); suite and `nametest.py` pass; Bets tab rendered at 1280px and 400px.

**Files:** `groupings.py`, `index.html`, `tests/test_list_card.py`, `claude/list-card-2026-11-17.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Card, the slip, the Daily List, any model.

**Roll back:** `git revert` the merge commit; or `LIST_KINDS = [("List 2x", 2.0, 1.15, 6)]` to drop the long kind alone.

## 2026-11-17-signup-push: a phone push for every Mailer sign-up (tag pending)

**What changed:** a new Mailer sign-up sends Douglas a push through ntfy: "New Mailer sign-up", the emails chosen and how many are on the list. The reader's address is never in the push. It is set up in the Supabase database (Inbox Innovation project): the trigger `almanac_signup_push` on `almanac.subscribers`, the function `almanac.notify_signup()` (security definer, not callable by the API roles), `pg_net`, and the topic in Vault as `almanac_ntfy_topic`. The site's code is unchanged.

**Evidence:** a test push to the topic returned 200 from ntfy.

**Not changed:** the form, `almanac_subscribe`, the site.

**Roll back:** `drop trigger almanac_signup_push on almanac.subscribers;` in the Supabase SQL editor.

## 2026-11-17-1: the Card funnel reads rule 12's opposition floor (tag pending)

**What changed:** the nightly Card review's funnel had no key for rule 12's two opposition messages, so a football leg with no opposition price vanished from the table, one priced under 5.0 counted as "other", and the missing-price count dropped every football leg (46 to 3). The funnel now has an `opposition` column and relief, an unpriced leg stands in at the floor, and a missing opposition price is taken from the football archive as the replay does.

**Evidence:** pool 6 to 17 Nov under rule 12: football clear 32 to 44, 31 opposition faults shown (was 0), price gaps 3 to 63 (38 football on started days). The opposition floor alone costs one group in fifteen days (13 v 12). `claude/card-funnel-rule12-2026-11-17.md`.

**Files:** `tools/card_funnel.py`, `tests/test_card_funnel_model.py`, `claude/card-funnel-rule12-2026-11-17.md`, `CLAUDE.md`.

**Not changed:** every Card rule; the replay; the page.

**Roll back:** `git revert` the merge.

## 2026-11-16-25: the Mailer is a tab like the others (tag pending)

**What changed:** the Mailer opens inside the main page with the same cover, stat panel and tab bar as the Daily List; only the content below the bar changes (`#mailer` section and a `mailer` view in `index.html`). Douglas: "I want the same hero section, banners, navs ... just when you click on mailer, it's just the content below that changes." The separate "Almanac Mailer" cover is gone. `mailer.html` now only forwards to `./#mailer` (it keeps the GTM and GA tags), so old links still work, and Analysis links to `./#mailer`.

**Evidence:** checked in Chrome at 1280px and 400px. `mailer.html` lands on `/#mailer` with no script errors, and switching to the Daily List hides the form. The tag tests pass.

**Files:** `index.html`, `mailer.html`, `analysis.html`.

**Not changed:** the form, its Supabase function, the copy and the consent wording.

**Roll back:** `git revert` the merge.

## 2026-11-16-24: the Card needs the opposition at 4/1 or longer, and the List 2x runs on paper (tag pending)

**What changed:** a football pick on the Card now needs its opponent priced 5.0 (4/1) or longer (`groupings.CARD_MODEL_OPP_MIN` `{"football": 5.0}`, `CARD_RULE` 12). Douglas asked "what can you do here to actually win" after a run of lost 2x groups, and said yes to this. Beside the Card, a new **List 2x** runs on paper every day: the Daily List's own picks priced 1.15+, the model's strongest first, added until the slip pays 2x (`build_list_card`, `list_group`). It is never staked or pushed, and is graded apart as `cardList` in `groupings-record.json`. The Bets tab shows it in an "On paper: the List 2x" fold, with its record under "More numbers".

**Evidence:** the condition is the pre-registered `m7opp5`, set live before its 100-pool-leg gate as Douglas's call. Across five football-data seasons it was +17.5% against +9.6% pooled (450 legs, p(worse) 0.014), ahead in all five. On the pool (`tools/card_replay.py`, 16 Nov) the new live Card shows 20 groups, 11 won, +34%. Rule 11 without the condition (`m7noopp`) shows 23 groups, 9 won, −4%, with paired p(worse) 1.00 for rule 11. The List 2x has no evidence behind it yet. That is why it runs on paper: list picks land 87.5% but returned −1.6% a pick at their prices on the results ledger.

**Files:** `groupings.py`, `index.html`, `tools/card_replay.py` (`m7noopp`), `tools/card_legs_history.py`, `tools/card_integrity.py` (`needs_opp` reads rule 12), `tests/test_list_card.py`, `tests/test_card_m7opp.py`, `tests/test_card_model_rule.py`, `tests/test_card_funnel_model.py`, `tests/test_context_review.py`, `claude/card-opp5-list2x-2026-11-16.md`, `CLAUDE.md`.

**Not changed:** the Card's other conditions, its stakes and the 2x-only build. The Daily List is unchanged and still takes no bookmaker input. NBA and tennis Card picks carry no opposition condition.

**Roll back:** `CARD_MODEL_OPP_MIN = {}` and `CARD_RULE` 11 for the condition. Remove the `build_list_card` line in `build()` for the List 2x. Or `git revert` the merge.

## 2026-11-16-23: college basketball reads this season sooner, and marks sides behind .500

**What changed:** a college basketball team's first six games of a season now move its rating half as far again (`sports.EARLY_K`), so a side that has changed over the summer is found sooner. College basketball rows in November and December whose picked side has a losing record (3+ games) carry a "Behind .500" mark. UMBC v Iona tonight reads 77% instead of 81%, marked.
**Evidence:** replay fit 2024-25, check 2025-26 (5,814 games): log loss 0.5499 to 0.5475, p(worse) 0.00, 65%+ gap 0.022 to 0.020; a heavier summer regression was worse. Behind .500 picks landed 75% v 80% quoted on the replay, under in both seasons. `claude/ncaab-early-k-2026-11-16.md`, `tools/ncaab_carry_eval.py`.
**Files:** `sports.py`, `sports.json` (ncaab refit), `index.html`, `tests/test_sports_early_k.py`, `tools/ncaab_carry_eval.py`, `claude/ncaab-early-k-2026-11-16.md`.
**Not changed:** other sports; the Daily List bar (85%); k, home advantage and summer regression (pinned at live).
**Roll back:** `git revert`.

## 2026-11-16-22: a later Card review run refreshes the day's issue (tag pending)

**What changed:** the nightly Card review posted once a day and every later run posted nothing, so today's issue (#342, 12:02 UTC) said "no paired season read on file yet" although tune.yml had committed the football-data paired read at 13:16 and the review ran again at 19:41. A later run now rewrites the day's issue body when its files say something new, with a closing "Refreshed" line; it never opens a second review or a second integrity issue. The gate table also says "identical to live on the pool" (was "behind on the pool") and names an identical football-data season as identical.
**Evidence:** the gate table rebuilt locally on today's files: no rule 7 variant passes; `m7opp5` is ahead on the pool (+0.79 a day, p(worse) 0.00, 33 legs of 100) and on 2026-27 (+0.67, 0.00) but 2025-26 misses at p(worse) 0.323; `m7under5`, `m7short`, `m7legs2`, `pay15` are behind live on football-data. No Card rule changed.
**Files:** `tools/card_review_post.py` (`review_body`, `posted_issue`, `refreshed`, `unrefreshed`), `tests/test_card_review_post.py` (four tests).
**Roll back:** `git revert`.

## 2026-11-16-21: paragraph copy runs the full width

**What changed:** intro and explainer copy (the Daily List's lede, notes, prose, footers, empty states) now fills the width of its container on desktop instead of stopping at about half (Douglas). Every page.
**Files:** `index.html`, `analysis.html`, `mailer.html`.
**Roll back:** `git revert`.

## 2026-11-16-20: ribbon line offsets corrected

**What changed:** the ribbon's third and fourth lines sit at 0 and +12px (Douglas's correction; the last line was clipped at -12px). Same on the Mailer page.
**Files:** `index.html`, `mailer.html`.
**Roll back:** `git revert`.

## 2026-11-16-19: ribbon line spacing and offsets set by hand

**What changed:** the ribbon's quote lines sit closer (line height 1) and each line's offset along the band is Douglas's own (-25, -12, -1, -12px). Same on the Mailer page.
**Files:** `index.html`, `mailer.html`.
**Roll back:** `git revert`.

## 2026-11-16-18: the ribbon's quote shortened and filled to the edges

**What changed:** the ribbon reads "Wait a minute, Doc. Are you telling me that you built a time machine?" on four larger lines that run almost edge to edge of the band, a letter or two clipped (Douglas). The red panel now clips the band, so it looks the same behind the black rows at every width. Same on the Mailer page.
**Evidence:** checked on the live page at 1178px and 918px covers.
**Files:** `index.html`, `mailer.html`.
**Roll back:** `git revert`.

## 2026-11-16-17: the ribbon quotes Marty, centred

**What changed:** the corner ribbon now reads "Wait a minute, Doc. Are you telling me that you built a time machine... out of a DeLorean?" on five lines, each centred on the visible part of the band, so the whole line reads (Douglas). Same on the Mailer page.
**Evidence:** checked on the live page at 1178px and 918px covers.
**Files:** `index.html`, `mailer.html`.
**Roll back:** `git revert`.

## 2026-11-16-16: the Doc Brown ribbon made thick

**What changed:** the 45-degree ribbon is thick again and sits against the right edge of the red panel, the quote on three lines and mostly readable (Douglas). Same on the Mailer page.
**Evidence:** checked on the live page at 1178px and 918px covers.
**Files:** `index.html`, `mailer.html`.
**Roll back:** `git revert`.

## 2026-11-16-15: Google Analytics connected directly, tabs reported to it (tag pending)

**For a reader:** nothing visible. Google Analytics showed "No data received" for the Sports Almanac stream: the Tag Manager container on the site holds no Google tag, so nothing was passed on. GA4 (`G-35788M25WE`) now loads straight after Tag Manager on every page (main page, Analysis, the Mailer), and every tab opened is sent to it as a `tab_view` event with `tab`, `tab_name` and `page_path`, so no Tag Manager setup is needed. Do not also add a Google tag for G-35788M25WE inside Tag Manager: every view would count twice.

**Evidence:** headless browser on all three pages: GA configured on each, three tab events for three tabs on the main page, no page errors.

**Files:** `tools/tag_pages.py` (`GA_ID`, `GA_TAG`, `add_tag` adds whichever is missing), `index.html`, `analysis.html`, `mailer.html`, `tests/test_tag_pages.py`, `CLAUDE.md`.

**Not changed:** no consent banner (see 2026-11-16-9).

**Roll back:** `git revert` the merge commit.

## 2026-11-16-14: the Doc Brown flash as a quiet 45-degree ribbon

**What changed:** the corner flash is a thin yellow ribbon at 45 degrees that starts under the 2026 band and runs under the tab bar, so only its middle crosses the red panel; the quote is centred on it and mostly hidden, a nod rather than a feature (Douglas). Replaces the tape strip. Same on the Mailer page.
**Evidence:** checked on the live page at 1178px and 918px covers.
**Files:** `index.html`, `mailer.html`.
**Roll back:** `git revert`.

## 2026-11-16-13: the Card replay reads the opposition's price on the pool's early legs (tag pending)

**What changed:** the pool archive kept no opposition price for football legs before 6 Nov, so 382 priced football legs from 30 Oct to 9 Nov faulted in every replay variant with an opposition condition (`rule6` and its family, `m7opp5`, `m7opp9`) for missing data, not for their rule. `tools/card_replay.py` now takes the opposition's and the draw's average price for those legs from the football archive (`predictions/`, rows published before kick-off, `archive_opp`), marked `oppFrom: "archive"`; the nightly Card review counts them apart from the legs left out.
**Evidence:** on the 246 legs carrying both prices the archive's agrees with the pool's on the 5.0 and 9.0 lines 91% of the time (median difference 0). In the review's window, `m7opp5` goes from 4 groups on 12 legs (-42%, p(worse) 0.24) to 11 groups on 33 legs (+2%, p(worse) 0.00); live is unchanged. Two new tests; nametest and the suite pass. `claude/card-replay-archive-opp-2026-11-16.md`.
**Not changed:** no Card rule. `m7opp5` is still under the gate's 100 pool legs; the funnel is untouched.
**Files:** `tools/card_replay.py`, `tools/card_review_post.py`, `tests/test_card_pool_replay.py`, `claude/card-replay-archive-opp-2026-11-16.md`, `CLAUDE.md`.
**Roll back:** `git revert`.

## 2026-11-16-12: the Mailer page and tab, sign-ups into Supabase, and the flash as tape

**What changed:** a Mailer tab closes the sections row on every page and opens `mailer.html`, the sign-up for the Daily List email: email, the three emails (Daily List, Scale, Sunday Record), an 18+ and consent tick, and a hidden spam trap. Sign-ups go to Supabase: the Inbox Innovation project (the free plan allows two projects and the other one is personal finance), in its own `almanac` schema that the API does not expose, written only through `almanac_subscribe` (security definer; the publishable key can call it and read nothing). Rows start `pending` for double opt-in; `almanac_confirm`, `almanac_get_preferences` and `almanac_update_preferences` are ready for the confirm and preferences links once sending is set up. The corner flash is now a strip of tape with torn ends and a soft shadow, the quote centred on it, overhanging the panel.
**Evidence:** the functions tested as the anon role (sign-up, repeat sign-up, spam trap; the anon role has no access to the schema or to Inbox Innovation's tables). The page rendered at 1440px and 400px; the tape checked on the live page at 1178px and 918px covers.
**Not changed:** nothing is emailed yet: the confirmation and daily sends need Resend and the sending domain.
**Files:** `mailer.html` (new), `index.html`, `analysis.html`, `.github/workflows/deploy.yml` (publishes `mailer.html`).
**Roll back:** `git revert`; the Supabase objects are `almanac.*` and `public.almanac_*`.

## 2026-11-16-11: the Doc Brown flash on narrower screens (tag pending)

**Shipped in:** ce8d6de (first logged as 2026-11-16-6, an id another session had already used the same afternoon)

**What changed:** between 701px and 1219px wide the quote on the corner flash is smaller and sits further into the corner, so it no longer runs over the List record cell's "534 of 616 landed".
**Evidence:** checked in a browser on the live page with a 918px cover: the band now starts right of the cell's text.
**Files:** `index.html`.
**Roll back:** `git revert`.

## 2026-11-16-10: every tab opened is sent to Google Tag Manager (tag pending)

**For a reader:** nothing visible. Tabs change without loading a page, so Tag Manager saw only the first page view. Every tab opened now pushes a `tab_view` event to the dataLayer, the tab a visitor lands on included, with the tab's key (`tab`, e.g. `today`, `sport:nba`), its label (`tab_name`, e.g. "Bets") and a path (`page_path`, e.g. `/#today`). To report it, the GTM container needs a Custom Event trigger on `tab_view` firing a GA4 event or page-view tag that reads those three dataLayer variables.

**Evidence:** checked in a headless browser on `index.html`: opening the page then Bets, Scale, Starred and Football gave five events in order, no page errors.

**Files:** `index.html` (the view switch), `tests/test_tag_pages.py`, `CLAUDE.md`.

**Roll back:** `git revert` the merge commit.

## 2026-11-16-9: Google Tag Manager on every page (tag pending)

**For a reader:** nothing visible. Douglas's Google Tag Manager container (`GTM-WP7C2F6B`) now loads on every page of the site, the main page and Almanac Analysis, straight after `<head>`, as he supplied it. Future pages get it too: a test fails CI on any page in the repo without it, and the deploy adds it to any published page that still lacks it (with a warning naming the page). The Cloudflare beacon is unchanged.

**Files:** `index.html`, `analysis.html`, `tools/tag_pages.py` (new), `tests/test_tag_pages.py` (new), `.github/workflows/deploy.yml` (the "Google Tag Manager on every page" step), `CLAUDE.md`.

**Not changed:** no consent banner. If the container fires Google Analytics or ad tags that set cookies, UK rules (PECR) expect consent first; Cloudflare's beacon sets none.

**Roll back:** `git revert` the merge commit.

## 2026-11-16-8: football half-time scores filled in for the season so far (tag pending)

**For a reader:** nothing on the page yet. Half-time scores were being kept only from 16 Nov: a finished day's API-Football file is never asked for again, and every day before 16 Nov had been cached without its half time. A finished day file without one is now asked for once more on scheduled builds, up to 25 a build and 180 days back (about 170 calls once, spread over a few builds; today's builds left 6,500 of the 7,500 a day unused), and `periods.py` looks back 180 days instead of 10. A graded fixture tried against a day with half times and not matched is noted in `periods/missed.json` and not tried again, so the matching stays quick.

**Evidence:** the 13:57 deploy's log: "periods: no cached day files with half-time scores yet". Matching 6,000 fixtures from scratch takes about a minute, hence the missed list. Found by the QA review (`claude/qa-review-2026-11-16.md`).

**Files:** `sources.py` (`_ht_refetch`, `HT_BACK_DAYS`, `HT_REFETCH_MAX`), `periods.py` (`LOOKBACK`, `MISSED`), `tests/test_data_capture.py`, `CLAUDE.md`, `claude/data-inventory-2026-11-16.md`.

**Not changed:** push-triggered builds (`AF_FRUGAL`) never refetch; nothing reads the half times yet.

**Roll back:** `git revert` the merge commit, or `HT_REFETCH_MAX = 0`.

## 2026-11-16-6: a frozen Scale group keeps every leg it was built from (tag pending)

**For a reader:** today's Scale fourfold (frozen at 13:00) showed a leg, Cuba v Grenada, that had dropped off the day's picks, so it could never settle and would have sat "pending" for good. Under rule 4 a group's football legs can come from outside the day's picks; when a later build's groups stopped using such a leg, it was no longer kept, while the frozen group still named it. A frozen group's legs now always stay on file, and one already lost is taken back from the day's candidates, so today's file repairs itself on the next build.

**Evidence:** `scale-archive/2026-11-16.json` (fourfold leg `f|concacaf.nations|2026-11-16|Cuba|Grenada` not in `picks`); `scale.py` run on the committed files with the fix puts it back. Found by the QA review (`claude/qa-review-2026-11-16.md`).

**Files:** `scale.py` (`merge_day`, `pool`), `tests/test_scale.py` (two tests).

**Not changed:** the Scale rule, the groups' selection, any number on the record.

**Roll back:** `git revert` the merge commit.
## 2026-11-16-5: two-row navigation, Doc Brown on the flash, and a responsible-gambling footer (tag pending)

**What changed:** the tab bar under the cover is now two rows (Douglas chose option 4 of the navigation mock-ups). Row one holds the Almanac's sections, Daily List, Bets, Scale, Starred, How it went, Analysis and HQ, in italic Anton on black like the 2026 band, split by slashes, the open one in white with a yellow underline. Row two is a yellow strip holding the sports, the open one reversed out in black. Both rows centre on desktop and scroll sideways on a phone; the bar stays sticky. The corner flash on the red stat panel now reads "Roads? Where we're going, we don't need roads." on a wider band at a shallower angle, so the whole line sits inside the panel. Every page (the Almanac and Analysis) ends with an 18+ "Keep it a game" banner: GamCare, BeGambleAware and GamStop.
**Evidence:** checked in a browser against the live data at 1180px and at 400px: every tab opens its board (Football tested), hidden sports stay hidden, the quote clears the last stat cell, the phone rows scroll.
**Not changed:** what any tab shows, the cover above the bar, the click handling (`#views` and each button's `data-view` are as before). Mailer has no page yet, so it has no tab.
**Files:** `index.html`, `analysis.html`.
**Roll back:** `git revert`.

## 2026-11-16-4: the site moves to sportsalmanac.bet (tag pending)

**What changed:** the site is served at https://sportsalmanac.bet/ (registered at Hostinger; four GitHub Pages A records and a `www` CNAME to `douglasbakeronline.github.io`; the custom domain set in Settings > Pages). The links the build writes into the day list, notifications, the free-prices user agent and the Julius export now point there. The old `douglasbakeronline.github.io/footyalmanac/` address redirects to the new one, so shared links keep working.
**Not changed:** `groupings.PUBLISHED` still reads the published `groupings.json` through the github.io address, which follows the redirect; HQ stays at github.io. Cloudflare Web Analytics needs nothing: the beacon reports from any host.
**Files:** `daylist.py`, `notify.py`, `free_prices.py`, `tools/julius_export.py`.
**Roll back:** `git revert`; to drop the domain, Remove it under Settings > Pages.

## 2026-11-16-7: every release tagged, release ids kept unique (tag pending)

**For a reader:** nothing on the page. Three releases of 15 Nov (the college Away / Neutral marks, Scale at a glance's ten a day, the FIFA dateless overview) shared their ids with other entries, so the tagger skipped them and they had no tag to roll back to. They are renumbered 2026-11-15-24 to -26, each naming the commit that shipped it (`**Shipped in:**`), and `tools/release_tags.py` tags such an entry on that commit rather than on the renumbering. Seven more of 15-16 Nov had word ids (`2026-11-16-comp3`, `2026-11-15-span-held` and five others) and were skipped as "no id"; the tagger now reads a word id, so they are tagged on their own merges. A test now fails CI when any release id from 14 Nov on is used twice. Older duplicate ids (October, 2026-11-10) stay as they are: their tags were made by hand or by the office long ago.

**Evidence:** `tools/release_tags.py` lists duplicate ids as skipped; `git ls-remote --tags` had no tag for the three. Found by the QA review (`claude/qa-review-2026-11-16.md`).

**Files:** `RELEASES.md`, `tools/release_tags.py` (`shipped_in`, `HEADER`), `CLAUDE.md` (release step 3), `tests/test_release_tags.py`.

**Roll back:** `git revert` the merge commit; tags already made stay.

## 2026-11-16-3: half-time and quarter scores, bookmaker lines and the model's rating gap kept for every sport (tag pending)

**What changed:** more of every game is now kept for later analysis, at no extra API cost. Football: the half-time score of every graded fixture (`periods/`, from the API-Football day sweep already made) and the bookmakers' extra lines for our fixtures (Asian handicap, handicap result, half-time/full-time, half winners, first-half goals, team totals, win both halves, clean sheets; average and William Hill, `x` in the markets archive). NBA, NFL, rugby, college sports, baseball, WNBA: points by period for every final game and ESPN's line (spread, total, money lines) in `history-sports/`, and on each prediction the rating gap it rests on (`eloDiff`) and the line at the time. A data inventory lists what is kept and what is not. Douglas: "we need to make sure we get to the level where everything is captured."
**Evidence:** the repository is 88 MB on GitHub with full history; git already compresses each file, so the daily files are left as they are. Nothing new is loaded by the page.
**Files:** `periods.py` (new), `sources.py` (`_compact` / `_expand` keep the half time), `sports.py` (`_periods`, `line_of`, `_game`, `eloDiff`), `markets.py` (`EXTRA_BETS`, `x`, `ODDS_VERSION` 2), `.github/workflows/deploy.yml` (runs `periods.py`, commits `periods/`), `tests/test_data_capture.py`, `tests/test_scale.py` (wiring), `claude/data-inventory-2026-11-16.md`, CLAUDE.md.
**Not changed:** any model, pick, list, Card or Scale rule; anything on the page.
**Roll back:** `git revert`. Old day files and archives read as before (the new fields are optional).

## 2026-11-16-2: every scale bet tracked across every sport (tag pending)

**What changed:** the Scale tab has a new table, **Every scale bet**: for each sport, every way of scaling a winner the final score can settle (football's goals, to-nil and margin bets; tennis straight sets and games handicaps; each sport's points-handicap ladder), how often each landed by confidence band, for Daily List picks and over the last 28 days, with the price it needs. It updates on every build. Douglas: "can we track all of these across all sports please?"
**Evidence:** first read on the whole record: football at 85%+ win by 2+ 82%, win and over 2.5 74%, win and both score 31%; tennis at 85%+ by 4+ games 84% against straight sets 78%; college basketball at 85%+ by 10+ 84%.
**Files:** `scale_ladder.py` (new), `scale.py` (`ladder` in scale.json), `index.html` (`scLadder`), `tests/test_scale_ladder.py`, `claude/scale-every-bet-2026-11-16.md`, CLAUDE.md.
**Not changed:** the Scale tab's own bets, picks and groups; any model; the record.
**Roll back:** `git revert`.

## 2026-11-16-briefing-on-the-hour: chained briefings dispatched on the slot's hour (tag pending)

**What changed:** the briefing chain now dispatches the build at the slot's hour (07:00, 11:00, 16:00, 21:00 UK) instead of ten minutes after, so a chained push should land about five minutes after its hour. The nightly Card review's briefing table drops the stale "backup cron" advice and adds a line for the chain's own days from 17 Nov.

**Evidence:** lunch on 16 Nov was the first chained slot: woke 11:10, dispatched 11:15, pushed 11:19:45, 19 minutes late (74 and 84 on 14 and 15 Nov). Dispatch to push took under five minutes, so most of the delay was the grace, which is there for the cron watchdog, not the chain. `claude/briefing-chain-2026-11-16.md`.

**Files:** `tools/briefing_watch.py` (`WAIT_GRACE_MIN`, `grace` on `decide` and `next_wait`), `tools/card_review_post.py` (`CHAIN_FROM`, `briefing_section`), `tests/test_briefing_watch.py`, `tests/test_briefing_log.py`, `claude/briefing-chain-2026-11-16.md`, `CLAUDE.md`.

**Not changed:** `notify.py`, the slots, any workflow file, the cron watchdog's 10-minute grace, any Card rule.

**Roll back:** `git revert` the merge commit, or set `WAIT_GRACE_MIN = 10`.

## 2026-11-16-briefing-chain: each build starts the wait for the next briefing (tag pending)

**What changed:** the briefings no longer wait on a scheduled run near their slot. Every deploy run ends by starting the briefing watchdog in wait mode: it sleeps until the next unsent slot (07:00, 11:00, 16:00, 21:00 UK) and dispatches the build that sends it, which starts the next wait.

**Evidence:** GitHub shed the watchdog's own crons: none of the nine 06:05-08:45 UTC runs started on 16 Nov, the only morning deploy started at 06:14 UTC, and the morning push was unsent 96 minutes after its hour at 08:36 UTC (sent by a hand dispatch from the build session). `claude/briefing-chain-2026-11-16.md`.

**Files:** `tools/briefing_watch.py` (`next_wait`, `wait_and_kick`, `--wait`), `.github/workflows/deploy.yml` (`briefing-next`), `.github/workflows/briefing-watch.yml` (`wait` input, timeout, concurrency per mode), `tests/test_briefing_watch.py`, `claude/briefing-chain-2026-11-16.md`, `CLAUDE.md`.

**Not changed:** `notify.py`, the slots, the crons, any Card rule.

**Roll back:** `git revert` the merge commit, or remove the `briefing-next` job.

## 2026-11-16-comp3: the Card's two-a-competition cap replayed on football-data too (tag pending)

**What changed:** nothing on the page. `comp3` (three Card picks from one competition, pre-registered 10 Nov) now runs in the football-data replay of the model's-picks Card (`cardM7`, paired and pooled), so the 30 Nov review can gate it on both sides.

**Evidence:** the UK day 16 Nov has four NBA picks that pass every Card condition and no group, because `COMP_MAX` allows two from one competition and a 2x needs three; over 13 to 19 Nov lifting the cap builds a 2x on 3 days of 7 (live 2). On the settled pool, 30 Oct to 15 Nov, comp3 is identical to live (12 groups, 4 won v 4.97 expected, -25%). `claude/card-comp3-2026-11-16.md`.

**Files:** `tools/card_legs_history.py`, `tests/test_card_comp3.py`, `claude/card-comp3-2026-11-16.md`, `CLAUDE.md`, this entry.

**Not changed:** `COMP_MAX` (2), `CARD_RULE` 11, any Card condition.

**Roll back:** `git revert` the merge commit.

## 2026-11-16: FIFA ranking read from the endpoint FIFA's page uses (tag pending)

**What changed:** the build can now take FIFA's 7 Oct 2026 release (211 teams) in place of the 20 Jul one on file. The file itself is not committed here: it is bot-written, so the first deploy after the merge refreshes it (the sandbox that rebased this cannot reach inside.fifa.com). FIFA's page loads its ranking from `/api/live-world-ranking/get-rankings?mode=schedule&gender=1&rankingType=football&scheduleId=FRS_Male_Football_YYYYMMDD`, with schedule ids listed with their publication dates in the page's embedded `dates` JSON. The numeric `dateId` overview API answers nothing after 20 Jul. `rankings._fifa_schedule` reads the newest schedule id from the page and takes that release under the existing checks (`FIFA_MIN_SHARE`, `_same_list`); six spellings the new endpoint changes (Brunei, Hong Kong, Macau, St Kitts and Nevis, St Lucia, St Vincent) are mapped back to the file's (`FIFA_SCHEDULE_NAMES`). Internationals on the Daily List are adjusted on the new points.
**Evidence:** run from the cloud sandbox (inside.fifa.com answered): the page named `FRS_Male_Football_20260720` as published 2026-10-07, the endpoint returned 211 rows led by Spain 2011.57 (previous points 1995.88 = the file's 20 Jul figure), and the overview API with `FRS_...` or any later id returned `{"rankings": []}`. `refresh_fifa` wrote the new file; the 211 teams match the old file except the six spellings above. New tests in `tests/test_rankings.py`.
**Files:** `rankings.py`, `tests/test_rankings.py`, `claude/world-rankings.md`, this entry.
**Not changed:** the FIFA adjustment weights (`FIFA_W`), the stale warning, the numeric scan (kept as a fallback). The file's `id` stays 15175 (the schedule ids have no number).
**Roll back:** `git revert` this release; the next refresh can no longer find releases after 20 Jul. From office pull request #330 (held for owner approval because it carried `fifa-rankings.json`), rebased onto main by the 16 Nov build session.


## 2026-11-15-ncaab-elo: college basketball Elo settings re-tested, no change (tag pending)

**What changed:** nothing in the model. A dated note, `claude/ncaab-elo-settings-2026-11-15.md`, records the tests.

**Evidence:** hfa 125-200 (K 24 and 32) all worse on the check season (0.5517-0.5587 v 0.5499, p(worse) 1.00); K 24 +0.0004. A neutral-court calibration curve (home-only base curves) gained 0.00055 log loss, p(worse) 0.15 on 5,814 check games, but widened the 65%+ quoted-landed gap from 0.0218 to 0.0232, which fails `tune_sport`'s guard; the neutral curve alone gained 0.00015. The replay shows college basketball quoted over its landed rate, so the live +4 point surplus is not something the history can fit.

**Files:** `claude/ncaab-elo-settings-2026-11-15.md`, `RELEASES.md`.

**Not changed:** `sports.py`, `sports.json`, any bar or list rule.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-span-held: the Card no longer stakes a two-day group's picks twice (tag pending)

**What changed:** a Card group built just after midnight now leaves out the picks the day before's two-day group already holds. The nightly Card review flags any fixture in two Card groups.

**Evidence:** on 15 Nov Pistoiese v Coriano and Philadelphia 76ers v Indiana Pacers were in 14 Nov's two-day Card 2x (2.36) and in a 15 Nov Card 2x (2.09) built at 00:44 UTC. `span_taken` was only carried from a day the same build built, and after midnight the day before is no longer built. `span_held("2026-11-15")` on the live archive returns the three events of 14 Nov's group.

**Files:** `groupings.py` (`span_held`, `main`), `tools/card_integrity.py` (`card-pick-twice`, `picks_twice`), `tests/test_card_span.py`, `tests/test_card_integrity_twice.py`, `claude/card-span-held-2026-11-15.md`, `CLAUDE.md`.

**Not changed:** any Card rule or constant (`CARD_RULE` 11), the record (15 Nov's groups stand as staked).

**Roll back:** `git revert` the merge commit.

## 2026-11-15-briefing-watch: briefings no longer wait for a dropped cron (tag pending)

**What changed:** a watchdog dispatches a deploy when a briefing slot (07:00, 11:00, 16:00, 21:00 UK) is 10+ minutes overdue and no build is running, so the morning, lunch, evening and night pushes arrive near their time.

**Evidence:** GitHub sheds the deploy crons: ten a day, never more than eight runs from 10 to 15 Nov, the 07:40 cron not once in six days; the 13 Nov backups did not mend it. Morning push 123 and 138 minutes late on 14 and 15 Nov; the evening slot still unsent at 16:38 on 15 Nov (the watchdog's dry run would have dispatched). `claude/briefing-watch-2026-11-15.md`.

**Files:** `tools/briefing_watch.py`, `.github/workflows/briefing-watch.yml`, `tests/test_briefing_watch.py`, `claude/briefing-watch-2026-11-15.md`, `CLAUDE.md`.

**Not changed:** `notify.py`, deploy.yml's crons, any Card rule.

**Roll back:** `git revert` the merge commit, or disable "Briefing watch" in Actions.

## 2026-11-15-daily-list-bar: Daily List bar replayed again, no change (tag pending)

**What changed:** nothing for a reader. A dated replay of the Daily List league bar is added to `claude/daily-list.md`.

**Evidence:** `tools/list_bar_replay.py`, fit 2025/26 (6,451 win picks): at 70/75/77.5/80/82.5/85% n=313/168/130/86/56/35, hit 78.3/81.5/82.3/81.4/78.6/65.7%; bootstrap against 80%: only 85% differs (-15.4, -25.8 to -6.8). Check 2026/27: 11 calls at 80% (81.8%), 31 at 75% (83.9%); all intervals span zero or rest on too few picks. No league has 30 calls.

**Files:** `claude/daily-list.md`, `RELEASES.md`.

**Not changed:** `LIST_MIN`, `build_tennis.LIST_MIN`, any per-league bar.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-23: calibration by band and sport rerun: note only (tag pending)

**What changed:** a dated note, `claude/calibration-rerun-2026-11-15.md`. No code or model change.

**Evidence:** `calibration_bands.py` on history (not `record.json`). Football check season now 2,320 calls: 60-70% span landed +8.6 points over quote [+3.5,+13.5] against +2.1 [-1.3,+5.2] on the fit season, so Rule 3 is not met. Ice hockey (-6.1 at 55-70%) and college basketball (-2.2) run under quote on the check window only; baseball's over-statement eased. Other sports inside noise.

**Files:** `claude/calibration-rerun-2026-11-15.md`, this entry.

**Not changed:** `calibration.json`, `sports.json`, `tune.py`, any model constant.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-22: ATP below quote: surface idea not retested, note only (tag pending)

**What changed:** a dated note, `claude/tennis-surface-third-check-2026-11-15.md`. No code or model change.

**Evidence:** the tournament-surface map was rejected on 13 Oct (ATP +0.0031 log loss, p(worse) 0.95, n=1,523), no free surface source exists (27 Oct, 9 Nov), and the live window (autumn indoor hard, tour finals) is all hard court, already the default, so surface cannot explain the 59% v 64% ATP shortfall. Gates: not applicable.

**Files:** `claude/tennis-surface-third-check-2026-11-15.md`, this entry.

**Not changed:** tennis ratings, `build_tennis.py`, the Daily List and Card tennis floors.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-21: fewer Claude API calls: two office sprints a day, context reads for the Card only (tag pending)

**What changed:** Douglas: "my API reach is now finished for Claude ... roll back whatever we've implemented recently that's causing a lot of these calls." The two recent additions that call the Claude API on the shared `ANTHROPIC_API_KEY` are rolled back. The office agents run two sprints a day again (06:30 and 18:30 UTC), not four: the 00:30 and 12:30 sprints added on 9 Nov are gone, and the day's pull request cap falls from 28 to 16. The context check reads the Card's picks only: the Daily List reads added on 12 Nov are off (`groupings.CX_LIST_MIN` None) and the daily cap is 8, down from 25.

**Why:** each office sprint runs up to six Claude Code sessions (Sonnet, up to 50 turns each), so four sprints a day was up to 24 sessions a day; the context check made up to 25 Sonnet and Haiku calls a day with web search. Both drew on the one key, which hit its monthly limit on 14 Nov (`claude/context-paused-2026-11-14.md`); every sprint since has failed on it. Nothing else in the pipeline calls the Claude API. The Scale tab, the markets, the ledger and the slip call none (they use API-Football and the odds feeds, not Claude).

**Files:** `.github/workflows/office-agents.yml`, `groupings.py`, `context_review.py`, `claude/api-allowance-2026-11-15.md`, `CLAUDE.md`, this entry.

**Not changed:** the Card's context veto (`CARD_CONTEXT`), the claude.ai scheduled sessions and weekly report (they run on the Claude plan, not the API key), `ceo.yml` and `claude.yml` (they run only when Douglas asks).

**Roll back:** `git revert` the merge commit; or restore the cron line, `CX_LIST_MIN = 0.75` and `CONTEXT_DAILY_READS` 25 one at a time.

## 2026-11-15-20: Scale at a glance shows the last seven days as dots again (tag pending)

**What changed:** Douglas: "on the scale tab, I want you to have the visual infographic for the last 7 days as you did before." The glance's dot rows (a line a day, a column a tier, a dot a pick coloured by result) run again from tomorrow back through the last seven days, each row opening its day's list on a tap. Older days sit in a "more days of dots" fold, and the ten-a-day tables added earlier today (#315) moved into a closed fold under the dots, unchanged.

**Evidence:** checked in Chrome at 1280px and 400px on a local build, no page errors, no sideways scroll; full suite and `nametest.py` pass.

**Files:** `index.html`, this entry.

**Not changed:** `scale.py`, the rule, the archive, grading, the tables' content.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-19: the FIFA ranking also read from FIFA's public ranking page (tag pending)

**What changed:** the build after 2026-11-15-18 (deploy run 43716339474) showed the dateless overview's `rankings` holds no parsable rows, so FIFA's API answers nothing after 20 Jul 2026 in any form tried. `rankings.refresh_fifa` now also reads the public men's ranking page (`FIFA_PAGE_URL`, `/fifa-rankings/world-ranking/men`): every `dateId=id` it links to is asked of the API first, and the longest `rankingItem` list in its embedded JSON (`__NEXT_DATA__` or any JSON script) is a release, under the same checks (newer than the file, 80%+ of its teams, the same top 20). Each build logs what the page held (size, ids, rows, `__NEXT_DATA__`), and the overview line now says "an empty rankings list" where that is what came back.
**Evidence:** run 43716339474's "FIFA ranking:" lines. `tests/test_rankings.py` +2 (a page's embedded rows taken and its id asked first; a bare page described); every refresh test has the page patched so no test reaches the network; suite OK; `nametest.py` clear. Read on the merge's CI build.
**Files:** `rankings.py`, `tests/test_rankings.py`, `claude/world-rankings.md`, `RELEASES.md`.
**Not changed:** the FIFA adjustment's weights, the Daily List's bars, the Card, any record.
**Roll back:** `git revert` the merge.

## 2026-11-15-18: Scale groups take football from every fixture; Starred rows match the Daily List (tag pending)

**What changed:** a Scale group's football legs now come from every football fixture William Hill offers at 55%+, not the Daily List alone (`RULE` 4), ranked by the model's own chance for each. Starred now draws every bookmark exactly as the Daily List does: the same row, chips and marks, in the list's order, with started picks kept and their results shown. Douglas: "scour all football fixtures ... widen the pool" and "They need to look identical."
**Evidence:** replayed 1 to 14 Nov: more groups (fourfolds 13 v 10, fivefolds 12 v 7), the same wins (2 and 1), so lower estimated returns (fourfolds -41% v +8%). Starred: first row's markup identical to the list's, checked at desktop and 400px.
**Files:** `scale.py` (`GROUP_ANY_TIER`, `with_group_legs`, `RULE` 4), `index.html` (`renderStarred`, `listPut`, `listByStrength`, `starIdOf`; Scale copy), `tests/test_scale.py`, `claude/scale-pool-and-starred-2026-11-15.md`, CLAUDE.md.
**Not changed:** any model, the Daily List, other sports' group legs, saved bookmarks.
**Roll back:** `git revert`; or `GROUP_ANY_TIER = ()` with a `RULE` bump for the Scale half alone.

## 2026-11-15-24: the FIFA ranking taken from the dateless overview (tag pending)

**Shipped in:** `036b7f03` (renumbered on 16 Nov 2026: its id was used twice, so it was never tagged)

**What changed:** the first build after 2026-11-15-17 (deploy run 43715171219) logged what FIFA's dateless overview returns, with and without `rankingType`: `keys: ['rankings']`, the current release's rows and no release id, while no id from 15176 to 15335 answers. So the id scan could never find it. `rankings.refresh_fifa` now parses the overview's own rows as a release and takes it when it is dated after the file, holds 80%+ of the teams on file and reads as the same ranking (`_same_list`: 80%+ of the file's top 20 inside its top 30, so a women's or futsal list is refused); the file keeps its id so the scan starts where it did. The log says "new release ... from the dateless overview", or why it was refused, with the rows' team count and date.
**Evidence:** run 43715171219's "FIFA ranking:" lines (above). `tests/test_rankings.py` +4 (overview rows taken, older rows ignored, another ranking refused, `_same_list`); suite OK; `nametest.py` clear. Confirmed on the merge's own CI build, not in the sandbox (inside.fifa.com is blocked there).
**Files:** `rankings.py`, `tests/test_rankings.py`, `claude/world-rankings.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the FIFA adjustment's weights, the Daily List's bars, the Card, any record.
**Roll back:** `git revert` the merge.

## 2026-11-15-17: the FIFA ranking refresh asks the API the way FIFA's site now does (tag pending)

**What changed:** the build has scored internationals on the 20 Jul 2026 FIFA ranking for 118 days: every build since August logged "no newer release than 2026-07-20 (scanned ids 15176-15335, latest per overview: None)" with no fetch failure, while FIFA kept publishing (an October 2026 release is on inside.fifa.com, whose ranking pages moved to `/fifa-rankings/world-ranking/`). FIFA's API URLs now carry `rankingType=football` (a public `id15136` URL has it). `rankings.refresh_fifa` asks with it first and without it second, for the release ids and for the dateless overview; an overview that names no id logs its top-level keys, so the next build log shows FIFA's shape if this is not the cause; and a release with under 80% of the teams on file (`FIFA_MIN_SHARE`, about 211 sides) is refused, so a futsal or women's list under the same id scheme can never replace the men's ranking.
**Evidence:** deploy run 43713946490 (15 Nov 12:28 UTC) log lines above. The sandbox cannot reach inside.fifa.com, so the fix is confirmed on the next CI build's "FIFA ranking:" line, not here. `tests/test_rankings.py` +3 (a release answered only with `rankingType`, the overview's keys logged, a short list refused), each failing on the old code; suite OK; `nametest.py` clear.
**Files:** `rankings.py`, `tests/test_rankings.py`, `claude/world-rankings.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the FIFA adjustment's weights, which internationals reach the Daily List, the Card (internationals are off it), any record. `fifa-rankings.json` is rewritten by the build only.
**Roll back:** `git revert` the merge; the old URL is still the second one tried, so behaviour only adds.
## 2026-11-15-16: Scale shows estimated prices where no feed prices the bet (tag pending)

**What changed:** on the Scale tab a pick with no real price now shows an estimate ("≈ 2.13", italic, marked "estimate"), worked as the fair price of its chance less a typical bookmaker margin (football's result-and-goals bets 15%, handicaps and set betting 8%). Groups without a real price on every leg read "Pays about 4.83", and the scoreboard and group lists show the estimated return beside the real one, tallied apart (`estN`, `estRet`). Douglas: "If you're missing data on prices, just give an estimate."
**Evidence:** William Hill kept about 16% a leg on win and both score over 69 priced fixtures (`claude/scale-strong-legs-2026-11-15.md`). First estimated read of the replay (1 to 14 Nov): doubles 7 of 14 -15%, threefolds 3 of 12 -29%, fourfolds 2 of 10 +8%, fivefolds 1 of 7 -60%.
**Files:** `scale.py` (`EST_MARGIN`, `est_price`, `price_or_est`, groups' `est`, `estRet`), `index.html` (`scRow`, `scCard`, `scRet`, `.sc-est`), `tests/test_scale.py`, `claude/scale-estimated-prices-2026-11-15.md`, CLAUDE.md (also: standing authorisation for sessions to merge their own pull requests, `.github/` and `agents/` included, and to tidy stale ones).
**Not changed:** any pick, chance, tier or group rule (`RULE` 3), the real-price record, any model.
**Roll back:** `git revert` the merge.

## 2026-11-15-15: baseball Elo refitted on a wider grid (tag pending)

**What changed:** MLB's Elo settings go from K 8, home advantage 25, carry-over regress 0.25, no margin to K 3, home advantage 15, regress 0.0, margin of victory on, with a refitted calibration (a 0.031, b 0.9188, applied: it narrows the 65%+ gap, 0.033 to 0.012). `sports.py` gains `GRID_SPORT` so baseball's tune searches lower K; other sports keep `GRID`.
**Why:** the planner showed MLB 27 of 40 live (z +1.5). That is inside noise and the opposite of history: on 3,626 check games MLB landed 60.0% v 64.2% quoted at 60%+. The live record only located the sport; the fit's K sat on the grid's lowest value (8), so the search was clipped.
**Evidence:** fit 1 Jul 2024 to 1 Jul 2025, check 1 Jul 2025 on (3,626 games, never fitted on). Check log loss 0.6844 v 0.6859 live settings: gain 0.0015, p(worse) 0.09; fit window gain 0.0024, p(worse) 0.02. Against defaults -0.0185, p(worse) 0.00; against backing home -0.0068, p(worse) 0.01. Calibration -0.0007, p(worse) 0.01, honesty guard passed. 60%+ now lands 61.4% v 64.0% quoted (was 60.0% v 64.2%): still over-stated, less so. No Daily List place for baseball (none earned). The new K and regress sit on the grid edge, so a wider search could move them again; not tried (Rule 4).
**Files:** `sports.py`, `sports.json` (mlb entry only), `claude/mlb-elo-k-2026-11-12.md`, `RELEASES.md`.
**Not changed:** football, tennis, other sports, list bars, grading.
**Roll back:** `git revert` this commit; the next hand `--tune` also refits from history.

## 2026-11-15-14: opponent-adjusted ratings tested and rejected (tag pending)

**What changed:** nothing on the page or the model. A dated note and the test harness record the rejected idea.

**Evidence:** opponent-adjusted attack/defence (3 iterations, blended with raw at 0.25, 0.5, 1.0), paired bootstrap, calibration live and refitted. Fit 2025/26 (6,474): -0.0001 to -0.0002, under the 0.0005 gain gate at every setting; check 2026/27 (1,584): -0.0002 to -0.0014. Fit-season gain fails, so not shipped.

**Files:** `claude/opp-adjusted-ratings-2026-11-13.md`, `tools/opp_adjust_eval.py`, this entry.

**Not changed:** `engine.py`, `calibration.json`, every constant.

**Roll back:** `git revert` this release's commit.

## 2026-11-15-13: England Championship league-specific calibration curve rejected (tag pending)

**What changed:** nothing for a reader. A dated note and a reproducible tool record a rejected test: an en.2-only calibration curve.

**Evidence:** best of 48 curves on 2025-26 (a 1.3, b -0.6) gains 0.0011 log loss (p(worse) 0.20); confirm 2026-27 only 95 fixtures (gate 250), -0.0026 (p 0.20); 2024-25 +0.0000, 2023-24 -0.0007 (p 0.33). Fails the enoughData gate and is unstable by season.

**Files:** `claude/championship-calibration-2026-11-11.md`, `tools/championship_calibration.py`, `RELEASES.md`.

**Not changed:** no model number, `calibration.json`, engine or page.

**Roll back:** `git revert` the commit; nothing depends on it.

## 2026-11-15-12: the office agents and Elena run on the Max-plan token when it is set (tag pending)

**What changed:** `office-agents.yml` and `ceo.yml` pass only `CLAUDE_CODE_OAUTH_TOKEN` to the Claude action when that secret is set; the API key is passed only when it is the sole key. Before, both were passed and the action always used the API key.

**Why:** the API key hit its $10 monthly cap at 00:24 UTC on 14 Nov. The agents' own logs report about $13 of usage from 5 to 13 Nov (about $2 a day at four sprints), and the context check read 25 picks on each of 12 and 13 Nov on the same key. Every sprint since has been refused in under a second. On the Max token the agents cost nothing extra and the key is left for the context check.

**Needs the owner:** add the `CLAUDE_CODE_OAUTH_TOKEN` repository secret (`claude setup-token` on the Mac) if it is not set. Without it nothing changes.

**Not changed:** `deploy.yml`, `context_review.py`, `DAILY_READS`, any Card rule.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-11: the office sprint skips a task whose pull request lost its labels (tag pending)

**What changed:** `agents/pick_task.py` now also treats an objective as busy when an open pull request's branch is `office-agent/<date>-<key>`, read from the branch name (`branch_objectives`), not only from its `objective:` label.

**Why:** #279 (college basketball) opened at 07:06 on 13 Nov but GitHub failed the label step with a GraphQL error, so it carried no labels. The planner saw `hq-sport-ncaab` as free and the 19:55 sprint gave the sports agent the same task, which failed pushing the same branch (non-fast-forward). Two of the day's four sprints ended failed on this one pull request, and each spent an agent place.

**Tested:** `tests/test_pick_task.py` (`TestBranchObjectives`); full suite and `nametest.py` pass.

**Files:** `agents/pick_task.py`, `tests/test_pick_task.py`, this entry.

**Not changed:** `open_pr.sh`, the merge gate, any Card rule. #279 itself still has no labels; adding `office-agent`, `agent:sports` and `objective:hq-sport-ncaab` by hand clears it today.
## 2026-11-15-10: Scale reviewed: football to win with over 2.5 goals, groups from Daily List picks only (tag pending)

**What changed:** Douglas: "we need to find a winning pattern in this scale feature. Review and optimise." Two things moved on the Scale tab. Football's second condition is now **to win with over 2.5 goals**, with the model's own number for the fixture as its chance and the best UK price on file for the bet, named; to win with both teams scoring stays under it with William Hill's price, and the week's table still says whether both scored. And the day's **groups are built from Daily List picks only**, most likely to land first: a double, threefold, fourfold and fivefold as far as those picks go. The reserve never fills a group, the football threefold is gone, and a day with fewer than two Daily List picks still to start has no group.

**Why:** the review of every graded pick at 55%+. Football: winning with both teams scoring lands 28-38% whatever the winner's strength (2,645 picks), while winning with over 2.5 goals rises from 41% at 55-62% confidence to 77% at 85%+; and William Hill's price for win and both score keeps about 16% a leg (price times fair chance 0.843 on 69 fixtures, against 0.93-0.94 on its other markets), so three legs return 60% of fair before a ball is kicked. Tiers: across the five sports a Daily List pick's Scale bet landed 216 of 344 times (63%), a reserve pick's 526 of 1,107 (48%), the rest 44%, so a reserve leg is the leg that loses an accumulator.

**Evidence:** `claude/scale-strong-legs-2026-11-15.md`. Groups replayed over 5 Oct to 14 Nov (41 days, chosen from what was published before each start): doubles 13 of 31, threefolds 7 of 24, fourfolds 6 of 21, fivefolds 5 of 18; the old rule's threefolds 13 of 41 and fivefolds 5 of 41. Forty-one days cannot separate the two at the threefold; the case rests on the per-pick tables. **None of this shows the bets pay**: four of the five have no price on file. A Daily List threefold landing three times in ten needs 3.4.

**Tested:** `tests/test_scale.py` (41 cases: the football sample by market and tier, groups from Daily List picks only, a pick grading by its own bet, an old rule's frozen group); full suite and `nametest.py` pass. The tab checked in Chrome at 1280px and 400px on a local build.

**Files:** `scale.py` (`RULE` 3, `FOOTBALL_MARKET`, `GROUP_TIERS`), `index.html`, `tests/test_scale.py`, `claude/scale-strong-legs-2026-11-15.md`, `CLAUDE.md`, this entry.

**Not changed:** any model, the Daily List, the tiers and their order, the ten-a-day top-up, the other sports' bets, the Card, the slip. Picks and groups already archived keep their own bet and grade by it.

**Roll back:** `git revert` the merge commit; or `FOOTBALL_MARKET = "wbtts"` / `GROUP_TIERS = TIERS` with a `RULE` bump for either half alone.
## 2026-11-15-9: The replays' check season runs past 20 Sep (tag pending)

**What changed:** `tune.load`, the loader behind `tune.py`, `backtest.py`, `replay.py`, `tools/card_legs_history.py`, `tools/goals_value.py` and `tools/model_ideas.py`, now scores the check season's unscored openfootball fixtures from the ESPN results the daily build commits in `current/` (`tune.fill_current`), by the live build's own rule (`build.fill_lagging`: its own pair within 21 days, never over the source, all or nothing on names). openfootball stopped scoring after 20 Sep, the build was fixed on 13 Nov, but every replay still ended its 2026-27 season there: the Card's football-data check season had 7 candidate legs in October, so no rule 7 variant's check-season side could be read, and the Monday calibration and home-advantage refits confirmed on August and September only.

**Evidence:** sandbox, 15 Nov: check fixtures 903 to 1,638 (735 filled in 14 leagues, Belgium 98, none refused on names; fit season unchanged at 5,262). `claude/replay-check-season-lag-2026-11-15.md`. 6 tests in `tests/test_tune_fill.py`; suite and `nametest.py` pass. `card-legs-history.yml` runs on this pull request with the fuller 2026-27.

**Files:** `tune.py`, `replay.py` (`--freeze` keeps openfootball rows only), `tools/card_legs_history.py` (docstring), `tests/test_tune_fill.py`, `claude/replay-check-season-lag-2026-11-15.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any model constant, `calibration.json`, `home-advantage.json`, any Card rule, the live build, the page, the evaluation harness (frozen snapshots).

**Roll back:** `git revert` the merge commit, or `tune.load(cache, fill=False)`.

## 2026-11-15-8: m7opp5 read on five seasons: ahead in all five, waiting on the pool (tag pending)

**What changed:** the note only. `m7opp5` (the model's picks, football opposition priced 5.0+) on the five football-data seasons: ahead of live in every one, +0.10 to +0.16 units a day; pooled 150 groups, 73 won v 62.8 expected, +17.5% v live +9.6%, p(worse) 0.014 on 450 legs. The pool is ahead too (p 0.07) but on 33 legs, under the 100-leg gate, so the live rule is unchanged. `m7opp9` builds 9 groups in five seasons.

**Files:** `claude/card-m7opp-2026-11-15.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any rule or code.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-7: The opposition's price on the model's picks, replayed (tag pending)

**What changed:** nothing on the page or the live Card. Rule 6's opposition condition (the other side priced 9+), the one Card condition that held in all five football-data seasons, was not carried over when the Card became the model's own picks on 11 Nov: `model_fault` never read it, and the first rule 11 group took VVV-Venlo with the opposition at 4.83 (lost). `groupings.CARD_MODEL_OPP_MIN` (empty, so live is unchanged) now lets the replay put it back, and two variants are pre-registered: `m7opp9` (9+) and `m7opp5` (5.0, the Edge flag's floor), on the pool nightly and on the five football-data seasons (`cardM7`).

**Evidence:** first pool and archive read (11 Sep to 14 Nov): live 20 groups, 8 won, -1%; `m7opp5` 11 groups, 6 won, +42%, +0.76 units a day v live, p(worse) 0.07 on 33 legs (gate 100); `m7opp9` one group. The football-data side runs in CI. `claude/card-m7opp-2026-11-15.md`. 5 tests in `tests/test_card_m7opp.py`; suite and `nametest.py` pass.

**Files:** `groupings.py`, `tools/card_replay.py`, `tools/card_legs_history.py`, `tests/test_card_m7opp.py`, `claude/card-m7opp-2026-11-15.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any live `CARD_*` rule, `CARD_RULE`, the model, the page.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-5: The week behind shows only games a bookmaker priced; the Analysis page brought up to date

**What changed:** Douglas: "make sure all games were a game / league available to bet on", and "update the analysis page with the latest context of the model".
- Scale at a glance: each past day's table now takes only picks a bookmaker feed priced before the start (`scale.priced_keys` reads the results ledger; football keeps its own win-and-both-score price or the replay's proxy), marks a game William Hill priced with "Hill", and counts the unpriced picks left off in the day line.
- Analysis page: the prose now describes the model as it stands on 15 Nov 2026: the cup calibration, the lagging-source fill and stale-league flag, the Daily List order and Group A / B, the wider leagues' 75% bar, the ranked-international rule, the full tested-and-rejected list (form by stage, team news, table position, the home-and-away tilt, FIFA lift damping, the goals scale, tennis hot form, home advantage per league on its weekly gate), the market's edge on the archive, the priced record's reading (short favourites hold their value, model-above-market picks land about half the time), the Bets tab in place of the Odds tab with its four tested-apart lines, the college sports' Away / Neutral marks and list status, tennis's list status and surface, and a dated "updated" line. The live tables are unchanged.

**Evidence:** rendered in headless Chromium, no errors, no overflow; one test added; suite and `nametest.py` pass.

**Files:** `scale.py`, `index.html`, `analysis.html`, `tests/test_scale.py`, `RELEASES.md`.

**Not changed:** any rule, model or record.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-25: Scale at a glance shows ten a day for the week behind

**Shipped in:** `00388c3a` (renumbered on 16 Nov 2026: its id was used twice, so it was never tagged)

**What changed:** Douglas: "I want there to be 10 games shown with what the recommendation was of the model, and whether or not that won or lost with the team, and if both teams scored ... in order of strongest ... make sure that it was bettable." The Scale tab's glance now lists each past day (the last seven open, the rest in a fold) as a table of its ten strongest picks: Daily List picks first, then the reserve, then the rest, strongest model number first within each; football only where William Hill prices the bet, as before, so nothing obscure. Each row: sport, the model's pick and opponent, competition, the model's number, Won / Lost / Void / No result with the score, and for football whether both teams scored (for the other sports whether the Scale margin landed). The day line sums it ("7 of 10 won · both scored in 2 of 3 football") and "full list" opens the day. The dot rows stay for today and tomorrow. `scale.py` writes the fields the table needs into the glance (`both_scored` from the score).

**Evidence:** rendered in headless Chromium at 1280px and 400px, no horizontal overflow; two tests in `tests/test_scale.py`; suite and `nametest.py` pass.

**Files:** `scale.py`, `index.html`, `tests/test_scale.py`, `RELEASES.md`.

**Not changed:** the Scale rule, tiers, groups or grading; the archive.

**Roll back:** `git revert` the merge commit.

## 2026-11-15-4: Scale in three tiers, five sports and ten games a day (tag pending)

**What changed:** the Scale tab now lists ten or more games a day in three tiers, each with its own line on the glance and the list: **Daily List picks**, **Daily List reserve**, and **everything else** the model picks at 55% or better, added strongest first only until the day has ten games. Three sports join football and tennis, each with a margin for its second condition: the NBA to win by 10 or more, the NFL by 7 or more, rugby by 8 or more. Within a tier the order is the chance the Scale bet lands. Each day has a threefold, fourfold and fivefold from the top of that order, and a football threefold priced on every leg at William Hill. An unpriced pick names the line to look for at William Hill (handicap -9.5, set betting 2-0) and the price its chance needs. Also fixed: a fixture replayed within days (New Zealand v India, 12 and 15 Nov) was graded with the earlier game's score before it kicked off.

**Why:** Douglas, on the first live day (two football picks, no group): "at least 10 games per day ... tiers with lines on that infographic that say daily list pick, daily list reserve pick, everything else ... NFL, basketball, you're going to need to propose something based on the data ... every day to have at least 5 games, to add into some sort of scale accumulator."

**Evidence:** the margins come from every graded pick in `sports-graded.json`. At 75%+: the NBA by 10+ 20 of 31 (65%), the NFL by 7+ 11 of 17 (65%), rugby by 8+ 23 of 35 (66%), tennis in straight sets 160 of 243 (66%). At 55%+: 43%, 43%, 58%, 48%. Football by tier in leagues Hill prices: list 43 picks, 81% won, 33% with both scoring; reserve 86, 65%, 33%; everything else 300, 60%, 26%. Under the new rule 15 Nov has 19 picks (6 list, 13 reserve) and four groups, 16 Nov has 10 (1, 7 and 2 from everything else). None of the margin or straight-sets bets has a price on file: the tab says how often they land, not that they pay.

**The days before the tab, replayed:** at Douglas's request ("retrospectively add picks ... follow the same rules ... add in the results afterwards, so it's not biased") the glance now shows 1 to 14 Nov rebuilt under the same rule: picks, tiers and order taken only from what was published before each start, the tallied chances from results dated before the day, results attached afterwards. 288 graded picks: Daily List tier 72, 90% won, 62% landed the Scale; reserve 215, 71% and 42%. Groups won: threefold 4 of 14, fourfold 4 of 14, fivefold 3 of 14, football threefold 0 of 5. The last seven days: list 26 of 26 won, 14 landed; threefold 1 of 7, fivefold 0 of 7. Football "at William Hill" is a proxy for those days and nothing in them has a price, so they say how often it landed, not what it paid. They are tallied apart from the record; a tap on any day of the glance opens its picks.

**Tested:** `tests/test_scale.py` (36 cases: the margin sample, the band rate, the top-up, tier order, the football threefold, margin grading, the earlier-meeting guard, the replay's chances not seeing the day's results); full suite and `nametest.py` pass. The tab checked in Chrome at 1280px and 400px on a local build (no page errors, no sideways scroll).

**Files:** `scale.py` (`RULE` 2), `daylist.py` (`pinned(every=True)`), `markets.py` (`_result_for`), `index.html`, `tests/test_scale.py`, `claude/scale-tiers-2026-11-15.md`, `CLAUDE.md`, this entry.

**Not changed:** any model, the Daily List, the reserve's rule, the Card. College basketball and college football stay off Scale (UK books rarely price them).

**Roll back:** `git revert` the merge commit; `scale-archive/` can stay.
## 2026-11-15-3: The slip, built for return

**What changed:** the Bets tab has **The slip** (`slip.py`, `slipSection`), one accumulator a UK day of 3 to 5 legs paying 3x to 6x, chosen for expected return: each leg's chance is the landed rate its sport and price band have shown on the results ledger (50+ graded picks, else the pooled band), legs from bands returning worse than -2% a leg, legs the model prices more than 5 points above the market, and away college picks are refused, and the slip is offered only when its expected return covers the stake. It shows the expected return in pence per pound, the tested basis of every leg, why an empty day is empty, and a table of landed-against-the-price by sport and band. Archived to `slip-archive/` (frozen at the first leg's start), graded from the ledger, tallied against a pre-registered gate (100 slips, positive, p(loss) <= 0.10) with a walk-forward replay over the ledger's past days beside it.

**Evidence:** `claude/the-slip-2026-11-15.md`. On the ledger, picks at 1.00-1.15 return -0.4% a leg, 1.30-1.50 -3.3%, 1.50-1.80 -13.8%; picks the model rates 5+ points above the price land 49-56% and lose 9-14% a leg. Douglas's eleven-fold at 3.0 was the better bet per pound than his five-fold at 6.6. Replay before today: 6 days built, 2 won, +7.3% (not evidence yet). 10 new tests in `tests/test_slip.py`; suite and `nametest.py` pass; Bets tab checked in headless Chromium at 1280px and 400px.

**Files:** `slip.py`, `index.html`, `tests/test_slip.py`, `.github/workflows/deploy.yml` (runs after `scale.py`, archives `slip-archive/`, copies `slip.js`), `.gitignore`, `slip-archive/`, `claude/the-slip-2026-11-15.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any model, the Daily List, the Card, the Edge flag, the Scale tab, the ledger.

**Roll back:** `git revert` the merge commit; the Bets tab loses the section and nothing else moves.

## 2026-11-15-26: Away and Neutral marks on college picks

**Shipped in:** `e2ae8654` (renumbered on 16 Nov 2026: its id was used twice, so it was never tagged)

**What changed:** every college basketball and college football row at 70%+ whose pick is away from home, or on a neutral court, carries an `Away` or `Neutral` chip (Daily List, reserve, sport tabs, pinned rows), and the reserve's summary line counts them. `sports.wary` writes the mark into the archive; `index.html` `sideWary` draws it from the row. `sports-record.json` gains `bySide` (landed v quoted by side per college sport at 70%+) with a pre-registered tripwire: 100 away picks two standard errors under quote takes that sport's away picks out of the reserve.

**Evidence:** `claude/college-side-mark-2026-11-15.md`. Replay (live parameters, 70%+, Aug-Dec, both test seasons): college basketball home picks 88.8% v 83.5% quoted (z +6.5), away 76.0% v 77.3%, neutral 74.9% v 78.3%; college football home 84.5% v 81.0%, away 79.9% v 78.0%. Live: college basketball away 11 of 21, neutral 9 of 16; college football away 36 of 54 (67% v 78%, z -2.0). The carried-rating idea (sides with an early loss) was tested on the same replay and is not a signal. Tests in `tests/test_sports.py`; suite and `nametest.py` pass; page checked in headless Chromium.

**Files:** `sports.py`, `index.html`, `tests/test_sports.py`, `claude/college-side-mark-2026-11-15.md`, `claude/daily-list-losses-2026-11-14.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any probability, bar, list or reserve membership, the order, any constant in `sports.json`.

**Roll back:** `git revert` the merge commit; or `WARY_SPORTS = set()` in `sports.py` and `index.html` to drop the mark alone.

## 2026-11-15-2: the Scale tab: Daily List winners with a second condition added (tag pending)

**What changed:** a new tab, **Scale**, third in the bar after Bets (Douglas, 14 Nov 2026: "scaling the odds and even reducing the stake"). A Scale pick is a Daily List pick at the list's own bar with one more condition: football to win with both teams scoring, shown only where William Hill prices that bet; tennis to win in straight sets. Each UK day gets a threefold, fourfold and fivefold of the picks most likely to land, when there are that many. The tab opens with the record and Scale at a glance, a line of dots a day (won and landed, won only, lost, to play, not priced at Hill), then the day's list with each pick's winner chance, Scale chance, Hill's price and the price it needs, the groups, the leagues Hill prices and a scoreboard. New `scale.py` builds, archives (`scale-archive/`) and grades it on every deploy.

**Why:** Douglas wants bigger prices from smaller groups and smaller stakes than a long winners' accumulator, without lowering the bar on the winner, and wants the tracking visible. His feedback on the mock-up was that several leagues on it are not at William Hill, so the football list is cut to what Hill prices, read from the price feed on every build.

**Evidence:** football Daily List picks in leagues Hill prices, before the tab: 43, 35 won (81%), 14 with both scoring (33%). Tennis picks at 75%+: 243, 213 won (88%), 160 in straight sets (66%). First day (15 Nov): 11 football list picks, 2 priced at Hill, 9 left off, no group; both Hill prices are under what the model's chance needs (2.80 v 3.39, 3.50 v 4.50), and the tab says so. Football alone is about two picks a day, so days without a group will be common until the other sports' margin bets are added.

**Tested:** `tests/test_scale.py` (23 cases: straight sets from a score, the band rate, nested groups, what freezes at a start, grading); full suite and `nametest.py` pass. The tab checked in Chrome at 1280px and 400px on a local build (no page errors, no sideways scroll).

**Files:** `scale.py`, `index.html`, `tests/test_scale.py`, `.github/workflows/deploy.yml` (run it, archive `scale-archive/`, copy `scale.js` / `scale.json` to the site), `.gitignore`, `agents/pick_task.py`, `agents/open_pr.sh` (protected path), `claude/scale-2026-11-15.md`, `CLAUDE.md`, this entry.

**Not changed:** any model, the Daily List, the Card, Bets. Prices feed no model; they only decide which football picks the Scale list shows.

**Roll back:** `git revert` the merge commit. `scale-archive/` can stay.

## 2026-11-15: two-day Card groups counted in the record; the review reads the model's-picks Card on its own (tag pending)

**What changed:** `groupings.grade` now carries a group's `span` (and `basis`) onto its graded row. It dropped them, so `groupings-record.json` `cardSpan` tallied 0 groups with the first two-day group on file (14 Nov: VVV-Venlo, Pistoiese, Philadelphia 76ers, 2.36). The nightly Card review's live section now counts two-day groups in its window and adds one line for the Card as it is built today: the groups under `CARD_RULE` 7 and later (the model's own picks, from 11 Nov) with settled, won v expected and the return at the page's stakes, read from `cardByRule`.

**Why:** the review's live line mixed rules 4 to 11, so whether the model's-picks Card is landing could not be read without opening the record; and the two-day groups (`CARD_SPAN`, 12 Nov) are the owner's call to be reviewed on their own tally, which read zero.

**Evidence:** `grade()` on the current archive: `cardSpan` 1 group (pending) after the fix, 0 before; the Card record unchanged at 37 groups. The live section on today's files: "Days with a group: 9 of 14; groups 13; last group published for 2026-11-14. Rules: 5, 6, 11. Two-day groups (`CARD_SPAN`): 1." and "The model's-picks Card (rules 11, from 11 Nov): 1 group(s), 0 settled ... none settled yet."

**Tested:** `tests/test_groupings_record.py` `Span` (fails on the old code), `tests/test_review_live_days.py` two new cases; full suite and `nametest.py` pass.

**Files:** `groupings.py`, `tools/card_review_post.py`, both tests, this entry.

**Not changed:** any Card rule, the Card record's own tallies, the page.

**Roll back:** `git revert` the merge commit; the next build regrades the record.

## 2026-11-14-9: ten football markets tracked, priced and graded (tag pending)

**What changed:** new `markets.py` gives every football fixture the model's number for ten markets beyond the match winner (both teams to score, over / under 1.5, 2.5 and 3.5, the pick to win and both score, to win and over 2.5, to win to nil, double chance, draw no bet, the pick's team to score), prices each from API-Football for today and tomorrow (average, best UK book, William Hill, the bookmakers' fair chance), archives them to `predictions-markets/` frozen at kick-off, and grades them into `markets-record.json` with a pre-registered gate per market. The nightly Card review prints the table and says a pass in bold. deploy.yml runs it after the ledger and commits the archive and record; the record is also published on the site. Agents' protected paths now include the four bot-written files added today.

**Why:** Douglas, 14 Nov 2026: "For football fixtures I want to start looking at winner and btts, as well as just btts, goals over 2.5, and any other things you suggest. Let's go hard on setting this up to track on football", and the reviewing must be automated.

**Evidence:** the price feed was probed live first (`tools/markets_probe.py` on `odds-probe-run`): every market is priced, an all-bets sweep costs the same pages as the match-winner sweep (57 on 14 Nov), William Hill prices six of the ten. Calibration on 11,112 graded fixtures replayed from the archive: double chance 75.6% v 75.1%, draw no bet 67.6% v 66.1%, win to nil 26.9% v 27.0%, win and both score 24.1% v 21.5% (on quote from 25% up); the goals markets run low (over / under 2.5 57.8% v 54.3%, over / under 3.5 67.0% v 71.8%). No price history exists for these markets, so no return is claimed. `claude/football-markets-2026-11-14.md`.

**Tested:** `tests/test_markets.py` (grid agrees with the published chances, win and both score plus win to nil equals win, every market settled, API-Football's labels, margin removal, the archive frozen at kick-off, the record, the gate, the review section); the fetch path run against a stubbed feed; full suite and `nametest.py` pass. Not run against the real feed from the sandbox (no key): CI is the check, see the "markets:" lines in the build log.

**Files:** `markets.py`, `tools/card_review_post.py`, `.github/workflows/deploy.yml`, `agents/pick_task.py`, `agents/open_pr.sh`, `tests/test_markets.py`, `claude/football-markets-2026-11-14.md`, `CLAUDE.md`, this entry.

**Not changed:** the model, the Daily List, the Card, any existing record, the page. Prices feed nothing. About 400 API-Football calls a day, standing down under 2,000 left.

**Roll back:** `git revert` the merge commit; the archive and record can stay.

## 2026-11-14-8: every release tagged automatically (tag pending)

**What changed:** new `release-tags.yml` runs on every push to `main` and tags each `RELEASES.md` entry headed `## YYYY-MM-DD[-N]: title` that has no tag, as `release-<id>`, annotated with its title, on the first-parent commit that added the entry (`tools/release_tags.py`). Existing tags are read from the remote and never moved; headers without an id of that shape, or with an id used twice, are skipped and listed.

**Why:** Douglas, 14 Nov 2026: "I'm not going to add tags myself so can we find another way?" Cloud sessions cannot push tags and the API proxy refuses tag writes; only the office's own merges were being tagged (by footyalmanac-hq), so 31 entries from 11 to 14 Nov had no tag.

**Evidence:** a dry run against `main` at `dca98b0` lists 31 tags to create, `release-2026-11-11-3` to `release-2026-11-14-7`, each on its merge. Twelve entries headed `## 2026-11-1x (tag pending): ...` (no suffix) are skipped: their ids are ambiguous.

**Tested:** `tests/test_release_tags.py` (header parsing, skips, the commit that added an entry, an existing tag left alone); full suite and `nametest.py` pass.

**Files:** `.github/workflows/release-tags.yml`, `tools/release_tags.py`, `tests/test_release_tags.py`, `CLAUDE.md`, this entry.

**Not changed:** the site, the model, any record. Workflow path: owner merge.

**Roll back:** `git revert` the merge commit; tags already made can stay.

## 2026-11-14-7: every prediction kept with its result and price (tag pending)

**What changed:** `sports.py` writes `sports-graded.json`, every graded and void pick of the other sports, merged and never trimmed, as `record-graded.json` is for football. New `ledger.py` writes `results-ledger.json.gz`: one row a prediction across every sport, with its result and its pre-start price (the football archive's market block, the pool's first and last real price with William Hill's, and each build's board prices, so a game priced on any build keeps its price after the start). It carries a summary (landed, quoted, and the flat return at the recorded, best and Hill price, by sport, list / reserve / board and band), price coverage by sport, and the ungraded report: picks three or more days past their start with no result, by competition, printed every build and raised as a `::warning::` on the first build of each UK Monday. deploy.yml runs it after `groupings.py` and commits both files with the archive.

**Why:** Douglas, 14 Nov 2026: "are we storing every result against our prediction so we can learn from it?" `sports-record.json` kept 14 days of game rows, so October's rugby, NFL and college football list picks could not be read one by one; about 650 predictions (465 older than two weeks) had fallen out of the record unseen; and no file held a pick's result beside its price, so a band's hit rate could not be read as a return.

**Evidence (first read, 14 Nov):** 15,983 predictions since 20 Aug; 186 ungraded 3-14 days past the start (1 a Daily List pick), 466 past 14 days (Czech First League, LaLiga, Süper Lig, Saudi league and wider leagues the most). Daily List picks with a price: 75-85% 65 priced, landed 86% at an average 1.19, +2.2%; 85%+ 145 priced (124 college basketball), landed 92% at 1.06 (break-even 94%), -2.2%. The 882 football rows from before publish times were recorded (`legacy-unverified`) stay out, by the same rule the record grades by.

**Tested:** `tests/test_ledger.py` (latest pre-start copy, late copies ignored, moved fixture once, rematch and series apart, results, prices by side and before the start, merge never loses a result, the Monday warning, `merge_graded`); full suite (939) and `nametest.py` pass; ledger.py run on the repo's archives as above.

**Files:** `ledger.py`, `sports.py`, `.github/workflows/deploy.yml`, `tests/test_ledger.py`, `claude/results-ledger-2026-11-14.md`, `CLAUDE.md`, this entry.

**Not changed:** the model, any grading rule, any record file's contents, the page.

**Roll back:** `git revert` the merge commit; the two new files can stay or be deleted.

## 2026-11-14-6: the build says why a football leg stayed unpriced (tag pending)

**What changed:** `groupings.price_football` counts each football leg it could not price by reason and competition, and the build log prints one line for it ("football unpriced: noOdds 60 (...); noFixture 40 (...)"): `noFixture` (API-Football lists no fixture under those names that day), `kickoff` (both names found, kick-offs 90+ minutes apart: a moved game), `noOdds` (fixture found, no 1X2 price for the side), `capped` (a mid-priced leg over `FB_CALLS_MULT`), `error`. Also in `groupings.json` under the price report (`football.miss`, `football.missComps`).

**Why:** the 17:21 build on 14 Nov priced 122 of 229 football legs, with 5,744 API-Football calls left, and nothing said why the other 107 failed. The funnel counts 36 football legs for 14-17 Nov that pass every Card condition but the price (most in fifth-tier regional leagues: NB III, Tercera RFEF, Oberliga). A `noFixture` count in one league is a spelling to add to `LIVE_NAMES`; `noOdds` is a game no book prices, and no fix exists. Today there is no way to tell them apart without a debug run.

**Tested:** `tests/test_football_unpriced.py` (each reason, by competition; the cap; no `miss` key when all priced); full suite (927) and `nametest.py` pass.

**Files:** `groupings.py`, `tests/test_football_unpriced.py`, `CLAUDE.md`, this entry.

**Not changed:** which legs are priced or how, any Card rule, the model, any record row. Diagnostic only.

**Roll back:** `git revert` the merge commit.

## 2026-11-14-5: the tennis tripwire judges the picks today's 85% floor takes (tag pending)

**What changed:** the Card's sport-off test (`groupings.card_legs_by_sport`) judges a sport with its own floor (tennis, 85% since `CARD_RULE` 10) on the legs that floor admits (`atFloor`); the every-leg tally stays and is shown as before, with `tripwireAll` beside it. The Bets scoreboard's tennis row reads "Under; judged at 85%+ (0 so far)" instead of "Watch: 9 more legs decide", and the nightly Card review adds the floor's own line.

**Why:** all 41 tennis Card legs in the record were priced under 85% (30 under rule 1, before any tennis floor); none has reached the Card since the floor went to 85%. Nine more tennis legs landing as quoted would have taken tennis off the Card on evidence from picks the rule no longer makes.

**Evidence:** `groupings-record.json` at 14 Nov: tennis 23 of 41 (56% v 71%, z -2.13), 0 legs at 85%+; on the pool 85%+ tennis four legs, all won (`claude/pool-order-of-play-2026-11-14.md`). `claude/card-tripwire-at-floor-2026-11-14.md`.

**Tested:** `tests/test_groupings_record.py` `test_floor_sport_judged_on_legs_the_floor_admits` (under-floor legs fire the every-leg test, not the tripwire; sports without a floor unchanged), the floor test moved to 86% legs; `tests/test_card_review_post.py` `test_floor_line_for_a_sport_with_its_own_floor`; full suite and `nametest.py` pass; the scoreboard rendered at 1280 and 400 wide.

**Files:** `groupings.py`, `index.html`, `tools/card_review_post.py`, both test files, `claude/card-tripwire-at-floor-2026-11-14.md`, `CLAUDE.md`, this entry.

**Not changed:** any `CARD_*` constant, `CARD_RULE`, the live Card, the model, any record row.

**Roll back:** `git revert` the merge commit.

## 2026-11-14-4: the pool remembers when a tennis order of play arrived (tag pending)

**What changed:** the pool archive now stamps `timeSet` and `whenSet` once on a tennis row first written on an estimated start (`timeEst`), from the first build before the start that has the real time. The Card replay, the funnel and the price-gap count read `groupings.pool_time_est`, so such a leg is no longer refused as "no order of play" for ever.

**Why:** `timeEst` stayed as first written, so the replay and the funnel refused every tennis match archived before its order of play, though the live Card re-reads it and can admit it once timed: 21 pool rows at 14 Nov, all played at a real time hours later (Ruud estimated 10:00, played 17:05). The funnel's tennis "no-time" column was counting them. Forward only: old rows keep their flag; none was within reach of the 85% tennis floor.

**Evidence, tennis legs (HQ's top Card task):** 177 settled tennis pool legs; 60-70% model calls landed 58.8% v 64.6%, bookmakers 60-70% 12 of 27; 70%+ on quote; 85%+ four legs, all won. The shortfall is in the band the Card's floor already keeps off. `claude/pool-order-of-play-2026-11-14.md`.

**Tested:** `tests/test_card_pool_replay.py` `test_order_of_play_clears_estimate` (stamped once, a new estimate does not stamp, nothing after the start, `timeEst` unchanged); full suite and `nametest.py` pass.

**Files:** `groupings.py`, `tools/card_replay.py`, `tools/card_funnel.py`, `tests/test_card_pool_replay.py`, `claude/pool-order-of-play-2026-11-14.md`, `CLAUDE.md`, this entry.

**Not changed:** any Card rule, the live Card, the model, any archived row.

**Roll back:** `git revert` the merge commit.

## 2026-11-14-3: a league table still missing results is flagged (tag pending)

**What changed:** after the lagging fill, a league with five or more unplayed fixtures dated more than three days back (`build.stale_leagues`, `STALE_MIN`, `STALE_GRACE`) has its fixtures flagged under Celtic's Law with the reason (`stale_reason`): today only the Czech First League, "missing 41 results from 9 Oct on". Flagged rows drop a tier and stay off the Daily List, the reserve, the Card's pool and the Edge flag, as every Celtic row does. API-Football and football-data leagues meeting the count are logged as `stale watch`, not flagged.

**Why:** ESPN's cze.1 slug returns nothing this season, so the 13 Nov lagging fill scored no Czech result and every Czech fixture since October has been priced on a table that stops at early October, shown as an ordinary row (one at 86% on 8 Nov). With the wider leagues on the Card since 11 Nov, a Czech favourite could have reached a group on six-week-old ratings.

**Tested:** `tests/test_lagging_results.py` `StaleLeagues` (four cases); full suite and `nametest.py` pass; local build on the cached ESPN rows flags cze.1 alone and the 21-22 Nov Czech rows carry the reason; the row's flag rendered at 1280 and 400 wide.

**Files:** `build.py`, `tests/test_lagging_results.py`, `claude/stale-league-flag-2026-11-14.md`, `CLAUDE.md`, this entry.

**Not changed:** any probability, the model, calibration, any Card rule. The Czech table itself still needs a second source.

**Roll back:** `git revert` the merge commit.

## 2026-11-14-2: the Belgian Pro League back on the board, its table complete (tag pending)

**What changed:** a league whose openfootball file has no fixture dated from today on (`build.exhausted_codes`; today only Belgium) now takes its fixture window from ESPN under openfootball's spelling (`build.fill_window`), and its ESPN results for pairings the file lists only as "datum TBC" are added to its table (`fill_lagging(append=True)`) instead of dropped.

**Why:** the Belgian 2026-27 file dates rounds 1 to 7 only, so no Belgian Pro League game has been on the board, the Daily List, the Edge flag or the Card since 20 Sep, and 37 of its 99 results to 13 Nov had no fixture to fill. On the cached ESPN rows: 61 filled and 37 dropped before, 98 scored after (61 + 37), every club on 11 games, no pairing twice, every name matched once.

**Tested:** six new cases in `tests/test_lagging_results.py` (only a league with nothing ahead, undated-round result added, a listed pair never added, off by default, all or nothing on names, window fixtures under the primary spelling and never twice); full suite and `nametest.py` pass; a fast build ran (no ESPN here). CI's first build should print `window be.1` and `lag be.1: 98`.

**Files:** `build.py`, `tests/test_lagging_results.py`, `claude/belgium-undated-rounds-2026-11-14.md`, `CLAUDE.md`, this entry.

**Not changed:** the model, constants, calibration, any Card rule, the parser's rule that an undated match is not shown.

**Roll back:** `git revert` the merge commit.

## 2026-11-14: the context check pauses itself at the API usage limit, and says so (tag pending)

**What changed:** when the Messages API refuses for the key's usage limit, the context check stops for the build, records the time access returns (`pausedUntil` in `groupings-archive/context-ledger.json`), makes one probe call a build until then (a refused call costs nothing), and resumes by itself when the probe gets through or the time passes. The Bets tab's Card section says the check is paused until that date and that no pick is being kept off for news; the nightly Card review says so in bold; the build log says "paused until".

**Why:** at 00:24 UTC on 14 Nov the key reached its monthly limit ("regain access on 2026-12-01"), after 25 reads on each of 12 and 13 Nov. Every later build would ask again for every due pick and fail, while the page still said "with the context check" over picks nobody had read. No Card rule changes: only an "against" verdict ever vetoed, so unread picks are admitted as before rule 9.

**Tested:** `tests/test_context_review.py` (limit time parsed, one refusal stops the build, the pause holds across builds with one probe each, a probe that gets through resumes it, it clears after the date, the ledger keeps 14 days and the pause), `tests/test_card_review_post.py` (bold pause line); full suite and `nametest.py` pass; the Card section rendered at 1280 and 400 wide.

**Files:** `context_review.py`, `groupings.py`, `index.html`, `tools/card_review_post.py`, both test files, `claude/context-paused-2026-11-14.md`, `CLAUDE.md`, this entry.

**Not changed:** `CARD_CONTEXT`, any Card rule, `DAILY_READS`, the record.

**Roll back:** `git revert` the merge commit; then delete `pausedUntil` from `groupings-archive/context-ledger.json` if it is set.

## 2026-11-13-14: the nightly Card review opens with what the live Card published (tag pending)

**What changed:** the nightly Card review issue now starts with the live Card's own output over the last 14 finished days (`card_review_post.live_days_section`): days with a group, groups, the last day a group was published, the rules they ran under, and in bold a run of three or more empty days. Full-rule Card groups only, not the wider-rule filler or the paper Model card.

**Why:** the Card has published no group since 10 Nov (rule 6's last; rules 7 to 11 went live on 11 Nov), and nothing in the review said so. Its replay tables read rules against each other on the pool, not what the page put up. Over 31 Oct to 13 Nov: 17 Card groups on 9 of 14 days, then 11, 12 and 13 Nov empty. That is the rule as set (empty days stay empty, Douglas 11 Nov), and every volume relief replayed so far failed the gate, so this is a line to read, not a trigger.

**Tested:** `tests/test_review_live_days.py` (empty run, filler and Model card excluded, today not read, missing folder); full suite and `nametest.py` pass.

**Files:** `tools/card_review_post.py`, `tests/test_review_live_days.py`, `CLAUDE.md`, this entry.

**Not changed:** any Card rule, the page, the record.

**Roll back:** `git revert` the merge commit.

## 2026-11-13-12: tennis legs in the groups, gap located, no rule to ship (tag pending)

**What changed:** a dated note only, `claude/tennis-legs-gap-2026-11-13.md`.
**Evidence:** 71 of 109 distinct settled tennis legs won v 84.4 expected. No attribute (gap to market, round, opposition, rule, model band) isolates it; the bookmakers' implied chances were as high as the model's; legs since the 85% floor (1-13 Nov) are 11 of 14 v 11.2. No tennis price history to replay a rule on, so Rule 3 gates cannot be run.
**Files:** `claude/tennis-legs-gap-2026-11-13.md`, `RELEASES.md`.
**Not changed:** `CARD_SPORT_MIN`, the tripwire, any model constant.
**Roll back:** `git revert` the merge commit.

## 2026-11-13 Belgian openfootball file parsed properly (tag pending)

**What changed:** `parse_fixture_txt` now reads a score after the away side separated by one space ("KV Kortrijk 3-0") and drops a "(*)" annotation from club names, so the junk names `KV Kortrijk 3-0` and `Lommel SK (*)` no longer appear. `è` is folded in `_base` and four ESPN spellings are aliased (Racing Genk, Royal Charleroi, Sint-Truidense, Union St.-Gilloise); Standard Liege matches once `è` folds.
**Evidence:** the 2026-27 Belgian file holds one scored match (Club Brugge 3-0) and rounds 8+ are undated, so the lagging fill can now match all names; check the next build's `lag be.1` line. `tests/test_belgium_parse.py` added; nametest and the suite pass.
**Files:** `sources.py`, `tests/test_belgium_parse.py`.
**Not changed:** Czechia (`cze.1` returns 0 from ESPN's slug), no model constants.
**Roll back:** `git revert` the merge commit.

## 2026-11-13-11: four more lagging leagues matched (tag pending)

**What changed:** the first CI build of release 2026-11-13-10 filled 382 results across eight leagues and held seven back on unmatched ESPN names, as designed. Six aliases (Athletico-PR, Atlético-MG, Red Bull Bragantino, Deportivo, NEC Nijmegen, Erzurum BB) and five accent folds in `sources._base` (ã õ ê ô and the combining dot under a lowered "İ", for Famalicão, Guimarães, Başakşehir) let Brazil, Spain, the Netherlands, Portugal and Turkey fill on the next build.

**Evidence:** deploy run 43468024759's `lag` lines; the stale-unplayed warning fell from 789 to 407. `claude/openfootball-lag-2026-11-13.md` (CI section).

**Tested:** `nametest.py` all clear (rated pool 1124 clubs, none resolving elsewhere); `tests/test_lagging_results.py` adds the nine pairs; full suite passes.

**Not changed:** Belgium (its 2026-27 file parses with no scores and junk names: a parser fault, filed as an issue), Czechia (ESPN returns nothing), any model constant or Card rule.

**Roll back:** `git revert` the merge commit.

## 2026-11-13-10: the core leagues see their October and November results (tag pending)

**What changed:** openfootball's 2026-27 files stopped scoring matches after 20 Sep 2026, and the build took the current season for its fifteen whole-season leagues (Premier League, Championship, LaLiga, Bundesliga, Serie A, Ligue 1, Eredivisie, Primeira Liga, Scottish Premiership, Austria, Greece, Czechia, Brazil, Turkey, Belgium) from those files alone. The build now walks ESPN from the day after each league's last scored fixture and scores the blank fixtures under openfootball's spelling (`build.lagging_codes`, `build.fill_lagging`, `sources.topup_current(since=)`), cached in `current/` like the existing top-up.

**Evidence:** 746 played matches missing on 13 Nov (six rounds of the Premier League; Belgium no current season at all), the CI warning's 789 with football-data's leagues. Since rule 7 the Card's football picks and the Edge flag read these tables. `claude/openfootball-lag-2026-11-13.md`.

**Guards:** a result fills only the blank fixture of the same home and away clubs within 21 days, never one openfootball scored (the primary source wins); one unmatched or doubly matched ESPN club fills nothing for that league and is named in a `::warning::` (Rule 6); a failed lag walk is never marked done. Five aliases from the cached Austrian, Greek and Scottish rows.

**Tested:** `tests/test_lagging_results.py` (12 tests: fill, primary wins, window, moved match, all-or-nothing names, lag selection, failed walk retried, aliases); the cached at.1, gr.1 and sco.1 rows against their 2026-27 files match every club; full suite and `nametest.py` pass; a sandbox build runs the path (ESPN unreachable here, so CI's first build is the real check: look for the `lag <code>: N result(s) filled` lines).

**Not changed:** engine constants, calibration, any Card or list rule, the gap leagues' top-up.

**Roll back:** `git revert` the merge commit; the `current/` caches it adds are harmless and are ignored once the code is gone.

## 2026-11-13 Odds tab price coverage: write-up only (tag pending)

**What changed:** nothing on the site. A dated note on why no price source was added.

**Evidence:** pool 9-13 Nov has 0 unpriced football legs among 86; a missing price cost the Card 4 legs in two days (`claude/card-price-gaps-2026-11-12.md`). No API key in the sandbox, so no before/after.

**Files:** `claude/price-coverage-oscar-2026-11-13.md`, `RELEASES.md`.

**Not changed:** `groupings.py`, any model, any price rule.

**Roll back:** `git revert` the merge commit.

## 2026-11-13-9: free-source check for uncovered leagues, nothing to add (tag pending)

**What changed:** nothing on the page or the model. A dated line in `claude/data-expansion-plan.md` records the re-probe.

**Evidence:** football-data.co.uk `new/` returns the same 16 leagues (all already covered); openfootball 2026-27 `de.3.json`, `pt.2.json` and the 3. Liga file are 404. No free, automatable source exists for the remaining gaps (Rule 10).

**Files:** `claude/data-expansion-plan.md`, this entry.

**Not changed:** `sources.py`, `FDX`, the Daily List rules.

**Roll back:** `git revert` this release's commit.


## 2026-11-13-8: Serie D Girone C, test not run (tag pending)

**What changed:** nothing on the page or the model. A dated note records why the Serie D Girone C accuracy question (30% over 54 games) could not be tested.

**Evidence:** no af.428 history in `history/` or `cache/`, no `API_FOOTBALL_KEY` in the unattended run, and the scoreboard is off limits (Rule 1). No fit/check season, so no paired bootstrap and no gate read.

**Files:** `claude/serie-d-girone-c-2026-11-13.md`, this entry.

**Not changed:** `HOME_MULT`, `home-advantage.json`, any draw handling, the model.

**Roll back:** `git revert` this release's commit.


## 2026-11-13-7: briefing pushes logged, late ones named (tag pending)

**What changed:** nothing on the page or the Card. Each briefing push (07:00, 11:00, 16:00, 21:00 UK) is now logged with how many minutes after its slot it went, and a slot a late build skipped is logged as skipped (`groupings-archive/briefed.json` `log`, 21 days). The nightly Card review shows the table and names in bold any slot whose median push is over an hour late or that was skipped.

**Why:** the pushes come from deploy.yml's scheduled builds, which GitHub runs late at busy times: the 12 Nov lunch push went at 13:18 UK (2h18 late), the night push at 22:40 (1h40); on 13 Nov the 12:00 UTC build had not started by 12:40, so a deploy was dispatched by hand. Douglas bets at those times, so a late push is a late price. `claude/briefing-lateness-2026-11-13.md`.

**Tested:** `tests/test_briefing_log.py` (lateness in GMT and BST, skipped slots logged once, an old file without a log, trimming, `due_slot` unchanged, the review table); full suite and `nametest.py` pass.

**Files:** `notify.py` (`mark_sent`, `LOG_DAYS`), `tools/card_review_post.py` (`briefing_section`), `tests/test_briefing_log.py`, the note, `CLAUDE.md`.

**Not changed:** when briefings are sent, what they say, the deploy schedule (backup crons are a separate `needs-owner` pull request), any Card rule.

**Roll back:** `git revert` the merge commit; old `briefed.json` files read as before.


## 2026-11-13-6: the pool reads each fixture once (tag pending)

**What changed:** nothing on the Card. The pool archive holds a fixture the source moved to another day twice (the new day's file and the old one, with the stale start), and the replays, the funnel, the price-timing read and the Daily List's at-William-Hill record counted it twice or kept the stale row. They now read the pool through `groupings.pool_rows`, one row a fixture, its latest placement. "How it went"'s at-Hill line drops three double-counted picks.

**Evidence:** 68 of 2,650 pool picks sat in two or more day files at 13 Nov (38 tennis, 25 football, Drina Zvornik on 13 and 14 Nov). Replay legs 759 to 756 (1,533 to 1,511 with `--recover`), every variant's groups unchanged; funnel legs at a real price 729 to 740 (the stale row was the unpriced one); `listAtBook` at Hill 18/18 to 17/17. `claude/pool-moved-fixtures-2026-11-13.md`. Eight new tests (`tests/test_pool_rows.py`); full suite and `nametest.py` pass.

**Files:** `groupings.py` (`pool_rows`, `_same_fixture`, `POOL_MOVE_DAYS`; `list_at_book`, `context_record`), `tools/card_replay.py`, `tools/card_funnel.py`, `tools/price_timing.py`, `tests/test_pool_rows.py`, `claude/pool-moved-fixtures-2026-11-13.md`, `CLAUDE.md`.

**Not changed:** `archive_pool` and the archive itself, every `CARD_*` constant, the live Card, the model.

**Roll back:** `git revert` this release's commit.


## 2026-11-13-5: openfootball outage keeps the last good copy (tag pending)

**What changed:** nothing for a reader on a normal day. When openfootball (the source for most leagues' history and fixtures) is unreachable after three retries, the build now uses the last good copy of each file, with a warning naming the URL and its age, instead of silently rating those leagues with no data. A 4xx (file not carried) is still an answer and never falls back. With no earlier copy the error is raised as before and the existing fallbacks run.

**Evidence:** `_get` had retries but no fallback, unlike football-data.co.uk (`_fdx_text`), so a single outage meant empty history and fixtures for every openfootball league. Three new tests with a fake failing source in `tests/test_source_failures.py`; full suite and `nametest.py` pass.

**Files:** `sources.py` (`_get`, `_raw_keep_path`, `_raw_last_good`), `tests/test_source_failures.py`, `RELEASES.md`.

**Not changed:** the model, ESPN, football-data and API-Football handling, the stale-fixture check in `build.py`.

**Roll back:** `git revert` this release's commit.


## 2026-11-13-4: fixture audit of 13 Nov (tag pending)

**What changed:** nothing for a reader. A dated audit of `predictions/2026-11-13.json` added to `claude/data-integrity.md`.

**Evidence:** 1,153 rows: 0 unrated, 0 date/kick-off mismatches, 0 duplicate keys, no club at two kick-offs at once. 22 swapped-team pairs are two-leg or return fixtures; 2 same-direction pairs are a known reschedule (Unisport Bafang v Canon) and a double friendly (Tahiti v Cook Islands); 6 folded-name splits are different feeds or different clubs, rated as such. `nametest.py` passes.

**Files:** `claude/data-integrity.md`, `RELEASES.md`.

**Not changed:** matcher, `LIVE_NAMES`, archive keys.

**Roll back:** `git revert` the commit.


## 2026-11-13-3: tests for the international rating fit (tag pending)

**What changed:** nothing for a reader. `tune_international.py` (371 lines, the international rating fit) was the largest module with no test at all. 16 tests now pin tournament tiers, row parsing (unplayed and pre-cutoff rows dropped, neutral only on "TRUE"), recency and tier weights, the fit's ordering and its shared-shift fix, `outcome` summing to 1, `score` (unrated skipped, baseline), and the paired bootstrap (deterministic, directional).

**Evidence:** all 16 pass against the current code; no bug exposed, so no code changed. Full suite and nametest pass.

**Files:** `tests/test_tune_international.py`, this entry.

**Not changed:** any model, constant or data file.

**Roll back:** `git revert` the merge commit.


## 2026-11-13-2: the Card's bookmaker read on the same picks (tag pending)

**What changed:** advisory only. The nightly Card review now sets each UK bookmaker against William Hill (the Card's book) on the picks both priced, at the first and the last pre-start price, with the settled singles return at each, and the best UK price against Hill. It says in bold when a book pays more than Hill on both counts, as a question for Douglas.

**Why:** issue #156. The review ranked each book against the average on its own set of legs, which cannot say whether Bet365 beats William Hill on the same pick.

**Evidence:** Card-rule legs in the pool, 30 Oct to 13 Nov: Bet365 +1.06% a pick over Hill on 88 paired football picks over 11 days (ahead on 10 days, p 0.000), about +3% on a three-pick 2x; settled singles -2.25% at Hill v -1.11% at Bet365. Betfair (-0.95%) and BetVictor (-1.27%) are behind Hill. Best UK price pick by pick +1.58%. NBA and tennis too few paired. `claude/card-book-paired-2026-11-13.md`.

**Tested:** `tests/test_book_vs.py` (pairing, both tails, ties read as neither, too few, review lines); full suite and nametest.

**Files:** `tools/price_timing.py`, `tools/card_review_post.py`, `tests/test_book_vs.py`, the note, `CLAUDE.md`.

**Not changed:** `CARD_BOOK` (Douglas's book), any Card rule, the page.

**Roll back:** `git revert` the merge commit.

## 2026-11-13: the two-day group finds its best group, and an empty day says why (tag pending)

**What changed:** (1) a day with no Card group that borrows the next day's picks (`CARD_SPAN`) now takes the best group that holds one of its own picks; before, it took the best group of both days and gave up if that held none of the first day's. (2) An empty day on the Bets tab now says why: too few picks, too many from one competition, or, as on 13 and 15 Nov, three picks that clear the rule but together pay more than a 2x group can (13 Nov: 3.51, over 3.00). It used to say "too few picks" whatever the reason.

**Why:** the span is Douglas's rule (12 Nov) and was built narrower than he asked; the page gave the wrong reason on the first empty day it was read. `claude/card-empty-day-why-2026-11-13.md`.

**Tested:** `tests/test_card_span.py` (two new tests; the first failed on the old code), `tests/test_card_short.py`; full suite and nametest; the Bets tab rendered at 1280 and 400 wide on the 13 Nov pool.

**Files:** `groupings.py` (`best_card` `need`, the span pass, `card_short`, `cardShort` per day), `tools/card_replay.py` (`build_span`), `index.html` (`cardShortText`), tests, the note, `CLAUDE.md`.

**Not changed:** any `CARD_*` constant, `CARD_RULE`, the band, the record.

**Roll back:** `git revert` the merge commit.

## 2026-11-12-10: the playbook's "place late" line follows the evidence (tag pending)

**What changed:** the Card's playbook no longer says the last price paid about 2 points more than the first. Its first habit is now written from the price-timing check on every build: "Place once, late" with the gain only while settled Card-rule picks show one (50+ legs, day-resampled p <= 0.10), "Place once, early" if the read turns, and otherwise "Place once, before the first start" (nearer it than not, as a group can change until its first start) with the plain read that the first and last prices paid about the same. Today it reads the last: 174 settled picks to 12 Nov.

**Why:** the line quoted the 10 Nov read (+1.95 points late on 104 legs, p 0.011). On 12 Nov the same test gave -0.25 points on 174 legs, p 0.70, and on the rule 6 legs of the same days, rebuilt, +0.32. The page was telling people to wait for a gain the record no longer shows. `claude/place-late-faded-2026-11-12.md`.

**Tested:** `tests/test_price_timing.py` (`page_read`, `timing_page` returns None on failure); full suite and nametest; Bets tab rendered at 1280 and 400 wide from a scratch build.

**Files:** `tools/price_timing.py` (`page_read`), `groupings.py` (`timing_page`, `timing` in `groupings-data.js`), `index.html` (`placeHabit`), `tests/test_price_timing.py`, `claude/place-late-faded-2026-11-12.md`, `CLAUDE.md`.

**Not changed:** any Card rule, push or briefing time, the nightly review.

**Roll back:** `git revert` the merge commit.

## 2026-11-12-9: the nightly Card review shows both sides of the gate (tag pending)

**What changed:** the nightly Card review issue now puts each rule 7 variant's pool read beside its football-data seasons (`cardM7Paired` in `card-legs-history.json`, which tune.yml commits on Mondays), with a gate verdict per variant: passes, or fails and why (pool legs short of 100, pool p(worse), or the football-data season it lost). A variant ahead on the pool but behind live on any football-data season is named as not a candidate. When one passes every side the review says so in bold, so the next build session acts. Variants that built nothing on the replayed days (short, notennis, tennis80 on 12 Nov) leave the "watch" list and are named apart: their +0.44 a day was only live's losses.

**Why:** on 12 Nov the review listed `m7under5` as ahead of live at p(worse) 0.014 while the five football-data seasons had already refused it (behind in all five, pooled p(worse) 0.99, `claude/card-m7under5-seasons-2026-11-12.md`). The gate in CLAUDE.md has three sides; the review showed one, inviting the next session to reopen a settled question.

**Tested:** `tests/test_card_review_post.py` (refused on seasons, identical to live, full pass, a missing season, nothing on file, the empty variant); rendered against a local `card_replay.py --since 2026-10-29` run. Until Monday's tune.yml commits `cardM7Paired`, the section says no paired season read is on file.

**Files:** `tools/card_review_post.py`, `tests/test_card_review_post.py`, `CLAUDE.md`.

**Not changed:** any Card rule, the replay, the gate itself.

**Roll back:** `git revert` the merge commit.

## 2026-11-12-8: the context check reads Daily List picks too (tag pending)

**What changed:** every Daily List pick at 75%+ now gets a context read (team news, rotation, motivation, table, goals, last five) after the Card's picks, football first, then NBA, tennis, college basketball and the rest, within 25 reads a day. Sonnet reads Card picks, football and NBA; Haiku the rest. Each read shows as a Clear / Caution / Against flag beside the price on the Daily List, sport tabs and Starred, and in full in the slip checker. Display only: the model's number never moves, and only Card picks are vetoed.

**Why:** Douglas: "I just feel now I've made a shortlist from the daily games I could do with more context and understanding or flags", within his plan's $100 monthly API credit.

**Cost:** about $2-3 a day at the cap (first reads cost $0.20-0.25 each on Sonnet).

**Files:** `context_review.py` (`priority`, `model_for`, `DAILY_READS`, ledger), `groupings.py` (`CX_LIST_MIN`, `context_page`), `index.html` (`cxChip`, slip checker), `tests/test_context_review.py`, `claude/context-check-2026-11-11.md`, `CLAUDE.md`.

**Roll back:** `CX_LIST_MIN = 1.01` reads Card picks only; `git revert` the merge commit.

## 2026-11-12-7: damping the FIFA ranking's big lifts tested and rejected (tag pending)

**What changed:** nothing in the model. `tools/fifa_lift_damping.py` tests eleven ways to soften the ranking's big lifts on ranked internationals (fit Oct 2022-Sep 2023, check Oct 2023-Oct 2024); none passes the gates. Note `claude/fifa-lift-damping-2026-11-12.md`, a line in CLAUDE.md's Tested and rejected.

**Roll back:** `git revert` the merge commit.

## 2026-11-12-6: two-day Card groups when a day makes none (tag pending)

**What changed:** a day whose picks make no Card group now tries one group from its own qualifying picks plus the next day's, under the same rule, holding at least one of its own (`groupings.CARD_SPAN`). It is open until its first start, labelled "two days" on the Bets tab, kept in the Card record and apart as `cardSpan`; the next day's Card never reuses its picks.

**Why:** Douglas: "if you can't make a card on 1 day - then look to the next day ahead to combine fixtures to be able to create a card."

**Evidence:** pool replay `span2`: two more days with a group (17 v 15), return +31% v +33%, paired p(worse) 0.49. Owner's call under the 100-leg gate. `claude/card-span-2026-11-12.md`.

**Files:** `groupings.py`, `index.html`, `tools/card_replay.py` (`span2`), `tests/test_card_span.py`, `claude/card-span-2026-11-12.md`, `CLAUDE.md`.

**Not changed:** the leg rule, stakes, the 2x shape.

**Roll back:** `CARD_SPAN = False`, or `git revert` the merge commit.

## 2026-11-12 (tag pending): the value demand's relief refused on five seasons

**What changed:** advisory only. The football-data Card replay now runs `m7under5` (the model up to 5 points under the bookmakers) and `m7core`, and pairs every rule 7 variant against live by day, per season and pooled (`cardM7Paired`, `cardM7Pooled`).
**Why:** the 12 Nov nightly review had `m7under5` well ahead of live on the pool (p(worse) 0.014, 45 legs) a day after it read well behind. It had never been run on football-data.
**Evidence:** five seasons, 912 legs: behind live in every season, pooled -0.31 units a day, p(worse) 0.99; 304 groups -6.9% (120 won v 120.5 expected) v live 162 groups +9.6%. On the pool it leads only at first real prices (p(worse) 0.10), is level on `--recover` (0.51) and behind at closing (0.63). The value demand stays. `m7core` equals live on football-data (all core leagues), so the wider-leagues rule is read on the pool only. `claude/card-m7under5-seasons-2026-11-12.md`.
**Files:** `tools/card_legs_history.py`, `tests/test_card_m7_paired.py`, `claude/card-m7under5-seasons-2026-11-12.md`, `CLAUDE.md`.
**Not changed:** the live Card, any CARD_* constant, the page, the record.
**Roll back:** `git revert` the commit.


## 2026-11-12 (tag pending): the Card review counts legs lost to a missing price

**What changed:** advisory only. The Card funnel and the nightly Card review now count the legs with no bookmaker price that pass every other Card condition (`price_gaps`), split into days already started (lost) and days still to come.
**Why:** the Card was empty on 11 and 12 Nov, and 943 pool legs from 6 Nov were "estimate only". If those would have cleared, the price feed was the lever.
**Evidence:** from 10 Nov (every leg keeps its first real price) a missing price cost four legs on started days (Ýokary Liga 2, Eerste Divisie 1, one tennis); none was the leg a group lacked. 57 legs for 13-15 Nov are still unpriced, mostly lower-tier football. Price coverage is not what starves the Card now. `claude/card-price-gaps-2026-11-12.md`.
**Files:** `tools/card_funnel.py`, `tools/card_review_post.py`, `tests/test_card_funnel_gaps.py`, `claude/card-price-gaps-2026-11-12.md`, `CLAUDE.md`.
**Not changed:** the live Card, any CARD_* constant, pricing, the page, the record.
**Roll back:** `git revert` the commit.


## 2026-11-12 (tag pending): two-pick Card groups replayed and refused

**What changed:** advisory only. `m7legs2` pre-registered in the Card replay (the 2x may be two picks as well as three to five), on the pool and the football-data seasons.
**Why:** the live Card built nothing for 11 or 12 Nov. On 11 Nov five NBA picks cleared the full rule at 1.53-1.64, but any three pay 3.6x+, over the 2x band, and a group needs three.
**Evidence:** pool 30 Oct to 15 Nov: 17 groups v live 7 at first real prices (p(worse) 0.47), 25 v 16 on `--recover` (+12% v +51%, p(worse) 0.80), -11% v +6% at closing prices. Football-data 2025-26: 114 groups, 43 won v 53.3 expected, -18% v live +22%, 8 losing months of 10. The extra groups are the weak ones. `claude/card-m7legs2-2026-11-12.md`.
**Files:** `tools/card_replay.py`, `tools/card_legs_history.py`, `tests/test_card_m7legs2.py`, `claude/card-m7legs2-2026-11-12.md`, `CLAUDE.md`.
**Not changed:** the live Card (still 3-5 picks), any CARD_* constant, the page, the record.
**Roll back:** `git revert` the commit.


## 2026-11-12 (tag pending): the rule 6 replay keeps its own tennis floor

**What changed:** advisory only. The Card replay's rule 6 family had inherited the live tennis floor (85% since CARD_RULE 10), so `rule6`, `notennis` and `tennis80` replayed identically and `rule6` built almost nothing. `RULE6` now pins tennis at 75%, the floor rule 6 ran with.
**Evidence:** pool 30 Oct to 14 Nov, `--recover`: `rule6` 3 groups before, 11 groups 5 won +8% after (matches the 11 Nov morning read); `notennis` v `rule6` +0.23 units a day, p(worse) 0.42, where it read "identical" before. `claude/card-replay-rule6-tennis-2026-11-12.md`.
**Files:** `tools/card_replay.py`, `tests/test_card_replay_rule6_family.py`, `claude/card-replay-rule6-tennis-2026-11-12.md`, `CLAUDE.md`.
**Not changed:** the live Card, any CARD_* constant, `tennis75`, the page, the record.
**Roll back:** `git revert` the commit.


## 2026-11-12 (tag pending): At a glance scrolls back a week

**What changed:** At a glance on the Daily List now holds the last seven days as well as the week ahead. It opens on today; swipe or tap back through each past day's list, every pick at its start time, won or lost, with the day's score on its tab (e.g. "Sun 8 18/21").
**How:** `daylist.py` writes `past` into `daylist.js`: each of the last seven UK days' lists as they stood before each game started (the same membership rule as today's pin), with results from the record files. About 36 KB.
**Files:** `daylist.py`, `index.html` (`glancePast`, `todayGlance`, `glanceDay`, `glanceSync`), `tests/test_daylist.py`.
**Checked:** browser at 400 and 1280 wide: tabs Thu 5 to Mon 17, opens on Today, the selected tab kept in view, the page does not move, no sideways scroll.
**Not changed:** the list, the record, How it went.
**Roll back:** `git revert` the commit.


## 2026-11-11 (tag pending): the Card takes the wider leagues (CARD_RULE 11)

**What changed:** football picks from the wider leagues (API-Football's, e.g. Bosnia RS) can now go on the Card; cups and internationals stay out, and a core-league pick still comes first at an equal chance.
**Evidence:** Douglas on Leotar (1.52, model 67% v 59%), kept off only by the league limit: "This should have been on. So relax all rules that would of said otherwise." The replay he was shown leans the other way (wider 28 groups, 15 won, +32% v core only 12 groups, 8 won, +69%); the owner's call. `claude/card-wider-leagues-2026-11-11.md`.
**Files:** `groupings.py`, `tools/card_replay.py` (`m7core`; rule 6 replays pinned to core), `index.html` (wording), tests, `CLAUDE.md`.
**Not changed:** the tennis floor, the price range, the 60% model floor, the value demand, cups and internationals.
**Roll back:** `git revert` the commit, or set `CARD_CORE_ONLY = True`.


## 2026-11-11 (tag pending): SportsGameOdds prices US games from its consensus line

**What changed:** SportsGameOdds now prices the US games nothing else priced. The build log (#259) showed 47 of its games matched ours by name and all 47 came with no per-bookmaker prices on the free plan; each still carries SportsGameOdds' consensus price, which is now used (labelled "SportsGameOdds consensus").
**Evidence:** deploy log after #259: `named 47, noBooks 47`, odds keys `points-home-game-ml-home` / `points-away-game-ml-away` present. Betfair answers our CI with its HTML "Forbidden" page, a location block: not fixable from GitHub's US runners.
**Files:** `free_prices.py`, `tests/test_free_prices.py`.
**Not changed:** any model number or pick; prices are display and Card veto only.
**Roll back:** `git revert` the commit.


## 2026-11-11 (tag pending): why the free price sources priced nothing, shown in the build log

**What changed:** the first build with keys showed SportsGameOdds fetching 128 games and matching none, and Betfair's login refused with a bare HTTP 403. The build log now shows, when SportsGameOdds matches nothing, what one of its games and one of our legs look like (names, start), and how far each got (named, no side, no books); an HTTP error from any free source now carries the reply's first line, so a location block reads as one.
**Evidence:** deploy run 43105328356 (#250's log line): `sgo: matched 0, legs 128, monthObjects 128`, `betfair: error HTTP Error 403: Forbidden`, `matchbook: no key`.
**Files:** `free_prices.py`, `tests/test_free_prices.py`.
**Not changed:** any price, any pick.
**Roll back:** `git revert` the commit.


## 2026-11-11 (tag pending): tennis at 85% on the Card, "Under 80" on tennis rows, rows keep their place

**What changed:** the Card takes a tennis pick only at 85%+ on the model and its tested rate (was 75%), `CARD_RULE` 10. Every tennis row under 80% shows "Under 80". Opening or starring a row no longer moves the page: the tapped row stays where it was on screen.
**Evidence:** Douglas, after Casper Ruud lost at 1.22 on a Hill five-fold: "Tennis score must go lower", then "Both". Graded tennis lands on quote or above from 70% (1,422 picks), so the numbers stay; the Card's tennis legs landed 22 of 40 (z -2.2). Browser check at 390 and 1280: row top unchanged after opening, no sideways scroll. `claude/tennis-floor-85-2026-11-11.md`.
**Files:** `groupings.py`, `index.html`, `tools/card_replay.py` (`tennis75`), tests, `claude/tennis-floor-85-2026-11-11.md`, `CLAUDE.md`.
**Not changed:** any tennis number, the Daily List bar, UK-book pricing for 75-85% tennis (`BOOKS_SPORT_MIN`).
**Roll back:** `git revert` the commit.


## 2026-11-11 (tag pending): the Card's league limit read by the replay and the funnel, `m7wide` pre-registered

**What changed:** advisory only. Under rule 7/8 the Card's core-league limit was hard-coded in `groupings.model_fault`, so the funnel could not relax it and named the value demand as the one condition costing groups. `model_fault` now reads `CARD_CORE_ONLY` as `card_fault` does; it stays True, so the live Card is unchanged (replay `live` identical before and after). The funnel gains a "league" relief and `tools/card_replay.py` gains `m7wide` (the rule 8 Card with the wider API-Football leagues, cups and new leagues still out), registered before it was read.

**Evidence:** funnel, pool 6 to 14 Nov at real prices: 45 football legs kept off by the league limit alone v 14 by the value demand; days with a 2x 3 -> 4, groups 4 -> 9. `m7wide` v live: first real prices 19 groups +19% v 6 +82% (p(worse) 0.60); `--recover` 28 groups +32% v 12 +69% (p 0.44); closing p 0.76. 84 legs, under the 100-leg gate. `claude/card-m7wide-2026-11-11.md`.

**Files:** `groupings.py`, `tools/card_replay.py`, `tools/card_funnel.py`, `tests/test_card_m7wide.py`, `claude/card-m7wide-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** `CARD_CORE_ONLY` (True), `CARD_RULE`, the page, the record.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-6 Build log: one line per price source (tag pending)

For the owner: each build's log now prints what every price source did
(matched, calls, allowance, any error), so whether Betfair, Matchbook or
SportsGameOdds is working can be read straight off the Actions log.

Files: `groupings.py` (the summary print in `main`). Nothing on the page.

Roll back: `git revert` this commit.

## 2026-11-11 (tag pending): Own-band List admission re-run, note only

**What changed:** a note, no code. The rule was shipped on 20 Oct 2026; the replay re-run reproduces it.
**Evidence:** held out, rugby 426 at 78.9% -> 232 at 84.1% (dropped 72.7%, p(worse) 0.002); college basketball 3,792 at 78.9% -> 1,884 at 87.4% (dropped 70.5%, p 0.000); NFL 110 at 71.8% -> 62 at 77.4% (p 0.07). `claude/own-band-rerun-2026-11-11.md`.
**Files:** `claude/own-band-rerun-2026-11-11.md`, `RELEASES.md`.
**Not changed:** any code or bar.
**Roll back:** `git revert` the commit.


## 2026-11-11 (tag pending): Card tennis legs, note only

**What changed:** a note, no code. Tennis Card legs are 8 of 15 since 29 Oct (z -2.1), 23 of 41 in all (z -2.13), under the 50-leg tripwire.
**Evidence:** `claude/tennis-card-legs-2026-11-11.md`. Cuts are 3 to 8 legs a cell and no tennis price history exists to replay a rule; gates cannot be met.
**Files:** `claude/tennis-card-legs-2026-11-11.md`, `RELEASES.md`.
**Not changed:** `CARD_SPORTS_OFF`, `CARD_SPORT_MIN`, `CARD_RULE`.
**Roll back:** `git revert` the commit.

## 2026-11-11-16: the context check graded in the nightly Card review (tag pending)

**What changed:** advisory only. The nightly Card review issue gains a "context check" section: every settled pick the check read, by verdict (clear, caution, against), landed against the model's own number and the bookmakers' chance, from `groupings-record.json` `cardContext`. It carries the pre-registered review written into words: at 30 settled "against" picks, if they land at or above the model's number, the review says in bold that the next build session sets `CARD_CONTEXT = False`; otherwise it says the veto stays, or how many are still to come.

**Why:** the veto (CARD_RULE 9) went live untested on 11 Nov with a review at 30 "against" picks, but nothing printed its tally, so the review had no trigger. Same shape as the tennis tripwire.

**Files:** `tools/card_review_post.py` (`context_section`, `CONTEXT_REVIEW_AT`), `tests/test_card_review_post.py`, `claude/context-check-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** the Card's rule, the veto, the record.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-15: "Is it working?" made readable (tag pending)

**What changed:** the Bets tab's scoreboard was fourteen tiles of dense text. It is now one headline (groups won and lost, the win rate against expected, the return at the page's stakes), one plain verdict, a table of picks by sport with a status for each (on or above, slightly under, watch, coming off), and a "More numbers" fold holding the rest as a table (each Card rule, each window, late, wider-rule and paper groups, prices that shortened). The verdict now says when the Card is winning as often as expected but still losing money, rather than a green "on quote".

**Why:** Douglas: "This section is far too chaotic."

**Files:** `index.html` (`tbRecord`, CSS). Checked at 400px and desktop with the live record.

**Not changed:** any number; the record (`groupings-record.json`).

**Roll back:** `git revert` the merge commit.

## 2026-11-11-14: the model's backed picks, with their context verdicts, shown under the Card (tag pending)

**What changed:** the Bets tab lists every pick the Card's rule admits today with its context verdict (news, numbers, sources), open by default when they make no group and folded under the groups when there are spare ones. A pick the check reads "against" shows as kept off. Labelled not a bet. `groupings.card_picks` writes `cardPicks` per day; `cardPicksHtml` in `index.html`.

**Why:** Douglas, on 11 Nov's three verdicts (Pelicans, Knicks, Magic): "I can't see those". They made no group (three NBA picks; at most two a competition), and verdicts showed only on a group's picks.

**Files:** `groupings.py`, `index.html`, `tests/test_context_review.py`. Checked at 400px and desktop.

**Not changed:** the Card's rule, groups, the record.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-13: tidy-up: nine stale pull requests closed, their findings kept (tag pending)

**What changed:** nine pull requests that had clashed with newer code or been overtaken (#67, #68, #106, #121, #127, #137, #142, #148, #215) are closed. What they held of value is kept here:
- #67's fixture-detail copy re-applied: a call shown as No read only because of its Celtic's Law flag now says so and gives its own landed rate, rather than "close to the 33% you would get from guessing".
- The findings of #68 (habitual losers), #106 (Championship goals scale), #148 (attack/defence shrinkage) and #215 (prices by hour of first pricing), with their tools, under `claude/` and `tools/`, and listed under "Tested and rejected" in `CLAUDE.md`.
- #127 (MLB Elo retune) and #137 (college basketball Nov-Dec calibration) passed their gates but clash with today's `sports.json`; each is an `office-backlog` issue to redo and re-test on current code.
- Not kept: #121 (re-ran a rule already shipped, no new finding) and #142 (looser name matching for prices, yield never measured; superseded by the odds-for-every-game work, and a loose match is worse than a missed one).

**Files:** `index.html`, `claude/tuning-evidence.md`, `claude/att-def-shrink-2026-11-06.md`, `claude/championship-goals-scale-2026-10-29.md`, `claude/price-by-first-hour-2026-11-10.md`, `tools/att_def_shrink_eval.py`, `tools/championship_goals_scale.py`, `CLAUDE.md`.

**Not changed:** any model or rule.

**Roll back:** `git revert` the merge commit; the closed pull requests can be reopened on GitHub.

## 2026-11-11-12: the context check on every Card pick (tag pending)

**What changed:** before the Card is built, Claude reads every pick the Card's rule admits with live web search (team news, rotation, motivation, the table, goals for and against, last five) and gives it a verdict: clear, caution or against, with a one-line reason and sources. An "against" pick, with a source, is kept off the Card and a substitute takes its place (`CARD_CONTEXT`, `CARD_RULE` 9). Each Card pick shows its verdict, news, numbers and sources on the Bets tab.

**Why:** Douglas: "with added human contextual review it does much better ... I want this contextual review now. But also just a better understanding of the numbers."

**Evidence:** none yet: it cannot be replayed on past seasons. Every verdict is archived with the pool and graded forward (`groupings-record.json` `cardContext`, landed v the model's number by verdict). Review at 30 "against" picks.

**Files:** `context_review.py` (new), `groupings.py` (`CARD_CONTEXT`, `card_fault`, `context_record`, pool `context`), `index.html` (`ogContext`), `.github/workflows/deploy.yml` (the key to the groupings step), `tests/test_context_review.py`, `tests/test_card_model_rule.py`, `claude/context-check-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** the model, the Daily List, the Card's leg rule otherwise.

**Roll back:** `CARD_CONTEXT = False` stops the veto (reads still show); `git revert` the merge commit removes it.

## 2026-11-11-11: the Card replayed by payout, 1.5x to 3x (tag pending)

**What changed:** advisory only. `tools/card_replay.py` and `tools/card_legs_history.py` replay the Card at four payouts (`pay15`, `pay25`, `pay3`) and Douglas's ladder (3x, 2.5x, 2x, 1.5x a day), on the pool nightly and on football-data weekly.

**Evidence:** four full football-data seasons pooled: 2x (live) +10.3%, 1.5x +0.6% (wins 58%, steadiest), 2.5x -2.5%, 3x -7.1%, ladder -0.4%. Pool (14 days): 2x +69%, 1.5x +47% (16 of 19), 3x -19%, ladder -13%. `claude/card-payout-bands-2026-11-11.md`.

**Not changed:** the Card (2x, rule 8), the page.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-11 The list at William Hill counts every settled pick (tag pending)

For a reader: the "Daily List at William Hill" line in How it went and the
nightly Card review read 1 settled pick since 10 Nov when about 40 had
finished, because most US-sport pool rows were first archived days ahead,
before rows carried the game's id, so they never settled. They now settle
by team names and date, as the Card replay already did, and later builds
fill the missing id into the pool row. On the archive at 11 Nov the tally
goes from 1 settled pick to 35: 5 priced at William Hill (5 won, +2.0% at
Hill's price), 15 priced elsewhere and not at Hill, 15 with no UK price read.

Files: `groupings.py` (`name_indexes` and `settle_pool` moved in from
`tools/card_replay.py`, `list_at_book` uses them, `archive_pool` fills a
missing `id`), `tools/card_replay.py` (re-exports them), tests
(`tests/test_list_books.py`), `claude/list-at-hill-2026-11-10.md`.

Not changed: any model, the Daily List, the Card's rules, any price first
written to the pool.

Roll back: `git revert` this commit.

## 2026-11-11-5 Free price sources: Betfair, Matchbook, SportsGameOdds (tag pending)

For a reader: once their keys are added, three free feeds fill the games the
bookmaker feeds leave unpriced: the Betfair and Matchbook exchanges (nearly
every football league and tennis match; shown as Exch) and SportsGameOdds
(US sports). Until then nothing changes.

Files: `free_prices.py`, `groupings.py` (`price` order, `board_prices` `x`),
`index.html` (`priceChip` Exch), `.github/workflows/deploy.yml` (six secrets
to the groupings step), `tests/test_free_prices.py`,
`claude/free-prices-2026-11-11.md`, `CLAUDE.md`.

Roll back: `git revert` this commit.

## 2026-11-11-4 Odds for every game (tag pending)

For a reader: every game the build can price now shows its price on its row,
on every tab: William Hill's price when Hill has one, else the bookmakers'
average (Avg) with the best book in the tooltip. Tennis and the US sports had
no price on their rows before. Behind it, every tennis match and every US
game nothing else priced is now asked for (one credit a slate), football legs
the bulk prices missed get their own call, and the Odds API's daily
allowance scales with the account when it reports a paid plan. On the 08:51
build only 152 of 408 legs had a real price (tennis 0 of 17).

Files: `groupings.py` (`odds_api_caps`, `board_prices`, `FB_CALLS_MULT`,
the tennis and US `want`), `index.html` (`priceChip`), tests,
`claude/odds-all-games-2026-11-11.md`, `CLAUDE.md`.

Not changed: any model, the Daily List's admission, the Card's rules.

Roll back: `git revert` this commit.

## 2026-11-11-10: the Card's empty-day filler switched off (tag pending)

**What changed:** a day the model's picks leave empty now stays empty. The wider-rule filler (picks chosen on the bookmakers' numbers, 1.08 to 2.10 at 60%+) no longer builds (`groupings.CARD_FILLER` False). An open filler group drops off at the next build; a filler group already locked at its first start stays on the page and settles. The Bets tab's description of the Card says so.

**Why:** Douglas, after Monday 9 Nov's two filler groups lost (2.01, 3.07): "The groups must win at all costs. The source of truth is my model. But the groups need to surface games that will win." The filler is the one part of the Card not chosen on the model's own numbers, and its record is the weakest: live 1 of 3; pool replay (`fillwide`) 2 of 12 won against 4.14 expected, -54%; football-data at or under the price on both seasons.

**Evidence and its limits:** the pre-registered drop (100 pool legs, p(worse) 0.70+) was not reached (36 legs); the owner's call, with every sample pointing the same way. Under rule 8 the full rule builds no group on many days (11 Nov: no priced pick passes), so the Card will be empty more often.

**Files:** `groupings.py` (`CARD_FILLER`, `rules.card.filler`), `index.html` (Card description), `tests/test_groupings_card.py` (`WiderRule` runs with the switch on; `FillerOff`), `claude/card-filler-off-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** the full rule (`CARD_RULE` 8), the record (`cardWide`, `cardWideByRule` kept), the replay's `fillwide` variant.

**Roll back:** set `CARD_FILLER = True`, or `git revert` the merge commit.

## 2026-11-11-9: four API-Football leagues back on the board; an intermittent test made deterministic; the floor tile's "-0.0" (tag pending)

**What changed:** Vietnam's V.League 1 and 2 and Cameroon's Elite One and Two had left the board: the API marks their season in play by its later year ("2027", "2027-28"), so `sources.af_season_window` opened their date window after it closed and no fixture passed. A season whose nominal start is after today now reads from a year earlier; the season-year filter in `af_rows` still keeps only that season's matches. `tests/test_af_seasons.PoolFallback` picked its league from a set, so it changed with the hash seed and failed whenever it drew a Cameroon league (#238, failed once on #237's push run); it now pins one league and season, and a new test covers the ahead-of-calendar season. The Bets scoreboard's floor tile read "Under quote" and "-0.0 standard errors" at z -0.02; it rounds first and reads "On quote, 0.0".

**Evidence:** none of the four leagues in any `predictions/` file from 29 Oct to 11 Nov; `current/af-seasons.json` gives each `current` 2027. New tests fail on the old code. Suite OK (772), nametest clear, Bets tab checked at 1280 and 400 wide. A cloud sandbox cannot reach API-Football, so the leagues' return is confirmed by the next CI build.

**Files:** `sources.py`, `tests/test_af_seasons.py`, `tests/test_af_cups.py`, `index.html`.

**Not changed:** any model, the Card, the Daily List rule.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-8: the replay's rule 6 variants run on rule 6 again (tag pending)

**What changed:** `tools/card_replay.py` builds the variants pre-registered for the 30 Nov review on the rule 6 Card they were registered against (`RULE6`, `RULE6_FAMILY`, `patch_of`). Since rule 7 they were patched onto live, which reads none of their constants, so the 11 Nov review showed `under8`, `uncapped`, `rule5`, `opp7` and others "identical to live" and the rule 5 / opp7 / short fillers built nothing; `tools/card_legs_history.py`'s `cardRule5`, `cardUncapped`, `cardOpp7` and fillers go through the same code and would have repeated live on Monday. Family variants are now also paired against `rule6`, and the nightly review prints that line.

**Evidence:** pool, 30 Oct to 14 Nov (`--recover`): live (rule 8) 12 groups, 8 won, +69%; `rule6` 11 groups, +8%, v live -1.35 units a day (p(worse) 0.97); `rule5` v `rule6` +0.95 a day (p 0.05); `fillrule5` v live +0.62 (p 0.00). All under the 100-leg gate. New tests `tests/test_card_replay_rule6_family.py` (fail on the old code); suite OK (771), nametest clear. Note: `claude/card-replay-rule6-family-2026-11-11.md`.

**Files:** `tools/card_replay.py`, `tools/card_review_post.py`, `tools/card_legs_history.py` (comment), `tests/test_card_replay_rule6_family.py`, `claude/card-replay-rule6-family-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** any Card rule, the page, the record, rule 7/8's own variants.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-7: the Card's playbook says place late; the empty paper Model card leaves the Bets tab (tag pending)

**What changed:** the Card's playbook now opens "Place once, late": any time before a group's first start, nearer it than not. That advice lived in the plan, which came off the page on 11 Nov, so the page had been saying only "any time before". The "On paper: the Model card" fold no longer shows on days with no Model card group: since rule 7 the Card is the model's own picks and the paper Model card is not built, so the fold was always empty and still promised a 30 Nov comparison. Its scoreboard tile now reads "31 Oct to 10 Nov; since 11 Nov they are the card". The "Why these rules" line about the model rating picks above the bookmakers says the card followed it until 11 Nov.

**Evidence:** `claude/price-timing-read-2026-11-10.md`: on 104 settled Card-rule singles the last pre-start price returned +1.95 points over the first (day-resampled p 0.011, mostly football); a group can still be replaced until its first start, so a late slip matches what the record grades. Suite OK (767), nametest clear, Bets tab checked at 1280 and 400 wide (no errors, no sideways scroll).

**Files:** `index.html`, `CLAUDE.md`.

**Not changed:** any Card rule, the push times, the record, any model.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-6: the Card funnel and integrity check read the live rule (tag pending)

**What changed:** the nightly Card review's funnel (`tools/card_funnel.py`) now reads the Card's live rule (rule 8: the model's own picks, the 2x alone). Before, it matched rule 6's messages, so 217 football legs outside the core leagues showed as "price-range" and 79 legs as "other", it offered reliefs for conditions that no longer exist, and it reported a Card 3x column. It now has rule 7's own fault keys and reliefs, only the kinds the Card builds, and counts every 2x a day can take. `tools/card_integrity.py` raises `no-opposition-price` only on rule 6 groups, so the review does not open backlog issues for a condition the rule no longer reads. New pre-registered replay variant `m7under5` (the model up to 5 points under the bookmakers).

**Evidence:** pool 6-14 Nov: live builds a 2x on 3 days of 9 (4 groups); the value demand is the one condition that costs groups (8 groups without it). Its relief replayed: `m7under5` 14 groups, 6 won, +0%, v live 6 groups, 4 won, +82%; paired p(worse) 0.97 on 42 legs. The value demand stays. Suite OK, nametest clear, integrity 0 findings. Note: `claude/card-funnel-rule7-2026-11-11.md`.

**Files:** `tools/card_funnel.py`, `tools/card_integrity.py`, `tools/card_review_post.py` (comment), `tools/card_replay.py` (`m7under5`), `tests/test_card_funnel_model.py`, `claude/card-funnel-rule7-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** any Card rule, the page, any model.

**Roll back:** `git revert` the merge commit.

## 2026-11-11-5: the Card builds the 2x alone (CARD_RULE 8) (tag pending)

**What changed:** the Card now makes up to three 2x groups a day and no 3x. Douglas: "Just do better on the groups." The Bets tab's rule and staking lines say so. The 3x's record stays.

**Evidence:** six shapes of the model's-picks Card replayed. Football-data, five seasons, the model's legs: 2x only +9.6% pooled on 324 units v the current Card -3.3% on 409, ahead in 2024-25 (-0.4% v -17.9%) and 2025-26 (+22.0% v -6.3%), level in 2022-23 and 2023-24; the rule 7 3x positive in one season of four. Pool, every sport: 2x only 8 of 12 groups, +69%, v 10 of 23, +37%, p(worse) 0.29 (0.16 at first prices). A bigger edge demand made it worse. Under the 100-leg pool gate: the build session's call on Douglas's instruction. Suite OK, nametest clear, Bets tab checked at 1280 and 400 wide. Note: `claude/card-2x-only-2026-11-11.md`.

**Files:** `groupings.py` (`CARD_BUILD`, `built_kinds`, `CARD_MODEL_EDGE`), `index.html`, `tools/card_replay.py` (m7 variants, `with3x`), `tools/card_legs_history.py` (`cardM7`), tests, `claude/card-2x-only-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** the leg rule, stakes per group, the Daily List, any model.

**Roll back:** `CARD_BUILD = ("Card 2x", "Card 3x")` and `CARD_RULE = 7`, or `git revert` the merge commit.

## 2026-11-11-4: the Card is the model's own picks (CARD_RULE 7) (tag pending)

**What changed:** the Card now takes the model's own picks: each one the model rates 60%+ and at or above the bookmakers' chance, priced 1.15 to 1.90, with the group's chance the model's number. Douglas: "I want the model to pick higher than the bookmakers ... The model rules." Stakes, kinds, the bench and the filler are unchanged; the separate paper Model card stops (it would repeat the Card). The Bets tab's rule text and each group's footnote say so.

**Evidence:** replay on the pool and archive (14 days): the model's picks 23 groups, 10 won, +37%, legs 73.9% v 65.1% quoted; the rule 6 Card 10 groups, 4 won, -7%; paired p(rule 6 worse) 0.93. Live: the paper Model card 6 of 14 (+19%) v the Card 11 of 35 (-12%). Football-data 2025-26 disagrees (-8.2% on 70 groups) and 69 legs is under the 100-leg gate: the owner's call. Suite OK, nametest clear, Bets tab checked at 1280 and 400 wide. Note: `claude/card-model-rules-2026-11-11.md`.

**Files:** `groupings.py`, `index.html`, `tools/card_replay.py` (`rule6` variant), `tests/test_card_model_rule.py`, six Card test modules pinned to rule 6, `claude/card-model-rules-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** stakes, the filler, the Daily List, any model.

**Roll back:** `CARD_MODEL_RULE = False` and `CARD_RULE = 6`, or `git revert` the merge commit.
## 2026-11-11-3 Edge flag: opposition floor 4/1 (tag pending)

For a reader: a football favourite now carries the green Edge flag when the
other side is priced 4/1 (5.0) or more, down from 9.0. Douglas's call (10 Nov
evening, confirmed 11 Nov after seeing the bands). The page says plainly that
the five-season figures were tested at 9.0+, and that with the opposition at
4.0 to 6.0 the same favourites lost in every season and at 6.0 to 9.0 broke
about even. The Edge record is now split by rule.

Files: `groupings.py` (`EDGE_OPP_MIN`, `EDGE_RULE` 2), `score.py`
(`edge_of` rule, `edge_record` `byRule`), `tools/card_legs_history.py`
(`edge_legs` at the Edge floor), `index.html` (wording, record line),
tests, `claude/edge-floor-2026-11-11.md`, `CLAUDE.md`.

Not changed: the Card's opposition floor (`CARD_OPP_MIN` 9.0, rule 6).

Roll back: `git revert` this commit.


## 2026-11-11-3: the Card's filler takes only 60%+ favourites (tag pending)

**What changed:** the empty-day filler (the wider rule) now takes only picks the bookmakers make 60%+ favourites, like the full rule, not 55%+. Douglas, on Saturday 14 Nov's filler (Luton, Southend, Almere City): "Make sure all picks are more like Almere and less like Luton and Southend." Luton (the bookmakers 56%) is off; Saturday's filler is rebuilt on every build. Wider-rule groups carry `wideRule` (2), tallied apart in `cardWideByRule`; the page's filler lines read the floor from the rules.

**Evidence:** football legs the wider rule admitted, archive and pool, 30 Sep to 14 Nov: bookmakers under 60% -6.3% singles (107 legs), the worst band; 60%+ with the model within 5 points (Almere's shape) +0.9% (82); 60%+ with the model 5-10 under (Southend's shape) +7.4% (55), the best band, so Southend's shape is not refused. Whole filler replayed: -1% after v +0% before, fewer groups. The owner's call with the evidence pointing the same way, not a gate pass. Suite OK, nametest clear, Bets tab checked at 1280 and 400 wide. Note: `claude/card-filler-like-almere-2026-11-11.md`.

**Files:** `groupings.py`, `index.html`, `tools/card_legs_history.py` (docstring), `tests/test_groupings_card.py`, `tests/test_card_fillers.py`, `claude/card-filler-like-almere-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** the full rule, `CARD_RULE`, stakes, past graded groups.

**Roll back:** `git revert` the merge commit (the floor returns to 55%).
## 2026-11-11 Card: Douglas's mismatch rule tested against the price (tag pending)

**What changed:** `tools/card_legs_history.py` replays the rule Douglas
described after his 8-fold won (#224), exactly as pre-registered on the
issue: a top-quarter home side, 10+ points from its last five, scoring in
the league's top third and conceding in its bottom third, against a
bottom-half side with 5 or fewer from its last five and the opposite goal
record, both 6+ games played, home win at 1.15-1.60. The table is built from
football-data's season file, earlier dates only. Per season and pooled:
singles landed v the bookmakers' fair chance and return at average and best
price, slips of 2, 4, 6 and 8 legs a day, how many legs the Edge flag already
catches and how the rest do, and the split by the home side's games played
(6-10, 11-20, 21+) with the 4-folds. `mismatchPooled.verdict` applies the
issue's gate (ahead of the price in 4 of 5 seasons, pooled p(loss) at the
best price 0.30 or less). `edge_accas` now calls a shared `accas`; its output
is unchanged.
**Evidence:** CI run 42932321819, 2022-23 to 2026-27: 185 legs, landed
74.1% v 72.2% quoted, -3.7% at the average price, -1.2% at the best (p(loss)
0.60), ahead of the price in 3 seasons of 5: it does not beat the price. The
11-20 games band passes alone (55 legs, +12.0% at best) but 21+ loses (105
legs, -6.6%), so no flag. `claude/mismatch-rule-2026-11-11.md`.
**Files:** `tools/card_legs_history.py`, `tests/test_mismatch_rule.py`,
`claude/mismatch-rule-2026-11-11.md`, `CLAUDE.md`.
**Not changed:** the Card's rule, the Edge flag, any model, the page.
**Roll back:** `git revert` the commit.

## 2026-11-11-2 At a glance: swipe through the coming days; true-size labels sideways (tag pending)

For a reader: Today at a glance on the Daily List now holds today and each
coming day with list picks (up to seven), one panel a day: swipe across, tap
a day tab (with its pick count) or use the arrows. Each day has its own line
(won, lost, in play, to come, the first or next start) and its own timeline;
a dot still jumps to its pick. Douglas, 11 Nov: "I want to be able to swipe
through the next few upcoming days also", and the axis labels were "too big
... when I turn my phone sideways". The drawing was a fixed 400 units wide,
stretched to a landscape phone's width; it is now drawn at the width it is
shown at and redrawn on a turn or resize, so labels stay 11px at any width.

Files: `index.html` (`glanceDay`, `todayGlance`, `glanceSync`, `glanceWidth`,
CSS). Checked in Chrome at 390 portrait, 844 landscape and 1280; no sideways
page scroll at 360, 390 or 412; suite OK, `nametest.py` clear.

Roll back: `git revert` this commit.


## 2026-11-11: the Card's record at the page's stakes (tag pending)

**What changed:** the Card's return is now shown at the stakes the page tells people to use (two units a 2x, one a 3x) as well as one unit a group. The Card scoreboard ("Is it working?") adds "at the page's stakes ... per N units" to every tile where the two differ. `planRungs` (unused since #228 removed the plan panel) quotes both too, so a revert of #228 brings the panel back honest. `groupings-record.json` tallies gain `unitsStaked`, `unitsReturned`, `unitsReturnedBest`; each graded group carries its published `stake` (one unit before 29 Oct, when the archive kept none).

**Evidence:** archive to 10 Nov, full rule: 35 groups, 49 units staked, 39.55 back (-19.3%; -18.2% at best prices) against -12.2% flat. The flat figure flattered the Card because the 2x, staked double, is the weaker kind live. `tests/test_groupings_record.py` (Stakes), `tests/test_place_now.py` (PlanCardStakes, in node). Checked in Chromium at 1280 and 400 wide on the real record. Note: `claude/card-record-at-stakes-2026-11-11.md`.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_record.py`, `tests/test_place_now.py`, `claude/card-record-at-stakes-2026-11-11.md`, `CLAUDE.md`.

**Not changed:** `CARD_STAKE`, `CARD_RULE`, any Card rule, replay or past grade; `staked` / `returned` still read one unit a group.

**Roll back:** `git revert` the merge commit; the record drops the units fields at the next build.
## 2026-11-11 Bets: the plan panel removed (tag pending)

For a reader: the Bets tab no longer opens with the plan (the three rungs,
the habits and Today's bets). Douglas, 10 Nov evening: "I don't like this
bit. Remove", the whole plan (`claude/plan-decision-2026-11-10.md`), and on
11 Nov: "Still showing the plan which I asked to remove". Bets now opens with
Coming up, then the Card and the Edge picks. The Card's fold, its play list
and the Model card fold no longer mention the plan; "Coming up" no longer
links to it.

Files: `index.html`, `CLAUDE.md`. `signalsPanel` and `planRungs` stay in the
file unused, so a revert brings the panel back; `sigList` still feeds Coming
up. The Edge flag's opposition floor is not changed here (see the note).

Checked in Chrome at 360, 390, 412 and 1280 wide; suite OK, `nametest.py`
clear.

Roll back: `git revert` this commit.

## 2026-11-10-31 Bets: Leave these out, Check a slip and the Accumulator removed (tag pending)

For a reader: the Bets tab no longer has the "Leave these out" list, the
slip checker or the accumulator calculator, and Card picks no longer carry
"Add to acca +". Douglas, 10 Nov 2026: "Remove these sections." With the plan
at the top saying what to bet and "nothing else", tools for building slips
outside it pulled the other way. The Card's play list now says "Only the
plan".

Files: `index.html` only. The avoid list is still built by `groupings.py`
(nothing reads it on the page now); the checker and calculator functions
stay in the file unused, so a revert restores them cleanly.

Checked in Chrome at 360, 390, 412 and 1280 wide; suite OK, `nametest.py`
clear.

Roll back: `git revert` this commit.

## 2026-11-11 Daily List: college basketball only at a William Hill price of 1.05 or more (tag pending)

**What changed.** Douglas (11 Nov 2026): college basketball picks are "almost pointless to have on daily list if I can't bet on them"; "just move to the college basketball tab unless there is a clear 1.05 or above". A college basketball list pick now shows on the Daily List only when William Hill's price, read before the start, is 1.05 or more. The rest stay on the College basketball tab, and each day says how many were left off, with a link to the tab. The masthead and list counts, Today at a glance and Coming up read the same filtered picks.

**Evidence.** Of 46 college basketball list picks checked at William Hill on 10-11 Nov (`listAtBook.picks`), 30 had no UK price, 11 were not at Hill and the 5 at Hill paid 1.00-1.01.

**Not changed.** Display only: the model, the list flag, the grading and the record (which still counts these picks as list picks), every other sport. The rule is one entry in `listHillMin` in `index.html`; empty it to undo.

**Checked.** `nametest.py`, the unit tests, a render at 1280 and 400 wide (the left-off line under the day header, the link opens the College basketball tab, no errors). The sandbox build had no football, so the live counts will be higher.

**Files.** `index.html`, `CLAUDE.md`.

**Roll back.** `git revert` the commit.

## 2026-11-10: tennis Odds API keys, second look (tag pending)

**What changed:** a note only. No code or page change.
**Evidence:** the key list is still unavailable (no `ODDS_API_KEY` in the sandbox, no stored report), so no unmatched-but-listed tournament can be shown. The `--probe` logging already exists.
**Files:** `claude/odds-api-tennis-keys-2026-11-10.md`.
**Not changed:** `_odds_keys`, pricing, any model.
**Roll back:** `git revert` the commit.

## 2026-11-10-34 Bets: the week ahead panel removed, one "Coming up" line instead (tag pending)

**What changed.** Douglas (10 Nov 2026): the week ahead "is entirely
redundant as it's not showing any groups for the days ahead. It also feels
too cluttered." The seven-day panel on the Bets tab (day cards, sport bars,
legend, the model doubles and trebles that were never in the plan) is gone.
In its place, under the plan, one line, **Coming up**, naming each day after
today that already has a plan bet (how many, tested or on trial) with a link
into the plan; when no later day has one, nothing shows. Today's bets were
already in the plan just above it.

**Not changed.** The plan, the Card, Edge picks, the briefings (the model
treble in the push is built server-side), Today at a glance (`weekPick` and
`weekDays` stay; the panel's own code and styles are removed).

**Checked.** Bets at 390 and 1280: no panel, no errors, no sideways scroll;
the line rendered with made-up bets at both widths. 745 tests pass.

**Files.** `index.html`, `CLAUDE.md`.

**Roll back.** `git revert` the release commit.

## 2026-11-10-33 Phone: the page no longer pans sideways in Safari (tag pending)

**What changed.** Douglas (10 Nov 2026, iPhone, How it went): "still getting
twitchy horizontal scroll". His screenshot shows the whole page panned about
8px left. #214 clipped sideways overflow on `html` and `body`; Safari hands
the root's overflow to the viewport and can still let a touch pan past it.
The same `overflow-x: clip` now also sits on `.wrap`, the one box every tab
lives in, which Safari honours as an ordinary element; sticky still works
(clip makes no scroll container).

**Checked.** In Chromium with the site's real fonts (from npm, as Google
Fonts is blocked in the sandbox), at 390 and 320 on the Daily List, Bets,
How it went, Football and Tennis with every fold open: no sideways scroll
and nothing reaching outside `.wrap`, so the clip hides nothing meant to
show; the tab bar still sticks. The offending element itself does not
overflow in Chromium and Safari's engine could not be fetched here, so the
check that matters is on the phone.

**Files.** `index.html`.

**Roll back.** `git revert` the release commit.

## 2026-11-10-32 Card review: the replay's coverage beside the record, Kelly read plainly (tag pending)

**What changed.** Two lines in the nightly Card review issue, so it cannot
be misread. The replay table's "live" row read 0 groups and 12 empty days
over 29 Oct to 9 Nov, as if the Card had made nothing; the record holds 21
live Card groups over those days. A **Coverage** line now sets the two side
by side and says why they differ (legs archived only as estimates before
10 Nov; from 10 Nov every leg carries its first real price), so the table
is read as rules against each other, not as the Card's own return. And the
staking section printed "quarter Kelly: median +0.0%, drawdown 0%" when the
groups land under the bookmakers' chance (live 0.942): Kelly stakes nothing
then, which read as a safe strategy. It now says so in words.

**Files.** `tools/card_review_post.py` (`coverage_lines`, `kelly_line`),
`tests/test_card_review_post.py` (four tests).

**Not changed.** No Card rule, no replay, no stake; the record is only
counted, never fitted.

**Roll back.** `git revert` the merge commit.

## 2026-11-10-31 Days at a glance on How it went (tag pending)

**What changed.** Douglas (10 Nov 2026): "add the Today at a glance section
to the How it went tab, showing for all previous days listed". The Daily
List board on How it went now opens with **Days at a glance**: every list
day it holds as one line of the clock, each list pick a dot at its start,
won green, lost red, void grey, unsettled hollow, on one shared hour axis so
the days read against each other. A day's tally sits beside its line (green
at 80%+, red under); tapping a line opens that day's picks below. A column
shows at most six dots, losses first so they are never the ones hidden, with
"+n won" for the rest (3 Nov had 15 college basketball tip-offs at 00:00).
The axis runs to 06:00 the next morning when any day has a pick that late.

**How.** `score.py` writes each football day row's `kickoff` (it was in
`record-graded.json`, not in the day rows); `score_tennis.py` gives each
tennis day row the start ESPN recorded (`history-tennis/`, on a copy, so the
kept graded rows are unchanged); US sports already carried `when`.
`listReviewDays` passes the start through; `daysGlance` in `index.html` draws
it. Display only: nothing is graded differently.

**Checked.** 14 days, 240 picks drawn at 1280 and 400 wide, no sideways
scroll, tap opens the day; the phone drawing is made at its real width so
the hour labels keep their size. 741 tests pass.

**Files.** `index.html`, `score.py`, `score_tennis.py`.

**Roll back.** `git revert` the release commit.

## 2026-11-10-30 The plan: one way to bet at the top of Bets (tag pending)

For a reader: the Bets tab opens with **the plan**, one ladder of three rungs
in order of proof, and nothing else. 1. Edge singles, tested over five
seasons (388 of 459, +5.4% at the best price, ahead in four seasons of five),
one unit each. 2. The Edge double, the day's two most likely Edge picks when
there are two or more (170 of 252, +4.6% at the best price), one unit. 3. The
Card, on trial at its own stakes (replay +4.4%, live 11 of 35, -12%), until
the 30 Nov review. Then four habits and today's bets, tested first. The week
ahead now counts the plan's bets per day; its model trebles are folded away
as not in the plan, with the reason (accurate, but the margin compounds:
-32% at three legs on real prices). The Card's long rule and the Model card
are folded.

Evidence: `claude/edge-accas-2026-11-10.md`, `claude/card-seasons-2026-11-09.md`,
`claude/list-accas-2026-11-10.md`; the reasoning in
`claude/the-plan-2026-11-10.md`.

Files: `index.html` (`signalsPanel`, `planRungs`, `sigList` builds the Edge
double, `weekDays` / `weekAhead`, `renderToday` order, CSS),
`tests/test_place_now.py`, `claude/the-plan-2026-11-10.md`, `CLAUDE.md`.
Checked in Chrome at 360, 390, 412 and 1280 wide; suite 741 OK, `nametest.py`
clear.

Not changed: any rule, stake, `CARD_*` constant, `CARD_RULE`, record or push.
The Edge double is shown, not archived or graded as a group.

Roll back: `git revert` this commit.

## 2026-11-10 Croatia, Serbia, Ukraine, Hungary, Korea, UAE: already covered, second check (tag pending)

**What changed:** a dated note only, `claude/af-new-leagues-recheck-2026-11-10.md`. No code, model or rule changed.
**Evidence:** every league API-Football carries for the six countries is already in the build (`sources.AF_NEW`, `af.301`, 16 lower divisions in `af-leagues.json`); extra API allowance per build 0; `nametest.py` all clear. The replay needs the API key and prior-season history, neither available here, so the Rule 3 gates could not be run and the leagues stay off the List.
**Files:** `claude/af-new-leagues-recheck-2026-11-10.md`, `RELEASES.md`.
**Not changed:** `sources.py`, any model number, the Daily List.
**Roll back:** `git revert` the commit.

## 2026-11-10-29 Phone layout: no sideways scroll, tap a glance dot to its pick, a Days button (tag pending)

For a reader: the page no longer drifts sideways on a phone after jumping
around it. Every tab, every day in the Daily List's day strip and every dot on
Today at a glance was checked at 360, 390 and 412 wide: the page cannot be
scrolled sideways after any of them. Tapping a dot on Today at a glance now
goes to that pick on the list and outlines it for a moment. A round "Days"
button appears bottom right once you are deep in the list and takes you back
to the day strip.

What was wrong: the Card's price notes (`.og-l .o small`) were set to one
line by a rule that came after the phone rule meant to wrap them, so on a
phone they ran past the edge (page 396 wide on a 390 screen). The views grid
on How it went could also push past the edge with long labels. Fixed with a
phone rule that wins, `overflow-x: clip` on the page under 860px as a
backstop, `minmax(0,1fr)` columns, and short chip words where the confidence
column is narrow ("No Hill", "No UK"). One scroll helper (`scrollClear`) now
serves the day strip, the glance dots and the Days button, clear of the
sticky tab bar; a jump of more than four screens goes straight there rather
than animating.

Files: `index.html` only (row keys `data-pk` on every list row builder,
`glanceGo`, `scrollClear`, `#toDays`, CSS). Checked in Chrome at 360, 390,
412 and 1280 wide; suite and `nametest.py` clear.

Not changed: what is listed, its order, any number or record.

Roll back: `git revert` this commit.

## 2026-11-10-28 When to take the Card's prices: a read with evidence, and the return first v last (tag pending)

**What changed:** `tools/price_timing.py` (issue #156) printed "take the price late" or "when published" from the sign of the mean move on any sample, two legs included. A read now needs 50+ legs and a day-resampled bootstrap p of the other sign at most 0.10, else "too few legs to read" or "no clear read". New `settled` block: singles on settled legs at the first price v the last pre-start price, paired, with p(late no better), since a drift only pays on legs that won. Legs not started yet are left out (`notStarted`; the nightly run read the next days' legs as closed). The nightly Card review prints both lines. The Place now panel gets one dated line: placing nearer the start has paid. `notify.py` resolves `briefed.json` from `HERE` at call time, so `tests/test_notify.py` no longer writes the real archive's file.

**Evidence:** pool 30 Oct to 10 Nov, 107 legs: mean move +1.76%, p(no drift) 0.003 by day; 104 settled singles -7.21% at the first price, -5.26% at the last, late +1.95 points, p 0.011; football 93 legs carries it, NBA 16 and tennis 3 have no read. Agrees with the football-data replay's CLV -3.4% (`claude/price-timing-read-2026-11-10.md`). Tests: `tests/test_price_timing.py` (the read gate, day resampling, the settled pairing, unstarted legs), `tests/test_card_review_post.py` (the new lines). Place now checked at 1280 and 400 wide. Suite OK, nametest clear.

**Files:** `tools/price_timing.py`, `tools/card_review_post.py`, `index.html`, `notify.py`, `tests/test_price_timing.py`, `tests/test_card_review_post.py`, `claude/price-timing-read-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any Card rule, `CARD_BOOK`, the push or briefing times, any pick, price or record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-27 The groupings record no longer crashes on the briefings file (tag pending)

**What changed:** `groupings.grade()` read every `.json` in `groupings-archive/` as a day of groups. Since #211 `notify.py` keeps `briefed.json` there (the briefing slots sent), which has no `groups`, so the next `groupings.py` run would stop with `KeyError: 'groups'`: no Card on the Bets tab (the workflow's "empty state"), no groups archived or re-checked, no record regrade, from the first scheduled build after 10:53 UTC on 10 Nov. `grade()` now reads day files only (`YYYY-MM-DD.json`, `groupings.DAY_FILE`). No other reader lists that folder that way (the tools read `pool-*.json.gz` or a named day).

**Evidence:** reproduced locally (`python3 groupings.py` on main: `KeyError: 'groups'` in `grade`); `tests/test_groupings_record.py` `NotADay` fails before the fix and passes after; `groupings.grade()` on the real archive runs. Suite OK, nametest clear.

**Files:** `groupings.py`, `tests/test_groupings_record.py`, `RELEASES.md`.

**Not changed:** any Card rule, pick, price, archive or record file; `notify.py`.

**Roll back:** `git revert` the merge commit (the crash comes back while `briefed.json` sits in the archive).

## 2026-11-10-26 Four briefings a day, at Douglas's betting times (tag pending)

**What changed:** the morning push becomes four, one per slot a UK day, timed to when Douglas places bets ("in the morning around 8am, around lunchtime, early evening and before I go to bed"): **morning** (the new 07:40 build: the day's list, Group A, the model treble, Edge picks, the Card), **lunch** (12:00 build) and **evening** (17:00 build: the day's tally so far, the strongest picks still to start, the treble from those, Edge picks not yet kicked off, open Card groups with Hill prices), and **night** (22:15 build: the same plus the overnight US slate to 08:00). Each slot is sent by the first build at or after its hour, only the latest due slot is sent (a late build never sends a stale one), and slots sent are kept in `groupings-archive/briefed.json`. A slot with nothing to back sends nothing. `deploy.yml` gains a 07:40 UTC run for the morning push (08:40 in summer); every paid source is capped by its own daily ledger, so the extra run cannot overspend.

**Evidence:** `tests/test_morning_brief.py` (each slot's content, the tally from the record, the overnight cut-off, latest-slot-only, never twice, a new day starts clean). Suite 734 OK. Not sent from the cloud session; the first real one is the next build after merge.

**Files:** `notify.py`, `.github/workflows/deploy.yml`, `tests/test_morning_brief.py`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Card pushes, any pick, price or record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-25 A morning briefing to the phone (tag pending)

**What changed:** once a UK day, the first build at or after 05:00 UK (normally the 05:15 build) sends a push through the same ntfy topic as the Card pushes: "Daily List, Tue 10 Nov: 15 picks", then Group A (the strongest picks at 85%+ with their start times), the model treble or double still to start (the week-ahead rule), the day's Edge picks with prices, and how many Card groups are open. Tapping it opens the site. The day sent is written to `groupings-archive/briefed.json`, which the build already commits, so a late or repeated build never sends it twice; a day with no list pick sends nothing. Display only.

**Evidence:** `tests/test_morning_brief.py` (picks by UK start day across pool dates, list-only, started picks out of the treble, Edge line, the wider filler not counted as a Card group, once a day from 05:00). Not sent from the cloud session (no topic here); the first real one is tomorrow's 05:15 build. Suite OK.

**Files:** `notify.py`, `tests/test_morning_brief.py`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Card pushes, the workflow, any pick or record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-24 Today at a glance, on the Daily List (tag pending)

**What changed:** the Daily List opens with **Today at a glance**: today's list picks on one 00:00-24:00 line, each at its start time and coloured by where it stands (won or lost from the record, in play ahead, behind or level from the live scores, finished but not yet graded, to come), a red line at the time now, and a summary: won, lost, in play, to come, and the next start with a countdown. Hover or tap a dot for the pick, time, confidence and state. It redraws on every live read and once a minute. A phone gets its own narrower drawing so the labels stay readable.

**Evidence:** checked at 390 and 1280 wide with mocked live tennis (two in play, one finished) and the day's remaining picks. Suite OK.

**Files:** `index.html`, `RELEASES.md`.

**Not changed:** the list, its order or record; grading.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-23 Where to trust the model, in How it went (tag pending)

**What changed:** How it went, Daily List, adds **Where to trust the model**: every graded pick at 55% or more, every sport, by family (football core / wider / cups and internationals, tennis ATP and WTA, each US sport, rugby) and confidence band (55-65, 65-75, 75-85, 85-95, 95+), landed against quoted with the count. A cell is tinted only past 90% (z 1.645): green above its number, red under; a cell under 10 picks is faint. Above the table, the cells that are clearly off, in words. `trustmap.py` builds the grid from `record-graded.json`, `tennis-record.json` and `sports.graded_games()`; `build.py` adds it to the on-demand `record-data.js` as `trust` (first paint unchanged; `record.json` unchanged).

**Evidence:** on the record at 10 Nov: above its number, football core leagues at 55-65% (65% v 59%, 539 picks) and 65-75% (78% v 69%, 187), college basketball at 55-65% (73% v 61%, 51); under, football cups and internationals at 65-75% (56% v 69%, 59) and college football at 85-95% (78% v 89%, 32), both already known (`claude/tuning-evidence.md`, `sports.LIST_OFF`). Checked at 390 and 1280 wide. `tests/test_trustmap.py`. Suite 728 OK.

**Files:** `trustmap.py`, `build.py`, `index.html`, `tests/test_trustmap.py`, `claude/trust-map-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any model, list rule or record figure.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-22 The week ahead, on top of Bets (tag pending)

**What changed:** the Bets tab opens with **The week ahead**: seven day cards (today to next Monday), each with its Daily List pick count, a bar of the picks by sport scaled to the busiest day, and the strongest model bet with its chance and a meter. Tap a day for its **Model treble** (the three strongest list picks still to start) and **Model double** (the top two): each leg with confidence, kick-off and its William Hill chip, the group's combined chance, and William Hill's combined price when every leg has one. Same sport allowed, no bookmaker condition (Douglas: "rely on the model and its accurate performance"). Under it, the same rule's record on the graded list, so the claim is checked on the page. Display only: not staked, pushed or archived; the Card below is unchanged. `listCollect` is now shared by the Daily List and this panel.

**Evidence:** checked at 390 and 1280 wide on the live sports and tennis files: 101 list picks over 7 days, a model bet on 7 of 7; on the graded sports and tennis list (football record not in the test page), top-2 double 12 of 13 days (92% v 85% quoted), top-3 treble 10 of 12 (83% v 79%). Suite 725 OK.

**Files:** `index.html`, `claude/week-ahead-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Card, its rules and record; the Daily List.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-21 Place now: the signalled bets at the top of the Bets tab (tag pending)

**What changed:** the Bets tab opens on **Place now**, a phone-first box listing only the bets that pass a rule the site tests and are still open, soonest first. Each one shows what to back, the William Hill price (or the best price and the average for an Edge single), the start time, the stake in units and pounds and what it returns, and the evidence in one line with a verdict: **Tested** for Edge singles (five football-data seasons: 388 of 459 won, +5.4% at the best price), **On trial** for Card groups (the live record, 11 of 35 against 11.7 expected at 10 Nov: not yet an edge). A **Copy slip** button puts the bet on the clipboard. When nothing qualifies in the next 24 hours it says **No bet to place**, names the next signal, and lists the wider-rule filler under "Not a signal" (replay 3 of 15 won against 5.1 expected, -46%). Started, locked and late groups are left out.

**Why:** Douglas, 10 Nov: "accurate signalled bets to put on as I'm on the train". The Bets tab carried the Card, the Edge picks, the paper card and the record in one long page; the bets themselves and how much to trust each were far down it.

**Evidence:** checked in Chromium at 1280 and 400 wide on a stub slate (two Edge singles, a Card 2x, a wider-rule group, a Card 2x two days out) and on an empty day; no horizontal scroll, copy works. `tests/test_place_now.py` runs the page's own functions in node: open signals only, soonest first, started / late groups out, the filler never a signal, the slip's stake and Hill prices. Suite OK, `nametest.py` clear. Display only.

**Files:** `index.html`, `tests/test_place_now.py`, `RELEASES.md`, `CLAUDE.md`.

**Not changed:** any rule, the Card, the Edge flag, the record, the Daily List.

## 2026-11-10-20 Live scores for tennis (tag pending)

**What changed:** started tennis picks on the Daily List now show the live set score (in the row's player order, "4–6 6–3 2–1"), the set in play and whether the pick leads, from ESPN's ATP and WTA scoreboards, the feed `build_tennis.py` already reads for results. Sets decide the lead; with sets level, the set in play does. A finished game in any sport now shows its score in the pill and "Final, unofficial" beneath, so a three-set score fits.

**Evidence:** Douglas, 08:57: "Why can't I see this now?" Nothing on today's list was in play: the rest of the day is tennis from 12:00 UK and college basketball from 23:00, and live scores covered only US team sports. Checked at 390 and 1280 wide on a mocked ESPN tennis scoreboard (tournament groupings, ESPN's player order reversed on one match, one finished): scores, leads and the tally correct. Not run against live ESPN from the cloud session. `tests/test_live_scores.py` adds the tennis case. Suite OK.

**Files:** `index.html`, `tests/test_live_scores.py`, `RELEASES.md`.

**Not changed:** grading, football rows (no ESPN id on file).

**Roll back:** `git revert` the merge commit.

## 2026-11-10-19 No ghost pins for games that moved day (tag pending)

**What changed:** today's pinned Daily List no longer keeps a game on a day it was moved away from. ESPN first lists some US games at a stand-in time of midnight Eastern and corrects it later; `daylist.pinned` took the newest copy published before the start *among copies dated today*, so a game moved to tomorrow kept an old copy pinned today, read as started, and showed "Result due". It now takes the newest pre-start copy of each game whatever its day, and pins the game only on that copy's day.

**Evidence:** 10 Nov 08:34, Douglas: "Still seeing result due". Texas Southern v College of Biblical Studies and San Francisco v Montana (reserve) were archived at 10 Nov 05:00 UK in the 4-5 Nov builds and at 11 Nov 00:00 / 03:00 from 6 Nov: not played yet. Rebuilt for 10 Nov: no started-without-result picks; for 11 Nov: both pinned at their real times. `tests/test_daylist_moved_start.py`. Suite OK. (#199, walking results to today, stands: it is a real gap for games filed under the US Eastern day, but it was not this one.)

**Files:** `daylist.py`, `tests/test_daylist_moved_start.py`, `RELEASES.md`.

**Not changed:** grading (`sports.graded_games` already takes the newest pre-start copy), the record, the list rule.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-18 "Is the list honest?" in How it went (tag pending)

**What changed:** How it went, Daily List, now opens with two charts under the scoreline. **Quoted against landed:** for each confidence band (80-85, 85-90, 90-95, 95+), the average quote as a bar and what landed as a dot, with the 90% range chance alone allows for that many picks; a band whose quote sits above its range turns the dot red. **Landed minus expected:** a running total across every list day, inside the shaded band chance alone allows. A one-line verdict above them ("on quote, within what chance alone would give", in standard errors). Built from the graded picks already on the page; nothing fitted (Rule 1).

**Evidence:** on the record at 10 Nov: 182 of 199 settled list picks landed (91%) against 89% quoted, +1.3 standard errors, on quote; every band's quote inside its range. Checked at 390 and 1280 wide. `tests/test_list_honesty.py` (the Wilson range, the 20-pick guard, the verdict) in node. Suite OK.

**Files:** `index.html`, `tests/test_list_honesty.py`, `RELEASES.md`.

**Not changed:** the record, the list, any number on it.

**Roll back:** `git revert` the merge commit.

## Football reserve v its quotes: tested, no change, 10 Nov (tag pending)

**What changed:** nothing in the model or the reserve rule. Dated note `claude/reserve-football-gap-2026-11-10.md`.
**Evidence:** reserve 13 Oct to 10 Nov, 379 settled: 242 landed v 256.8 expected (z -1.64). Home picks 203 v 222.0 (z -2.26), away 39 v 34.8; wider-league (`af.*`) picks 161 v 176.7; bands all slightly under, none alone significant; no league has 12 picks. The same leagues' list picks land on quote (93 v 93.6). The wider leagues are not in the replay, so no fit/check test of an exclusion or tilt is possible (Rule 3); a live-only exclusion would fit on the scoreboard (Rule 1).
**Files:** claude/reserve-football-gap-2026-11-10.md, RELEASES.md.
**Not changed:** reserve floor (62%), list bars, probabilities, grading.
**Roll back:** revert the commit.

## 2026-11-10-17 Live scores on the Daily List (tag pending)

**What changed:** a started Daily List pick in the US sports (college basketball, NBA, NFL, college football, NHL, MLB, WNBA) now shows its live score in the middle of the row, coloured by the pick's position (green ahead, red behind, gold level), with the clock; a finished game shows "Final" with an outline until the next build grades it. The day heading adds a live line: how many picks are ahead, behind and level, and the finished-but-ungraded tally. The page reads ESPN's public scoreboard (the source these sports are rated and graded from) once a minute while it is open and visible, one call per sport and US day, and stops when every watched game is final. Display only and marked unofficial: the record still grades from the build. `daylist.py` now carries each pinned pick's ESPN feed.

**Evidence:** checked at 390 and 1280 wide against a mocked ESPN scoreboard in ESPN's shape (two in play, one level, two finished): pills, clock, tally and the US-Eastern date in the request all correct; with ESPN blocked the rows keep "In play" and the page logs no error. Not run against the live ESPN feed from the cloud session (ESPN is blocked here); the first real read is the first open of the deployed page during a game. `tests/test_live_scores.py` (the feed on a pinned item; the page's parser and ahead / behind read run in node on an ESPN-shaped payload). Suite 709 OK.

**Files:** `index.html`, `daylist.py`, `tests/test_live_scores.py`, `RELEASES.md`.

**Not changed:** grading, the record, the list, football and tennis rows (no ESPN id on file).

**Roll back:** `git revert` the merge commit.


## 2026-11-10-18 The nightly Card review posts once a day, so a missed night can be caught (tag pending)

**What changed:** `tools/card_review_post.py` now checks the last ten `card-review` issues before posting and posts nothing when "Card review <today>" is already there (open or closed). `FORCE_POST=1` posts anyway. An unreadable listing still posts, so the guard can only ever cost a duplicate, never a missing review.

**Why:** the 03:40 UTC schedule did not fire on 10 Nov (GitHub drops scheduled runs under load; the 9 Nov run itself started at 12:07). The review was dispatched by hand at 08:40 (#200, 0 integrity findings). The guard lets `card-review.yml` carry a second, later schedule without posting twice; that workflow change is a separate pull request left for Douglas (`.github/`, needs-owner).

**Evidence:** `tests/test_card_review_post.py` `OncePerDay` (posts when today is missing, skips when posted, `FORCE_POST`, unreadable listing). Suite OK, `nametest.py` clear.

**Files:** `tools/card_review_post.py`, `tests/test_card_review_post.py`, `RELEASES.md`.

**Not changed:** the review's content, any Card rule, the record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-16 US results graded the same day (tag pending)

**What changed:** finished US games (college basketball above all) are graded by the next build instead of the next day. The results walk in `sports.py` stopped at yesterday; ESPN files a game under its US Eastern day, so anything tipping off at midnight Eastern or later (05:00 UK in winter) sat on "today" and read "Result due" until the following day's walk. On 10 Nov at 08:34 two picks (Texas Southern v College of Biblical Studies, San Francisco v Montana, both 05:00 UK) were finished and ungraded. The walk now reaches today.

**Evidence:** `history-sports/` walked through 9 Nov at the 07:54 build; both games filed under 10 Nov Eastern. Only final games are kept, the next walk rescans `RESCAN` (3) days, and a pick is voided only `NOT_PLAYED_DAYS` (7) after its start, so walking a day still in progress records nothing wrong. `tests/test_sports_walk_today.py`. Suite OK.

**Files:** `sports.py`, `tests/test_sports_walk_today.py`, `RELEASES.md`.

**Not changed:** grading rules, ratings, the record's history.

**Roll back:** `git revert` the merge commit.

## 2026-11-10: Card stake line, tested and not built (tag pending)

**What changed:** a note only. The Bets page line (unit size for a stated bankroll) is not built.
**Evidence:** the replay of the current Card rule holds 0 groups on both football-data seasons (rule 6); the nearest, `cardRule5`, holds 22 groups on one season (bankroll 47 units for a 66-group season, 10 won v 7.0 expected). Too thin to state a bankroll.
**Files:** `claude/card-stake-line-2026-11-10.md`.
**Not changed:** `CARD_STAKE`, `CARD_RULE`, any record, the page.
**Roll back:** `git revert` this commit.

## 2026-11-10-15 Which book to write the Card for: Hill stays (tag pending)

**What changed:** notes only, `claude/card-book-2026-11-10.md`.
**Evidence:** 111 Card-rule pool legs, 30 Oct to 10 Nov: Bet365 +0.30% v average (best on 65%), William Hill -0.04% (62%), Betfair -0.89%, BetVictor -1.73%. Paired Bet365 v Hill on 77 legs +0.43%, p 0.045 one-sided; best price v Hill +1.09%, under the 2-point line. Under 100 paired legs and a sub-1-point gap: no change.
**Files:** `claude/card-book-2026-11-10.md`, `RELEASES.md`.
**Not changed:** `CARD_BOOK`, Card rules, the Bets page.
**Roll back:** `git revert` the commit.


## 2026-11-10-14 Card over 2022-25: task already answered, index note (tag pending)

**What changed:** notes only, `claude/card-seasons-recheck-2026-11-10.md`, pointing each requested table (legs v quote, singles, gap band, opposition band, Card return, losing months) to its place in `claude/card-seasons-2026-11-09.md`. No rerun: the sandbox cannot fetch football-data.
**Evidence:** none new; the 9 Nov CI runs 42543472973 and 42546496524 stand. No gate met, no rule changed.
**Files:** `claude/card-seasons-recheck-2026-11-10.md`, `RELEASES.md`.
**Not changed:** code, model, Card rules.
**Roll back:** `git revert` the commit.


## 2026-11-10-13 Edge picks on the Bets tab, with five seasons of accumulators behind them (tag pending)

**What changed:** the Bets tab has an **Edge picks** section under the card: every football fixture with the green Edge flag for the chosen day, its average and best price and the opposition's price, then the Edge double and every Edge pick as one slip, priced at the average and the best price with the bookmakers' chance each lands, and what each did when tested. The test is new: `tools/card_legs_history.py` (`edge_legs`, `edge_accas`) replays the flag's legs as singles, doubles, trebles, four-folds and whole-day slips on every football-data season; `build.edge_tested` hands the latest seasons to the page (`edgeTested`).

**Evidence:** `claude/edge-accas-2026-11-10.md`. Five seasons, 2022-23 to 2026-27 (CI run 42751060085): the day's most likely Edge pick as a single won 388 of 459, +3.0% at the average price, +5.4% at the best; doubles +0.1% / +4.6%; every Edge pick of the day as one slip 139 of 252, +2.4% / +9.7%, ahead at the best price in four seasons of five; trebles and four-folds +16% / +22% pooled at best but -29% to +99% by season. `tests/test_edge_accas.py`; suite 709 OK; `nametest.py` clear. Checked at 1280 and 400 wide.

**Files:** `tools/card_legs_history.py`, `build.py`, `index.html`, `tests/test_edge_accas.py`, `claude/edge-accas-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Card, the flag's rule, the model, any record. Nothing is staked or pushed from the section.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-12 The Daily List on a phone: day jump, full names (tag pending)

**What changed:** a "Jump to" strip of the week's days, each with its pick count, sits above the Daily List; a tap scrolls to that day just under the tab bar (a week of picks ran to about 40,000px on a phone). Team names wrap on a phone instead of being cut mid-word ("Northern Arizona Lum"); on a desktop a long name in a sport row now ends in an ellipsis instead of losing its first letters ("orthern Arizona Lumberjacks"). The William Hill chip fits the phone's confidence column.

**Evidence:** checked at 390 and 1280 wide on the live sports and tennis files: no chip overflows its row, no name clipped without an ellipsis, the jump lands with the day heading visible under the one-row (phone) and two-row (desktop) tab bar. Suite 706 OK.

**Files:** `index.html`, `RELEASES.md`.

**Not changed:** what the list contains or its order; any data file.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-11 "Edge only" on the football board (tag pending)

**What changed:** the football board's Show control has a third option, **Edge only**, listing just the fixtures with the green Edge flag, and each day's header counts them ("2 fixtures · 2 confident · 2 edge"). When none are flagged the board says why (rare by design, prices arrive through the week). Display only.

**Evidence:** a filter on the existing flag (`claude/edge-flag-2026-11-10.md`). Checked at 1280 and 400 wide on a preview of the 8 Nov fixtures (Celtic v Kilmarnock, Estrela v Benfica); a green count on the red day band was illegible, so the count takes the band's own colour. Suite OK; `nametest.py` clear.

**Files:** `index.html`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the flag's rule, the default view, the Daily List.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-10 The Daily List at William Hill (tag pending)

**What changed:** each Daily List pick now says whether William Hill offers it: a chip under the tested rate reading `Hill 1.04`, `Not at Hill` (UK books price it, Hill does not) or `No UK price`. A new "Show: Every pick / At William Hill" control on the Daily List hides the picks Hill does not price. "How it went" adds an "At William Hill" tile (settled list picks Hill priced, landed, return at Hill's price, from 10 Nov) and the chip on each list row; the nightly Card review prints the same table. To fill it, list picks are sent to The Odds API's UK region (`price_odds_api(list_books=True)`), US sports included, one credit a slate, capped at 9 credits a day so the Card keeps its share. Display only: the list never sees a price.

**Evidence:** `claude/list-at-hill-2026-11-10.md`. List picks 1-13 Nov in the pool archive: 172 college basketball, none with a UK price read; across every sport 3 of 228 had a William Hill price. `tests/test_list_books.py` (7 tests); suite 700 OK; `nametest.py` clear. Checked at 400 and 1280 wide on the live sports and tennis files with sample marks. No build fetch from the cloud session (no ESPN or API access): the first real marks arrive with the next deploy build.

**Files:** `groupings.py`, `index.html`, `tools/card_review_post.py`, `tests/test_list_books.py`, `claude/list-at-hill-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Daily List's admission, order or record; the model; the Card and every `CARD_*` constant; `CARD_RULE`.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-9 The Model card's rule replayed beside the Card (tag pending)

**What changed:** nothing a reader sees. `tools/card_replay.py` pre-registers `modelcard`: the Model card's rule (the model's own picks at or above the bookmakers' chance) built on the same legs as the Card, staked as the Card. `tools/card_legs_history.py` replays it on every football-data season (`cardModel`, legs admitted on the model's own 60%+). The nightly review's variant table carries it.

**Evidence:** `claude/card-modelcard-2026-11-10.md`. Pool from 30 Oct with `--recover`: modelcard 12 groups, 7 won, legs 29 of 36 (80.6% v 68.1% quoted), +58%; live 10 groups, 4 won, -7%; paired +1.60 units a day, p(worse) 0.02, on 36 legs, under the 100-leg gate. Football-data (CI on this pull request), 2025-26: 70 groups, 22 won v 25.4 the model expected, -8.2% (best -0.4%), so the two samples disagree and nothing changes. `tests/test_card_modelcard.py`; suite OK; `nametest.py` clear.

**Files:** `tools/card_replay.py`, `tools/card_legs_history.py`, `tests/test_card_modelcard.py`, `tests/test_card_legs_history.py`, `claude/card-modelcard-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Card, the Model card, any constant, any record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-8 The Edge flag's own record, on the page and in the review (tag pending)

**What changed:** the green Edge flag now shows its own record on this site. `score.py` grades every flagged football fixture (`edge_record` in `record.json`): live flags as published from 10 Nov, and earlier fixtures flagged from the prices archived before kick-off. The flag's title and the row's green panel quote it ("27 of 34 landed against 76% quoted, -2.1% at the average price, +0.5% at the best"), and the nightly Card review prints it.

**Evidence:** 34 graded flagged fixtures, 12 Sep to 8 Nov: 79.4% landed v 75.9% quoted. `tests/test_edge_record.py` (live v replayed, a published unflagged row never replayed, the tally, the summary key); suite 696 OK; `nametest.py` clear. Checked at 1280 and 400 wide.

**Files:** `score.py`, `build.py`, `index.html`, `tools/card_review_post.py`, `tests/test_edge_record.py`, `claude/edge-flag-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the flag's rule, the model, the Card, any other record figure.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-7 The Edge flag tested on every sport (tag pending)

**What changed:** nothing a reader sees. `tools/edge_sports.py` tests the green Edge flag's conditions on every sport's favourites in the priced pool, by price, gap to the market and the opposition's price, with two candidates (the flag without the opposition condition; the short favourite at 1.15-1.30) and a gate for switching a sport on. The nightly Card review prints every sport's line on legs from 11 Nov, out of sample (`card_review_post.edge_section`, no workflow change).

**Evidence:** `claude/edge-sports-2026-11-10.md`. Pool 30 Oct to 9 Nov, first real prices: no sport passes (100+ legs, landed above the bookmakers, best-price return positive, p(loss) <= 0.30). Football candidate 100 legs, +3.0% at best; tennis 27 legs, -18.1%; NFL 12 legs, +16.2%; college football 44, +4.8%. The short favourite over all sports: 62 legs, 90.3% v 77.0%, +11.0%; with `--recover` 162 legs, +2.0%, chosen on that sample, so tracked out of sample from 11 Nov. `tests/test_edge_sports.py`; suite 693 OK; `nametest.py` clear.

**Files:** `tools/edge_sports.py`, `tools/card_review_post.py`, `tests/test_edge_sports.py`, `claude/edge-sports-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the flag (football only), the page, the model, the Card, any record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-6 The green Edge flag on fixtures (tag pending)

**What changed:** a green **Edge** flag on football fixtures that meet the one price condition with evidence behind it, on the Daily List and the full board, with a short evidence panel in the row's detail. A fixture qualifies when it is in one of football-data's 20 tested leagues, clean for the Daily List, the model's pick is also the bookmakers' favourite at 1.15 to 1.90 with the bookmakers 60%+, the opposition is priced 9+, and the model is no more than 5 points above the market (`groupings.edge_flag`, `EDGE_RULE` 1). Display only: the model never sees a price. The flag is archived with each prediction (`edge`) so it can be graded.

**Evidence:** `claude/edge-flag-2026-11-10.md`. Five seasons: 511 legs, 83.8% landed v 76.2% quoted, +4% average price, +7% best; 2025-26: 232 legs, +3.3% / +5.8%; 2026-27 so far 52 legs, -1.7% / +1.1%. On the site's own archive since 11 Sep: 43 flagged fixtures, 27 of 34 graded landed v 25.8 quoted. `tests/test_edge_flag.py` (each condition, the away side, the favourite check, the leagues); suite 688 OK; `nametest.py` clear. Checked at 1280 and 400 wide.

**Files:** `groupings.py`, `build.py`, `index.html`, `tests/test_edge_flag.py`, `claude/edge-flag-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the model, the Daily List's admission or order, the Card, any record. No flag for other sports (no tested price condition).

**Roll back:** `git revert` the merge commit.

## 2026-11-10-5 Daily List picks as accumulators, measured (tag pending)

**What changed:** nothing a reader sees. `tools/list_accas.py` measures Daily List picks combined into accumulators: the top N of each day on the graded record (landed v quoted) and on the priced pool (return at the average price beside the bookmakers' own expectation). Douglas asked after losing on accumulators of list picks.

**Evidence:** `claude/list-accas-2026-11-10.md`. 458 graded list picks land as quoted (85.8% v 84.9%), and combined they still do (top 5: 48% v 58% on 27 days; top 8: 40% v 40%). The loss is the price: 118 priced list picks, average 1.12, margin 5.3%, singles -0.5%; the bookmakers' own expectation for an accumulator is about -5% a leg, compounding to -41% at ten. `tests/test_list_accas.py`; suite OK (683); `nametest.py` clear.

**Files:** `tools/list_accas.py`, `tests/test_list_accas.py`, `claude/list-accas-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the Daily List, the Card, any constant, any record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-4 The empty-day fillers replayed, the page's own fallback included (tag pending)

**What changed:** nothing a reader sees. `tools/card_replay.py` pre-registers four empty-day fillers for the 30 Nov review (issue #155): `fillwide` (the page's wider-rule fallback, which the replay had never built), `fillopp7`, `fillrule5`, `fillshort`. Each is live exactly, plus groups under the filler only on a day the full rule leaves empty, with the filler's own groups reported apart (`fill`). The nightly Card review prints each filler on its own days and gates a filler on its own legs (`card_review_post.fill_lines`, `gate_legs`). `tools/card_legs_history.py` replays `fillwide`, `fillrule5` and `fillopp7` on every football-data season (first numbers from `tune.yml` on 16 Nov).

**Evidence:** `claude/card-fillers-2026-11-10.md`. Pool 30 Oct to 9 Nov, first real prices: the page's filler built 12 groups on 7 empty days, 2 won against 4.14 expected, -54% (36 legs), paired against live -1.47 units a day, p(worse) 0.95; `fillrule5` 4 groups, 2 won v 1.28, +12% (12 legs); `fillopp7` and `fillshort` built nothing on any empty day. Football-data (CI on this pull request), football only: `fillwide` 2025-26 177 groups, 68 won v 56.0 expected, -0.9% (best +6.6%); 2026-27 35 groups, 12 v 11.4, -11.7%. Under the 100-leg gate on the pool, so no change; the drop-the-filler decision is pre-registered in the note and `CLAUDE.md`. `tests/test_card_fillers.py` (an empty day takes the wider rule, a full day is live unchanged, constants restored, the wider gate only when asked, the gate on the filler's own legs); suite OK; `nametest.py` clear.

**Files:** `tools/card_replay.py`, `tools/card_legs_history.py`, `tools/card_review_post.py`, `tests/test_card_fillers.py`, `tests/test_card_legs_history.py`, `claude/card-fillers-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the page's filler, any `CARD_*` constant, `CARD_RULE`, any record or archive file, `.github/`.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-3 The nightly Card review applies the decision gate on legs (tag pending)

**What changed:** nothing a reader sees. The review's "candidates beating live" line used 30+ groups; the delegated-decisions gate in `CLAUDE.md` is p(worse) at most 0.30 on 100+ legs. `tools/card_replay.py` now writes each variant's legs (`legs`, `legsWon`), the review table shows them, the candidate line uses the legs gate (`card_review_post.candidates`), and variants ahead of live but under 100 legs are listed apart as "watch, do not act".

**Evidence:** pool replay from 30 Oct (`--recover`), read only: live 10 groups on 31 legs; ahead of live at p(worse) 0.30 or under: `short` (27 legs, p 0.00), `notennis` and `tennis80` (10 legs, about 0.22), `uncapped` (34 legs, 0.24), all far under the gate. `tests/test_card_review_post.py` (the gate is legs not groups; the watch line; the legs column); suite OK; `nametest.py` clear.

**Files:** `tools/card_replay.py`, `tools/card_review_post.py`, `tests/test_card_review_post.py`, `RELEASES.md`.

**Not changed:** any `CARD_*` constant, `CARD_RULE`, any variant's definition, any record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10-2 The two-per-competition cap named and `comp3` pre-registered (tag pending)

**What changed:** nothing a reader sees. The limit of two legs from one competition in a Card group or a Multiplier is now `groupings.COMP_MAX` (2, unchanged), so the replay can patch it. `tools/card_replay.py` pre-registers `comp3` (three) for the 30 Nov review, and the Card funnel adds it as a relief row ("three legs a competition").

**Evidence:** `claude/card-funnel-2026-11-10.md`, addendum. On 9 Nov five NBA legs cleared the full rule and no group was built. Funnel 6 to 12 Nov: a 2x on 4 days of 7 (live 3), a 3x on 1 (live 0). Pool replay from 30 Oct (approximate before 10 Nov): comp3 12 groups, 5 won v 4.6 expected, -1%; live 10, 4 won, -7%; paired +0.13 units a day, p(worse) 0.43. Too few to change anything. Tests: `tests/test_card_funnel.py` (cap unchanged, comp3 registered, the relief builds the 9 Nov case); suite OK; `nametest.py` clear.

**Files:** `groupings.py`, `tools/card_replay.py`, `tools/card_funnel.py`, `tests/test_card_funnel.py`, `claude/card-funnel-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the cap's value, any `CARD_*` constant, `CARD_RULE`, the Odds tab's `ok_combo`, the page, any record.

**Roll back:** `git revert` the merge commit.

## 2026-11-10 What keeps groups off the Card: the funnel in the nightly review (tag pending)

**What changed:** nothing a reader sees. `tools/card_funnel.py` (issue #155) reads the pool at each leg's first real price and, per Card day, gives each leg's first failing condition by sport (the live `card_fault`), the legs kept off by one condition alone, and whether a first Card 2x and 3x can be built live and with one condition relaxed at a time. The nightly Card review prints it from 6 Nov (`card_review_post.funnel_section`, no workflow change).

**Evidence:** `claude/card-funnel-2026-11-10.md`. Pool 6 to 12 Nov, legs before 10 Nov at their last price, 651 priced legs over 7 days: it reproduces the live Card (a 2x on 6, 7, 8 Nov, none on 9 Nov, no 3x). No football leg cleared the full rule (262 outside the core leagues, 96 under-market, 26 opposition). A 3x comes back only by relaxing the tennis 75% floor (3 days of 7) or the opposition rule (2 days), the two conditions with evidence behind them (tennis legs z -2.23; opposition 9+ holds in all five seasons), so no change. 9 Nov had five clear NBA legs and no group: two legs per competition (`mult_combo`). `tests/test_card_funnel.py` (every `card_fault` branch keyed, first real price, one condition relaxed, constants restored); suite 669 OK; `nametest.py` clear.

**Files:** `tools/card_funnel.py`, `tools/card_review_post.py`, `tests/test_card_funnel.py`, `claude/card-funnel-2026-11-10.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any `CARD_*` constant, `CARD_RULE`, the page, any record or archive file, `.github/`.

**Roll back:** `git revert` the merge commit.

## 2026-11-09 Office review and next week's priorities (tag pending)

**What changed:** nothing a reader sees. A dated note, `claude/office-review-2026-11-09.md`: what shipped since 31 Oct, what was rejected, where accuracy stands, three tasks (Kofi, Hannah, Susie).

**Evidence:** `RELEASES.md`, the `claude/` notes, `groupings-record.json` and `record.json`, read only. Card 11 of 35 groups won v 11.7 expected; tennis Card legs 22 of 40 v 28.3 (z -2.23); football list 80.6% v 81.8% quoted (n 165). Gates: not applicable (report by nature).

**Files:** `claude/office-review-2026-11-09.md`, `RELEASES.md`.

**Not changed:** code, models, rules, record files.

**Roll back:** `git revert` the commit.

## 2026-11-09 Grading audit: tennis winner spelling and sports score order (tag pending)

**What changed:** four tennis wins graded as losses are corrected on the next score run (Alex de Minaur, China Open, 1-5 Oct: ESPN "de", pool "De"), and sports scores at neutral sites now read in the priced home-away order.

**Evidence:** 124 results checked against ESPN (93 of 94 football, 15 of 15 NBA/NFL; the one football miss was a name-match artefact) and every graded file checked for internal consistency. Walkover, cancelled, postponed, abandoned, retired and tied handling confirmed. Tennis record 883 of 1,395 before the fix. Gates: not applicable (grading code, no model number).

**Files:** `score_tennis.py`, `sports.py`, `tests/test_tennis_winner_spelling.py`, `tests/test_sports_score_order.py`, `claude/results-review-board.md`.

**Not changed:** football grading, models, record files by hand.

**Roll back:** `git revert` the merge commit.

## 2026-11-09 Leg properties, third look: nothing to replay, no change (tag pending)

**What changed:** nothing a reader sees. A dated note and a section in `claude/odds-groupings.md`; no code or model number changed.

**Evidence:** the 23 and 31 Oct scans stand (eligible legs land +9.3 pts on 310 fit legs, +8.8 on 42 check; no cut holds on both seasons; model-at-or-below-market removes about half the legs, limit one fifth). The pool archive's tested rate has 45 real-priced football 65%+ legs to 8 Nov against the 250 Rule 3 needs. The leg scan was not rerun (unchanged inputs). Gates: not applicable, no candidate.

**Files:** `claude/leg-property-third-2026-11-09.md`, `claude/odds-groupings.md`, `RELEASES.md`.

**Not changed:** `groupings.py`, `MAX_ABOVE_BOOK`, any model.

**Roll back:** `git revert` the commit.

## 2026-11-09 Weakest other sport: none below the bar, no change (tag pending)

**What changed:** nothing a reader sees. A dated note; no code or model number changed.

**Evidence:** hits v expected on the live records: college football 193/291 v 202.7 (z -1.23, already off the list), ATP 327/528 v 335.1 (z -0.73), NFL z -0.54, WTA -0.09; NBA, rugby, MLB, college basketball above quote. None is two standard errors under on 50+ games. ATP's 55-65% bands run under quote (z about -1.3) but a fix needs a history walk-forward, not the live record. Gates: not applicable, no candidate.

**Files:** `claude/weakest-sport-2026-11-09.md`, `RELEASES.md`.

**Not changed:** `build_tennis.py`, `sports.py`, any rating, bar or record.

**Roll back:** `git revert` the commit.

## 2026-11-09 Edge over the bookmakers' price, third run: still none (tag pending)

**What changed:** nothing a reader sees. A dated note and a section in `claude/odds-groupings.md`; no code or model number changed.

**Evidence:** `tools/odds_edge_test.py` on football-data.co.uk prices, fit 2025-26 and check 2026-27, bootstrapped. Legs 2 / 4 / 6 points above fair landed -1.8 / -2.1 / -1.5 pts below fair on fit (n 4,188 / 2,539 / 1,510) and -1.9 / -2.1 / -0.6 on check (n 689 / 476 / 323); identical to 31 Oct (the check file has not grown). No positive cell on both seasons; the 65%+ cell has 11 check legs. Gates: failed.

**Files:** `claude/odds-edge-retest-2026-11-09.md`, `claude/odds-groupings.md`, `RELEASES.md`.

**Not changed:** `MAX_ABOVE_BOOK`, leg rules, any model.

**Roll back:** `git revert` the merge commit.

## 2026-11-09 Tennis surface: second source check, nothing to ship (tag pending)

**What changed:** nothing a reader sees. A dated note; no code or model number changed.

**Evidence:** the tournament-name surface map was already rejected (13 Oct: WTA +0.0024 log loss worse, p(worse) 0.88, n=2,686; ATP +0.0031, 0.95, n=1,523), so it was not rerun. Sources re-probed today: Sackmann 2026 WTA and ATP files 404, tennis-data.co.uk 403, ESPN's WTA event JSON has no surface field (venue city only). Gates: not applicable, no candidate exists. Every remaining 2026 event is hard court, so a map would change no price before April 2027.

**Files:** `claude/tennis-surface-recheck-2026-11-09.md`, `RELEASES.md`.

**Not changed:** `build_tennis.py`, `tennis.json`, `surfaceWeight`, the Daily List, any record.

**Roll back:** `git revert` the commit.

## Southern League Premier Central v its quotes: no test possible, no change, 9 Nov (tag pending)

**What changed:** nothing in the model. Dated note `claude/southern-central-gap-2026-11-09.md`.
**Evidence:** the planner's 43 of 74 (z -2.1) counts draw reads as landed. Strictly 33 of 74 won v 39.0 expected, z -1.44. Draws 23.0% v 23.9% quoted; away wins 36.5% v 27.6% quoted (the known away under-quote). No en.7sc history in `history/` and no API-Football key in the sandbox, so no replay could run; fitting on the live rows would break Rule 1.
**Files:** claude/southern-central-gap-2026-11-09.md, RELEASES.md.
**Not changed:** probabilities, bands, board-only status.
**Roll back:** `git revert` the commit.

## 2026-11-09 Card: which book and when (tag pending)

**What changed:** nothing a reader sees. A dated re-read of the book ranking and price timing added to `claude/price-lead-time-2026-11-09.md` (issue #156).

**Evidence:** 107 Card-rule pool legs: Bet365 +0.30% v average (best 65%), William Hill -0.04% (62%), Betfair -0.89%, BetVictor -1.73%. Mean first-to-last move +1.56%, football only. Not a clear book winner or a push-time case.

**Files:** `claude/price-lead-time-2026-11-09.md`, `RELEASES.md`.

**Not changed:** `CARD_BOOK`, `notify.py`, any rule.

**Roll back:** `git revert` the commit.

## 2026-11-09 When to take the Card's price: the move by lead time, and last prices after the start left out (tag pending)

**What changed:** `tools/price_timing.py` (issue #156) adds the move from first to last price by how far ahead the first price was taken (under 6h to 72h+, overall and by sport) and how close to the start the last price sat, both printed in the nightly Card review. A leg whose last price came after its latest known start is left out and counted (`lastAfterStart`): 48 of 1,394 pool legs to 9 Nov (45 tennis), one of them a Card-rule leg. `groupings.archive_pool` records `whenLast` when a build sees a different start from the one first written, so from 10 Nov a moved start can be told from an in-play price; `when` is never changed.
**Evidence:** `claude/price-lead-time-2026-11-09.md`. Pool to 12 Nov, read only, 107 Card-rule legs: first priced 48h+ out the price drifted about +2.6% to the start (55 legs), inside 48h about +0.5% (52); last price a median 2.0h before the start. Football only in effect; not enough to move the push in `notify.py`. `tests/test_price_timing.py` (lead buckets, the after-start guard, a moved start kept), `tests/test_card_pool_replay.py` (`whenLast` written only on a change); suite OK; `nametest.py` clear.
**Files:** `groupings.py`, `tools/price_timing.py`, `tools/card_review_post.py`, `tests/test_price_timing.py`, `tests/test_card_pool_replay.py`, `claude/price-lead-time-2026-11-09.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any `CARD_*` constant, `CARD_RULE`, `CARD_BOOK`, `notify.py`, any record or archive file, the page.
**Roll back:** `git revert` the merge commit.

## 2026-11-09 Every UK bookmaker's price on every card (tag pending)

**What changed:** Douglas: "Can you make sure all odds are being displayed across all cards." On 6 to 8 Nov only 1 of 11 Card picks carried a UK bookmaker's prices: NBA picks are priced from ESPN's DraftKings line and tennis from Pinnacle, so the card showed "not at William Hill" on most picks and never a William Hill combined price. Now a pick priced by one non-UK source that could reach a card (`groupings.books_wanted`: a sport the Card takes, a price inside the wider Card range, the model at the sport's bar) also takes every UK book's price from API-Sports (NBA, rugby) or The Odds API (tennis, rugby), inside the same daily call caps. API-Sports' own prices (rugby) now carry the UK books too. Every Card and Model card group has a "Prices by bookmaker" fold: each pick at each UK book, the best in blue, the combined price at each book that prices every pick. Model card picks show the William Hill price, and the Model card's header its William Hill combined price.
**Evidence:** `groupings-archive/` 6 to 8 Nov, read only (NBA 0 of 7 Card picks with UK books, tennis 0 of 3, football 1 of 1). `tests/test_uk_books.py` (UK books added with the average, margin, source and opposition untouched; only card-range picks spend calls; tennis under the Card bar not looked up; primary API-Sports pricing carries UK books; non-UK books left out); suite OK; `nametest.py` clear; Bets tab rendered at 1280 and 400 wide with the fold open (no page overflow; the table scrolls inside its box on a phone).
**Files:** `groupings.py`, `index.html`, `tests/test_uk_books.py`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** the price the Card rule reads (`odds`, `margin`, `fair`), any `CARD_*` constant or `CARD_RULE`, the best price used for grading, any record or archive file. Model card groups built before 6 Nov show no opposition price; those built since do.
## 2026-11-09 The Card's bankroll figure corrected; `flatstake` pre-registered (tag pending)

**What changed:** `tools/staking.py`, the nightly review's staking section. The bankroll figure was inverted (`0.5 / p95 drawdown x 100`: 289 units where about 35 was meant), a "season" was the sample's own length, and late groups were in the live sample. Now `bankroll()` draws a month and a season of groups at each source's own rate, at the page's stakes (two units on a 2x, one on a 3x), and gives the 95%-worst drawdown in units, the median profit and a bankroll of twice the drawdown; the review issue prints both lines. `tools/card_replay.py` pre-registers `flatstake` (one unit a group) for the 30 Nov review.
**Evidence:** `claude/card-staking-2026-11-09.md`. Live record, read only: Card 2x 5 of 22 (8.3 expected, -49% a unit), Card 3x 6 of 13 (3.4 expected, +56%); the football-data seasons have the 2x positive and the 3x negative every season, so `CARD_STAKE` is not changed. A month at the live rate: 123-unit bankroll. `tests/test_staking.py` (7 tests); suite OK; `nametest.py` clear.
**Files:** `tools/staking.py`, `tools/card_review_post.py`, `tools/card_replay.py`, `tests/test_staking.py`, `claude/card-staking-2026-11-09.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** `CARD_STAKE`, `CARD_RULE`, any record file, the page.
**Roll back:** `git revert` the merge commit.

## 2026-11-09 The live Card checked against the pool archive; two tennis variants registered (tag pending)

**What changed:** `tools/card_replay.py` on the pool rebuilt no live Card on any day under rule 6, because 42 of the live Card's 59 legs from 30 Oct to 8 Nov (20 of 23 from 4 Nov, nearly all NBA and tennis) sat in the pool only as the model's estimate. The `priced` block (#159) closes that from 10 Nov; `tools/card_integrity.py` now checks it every night (`card-leg-unreplayable`: any Card leg from `PRICED_FROM` the pool does not hold at a real price, with the coverage printed as "x of y"), so the 30 Nov review compares variants on the Card's real legs. `tools/card_replay.py` adds two pre-registered variants for the tennis leak: `notennis` (tennis off the Card) and `tennis80` (tennis at 80%+).
**Evidence:** `claude/card-pool-coverage-2026-11-09.md`. `groupings-record.json` and the pool files, read only. Approximate `--recover` read: both tennis variants +0.74 units a day against live, p(worse) 0.22, on 3 groups; nothing to act on. `tests/test_card_replay_coverage.py` (4 tests: coverage findings and count, late US game in the next day's file, days before `since`, variants patch `card_fault` and are restored); suite OK; `nametest.py` clear.
**Files:** `tools/card_integrity.py`, `tools/card_replay.py`, `tests/test_card_replay_coverage.py`, `claude/card-pool-coverage-2026-11-09.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any `CARD_*` constant, `CARD_RULE`, any record or archive file, the site.
**Roll back:** `git revert` the merge commit.

## 2026-11-09 The Card's legs by sport in the record, on the page and in the nightly review (tag pending)

**What changed:** the tennis tripwire from "The Card's return: decisions delegated" (tennis off the Card at 50 legs two standard errors under quote) is now measured by the record rather than by hand. `groupings.card_legs_by_sport` tallies the Card's settled legs by sport over the full rule (not wide, not late), each pick once a day: legs, landed, quoted, `z` and `tripwire` (true at `CARD_FLOOR_N`+ legs with `z` at or under `CARD_FLOOR_Z`), written to `groupings-record.json` as `cardLegsBySport`. The Bets scoreboard shows a tile a sport with the state in words and the legs to go; the nightly Card review issue prints the table and says in bold when a tripwire has fired, which is the next build session's cue to act.
**Evidence:** `claude/card-legs-by-sport-2026-11-09.md`. Record at 9 Nov, read only: tennis 22 of 40 (55% v 71% quoted, z -2.23, ten legs short of the floor), NBA 24 of 32 (z +0.51), football 22 of 30 (z +0.71), rugby 3 of 5. `tests/test_groupings_record.py` (once a day, full rule only, the tripwire at and one short of the floor), `tests/test_card_review_post.py` (3 tests); suite 626 OK; `nametest.py` clear; the scoreboard rendered at 1280 and 400 wide.
**Files:** `groupings.py`, `index.html`, `tools/card_review_post.py`, `tests/test_groupings_record.py`, `tests/test_card_review_post.py`, `claude/card-legs-by-sport-2026-11-09.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** `CARD_SPORTS_OFF`, `CARD_SPORT_MIN`, `CARD_RULE`, any record file (the tally appears at the next grading run).
**Roll back:** `git revert` the merge commit.

## 2026-11-09 Card decisions delegated: recorded, and the two open variants replayed as whole Cards (tag pending)

**What changed:** Douglas: "Take all decisions on providing the highest return consistently." `CLAUDE.md` gains "The Card's return: decisions delegated" with the decisions taken on the evidence: Card 3x stays (live 7 of 15 against 4.0 expected; the football-only replay is not the live Card), the 10+ cap stays on probation to the 30 Nov review, tennis stays with a tripwire (off the Card at 50 legs two standard errors under quote; now 25 of 44, z -2.1), opposition 9+ stays, no Reports page. `tools/card_legs_history.py` adds `cardUncapped` and `cardOpp7` (whole-Card replays of the two pre-registered variants on every season) so the review has the football-data side of the gate.
**Evidence:** `groupings-record.json` at 9 Nov, read only; `claude/card-seasons-2026-11-09.md`. Suite 621 OK; `nametest.py` clear.
**Files:** `tools/card_legs_history.py`, `tests/test_card_legs_history.py`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any `CARD_*` constant or `CARD_RULE`.
**Roll back:** `git revert` the merge commit.

## 2026-11-09 The weekly report (tag pending)

**What changed:** Douglas (9 Nov 2026): "I want a weekly report sent on Sunday morning 8am." `tools/weekly_report.py` reads the record files only and writes `weekly-report.json` and `.md` for the seven days ending `--to` (default yesterday): the Card's full-rule groups by day (won against expected, return at the average and best price at one unit a group, legs by sport landed v quoted, Card 3x count, days with a Card) and since 25 Oct; the Daily List by sport, landed against quoted, reserve apart; the releases in the window; `--extra FILE` merges the session's health, next-week and decision lines. `tools/weekly_report_pdf.mjs` prints it to an A4 PDF in the almanac's colours with Playwright (sandbox only, not CI). A claude.ai scheduled task, "Almanac weekly report", runs Sundays at 07:40 London and sends the PDF by push and email. The first report (2 to 8 Nov) was sent on 9 Nov.
**Evidence:** `tests/test_weekly_report.py` (stubbed record files: wide and pending groups left out, to-date window, list by sport, release parsing of both heading styles, empty week). Suite 621 OK; `nametest.py` clear.
**Files:** `tools/weekly_report.py`, `tools/weekly_report_pdf.mjs`, `tests/test_weekly_report.py`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any record file, the site, any rule.
**Roll back:** `git revert` the merge commit; pause the scheduled task from the Claude app.

## 2026-11-09 The Card over five seasons: the note (tag pending)

**What changed:** notes only, `claude/card-seasons-2026-11-09.md` and the raw output `claude/card-seasons-2026-11-09-output.txt`; `CLAUDE.md` "tested and rejected" carries the summary. No code, model or rule changed. Issue #153.
**Evidence:** `tools/card_legs_history.py --seasons 2022-23,2023-24,2024-25` in CI (run 42543472973 on the report-only PR #162). Under-market legs land 2-5 points above quote every full season but about break-even at the average price; no gap band is positive on every season, so the rule 5 cap (10+ under) is not supported over 2022-25; the opposition at 9+ lands about 5 points above quote in all five seasons (511 legs, 83.8% v 76.2%, +4%) and 4-6 loses in all five; the rule 5 Card over four seasons 93 groups, 37 won v 31 expected, +4.4%, the 2x positive every season and the 3x negative every season; the rule 6 Card on football alone makes one group in five seasons.
**Files:** `claude/card-seasons-2026-11-09.md`, `claude/card-seasons-2026-11-09-output.txt`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any `CARD_*` constant or `CARD_RULE` (a change needs the archive side too; the pool has it from mid-November).
**Roll back:** `git revert` the merge commit.

## 2026-11-09 The weekly Card replay on past seasons: crash fixed, `--seasons` added (tag pending)

**What changed:** `tools/card_legs_history.py`. (1) The 6 Nov release (#144) shipped `card_season` reading each leg's `opp` and `draw` without the `legs()` line that writes them, so `tune.yml`'s Monday run has died on `KeyError: 'opp'` since (hidden by `continue-on-error`; `card-legs-history.json` is from 2 Nov). The line, the `lopsided` opposition-price table and `card_season(variant)` with `cardRule5` are restored from the `lopsided-test` branch, where PR #143's numbers came from. (2) Issue #153: `--seasons 2022-23,2023-24,2024-25` replays each past season with the season before as its prior (`season_split` stands in for `tune.splits` while it runs) and prices it from football-data's season file; every season reports the cuts, the new `byGap` table (5-8, 8-10, 10+ under; opposition 4-6, 6-9, 9+), `lopsided`, the whole Card and its losing months. Not run here: the sandbox cannot reach openfootball or football-data; `tune.yml` runs the fit and check seasons on Monday 04:40 UTC, and the past seasons need a dispatch of `card-legs-history.yml`, which is on the `lopsided-test` branch only (never landed on `main`; restored in PR #158 for Douglas).
**Evidence:** `tests/test_card_legs_history.py` (5 tests: the legs carry `opp` / `draw`, `card_season` runs, the tables, `season_split`, `replay_split` with the fetch stubbed and `tune.splits` restored). Suite 619 OK; `nametest.py` clear.
**Files:** `tools/card_legs_history.py`, `tests/test_card_legs_history.py`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any Card rule, `tune.yml`, `card-legs-history.json` (bot-written, next Monday).
**Roll back:** `git revert` the merge commit.

## 2026-11-09 Price timing by sport and on the first real price (tag pending)

**What changed:** issue #156, first slice. `tools/price_timing.py` takes a leg's first price from the row or its `priced` block (so the 38% of pool legs archived before any book priced them count once the block exists) and reports timing and the book table for each sport apart (`bySport`), which the nightly review issue prints; `MIN_BOOK` (10) legs before a book is ranked. `legs()` / `report()` split for testing.
**Evidence:** on the pool to 9 Nov, 100 Card-rule legs, 91 football: mean move first to last +1.74% (50 drifted, 36 shortened), football +1.88%, NBA 6 legs +0.65%, tennis 3 legs -0.29%; no book has 10 priced tennis or NBA legs, so the book ranking (William Hill -0.04%, Bet365 +0.29% v the average, best 62% / 64%) is a football ranking only. Too few non-football legs to act on `CARD_BOOK` or the push time; the sample grows with `priced`. `tests/test_price_timing.py` (2 tests); suite 614 OK; `nametest.py` clear.
**Files:** `tools/price_timing.py`, `tools/card_review_post.py`, `tests/test_price_timing.py`, `RELEASES.md`.
**Not changed:** `CARD_BOOK`, `notify.py`, any rule or record file.
**Roll back:** `git revert` the merge commit.

## 2026-11-09 The Card replay reads the archived pool; the pool keeps the first real price (tag pending)

**What changed:** issue #154, first slice. `groupings.archive_pool` writes a `priced` block, once, onto a leg that was first archived as the model's estimate when a later build before its start carries a real bookmaker price (odds, best, books, margin, fair, opposition and draw price, `at`), plus `lastFair`; `POOL_KEYS` gains `id`, `listOff`, `timeEst`. `tools/card_replay.py` builds every variant from the pool from 30 Oct 2026 (`POOL_FROM`): the row's market or its `priced` block, estimate-only legs left out and counted, results for every sport (`--no-pool`, `--closing`, `--recover` documented in the tool). The nightly review issue prints the source and what was left out; a variant identical to live says so. `tools/card_integrity.py` gains `pool-unpriced`.
**Evidence:** `claude/card-pool-replay-2026-11-09.md`. Pool to 9 Nov: 2,113 legs, 564 with a real first price, 810 estimate-first with a real last price but no bookmakers' chance or books kept, 16 with a first-write opposition price; the live rule replayed on the pool as it stood made no groups on any day while the Card published 18. 9 new tests on synthetic pool files; suite 611 OK; `nametest.py` clear.
**Files:** `groupings.py`, `tools/card_replay.py`, `tools/card_review_post.py`, `tools/card_integrity.py`, `tests/test_card_pool_replay.py`, `claude/card-pool-replay-2026-11-09.md`, `CLAUDE.md`, `RELEASES.md`.
**Not changed:** any `CARD_*` rule, `CARD_RULE`, what the pool first wrote, the live Card, any record file, `.github/`.
**Roll back:** `git revert` the merge commit; pool rows written meanwhile keep their `priced` block, which nothing else reads.

## 2026-11-09 Office merge window: the workflow file was invalid since 5 Nov; Card legs workflow restored (tag pending)

**Also:** `.github/workflows/card-legs-history.yml` (6 Nov 2026) existed only on the `lopsided-test` branch, so nothing on `main` ran `tools/card_legs_history.py` on a pull request or by hand. Restored, with a `seasons` input for the past-season replay (#153: `2022-23,2023-24,2024-25`), 90-minute step timeout; report as an artifact, nothing written to the repo.

**What changed:** `office-merge.yml` used `if: secrets.OFFICE_APP_ID != ''` on two steps. The `secrets` context is not available in a step's `if`, so GitHub refused the file: no merge window has started since 5 Nov 01:13 UTC (the last scheduled success; #136 landed at 15:17), and every push to `main` since has logged a failed "office-merge.yml" run. The stale-rebase step (#136) and the four windows (#157) never ran. The condition is now a job-level `HAS_APP` flag, the form `office-agents.yml` and `ceo.yml` already use.
**Evidence:** `gh api .../workflows/office-merge.yml/runs`: 10 scheduled successes to 5 Nov 01:13, then only push failures. YAML parses; the same expression runs in two other workflows.
**Files:** `.github/workflows/office-merge.yml`, `RELEASES.md`.
**Not changed:** `agents/merge_gate.py`, `agents/rebase_stale.py`, the schedule.
**Roll back:** `git revert` the merge commit.

## 2026-11-06 Daily List bar replay, rerun: no change (tag pending)

**What changed:** a dated note only, appended to `claude/daily-list.md`. No code, model or rule changed.
**Evidence:** fit season 80%+ 81.4% of 86; 75%+ 81.5% of 168; 85%+ 65.7% of 35 (-15.4 v 80%, interval -25.8 to -6.8). Check season only 8 calls at 80% (75.0%); all intervals span zero. No league has 30 calls at 80%.
**Files:** `claude/daily-list.md`, `RELEASES.md`.
**Not changed:** `LIST_MIN`, `sports.list_threshold`, any per-league bar.
**Roll back:** `git revert` the commit.

## 2026-11-06 Calibration by band and sport, rerun: nothing to ship (tag pending)

**What changed:** a dated note only, `claude/calibration-rerun-2026-11-06.md`. No code, model or rule changed.
**Evidence:** football check season (1,557 calls) 55%+ +5.7 points, 60-70% +7.0 [+0.6,+13.2] under quote, fit season on quote, so Rule 3 is not met. Hockey (-8.3 at 60-70%), baseball (-5.0 at 62%+) and college basketball (-4.6 at 60-70%) stay over-stated; 70%+ calls are inside noise. Same as 29 Oct.
**Files:** `claude/calibration-rerun-2026-11-06.md`, `RELEASES.md`.
**Not changed:** `calibration.json`, `sports.json`, `calibration_bands.py`.
**Roll back:** `git revert` the commit.

## 2026-11-06 Tennis legs in groups (27/49 v 35): located, nothing to ship (tag pending)

**What changed:** a dated note only, `claude/tennis-legs-gap-2026-11-06.md`. No code, model or rule changed.
**Evidence:** 49 settled tennis legs since 19 Oct landed 27 (55%) v 35.4 quoted. Model under 75%: 16 of 32; 75%+: 11 of 17 (65% v 81%, z about -1.6). Built before the 29 Oct tennis floor: 19 of 34; after: 6 of 10. No tennis price history exists to replay a further rule and every cut is under 50 legs, so choosing one would fit the live record (Rule 1).
**Files:** `claude/tennis-legs-gap-2026-11-06.md`, `RELEASES.md`.
**Not changed:** `groupings.py`, `CARD_SPORT_MIN`, any model number.
**Roll back:** `git revert` the merge commit.

## 2026-11-06 Tennis Daily List: ATP bar to 80% (tag pending)

**What changed:** `build_tennis.LIST_MIN` for ATP (and the ranked key) 75% -> 80%. ATP picks at 75-80% go to the reserve; WTA stays at 75%. No rating or confidence number changed.
**Evidence:** planner 58 of 78 v 64.3. Live located (read only): Wuhan 5 of 10, Paris Masters 1 of 4, 75-80% band 20 of 30. Rule from history, not the record: ATP own 75-80% band landed 75.5% (237) in 2025 and 77.7% (112) in 2026, under the 80% rule both times; ATP 80%+ 89.7% / 88.5%; WTA's own band passes (81.8% / 88.4%). `claude/tennis-list-own-band-2026-11-06.md`. nametest clear; tests pass.
**Files:** `build_tennis.py`, `tests/test_tennis_names.py`, `claude/tennis-list-own-band-2026-11-06.md`, `RELEASES.md`.
**Not changed:** WTA bar, ratings, calibration, list order, any record file.
**Roll back:** `git revert` the merge commit, or set ATP / ATP_RANKED back to 0.75.

## 2026-11-06 (tag pending): free-source check for uncovered leagues (docs only)

**What changed:** nothing for readers. Re-probed free sources for the remaining gaps and recorded the result in `claude/data-expansion-plan.md`.
**Evidence:** ESPN scoreboard slugs for 3. Liga, Liga Portugal 2, UAE, Poland 1/2, Sweden 3, Australia 2 and Vietnam return 400; slugs that answer 200 are already covered.
**Files:** `claude/data-expansion-plan.md`, `RELEASES.md`.
**Not changed:** no source, model or league code.
**Roll back:** `git revert` the merge commit.

## 2026-11-06 Retry for the NFL/MLB/NBA/rugby and tennis ESPN fetches (tag pending)

**What changed:** `sports._day` and `build_tennis._get_day` tried each ESPN host once and gave up, so one network blip dropped a whole day of games (football's `_espn_day` already retried). Now, when every host fails on something transient (timeout, reset, 5xx, 429), the round repeats once after a 1s pause. A 4xx such as 404 is not retried. `sports._day` still returns None (unreadable, not an empty day) after the last try; tennis still returns [] with the errors logged.
**Evidence:** `tests/test_sports_fetch_retry.py` with a fake failing source: blip on every host then success, persistent failure (None, 2 rounds of calls), 404 (one round). Full suite 593 tests OK; `nametest.py` passes.
**Files:** `sports.py`, `build_tennis.py`, `tests/test_sports_fetch_retry.py`, `RELEASES.md`.
**Not changed:** football fetching, any model number, ratings, archives. Football-data and API-Football paths already had retries and last-good-copy fallbacks.
**Roll back:** `git revert` the merge commit.

## 2026-11-05 Fixture audit note (tag pending)

**What changed:** nothing on the site. Audit of the 5 Nov predictions file written up in `claude/data-integrity.md`.
**Evidence:** 1,830 rows; 0 unrated, 0 wrong-date kick-offs, no spelling splits; 18 rescheduled fixtures stored twice (archive key includes date), 3 Mexican home/away pairs (probably two-leg ties), Badajoz v Tenerife in `es.cup` and `afc.143`. None on the Daily List. `nametest.py` passes.
**Files:** `claude/data-integrity.md`, `RELEASES.md`.
**Not changed:** the archive key, matcher and `LIVE_NAMES` (a key change alters the scoreboard; Douglas's call).
**Roll back:** `git revert` the merge commit.

## 2026-11-05 Tests for predictability.py (tag pending)

**What changed:** nothing for readers. Added unit tests for the pure maths in `predictability.py`, the module with the most logic and no tests.
**Evidence:** 9 new tests (logit/sigmoid clamps, linear solver incl. singular matrix, logistic fit direction, log loss, top-hit, standardise/design, league shift sign and shrinkage) all pass; full suite and nametest pass. No bug exposed.
**Files:** `tests/test_predictability.py`, `RELEASES.md`.
**Not changed:** any module code, model, or record.
**Roll back:** `git revert` the merge commit.

## release-2026-11-11-ncaab (tag pending): college basketball November-December calibration curve

**What changed:** college basketball probabilities in November and December use their own calibration curve (early non-conference games land above quote); January-April a slightly shrunk one. Daily List bar stays 85%. Other sports unchanged.

**Evidence:** fitted on 2024-25, checked on 2025-26 (5,814 games): log loss 0.5523 -> 0.5499, gain 0.0024, p(worse) 0.01; 65%+ gap 0.013 -> 0.022 (limit +0.01, passed). Redo of #137 on current main, identical numbers. `claude/ncaab-season-phase-2026-11-05.md`.

**Files:** `sports.py` (`PHASE_MONTHS`, `fit_phase_calibration`, `calibrate(..., when)`), `sports.json` (ncaab only), `tests/test_sports_phase_cal.py`, the note.

**Not changed:** Elo constants, list bar, other sports, the Card.

**Roll back:** `git revert` the commit; ncaab returns to the single calibration.

## release-2026-11-09-2 (pending tag): double the office

**What changed.** Douglas (9 Nov 2026): "Please double output. I want agents
working more." Four sprints a day (00:30, 06:30, 12:30, 18:30 UTC, was two),
the daily cap on office pull requests 14 to 28, `MAX_OPEN` agent pull
requests 6 to 12, and four merge windows (03:00, 09:00, 15:00, 21:00 UTC)
that rebase and retry stale pull requests. Beside the office, a scheduled
Claude build session now runs four times a day (03:17, 09:17, 15:17, 21:17
London) on the Card backlog and HQ's backlog, merging its own pull requests
once the checks pass. HQ's planner serves 24 tasks a day (was 14).

**Files.** `.github/workflows/office-agents.yml`, `.github/workflows/office-merge.yml`,
`agents/pick_task.py`, `CLAUDE.md`; footyalmanac-hq `scripts/planner.py`.

**Cost.** Roughly double the Anthropic API spend of the office and four
Claude sessions a day on the account; watch both for a week.

**Roll back.** `git revert` the release commit; the scheduled task is
paused from the Claude app.

## release-2026-11-09 (pending tag): the Card gets its own autonomous review

**What changed.** Douglas (9 Nov 2026): "I want to set up an autonomous
agent that makes improvements to the almanac platform. The ultimate goal is
to make consistent returns on group accumulators." Four pieces, all advisory,
none changes a rule on its own:

1. `card-review.yml`, nightly at 03:40 UTC: `tools/card_integrity.py` (legs
   pending with a result on file, stale rule numbers, Card legs with no
   opposition price, missing pool files, a stale record), `tools/card_replay.py`
   on every pre-registered variant (now with the opposition's price on each
   archive leg and a JSON report), `tools/price_timing.py` (first v last
   pre-start price, each UK book against the average, by hour) and
   `tools/staking.py` (flat, half and quarter Kelly, drawdown, bankroll). One
   `card-review` issue a night; integrity findings open an `office-backlog`
   issue for the engineer, which the next sprint works first.
2. HQ's planner (footyalmanac-hq #47) now leads the backlog with the Card:
   return at stake, legs by sport, price and the opposition's price, empty
   days, the move to the closing price, and five standing Card tasks.
3. Paid prices go to legs that matter: a tennis match is priced only at the
   Card's bar or on the Daily List; college football and basketball take no
   API-Sports calls (ESPN prices them free).
4. `tests/test_groupings_card.py` ran on a fixed "future" date that had
   passed, failing 12 tests from today; it now rolls to the next Saturday in
   GMT.

**Files.** `.github/workflows/card-review.yml`, `tools/card_integrity.py`,
`tools/price_timing.py`, `tools/staking.py`, `tools/card_review_post.py`,
`tools/card_replay.py`, `tools/card_legs_history.py`, `groupings.py`
(`AS_SKIP`, the tennis price filter), `tests/`, `CLAUDE.md`.

**Roll back.** `git revert` the release commit; the nightly review stops and
pricing returns to every pool leg.

## release-2026-11-07 (pending tag): a tennis pick is judged against the match's recorded start

**What changed.** Douglas (7 Nov 2026): "why are these results pending".
Andreescu v Giovannini (Cali quarter-final, 5 Nov) was listed for 19:00 and
began 19:25; the 19:09 build saw it still to start and re-stamped the row,
and the grader, holding the row to its listed time, refused the pick as
published late although it had been up since 00:35. The Card 2x leg sat
pending with the result on file. `score_tennis.start_of` now judges every
price against the start ESPN recorded for the match when there is one (until
now only a placeholder time was replaced); the archive also keeps each row's
first publish stamp (`firstPublished`). Two archived picks change from
unscored to graded, both won; the Card leg settles on the next build.

**Files.** `score_tennis.py`, `build_tennis.py`, `tests/test_tennis_late_start.py`.

**Roll back.** `git revert` the release commit; the two rows return to unscored.

## release-2026-11-06-2 (pending tag): home / draw / away prices on every row

**What changed.** Douglas (6 Nov 2026): "why can't I see the odds for home
and away". The price chip under each Daily List and board row now lists the
bookmakers' three prices in the order every bookmaker uses, home / draw /
away, the pick in bold and the opposition in red when priced 9+ (the Card's
condition); two-outcome sports show the two. Replaces "best 1.18 · opp 10.89".

**Files.** `index.html` (`hdaChip`, `oppLine`). Checked at 1280 and 400.

**Roll back.** `git revert` the release commit.

## release-2026-11-06 (pending tag): the opposition's price, Card rule 6

**What changed.** Douglas (6 Nov 2026) noticed his winning hand-picks were
favourites whose opposition was priced 10-12 and his losers favourites whose
opposition was priced about 4. Tested on last season's replay it holds:
favourites with the opposition at 9+ landed 84.1% v 76.0% quoted (+3.3% as
singles, +5.8% at best price), with the opposition at 4-6 they landed 63.7% v
61.8% (-4.4%); the same split holds within one favourite price band and on
this season. With the Card's under-market rule, 106 legs landed 86.8% v 75.4%
(+7.5%) last season and 39 landed 84.6% v 76.5% (+3.7%) this. So: every price
source now records the opposition's price (and the draw's) on each leg, for
every sport; a football Card leg needs the opposition priced 9+
(`CARD_OPP_MIN`, `CARD_RULE` 6); the page shows the opposition's price on
every Bets leg, substitute and Daily List row that has a bookmaker price;
groups may have five picks (`CARD_LEGS`), since legs with the opposition at
9+ are short.
Football only for the rule: in two-outcome sports the opposition's price is
the arithmetic complement of the favourite's. `claude/opposition-price-2026-11-06.md`.

**Evidence.** `tools/card_legs_history.py` `lopsided` table, run on PR #143
(`card-legs-history.yml`, new, runs the replay on any pull request that
touches the tool).

**Files.** `groupings.py`, `index.html`, `tools/card_replay.py` (variants
`rule5`, `opp7`), `tools/card_legs_history.py`, `.github/workflows/card-legs-history.yml`,
`tests/test_groupings_card.py`, `claude/opposition-price-2026-11-06.md`, `CLAUDE.md`.

**Not changed.** The Model card, the wide groups, the Daily List's ranking
(prices are display only), the pool archive format (two keys added).

**Roll back.** `git revert` the release commit; the Card returns to rule 5 at
the next build and the record tallies the rule-6 groups apart (`cardByRule`).

## release-2026-11-05-3 (pending tag): more from the office, twice a day

**What changed.** Douglas asked for more delivered output from the autonomous
agents (5 Nov 2026). Four things: (1) `office-merge.yml` now rebases every open
`office-agent/*` pull request that is behind `main` onto it and pushes with the
App token (`agents/rebase_stale.py`), so its checks and evaluation run again and
the merge gate can judge it fresh; a branch that will not rebase cleanly is left
with one comment. Before this, one human commit on `main` stranded every open
agent pull request ("main changed since evaluation"), and six piled up and
stopped the sprint from 1 to 5 Nov. (2) A second sprint at 18:30 UTC, and the
daily cap on office pull requests raised from 8 to 14. (3) Every agent brief
now says the deliverable is a change that passes the gates, a note only when
the evidence fails them (57 of the first 78 merged agent pull requests were
findings only). (4) With `release-2026-11-05-2`, a full queue idles the sprint
instead of failing it.

**Evidence.** Sprint runs 1-5 Nov: every one failed on the matrix JSON or
opened nothing; #96, #97 and #109 closed as Odds-tab-era and conflicting;
#106, #121 and #127 rebased by hand and their evaluations re-ran.

**Files.** `.github/workflows/office-merge.yml`, `.github/workflows/office-agents.yml`,
`agents/rebase_stale.py` (new), `agents/pick_task.py`, `CLAUDE.md`.

**Not changed.** The merge gate itself (still fails closed, still needs owner
approval on workflow and security paths), `SPRINT_SIZE`, the evaluation layer.

**Roll back.** `git revert` the release commit. The second cron and the rebase
step go with it; nothing on the site is touched.

## release-2026-11-05-2 (pending tag): the sprint idles, not fails, when the agent queue is full

`agents/pick_task.py --active-agents` printed "N agent pull requests already open; waiting for them to merge" to stdout, which the workflow reads as the JSON agent matrix, so every sprint from 1 to 5 Nov 2026 failed before any agent ran. The message now goes to stderr and the matrix is `[]` (an idle day). The queue itself filled because the merge gate refuses a pull request once a human commit lands on `main` after its evaluation (re-run needed), and nothing re-ran them; three were rebased by hand today (#106, #121, #127) so their evaluations re-run. Files: `agents/pick_task.py`. Roll back: revert the commit.

## release-2026-11-05 (pending tag): site analytics

Cloudflare Web Analytics on the page (Douglas's Cloudflare account; the beacon tag in `index.html`'s head). Visitors, page views, countries, devices and referrers, live and historical, with no cookies and no consent banner. `spa: true` counts each tab change as a view, since the tabs write their name to the URL hash. Nothing else on the site changes. Files: `index.html`. Roll back: revert the commit.

## release-2026-10-31-3 (pending tag): college basketball off the Card

Douglas, after a Sunday Card 2x carried two college basketball picks on the week the season opens: a sport with no live record on the site stays off the Card (`CARD_SPORTS_OFF` gains `ncaab`), as college football does. Its picks still reach the Daily List and the reserve. Back on when it has 50 graded games and lands on quote. Files: `groupings.py`. Roll back: revert the commit.

## release-2026-10-31-2 (pending tag): the Model card, on paper beside the Card

Douglas, 31 Oct 2026: "the whole point is that our model is meant to pick winners". Every day the build now also makes a **Model 2x** and a **Model 3x** (`groupings.build_model_card`, `MODEL_KINDS`): the model's own picks, chosen the opposite way to the Card. A leg is a core-league pick (or 75%+ tennis) the model rates 60%+ and at or above the bookmakers' chance (`model_fault`), and the group's chance is the model's number (`as_model`), not the market's. Same price band and kinds. Held as first built until first kick-off, frozen and archived like a Card group, graded on its own line (`cardModel`), never staked (stake 0), never pushed, fixtures may overlap the Card's. The Bets tab shows them in an "On paper" section under the card with a scoreboard tile. At the 30 Nov review the two lines are compared; if the model's own picks beat the price, the Card changes. Files: `groupings.py`, `index.html`. Roll back: revert the commit; archived Model groups are harmless.

## release-2026-10-31 (pending tag): the Card's gap to the market capped at 10 under (rule 5)

Douglas, on Norwich (model 49%, bookmakers 61%) on the day's Card 3x. A football pick now needs the model between 5 and 10 points under the bookmakers' chance (`CARD_UNDER_MAX` 0.10, with `CARD_UNDER_MARKET` 0.05). Evidence: 10+ under lost on every sample (live archive −3.6%, 2025-26 −6.4%, 2026-27 −9.8%); 5-10 under was positive on all three (+9.5%, +6.2%, +5.8%). That far under, the model has not rated the side. `CARD_RULE` 5, tallied apart in `cardByRule`; groups already frozen stand. `tools/card_replay.py`'s `under5to10` variant is now the live rule, replaced by `uncapped` (rule 4) for the 30 Nov review. Files: `groupings.py`, `tools/card_replay.py`, `tests/test_groupings_card.py`. Roll back: revert the commit.

## 2026-10-31 Office review and next week's priorities (tag pending)

**What changed:** a dated note only, `claude/office-review-2026-10-31.md`. No code, model or rule changed.
**Evidence:** read from `RELEASES.md`, the `claude/` notes and the record summaries: football list 101 of 127 (79.5% v 81.6%), tennis list 53 of 68, sports reserve 108 of 166 v 71.1%, Card on current rules 5 won v 5.9 expected (19 groups).
**Files:** `claude/office-review-2026-10-31.md`, `RELEASES.md`.
**Not changed:** any code, model number or record file.
**Roll back:** `git revert` this commit.

## 2026-10-31 Results grading audited: no bug found (tag pending)

**What changed:** a dated audit section in `claude/results-review-board.md` only. No code, model or rule changed.
**Evidence:** 105 graded games checked against ESPN (football 50, sports 30, tennis 25), 0 disagreements; whole-file consistency of football (8,239 rows), tennis (1,145) and sports (220) clean; postponed, abandoned, walkover, retirement and extra-time handling read and already covered by `tests/test_grading.py`.
**Files:** `claude/results-review-board.md`, `RELEASES.md`.
**Not changed:** `score.py`, `score_tennis.py`, `sports.py`, any record file.
**Roll back:** `git revert` this commit.

## 2026-10-31 Leg properties re-scanned: no rule (tag pending)

**What changed:** dated notes only (`claude/leg-property-rescan-2026-10-31.md`, a section in `claude/odds-groupings.md`). No code, model or rule changed.
**Evidence:** `tools/odds_edge_test.py` + `tools/leg_property_test.py`, fit 2025-26 (310 eligible legs, +9.3 pts v quote), check 2026-27 (42 legs, +8.8). No cut holds on both seasons; the model-not-above-market cap removes about half the fit legs (limit a fifth) and fails on check (+7.9 v +8.8 for all).
**Files:** `claude/leg-property-rescan-2026-10-31.md`, `claude/odds-groupings.md`, `RELEASES.md`.
**Not changed:** `groupings.py`, `MAX_ABOVE_BOOK`, any model number.
**Roll back:** `git revert` this commit.

## 2026-10-31 Edge over the bookmaker price re-tested: none (tag pending)

**What changed:** dated notes only (`claude/odds-edge-retest-2026-10-31.md`, a section in `claude/odds-groupings.md`). No code, model or rule changed.
**Evidence:** `tools/odds_edge_test.py`, fit 2025-26 (12,510 legs), check 2026-27 (1,749). Legs 2/4/6 pts above fair landed -1.8/-2.1/-1.5 pts below fair on fit and -1.9/-2.1/-0.6 on check; no positive cell on both seasons, bootstrapped.
**Files:** `claude/odds-edge-retest-2026-10-31.md`, `claude/odds-groupings.md`, `RELEASES.md`.
**Not changed:** `groupings.py`, the 5-point cap, any model number.
**Roll back:** `git revert` this commit.


## release-2026-10-30-2 (pending tag): push-triggered builds spare the API-Football allowance

A build started by a push to `main` now runs with `AF_FRUGAL=1` (deploy.yml) and reuses the day's cached API-Football fixtures and prices up to a day old (`sources.AF_FRUGAL_TTL`, `odds.AF_FRUGAL_TTL`) instead of fetching them again; the six scheduled builds refresh as before. Twenty-five builds on 29-30 Oct 2026, most of them merges and manual dispatches, plus the Pro plan lapsing to the free tier, left the board on its last copy. Files: `odds.py`, `sources.py`, `.github/workflows/deploy.yml`. Roll back: revert the commit.
## release-2026-10-30-4 (pending tag): the whole priced pool archived daily

`groupings.archive_pool` writes every priced leg of every sport, for each day the build prices, to `groupings-archive/pool-<date>.json.gz`: first price and numbers as first published, then last pre-start price on later builds. Douglas, 30 Oct 2026: "will we be able to test other models and how they would have performed, e.g. at minimum of 4 legs". The 30 Nov review rebuilds any Card rule on the month's real pool, every sport, from these files; results join from the graded records. Nothing on the site changes. Files: `groupings.py`, `tests/test_groupings_card.py`. Roll back: revert the commit; the pool files are harmless.

## release-2026-10-30-3 (pending tag): the API-Football "spent" marker expires

Once a build heard the daily allowance was gone it left a marker for the UTC day and no later build that day made a call. On 30 Oct 2026 the Pro plan lapsed and was renewed within the hour, and the board stayed on its last copy all afternoon. The marker is now honoured for `sources.AF_SPENT_TTL` (90 minutes); after that the next build spends one call to find out, and re-marks if the answer is still "spent". Files: `sources.py`. Roll back: revert the commit.

## 2026-10-30 Odds API tennis keys: logging already live, cause unconfirmed (tag pending)

**What changed:** a dated note only, `claude/odds-api-tennis-keys-2026-10-30.md`. No code, model or rule changed.
**Evidence:** the requested logging (`tennisKeys`, `noKey`) shipped on 20 Oct (#55). This sandbox has no `ODDS_API_KEY` (the /sports list returns 401) and no archived report holds the key list, so the matcher could not be tested; no fix was guessed.
**Files:** `claude/odds-api-tennis-keys-2026-10-30.md`, `RELEASES.md`.
**Not changed:** `groupings.py`, matching, ledger caps, any model number.
**Roll back:** `git revert` this commit.

## 2026-10-30 Croatia, Serbia, Ukraine, Hungary, Korea, UAE: already covered (tag pending)

**What changed:** a dated note only, `claude/af-new-leagues-coverage-2026-10-30.md`. No code, model or rule changed.
**Evidence:** the five top flights have been on the board via `sources.AF_NEW` since 20 Oct and the UAE Pro League via `af.301`; the 30 Oct archive holds fixtures for all six (3-11 each). Extra API allowance per build: 0 (shared date pool). A replay is not possible here: no API key, and `history/` holds none of them. No hit-rate claim is made.
**Files:** `claude/af-new-leagues-coverage-2026-10-30.md`, `RELEASES.md`.
**Not changed:** `sources.py`, any model number, the Daily List, `NEW_BOARD_ONLY`.
**Roll back:** `git revert` this commit.

## 2026-10-30 Tennis legs in groups (22/40 v 28): located, nothing to ship (tag pending)

**What changed:** a dated note only, `claude/tennis-legs-gap-2026-10-30.md`. No code, model or rule changed.
**Evidence:** 40 settled tennis legs since 19 Oct landed 22 (55%) v 28.4 quoted. Model under 75%: 15 of 31 (48%); model 75%+: 7 of 9 (78%, on quote). The 75% floor (`CARD_SPORT_MIN`, `CARD_RULE` 2, 29 Oct) already excludes the weak kind. No tennis price history exists to replay a further rule, and every other cut is 40 legs or fewer, so choosing one would fit the live record (Rule 1).
**Files:** `claude/tennis-legs-gap-2026-10-30.md`, `RELEASES.md`.
**Not changed:** `groupings.py`, any model number, the Daily List.
**Roll back:** `git revert` the commit.

## 2026-10-30 Tennis list shortfall (39/51 v 42): located, nothing to ship (tag pending)

**What changed:** a dated note only, `claude/tennis-list-shortfall-2026-10-30.md`. No code, model or rule changed.
**Evidence:** the planner's 39 of 51 v 42.2 is the 15 Oct fortnight that was already reviewed on 28 Oct. At the 75% bar, 115 of 139 graded main-draw picks landed (82.7%) v 82.3% quoted; 16-30 Oct 59 of 69 (86%) v 82%. The gap is Wuhan (6 of 12, before the 8 Oct ratings fix). The 75-80% band lands 82% v 77%, so a stricter bar would not help; the own-band chip is already live (26 Oct); tennis has no tier-2 leagues.
**Files:** `claude/tennis-list-shortfall-2026-10-30.md`, `RELEASES.md`.
**Not changed:** `build_tennis.py`, `LIST_MIN`, `LIST_ON`, any model number.
**Roll back:** `git revert` the merge commit.

## release-2026-10-30 (pending tag): a published Card group holds through price drift

The 05:40 build replaced a Card 3x (Bristol Rugby, Houston Rockets, Miami Heat, 3.00) that Douglas had placed overnight, because its combined price had slipped to 2.86, under the 3x band's 3.00 floor. The band is how a group is chosen, not a rule a pick can fail, so the re-check now holds a published group while its combined price stays within `CARD_DRIFT` (10%) of its band; only a larger move, or a pick failing the leg rule, replaces it. `tests/test_groupings_card.py` PriceDrift. Files: `groupings.py`, `tests/test_groupings_card.py`. Roll back: revert the commit.

## release-2026-10-29 (pending tag): the Card's leg rule replayed on past seasons

`tools/card_legs_history.py` replays the Card's football leg rule (bookmakers' 60%+ at 1.15-1.90, the model 5+ points under the market) over the 2025-26 and 2026-27 walk-forward replays against football-data.co.uk prices: picks, landed v quoted, singles return at average and best price, closing-line value, price bands, and one treble a day. Run weekly by `tune.yml`, written to `card-legs-history.json`. Advisory; the site does not change. Douglas, 29 Oct 2026: "Why can't you grab data from last season and learn that way?"

Files: `tools/card_legs_history.py`, `.github/workflows/tune.yml`. Roll back: revert the commit.

## 2026-10-29 Goals-market value backtest (tag pending)

**What changed:** `tools/goals_value.py`: the model's over-2.5 number (the same Dixon-Coles grid as the match-winner numbers, shrunk as the site publishes it) against football-data.co.uk's over/under 2.5 prices on the fit season (2025-26) and the check season (2026-27 to date), walked forward with `tune.lambdas` and matched with `odds.match`. Reports log loss model v market, calibration by band, and the value picks (model above the best price by 5%+) by hit rate, ROI and closing-line value with a bootstrap, per season; `valueGate` passes only when CLV is positive on both. `tune.yml` runs it after the weekly report (advisory, `continue-on-error`) and commits `goals-value.json`. Douglas's request after the Card review: is the goals market priced more softly than match winner?

**Files:** `tools/goals_value.py`, `.github/workflows/tune.yml`, `CLAUDE.md`, `RELEASES.md`. Workflow path: owner's merge. **Not changed:** anything on the site; nothing flags value from this yet. **Roll back:** remove the step.

## 2026-10-29 Placed marker, flagged replacement pushes, pre-registered replay variants (tag pending)

**What changed:** a **Mark as placed** button on each open Card group (per browser): the page then shows "Placed" on that version, or, if a pick failed the rule and the slot shows a different group, which version was placed and that the record grades the published one. Replacement pushes carry a `REPLACEMENT:` title and the warning tag. `tools/card_replay.py` rebuilt around the live `build_card` pieces with pre-registered variants (`under8`, `under10`, `four3x`, `wider`) and `--since`, for the 15 and 30 Nov reviews; on October all are within noise of the live rule. One test added; 576 pass.

**Files:** `index.html`, `notify.py`, `tools/card_replay.py`, `tests/test_notify.py`, `claude/betting-groups-review-2026-10-29.md`, `RELEASES.md`.

**Not changed:** the leg rule, floors, stakes, grading. **Roll back:** `git revert` the merge commit.

## 2026-10-29 A push to the phone when the build makes a Card group (tag pending)

**What changed:** `notify.py`, run by `deploy.yml` straight after `groupings.py`. Each Card group whose status is new or replacement and whose `first` stamp is this build's gets one push through ntfy (free, iOS and Android apps): title "Card 2x · Fri 30 Oct · 2.18 (2.24 at William Hill)", a line a pick with kick-off and the William Hill price (or the best price and who has it), the units to stake, when the group freezes (its first kick-off) and how many substitutes it carries. The topic is the only secret (`NTFY_TOPIC`); unset, nothing is sent. Two tests; 575 pass.

**Setup (owner):** install the ntfy app, subscribe to a private topic (a long random name), add it as the repository secret `NTFY_TOPIC`. Workflow path, so this merge needs Douglas's approval.

**Files:** `notify.py`, `tests/test_notify.py`, `.github/workflows/deploy.yml`, `RELEASES.md`, `CLAUDE.md`. **Roll back:** remove the step from `deploy.yml`, or delete the secret.
## 2026-10-29 Daily List bar replay, no change (tag pending)

**What changed:** nothing for readers. Replay of the league bar written up in `claude/daily-list.md`.
**Evidence:** 2025/26: n=344/189/140/94/60/39 at 70/75/77.5/80/82.5/85%, hit 77.6/79.4/81.4/81.9/80.0/69.2%; only 85% differs from 80% (-12.5, -21.3 to -4.4). 2026/27: 11 calls at 80% (81.8%), 20 at 75% (80.0%); intervals span zero. No league has 30 calls at 80%.
**Files:** `claude/daily-list.md`, `RELEASES.md`.
**Not changed:** `LIST_MIN`, any model number, per-league bars.
**Roll back:** `git revert` the commit.

## 2026-10-29 Calibration by band and sport, rerun (tag pending)

**What changed:** nothing in the model or the page. A dated note, `claude/calibration-rerun-2026-10-29.md`, from re-running `calibration_bands.py` (football walk-forward replay and each sport's own replay, bootstrap 90% intervals; `record.json` not read).

**Evidence:** football 55-80% inside noise on the fit season (1,504+ calls); check season 60-70% under-confident +7.9 [+1.3,+14.2] on 136 calls but the fit season disagrees (+0.6), so Rule 3 blocks a refit; 85%+ still over-confident (68.3% v 88.8%, 41 pooled, 2 out of sample). Sports: ice hockey over-confident at 55-70% on the check window (-6.1 [-8.8,-3.4] at 55%+, fit window fine), baseball -5.0 [-8.2,-1.6] at 62%+ again, college basketball -4.6 at 60-70%; NBA, rugby union and league calibrated.

**Files:** `claude/calibration-rerun-2026-10-29.md`, `RELEASES.md`. **Not changed:** `calibration.json`, `sports.json`, any constant. **Roll back:** `git revert` this commit.

## 2026-10-29 The Card: core leagues only again, after the two-rule replay (tag pending)

**What changed:** `CARD_CORE_ONLY` back to True, Douglas's decision at 11:59 after both rules were replayed on October with the live Card machinery: core only +5.5 units on 15 staked (10 groups, 5 won); wider in +0.5 on 32 (21 groups, 8 won); the extra groups lost 5 units, nearly all Card 3x built from wider picks (2 of 10). `CARD_MAX_GROUPS` stays at 6. Page copy updated.

**Evidence:** `claude/betting-groups-review-2026-10-29.md`, seventh pass. **Files:** `groupings.py`, `index.html`, `RELEASES.md`, `CLAUDE.md`. **Roll back:** set `CARD_CORE_ONLY = False`.

## 2026-10-29 The Card: wider leagues in under the market rule, core first, six groups a day (tag pending)

**What changed:** Douglas, 10:05: "I want what will build the biggest return on a monthly basis". With a positive edge on every leg the monthly return is the number of qualifying groups times their edge, so the card now takes every pick with evidence behind it: `CARD_CORE_ONLY` False, football from any league but a cup or an international (`card_league`), all still under the market rule; core-league picks are chosen first at an equal chance (`CARD_CORE_NUDGE` 0.02, selection only, the quoted chance unchanged); up to six groups a day (`CARD_MAX_GROUPS`).

**Evidence:** `claude/betting-groups-review-2026-10-29.md`, fifth pass: wider-league picks under the market landed 76.8% v 66.8% quoted (n=56, +4% a unit) against core 81.9% v 67.6% (+12%); wider picks not under the market 58.3% v 67.1% and stay out. Midweek pool roughly doubles (5 to 8 picks against 0 to 3). Two tests changed or added; 573 pass; `nametest.py` clear.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_card.py`, `RELEASES.md`, `CLAUDE.md`. **Roll back:** set `CARD_CORE_ONLY = True` and `CARD_MAX_GROUPS = 4`.

## 2026-10-29 The Card: no clock lock; a group is open until its first kick-off (tag pending)

**What changed:** Douglas, 29 Oct 2026: "remove all locks ... worldwide games over a 24 hour period ... the ability to place at any time and for the days ahead". The 07:00 lock is gone. A group (today or any of the next three days) is open until its first kick-off: every build re-checks it and it holds unless a pick fails the rule (the reason logged), its bench is rebuilt, and at the first build after its first kick-off it is frozen as last published and archived (`groupings.first_kick`, `build_card`; `lockAt` is the group's first kick-off). No group is "late" any more. The record's honesty is unchanged: what is graded is what was published before the first game started. The Bets page copy says so; the one-day 12:00 lock of the previous entry is superseded, and today's old-window groups stay off the page for today (`CARD_TRANSITION`, now a date set).

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_card.py`, `RELEASES.md`, `CLAUDE.md`. Tests adapted (a group freezes at its first kick-off, not at 07:00); 572 pass; `nametest.py` clear.

**Not changed:** the leg rule, the four-group cap, grading. **Roll back:** `git revert` the merge commit.

## 2026-10-29 Today's card built under the new rules, locking 12:00 (tag pending)

**What changed:** a one-day exception (`groupings.CARD_TRANSITION`): for 29 Oct 2026 the one-window card locks at 12:00 UK instead of 07:00, so a card built after the morning's merge is a proper locked card under rule 4 rather than a late one, and the groups locked under the old windows that morning are left off the page for this date (they stay in the archive and the record as they were). Douglas's request: "I want today's card to be the new formatting and improved chance of success". Delete the entry from `CARD_TRANSITION` once the date has passed. One new test; 570 pass.

**Files:** `groupings.py`, `tests/test_groupings_card.py`, `RELEASES.md`. **Roll back:** empty `CARD_TRANSITION`.

## 2026-10-29 The Card: groups locked under the old windows stay on the page (tag pending)

**What changed:** on the day the three windows became one, groups already locked as Overnight, Daytime or Evening (placed bets) were dropped from the day by `build_card` because their window no longer existed. A locked group in a legacy window is now kept as locked or under way until it settles, never rebuilt; `card_windows` lists a legacy window only while such a group sits in it, and the page heads it "locked under the old three-window card". An unlocked group in an old window is dropped, not rebuilt. One new test; 569 pass.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_card.py`, `RELEASES.md`.

**Roll back:** `git revert` the merge commit.

## 2026-10-29 The Card: a football pick needs the model 5+ points under the bookmakers (#99, tag pending)

**What changed:** `groupings.CARD_UNDER_MARKET` 0.05: a football leg on the Card (full rule only) needs the model's chance at least 5 points under the bookmakers' fair chance. The Bets page states it.

**Evidence:** `claude/betting-groups-review-2026-10-29.md`, fifth pass. On the priced archive the model-under-market legs landed 81.9% v 67.6% quoted (n=72, +2.6 se), 78.7% v 68.2% outside the one hot week (n=47), and 76.8% v 66.8% in the wider leagues (n=56); legs not under the market land at or below quote in every slice. Home/away, draw share and price band were tested and rejected (the price cut is the hot week). The same note corrects the core-only evidence: outside the hot week core legs are on quote, +6 points at 1.2 se.

**Not changed:** the wider-rule fallback, the 60% floor, the lock, grading, any model number. **Roll back:** set `CARD_UNDER_MARKET = 0`.

## 2026-10-29 The Card: up to four groups a day, stake weights, a record line per rule (#99, tag pending)

**What changed:** up to four groups a day (`CARD_MAX_GROUPS`): 2x, 3x, then a second 2x and 3x from the fixtures left, each clearing the same floor and range; `seq` joins `card_slot`, so each locks, holds and archives on its own. Stake weights (`CARD_STAKE`): two units on each 2x, one on each 3x, shown on each group and in the playbook. A record line per `CARD_RULE` version (`cardByRule`), with z, on the Bets scoreboard.

**Evidence:** `claude/betting-groups-review-2026-10-29.md`, fourth pass. **Roll back:** set `CARD_MAX_GROUPS = 2`.

## 2026-10-29 The Card: core leagues only, and the floor (#99, tag pending)

**What changed:** football picks on the Card come from `engine.LEAGUES` without the API-Football wider set, cups and internationals (`CARD_CORE_ONLY`, `core_league`). Every tally in `groupings-record.json` carries `z`, won against expected in standard errors; the Bets scoreboard shows the Card as On quote, Under quote or Under the floor (`CARD_FLOOR_Z` -2 on `CARD_FLOOR_N` 50+ settled groups, the retire signal). `tools/card_replay.py` (advisory): the Card rebuilt on the priced archive under several leg rules.

**Evidence:** `claude/betting-groups-review-2026-10-29.md`, third and fifth passes (the core-only comparison is confounded by when wider leagues were first priced; kept as the cautious side). **Roll back:** set `CARD_CORE_ONLY = False`.

## 2026-10-29 The Card: one window a day, William Hill prices, substitutes (#99, tag pending)

**What changed:** the card is built once a day from every game kicking off between 07:00 UK and 07:00 the next morning, locks at 07:00 and is placed once (`CARD_WINDOWS`, `uk_slot`, `window_end`); the three windows made no difference to accuracy (71 / 72 / 73% landed) and left each slot drawing on a third of the pool. Days to 28 Oct keep their windows in the record. Every pick carries each UK bookmaker's price (`bookOdds`, from API-Football's per-book odds and The Odds API; `odds.af_parse_odds` adds `ukBooks`, cache version 3); the card is written for William Hill (`CARD_BOOK`), a preference, nothing refused for it. Each group carries up to three substitutes (`bench_for`, `CARD_BENCH`) that keep it in range, frozen at lock.

**Evidence:** `claude/betting-groups-review-2026-10-29.md`, time windows and second-change sections. **Roll back:** restore `CARD_WINDOWS` to the three windows and bump `CARD_RULE`.

## 2026-10-29 The Card: NFL and college football off, tennis legs to 75% (tag pending)

**What changed:**
- **NFL and college football legs are off the Card** (`groupings.CARD_SPORTS_OFF`, `card_fault`). College football was already kept off through `listOff`; NFL was not.
- **A tennis leg needs the model and its tested rate both at 75% or more** (`groupings.CARD_SPORT_MIN`). Football, rugby and the NBA are unchanged at the 60% bookmaker floor.
- `CARD_RULE` is 2, so any unlocked Card group rebuilds under the new rule on the next build; locked groups stand as published. The Bets page states the rule, and the avoid list marks a tennis pick under the floor as caution and an NFL pick at 70%+ as avoid.

**Evidence:** `claude/betting-groups-review-2026-10-29.md`. 379 settled legs, 4 to 29 Oct: football landed 75.8% against 75.3% quoted (n=223) and on quote in every UK time window; tennis 64.8% v 78.0% (n=91), college football 70.4% v 85.4% (n=27), NFL 60.0% v 73.0% (n=20). On the Card itself tennis legs landed 19 of 32. Time of day makes no difference (overnight 71.4%, daytime 72.0%, evening 72.8%; z -0.16): the Overnight window's 1 of 6 is 13 tennis legs landing 6. The Daily List's top N by confidence over the same days landed 291 of 379 (76.8%) against the legs' 274 (72.3%), with equal mean quoted chance. Four new tests in `tests/test_groupings_card.py`; 560 tests pass; `nametest.py` clear.

**Files:** `groupings.py`, `index.html`, `tests/test_groupings_card.py`, `claude/betting-groups-review-2026-10-29.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** any model number, the Daily List (tennis stays on it at 75%), the windows and lock times, the 60% bookmaker floor for the other sports, the retired kinds' rules, grading.

**Roll back:** `git revert` the merge commit, or set `CARD_SPORTS_OFF = set()` and `CARD_SPORT_MIN = {}` and bump `CARD_RULE`.

## 2026-10-28 Daily List: confidence order, two groups of five, tennis back on (tag pending)

**What changed:**
- **Order.** The Daily List and the pinned day list sort by confidence first, tested rate second (`index.html` `byStrength`, `daylist.strength`). Before, the tested rate came first, which ranked band tables from different families against each other (a 97% Brighton under an 80% Kyrgyz pick) and was not monotone on the live record, where confidence was.
- **Bug fixed.** A started football pick sorted last in Strongest order: `build.py` never archived `accuracy` for football (the other sports did), so `daylist.py` gave every pinned football row strength 0. The archive row now carries it and `daylist._accuracy` recomputes it for older archives.
- **Groups.** In strongest order each day's list is labelled Group A, Group B and The rest, with a "landed" tally per group once results are in; `daylist.groups` and the `daylist.json` summary carry `groupA` / `groupB`. Group A is the strongest five at 85% or better and nothing weaker (`GROUP_A_MIN`), so it is short or empty on a thin day: on the record since 29 Sep, top-five picks at 85%+ landed 53 of 59 (90%) against 89 of 107 (83%) with the bar at 80%. Group B is the next five.
- **Tennis back on the list**, both tours at 75% (`build_tennis.LIST_ON`), Douglas's decision on the evidence below.

**Evidence:** `claude/daily-list-order-review-2026-10-28.md`, reproduced by `tools/list_order_replay.py`. 218 settled list picks since 29 Sep: landed by confidence 82 / 86 / 86 / 100% up the bands, by tested rate 88 / 75 / 85 / 83 / 77%. Top 10 on the 7 days with 10+ picks: confidence 57 of 70, tested rate 55 of 70 (within noise; nothing beats confidence). Tennis: the 15 Oct removal rested on 39 of 51 v 42.1 expected (1.1 standard errors); at the bar, 75%+ landed 61 of 75 before and 78 of 88 since in the reserve, 139 of 163 (85%) overall. College football stays off (80%+ 26 of 35, 74% v 86%, z -2.1). New tests in `tests/test_daylist.py`; tennis tests updated; 554 tests pass; `nametest.py` clear. Page checked in headless Chromium at 1280px and 400px with a simulated 19-pick day (no football data in the cloud sandbox).

**Files:** `index.html`, `daylist.py`, `build.py`, `build_tennis.py`, `tools/list_order_replay.py`, `tests/test_daylist.py`, `tests/test_tennis_names.py`, `tests/test_tennis_live_bands.py`, `claude/daily-list-order-review-2026-10-28.md`, `CLAUDE.md`, `RELEASES.md`.

**Not changed:** the 80% rule and every bar, any model number, the reserve rule, college football (`sports.LIST_OFF`), grading. The groups have no record of their own yet.

**Roll back:** `git revert` the merge commit. To take tennis off alone, set `LIST_ON` back to False.

## 2026-10-28 football-data.co.uk outage keeps the last good copy (tag pending)

**What changed:** football-data.co.uk is the only source for Poland, Switzerland, Romania, Finland and Ireland (history and fixtures). After its retries failed, `_fdx_text` returned an empty string with no warning of its own, so those five leagues lost all data for the run. A clean download is now kept in `.afcache/fdx-*` (CI already persists that folder); on an outage the last good copy is used with a stderr warning giving its age, or a warning that no copy exists. An outage is still never remembered as an empty answer, and a 404 still means "absent".
**Evidence:** three new tests with a fake failing source (`tests/test_source_failures.py`): fallback to the copy with the warning, no copy gives the warning and "", and the existing not-cached-as-empty test. Full suite 551 tests pass; nametest.py passes. No model, rating or ranking code touched.
**Files:** sources.py, tests/test_source_failures.py, RELEASES.md.
**Not changed:** retry counts, ESPN and API-Football handling (already retried or cached), any model number.
**Roll back:** `git revert` the merge commit.

## 2026-10-28 Data audit: reversed fixture in Ukraine noted (tag pending)

**What changed:** notes only. Audit of the 28 Oct archive found no duplicates, wrong dates or doubtful name matches, and one home/away flip (Chernihiv v Yarud Mariupol', af.334, 1 Nov).
**Evidence:** 2,116 rows checked; nametest.py passes; the flipped pair is `below`, not on the Daily List.
**Files:** claude/data-integrity.md, RELEASES.md.
**Not changed:** matcher, LIVE_NAMES, archive keys (a fix alters the scoreboard; Douglas's call).
**Roll back:** `git revert` the merge commit.

## 2026-10-28 Free-source check for uncovered leagues: none feasible (tag pending)

**What changed:** notes only. `claude/data-expansion-plan.md` records the re-check of German 3. Liga, Liga Portugal 2, UAE and Poland 2.
**Evidence:** openfootball 2025-26 `de.3.json` and `pt.2.json` are 404; `at.2.json` exists but has no 2026-27 fixtures and Austria 2 is already on the board via API-Football (`af.219`); football-data.co.uk `new/` unchanged.
**Files:** claude/data-expansion-plan.md, RELEASES.md.
**Not changed:** any code, model number or Daily List rule.
**Roll back:** `git revert` the merge commit.

## 2026-10-27 Tests for build_tennis.py's pricing core and ESPN parser (tag pending)

**What changed:** nothing a reader sees. 16 new tests in `tests/test_build_tennis_core.py` for the parts of `build_tennis.py` that had none: `price_match` (symmetry, 400 points = 10:1, surface fallback and blend), `dampen`, `tier_of` boundaries, `_matches_from_event` (completed, scheduled, doubles and malformed skipped, short dates), `is_walkover`, `is_retirement`, `pred_key`.

**Evidence:** no bug found. Suite 549 tests OK, `nametest.py` clear.

**Files:** `tests/test_build_tennis_core.py`, `RELEASES.md`.

**Not changed:** any production code or model number.

**Roll back:** `git revert` this commit.

## 2026-10-27 Tennis surface: source check, nothing to ship (tag pending)

**What changed:** nothing a reader sees. A dated note only.

**Evidence:** the tournament-name map was already rejected on 13 Oct (WTA +0.0024 log loss worse, p(worse) 0.88, n=2,686; ATP +0.0031, 0.95, n=1,523), so it was not rerun. ESPN's event, grouping and competition JSON carry no surface (only city and court name); Sackmann's 2026 WTA file is a 404; tennis-data.co.uk answers 403 from the sandbox. No automatable source. The rest of the 2026 calendar is hard court, so a map would change no price before April 2027.

**Files:** `claude/tennis-surface-source-2026-10-27.md`, `RELEASES.md`.

**Not changed:** `build_tennis.py`, `tennis.json`, any model number, the Daily List rule.

**Roll back:** `git revert` this commit.

## 2026-10-26: Warn when unplayed fixtures sit on a stale date (tag pending)

**What changed:** `build.py` now counts unplayed fixtures dated before the build window and prints a `::warning::` line naming up to twelve of them. Nothing is published differently: those fixtures were already dropped, and they still are. The warning makes the drop visible in the CI log.

**Why:** on 26 Oct 2026 the board showed no Sevilla v Osasuna and no PSG v Lyon for tonight. openfootball still held both on 25 Oct with no kick-off time, so the build filtered them out silently. A reschedule the source has not caught up with looked identical to a match that does not exist.

**Not changed:** the Daily List rule (unconfirmed days stay off), the window, the sources. Catching a moved fixture needs a cross-check against ESPN for the same dates, which runs in CI only (the cloud sandbox cannot reach ESPN). That is the next step, not this release.

**Tests:** `nametest.py` clear; `python3 -m unittest discover -s tests` 533 tests OK.

**Files:** `build.py`, `RELEASES.md`. Roll back by reverting this commit.

## 2026-10-26: College football landing below its quotes; no change (tag pending)

**What changed:** a note only (`claude/cfb-all-calls-gap-2026-10-26.md`). No code or model change.

**Evidence:** live 109 of 173 (63%) v 69% quoted (z -1.8). On held-out history, cfb calls at 62%+ landed 78.9% v 75.0% quoted (fit, 615) and 83.2% v 76.2% (check, 863); no cut (experience, neutral site, early or late season) lands under quote. K, home advantage, carry-over and margin were already swept by `sports.py --tune`. A change would be fitting on the record (Rule 1).

**Files:** `claude/cfb-all-calls-gap-2026-10-26.md`, `RELEASES.md`.

**Not changed:** `sports.py`, `sports.json`, probabilities, `LIST_OFF`.

**Roll back:** `git revert` this commit.

## Isthmian League Premier v its quotes: no test possible, no change, 26 Oct (tag pending)

**What changed:** nothing in the model. Dated note `claude/isthmian-gap-2026-10-26.md`.
**Evidence:** the planner's 24 of 45 (z -2.1) counts draw reads as landed against a win-or-draw expectation. Strictly 21 of 45 won v 22.6 expected (mean confidence 50.3%), z -0.49. Away wins 18 v 29% quoted. No en.7i history exists in `history/` and the sandbox has no API-Football key, so no replay could run. Fitting on the 45 live rows would break Rule 1.
**Files:** claude/isthmian-gap-2026-10-26.md, RELEASES.md.
**Not changed:** probabilities, bands, board-only status.
**Roll back:** `git revert` the commit.

## Other-sports reserve v its quotes: tested, no change, 26 Oct (tag pending)

**What changed:** nothing in the model or the reserve rule. Dated note `claude/sports-reserve-gap-2026-10-26.md`.
**Evidence:** reserve 13-26 Oct, 113 settled: 63.7% landed v 71.6% quoted. College football 43 of 68 (63.2% v 73.7%) and NFL 7 of 15 (46.7% v 68.5%) carry it; NBA 16 of 20 and rugby are on quote. On held-out history cfb calls at 60%+ landed 78.1% v 75.5% quoted (check) and 74.3% v 74.9% (fit); NFL windows disagree (69.5% v 71.8% check, 74.0% v 70.8% fit). A live-only exclusion would be fitting on the scoreboard (Rule 1).
**Files:** claude/sports-reserve-gap-2026-10-26.md, RELEASES.md.
**Not changed:** reserve floor, list bars, probabilities, grading.
**Roll back:** `git revert` the commit.

## Weekly retune: add only the files that exist, 26 Oct (tag pending)

**What changed:** Weekly retune #11 failed at "Commit the result" with exit 128: `git add` of a pathspec that does not exist. `home-advantage.json` (added to the step on 25 Oct) and `tuning-pending.json` (25 Oct, two-pass gate) are written only once a refit passes, so on a Monday with nothing to apply neither exists and the add refused. The step now adds each file only if it is on disk. The refit itself ran; only the commit of the advisory report was lost, and it will be written next Monday.
**Files:** .github/workflows/tune.yml, RELEASES.md.
**Roll back:** `git revert` the commit.

## Every Card leg keeps its full board row after kick-off, 26 Oct (tag pending)

**What changed:** Douglas saw two legs of an under-way Card 3x with no fixture row under them while the third had one. The row was drawn from the live files (data.js, tennis-data.js, sports-data.js), which carry only games not yet started, with the pinned Daily List as the only fallback; a leg that had started and was not on the list lost its row. `groupings.legs` now freezes the board row each leg was built from into the leg (`fx`, football, tennis and the other sports), it travels into the archive with the group, and the page draws it when the live lookup and the pinned list both miss. Checked under jsdom with legs for games absent from every live file.
**Files:** groupings.py, index.html, tests/test_groupings_record.py, RELEASES.md.
**Roll back:** `git revert` the commit; archives written meanwhile keep an unused `fx` field.

## "Stale" only on a group you can still place, 26 Oct (tag pending)

**What changed:** a leg in a locked group, or one that has started, now shows "price at lock · read HH:MM" instead of the red "stale" tag. The lock freezes the price by design, so a read time over two hours old is provenance there, not a warning; "stale" stays on groups that can still be placed, where it means the price may have moved. The snapshot line on the Bets tab says the same. Douglas asked what stale meant on an under-way Card.
**Files:** index.html, RELEASES.md.
**Roll back:** `git revert` the commit.

## Tennis rows with no order of play show TBC and stay off the Card, 26 Oct (tag pending)

**What changed:** Douglas found Monday-morning tennis rows that are really Tuesday's, and ruled that nothing goes on the Daily List or its reserve unless it is being played that day: a tennis row with an unconfirmed day is never `list` or `reserve`, whatever its confidence. Before the order of play is out, ESPN dates a match at midnight New York (04:00 UTC), which the tennis tab showed as 05:00 that morning. The date is the round's first day, not the match's: on the archive, 15-25% of such rows were played the day after, and about half in rounds that run over two days (Antwerp 16 of 28). `build_tennis` now marks those rows `timeTbc`; the tennis tab shows "TBC, day not confirmed" with a title explaining why, sorts them last on their date, and the lede says so; `groupings.card_fault` and `mult_fault` refuse a tennis leg with an estimated time, since it cannot be placed in a window (the order of play is normally out before the 21:00 lock). Also removed the stale lede line about the ATP ranking layer, off since 7 Oct.
Second commit: the pinned Daily List (`daylist.py`) also drops them. It pins each game on its latest archived price published before its start, and a stand-in start of 04:00 UTC had already "started" by the morning, so the 00:10 build's rows (Alcaraz, Djokovic, Zverev, Osaka and 13 more today) were frozen into the day and no later build could remove them. `daylist.unconfirmed_day` now skips any tennis row with a stand-in time, in old archives too.
**Files:** build_tennis.py, groupings.py, daylist.py, index.html, tests/test_tennis_live_bands.py, tests/test_daylist.py, RELEASES.md.
**Not changed:** the tennis model, grading (score_tennis already judges late prices against real starts), the Daily List.
**Roll back:** `git revert` the commit.

## Overnight 26 Oct: lighter page, phone nav, honest Bets tab, tennis live chip; the home/away tilt tested and not shipped (tag pending)

**What changed:**
- *Page weight.* `build.py` no longer inlines `record.json` into `dashboard.html`; the football record goes to `record-data.js`, and it, `sports-record.js` and `tennis-record.js` load only when "How it went" is first opened (`loadRecords` in `index.html`). A small `window.__RECORD_SUMMARY__` (overall, tiers, ladder, list, reserve, bands, recent list results; ~10 KB) is inlined for the lede, stat strip and Daily List. `dashboard.html` 4.4 MB -> 0.43 MB (100 KB gzip) on a local 2-day build; no record script before first paint. `deploy.yml` copies `record-data.js` into `_site`; `.gitignore` lists it.
- *Phone navigation.* At <=860px the tab bar is sticky and a single horizontally scrolling row, 44 px tall; Starred moves to third behind Daily List and Bets. Chips, segment buttons, day pickers, add/remove buttons and star buttons get 40-48 px tap targets on phones; the desktop look is unchanged.
- *Bets tab.* Every priced leg shows its read-at time (UK) and turns red with a "stale" tag after 2 hours on the viewer's clock (`pricedAt` from `groupings.read_at`, the cache file's mtime); estimated prices sit in their own labelled cell with "estimated from the model, not a bookmaker price"; each group's headline is three labelled figures (Bookmakers, Model, Tested) in place of "Lands about N in 10"; the scoreboard leads with the strict won/lost Card record beside the Late groups tile; the snapshot disclaimer is on the tab and in the footer; the dead `renderOdds` view and `#odds` markup are removed; the Google link is secondary.
- *Tennis tested chip.* `score_tennis.py` writes `liveBands` (per tour, 5-point bands from 55%, graded rows only) into `tennis-record.json`; `build_tennis.accuracy_for` quotes a band's live landed rate when it has 30+ graded picks (`rateSource: "live"`, chip reads "N% live") and otherwise shows no chip, because the archive-walk bands describe a different model (true surfaces, main draw only). Today ATP quotes live for 55-75% and WTA for 55-80%. List and reserve rules are unchanged.
- *Home/away tilt, tested and not shipped.* The live record's away under-quote (quoted 44.7%, landed 51.7%) reproduces on the replay smaller (+2.1 fit, +4.8 check). `tools/home_away_tilt.py` sweeps `ha_scale` 0.80-1.00 with and without a curve refit and RHO: every value from 0.80 to 0.98 is better on both seasons, but the check gain is 0.0001-0.0004 against a noise sd of 0.0010-0.0012, p(worse) 0.36-0.59. Fails the gain and p(worse) gates; no engine change. `claude/home-away-tilt-2026-10-26.md` has the full table and what would settle it (about 3,000 check fixtures, around January). AF_EXTRA leagues cannot be gated on the replay at all (no check season), which is where most of the live gap sits.
- *Tests.* `test_seasons` no longer asserts derivation on leagues the API pins (the bot's first `current/af-seasons.json` had broken it on main). Suite now 528 tests.

**Not changed:** every model constant, `calibration.json`, `europe.json`, the Daily List rule, the Card rules, the cover header. Visual changes were checked under jsdom only (no browser in the cloud session): a look at the page on a phone and at desktop width is still owed.
**Files:** build.py, index.html, groupings.py, score_tennis.py, build_tennis.py, tools/home_away_tilt.py, .github/workflows/deploy.yml, .gitignore, tests/ (test_record_summary, test_tennis_live_bands, test_home_away_tilt, test_groupings_sources, test_ladder, test_seasons), claude/home-away-tilt-2026-10-26.md, CLAUDE.md, RELEASES.md.
**Roll back:** `git revert` the merge commit, or any single commit; each piece is self-contained. Reverting the page-weight commit restores the inlined record without data loss.

## One tier ladder, 25 Oct (tag pending)

**What changed:** `score.py` is now the only definition of the confidence tiers: `TIERS` plus `TIER_BACKTEST` are written to `record.json` as `ladder`, and `index.html` reads that, keeping its literal only as a fallback for a page built without a record. `tests/test_ladder.py` fails if the fallback drifts. Rule 7 and the open item updated in CLAUDE.md. No number changes.
**Files:** score.py, index.html, tests/test_ladder.py, CLAUDE.md, RELEASES.md.
**Roll back:** `git revert` the commit.

## Full review: 21 fixes from the 25 Oct audit, 25 Oct (tag pending)

**What changed:** the review in `claude/full-review-2026-10-25.md` found 22 bugs; 21 are fixed here, one commit each, all behind the test suite (508 tests) and `nametest.py`. Nothing fits anything on the live record and no model constant moves.

*Betting layer (bugs 1, 2, 8, 9, 10, postponed legs).* Graded group rows now carry `wide`, `late`, `locked`, `lockAt`; the Card record counts only full-rule groups locked on time, `cardWide` and a new `cardLate` are tallied apart and shown as such. Best price is taken over UK-licensed bookmakers only (`odds.UK_BOOKS`), falling back to the average with no book named; the odds cache is re-read once (`AF_ODDS_VERSION` 2). Per-fixture prices go through `sources._af_get`, so a quota-exhausted empty answer is never cached as "no prices", and `recheck_card` keeps the last known price through an outage like `recheck` does. Locked Card slots are read from `groupings-archive/<date>.json`, never rebuilt or duplicated. Each Card leg records `lockPrice` from the first build after lock and the record grades `returnedLock`/`stakedLock` beside the average and best returns. Postponed or abandoned football legs void (from the day pool's status, or no result 72 h after kick-off once the other legs are settled), so the group pays on the rest.

*Football (bugs 3, 4, 5, 6, 11, 12, 21, 22).* The headline, tiers and bands are strict (`won`: the pick won); draw reads are a separately labelled `reads` figure, and result rows mark a draw read "≈". `rankings.py` learns the latest FIFA release from the overview endpoint, scans from the newest id on file, logs failures instead of swallowing them, and warns when the file is over 45 days old. AF extra-league seasons come from the API's `seasons[].current` (`current/af-seasons.json`, refreshed every 3 days) and a league with no current season is logged, not silently fetched finished. `engine.current_season` derives every season string from the date (split-year on 1 July, calendar on 1 January); `tests/test_seasons.py` fails CI if any competition's season does not contain the current year. A club with no prior season stays flagged under Celtic's Law for its first six games. `accuracy_for` returns no tested rate for native cups, continental ties and AF_NEW leagues. `MAX_GOALS` 10 -> 15: ordinary 1X2 triples move by under 1e-6; lopsided ties (lambda 9 v 1) recover the 28% of mass the old grid dropped, which changes their scoreline, BTTS and over-2.5 figures. The build and `score.live_results` anchor on the UK date.

*Tennis and sports (bugs 13, 15, 16, never-played games, rugby).* Retirements enter live tennis ratings at the tour's fitted `retirementWeight` (WTA 0.5, ATP 1.0) instead of full weight, matching the fit. A price archived against ESPN's placeholder start is judged against the real start from history where one exists (five rows rescued today, no grade changes). `sports.CHECK` ends at 27 Sep 2026, the first archived sports prediction, so the tested window never overlaps the live record. Archived sports picks never played are void after 7 days once the feed's history has passed the date (13 of 16 today). `build_tennis.py --unrated-report` gives the evidence for the provisional-rating idea (bug 14, not implemented: the true own-tour gap is 2.7% ATP / 4.1% WTA, smaller than the review said). Rugby World Cup months include November.

*Automation (bugs 7, 17, 18, 19, 20, spend guard).* `deploy.yml` refuses a football build under 40% of the last committed archive, guards sports and groupings as tennis is guarded, and fails a scheduled run that has no App token instead of losing the archive. Note-only pushes no longer rebuild. The office sprint has one cron (06:30) and skips when more than 8 office pull requests already exist today. Elena runs once per brief (`labeled` only, cancel-in-progress). `unknown` paths no longer auto-merge; `home-advantage.json` and the new `tuning-pending.json` are protected and in the calibration class. The weekly calibration and home-advantage refits apply only after two consecutive Monday passes (`tune.consecutive_passes`, `tuning-pending.json`), so the earliest auto-apply is two weeks out.

*Not changed:* bug 14 (needs evidence), `claude.yml` (its skips were the author gate working, no `@claude` mentions since 4 Oct), every model constant, `calibration.json`, `europe.json`, the Daily List rule, and the home/away tilt finding, which goes to the replay next.

**Files:** groupings.py, odds.py, sources.py, engine.py, build.py, score.py, rankings.py, build_tennis.py, score_tennis.py, sports.py, tune.py, tools/model_ideas.py, tools/julius_export.py, daylist.py, index.html, agents/policy.json, agents/open_pr.sh, agents/pick_task.py, .github/workflows/deploy.yml, office-agents.yml, ceo.yml, tune.yml, tests/ (new: test_groupings_record, test_af_odds, test_af_seasons, test_seasons, test_no_prior, test_accuracy_for, test_draw_reads, test_max_goals, test_uk_today, test_two_pass_gate and others), claude/full-review-2026-10-25.md, claude/world-rankings.md, claude/results-review-board.md, CLAUDE.md, RELEASES.md.
**Roll back:** `git revert` the merge commit (or any single fix commit; each is self-contained). The odds cache re-reads itself; `tuning-pending.json` and `current/af-seasons.json` can be deleted.

## Douglas's model ideas tested; per-league home advantage learns weekly, 25 Oct (tag pending)

**What changed:** Douglas asked for home advantage, table position, goals for and against and stronger recent form in the model, and for it to learn each week. Tested on the walk-forward replay (fit 5,262 fixtures last season, check 902 this season, paired, live calibration): table position, last-5 goal difference and last-3 points make it worse at every strength; recent goals against the season average add nothing; **home advantage per league** helps (fit −0.0010 log loss, check −0.0007) but misses the p(worse) gate (0.33 against 0.30) on the short current season. So it is built and wired in, and refitted every Monday by `tools/model_ideas.py --fit-home` in `tune.yml`, which writes `home-advantage.json` only when it passes the same gates as the calibration. Today it does not, so **no prediction changes yet**. The other ideas are re-tested weekly, advisory.
**Files:** engine.py (`LEAGUE_HOME`, `league_home`), build.py (league path), replay.py (`home_s`), tune.py (replay uses the live factor), tools/model_ideas.py, .github/workflows/tune.yml, tests/test_league_home.py, claude/model-ideas-2026-10-25.md, CLAUDE.md, RELEASES.md.
**Not changed:** every live number (no `home-advantage.json`), the calibration, the Daily List rule.
**Roll back:** `git revert` the commit; delete `home-advantage.json` if it has been written.

## The tab bar on Analysis, and the football record on the Football page, 25 Oct (tag pending)

**What changed:** Douglas: "I want all sports tabs to stay where they are when you click into the analysis page" and "the football record removed from the header and held at the top of the football page like the other sports give an overview."
- **Analysis** now carries the Almanac's own tab bar, same order and size, with Analysis highlighted. Each tab links back to that board: the Almanac opens the tab named after the `#` (`index.html#fixtures`, `#sport:nba`, `#today`), and keeps the address in step as tabs change, so the browser's back button returns to the same board. Sport tabs hide by the same rule as on the Almanac (Analysis now loads `sports-data.js` and `sports-record.js` for it).
- **Football record** is out of the red header panel (now: this week, Daily List, games priced, list record). The Football page opens with an overview like the other sports: games graded, read right against always backing the home side, Strong calls landed, the Daily List's football record.
**Checked:** unit tests, nametest, Playwright at 1280px and 390px on both pages, no horizontal scroll, no script errors.
**Files:** index.html, analysis.html, RELEASES.md.
**Roll back:** `git revert` the commit.

## Daytime and Evening groups: tennis times fixed, a wider rule for empty windows, 25 Oct (tag pending)

**What changed:** Douglas: "There is no day time and evening bets. There needs to be some even if they update on later rebuilds."
- **The cause:** before the order of play is out, ESPN dates every tennis match at midnight New York (04:00 or 05:00 UTC). So Monday's Vienna, Basel and Aosta first rounds, 30 of the 38 tennis picks, were filed in the Overnight window, and Daytime and Evening were left with a handful of picks. Such a match now takes its tournament's usual first start from `history-tennis/` (Vienna and Basel 09:00 UTC), marked `timeEst` and shown as "TBC" (`tennis_placeholder`, `tennis_starts`). On Monday's board: Daytime 31 tennis picks, Overnight 7 (was 36).
- **Wider rule:** a window the full rule leaves empty takes the best group under a wider rule: three to five picks priced 1.08 to 2.10 at the bookmakers' 55%+, the model still no more than 5 points above them (the weekend's losing pattern stays out). Marked "Wider rule" in red, rebuilt on every build until the lock, replaced by a full-rule group once one can be made, archived and locked like any Card group, and graded apart (`cardWide`; `card` and `cardByWindow` stay full-rule only). A fifth pick lets five short favourites (1.17 each) reach 2x.
- An empty window now says why (too few priced picks so far) and that it is checked on every build.
**Checked:** unit tests (8 new), nametest, Playwright at 1280px and 390px.
**Files:** groupings.py, index.html, tests/test_groupings_card.py, claude/the-card-2026-10-25.md, CLAUDE.md, RELEASES.md.
**Not changed:** the full Card rule, lock times, any model.
**Roll back:** `git revert` the commit.

## One Bets page, Daily List first, fewer tabs, cup rows banded right, 25 Oct (tag pending)

**What changed:** Douglas: "merge today's bets in odds ... into one page to be the 2nd tab behind daily list", drop the WNBA and Baseball tabs, and make sure Analysis is accurate.
- **Bets** (the `today` view) is now the one betting page, second tab. It keeps everything from Today's bets (the playbook, the Card by window with lock times, Leave these out, Check a slip, the scoreboard by window) and takes from Odds what was still useful: the re-check log, the accumulator calculator and the day-by-day results history (`ogRecord(true)`, compact: the scoreboard tiles already sit above it; Card chips now read "Daytime 2x 2.19"). The Odds tab is gone; the Multipliers and Wider groups it showed are no longer built (since the Card), and their record stays in the history.
- **The Daily List opens first** again. Tabs: Daily List, Bets, Football, Tennis, the sport boards, Starred, How it went, Analysis, HQ. **Baseball and WNBA have no tab** (too few games); their picks still reach the Daily List and the record. The tab grid is 15 cells, five even rows of three on a phone.
- **Analysis and the record:** until 24 Oct domestic cup rows (afc.*) stored the untempered confidence beside tempered probabilities (Berkhamsted showed 61% but was banded at 80%). `score.py` now grades every row on its published top probability (`max(p)`), so those rows move to the band and tier they were shown at, on the record, How it went and the Analysis page (which reads `record.json` on every build). On the archive the two numbers differ on 643 of 56,732 rows, every one a cup row.
- The scoreboard tiles fit six to a row on desktop.
**Checked:** nametest, the unit tests, Playwright at 1280px and 390px (no horizontal scroll, no script errors, one calculator on the page).
**Files:** index.html, score.py, CLAUDE.md, RELEASES.md.
**Not changed:** every model, the Card rules, the Daily List rule, `renderOdds` (left in the code, unreachable, so a revert restores the tab).
**Roll back:** `git revert` the commit.

## Tennis back on the Card, 25 Oct (tag pending)

**What changed:** Douglas: "yes put tennis back on". Tennis picks may go on the Card again (`listOff` False for tennis legs in `groupings.legs`), held to the Card rule like every sport: a bookmaker price (now mostly Pinnacle, through PinnWire), the bookmakers at 60%+, the model no more than 5 points above them, no qualifying rounds. Tennis stays off the Daily List (`build_tennis.LIST_ON`) until its live record holds, and is still never used in the retired strict groups.
**Evidence:** the tennis model re-tested sound on 1,096 Sep-Oct main-draw matches (75%+ calls landed about 85%); it came off the list on 15 Oct as a precaution after a bad fortnight. With Pinnacle prices the Card can hold each pick to the market's number.
**Files:** groupings.py, tests/test_groupings_card.py, claude/the-card-2026-10-25.md, RELEASES.md.
**Roll back:** `git revert` the commit.

## API-Sports pricing fix: pace calls, never cache an error, 25 Oct (tag pending)

**What changed:** the first live run matched 0 of 15 NBA legs although names and times matched exactly (`tools/odds_match_probe.py`, run in CI): the free plan allows 10 calls a minute per product, the burst got rate-limit replies, and those were cached as "no games" for four hours. Calls are now paced 6.5 seconds apart per product, error replies are logged and never cached (new cache prefix, so the bad copies are ignored), and legs past tomorrow are skipped (the free plan only serves yesterday to tomorrow).
**Files:** groupings.py, tests/test_groupings_sources.py, tools/odds_match_probe.py, RELEASES.md.
**Roll back:** `git revert` the commit.

## Prices for more sports: API-Sports (free) and PinnWire, 25 Oct (tag pending)

**What changed:** Douglas: "scope a few different free sources, let's utilise what we can". `tools/odds_probe.py` (run in CI by `.github/workflows/odds-probe.yml`, report on the `odds-probe-report` branch, counts and field names only) found:
- **API-Sports' other products** answer on the existing API-Football key, each on its own free plan of 100 calls a day: rugby, basketball, hockey, baseball, american-football (and handball, volleyball). Odds come per game; on 25 Oct they priced 2 of 3 rugby, 3 of 3 basketball, 3 of 3 hockey, 3 of 3 NFL games tried (baseball 0 of 3, end of season).
- **PinnWire** (Pinnacle prices, 13 sports including tennis and rugby): the shared demo key is used up by others each day; a free personal key (100 calls a day, no card) needs an email signup by Douglas.
- **ESPN** carries NBA odds on the day of the game only (25 Oct: 7 of 7 that day, 0 of 25 for the next three days).
Built: `price_api_sports` (rugby, NBA, WNBA, college basketball, NHL, MLB, NFL, college football; games cached 4 hours, odds 90 minutes, at most 85 calls a UK day per product; average, best price and its bookmaker) and `price_pinnwire` (only with the `PINNWIRE_KEY` secret: one call per build at most, every prematch market at once, legs nothing else priced, never football). Order: API-Football, ESPN soccer, ESPN, API-Sports, PinnWire, The Odds API.
**Files:** groupings.py, .github/workflows/deploy.yml (passes the keys to the groupings step), tools/odds_probe.py, .github/workflows/odds-probe.yml, tests/test_groupings_sources.py, claude/the-card-2026-10-25.md, RELEASES.md.
**Not changed:** every model and rule; prices still never feed a model.
**Roll back:** `git revert` the commit.

## The Card: windowed, locked groups at 2x and 3x, and the playbook, 25 Oct (tag pending)

**What changed:** Douglas, after the weekend: bet the day before or in the morning and leave it; groups over the same hours; one fixture per group; 2x and 3x+ returns; all sports considered. **The Card** replaces the Double / Treble / Wider / Multiplier groups as what the site puts forward:
- Three UK windows by kick-off: **Overnight** 00:00-09:00, **Daytime** 09:00-17:00, **Evening** 17:00-24:00. In each, a **Card 2x** (pays 2.0+) and a **Card 3x** (3.0+), each 3-4 picks from different fixtures, no fixture twice in a day.
- Every pick: bookmaker-priced 1.15-1.90, the bookmakers 60%+, the model no more than 5 points above them, clean, any sport still on the Daily List. Chance quoted is the bookmakers'.
- **Locking:** Overnight groups lock at 21:00 UK the evening before, Daytime and Evening at 07:00 on the day. Before the lock a group can be rebuilt as prices settle; after it, it never changes. A window empty at its lock may get a late group from games not yet started, marked Late.
- **Record:** only locked groups are archived (`archive_locked`) and graded, by window (`card`, `cardByWindow`); closing prices are tracked for yesterday, today and tomorrow.
- **Today's bets** page: the five-rule playbook at the top (place once, leave it, only the card, best price, review weekly), each window with its lock time and its 2x and 3x groups, then Leave these out, Check a slip, the scoreboard by window, and the reasons from the weekend in a fold.
**Evidence:** the weekend's slips and the archive work in `claude/todays-bets-2026-10-25.md` and `claude/multipliers-2026-10-24.md`. On 25 Oct's prices the card would have had Daytime 2.05 (39%) and 3.01 (27%), Evening 2.08 (38%) and 3.03 (27%).
**Files:** groupings.py, index.html, tests/test_groupings_card.py, CLAUDE.md, claude/the-card-2026-10-25.md, RELEASES.md.
**Not changed:** every model, the Daily List, the avoid list and slip checker, older kinds' code and record (no longer built).
**Roll back:** `git revert` the commit; build_day and the older kinds return.

## Today's bets: a front page built on the weekend's lessons, 25 Oct (tag pending)

**What changed:** Douglas, after a losing weekend: "a rebuild that takes in all the learnings and surfaces what serves our purpose of making money". New front page, **Today's bets** (the Daily List and Odds tabs stay one tap away):
- **Built to land** (strict Double / Treble) and **Multipliers**, placeable groups only, each pick with its full board row and best price.
- **Leave these out**: the day's priced picks where the model sits 8+ points above the bookmakers (Avoid under 70%, Caution at 70%+, where the archive is thin), and strong picks from sports off the Daily List.
- **Check a slip**: paste picks, one a line; each is matched to the almanac and marked Back, Caution, Avoid or No read, with the chance they all land.
- **Is it working?**: beat-the-closing-price, the strict and Multiplier records, and a plain "model v bookmakers: not yet".
- The six rules from the weekend and the archive, in a fold at the top.
Rules changed in `groupings.py`: no more forced groups (`MIN_GROUPS` 3 -> 0, Douglas: "only show what qualifies"); Multipliers exclude sports off the Daily List (`listOff`: college football, tennis).
**Evidence:** the weekend's slips (losing picks Oita Trinita, model 63% v bookmakers 50%; North Carolina, college football; Folgore, Ordino, Wolves all flagged); 909 archived priced picks: under 70%, model 8+ points above the market, 31 picks quoted 61% landed 35%; 70%+ with that gap, 5 picks (all won), hence Caution.
**Files:** groupings.py, index.html, tests/test_groupings_multiplier.py, tests/test_groupings_minimum.py, CLAUDE.md, claude/todays-bets-2026-10-25.md, RELEASES.md.
**Not changed:** every model, the Daily List rule, the strict and Multiplier leg rules (other than `listOff`). No stake advice, by Douglas's choice.
**Roll back:** `git revert` the commit; the front page returns to the Daily List.

## Detail tables scroll sideways on phones, 25 Oct (tag pending)

**What changed:** opening a row on a phone could push the season tables (GD, Pts, PPG) and the form chips past the screen edge (Douglas's screenshot, Oita Trinita v Ventforet Kofu). Every detail table (season sheets, the bookmakers grid, form lists, the Starred slip) now sits in a box that scrolls sideways, grid columns no longer grow to their content, and the attack / defence / form line wraps. Checked at 360px, 390px and 1280px on the Daily List, Football, Rugby, College football, Tennis and Odds tabs: page width equals the screen on all, no console errors.
**Files:** index.html, RELEASES.md.
**Not changed:** content, data, every model.
**Roll back:** `git revert` the commit.

## Best prices, closing-line check, profit record, 25 Oct (tag pending)

**What changed:** Douglas: "I need the model to beat the bookies' odds". Three measures, no rule or model change:
- **Best price on every pick.** Each Odds tab leg shows the best price on offer and the bookmaker offering it ("best 1.52 Bet365"), and each group its combined price at best prices. On the archive (909 priced picks), taking the best price instead of the average was worth about 3p in the pound on every pick (-6.8p to -3.8p overall; the Multiplier-type legs +6.8p to +9.8p).
- **Closing-line check.** Every build writes each archived leg's latest price before kick-off (`lastOdds`, `lastBest`) into `groupings-archive/`; what was published is never changed. The record counts how many picks' prices shortened after we published them ("Beat the closing price"). A model with a real edge sees its picks shorten; this shows within weeks, profit within months.
- **Profit record.** Groups are graded at average and at best prices (`paidBest`, `returnedBest`).
**Files:** groupings.py, odds.py (records the best price's bookmaker, `maxBook`), index.html, tests/test_groupings_closing.py, CLAUDE.md, RELEASES.md.
**Not changed:** every group rule, every model, the Daily List.
**Roll back:** `git revert` the commit.

## Multipliers across all sports, 24 Oct (tag pending)

**What changed:** Douglas: "Multipliers should be across all sports". Picks from every published sport (football, rugby, tennis, NFL, college football, baseball, basketball, WNBA, and any other on the site) now enter the Multiplier pool on the same rule: priced 1.30-1.90, the bookmakers 60%+, the model 40%+ and no more than 5 points above them. Tennis rows show under their picks like the others.
**Evidence:** the quoted chance is the bookmakers' own, so it is honest for any sport; the archive evidence (legs at these prices landing above fair) is football only, said on the page note.
**Safety:** picks from sports outside `GROUP_SPORTS` are `multOnly`: `safe_leg` and `wide_leg` refuse them, so the Doubles, Trebles and Wider groups are unchanged. The Odds API (tennis, rugby; 15 credits a day) spends on keys the safer groups need first; Multiplier-only legs use what is left.
**Files:** groupings.py, index.html, tests/test_groupings_multiplier.py, tests/test_groupings_banker.py, CLAUDE.md, RELEASES.md.
**Roll back:** `git revert` the commit.

## Odds tab: every pick carries its full board row, 24 Oct (tag pending)

**What changed:** Douglas: "the fixture rows from the daily lists, and all content and links, in the groups". Under each pick in every group (Doubles, Trebles, Wider, Multipliers) is the same row the Daily List draws: kick-off, form, probability bar, predicted score, tier, tested rate, bookmark star; tap it for the full detail (season tables, the why, head to head, predictions, search and table links). A pick that has started shows its pinned row from the day list where one exists. Group cards are now full width so the rows fit.
**Files:** index.html, RELEASES.md.
**Not changed:** groupings.py, every rule and model.
**Roll back:** `git revert` the commit.

## Multipliers rule 2: three a day, 3-4 likely picks each, 24 Oct (tag pending)

**What changed:** Douglas: "at least 2-3 groups per day, at least 3 teams in each group ... all picks must be likely to come in". The 3x / 5x Multipliers are replaced by up to three Multipliers a day (first, second, third choice), each three or four picks the bookmakers rate 60%+ (was 45%+), paying 2.8x or more together, no pick shared. Chosen for the highest combined chance, so they come out as three picks at about 1.35-1.55. About 28-30% each to land.
**Evidence:** on the archive, clean legs priced 1.30-1.90 at 60%+ fair with the model no more than 5 points above the market landed 76.1% (n=67, fair 64.8%; `tools/market_check.py` section 4 at the higher floor). On 24 Oct's board this gives three groups at 2.82-2.86 (Huddersfield, Nashville, Lazio; Häcken, Arsenal, Porto; Brighton, Madryn, Philadelphia), on 25 Oct three at 2.80-2.82.
**Files:** groupings.py, index.html, tests/test_groupings_multiplier.py, claude/multipliers-2026-10-24.md, CLAUDE.md, RELEASES.md.
**Not changed:** the groups built to land, every model, the Daily List. Rule 1 groups published earlier today are rebuilt under rule 2 on the next build.
**Roll back:** `git revert` the commit.

## Odds tab order: Multipliers above underway groups, 24 Oct (tag pending)

**What changed:** on the Odds tab, groups that can still be placed come first, then the Multipliers, then groups already underway under their own heading. A "Multipliers ↓" button beside the day picker jumps to them. On Saturday evening every group was underway, which pushed the Multipliers a long scroll down on a phone.
**Files:** index.html, RELEASES.md.
**Not changed:** groupings.py, every rule and model.
**Roll back:** `git revert` the commit.

## Multipliers, cup confidence fix, market check, 24 Oct (tag pending)

**What changed:** the Odds tab has a new **Multipliers** section under the groups built to land: for a target return of 3x or 5x, the 2-4 football picks with the highest combined chance whose combined price reaches it. Each pick is priced 1.30-1.90, the bookmakers give it 45%+, and the model sits no more than 5 points above them; its chance is the bookmakers' fair chance (price less margin), shown as such. Built after the other groups from the picks they leave, re-checked on every build, archived and graded on their own line ("Multipliers won"). They do not count toward the three groups a day. Separately, domestic cup ties no longer show their untempered confidence: `engine.cup_temper` now resets `confidence` to the tempered maximum (Berkhamsted v Cray showed 80% beside a 61% win chance; 200 rows on 24 Oct), so cup rows rank, tier and band on the number they display.
**Evidence:** `tools/market_check.py` (new, advisory) on 909 archived football picks with a pre-kick-off price, 11 Sep-24 Oct: the market beats the model on log loss (0.979 v 1.013; 50/50 blend better than the model, +0.023, 90% +0.017 to +0.029); picks landed at the market's rate, not the model's (model 5-10 points above: 47% landed; 10+: 42%); Multiplier-eligible legs (n=181) landed 66.9% against 58.2% fair (+8.6 pts, 90% +2.7 to +14.0), profit per unit +6.0% (90% -3.6% to +14.8%, no proven edge). Draw share at a fixed win chance did not change landing (50-70% picks: landed 62/62/52% against quoted 67/59/54%), so no draw filter. Agrees with `claude/odds-edge-test-2026-10-23.md` (no edge over the price on 12,510 replay legs).
**Files:** groupings.py, index.html, engine.py, tools/market_check.py, tests/test_groupings_multiplier.py, tests/test_groupings.py, tests/test_cup_calibration.py, claude/multipliers-2026-10-24.md, claude/odds-groupings.md, CLAUDE.md, RELEASES.md.
**Not changed:** the Daily List, every model probability and constant, Double / Treble / Wider rules (the leg pool now admits mid-priced football picks marked `multOnly`; the strict and Wider gates already required their own tested rate, so they pick from the same legs as before, and `multOnly` legs never cost a per-fixture price call). No bookmaker input into any model: the market is used only for the Multipliers' quoted chance and as a veto, as prices already were.
**Roll back:** `git revert` the commit. Archived Multiplier groups stay in `groupings-archive/` and the record tallies them by name.

## Office review and next week's priorities, 23 Oct (tag pending)

**What changed:** nothing a reader sees. A dated review of the fortnight 12-23 Oct and three priorities for next week (Jade, Susie, Andrew).
**Evidence:** read from `record.json` (football 5,931 graded, 67.8%; Daily List 84 of 103), `sports-record.json`, `tennis-record.json` (61.6% v 62.7% quoted) and `groupings-record.json` (11 of 59 won, 19.0 expected, mostly retired kinds).
**Files:** claude/office-review-2026-10-23.md, RELEASES.md.
**Not changed:** code, every model constant, the record files.
**Roll back:** `git revert` the commit.

## Grading audit: extra-time ties in openfootball results (tag pending)

**What changed:** nothing a reader sees. The openfootball parser now reads the 90-minute score of a tie decided in extra time or on penalties, as the board prices 90 minutes.
**Evidence:** 88 graded games re-checked on ESPN (30 football, 25 tennis, 33 other sports): 0 mismatches. Parser bug: "Birkirkara FC  0-1 a.e.t. (0-0)" stayed in the away name (game read unplayed, junk team); "3-2 a.e.t. (2-2, 1-1)" graded 3-2. None of the 4 cached games is in the graded record.
**Files:** sources.py, tests/test_grading.py, claude/results-review-board.md, RELEASES.md.
**Not changed:** ESPN and API-Football handling, tennis and sports grading, every model constant.
**Roll back:** `git revert` the commit.

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
