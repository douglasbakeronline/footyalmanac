# Sports Almanac (repo: footyalmanac)

A daily-refreshed sports prediction site: football (a Dixon-Coles adjusted
Poisson model, home / draw / away), tennis (surface Elo), and NFL, baseball,
basketball and rugby (Elo per sport). It rates every team or player it has free
data for, prices each upcoming game, ranks the slate so the most predictable
games sit at the top, and grades itself publicly against what actually
happened. It began as football-only, which is why many notes and names say
"football" or "footy".

- Live: https://douglasbakeronline.github.io/footyalmanac/
- Repo: https://github.com/douglasbakeronline/footyalmanac (public)
- Owner: Douglas. At least one other collaborator has push access.

The point of the site is honest confidence: surface the genuinely predictable
games, say plainly when a call is weak, and never inflate a number to look good.

The front page is the **Daily List**; **Bets**, the second tab (`renderToday` in `index.html`, the `today` view: Today's bets and the Odds tab merged on 25 Oct 2026, Douglas's decision), holds **the Card** (`groupings.build_card`: one window a day, 07:00 UK to 07:00 the next morning (`CARD_WINDOWS`; the three windows to 28 Oct 2026 stay in the record), no clock lock: a group is open until its first kick-off (`first_kick`), re-checked on every build and holding unless a pick fails the rule or the combined price moves more than `CARD_DRIFT` (10%) outside its band (30 Oct 2026), then frozen as published and archived (Douglas, 29 Oct 2026), up to `CARD_MAX_GROUPS` (6) groups a day, a Card 2x and a Card 3x then a second of each (`seq`), each of 3-5 bookmaker-priced 60%+ picks from different fixtures (five since 6 Nov 2026), staked `CARD_STAKE` (two units on a 2x, one on a 3x), the record tallied per `CARD_RULE` version (`cardByRule`), each pick with its price at every UK book (`bookOdds`) and the card written for William Hill (`CARD_BOOK`, a preference not a filter), each group with up to three substitutes (`bench_for`), NFL, college football and college basketball (no live record, 31 Oct 2026) never, tennis only at 75%+ on model and tested rate, football from the core leagues only (`CARD_CORE_ONLY` True; set False to admit wider leagues through `card_league`, tried and reversed on 29 Oct 2026 after the two-rule replay; `CARD_CORE_NUDGE` then puts core picks first) and with the model 5 to 10 points under the bookmakers' chance (`CARD_SPORTS_OFF`, `CARD_SPORT_MIN`, `CARD_UNDER_MARKET`, 29 Oct 2026; `CARD_UNDER_MAX` 31 Oct 2026, 10+ under lost on every sample, `CARD_RULE` 5) and the opposition priced 9+ (`CARD_OPP_MIN`, `CARD_RULE` 6, 6 Nov 2026: Douglas's observation, replayed in `claude/opposition-price-2026-11-06.md`; every leg of every sport carries `opp` and `draw`, shown on the page, football only for the rule), the record carrying `z` against expected and the scoreboard a floor line (`CARD_FLOOR_Z` -2 on 50+ groups retires the rule), never changed after its first kick-off; a day the full rule leaves empty gets a marked wider-rule group, 3-5 picks at 1.08-2.10 and 55%+, graded apart as `cardWide`; tennis matches ESPN dates at midnight New York take their tournament's usual first start, `tennis_starts`), **The plan** at the top (`signalsPanel` / `planRungs` in `index.html`, 10 Nov 2026, Douglas: "one clear direction that uses the best case from each"; was Place now: three rungs in order of proof, Edge singles (Tested, one unit), the Edge double of a day's two most likely Edge picks (Tested, one unit, built in `sigList`), the Card (On trial, its own stakes), four habits, then today's open bets tested first, Hill price, stake, copy slip; the wider-rule filler, the Model card and the week ahead's model trebles named as not in the plan; display only, `claude/the-plan-2026-11-10.md`), Coming up (one line, later days with a plan bet), the **Model card** on paper (`build_model_card`, `MODEL_KINDS`, 31 Oct 2026: a Model 2x and 3x a day of the model's own picks, each rated 60%+ and at or above the bookmakers' chance with the group's chance the model's own, never staked or pushed, graded as `cardModel`; the Card chosen the other way round, compared at the 30 Nov review), the playbook, the picks to leave out (`groupings.avoid_list`), a slip checker, the re-check log, the accumulator calculator, the scoreboard by window and the day-by-day group history (`ogRecord(true)`). There is no Odds tab, and no Baseball or WNBA tab (too few games; their picks still reach the Daily List). See `claude/the-card-2026-10-25.md` and `claude/todays-bets-2026-10-25.md`. The Double / Treble / Wider / Multiplier kinds are no longer built; their record stays. The **Daily List** is the most likely results across every
sport, one ranking per day, confidence first and tested rate second
(28 Oct 2026; was tested rate first, see
`claude/daily-list-order-review-2026-10-28.md`), with Group A (the strongest five at
85%+, `GROUP_A_MIN`, never padded) and Group B (the next five) labels in that
order. One rule for
all sports: a pick qualifies only if calls at its level landed ≥80% in
testing on games never tuned on (`sports.list_threshold`), plus football's
blind-spot exclusions and no draws, no tennis qualifying rounds, and a
ranked international must clear its bar before the FIFA ranking too. Raised
from 75% on 29 Sep 2026 at Douglas's request (`claude/ranking-review.md`). Every
row shows its tested rate (tennis: the live own-band rate once a band has 30 graded picks, else no chip, 26 Oct 2026). See `claude/multi-sport.md`. It is the
model's own independent read, with no bookmaker input, by Douglas's decision.
The full board sits one tap behind it.

## Working as an AI agent

This repo is worked on by Claude Code in several places. The rules below apply
in all of them; `AGENTS.md` has the same guardrails for any other agent.

| Where | How work lands |
|---|---|
| Local session with Douglas (terminal / VS Code) | Straight to `main` via the release process below. Douglas has given standing authorisation to push. |
| claude.ai/code (cloud) | A branch and a pull request, with the would-be `RELEASES.md` entry (mark the tag "pending"). A push to `main` deploys the live site, so merging stays with Douglas unless he says otherwise in that session. Tested 28 Sep 2026: the cloud session can push branches and commits but **not tags** (GitHub drops the connection), and **cannot reach ESPN**, so its builds are partial. A local session adds the tag after merge. |
| GitHub agent (`@claude` on an issue or PR, `.github/workflows/claude.yml`) | Same as cloud: branch and pull request, never a direct push to `main`. Only the owner and collaborators can trigger it (public repo). Needs the `ANTHROPIC_API_KEY` secret. |

- **Protect what exists.** Before replacing anything, find out why it is the
  way it is: the comment above it, the matching `claude/` note, `RELEASES.md`
  and `git log -p`. Most odd-looking choices here were deliberate and tested.
  Extend rather than rewrite; remove only with a stated reason.
- **Owner's standing decisions** (do not reverse without asking): the Daily
  List is the front page and Bets the second tab (25 Oct 2026); no bookmaker input into any model; no manual data
  entry; the cover header (star banner, grey cover, stacked SPORTS / ALMANAC,
  year band, red stat panel) stays; no dark border thicker than 1px; every
  release is tagged and logged.
- **Cloud and CI environments** run Python 3.12. Network access to ESPN,
  openfootball, football-data.co.uk or FIFA may be blocked in a cloud sandbox:
  if a build cannot fetch, say so and let CI be the check. Never commit the
  output of a build that could not fetch its data.
- **Visual changes** must be checked in a browser at desktop and phone
  (~400px) width before shipping.

## Read before non-trivial work

`claude/` holds dated handover notes. Read the one that matches the task.

