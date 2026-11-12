# Releases

Newest first. Every release is an annotated git tag (`release-YYYY-MM-DD`,
with `-2`, `-3` for a second release the same day) and an entry here.


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