| File | Covers |
|---|---|
| `claude/full-review-2026-10-25.md` | Full review of 25 Oct 2026: live record by tier and sport, 22 bugs with fixes, the betting record, costs, and a dated timeline. Read first when deciding what to work on next. |
| `claude/home-away-tilt-2026-10-26.md` | The away under-quote on the live record, the `ha_scale` sweep through the gates (failed on gain and p(worse)), why AF_EXTRA cannot be gated on the replay, what would settle it. Read before touching home advantage or `HOME_MULT`. |
| `claude/daily-list-order-review-2026-10-28.md` | Why the list is ordered by confidence (the tested-rate order was not monotone and sank started football picks), the two-groups-of-five evidence, why tennis is back on and college football stays off, the rule for taking a sport off. Read before touching the list order or `LIST_ON` / `LIST_OFF`. |
| `claude/daily-list.md` | The Daily List rule and its evidence, what does and doesn't predict a pick landing (`predictability.py`), the ESPN slug audit, the US Eastern/UTC day bug. Read before touching the list, `LIST_MIN`, or ESPN fetching. |
| `claude/world-rankings.md` | Which world rankings are in the model, the tests behind them, sources and name mapping. Read before touching `rankings.py`. |
| `claude/ranking-review.md` | Burundi v Algeria: the FIFA adjustment re-checked on 2022-24, why ranked internationals need 65%, the goals line fix, the open question on big lifts. |
| `claude/multi-sport.md` | NFL, baseball, basketball, rugby: the model, its evidence, which sports earn a Daily List place and why. Read before touching `sports.py` or `sports.json`. |
| `claude/tennis-record.md` | How tennis picks are archived and graded, the publish-before-start rule, the seed from git history. Read before touching `build_tennis.py` or `score_tennis.py`. |
| `claude/tennis-ratings-gap-2026-10-08.md` | Why tennis ratings missed every result from June to October, `history-tennis/`, the archive boundary, the evidence, hot-form signals tested and rejected. Read before touching how `build_tennis.py` updates ratings. |
| `claude/evaluation-audit.md` | The 2 Oct 2026 audit: prior/test overlaps, the tune/backtest calculation mismatch, same-day leakage, the archive's publish-time gap, what was fixed, before/after numbers, open questions. Read before touching `replay.py`, `tune.py`, `backtest.py` or the prediction archive. |
| `claude/data-integrity.md` | The two-source name-matching failures, the season-so-far cache, `nametest.py`, matching rules. Read before touching `sources.py` or anything that looks up a club. |
| `claude/tuning-evidence.md` | What every constant is worth, the calibration curve, what was tested and rejected, the tuning rules. Read before touching `engine.py` constants, `tune.py` or `calibration.json`. |
| `claude/coverage-expansion.md` | Why 61 competitions come from ESPN, `backfill.py`, which leagues still lack a prior season. |
| `claude/midband-calibration-2026-10-21.md` | Whether 60-80% calls land above quote: on quote overall, but core-league 65-75% calls landed ~87% this season. Why `ok` is the wrong test for win bets. The replay test that should come next. |
| `claude/results-review-board.md` | The "How it went" board, tier ladder, live calibration. |
| `claude/data-expansion-plan.md` | API-Football Pro (bought 30 Sep 2026), where the key lives, the order of work: coverage, lower leagues, replay test, U21, UFC, boxing. Read before any paid-data or new-sport work. |
| `claude/brand-identity.md` | Mark, type, colour tokens with contrast ratios, sticky bar, assets. |
| `claude/betting-groups-review-2026-10-29.md` | The betting record to 29 Oct: 90 groups, legs by sport (football on quote, tennis / cfb / NFL under), the Daily List top N against the legs, time windows checked and cleared. Why NFL legs are off the Card and tennis legs need 75%. Read before touching `card_fault`. |
| `claude/the-card-2026-10-25.md` | The Card and the playbook: windows, 2x / 3x kinds, leg rule, lock times, archive of locked groups only, prices for every sport and what would close the gap. Read before touching `build_card` or the front page. |
| `claude/todays-bets-2026-10-25.md` | The Today's bets front page, the weekend's losing slips and the six rules taken from them, the avoid list and slip checker, no forced groups. Read before touching the front page or `MIN_GROUPS`. |
| `claude/model-ideas-2026-10-25.md` | Home advantage per league, table position, recent goals, goal difference and last-3 points tested on the replay; the weekly gated home-advantage refit. Read before touching form or home advantage. |
| `claude/card-seasons-2026-11-09.md` | The Card's leg rule over 2022-23 to 2026-27 on football-data prices: the under-market cut by season, the gap bands (the rule 5 cap not supported), the opposition's price (rule 6 holds in all five), the whole Card under rules 5 and 6, the 2x v the 3x. Read before any Card rule change or the 30 Nov review. |
| `claude/card-pool-replay-2026-11-09.md` | What the pool archive held and could not hold (38% of legs first written as estimates, no bookmakers' chance kept), the `priced` block, the pool-based `card_replay.py`, the approximate `--recover` read. Read before touching `archive_pool`, `POOL_KEYS` or the Card replay. |
| `claude/card-pool-coverage-2026-11-09.md` | The live Card's legs against the pool: 42 of 59 to 8 Nov held only as estimates, so the pool replay rebuilt no live Card; the nightly coverage check; the `notennis` and `tennis80` variants. Read before reading any pool-based Card replay. |
| `claude/card-legs-by-sport-2026-11-09.md` | The Card's legs by sport in the record (`cardLegsBySport`), the sport-off tripwire measured rather than counted by hand, the read at 9 Nov. Read before acting on the tennis tripwire or touching `CARD_SPORTS_OFF`. |
| `claude/card-staking-2026-11-09.md` | `tools/staking.py`'s bankroll corrected (it was inverted), the month and season bankroll at the page's stakes, the live 2x / 3x split against the replay's, `flatstake` pre-registered. Read before touching `CARD_STAKE` or the staking section of the review. |
| `claude/price-lead-time-2026-11-09.md` | The Card's price move by the first price's lead on the start, last prices stamped after the start (`whenLast`, `lastAfterStart`). Read before touching the push time in `notify.py` or `CARD_BOOK`. |
| `claude/price-timing-read-2026-11-10.md` | The price-timing read made to earn its place (50+ legs, day-resampled p <= 0.10), the singles return at the first v the last pre-start price (+1.95 points late on 104 settled legs, p 0.011, mostly football), unstarted legs left out. Read before moving a push time or telling anyone when to place. |
| `claude/card-funnel-2026-11-10.md` | Which Card condition costs the groups (`tools/card_funnel.py`): no football leg cleared rule 6 from 6 to 12 Nov, the 3x returns only by relaxing the tennis floor or the opposition rule, two legs per competition caps NBA groups. Read before any Card change made for volume. |
| `claude/card-fillers-2026-11-10.md` | The empty-day fillers on the replay: the page's wider-rule fallback (`fillwide`) 2 of 12 won v 4.1 expected on the pool, `fillrule5` the one alternative that builds, the pre-registered drop-the-filler decision, the filler's own legs as the gate. Read before touching the wider-rule block of `build_card`. |
| `claude/list-accas-2026-11-10.md` | Daily List picks as accumulators (`tools/list_accas.py`): the picks land as quoted singly and combined, the loss is the price (average 1.12, margin 5.3%, about -5% a leg compounding), what the data supports instead. Read before any change made for people betting the Daily List. |
| `claude/list-at-hill-2026-11-10.md` | The Daily List at William Hill: the UK-books pass for list picks (`price_odds_api(list_books=True)`, `LIST_BOOK_*`), the chips and the "At William Hill" filter, the `listAtBook` record line, what it cannot tell apart yet. Read before touching list pricing or The Odds API ledger. |
| `claude/edge-flag-2026-11-10.md` | The green Edge flag on football fixtures (`groupings.edge_flag`, `EDGE_RULE`): the rule, the evidence (511 legs over five seasons, the site's own archive), why football-data leagues only, the page. Read before touching the flag or the Card constants it reuses. |
| `claude/edge-sports-2026-11-10.md` | The Edge flag tested on every sport (`tools/edge_sports.py`): only the pool has non-football prices, no sport passes the gate yet, the short favourite (1.15-1.30) tracked out of sample from 11 Nov in the nightly review. Read before giving any other sport the flag. |
| `claude/card-modelcard-2026-11-10.md` | The Model card's rule replayed beside the Card (`modelcard`, `cardModel`): on the pool 7 of 12 groups v the Card's 4 of 10, under the gate, but -8.2% over 2025-26 on football-data (70 groups); the pre-registered switch for the 30 Nov review. Read before comparing the Card and the Model card. |
| `claude/the-plan-2026-11-10.md` | The plan on the Bets tab: the three methods (Edge, the Card, the week ahead's model trebles) by their evidence, what was taken from each, the Edge double, what is not in the plan and why. Read before changing what the Bets tab tells people to bet. |
| `claude/edge-accas-2026-11-10.md` | Edge picks as accumulators over five football-data seasons (`edge_accas`): singles +5.4% and every Edge pick of the day +9.7% at the best price pooled, ahead in four seasons of five; longer slips swing -46% to +99%; the Bets tab's Edge picks section. Read before changing how the Edge flag is offered for betting. |
| `claude/opposition-price-2026-11-06.md` | The opposition's price as a Card condition: the replay by opposition price band, why football only, the variants for the 30 Nov review. Read before touching `CARD_OPP_MIN` or the price fields on a leg. |
| `claude/multipliers-2026-10-24.md` | The Multipliers, the market beating the model on the archive (0.979 v 1.013 log loss), why there is no draw filter, the cup confidence fix. Read before touching the Multipliers or proposing market input to the Daily List. |

**The code on `main` is the source of truth.** The notes are snapshots from
September 2026 and some have been overtaken (see "Known drift" below). Where a
note and the code disagree, trust the code and tell Douglas the note is stale.

## Files

Pipeline, all Python 3.12, **standard library only, no pip, no requirements.txt**:

- `engine.py` ratings and match model. Every number on a row comes from here.
  `current_season(code, today)` derives every season string from the date
  (`tests/test_seasons.py` fails CI on a rollover miss); `uk_today()` is the
  build's anchor day; `apply_af_seasons` reads `current/af-seasons.json`.
- `sources.py` openfootball + ESPN + football-data.co.uk (`FDX`) + API-Football (`AF`, paid, key `API_FOOTBALL_KEY` in secrets and the cloud env) fetchers, `match_team`, `LIVE_NAMES`, `ESPN_SLUGS`, `topup_current`.
- `build.py` fetch, rate, price, write `data.js` / `data.json` / `dashboard.html`, archive `predictions/<date>.json`. Since 26 Oct 2026 the page inlines fixtures plus `__RECORD_SUMMARY__` only; the full football record is `record-data.js`, loaded with `sports-record.js` and `tennis-record.js` when "How it went" opens (`loadRecords` in `index.html`).
- `score.py` grades every archived prediction, writes `record.json`. Has its own copy of the tier ladder. Each row is `verified`, `verified-by-date` or `legacy-unverified` (graded), or `late` / `timing-unverifiable` (not graded, counted apart); see `claude/evaluation-audit.md`.
- `backtest.py` walk-forward backtest.
- `tune.py` constant sweep and calibration refit, behind gates, both measured against the live configuration (`live_baseline()`). `--snapshot FILE` runs either on a frozen snapshot and writes nothing.
- `replay.py` the one walk-forward replay for football, shared by `backtest.py` and `tune.py`, built from the live build's engine functions and batched by date; `validate_split` refuses overlapping or missing seasons. `python3 replay.py --audit` lists what is usable and what is excluded.
- `tools/capture_predictions.py`, `tools/compare_predictions.py`: reproducible before/after comparison of tune.py and backtest.py across two checkouts on one frozen snapshot (`replay.py --freeze`; `--filter-snapshot` derives an openfootball-only, public-domain copy). Outputs go in `audit-out/` (gitignored).
- `tools/cup_calibration.py` fits the domestic cup calibration from `current/af-cup-replay.json` "rows" (cup replay version 4+); advisory, a human commits the constant.
- `tools/af_team_news.py` fetches API-Football injuries and player minutes (needs the secret: run from a workflow); `tools/team_news_eval.py` backtests them. Output stays in `audit-out/` (API-Football data is not for redistribution).
- `tools/julius_export.py` writes `julius/julius.ai.review.<date>/` (and a `.zip`): every graded prediction as CSVs, Daily List, reserve and each sport separately, with ✓ / ✗ marks, a summary, per-day tallies and calibration bands, for outside review (Julius AI). Reads `record-graded.json`, `tennis-record.json` and `sports.graded_games()`; nothing is regraded. Run it after the daily build: a local `score.py` lacks the paid results and grades about half the football.
- `claude/proposals/` follow-up proposals awaiting a decision (history regeneration, League One prior, cache expansion).
- `tests/` regression tests (stdlib `unittest`): `python3 -m unittest discover -s tests -v`. Run before any push that touches the model, replay, archive or grading.
- `tools/midband_calibration.py` landed v quoted by band and segment on the graded record, strict win test. Advisory.
- `tools/card_replay.py` the Card rebuilt under several leg rules (29 Oct 2026; variants pre-registered for the 30 Nov review, `notennis` and `tennis80` added 9 Nov 2026, `comp3` (three legs from one competition, `groupings.COMP_MAX` 2 live) 10 Nov 2026; the empty-day fillers `fillwide` (the page's own fallback), `fillopp7`, `fillrule5`, `fillshort`, 10 Nov 2026, gated on the filler's own legs, `claude/card-fillers-2026-11-10.md`); `modelcard`, the Model card's rule on the same legs, 10 Nov 2026, `claude/card-modelcard-2026-11-10.md`: on the archived pool from 30 Oct 2026 (`POOL_FROM`, every sport, first real price, `--closing` for the last; `--recover` admits legs archived before `priced` existed at their last price, approximate) and on the football-data-priced archive rows before. Advisory. See `claude/card-pool-replay-2026-11-09.md`.
- `tools/card_integrity.py`, `tools/price_timing.py`, `tools/staking.py`, `tools/card_review_post.py`: the nightly **Card review** (`card-review.yml`, 03:40 UTC, 9 Nov 2026): integrity checks on the Card's record (an `office-backlog` issue for the engineer when they fail; `card-leg-unreplayable` since 9 Nov 2026: every Card leg from 10 Nov must be in the pool at a real price, as only 17 of 59 were from 30 Oct to 8 Nov, `claude/card-pool-coverage-2026-11-09.md`), every replay variant, first v last price (by sport and by the first price's lead on the start; a leg whose last price came after its start is left out, `lastAfterStart`, `claude/price-lead-time-2026-11-09.md`; since 10 Nov 2026 a read only on 50+ legs at day-resampled p <= 0.10, the singles return at first v last price on settled legs, unstarted legs left out, `claude/price-timing-read-2026-11-10.md`) and each UK book, stake size and drawdown. One `card-review` issue a night. Advisory; Douglas's objective is consistent returns on the group accumulators, and HQ's planner now ranks the Card's gaps first.
- `tools/card_funnel.py` which Card condition keeps groups off the page (10 Nov 2026, #155): each pool leg's first failing condition by sport (the live `card_fault`), legs kept off by one condition alone, and the days a first 2x / 3x builds live and with one condition relaxed; no results needed, `--recover` for legs before 10 Nov. Printed in the nightly Card review (`card_review_post.funnel_section`). Volume only, advisory. See `claude/card-funnel-2026-11-10.md`.
- `tools/list_accas.py` Daily List picks combined into accumulators (10 Nov 2026): the top N of each day on the graded record, landed v quoted, and on the priced pool at the average price beside the bookmakers' own expectation. Advisory. See `claude/list-accas-2026-11-10.md`.
- `tools/card_legs_history.py` the Card's leg rule and the whole Card replayed over past seasons on football-data.co.uk prices; run by `tune.yml` (fit and check seasons), writes `card-legs-history.json`; `--seasons 2022-23,2023-24,2024-25` adds past seasons, each with the season before as its prior, with the gap and opposition-price tables and losing months (9 Nov 2026, #153). Advisory (29 Oct 2026). `card-legs-history.yml` (run on any pull request touching the tool, or by hand with a `seasons` input) landed on `main` in #158 and ran the fillers on #184. From 6 to 9 Nov the tool crashed on `KeyError: 'opp'` (#144 shipped half a change), so the Monday report was stale.
- `tools/goals_value.py` value backtest on the goals market (over/under 2.5 v football-data.co.uk prices, fit and check seasons, log loss, calibration by band, value picks' hit, ROI and closing-line value); run by `tune.yml`, writes `goals-value.json`. Advisory (29 Oct 2026).
- `tools/market_check.py` model against market on the archive (log loss, landing by the model's lead over the market, draw share, the Multiplier price range). Advisory.
- **Days at a glance** (10 Nov 2026, Douglas): How it went's Daily List board opens with every list day as one line of the clock, each pick a dot at its start coloured by result (`daysGlance` in `index.html`; starts from `score.py` day rows' `kickoff`, `score_tennis.py` day rows' `start` from `history-tennis/`, sports' `when`). Display only.
- `trustmap.py` where to trust the model (10 Nov 2026): every graded pick at 55%+, every sport, by family and confidence band, landed v quoted with z; `build.py` adds it to `record-data.js` as `trust`, shown in How it went (`trustMap` in `index.html`). A tally, never a fit. See `claude/trust-map-2026-11-10.md`.
- `predictability.py` tests signals beyond the model's confidence (did the pick land?). Advisory only, changes nothing.
- `eurotest.py` cross-competition harness for league strength, writes `europe.json`.
- `nametest.py` guards the club-name matcher. Runs before every deploy.
- `notify.py` one ntfy push per Card group a build creates (new or replacement, `first` stamp this build), run by `deploy.yml` after `groupings.py`; needs the `NTFY_TOPIC` secret, silent without it (29 Oct 2026). Since 10 Nov 2026 also four **briefings** a UK day at Douglas's betting times (`SLOTS`: morning 07:00, lunch 11:00, evening 16:00, night 21:00 UK, sent by the first build at or after each, i.e. the 07:40, 12:00, 17:00 and 22:15 builds; `due_slot` sends only the latest due slot): picks still to start, the strongest of them, the model treble, Edge picks and open Card groups with Hill prices, and from lunch the day's tally; the night push adds the overnight slate to 08:00. Slots sent are kept in `groupings-archive/briefed.json` (committed with the archive) so none sends twice.
- `backfill.py` walks a past season from ESPN into `history/`.
- Paid prices (9 Nov 2026): The Odds API prices a tennis match only at the Card's bar (`CARD_SPORT_MIN`) or on the Daily List; API-Sports skips `AS_SKIP` (college football and basketball; ESPN prices them free). Since 9 Nov 2026 (Douglas: "make sure all odds are being displayed across all cards") a leg priced by one non-UK source (ESPN's DraftKings line for the NBA, Pinnacle for tennis) that could reach a card (`groupings.books_wanted`) also takes every UK book's price (`bookOdds`) from API-Sports or The Odds API (`books_only`), display only: its average and fair chance are unchanged. Every Card and Model card group has a "Prices by bookmaker" fold (`ogBooks` in `index.html`) and Model card picks show the William Hill price.
- The Daily List at William Hill (10 Nov 2026, Douglas: "a lot of those games ... are not on William Hill"): every list pick without UK books is sent to The Odds API's UK region last in `groupings.price`, US sports included (`LIST_BOOK_KEYS`, one credit a slate, only under `LIST_BOOK_DAY` 9 credits a day). Display only: chips on each list row (Hill price / Not at Hill / No UK price), an "At William Hill" filter, and `groupings-record.json` `listAtBook` (settled list picks priced at Hill, landed and return at Hill's price, from 10 Nov) shown in "How it went" and the nightly Card review. The list still never sees a price. See `claude/list-at-hill-2026-11-10.md`.
- College basketball on the Daily List (11 Nov 2026, Douglas: "move to the college basketball tab unless there is a clear 1.05 or above"): a college basketball list pick shows on the list only at a William Hill price of 1.05+ (`listHillMin` / `listShown` in `index.html`, applied in `listCollect` and the counts); the rest stay on its tab with a left-off line per day. Display only, Douglas's exception to the list taking no bookmaker input; the record still grades them as list picks (whether it should grade only the shown ones is open).
- `odds.py` football-data.co.uk prices and the value backtest; since 22 Oct 2026 also API-Football prices for every fixture it lists (`af_odds_day`, by date, cached; `match_af` on names and kick-off), display only, never the value tag.
- `groupings.py` the Odds tab (4 Oct 2026; rebuilt 21 Oct): **Double** (two legs, 60%+ together) and **Treble** (three, 50%+), built to land, nothing risky. A leg needs tested rate, model and bookmaker's fair chance all 75%+, the model no more than 5 points above the market, and (football) nothing the Daily List excludes for blindness (`safe_leg`, `CLEAN_WHY`). No group when nothing clears. Today and the next three days (`DAYS_AHEAD`), every published group re-checked on each build: still passing keeps its place, failing is replaced with the reason logged (`recheck`, 21 Oct 2026). At least `MIN_GROUPS` (3) a day: when the strict kinds make fewer, **Wider Double / Wider Treble** fill from the strongest legs: 65%+ priced (`wide_leg`) or unpriced Daily List picks at 75%+, on equal terms (`best_wide`, `WIDE_RULE` 2), labelled Higher risk and graded apart (22 Oct 2026). Every group pays at least `MIN_RETURN` (2.00) combined (Douglas, 22 Oct 2026), so groups land roughly 43-48%. Football and rugby only (`GROUP_SPORTS`), each leg at min(tested rate, model, fair), settled from each sport's full graded history (`claude/odds-groupings.md`), priced by API-Football (football) and ESPN (NFL, MLB, NBA); writes `groupings.json` / `groupings-data.js` in CI before the archive commit, archives each day's first groups to `groupings-archive/` and grades them into `groupings-record.json` (both bot-written). Banker, Steady, Balanced, Stretch are retired but stay in the record. **Multipliers** (24 Oct 2026, `MULT_KINDS`, rule 2 the same evening): a separate section, up to `MULT_PER_DAY` (3) a day, each 3-4 legs from any sport (all sports since that evening; non-`GROUP_SPORTS` legs are `multOnly`, refused by `safe_leg` / `wide_leg`) with the highest combined chance paying 2.8x+; legs 1.30-1.90, the market 60%+, the model no more than 5 points above it; a leg's chance is the bookmakers' fair chance (`as_mult`), the model a veto; built after the other groups, never counted toward `MIN_GROUPS`, graded as `multiplier`. Since 25 Oct 2026 every leg shows its best price and bookmaker (`bestBook`, from `odds.af_parse_odds` `maxBook`), groups carry `bestOdds`, the record grades at average and best prices (`returnedBest`), and `update_closing` writes each archived leg's last pre-kick-off price (`lastOdds`) into `groupings-archive/` for the closing-line tally (`clv`). Since 30 Oct 2026 `archive_pool` also writes the whole priced pool, every sport, to `groupings-archive/pool-<date>.json.gz` (first price as published, last pre-start price; since 9 Nov 2026 a leg first archived as an estimate takes a `priced` block from its first real price, and rows carry `id`, so `tools/card_replay.py` can rebuild any Card rule on the month's real legs at the 30 Nov review; rows before 10 Nov have no `priced` block). Mid-priced legs enter the pool as `multOnly` and cost no per-fixture price call (`claude/multipliers-2026-10-24.md`). Prices never feed a model; they only veto legs.
- `build_tennis.py`, `tune_tennis.py` separate tennis pipeline, `tennis.json` ratings (with each tour's archive boundary). The build applies every ESPN result since the archive ends from `history-tennis/`. `tools/tennis_gap_eval.py` is the evidence. Football must never depend on it.
- `sports.py` NFL, MLB, NBA, rugby: Elo per sport keyed by ESPN team id, `--tune` (by hand, writes `sports.json`), `--daily` (CI). Separate from football and tennis.
- `ranktest.py` out-of-time check of the FIFA adjustment (2022-24). Advisory only.
- `rankings.py` FIFA and ATP/WTA world rankings: fetch, and the tested adjustments (FIFA for men's internationals, ATP for men's tennis; WTA shown only).
- `score_tennis.py` grades archived tennis picks against the winner, writes `tennis-record.json` / `tennis-record.js` (with `liveBands`, which `build_tennis.accuracy_for` quotes). Only prices published before the match started count.
- `brandassets.py` redraws icon PNGs in Pillow (the one exception to stdlib-only, local use only).

Front end: `index.html` is the template (loads `data.js`). The week ahead panel (10 Nov 2026) was removed the same evening at Douglas's request ("entirely redundant ... too cluttered"); in its place **Coming up** (`weekNext`), one line under the plan naming each later day that already has a plan bet, nothing when none does (`weekDays` stays for it and Today at a glance). Live scores (10 Nov 2026): a started Daily List pick in a US sport polls ESPN's public scoreboard from the browser once a minute (`liveTick`, `parseScoreboard`), display only and marked unofficial; grading never reads it. Cloudflare Web Analytics beacon in its head (5 Nov 2026, Douglas's Cloudflare account, `spa: true` so tab changes count as views); the dashboard is at dash.cloudflare.com under Web Analytics. `dashboard.html` is
the self-contained build output and is what gets published as the site's
index. Edit `index.html`, never `dashboard.html`.

Config the model reads: `calibration.json` (auto-refitted weekly when a
candidate beats the live curve under the gates), `home-advantage.json`
(per-league home advantage, same weekly gated refit; absent until it passes),
`europe.json` (structural, refitted by hand only), `adjustments.json`
(deliberately empty, see rules).

`RELEASES.md` is the release log; every release gets an entry and a tag.
`README.md` is the public overview (rewritten 28 Sep 2026, current).
`AGENTS.md` is the guide for any AI agent; `.github/copilot-instructions.md`
points Copilot at it. `.gitignore` keeps `data.js`, `data.json` and caches out.

Written by the bot, never hand-edit: `predictions/`, `current/`,
`record.json`, `record-graded.json`, `tennis-data.js`, `tuning-report.json`, `predictions-tennis/`,
`tennis-record.json`, `tennis-record.js`, `predictions-sports/`,
`sports-data.js`, `sports-record.json`, `sports-record.js`, `fifa-rankings.json`, `groupings-archive/`, `groupings-record.json`
(refreshed by the build when FIFA publishes). `history-sports/` and
`history-tennis/` are topped up by CI; their first walks were committed by hand. `history/` is written
by `backfill.py` and committed by hand.

## Commands

```
python3 nametest.py                          # must pass before any push
python3 -m unittest discover -s tests -v     # regression tests
python3 replay.py --audit                    # which competitions the replay can use, and why not
python3 build.py --days 7 --top 50           # what CI runs (7 days: reaches the weekend, like the other sports)
python3 build.py --days 2 --no-topup --no-odds   # fast local check
python3 score.py                             # regrade, rewrite record.json
python3 score_tennis.py                      # grade tennis picks, rewrite tennis-record.*
python3 backtest.py --season 2025-26 --prior 2024-25
python3 tune.py --report                     # advisory sweep, changes nothing
python3 predictability.py                    # which signals separate hits from misses
python3 backfill.py --probe --on 2026-09-20,2026-09-13   # probe on club dates, not an international break
python3 tune.py --fit --dry-run
python3 eurotest.py --report
python3 backfill.py --probe                  # which ESPN slugs answer
python3 odds.py --report
```

Open `dashboard.html` straight off disk to check the page.

## Automation

- `deploy.yml` runs at 00:10, 05:15, 07:40 (the morning briefing, 10 Nov 2026), 12:00, 17:00, 19:30 and 22:15 UTC, on manual dispatch, **and on every
  push to `main`**. Order: `nametest.py`, build, refuse-if-empty, `score.py`,
  tennis build, `score_tennis.py`, `sports.py --daily` (both allowed to fail),
  commit the archives back
  to `main`, rebuild, publish to Pages.
- `tune.yml` runs Mondays 04:40 UTC: `tune.py --fit` (auto-applies only after
  two consecutive Monday passes of all gates, tracked in `tuning-pending.json`), `tools/model_ideas.py --fit-home` (per-league home
  advantage, writes `home-advantage.json` only if it passes the same gates;
  Douglas's exception to rule 5, 25 Oct 2026), then `tools/model_ideas.py`,
  `--report` and `eurotest.py --report` as advisory output for a human.
- `office-agents.yml` runs four sprints a day, 00:30, 06:30, 12:30 and 18:30 UTC (9 Nov 2026, Douglas: "double output"; two from 5 Nov; skips when more than 28 office pull requests exist that day, and idles when `MAX_OPEN` (12) agent pull requests are already open) (Douglas's
  instruction, 4 Oct 2026: no owner review, every agent productive). Since
  20 Oct 2026 the sprint runs the `SPRINT_SIZE` (5) agents whose best free task
  ranks highest, one at a time, in this order: owner `office-backlog` issues,
  pipeline health (failed build, unrated fixtures), then the **HQ backlog**:
  footyalmanac-hq's `scripts/planner.py` ranks every gap between quoted and
  landed (Daily List by sport, 5-point bands, leagues, tours, sports, Odds tab
  legs) by z-score each morning and publishes `data/backlog.json` on HQ's
  Pages, with the README's priority list below the measured gaps. A backlog
  over 48 hours old is ignored and the scoreboard's own picks take over.
  Since 9 Nov 2026 the backlog leads with the Card (return at stake, legs by sport, price and opposition price, empty days, closing move, five standing Card tasks).
  Standing tasks fill any spare places. Each objective still rests 7 days.
  Every brief says the deliverable is a change that passes the gates, a note
  only when the evidence fails them (5 Nov 2026).
  The **Groups & Odds Desk** (`pick_task.DESK`: Jade, Oscar, Kofi on value,
  Hannah on leg selection) always gets one more place. `agents/open_pr.sh` (run from a copy made before the agent
  works) runs nametest.py, the unittest suite and (for pipeline code) a fast
  build without tokens, replays the branch onto the latest main, and opens the
  pull request with the footyalmanac-office GitHub App token so Tests and
  Evaluation run on it. Failed checks, model changes without every gate
  passed and changes the agent would not ship are closed with the report
  kept. Agents cannot change `.github/`, `agents/`, `CLAUDE.md` or `AGENTS.md`.
- `agents/merge_gate.py` fails closed and never trusts labels. A pull request
  merges only if all of these hold (`agents/policy.json`):
  - the required checks are green on its current head SHA
  - the evidence artifact from the verified `evaluation.yml` run says pass or n/a
  - it is confirmed mergeable
  - `main` has had only bot commits since the evaluation base
  - owner approval of that exact commit only for workflow/security paths
    (agents cannot produce these); every other class ships without review
    once the checks and evaluation pass (Douglas, 4 Oct 2026)

  The sprint calls it with `--pr N --wait`, which waits for the checks, so
  each merge lands before the next agent starts. `office-merge.yml` (03:00,
  09:00, 15:00 and 21:00 UTC) first rebases every open `office-agent/*` pull request
  that is behind `main` and pushes it with the App token so its evaluation
  re-runs (`agents/rebase_stale.py`, 5 Nov 2026; a conflicting branch is left
  with a comment), then catches leftovers. The merge is pinned with `--match-head-commit`.
  Tests: `tests/test_merge_gate.py`.
- `evaluation.yml` runs on every pull request. It uses main's harness
  (`evaluation/predict.py`, `evaluation/score_pair.py`) on the last approved
  frozen snapshot (`evaluation/approved-snapshots.json`; raw data only in the
  private repo `footyalmanac-eval-data`). The candidate predicts offline with
  no secrets. It compares on identical fixture keys and posts log loss, Brier,
  accuracy and a paired bootstrap. Insufficient evidence is a hold, so model
  changes cannot ship until a snapshot is approved. It never refits, applies
  calibration or deploys. `evaluation-freeze.yml` (owner only) makes
  snapshots. See `claude/evaluation-layer.md`.
- `ceo.yml` is **Elena, the CEO** (20 Oct 2026). Douglas opens an issue
  labelled `ceo` (HQ's CEO tab does it for him) or comments on one; only his
  words reach her (`agents/ceo_prompt.py`). Claude, as Elena, answers on the
  issue, ships what is safe through `open_pr.sh` and the merge gate (PR key
  `ceo-<issue>`), and delegates bigger work as `office-backlog` issues with an
  `agent:` label, which the next sprint works first. She cannot change the
  workflow-security paths either.
- **Weekly report** (9 Nov 2026, Douglas: "a weekly report sent on Sunday morning 8am"): a claude.ai scheduled task, "Almanac weekly report", runs Sundays at 07:40 London, runs `tools/weekly_report.py` (record files only; `--extra` for the session's health, next-week and decision lines) and `tools/weekly_report_pdf.mjs` (Playwright, sandbox only), and sends the PDF by push and email. Managed from the Claude app, not from this repo.
- **Scheduled build sessions** (9 Nov 2026): a claude.ai scheduled task, "Almanac Card build sessions", runs six times a day (00:34, 04:34, 08:34, 12:34, 16:34, 20:34 London; four times to 9 Nov) in a cloud sandbox with this file as its law: health first, then the `office-backlog` issues titled "Card:" and HQ's backlog, ships tested changes on a branch, merges its own pull requests once Tests and Evaluation pass (Douglas's authorisation), leaves `.github/` and `agents/` changes open with `needs-owner`. Managed from the Claude app's scheduled tasks, not from this repo.
- `claude.yml` runs the Claude GitHub agent when the owner or a collaborator
  mentions `@claude` on an issue or pull request. It opens pull requests; it
  never deploys.
- The bot commits to `main` every day. Pull before starting and before
  pushing. If a conflict lands on a bot-written file, take the remote copy.

## Releases

Douglas's standing instruction: every finished piece of work is committed
and pushed to `main` with a release note, so it can be rolled back.

1. Pull first. Run `nametest.py` and a fast build. Restore any bot-written
   file the local build overwrote (`predictions/`, `dashboard.html`,
   `record.json`); don't commit `data.js` / `data.json`.
2. Add an entry at the top of `RELEASES.md`: what changed for a reader, the
   evidence, the files, what was not changed, how to roll back.
3. Commit, then tag `release-YYYY-MM-DD` (annotated, `-2` for a second the
   same day) and `git push --follow-tags`. The push deploys the site.
4. Roll back with `git revert`, never `git reset`: the bot's daily archive
   commits sit between releases. Instructions are at the top of `RELEASES.md`.

## Rules

These were each learned the hard way. Do not break them without asking.

1. **Nothing is ever fitted on `record.json`.** It is the scoreboard. The
   site's one honest claim is that its numbers were published in advance.
2. **Every model comparison is paired and bootstrapped.** Two log losses near
   1.016 have a ±0.005 noise band, wider than every real effect in the model.
3. **Fit on the last completed season, confirm on the current one.** Gates:
   ≥250 check fixtures, p(worse) ≤ 0.30, gain ≥ 0.0005.
4. **Fit one thing, then re-test everything else.** Two constants looked like
   wins and evaporated once calibration went in.
5. **Structural constants never move on their own.** Only `calibration.json`
   (and `home-advantage.json`) auto-apply, and only after two consecutive
   weekly passes. Everything else is advisory until a human commits it.
6. **A name mismatch or a missing current season must fail loudly.** A wrong
   match is worse than a missed one. When a "not rated" row turns out to be a
   spelling, fix it and add the spelling to `LIVE_NAMES`. In normalisation,
   aliases before city exonyms, and founding years are stripped only at the
   last-resort step, never in the normalised form.
7. **The tier ladder has one definition**: `score.TIERS` (with
   `TIER_BACKTEST`), written to `record.json` as `ladder` and read by the page
   (25 Oct 2026). `index.html`'s `TIERS` literal is only the fallback for a page
   built without a record; `tests/test_ladder.py` keeps it in step.
8. **Automation first.** No manual data entry. Manual injury input was built
   and removed on purpose. `adjustments.json` stays empty.
9. **Honesty over confidence.** Celtic's Law fixtures are flagged and demoted,
   not hidden. BTTS is weaker than the winner board and must not be presented
   as equivalent. A failing upstream keeps yesterday's site rather than
   publishing an empty or wrong one.
10. **Don't build what won't deliver.** If a feature won't work or add real
    value, say so before building it.

## Concepts

- **Celtic's Law**: fixtures where the model is structurally blind before
  kick-off (promoted sides, unrated clubs, cross-division cup ties, overridden
  teams). Backtested as real. Flagged rows drop one confidence tier.
- **Tiers**: Strong ≥70%, Firm ≥62%, Lean ≥55%, No read below. Headline, tier
  and band figures are strict (the pick won); draw reads are a labelled
  secondary figure (25 Oct 2026).
- **Calibration**: a line in raw confidence, `T = a + b × (confidence − 0.45)`,
  read from `calibration.json` (`engine.CALIBRATION`); the flat
  `engine.TEMPERATURE` 1.15 applies only if the file is missing. Live since
  30 Sep 2026: `a = 1.135, b = −0.30` (first shipped 9 Sep as 1.075 / −0.45;
  refitted 14, 20, 28 and 30 Sep). Read the file, not this line, for the
  current values. `tune.py --fit` gates a candidate against the live curve on
  the same fixtures (until 3 Oct 2026 it was gated against the flat 1.15, so
  earlier refits were never shown to beat the curve they replaced).
- **Cup calibration**: domestic cups (API-Football, `afCup`) carry a second curve on top, `engine.CUP_CALIBRATION` (T = 0.90 + 2.75 x (conf - 0.45), 19 Oct 2026), fitted by `tools/cup_calibration.py` on the cup replay's stored ties (Jan-Jun) and checked on Jul-Oct. A raw 75% cup favourite shows about 59%. Refit by hand only. Since 24 Oct 2026 `cup_temper` also resets `confidence` to the tempered maximum; before that cup rows ranked, tiered and banded on the raw number (past record rows keep it).
- **Sources**: openfootball spells clubs in full (*FC Bayern München*), ESPN
  abbreviates (*Bayern Munich*). football-data.co.uk's extra-league files
  are the sole source for Poland, Switzerland, Romania, Finland and Ireland
  (`sources.FDX`), history and fixtures both, so each league has one spelling. Cup ties are rated against the club's
  domestic league via `domestic_of`.

## Tested and rejected, don't reopen without new evidence

Separate home/away ratings (+0.0124 log loss), a global home/away tilt `ha_scale` 0.80-0.98 (26 Oct 2026: better on both seasons but under the gain bar, p(worse) 0.36+, `claude/home-away-tilt-2026-10-26.md`), rest days (no effect), ten free
per-band temperatures (overfit), heavier recent-form weighting, tuning on the
live record. Form re-tested 29 Sep 2026 at Douglas's request, calibrated, both
seasons: a form-led model (form cap 0.30-0.50, or current season taking over
after 3 games) is +0.005 log loss worse on both; FORM_MAX 0.10 a wash. What
passed was this season counting sooner (SHRINK_FULL_SEASON 6 -> 4, shipped).
Bottom-10%-away and weak-goal-record penalties (30 Sep 2026): worse at every
strength, the ratings already carry it. See `claude/tuning-evidence.md`.
Football form by stage of season (19 Oct 2026): games 4-6 are the weak spot in both seasons, but no weighting fixes it (faster season, more form, slower season, last season only: none passes both seasons); team news is the untested lever.
Football team news (19 Oct 2026): API-Football injury and suspension lists, by count, by last season's minutes and as new absences, add nothing that passes cleanly (best: wrong-signed, under the gain bar on the fit season). `tools/team_news_eval.py`; data in `audit-out/team-news/`, never committed.
Hot form, big clubs, cups (19 Oct 2026): favourites that won their last 3 land under their quote (68.2% v 70.8%), big clubs land as quoted, cup favourites land far under (live 60%+: 56.5% v 69.7%). See `claude/tuning-evidence.md`.
Douglas's ideas (25 Oct 2026, `tools/model_ideas.py`, `claude/model-ideas-2026-10-25.md`): table position, last-5 goal difference and last-3 points make it worse at any strength; recent goals against the season average add nothing. Home advantage per league helps (fit −0.0010, check −0.0007) but misses p(worse) on the short check season: it is refitted every Monday and switches itself on through `home-advantage.json` when it passes.
The Card on past seasons (29 Oct 2026 evening, `tools/card_legs_history.py`, `card-legs-history.json`, run weekly by `tune.yml`): the leg rule over 2025-26 on football-data prices lands 72.7% v 68.0% quoted (n 417), singles -0.2% at average price, +2.4% at best, CLV -3.4%; near-market picks do as well, so the under-market filter is not the source of the edge (the favourite-longshot bias is). The whole Card at a flat stake: 77 groups, 35 won v 25 expected, +16.5% on turnover (+26% at best prices), two months made the year, five of ten lost. Picks the model rates above the market land at the market's rate at every gap size (20+ above: 20% landed, -48%); 5-10 under is the only band positive on every sample, 10+ under loses. The 5-10 cap shipped on 31 Oct 2026 as `CARD_RULE` 5 (Douglas, on Norwich 49% v 61%); variants `uncapped` (rule 4) and `short` (1.15-1.35) pre-registered in `tools/card_replay.py` for the 30 Nov review.
The Card over five seasons (9 Nov 2026, `claude/card-seasons-2026-11-09.md`, `--seasons 2022-23,2023-24,2024-25` run in CI): the under-market cut lands 2-5 points above quote in every full season (about break-even at the average price, +2-3% at best, never beats the closing line). No gap band is positive on every season: 10+ under was the best band in 2023-24 and 2024-25 and the worst in 2025-26 and 2026-27, so the rule 5 cap is not supported over 2022-25; `uncapped` is the comparison for the 30 Nov review. The opposition at 9+ (rule 6) holds: 9+ legs land about 5 points above quote in all five seasons (511 under-market legs, 83.8% v 76.2%, +4% / +7% at best; 2022-23 on quote only) and 4-6 legs lose in all five. The whole Card under rule 5 on football-data legs: 93 groups over four seasons, 37 won v 31 expected, +4.4% (+12.5% at best), 3-5 losing months a season; the Card 2x 33/69 and positive every season, the Card 3x 4/24 and negative every season. Under rule 6 the football-only Card makes one group in five seasons: the live Card's volume is tennis and NBA.
Edge picks as accumulators (10 Nov 2026, `claude/edge-accas-2026-11-10.md`, five seasons): pooled at the best price, singles +5.4% (459), doubles +4.6% (252), every Edge pick of the day +9.7% (252, 2022-23 -12%), trebles +16% and four-folds +22% but -29% to +99% by season. Not a reason to go longer: the swing grows faster than the return.
Goals market value (29 Oct 2026, `tools/goals_value.py`, `goals-value.json`): over/under 2.5 against football-data.co.uk prices, the market beats the model on log loss both seasons (0.679 v 0.686, 0.655 v 0.675) and 5-point value picks lose at best price (ROI -4.6% / -19.0%) and against the closing line (CLV -3.2% / -3.9%); the model's over number runs low in the 55-65% bands, under picks worst. No goals-market bets without a goals calibration that passes the gates.
Tennis hot form (8 Oct 2026, after Muchova v Bartunkova): a more responsive
Elo (K x 1.5) is worse on both tours; a wins-in-this-tournament term fits to
zero. The real gap was four months of missing results, now fixed. See
`claude/tennis-ratings-gap-2026-10-08.md`.

## The Card's return: decisions delegated (9 Nov 2026)

Douglas, 9 Nov 2026, after the first weekly report: "Take all decisions on
providing the highest return consistently." So the build sessions decide
Card questions themselves, on the evidence rules above (replays and the
pool, never the scoreboard; a rule change needs the pre-registered variant
to beat live on both football-data seasons and the archive, p(worse) at most
0.30 on 100+ legs) and record each decision here with its numbers. Taken so
far, on `groupings-record.json` at 9 Nov (41 full-rule groups) and
`claude/card-seasons-2026-11-09.md`:

- **Card 3x stays.** The football-data replay has it losing on every season
  under rule 5 (4 of 24), but that replay is football only and the live Card
  is tennis and NBA: live Card 3x is 7 of 15 won against 4.0 expected (+50%),
  live Card 2x 9 of 27 against 10.3 (-26%). Not retired; revisit at 50
  settled 3x groups.
- **The 10+ under cap (rule 5) is on probation, not changed.** Over 2022-25
  no gap band is positive on every season; `uncapped` (rule 4) and `opp7` are
  now replayed as whole Cards on every football-data season
  (`tools/card_legs_history.py` `cardUncapped`, `cardOpp7`), and the pool
  side accumulates from 9 Nov. Run on 9 Nov over five seasons: 32 and 23
  groups in total, signs flipping by season; nothing to act on. Decide at
  the 30 Nov review by the gate, on the pool.
- **Tennis stays on the Card, with a tripwire.** Tennis legs are the one
  consistent leak: 25 of 44 landed (57%) against 71% quoted, z -2.1, and the
  29 Oct 75% floor did not mend it (7 of 14 since). But groups with a tennis
  leg returned +11% (10 of 24) and groups without -15% (5 of 17), and 44 legs
  is under the 50-leg rule for taking a sport off. The tripwire: when tennis
  Card legs reach 50 and sit two standard errors or more under quote, the
  next session adds `"tennis"` to `CARD_SPORTS_OFF` (CARD_RULE bump, note,
  release) without asking. Since 9 Nov 2026 (morning) the record carries the
  count: `groupings-record.json` `cardLegsBySport.<sport>` (`legs`, `landed`,
  `quoted`, `z`, `tripwire`), shown on the Bets scoreboard and printed in the
  nightly Card review issue, which says in bold when a tripwire has fired
  (`claude/card-legs-by-sport-2026-11-09.md`; full rule only: tennis 22 of 40
  at 9 Nov).
- **The page's empty-day filler (the wider rule) is on watch.** Replayed for
  the first time on 10 Nov (`claude/card-fillers-2026-11-10.md`): 2 of 12
  groups won against 4.14 expected on the pool at first real prices (-54%,
  36 legs); on football-data, football only, at or above quote but under
  the price (2025-26 -0.9%, 2026-27 -11.7%). Pre-registered: when `fillwide`'s own legs reach 100 on the pool
  and its p(worse) against live is 0.70 or more, and the football-data
  `cardFillWide` agrees on both seasons, the next session drops the filler
  (an empty day stays empty; CARD_RULE bump, note, release) without asking.
  `fillrule5` replaces it only if it passes the gate on its own legs.
- **No Reports page for the weekly PDF.** It adds nothing to the return;
  the Sunday email is the delivery.
- **Opposition 9+ (rule 6) stays**: the one condition that holds in every
  season (`claude/card-seasons-2026-11-09.md`).

## Open items

- Slugs were audited against ESPN on 27 Sep 2026 and 14 leagues backfilled
  (see `claude/daily-list.md`). ESPN does not carry Poland, Croatia, Serbia,
  Ukraine, Hungary, Korea, the UAE, the 3. Liga, Liga Portugal 2 or most small
  European leagues. Covering them needs a second free source, not a slug.
- The backfilled leagues have no walk-forward of their own yet (needs a
  second prior season).
- Whether unrated rows should compete for the top of the board on raw
  confidence. Currently they do, deliberately. Douglas's call.
- "Lean or better only" filter on the fixtures board, not built.
- Tennis results from ESPN carry no surface and go in as hard court; for ATP
  that hurt over the grass season (`claude/tennis-ratings-gap-2026-10-08.md`).
  Needs a surface source before June 2027. The Sackmann archive behind
  `tennis.json` has not updated since 1-2 June 2026.
- The green **Edge** flag (10 Nov 2026, Douglas): football fixtures in football-data's leagues where the model's pick is the bookmakers' favourite at 1.15-1.90, the bookmakers 60%+, the opposition 9+ and the model no more than 5 points above the market (`groupings.edge_flag`, computed in `build.py`, archived as `edge`, shown by `edgeFlag` in `index.html`; the football board's Show control has **Edge only**, and each day's header counts the flags). The Bets tab's **Edge picks** section (`edgeSection`) lists the day's flagged fixtures with the Edge double and the whole-day slip, priced, beside their five-season test (`claude/edge-accas-2026-11-10.md`; `build.edge_tested` reads `card-legs-history.json` `edgeAccas`). Display only. Graded by `score.py` (`edge_record` in `record.json`: live from 10 Nov, replayed on archived prices before; 27 of 34 at 10 Nov, -2.1% average, +0.5% best), quoted on the page and in the nightly review. Every other sport tested on the pool (`tools/edge_sports.py`, 10 Nov 2026): none passes the gate (100+ legs, landed above the bookmakers, best-price return positive, p(loss) <= 0.30); the nightly Card review prints each sport's line from 11 Nov, and a sport that passes gets the flag in a release.
- Market input to the Daily List: on 909 archived priced fixtures the market beats the model on log loss (0.979 v 1.013) and picks the model rates 5+ points above the market land at the market's rate (`tools/market_check.py`). The list takes no bookmaker input by Douglas's standing decision; the evidence is there if he wants to revisit it.
- Past cup rows in the record carry the untempered confidence (fixed for new rows 24 Oct 2026). Whether to regrade their bands is Douglas's call.
- No dark theme. The flag sprite covers every country code in `engine.LEAGUES`
  (84 symbols); a new league with a new `iso` needs a symbol added.

- 227 wider leagues from API-Football (`af-leagues.json`, `engine.AF_EXTRA`): tier 2, own bands, list bar 75% (`build.LIST_MIN_AFX`), out of the calibration fit. National League, North and South also come from `AF` now.
- English step 3 (four leagues, `sources.AF`) is on the board and reserve, never the Daily List: replayed below the bar (`build.NO_LIST`).
- The Daily List shows every pick that clears the bar (no cap since 8 Oct
  2026: the records grade every list-flagged pick, and 10 Oct had 36). The
  **reserve** (below the bar, Firm 62%+, clean) sits in a fold under each
  day, open by itself when fewer than 20 picks clear the bar; flagged per
  pipeline as `reserve` and graded as its own group (`record.json` /
  `tennis-record.json` / `sports-record.json` "reserve"). "How it went" has
  the same fold under each list day.
- College football is off the Daily List (`sports.LIST_OFF`, 19 Oct 2026: 80%+ landed 74% v 86% quoted, z -2.1); its Firm+ picks go to the reserve. Tennis was off from 15 Oct and back on from 28 Oct (`build_tennis.LIST_ON`): the removal rested on a 1.1 standard-error shortfall, and 75%+ landed 139 of 163 (85%) over the whole record. Rule for taking a sport off: under quote by two standard errors or more on 50+ picks at the bar. Review tennis at 300 graded list picks.
- The Starred tab's **Run** button (`runSlip` in `index.html`) gives the
  chance all starred picks land, fair odds, and a Strong / Reserve / Wary
  verdict per leg. Site numbers only, never bookmaker prices.
- International ratings are refitted on every match to date when
  `tune_international.py --fit` runs (before 30 Sep 2026 they stopped at the
  holdout start, 1 Jan). Nothing reruns it automatically yet; weekly in
  `tune.yml` is the obvious home, Douglas's call.
- Picks the FIFA ranking lifts 20+ points landed 65% of 40 in 2022-24.
  Confirm on 2026 before flagging them (`claude/ranking-review.md`).
- Row "landed" rates are cumulative bands, so a 79% pick shows the 75%+
  record (84%) including 90%+ calls. Own-band rates would be stricter. Douglas's call.

## Known drift

- The notes say the 74 league strength coefficients are hand-set and
  untested. `eurotest.py` and a fitted `europe.json` now exist. Check how
  `engine.py` consumes it before treating the coefficients as untested.
- `claude/brand-identity.md` describes a three-bar mark with Anton;
  `brandassets.py` on `main` still describes a slab-serif A in Bevan. What is
  live (28 Sep 2026), and Douglas's choice: the Grays-style cover (red star
  banner, grey cover with "Sports" in Bevan red over "Almanac" in Archivo
  Black white, "Complete sports statistics", black year band, red stat panel
  with yellow corner flash), bands flush to the cover edge, 1px dark borders,
  sticky tab bar on desktop. A slimmer dark masthead was tried and reverted
  at his request (release-2026-09-28-4). The brand note's contrast tokens still apply (`--mute` is now its
  4.8:1 value).
- `claude/coverage-expansion.md` calls the ESPN slugs unverified and lists 45
  leagues to backfill; superseded by `claude/daily-list.md`.
- The local Mac has Python 3.7 only (Homebrew can't install 3.12 on it).
  `nametest.py` and `build.py` run on 3.7; `eurotest.py` needs 3.8+.

## Working with Douglas

- UK English. No em dashes. Direct and output-first, no preamble or filler.
- If he's wrong, say so and why.
- Deliver complete, working changes, not outlines. Say what changed, where,
  and why, in a few lines.
- Run `nametest.py` and a fast local build before saying something is done.
- Work from context; ask only when a decision is genuinely his.
- Visual work: hierarchy, spacing, type, colour and restraint, and respect the
  contrast tokens in the brand note.
- After a significant piece of work, add a dated note to `claude/` in the same
  style as the existing ones, and update this file if a rule, file or open
  item changed.
