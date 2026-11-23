# Sports Almanac (repo: footyalmanac)

A daily-refreshed sports prediction site: football (a Dixon-Coles adjusted
Poisson model, home / draw / away), tennis (surface Elo), and NFL, baseball,
basketball and rugby (Elo per sport). It rates every team or player it has free
data for, prices each upcoming game, ranks the slate so the most predictable
games sit at the top, and grades itself publicly against what actually
happened. It began as football-only, which is why many notes and names say
"football" or "footy".

- Live: https://sportsalmanac.bet/ (since 16 Nov 2026; the github.io address redirects)
- Repo: https://github.com/douglasbakeronline/footyalmanac (public)
- Owner: Douglas. At least one other collaborator has push access.

The point of the site is honest confidence: surface the genuinely predictable
games, say plainly when a call is weak, and never inflate a number to look good.

The front page is the **Daily List**; **Bets**, the second tab (`renderToday` in `index.html`, the `today` view: Today's bets and the Odds tab merged on 25 Oct 2026, Douglas's decision), holds **the Card** (`groupings.build_card`; since 11 Nov 2026 the model's own picks, `CARD_MODEL_RULE`, `CARD_RULE` 7, the rule described next is rule 6, kept as the `rule6` replay variant: one window a day, 07:00 UK to 07:00 the next morning (`CARD_WINDOWS`; the three windows to 28 Oct 2026 stay in the record), no clock lock: a group is open until its first kick-off (`first_kick`), re-checked on every build and holding unless a pick fails the rule or the combined price moves more than `CARD_DRIFT` (10%) outside its band (30 Oct 2026), then frozen as published and archived (Douglas, 29 Oct 2026), up to `CARD_MAX_GROUPS` (6) groups a day, a Card 2x and a Card 3x then a second of each (`seq`; since 11 Nov 2026 the 2x alone, up to three a day, `CARD_BUILD`, `CARD_RULE` 8), each of 3-5 bookmaker-priced 60%+ picks from different fixtures (five since 6 Nov 2026), staked `CARD_STAKE` (two units on a 2x, one on a 3x), the record tallied per `CARD_RULE` version (`cardByRule`), each pick with its price at every UK book (`bookOdds`) and the card written for William Hill (`CARD_BOOK`, a preference not a filter), each group with up to three substitutes (`bench_for`), NFL, college football and college basketball (no live record, 31 Oct 2026) never, tennis only at 85%+ on model and tested rate (75% until 11 Nov 2026, `CARD_RULE` 10), football from the core leagues and, since 11 Nov 2026 (`CARD_RULE` 11, Douglas on Leotar), the wider leagues too (`CARD_CORE_ONLY` False, through `card_league`: cups and internationals still out; tried and reversed on 29 Oct 2026 after the two-rule replay; `CARD_CORE_NUDGE` puts core picks first; `m7core` replays core only, `claude/card-wider-leagues-2026-11-11.md`) and with the model 5 to 10 points under the bookmakers' chance (`CARD_SPORTS_OFF`, `CARD_SPORT_MIN`, `CARD_UNDER_MARKET`, 29 Oct 2026; `CARD_UNDER_MAX` 31 Oct 2026, 10+ under lost on every sample, `CARD_RULE` 5) and the opposition priced 9+ (`CARD_OPP_MIN`, `CARD_RULE` 6, 6 Nov 2026; under the model's rule the two bookmaker conditions, the value demand `CARD_MODEL_EDGE` and rule 12's football opposition floor `CARD_MODEL_OPP_MIN`, were both switched off on 17 Nov 2026, `CARD_RULE` 13, `claude/card-rule13-model-only-2026-11-17.md`; since 19 Nov 2026 (`CARD_RULE` 14) the Card runs rule 8's constants: the value demand on, core leagues only, tennis 75%+, no two-day groups, `claude/card-rule14-rule8-2026-11-19.md`: Douglas's observation, replayed in `claude/opposition-price-2026-11-06.md`; every leg of every sport carries `opp` and `draw`, shown on the page, football only for the rule), the record carrying `z` against expected and the scoreboard a floor line (`CARD_FLOOR_Z` -2 on 50+ groups retires the rule), never changed after its first kick-off; a day the full rule leaves empty got a marked wider-rule group until 11 Nov 2026 (switched off then, `CARD_FILLER` False, Douglas: "the groups must win at all costs", `claude/card-filler-off-2026-11-11.md`; an empty day now stays empty), 3-5 picks at 1.08-2.10 and 60%+ (55%+ until 11 Nov 2026, Douglas on Luton v Almere City, `CARD_WIDE_RULE` 2, `claude/card-filler-like-almere-2026-11-11.md`), graded apart as `cardWide` (by version in `cardWideByRule`); tennis matches ESPN dates at midnight New York take their tournament's usual first start, `tennis_starts`), **The plan** (removed from the page 11 Nov 2026 at Douglas's request, `claude/plan-decision-2026-11-10.md`; the functions stay unused; `signalsPanel` / `planRungs` in `index.html`, 10 Nov 2026, Douglas: "one clear direction that uses the best case from each"; was Place now: three rungs in order of proof, Edge singles (Tested, one unit), the Edge double of a day's two most likely Edge picks (Tested, one unit, built in `sigList`), the Card (On trial, its own stakes), four habits, then today's open bets tested first, Hill price, stake, copy slip; the wider-rule filler, the Model card and the week ahead's model trebles named as not in the plan; display only, `claude/the-plan-2026-11-10.md`), Coming up (one line, later days with a plan bet), the **Model card** on paper (`build_model_card`, `MODEL_KINDS`, 31 Oct 2026: a Model 2x and 3x a day of the model's own picks, each rated 60%+ and at or above the bookmakers' chance with the group's chance the model's own, never staked or pushed, graded as `cardModel`; the Card chosen the other way round, compared at the 30 Nov review), the playbook (first habit "Place once" since 11 Nov 2026, worded since 12 Nov 2026 from the settled price-timing read, `timing` in `groupings-data.js` from `price_timing.page_read`, `placeHabit`: "late" only while the read says so, `claude/place-late-faded-2026-11-12.md`; the paper Model card fold shows only on a day that has one, none built under rule 7), the picks to leave out (`groupings.avoid_list`), a slip checker, the re-check log, the accumulator calculator, the scoreboard by window and the day-by-day group history (`ogRecord(true)`). There is no Odds tab, and no Baseball or WNBA tab (too few games; their picks still reach the Daily List). See `claude/the-card-2026-10-25.md` and `claude/todays-bets-2026-10-25.md`. The Double / Treble / Wider / Multiplier kinds are no longer built; their record stays. The **Daily List** is the most likely results across every
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
| claude.ai/code (cloud) | A branch and a pull request, with the would-be `RELEASES.md` entry (mark the tag "pending"). A push to `main` deploys the live site. Since 15 Nov 2026 Douglas has given standing authorisation for every session, cloud and scheduled, to merge its own pull requests once Tests and Evaluation pass, `.github/` and `agents/` changes included, and to rebase, merge or close stale pull requests (keeping anything of value): "I don't want to keep having to do this myself". Leave nothing open labelled `needs-owner` for him. Tested 28 Sep 2026: the cloud session can push branches and commits but **not tags** (GitHub drops the connection), and **cannot reach ESPN**, so its builds are partial. The tag is added automatically after merge (`release-tags.yml`, 14 Nov 2026). |
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

## Skills (`.claude/skills/`)

Eight shared skills, the same set in each of Douglas's project repos (added
12 Nov 2026; sources, versions and what was left out are in
`.claude/skills/SOURCES.md`).

| Skill | Use it for |
|---|---|
| `verification-before-completion` | Before saying anything is done, fixed or passing |
| `systematic-debugging` | Any bug, failing test or odd output: find the root cause before fixing |
| `test-driven-development` | Logic changes: a failing test first |
| `requesting-code-review` | A fresh-context reviewer subagent on the diff before it ships |
| `verification-loop` | The pre-ship check report (build, types, lint, tests, secrets, diff) |
| `security-review` | Auth, user input, secrets, API routes, third-party data |
| `production-audit` | "Is this ready to ship? What breaks in production?" |
| `safety-guard` | Destructive commands: stop and take the safer route |

How they fit this repo:

- **This file wins.** Where a skill and a rule here disagree (how work lands,
  release steps, commands, what not to touch), follow this file. The skills
  shape how you work, never where or how work ships.
- **Unattended runs don't stop to ask.** Where a skill says to ask your human
  partner, decide, write the decision and the reason where this repo records
  its work, and carry on. Stop only for something irreversible.
- **Use this repo's own checks:** `nametest.py`, the regression tests and the fast build under "How to verify a change" in `AGENTS.md`, plus the release steps under Releases below. The npm, pyright and ruff
  commands in the skills are generic examples.
- **Test-first is for logic**: code whose behaviour a test can pin. Visual,
  copy and generated or bot-written data changes are checked the way this
  repo already checks them, not test-first.
- **No dependency churn from a review.** Don't run `npm update`,
  `npm audit fix` or upgrade packages because a skill suggests it, unless the
  task is a dependency update.
- **Never** `git push --force`, `git reset --hard` on a shared branch, or
  `--no-verify`. `safety-guard` is advisory, so this line is the rule.

## Read before non-trivial work

`claude/` holds dated handover notes. Read the one that matches the task.

| File | Covers |
|---|---|
| `claude/full-review-2026-10-25.md` | Full review of 25 Oct 2026: live record by tier and sport, 22 bugs with fixes, the betting record, costs, and a dated timeline. Read first when deciding what to work on next. |
| `claude/home-away-tilt-2026-10-26.md` | The away under-quote on the live record, the `ha_scale` sweep through the gates (failed on gain and p(worse)), why AF_EXTRA cannot be gated on the replay, what would settle it. Read before touching home advantage or `HOME_MULT`. |
| `claude/the-slip-2026-11-15.md` | The slip (`slip.py`, Bets tab): the ledger's return by price band (short prices hold their value, the model's disagreements with the market lose), the leg rule, the 3x-6x search for expected return, the gate and the walk-forward replay. Read before touching `slip.py` or proposing any accumulator for the page. |
| `claude/ncaab-early-k-2026-11-16.md` | College basketball's faster early-season K (`sports.EARLY_K`, x1.5 for a team's first 6 games after the summer; check log loss 0.5499 to 0.5475, p(worse) 0.00), heavier summer regression rejected, `GRID_SPORT["ncaab"]` pinned at live, and the display-only Behind .500 mark (`trailWary`, 75% v 80% on the replay) with its pre-registered review. Read before touching college Elo settings or the college row marks. |
| `claude/college-side-mark-2026-11-15.md` | The Away / Neutral mark on college picks (`sports.wary`, `sideWary`): home college picks land above quote on the replay, away and neutral do not; the `bySide` tally and the pre-registered away tripwire (100 picks, z -2). Read before touching `WARY_SPORTS` or proposing a side rule for the college sports. |
| `claude/daily-list-losses-2026-11-14.md` | Saturday 14 Nov's losses read against the quotes (the list and reserve landed as quoted), the carried-rating idea tested and rejected on the replay, the open model tests for the college sports. |
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
| `claude/card-record-at-stakes-2026-11-11.md` | The Card's record at the page's stakes (`unitsStaked`, `unitsReturned` in every `groupings-record.json` tally; 11 Nov 2026: -19.3% at two units a 2x and one a 3x v -12.2% flat on 35 groups). Read before quoting the Card's live return. |
| `claude/card-filler-like-almere-2026-11-11.md` | The filler's floor raised to 60% (Douglas: Luton out, more like Almere City): legs by shape, bookmakers under 60% the worst band (-6.3%), Southend's shape the best (+7.4%), why only the floor moved. Read before touching `CARD_WIDE_*`. |
| `claude/card-model-rules-2026-11-11.md` | The Card switched to the model's own picks (`CARD_MODEL_RULE`, `CARD_RULE` 7): the evidence at the switch, `rule6` kept as a variant, how to roll back. Read before touching the Card's leg rule. |
| `claude/card-funnel-rule7-2026-11-11.md` | The funnel and the integrity check made to read rule 7/8; the value demand the one condition costing groups; `m7under5` (model up to 5 under) replayed worse. Read before loosening `CARD_MODEL_EDGE` for volume. |
| `claude/card-m7wide-2026-11-11.md` | The core-league limit under rule 8: `model_fault` reads `CARD_CORE_ONLY` (still True), the funnel's "league" relief (45 football legs kept off by it alone v 14 by the value demand), `m7wide` pre-registered and read (more groups, lower return, under the gate). Read before admitting wider leagues to the Card. |
| `claude/card-replay-rule6-family-2026-11-11.md` | Why the rule 6 variants replayed as live after rule 7, `RULE6_FAMILY` / `patch_of`, the pool numbers v live and v `rule6`. Read before adding a Card replay variant. |
| `claude/card-2x-only-2026-11-11.md` | Six shapes of the model's-picks Card replayed on five football-data seasons and the pool; why the Card builds the 2x alone (`CARD_BUILD`, `CARD_RULE` 8); bigger edge demands made it worse. Read before changing the group shape. |
| `claude/card-payout-bands-2026-11-11.md` | The Card at 1.5x, 2x, 2.5x and 3x and Douglas's ladder, five football-data seasons and the pool: the 2x the only band ahead pooled (+10.3%), the 1.5x steadiest but flat (+0.6%), the 3x and the ladder losing. Read before changing the Card's payout. |
| `claude/context-check-2026-11-11.md` | The context check (`context_review.py`, `CARD_CONTEXT`, `CARD_RULE` 9): Claude reads every Card pick with web search, an "against" verdict keeps it off the Card, graded forward as `cardContext`; when to switch it off. Read before touching the veto or the review prompt. |
| `claude/card-staking-2026-11-09.md` | `tools/staking.py`'s bankroll corrected (it was inverted), the month and season bankroll at the page's stakes, the live 2x / 3x split against the replay's, `flatstake` pre-registered. Read before touching `CARD_STAKE` or the staking section of the review. |
| `claude/price-lead-time-2026-11-09.md` | The Card's price move by the first price's lead on the start, last prices stamped after the start (`whenLast`, `lastAfterStart`). Read before touching the push time in `notify.py` or `CARD_BOOK`. |
| `claude/price-timing-read-2026-11-10.md` | The price-timing read made to earn its place (50+ legs, day-resampled p <= 0.10), the singles return at the first v the last pre-start price (+1.95 points late on 104 settled legs, p 0.011, mostly football), unstarted legs left out. Read before moving a push time or telling anyone when to place. |
| `claude/place-late-faded-2026-11-12.md` | The 10 Nov late gain gone by 12 Nov (-0.25 points on 174 settled legs, p 0.70; rule 6 legs rebuilt +0.32); the playbook's first habit now written from the read on every build (`placeHabit`). Read before quoting any price-timing number on the page. |
| `claude/card-book-paired-2026-11-13.md` | Each UK book against William Hill on the same Card-rule picks (`price_timing.book_vs`, 13 Nov 2026): Bet365 +1.06% a pick on 88 paired football picks (p 0.000, about +3% a 2x), Betfair and BetVictor behind Hill; `CARD_BOOK` unchanged, Douglas's call. Read before touching `CARD_BOOK`. |
| `claude/card-funnel-2026-11-10.md` | Which Card condition costs the groups (`tools/card_funnel.py`): no football leg cleared rule 6 from 6 to 12 Nov, the 3x returns only by relaxing the tennis floor or the opposition rule, two legs per competition caps NBA groups. Read before any Card change made for volume. |
| `claude/card-fillers-2026-11-10.md` | The empty-day fillers on the replay: the page's wider-rule fallback (`fillwide`) 2 of 12 won v 4.1 expected on the pool, `fillrule5` the one alternative that builds, the pre-registered drop-the-filler decision, the filler's own legs as the gate. Read before touching the wider-rule block of `build_card`. |
| `claude/list-accas-2026-11-10.md` | Daily List picks as accumulators (`tools/list_accas.py`): the picks land as quoted singly and combined, the loss is the price (average 1.12, margin 5.3%, about -5% a leg compounding), what the data supports instead. Read before any change made for people betting the Daily List. |
| `claude/list-at-hill-2026-11-10.md` | The Daily List at William Hill: the UK-books pass for list picks (`price_odds_api(list_books=True)`, `LIST_BOOK_*`), the chips and the "At William Hill" filter, the `listAtBook` record line, what it cannot tell apart yet. Read before touching list pricing or The Odds API ledger. |
| `claude/edge-flag-2026-11-10.md` | The green Edge flag on football fixtures (`groupings.edge_flag`, `EDGE_RULE`): the rule, the evidence (511 legs over five seasons, the site's own archive), why football-data leagues only, the page. Read before touching the flag or the Card constants it reuses. |
| `claude/edge-sports-2026-11-10.md` | The Edge flag tested on every sport (`tools/edge_sports.py`): only the pool has non-football prices, no sport passes the gate yet, the short favourite (1.15-1.30) tracked out of sample from 11 Nov in the nightly review. Read before giving any other sport the flag. |
| `claude/card-modelcard-2026-11-10.md` | The Model card's rule replayed beside the Card (`modelcard`, `cardModel`): on the pool 7 of 12 groups v the Card's 4 of 10, under the gate, but -8.2% over 2025-26 on football-data (70 groups); the pre-registered switch for the 30 Nov review. Read before comparing the Card and the Model card. |
| `claude/the-plan-2026-11-10.md` | The plan on the Bets tab: the three methods (Edge, the Card, the week ahead's model trebles) by their evidence, what was taken from each, the Edge double, what is not in the plan and why. Read before changing what the Bets tab tells people to bet. |
| `claude/edge-accas-2026-11-10.md` | Edge picks as accumulators over five football-data seasons (`edge_accas`): singles +5.4% and every Edge pick of the day +9.7% at the best price pooled, ahead in four seasons of five; longer slips swing -46% to +99%; the Bets tab's Edge picks section. Read before changing how the Edge flag is offered for betting. |
| `claude/mismatch-rule-2026-11-11.md` | Douglas's mismatch rule (top-of-table form side at home v the opposite) against the price over five seasons: wins as often as priced, no edge; the games-played split. Read before proposing any table or form filter for the Card. |
| `claude/edge-floor-2026-11-11.md` | The Edge flag's opposition floor lowered from 9.0 to 4/1 (5.0) at Douglas's call, the band evidence he was shown, `EDGE_OPP_MIN`, the record by rule, what would reverse it. Read before touching the Edge floor. |
| `claude/odds-all-games-2026-11-11.md` | Odds for every game: what was priced on 11 Nov and why not, every tennis and US game asked of The Odds API, caps that follow the account, football calls for every leg, the price chip on every row, the free-plan limit. Read before touching how legs are priced. |
| `claude/free-prices-2026-11-11.md` | Why the site cannot read William Hill directly, every free odds source found on 11 Nov and its terms, `free_prices.py` (Betfair, Matchbook, SportsGameOdds), the risks to check on the first build with keys. Read before adding a price source. |
| `claude/tennis-floor-85-2026-11-11.md` | Tennis on the Card at 85% (`CARD_RULE` 10), the "Under 80" mark on tennis rows, `holdPlace` keeping a tapped row in place. Read before touching `CARD_SPORT_MIN` or row redraws. |
| `claude/card-wider-leagues-2026-11-11.md` | The Card admits the wider leagues (`CARD_CORE_ONLY` False, `CARD_RULE` 11) at Douglas's call after Leotar; the replay against it; `m7core`. Read before touching the Card's league limit. |
| `claude/card-replay-rule6-tennis-2026-11-12.md` | The rule 6 family had inherited the live 85% tennis floor, so `rule6`, `notennis` and `tennis80` replayed alike; `RULE6` pins tennis at 75%. Read before pinning any constant a later `CARD_RULE` changes. |
| `claude/card-m7legs2-2026-11-12.md` | Two-pick Card 2x groups (`m7legs2`) replayed after the empty 11 and 12 Nov: more groups, worse return (football-data 2025-26 -18% v live +22%); the 3-pick minimum stays. Read before loosening `CARD_LEGS` for volume. |
| `claude/card-price-gaps-2026-11-12.md` | Legs a missing bookmaker price alone keeps off the Card (`card_funnel.price_gaps`, in the nightly review from 10 Nov): four lost on started days at 12 Nov, so price coverage is not the lever. Read before spending price credits for Card volume. |
| `claude/card-price-gaps-rule13-2026-11-18.md` | The price-gap section read under rule 13 (no value demand left to clear) and the empty days named (`empty_card_days`): 39 started-day legs, 6 on 4 empty days, at most 2 a day, all lower leagues no UK book prices; still not the lever. |
| `claude/card-m7under5-seasons-2026-11-12.md` | The value demand's relief (`m7under5`) on five football-data seasons: behind live in all five, pooled p(worse) 0.99 on 912 legs; `cardM7Paired` / `cardM7Pooled` pair every rule 7 variant with live; `m7core` equals live on football-data. Read before loosening `CARD_MODEL_EDGE`. |
| `claude/card-span-2026-11-12.md` | Two-day Card groups (`CARD_SPAN`): a day with no group borrows the next day's picks, holding one of its own; `taken` keeps them off the next day; `span2` replayed (+2 days, return unchanged; since 17 Nov 2026 the replay's live spans and `nospan` is the rollback). Read before touching how days are built. |
| `claude/card-replay-live-span-2026-11-17.md` | The Card replay's "live" built without two-day groups for five days after `CARD_SPAN` went live, so every variant was paired against a Card the page no longer built (`span2` was live); now every live-machinery variant spans (`card_replay.spans`), `nospan` is the rollback, and the watch list changes (m7under5 and tennis75 no longer ahead). Read before reading any pool replay from 12 to 17 Nov. |
| `claude/card-span-held-2026-11-15.md` | The day before's two-day group held after midnight (`groupings.span_held`): 15 Nov staked Pistoiese and the 76ers twice; `card-pick-twice` in the nightly integrity check. Read before touching `span_taken` or `CARD_SPAN`. |
| `claude/card-empty-day-why-2026-11-13.md` | Why a day has no Card group (`card_short`, `cardShort`, `cardShortText`: few, spread, long, short, chance), the 13 and 15 Nov "long" days (three picks over the 2x top), and the two-day group's search fixed to hold a pick of its own day (`best_card` `need`). Read before touching the empty-day message or `CARD_SPAN`. |
| `claude/openfootball-lag-2026-11-13.md` | openfootball's 2026-27 files stopped scoring matches after 20 Sep 2026 (746 played matches unseen by the ratings); the lagging leagues are now scored from ESPN under openfootball's spelling (`build.lagging_codes`, `build.fill_lagging`, `topup_current(since=)`), all or nothing on names. Read before touching how the current season is assembled. |
| `claude/pool-moved-fixtures-2026-11-13.md` | A fixture moved to another day sat in two pool files and was read twice; `groupings.pool_rows` (one row a fixture, its latest placement) is how every pool reader reads the archive now. Read before writing anything that reads `groupings-archive/pool-*`. |
| `claude/replay-check-season-lag-2026-11-15.md` | The replays' check season (`tune.load`, behind tune, backtest, the Card's football-data replay and the Monday refits) ended on 20 Sep for every openfootball league; now filled from the committed ESPN cache by the build's rule (903 to 1,638 check fixtures). Read before touching `tune.load` or quoting a 2026-27 replay read made before 15 Nov. |
| `claude/stale-league-flag-2026-11-14.md` | A league table still missing results after the lagging fill (5+ unplayed fixtures over 3 days back, `build.stale_leagues`) flags its fixtures under Celtic's Law; the Czech First League, which ESPN does not score; API-Football and football-data leagues only logged (`stale watch`). Read before touching `STALE_MIN` or the Czech source. |
| `claude/czech-results-api-football-2026-11-18.md` | The Czech First League's blank fixtures scored from the API-Football day pool the build already reads (`sources.AF_LAG`, `af_lag_results`, `fill_lagging(source="apifootball")`), all or nothing on names and country, nothing written to `current/`; Czech letters folded in `_base`. What the first CI build should print. Read before adding a league to `AF_LAG`. |
| `claude/belgium-undated-rounds-2026-11-14.md` | Belgium's openfootball file dates rounds 1-7 only, so the Pro League was off the board from 20 Sep; an exhausted league takes its window from ESPN (`build.exhausted_codes`, `fill_window`) and its undated-round results are added (`fill_lagging(append=True)`). Read before touching how an openfootball league's fixtures are assembled. |
| `claude/context-paused-2026-11-14.md` | The context check paused by the API key's monthly limit on 14 Nov (back 1 Dec), the self-pause and where it shows, the office sprints failing the same way. Read before touching `context_review.py`'s calls or `DAILY_READS`. |
| `claude/briefing-chain-2026-11-16.md` | The briefing chain: every deploy run starts `briefing_watch.py --wait`, which sleeps until the next unsent slot and dispatches the build that sends it; why (16 Nov: the watchdog's own crons shed, the morning push 96 minutes late). Read before touching `briefing-watch.yml` or `briefing-next`. |
| `claude/briefing-lateness-2026-11-13.md` | The briefing pushes against their slots (12 Nov lunch 2h18 late, night 1h40), the send-time log in `briefed.json`, the nightly review's table, the backup crons left for the owner. Read before touching `notify.py` slots or deploy.yml's schedule. |
| `claude/pool-order-of-play-2026-11-14.md` | The pool's `timeEst` kept as first written, so the replay and funnel refused tennis legs timed later; `timeSet` / `whenSet` and `pool_time_est` (forward only); the Card's tennis legs by band on the pool (the shortfall sits under 70%, 85%+ four legs). Read before reading the funnel's tennis "no-time" column. |
| `claude/football-no-kickoff-2026-11-19.md` | The second named noFixture read (six spellings) and the football legs with no kick-off time: every row of La Liga, the Süper Lig and Brazil's Serie A, never "started", so a Card group could stay open past kick-off; API-Football's time on the leg, the Card's no-time guard. Read before touching how a football leg's `when` is set. |
| `claude/super-lig-untimed-spelling-2026-11-19.md` | The first CI read of `build.fill_untimed` (#425): La Liga and Brazil's Serie A took API-Football's days and times, the Süper Lig was refused whole on one spelling (Erzurumspor FK), now an alias; stale nominal-date copies in the archive checked and found not to double-grade. Read before adding a league to the untimed fill. |
| `claude/premier-league-nominal-times-2026-11-19.md` | openfootball's Premier League times are a nominal Saturday 15:00 and Serie A's 29 Nov round has none: `sources.AF_RETIME` (en.1) has `build.fill_untimed(retime=)` take API-Football's date and time when they differ; it.1 joins `AF_UNTIMED`. Read before adding a league to either. |
| `claude/football-nofixture-names-2026-11-19.md` | The first named noFixture read: four API-Football spellings (`AF_SPELLINGS`), Premier League and Brazilian games on another day (`moved`). Read before adding a spelling. |
| `claude/football-card-unpriced-2026-11-20.md` | The 19 Nov "noOdds (Premier League 12)" was a dozen leagues of that name; core-league 60%+ legs 41 of 43 priced 13 to 23 Nov; `comp_label`, `card_unpriced`, `card_reach` on the live league test; the Odds API football fallback not built and when to build it. Read before spending credits on football prices. |
| `claude/football-calls-card-first-2026-11-19.md` | The capped football price calls (`FB_CALLS_MULT`) spent Card-reachable legs first (`call_order`): 97 legs capped on the 19 Nov 11:05 build, Premier League among them. Read before touching the cap or the call order. |
| `claude/football-unpriced-2026-11-14.md` | Why football legs go unpriced (`price_football` `miss`, the build log's "football unpriced:" line): first read 101 of 104 misses `noOdds` (no book prices the game), 3 `noFixture`; names are not the gap. Read before chasing football price coverage. |
| `claude/card-tripwire-at-floor-2026-11-14.md` | The sport-off tripwire reads the legs today's floor admits (`atFloor`): all 41 tennis Card legs to 14 Nov were under 85%, 30 from rule 1. Read before acting on the tennis tripwire. |
| `claude/results-ledger-2026-11-14.md` | The results ledger (`ledger.py`, `results-ledger.json.gz`) and `sports-graded.json`: every prediction with its result and pre-start price, how moved fixtures and rematches are told apart, where prices come from and their coverage, the ungraded report, the first read (85%+ list picks land but lose at their prices). Read before analysing results against prices or chasing missing grades. |
| `claude/football-markets-2026-11-14.md` | Football markets beyond the match winner (`markets.py`): the ten markets and how each number is read from the scoreline grid, API-Football's bet ids and labels (probed live), the archive, `markets-record.json`, the pre-registered gate, the first calibration read on 11,112 fixtures (goals run low; double chance, draw no bet and win to nil on quote). Read before touching `markets.py`, adding a market or offering one for betting. |
| `claude/scale-2026-11-15.md` | The Scale tab (`scale.py`, `renderScale`): Daily List winners with a second condition (football: and both teams score, only where William Hill prices it; tennis: in straight sets), the archive, the day's threefold / fourfold / fivefold, grading, live v before the tab, the volume and value caveats, the margin bets still to add. Read before touching `scale.py`, the Scale tab or adding a sport to it. |
| `claude/scale-tiers-2026-11-15.md` | Scale rule 2: the three tiers (Daily List, reserve, everything else at 55%+ topping the day up to ten), the margin bets proposed from the record (NBA by 10+, NFL by 7+, rugby by 8+), the band rate, the groups and the football threefold, football by tier, the rematch grading bug, the replay of the days before the tab and what keeps it unbiased (first read: list tier 90% won, 62% landed; threefold 4 of 14). Read before changing `FLOOR`, `TARGET`, a margin or the group kinds, or quoting the replay. |
| `claude/scale-strong-legs-2026-11-15.md` | The Scale review and rule 3: win and both score flat at 28-38% whatever the winner's strength and priced at about 16% a leg by William Hill, win and over 2.5 rising to 77%, the Scale bet by tier across five sports (Daily List 63%, reserve 48%), groups from Daily List picks only, the 41-day group replay, what was tried and rejected, why nothing yet shows the bets pay. Read before changing `FOOTBALL_MARKET`, `GROUP_TIERS` or what a Scale group is built from. |
| `claude/scale-pool-and-starred-2026-11-15.md` | Scale rule 4 (a group's football legs from every football fixture William Hill offers, `GROUP_ANY_TIER`, the replay against rule 3) and Starred drawn with the Daily List's own items and row function (`listPut`, `starIdOf`). Read before touching the Scale group pool or how Starred renders. |
| `claude/data-inventory-2026-11-16.md` | What is kept, where, since when and how big, every sport; what is not kept and why; the data capture of 16 Nov (football half-time scores in `periods/`, football extra lines `x` in the markets archive, US sports and rugby points by period `hp`/`ap` and ESPN's `line` in `history-sports/`, `eloDiff` and `line` on each sports prediction); why the daily files are not compressed. Read before adding or removing anything kept. |
| `claude/scale-every-bet-2026-11-16.md` | Every scale bet tracked across every sport (`scale_ladder.py`, the Scale tab's Every scale bet table): which bets, what the scores cannot settle, the first read (football win by 2+ 82% and tennis by 4+ games 84% at 85%+). Read before changing a Scale bet or quoting a scale rate. |
| `claude/scale-estimated-prices-2026-11-15.md` | Estimated prices on the Scale tab where no feed prices a bet (`est_price`, `EST_MARGIN`, `estRet`): how they are worked, how they show, why an estimated return says the bets landed as often as their chance and not that a book would have paid it. Read before quoting a Scale return or changing a margin. |
| `claude/card-m7opp-2026-11-15.md` | Rule 6's opposition condition was dropped with the switch to the model's picks (`model_fault` never read it); `CARD_MODEL_OPP_MIN` (empty live) and the pre-registered `m7opp9` / `m7opp5`; 5.0 ahead of live in all five football-data seasons (pooled 450 legs, +17.5% v +9.6%, p(worse) 0.014) and on the pool (33 legs, p 0.07): waits for 100 pool legs; 9+ builds almost nothing. Read before touching the opposition condition under rule 7+. |
| `claude/card-rule14-rule8-2026-11-19.md` | The Card back on rule 8's constants (`CARD_RULE` 14, 19 Nov 2026, Douglas: "let's then group to rule 8"): the value demand on, core leagues, tennis 75%, no two-day groups; the replay's rules 10 to 13 pinned, `rule13` and `span2` variants; the Bets scoreboard on the live rule's own groups (`cardLive`). Read before touching any Card constant or the scoreboard. |
| `claude/card-rules-timeline-2026-11-19.md` | Every Card rule (1 to 13) as a replay variant on the whole pool (`card_replay.RULES`, `rules_table`, the nightly review's `rules_section` with `cardByRule` beside it): the read at 19 Nov (no rule beats live at the gate; few-group core-league rules above expectation, every widening at or under). Read before comparing Card rules or adding a rule 14. |
| `claude/card-rule13-model-only-2026-11-17.md` | The Card on the model alone (`CARD_RULE` 13, 17 Nov 2026, Douglas: "just drop both of those"): `CARD_MODEL_EDGE` None and `CARD_MODEL_OPP_MIN` empty, `rule12Fault` on every Card leg, the `rule12` / `m7value` variants, the pool read at the switch (rule 13 41% of 41 groups, -4%; rule 12 55% of 20, +34%), the month's estimate, what to collect. Read before touching the Card's leg rule or quoting its expected return. |
| `claude/card-integrity-slim-2026-11-17.md` | The integrity check's crash on the record's slim legs (Pistoiese v Coriano, `KeyError: 'date'`), `full_leg`, the staked slips it now reads, `OPP_RULES`, and the review dispatched from the first build after 03:40 UTC. Read before touching `tools/card_integrity.py` or the review's timing. |
| `claude/card-m7cap160-2026-11-18.md` | 60%+ picks priced 1.60-1.90 on the ledger (football 76 legs, 50% v the model's 64%, z -2.45), how rarely the Card or the Daily 2x picks them, `m7cap160` replayed and rejected (behind live on both football-data seasons). Read before touching `CARD_ODDS`. |
| `claude/card-rule13-split-2026-11-17.md` | Rule 13's Card groups split by what rule 12 would have said (`cardRule13Split` in `groupings-record.json`, `rule12Fault` kept on graded legs, a table in the nightly review): how to read it beside the `rule12` replay at the 30 Nov review. |
| `claude/card-decisions-table-2026-11-18.md` | The nightly review's table of every pre-registered Card decision (`card_review_post.decisions_section`): trigger, tonight's standing, waiting / due / fired, who acts; the opposition floor's auto-adopt now goes to Douglas under rule 13. Since 22 Nov 2026 it reads the live rule (`cardLiveRule`): under rule 14, one row rule 14 v `rule13` and `rule12` for 30 Nov, the tennis 75% and core-league rows retired (`claude/card-decisions-rule14-2026-11-22.md`). Read before the 30 Nov review or acting on any Card tripwire. |
| `claude/card-rule12-fault-recheck-2026-11-18.md` | `recheck_card` dropped `rule12Fault`, so no rule 13 group reached the archive with it; now re-asked on each re-check, and archived legs without it read from the frozen leg (`rule12_fault`, `r12` "derived"). The four rule 13 groups to 18 Nov all hold a rule-13-only pick. |
| `claude/list-card-2026-11-17.md` | The Daily List pattern review (lands as quoted in every cut, no cut beats the price) and the List card in the open: List 2x (1.15+, six) else List long (any price, ten), college out, Tested chance from the ledger, own record lines, the 30-group review rule. Read before touching `LIST_KINDS` or claiming a pattern in the list's winners. |
| `claude/card-opp5-list2x-2026-11-16.md` | The Card's rule 12 (football opposition 5.0+, set live as the owner's call before its gate; pool +34% v rule 11's -4%) and the List 2x on paper (`build_list_card`, `cardList`): why the Daily List's success does not carry into groups. Read before touching `CARD_MODEL_OPP_MIN` or the List 2x. |
| `claude/card-comp3-2026-11-16.md` | The two-picks-a-competition cap (`COMP_MAX` 2) on the model's-picks Card: NBA-only nights build nothing (16 Nov: four clear NBA picks, no group); `comp3` added to the football-data replay so the gate has both sides; identical to live on the settled pool so far. Read before touching `COMP_MAX`. |
| `claude/qa-review-2026-11-16.md` | The QA review of the 15-16 Nov work: a frozen Scale group losing a leg (#347), ten releases untagged (#348), half-time scores only from 16 Nov (#349), the checks that passed, MLB K 3 on the grid's edge. Read before the next QA pass. |
| `claude/card-replay-archive-opp-2026-11-16.md` | The pool's football legs before 6 Nov had no opposition price, so every opposition variant (`rule6` family, `m7opp5`, `m7opp9`) faulted on them for missing data; `archive_opp` fills it from the football archive (91% agreement on the 5.0 and 9.0 lines); `m7opp5` on the review's window 12 to 33 legs. Read before reading any opposition variant on the pool. |
| `claude/opposition-price-2026-11-06.md` | The opposition's price as a Card condition: the replay by opposition price band, why football only, the variants for the 30 Nov review. Read before touching `CARD_OPP_MIN` or the price fields on a leg. |
| `claude/retime-championship-seriea-2026-11-20.md` | The first named kick-off misses (Sheffield United v Watford 12:30 v 15:00, Bologna v Udinese 17:00 v 14:00): the Championship joins `AF_RETIME` and Serie A moves there from `AF_UNTIMED`. Read before adding a league to either. |
| `claude/championship-af-spellings-2026-11-20.md` | The first CI read of the Championship under `AF_RETIME`: refused whole on two API-Football spellings (QPR, Sheffield Utd), now aliases; Serie A retimed 13. Read before adding a league to `AF_RETIME`. |
| `claude/kickoff-legs-racing-feed-2026-11-20.md` | The price log's kick-off misses named with both times, OL Lyonnes, and the racing tab's feed note (the free plan: no prices, no results, no tips). Read before adding a league to `AF_RETIME` or changing the racing plan. |
| `claude/horse-racing-2026-11-19.md` | The Horse racing tab on trial (`racing.py`, `renderRacing`): The Racing API, the Benter-style chance (racecard score blended with the bookies' fair chance, starter weights), the tip rule, each-way terms and settlement, the archive and record, what the first build with the secrets must check. Read before touching `racing.py` or the tab. |
| `claude/nominal-date-grading-2026-11-20.md` | Football predictions archived under openfootball's round date (Premier League nominal Saturdays, La Liga and Brazil untimed) never met their result; `score.nearby_results` grades them from the ESPN cache within 3 days, with the guards against double and late grading (46 rows at 20 Nov). Read before touching how `score.py` keys results. |
| `claude/same-date-cache-grading-2026-11-21.md` | `nearby_results` taking a prediction's own date's result from the committed cache (778 September-heavy rows, on quote) and mapping names only over results in the window (the Segunda's Málaga refusal). Read before touching how `score.py` reads `current/`. |
| `claude/round-date-early-copy-grading-2026-11-21.md` | Round-date rows played the day before graded from the copy published before the match day (`earlier_copy`), the Süper Lig's two archive spellings (names mapped per run of dates), `_owned`; 66 more graded, the 27 two-spelling duplicates already on the record. Read before touching how `score.py` picks a prediction's copy. |
| `claude/flags-emoji-caution-2026-11-21.md` | The 82 wider leagues with no flag (`EXTRA_ISO`, `iso_of`, `FLAG_ONLY`), the sport emoji on rows, the caution mark's rule (1.5 SE on 50+ picks, Douglas's call) and the leagues it marked at 21 Nov. Read before touching flags or `unpredictable_leagues`. |
| `claude/duplicate-spellings-graded-once-2026-11-21.md` | 24 matches graded twice under two spellings (Southend / Southend United, East Bengal), now once (`score.drop_duplicates`); Managua and UNAN Managua kept apart (`distinct_names`); the ledger's `duplicate` mark. Read before touching how `score.py` builds its graded rows. |
| `claude/czech-grading-2026-11-20.md` | The Czech First League ungraded from 9 Oct (score.py never read the API-Football fill), `score.lag_results`, what the first CI build should print, League One's 14 Nov games postponed not lost. |
| `claude/bookies-mark-2026-11-20.md` | The Bookies mark: which of a hand review's checks had evidence on the site's own record (the market gap did; table and form, team news and the rest had been tested and rejected), the ledger read by gap band and sport, the fair-chance sources, what to watch. Read before touching `bookGapChip` or proposing a market-gap rule for a card. |
| `claude/af-short-names-2026-11-21.md` | `af_same` reads `odds.ALIASES` so API-Football's short names (QPR, Wolves) price in the one-fixture fallback; Norwich City v Queens Park Rangers the case. Read before adding to `AF_SPELLINGS`. |
| `claude/ledger-postponed-relisted-2026-11-21.md` | Postponed football fixtures re-listed more than 10 days later (Tajikistan's 7 Nov round, Pistoiese v Coriano): `ledger.predictions` marks the earlier copy `movedTo`, the ungraded report counts it apart (`moved`; 418 stale to 227 on 21 Nov). Read before touching how the ledger groups copies. |
| `claude/slip-tracker-2026-11-22.md` | The slip's tracker on the Bets tab (`slipTracker`): profit v the expected line, live and replayed slips, the read at 22 Nov (2 of 15 v 5.2 expected). Read before quoting the slip's record. |
| `claude/round-date-ghosts-multisport-2026-11-22.md` | Saturday's La Liga and Süper Lig games shown on Sunday: copies archived under the round's date before 19 Nov were a second game to `daylist.pinned`; a football copy now gives way to a newer copy of the same pair within `ROUND_DAYS` (3) on another day; the ledger's ghost rows left. The Sport filters taking several sports at once. Read before touching how `daylist.pinned` keys football. |
| `claude/rescheduled-postponed-2026-11-22.md` | Postponed games kept under their first date (Rayo v Athletic, 10 Oct) never came back to the board; `fill_untimed` now moves an older unplayed row when API-Football lists its ordered pair once in the window; leagues outside the untimed and retime lists not covered. Read before touching `fill_untimed`. |
| `claude/rescheduled-postponed-portugal-2026-11-22.md` | Postponed Primeira Liga games (Braga v Gil Vicente, Estoril v Marítimo) moved to API-Football's new date (`AF_RESCHEDULE`, `fill_untimed(postponed_only=True)`); why Portugal alone (no split). Read before adding a league to `AF_RESCHEDULE`. |
| `claude/before-window-retime-2026-11-22.md` | Sunday's Premier League and Brazilian games dropped from the 22 Nov board (openfootball dated them on the Saturday, before the window, so `fill_untimed` never saw them); unplayed rows up to 3 days back now move to API-Football's date when it is in the window. Read before touching `fill_untimed`'s range. |
| `claude/round-date-in-window-results-2026-11-22.md` | La Liga's and the Süper Lig's Friday and Saturday games dated on the round's Sunday sat unscored on the build day (`fill_lagging` filled only rows before the window); now filled up to `AHEAD_DAYS` (3) into it and re-dated (es.1 5, tr.1 4 on 22 Nov). Read before touching `fill_lagging`'s window. |
| `claude/rescheduled-postponed-split-leagues-2026-11-22.md` | Postponed Premiership, Super League and Czech games moved to API-Football's new date (`AF_SPLIT`): the files hold the whole regular season, so a move never passes the file's last fixture; "Dundee Utd" alias. Read before adding a split league to `AF_RESCHEDULE`. |
| `claude/lookback-postponed-2026-11-23.md` | A postponed game dated inside the three-day look-back (Brazil's 21 Nov pair) now takes `fill_untimed`'s rescheduled step when no listing lies within three days of its date; the 23 Nov "rescheduled ...: 0" lines are expected. Read before touching `fill_untimed`'s look-back. |
| `claude/likely-winner-star-2026-11-23.md` | The ⭐ likely winner beside a picked side (`likelyWinner`, `winStar` in `index.html`: Daily List, football under `WIN_FB_MAX` 1.40, no college away / neutral / behind .500, no tennis under 80, no Bookies mark, no context "against") and each day's Most nailed on (`computeNailed`, `nailedLine`); the weekend's evidence in `claude/bet-mistakes-proof-2026-11-23.md`. Display only. Read before touching the star or grading it. |
| `claude/af-normaliser-fallback-2026-11-23.md` | The one-fixture price fallback (`af_same`) reads `sources._norm`: CA Mineiro v Corinthians noFixture beside Atletico-MG; equality only, no cross-club collision on November's board names. Read before adding to `AF_SPELLINGS`. |
| `claude/card-unpriced-near-2026-11-23.md` | The "football Card unpriced" trigger read on legs within 24h of the start (`card_unpriced_near`, `CARD_UNPRICED_NEAR_H`, `football.cardUnpricedNear`): the week to 23 Nov named core legs two and three days out, all priced before kick-off. Read before building a second football price source. |
| `claude/college-tiers-2026-11-23.md` | The college basketball tier chip (Banker / Solid / Caution / Leave out, `sports.college_tier`, `collegeTier` in `index.html`): venue and ESPN's spread for the pick, the record 1 to 23 Nov by tier, `collegeTiers` in `sports-record.json`, what would take it off. Display only. Read before touching the college row marks. |
| `claude/ux-1-foundations-2026-11-23.md` | UX release 1: one segmented control (`.seg`, `aria-pressed`, `.seg--sm`, `.seg--scroll`, the old class names kept beside it), spacing (`--s1`..`--s6`) and type (`--t-xs`..`--t-xl`) tokens, one empty state (`.empty`, `.empty-t`). Read before styling any toggle group or "nothing here yet" box. |
| `claude/markets-pass-spread-2026-11-23.md` | The football markets' first two gate passes (over / under 2.5, the pick's team to score) read for where they come from: the unders alone, three days, no Hill price, the football-data seasons against; the review's line under every pass. Read before offering any football market on the page. |
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
- `sources.py` openfootball + ESPN + football-data.co.uk (`FDX`) + API-Football (`AF`, paid, key `API_FOOTBALL_KEY` in secrets and the cloud env) fetchers, `match_team`, `LIVE_NAMES`, `ESPN_SLUGS`, `topup_current` (since 13 Nov 2026 also for openfootball leagues whose file has stopped scoring, `since=`, filled by `build.fill_lagging`; since 22 Nov 2026 a result also fills its pair's row dated up to `build.AHEAD_DAYS` (3) days into the window, a round's nominal date, re-dated to the day played, `claude/round-date-in-window-results-2026-11-22.md`; since 14 Nov 2026 a league whose file has no fixture dated ahead takes its window from ESPN, `build.exhausted_codes` / `fill_window`; a league still missing 5+ results after that is flagged under Celtic's Law, `build.stale_leagues`; since 18 Nov 2026 a lagging league ESPN cannot score is filled from the API-Football day pool, `AF_LAG`, today the Czech First League; since 19 Nov 2026 leagues openfootball gives no kick-off take API-Football's date and time, `AF_UNTIMED` (La Liga, the Süper Lig, Brazil's Serie A), and leagues whose times are nominal or stale take them when they differ, `AF_RETIME` (the Premier League; the Championship and Serie A since 20 Nov 2026, `claude/retime-championship-seriea-2026-11-20.md`; the Championship's API-Football spellings QPR and Sheffield Utd in `ALIASES`, `claude/championship-af-spellings-2026-11-20.md`), `build.fill_untimed`; since 22 Nov 2026 also unplayed rows up to 3 days before the window, moved only to a date in it, so a nominal Saturday's Sunday games stay on the board, `claude/before-window-retime-2026-11-22.md`; and a postponed game kept under its first date, however old, moves when API-Football lists its ordered pair once in the window, `claude/rescheduled-postponed-2026-11-22.md`; since 22 Nov 2026 (evening) the same for the Primeira Liga alone, `AF_RESCHEDULE` (`fill_untimed(postponed_only=True)`: its own dates and times otherwise kept; Scotland, Greece and Czechia left out, their splits repeat pairs), `claude/rescheduled-postponed-portugal-2026-11-22.md`; since 22 Nov 2026 (night) Scotland, Greece and Czechia too, `AF_SPLIT`: never moved past the file's last regular-season fixture, `fill_untimed(split=True)`, "Dundee Utd" in `ALIASES`, `claude/rescheduled-postponed-split-leagues-2026-11-22.md`; since 23 Nov 2026 a row dated inside the three-day look-back with no listing within three days of its date takes the rescheduled step too, `claude/lookback-postponed-2026-11-23.md`).
- `build.py` fetch, rate, price, write `data.js` / `data.json` / `dashboard.html`, archive `predictions/<date>.json`. Since 26 Oct 2026 the page inlines fixtures plus `__RECORD_SUMMARY__` only; the full football record is `record-data.js`, loaded with `sports-record.js` and `tennis-record.js` when "How it went" opens (`loadRecords` in `index.html`).
- `score.py` grades every archived prediction, writes `record.json`. Has its own copy of the tier ladder. Each row is `verified`, `verified-by-date` or `legacy-unverified` (graded), or `late` / `timing-unverifiable` (not graded, counted apart); see `claude/evaluation-audit.md`. Since 20 Nov 2026 a prediction archived under a round's nominal date is graded from the committed ESPN cache's result of the same pair within `NEAR_DAYS` (3) days (`nearby_results`; never beside a copy on the real date, never a match played earlier unless the price was published before that day; `claude/nominal-date-grading-2026-11-20.md`). Since 21 Nov 2026 a prediction also takes its own date's cached result (September's ESPN-only results had fallen out of `LIVE_LOOKBACK`: 778 graded, on quote) and only results within the window enter the name map (the Segunda had been refused on June's play-offs; `claude/same-date-cache-grading-2026-11-21.md`). Since 21 Nov 2026 a match played before its round date whose last copy was written on the match day is graded from the copy published before that day (`earlier_copy`; La Liga's and the Süper Lig's 8 Nov rounds), names are mapped per run of nearby dates (the Süper Lig's two spellings) and a result a same-day prediction owns under another spelling is never graded twice (`_owned`; `claude/round-date-early-copy-grading-2026-11-21.md`). Since 21 Nov 2026 a match archived under two spellings within `NEAR_DAYS` (same score, both clubs matching both ways, never two clubs the archive shows apart) is graded once (`drop_duplicates`, `distinct_names`; the copy left out is in `record-graded.json` `duplicates`, which the ledger marks `duplicate`; 24 at 21 Nov, `claude/duplicate-spellings-graded-once-2026-11-21.md`). Since 20 Nov 2026 the `sources.AF_LAG` leagues (the Czech First League) are graded from the API-Football day pool the build fills them from (`lag_results`, kept in the settled cache; `claude/czech-grading-2026-11-20.md`).
- `backtest.py` walk-forward backtest.
- `tune.py` constant sweep and calibration refit, behind gates, both measured against the live configuration (`live_baseline()`). `--snapshot FILE` runs either on a frozen snapshot and writes nothing.
- `replay.py` the one walk-forward replay for football, shared by `backtest.py` and `tune.py`, built from the live build's engine functions and batched by date; `validate_split` refuses overlapping or missing seasons. `python3 replay.py --audit` lists what is usable and what is excluded. Since 15 Nov 2026 `tune.load` fills the check season's lagging openfootball fixtures from the committed ESPN cache (`tune.fill_current`, the build's `fill_lagging` rule; `--freeze` passes `fill=False`), so the replays' 2026-27 no longer stops on 20 Sep (`claude/replay-check-season-lag-2026-11-15.md`).
- `tools/capture_predictions.py`, `tools/compare_predictions.py`: reproducible before/after comparison of tune.py and backtest.py across two checkouts on one frozen snapshot (`replay.py --freeze`; `--filter-snapshot` derives an openfootball-only, public-domain copy). Outputs go in `audit-out/` (gitignored).
- `tools/cup_calibration.py` fits the domestic cup calibration from `current/af-cup-replay.json` "rows" (cup replay version 4+); advisory, a human commits the constant.
- `tools/af_team_news.py` fetches API-Football injuries and player minutes (needs the secret: run from a workflow); `tools/team_news_eval.py` backtests them. Output stays in `audit-out/` (API-Football data is not for redistribution).
- `tools/julius_export.py` writes `julius/julius.ai.review.<date>/` (and a `.zip`): every graded prediction as CSVs, Daily List, reserve and each sport separately, with ✓ / ✗ marks, a summary, per-day tallies and calibration bands, for outside review (Julius AI). Reads `record-graded.json`, `tennis-record.json` and `sports.graded_games()`; nothing is regraded. Run it after the daily build: a local `score.py` lacks the paid results and grades about half the football.
- `claude/proposals/` follow-up proposals awaiting a decision (history regeneration, League One prior, cache expansion).
- `tests/` regression tests (stdlib `unittest`): `python3 -m unittest discover -s tests -v`. Run before any push that touches the model, replay, archive or grading.
- `tools/midband_calibration.py` landed v quoted by band and segment on the graded record, strict win test. Advisory.
- `tools/card_replay.py` the Card rebuilt under several leg rules (29 Oct 2026; variants pre-registered for the 30 Nov review, `notennis` and `tennis80` added 9 Nov 2026, `comp3` (three legs from one competition, `groupings.COMP_MAX` 2 live) 10 Nov 2026; the empty-day fillers `fillwide` (the page's own fallback), `fillopp7`, `fillrule5`, `fillshort`, 10 Nov 2026, gated on the filler's own legs, `claude/card-fillers-2026-11-10.md`); `modelcard`, the Model card's rule on the same legs, 10 Nov 2026, `claude/card-modelcard-2026-11-10.md`; since 11 Nov 2026 the variants registered on rule 6 (`RULE6_FAMILY`) are built on the rule 6 Card and paired against live and `rule6`, `claude/card-replay-rule6-family-2026-11-11.md` (`RULE6` pins the constants rule 6 ran with: core leagues only, tennis at 75%, 12 Nov 2026, `claude/card-replay-rule6-tennis-2026-11-12.md`): on the archived pool from 30 Oct 2026 (`POOL_FROM`, every sport, first real price, `--closing` for the last; `--recover` admits legs archived before `priced` existed at their last price, approximate); since 16 Nov 2026 a football pool leg with no opposition price takes the football archive's pre-start average, `archive_opp`, as the pool kept no `opp` before 6 Nov, `claude/card-replay-archive-opp-2026-11-16.md`) and on the football-data-priced archive rows before. Advisory. See `claude/card-pool-replay-2026-11-09.md`.
- `tools/card_integrity.py`, `tools/price_timing.py`, `tools/staking.py`, `tools/card_review_post.py`: the nightly **Card review** (`card-review.yml`, 03:40 UTC, 9 Nov 2026): integrity checks on the Card's record (an `office-backlog` issue for the engineer when they fail; `card-leg-unreplayable` since 9 Nov 2026: every Card leg from 10 Nov must be in the pool at a real price, as only 17 of 59 were from 30 Oct to 8 Nov, `claude/card-pool-coverage-2026-11-09.md`), every replay variant, first v last price (by sport and by the first price's lead on the start; a leg whose last price came after its start is left out, `lastAfterStart`, `claude/price-lead-time-2026-11-09.md`; since 10 Nov 2026 a read only on 50+ legs at day-resampled p <= 0.10, the singles return at first v last price on settled legs, unstarted legs left out, `claude/price-timing-read-2026-11-10.md`) and each UK book (since 13 Nov 2026 also paired against `CARD_BOOK` on the picks both priced, `book_vs`, `claude/card-book-paired-2026-11-13.md`), stake size and drawdown (since 17 Nov 2026 the live bankroll's rate is read from `staking.RATE_FROM`, the 2x-only Card, empty days counted, `claude/card-staking-live-rate-2026-11-17.md`; since 18 Nov 2026 the replay rows are the live rule's own, `cardM7.live` on football-data and the pool replay's live `groupList`, `claude/card-staking-live-rule-2026-11-18.md`). Since 17 Nov 2026 the integrity check reads the record's slim legs through the day's archive (`full_leg`; a slim football leg pending 24h+ had crashed it), watches the Daily 2x and List card as well as the Card (`staked`), and deploy.yml's `card-review-next` dispatches the review from the first build at or after 03:40 UTC when the day has none (the cron had fired near noon every day, `claude/card-integrity-slim-2026-11-17.md`). One `card-review` issue a night (since 23 Nov 2026 the older open ones are closed once it posts, `close_older`), opening since 13 Nov 2026 with the live Card's own output over 14 days and any run of 3+ empty days in bold (`live_days_section`). Since 16 Nov 2026 a later run the same day rewrites that issue's body when its files changed (`posted_issue`, a closing "Refreshed" line), so the Monday football-data read that lands after the morning review shows the same day; it never opens a second issue. Since 12 Nov 2026 it sets each rule 7 variant's pool read beside its football-data seasons (`cardM7Paired`, committed by tune.yml) with a gate verdict per variant (`card_review_post.fd_gate_lines`), and names variants that built nothing apart from the watch list. Advisory; Douglas's objective is consistent returns on the group accumulators, and HQ's planner now ranks the Card's gaps first.
- `tools/card_funnel.py` which Card condition keeps groups off the page (10 Nov 2026, #155): each pool leg's first failing condition by sport (the live `card_fault`), legs kept off by one condition alone, and the days a first 2x / 3x builds live and with one condition relaxed; no results needed, `--recover` for legs before 10 Nov. Printed in the nightly Card review (`card_review_post.funnel_section`). Since 12 Nov 2026 it also counts the legs a missing price alone keeps off (`price_gaps`, started v to come, from 10 Nov; `claude/card-price-gaps-2026-11-12.md`). Since 11 Nov 2026 it reads the live rule (rule 7's `model_fault` keys and reliefs, the kinds in `CARD_BUILD`, every group a day takes; `claude/card-funnel-rule7-2026-11-11.md`: the value demand's relief `m7under5` replays worse, p(worse) 0.97; since 11 Nov 2026 evening the core-league limit has a relief too and costs more groups than the value demand, `m7wide` its variant, `claude/card-m7wide-2026-11-11.md`). Since 17 Nov 2026 it reads rule 12's opposition floor (an `opposition` key and relief, unpriced legs stood in at the floor, missing opposition prices from the football archive; `claude/card-funnel-rule12-2026-11-17.md`). Volume only, advisory. See `claude/card-funnel-2026-11-10.md`.
- `tools/list_accas.py` Daily List picks combined into accumulators (10 Nov 2026): the top N of each day on the graded record, landed v quoted, and on the priced pool at the average price beside the bookmakers' own expectation. Advisory. See `claude/list-accas-2026-11-10.md`.
- `tools/card_legs_history.py` the Card's leg rule and the whole Card replayed over past seasons on football-data.co.uk prices; run by `tune.yml` (fit and check seasons), writes `card-legs-history.json`; `--seasons 2022-23,2023-24,2024-25` adds past seasons, each with the season before as its prior, with the gap and opposition-price tables and losing months (9 Nov 2026, #153); since 11 Nov 2026 also Douglas's mismatch rule (#224, `mismatch` per season, `mismatchPooled` with the issue's gate); since 12 Nov 2026 every rule 7 variant (`cardM7`, `m7under5` and `m7core` included; `comp3` since 16 Nov 2026, `claude/card-comp3-2026-11-16.md`) paired by day against live per season and pooled (`cardM7Paired`, `cardM7Pooled`, `claude/card-m7under5-seasons-2026-11-12.md`). Since 17 Nov 2026 `card_season` builds two-day groups wherever `card_replay.spans` says a variant spans, so the football-data live is the page's Card, as on the pool; `nospan` replays the rollback (`claude/card-legs-history-span-2026-11-17.md`). Advisory (29 Oct 2026). `card-legs-history.yml` (run on any pull request touching the tool, or by hand with a `seasons` input) landed on `main` in #158 and ran the fillers on #184. From 6 to 9 Nov the tool crashed on `KeyError: 'opp'` (#144 shipped half a change), so the Monday report was stale.
- `tools/goals_value.py` value backtest on the goals market (over/under 2.5 v football-data.co.uk prices, fit and check seasons, log loss, calibration by band, value picks' hit, ROI and closing-line value); run by `tune.yml`, writes `goals-value.json`. Advisory (29 Oct 2026).
- `tools/market_gap.py` (20 Nov 2026, Douglas after a hand review: "Can we learn from this method ... for automation") the model against the bookmakers on the results ledger by gap band and sport; behind the page's **Bookies** mark (`bookGapChip` in `index.html`, `BOOK_GAP` 0.10: a row whose model sits 10+ points above the bookmakers' fair chance, from `board_prices` `f`, the football market line or ESPN's moneyline, `mlFair`). First read: 193 marked picks landed 51% v the model's 71% and the bookmakers' 53%. Display only, no model input. `claude/bookies-mark-2026-11-20.md`.
- `tools/market_check.py` model against market on the archive (log loss, landing by the model's lead over the market, draw share, the Multiplier price range). Advisory.
- **At a glance, the week behind** (12 Nov 2026, Douglas): the Daily List's At a glance also scrolls back the last seven days (`daylist.py` `past`, `PAST_DAYS`; `glancePast` in `index.html`), opening on today. Display only.
- **Days at a glance** (10 Nov 2026, Douglas): How it went's Daily List board opens with every list day as one line of the clock, each pick a dot at its start coloured by result (`daysGlance` in `index.html`; starts from `score.py` day rows' `kickoff`, `score_tennis.py` day rows' `start` from `history-tennis/`, sports' `when`). Display only.
- `trustmap.py` where to trust the model (10 Nov 2026): every graded pick at 55%+, every sport, by family and confidence band, landed v quoted with z; `build.py` adds it to `record-data.js` as `trust`, shown in How it went (`trustMap` in `index.html`). A tally, never a fit. See `claude/trust-map-2026-11-10.md`.
- `predictability.py` tests signals beyond the model's confidence (did the pick land?). Advisory only, changes nothing.
- `eurotest.py` cross-competition harness for league strength, writes `europe.json`.
- `nametest.py` guards the club-name matcher. Runs before every deploy.
- `notify.py` one ntfy push per Card group a build creates (new or replacement, `first` stamp this build), run by `deploy.yml` after `groupings.py`; needs the `NTFY_TOPIC` secret, silent without it (29 Oct 2026). Since 10 Nov 2026 also four **briefings** a UK day at Douglas's betting times (`SLOTS`: morning 07:00, lunch 11:00, evening 16:00, night 21:00 UK, sent by the first build at or after each, i.e. the 07:40, 12:00, 17:00 and 22:15 builds; `due_slot` sends only the latest due slot): picks still to start, the strongest of them, the model treble, Edge picks and open Card groups with Hill prices, and from lunch the day's tally; the night push adds the overnight slate to 08:00. Slots sent are kept in `groupings-archive/briefed.json` (committed with the archive) so none sends twice. Since 13 Nov 2026 it also logs each slot's minutes late and any slot a late build skipped (`briefed.json` `log`), shown in the nightly Card review (`card_review_post.briefing_section`): GitHub runs the crons up to two hours late at busy times (`claude/briefing-lateness-2026-11-13.md`). Since 15 Nov 2026 `briefing-watch.yml` (`tools/briefing_watch.py`) checks every 20 minutes around each slot and dispatches a deploy when a slot is 10+ minutes overdue and no build is running, at most two a slot: GitHub had shed the 07:40 cron every day from 10 to 15 Nov (`claude/briefing-watch-2026-11-15.md`). Since 16 Nov 2026 every deploy run ends by dispatching it with `wait=true` (`briefing-next`, `briefing_watch.py --wait`): it sleeps until the next unsent slot, up to 300 minutes ahead, and dispatches the build that sends it, as GitHub shed the watchdog's crons too; the wait acts on the slot's hour (`WAIT_GRACE_MIN` 0, the cron watchdog keeps 10 minutes; `claude/briefing-chain-2026-11-16.md`).
- `backfill.py` walks a past season from ESPN into `history/`.
- Paid prices (9 Nov 2026): The Odds API prices a tennis match only at the Card's bar (`CARD_SPORT_MIN`) or on the Daily List; API-Sports skips `AS_SKIP` (college football and basketball; ESPN prices them free). Since 9 Nov 2026 (Douglas: "make sure all odds are being displayed across all cards") a leg priced by one non-UK source (ESPN's DraftKings line for the NBA, Pinnacle for tennis) that could reach a card (`groupings.books_wanted`) also takes every UK book's price (`bookOdds`) from API-Sports or The Odds API (`books_only`), display only: its average and fair chance are unchanged. Every Card and Model card group has a "Prices by bookmaker" fold (`ogBooks` in `index.html`) and Model card picks show the William Hill price.
- The Daily List at William Hill (10 Nov 2026, Douglas: "a lot of those games ... are not on William Hill"): every list pick without UK books is sent to The Odds API's UK region last in `groupings.price`, US sports included (`LIST_BOOK_KEYS`, one credit a slate, only under `LIST_BOOK_DAY` 9 credits a day). Display only: chips on each list row (Hill price / Not at Hill / No UK price), an "At William Hill" filter, and `groupings-record.json` `listAtBook` (settled list picks priced at Hill, landed and return at Hill's price, from 10 Nov) shown in "How it went" and the nightly Card review. The list still never sees a price. See `claude/list-at-hill-2026-11-10.md`.
- College basketball on the Daily List (11 Nov 2026, Douglas: "move to the college basketball tab unless there is a clear 1.05 or above"): a college basketball list pick shows on the list only at a William Hill price of 1.05+ (`listHillMin` / `listShown` in `index.html`, applied in `listCollect` and the counts); the rest stay on its tab with a left-off line per day. Display only, Douglas's exception to the list taking no bookmaker input; the record still grades them as list picks (whether it should grade only the shown ones is open).
- Odds for every game (11 Nov 2026, Douglas: "get a grip on odds for all games"): every unpriced tennis match and US game is asked of The Odds API (one credit a slate), football legs the bulk prices missed get their own call (`FB_CALLS_MULT`), the Odds API caps follow the account's real allowance (`odds_api_caps`: free-plan caps unless the API reports more than 500 left), and every priced game, every sport, is written to `groupings-data.js` `prices` (`board_prices`) and shown on its row (`priceChip` in `index.html`: Hill, else the average). Display only. `claude/odds-all-games-2026-11-11.md`.
- `context_review.py` the context check on the Card's picks (11 Nov 2026): Claude with web search reads each pick the Card's rule admits (team news, rotation, motivation, table, goals, last five) and returns clear / caution / against with sources; `groupings.CARD_CONTEXT` makes "against" a `card_fault`; verdicts in `groupings-archive/context-<date>.json` and the pool (`context`), graded as `cardContext`; needs `ANTHROPIC_API_KEY`; since 12 Nov 2026 also every Daily List pick at `groupings.CX_LIST_MIN` (75%)+, display only (switched off on 15 Nov 2026 with `DAILY_READS` 25 -> 8 when the API allowance ran out: Card picks only, `claude/api-allowance-2026-11-15.md`) (`cxChip` on rows and Starred, the full read in the slip checker, `contexts` in `groupings-data.js`), in priority order (Card, football, NBA, tennis, college basketball, the rest) within `DAILY_READS` (25) a day, Sonnet for Card picks, football and NBA, Haiku for the rest, sized to the Max plan's $100 monthly API credit. `claude/context-check-2026-11-11.md`. Since 14 Nov 2026 a usage-limit refusal pauses it until the time the API names (`pausedUntil` in `context-ledger.json`, `contextPaused` on the page, bold in the nightly review); the key hit its limit that day, access back 1 Dec (`claude/context-paused-2026-11-14.md`).
- `free_prices.py` the free price sources (11 Nov 2026, Douglas: "find as many free sources as you can"): SportsGameOdds (`SGO_API_KEY`, US leagues, 2,400 games a month), the Betfair Exchange delayed key (`BETFAIR_APP_KEY`, `BETFAIR_USERNAME`, `BETFAIR_PASSWORD`) and Matchbook (`MATCHBOOK_USERNAME`, `MATCHBOOK_PASSWORD`), run after every bookmaker source in `groupings.price`, each filling only unpriced legs and silent without its secrets; exchange prices show as Exch. Sessions never touch disk. On the first builds with keys (11 Nov 2026) Betfair's login is location-blocked from GitHub's runners and SportsGameOdds prices from its consensus line (no per-book prices on the free plan). `claude/free-prices-2026-11-11.md`.
- Football price misses (14 Nov 2026): `groupings.price_football` reports each unpriced football leg's reason (`noFixture`, `kickoff`, `noOdds`, `capped`, `error`) by competition, in the build log ("football unpriced:") and `groupings.json` (`football.miss`, `missComps`). A `noFixture` cluster in one league is a spelling for `LIVE_NAMES`; `noOdds` has no fix. Since 19 Nov 2026 each `noFixture` leg is named ("football noFixture:" in the log, `football.noFixture` in `groupings.json`, up to `NOFIXTURE_KEEP` 12) with the day's fixtures sharing one of its names (`near`). Since 19 Nov 2026 board names API-Football spells another way are matched through `AF_SPELLINGS` (`af_same`; AGF, Inverness CT, STVV, Dux Logroño), and since 21 Nov 2026 API-Football's short forms through `odds.ALIASES` too (QPR, Wolves; `claude/af-short-names-2026-11-21.md`), and since 23 Nov 2026 any pair the build's club normaliser joins (`sources._norm` equal, never a bare city; CA Mineiro / Atletico-MG, `claude/af-normaliser-fallback-2026-11-23.md`), and a leg listed on another day in the window is `moved` ("football moved:", `football.moved`), never priced (`claude/football-nofixture-names-2026-11-19.md`). Since 19 Nov 2026 (second read) six more spellings, and a leg with no board kick-off (La Liga, the Süper Lig and Brazil's Serie A carry none) takes the matched API-Football fixture's (`whenSrc`, "football timed:"); the Card refuses a leg with no start time and `recheck_card` keeps a published leg's (`claude/football-no-kickoff-2026-11-19.md`). Since 19 Nov 2026 the capped one-fixture calls (`FB_CALLS_MULT`) go to Card-reachable legs first, then list and reserve picks (`call_order`, `card_reach`; `claude/football-calls-card-first-2026-11-19.md`). Since 20 Nov 2026 the price reports name a competition with its country (`comp_label`), `card_reach` reads the live Card's league test, and the Card-reachable legs no source priced are counted and named after every source (`card_unpriced`, "football Card unpriced:", `football.cardUnpriced`; `claude/football-card-unpriced-2026-11-20.md`); since 23 Nov 2026 with how many start within 24h, `card_unpriced_near`, the fallback's trigger, `claude/card-unpriced-near-2026-11-23.md`). Since 20 Nov 2026 each `kickoff` miss (both names on API-Football's day, the kick-offs 90+ minutes apart) is named with both times ("football kickoff:", `football.kickoff`), to spot leagues for `sources.AF_RETIME` (`claude/kickoff-legs-racing-feed-2026-11-20.md`).
- `odds.py` football-data.co.uk prices and the value backtest; since 22 Oct 2026 also API-Football prices for every fixture it lists (`af_odds_day`, by date, cached; `match_af` on names and kick-off), display only, never the value tag.
- `groupings.py` the Odds tab (4 Oct 2026; rebuilt 21 Oct): **Double** (two legs, 60%+ together) and **Treble** (three, 50%+), built to land, nothing risky. A leg needs tested rate, model and bookmaker's fair chance all 75%+, the model no more than 5 points above the market, and (football) nothing the Daily List excludes for blindness (`safe_leg`, `CLEAN_WHY`). No group when nothing clears. Today and the next three days (`DAYS_AHEAD`), every published group re-checked on each build: still passing keeps its place, failing is replaced with the reason logged (`recheck`, 21 Oct 2026). At least `MIN_GROUPS` (3) a day: when the strict kinds make fewer, **Wider Double / Wider Treble** fill from the strongest legs: 65%+ priced (`wide_leg`) or unpriced Daily List picks at 75%+, on equal terms (`best_wide`, `WIDE_RULE` 2), labelled Higher risk and graded apart (22 Oct 2026). Every group pays at least `MIN_RETURN` (2.00) combined (Douglas, 22 Oct 2026), so groups land roughly 43-48%. Football and rugby only (`GROUP_SPORTS`), each leg at min(tested rate, model, fair), settled from each sport's full graded history (`claude/odds-groupings.md`), priced by API-Football (football) and ESPN (NFL, MLB, NBA); writes `groupings.json` / `groupings-data.js` in CI before the archive commit, archives each day's first groups to `groupings-archive/` and grades them into `groupings-record.json` (both bot-written). Banker, Steady, Balanced, Stretch are retired but stay in the record. **Multipliers** (24 Oct 2026, `MULT_KINDS`, rule 2 the same evening): a separate section, up to `MULT_PER_DAY` (3) a day, each 3-4 legs from any sport (all sports since that evening; non-`GROUP_SPORTS` legs are `multOnly`, refused by `safe_leg` / `wide_leg`) with the highest combined chance paying 2.8x+; legs 1.30-1.90, the market 60%+, the model no more than 5 points above it; a leg's chance is the bookmakers' fair chance (`as_mult`), the model a veto; built after the other groups, never counted toward `MIN_GROUPS`, graded as `multiplier`. Since 25 Oct 2026 every leg shows its best price and bookmaker (`bestBook`, from `odds.af_parse_odds` `maxBook`), groups carry `bestOdds`, the record grades at average and best prices (`returnedBest`), and `update_closing` writes each archived leg's last pre-kick-off price (`lastOdds`) into `groupings-archive/` for the closing-line tally (`clv`). Since 30 Oct 2026 `archive_pool` also writes the whole priced pool, every sport, to `groupings-archive/pool-<date>.json.gz` (first price as published, last pre-start price; since 9 Nov 2026 a leg first archived as an estimate takes a `priced` block from its first real price, and rows carry `id`, so `tools/card_replay.py` can rebuild any Card rule on the month's real legs at the 30 Nov review; rows before 10 Nov have no `priced` block). Mid-priced legs enter the pool as `multOnly` and cost no per-fixture price call (`claude/multipliers-2026-10-24.md`). Prices never feed a model; they only veto legs.
- `build_tennis.py`, `tune_tennis.py` separate tennis pipeline, `tennis.json` ratings (with each tour's archive boundary). The build applies every ESPN result since the archive ends from `history-tennis/`. `tools/tennis_gap_eval.py` is the evidence. Football must never depend on it.
- `sports.py` NFL, MLB, NBA, rugby: Elo per sport keyed by ESPN team id, `--tune` (by hand, writes `sports.json`), `--daily` (CI). Separate from football and tennis. Since 14 Nov 2026 `score()` also writes `sports-graded.json`, every graded and void pick, merged and never trimmed (`sports-record.json` keeps 14 days of rows for the page).
- `ranktest.py` out-of-time check of the FIFA adjustment (2022-24). Advisory only.
- `rankings.py` FIFA and ATP/WTA world rankings: fetch, and the tested adjustments (FIFA for men's internationals, ATP for men's tennis; WTA shown only); since 15 Nov 2026 FIFA is asked with `rankingType=football` first (the file had sat at 20 Jul 2026 for 118 days) and a release under `FIFA_MIN_SHARE` (80%) of the teams on file, or with another top 20 (`_same_list`), is refused; the dateless overview's own rows, which carry no id, are the release since then. Since 16 Nov 2026 the release is read from the endpoint FIFA's own page calls (`_fifa_schedule`: the newest `FRS_Male_Football_YYYYMMDD` schedule id in the page's embedded `dates`, then `get-rankings?mode=schedule`), as the numeric overview answers nothing after 20 Jul; the first deploy after #337 took the 7 Oct 2026 release (211 teams).
- `periods.py` (16 Nov 2026) football half-time scores for the graded fixtures: read from the API-Football day files already cached (`sources._compact` keeps the half time since 16 Nov), matched by `odds.match_af`, refused when the full time disagrees with the graded result, kept in `periods/football-YYYY-MM.json` (`league|date|home|away` -> [ht, ht, ft, ft, AF id]); no API calls of its own; since 16 Nov 2026 (QA) the look-back is 180 days, `sources._ht_refetch` asks once more for a finished day file written before the half time was kept (`HT_REFETCH_MAX` 25 a process, `HT_BACK_DAYS` 180, scheduled builds only, about 170 calls once), and a fixture tried and not matched is kept in `periods/missed.json` and not tried again; run after `markets.py` in deploy.yml, committed with the archive. The other sports keep points by period in `history-sports/` (`sports._game` `hp`/`ap`, with ESPN's `line`); tennis keeps set scores in its notes. `claude/data-inventory-2026-11-16.md`.
- `ledger.py` (14 Nov 2026) the results ledger, `results-ledger.json.gz`: one row a prediction for every sport (latest pre-start copy, a moved fixture once), its result from the three graded files, and its pre-start price (football archive `market`, the pool's first and last real price with William Hill's, this build's board prices), merged and never trimmed; `summary` (landed, quoted, flat return at the recorded, best and Hill price by sport, list/reserve/board and band), `priceCover`, and the ungraded report (picks 3+ days past the start with no result; `::warning::` on Monday's first build; since 21 Nov 2026 a football fixture re-listed for a later date within `RESCHEDULE_DAYS` (45) is marked `movedTo` and counted apart as `moved`, not chased, `claude/ledger-postponed-relisted-2026-11-21.md`). Runs after `groupings.py` in deploy.yml; nothing on the page reads it. `claude/results-ledger-2026-11-14.md`.
- `markets.py` (14 Nov 2026, Douglas: "go hard on setting this up to track on football") football markets beyond the match winner: both teams to score, over / under 1.5, 2.5 and 3.5, the pick to win and both score, to win and over 2.5, to win to nil, double chance, draw no bet and the pick's team to score, each read from the model's scoreline grid rescaled to the published 1X2 chances (`numbers`, `RULE`); priced from API-Football (one unfiltered `/odds?date=` sweep a date for today and tomorrow, five-hour cache, stands down under `AF_FLOOR` calls left; ids and labels in `LABELS`, probed on the live feed by `tools/markets_probe.py` on the `odds-probe-run` branch); archived to `predictions-markets/<date>.json.gz` (frozen at kick-off) and graded against `record-graded.json` into `markets-record.json` (landed v model and v bookmakers, return at average / best UK / William Hill price, bands, model-v-bookmakers gaps; fixtures before the archive replayed without prices as `replay`). The gate is pre-registered (`GATE_N` 150 priced picks, landed above the bookmakers, best-price return positive, day-resampled p(loss) <= `GATE_P` 0.10; rules `value`, the model 5+ points above the bookmakers, and `all`); a pass is bold in the nightly Card review (`card_review_post.markets_section`); since 23 Nov 2026 with a line under each pass saying where it comes from (each selection, the days, William Hill, the football-data seasons for over / under 2.5, and the chance of a pass by luck across the 20 rules read; `market_pass_lines`, `claude/markets-pass-spread-2026-11-23.md`: the 23 Nov over / under 2.5 pass is the unders alone, which lost on both football-data seasons). No page view, no model input, nothing fitted. Runs after `ledger.py` in deploy.yml. `claude/football-markets-2026-11-14.md`.
- `scale.py` (15 Nov 2026, Douglas: "scaling the odds and even reducing the stake"; `RULE` 2 the same day: "at least 10 games per day ... tiers"; `RULE` 3: "find a winning pattern ... review and optimise") the **Scale** tab, third in the bar after Bets (`renderScale` in `index.html`, the `scale` view): the model's pick to win with a second condition (`SPORTS`): football to win with over 2.5 goals since `RULE` 3 (`FOOTBALL_MARKET` `wo25`, the model's number from `markets.py` with the best UK price on file, named; to win and both score until then and still shown beside it with Hill's price; only fixtures William Hill prices for win and both score), tennis in straight sets, the NBA by 10+, the NFL by 7+, rugby by 8+ (each of those a tally of the record in the pick's confidence band, `band_rate`, never a fit; no price feed yet, so tracked unpriced with the Hill line to look for). Three tiers in order (`TIERS`): Daily List picks, the reserve, and everything else at `FLOOR` (55%+) topping the day up to `TARGET` (10) games (`choose`; a started "else" game is never added); within a tier by the chance the bet lands (`rank`). Groups (`KINDS`, `RULE` 4): a double, threefold, fourfold and fivefold, most likely to land first, frozen at the first leg's start: Daily List picks only (`GROUP_TIERS`) except football, whose legs come from every football fixture William Hill offers at `FLOOR`+ (`GROUP_ANY_TIER`, `with_group_legs`; 15 Nov 2026, Douglas: "scour all football fixtures ... widen the pool"; the replay showed more groups and the same wins, `claude/scale-pool-and-starred-2026-11-15.md`). Archived to `scale-archive/<day>.json` (a pick frozen at its start), graded from `record-graded.json`, `tennis-record.json` and `sports-graded.json` (`scale` / `won` / `lost` / `void`; a group's return only when every leg had a Hill price), written to `scale.json` / `scale.js` (gitignored). `LIVE_FROM` 2026-11-15: earlier days in the glance are replayed once under the current rule (`replay_day`: selection from the pre-start archives only, tallied chances from results dated before the day, football at Hill by proxy, no prices; again only when `RULE` changes) and tallied apart (`before`); a tap on a glance day opens its picks. Display and record only, no model input. College basketball and football are left out (rarely priced in the UK). A pick or group with no real price shows an estimate (15 Nov 2026, Douglas: "If you're missing data on prices, just give an estimate"): `est_price`, the chance's fair price less `EST_MARGIN` (football 15%, the rest 8%), marked "≈" and "estimate" on the page, tallied apart as `estN` / `estRet`, never in `price` or `ret`; an estimate is not a price a bookmaker paid. **Every scale bet** (16 Nov 2026, Douglas: "can we track all of these across all sports"): `scale_ladder.py` tallies every scale bet a final score settles (football's goals, nil and margin bets, tennis sets and games handicaps, each sport's points-handicap ladder) for every graded pick at 55%+, by band, tier and the last 28 days, with the price each needs; written to scale.json as `ladder`, shown as a table per sport (`scLadder`); a tally, never a fit (`claude/scale-every-bet-2026-11-16.md`). Runs after `markets.py` in deploy.yml. `claude/scale-2026-11-15.md`, `claude/scale-tiers-2026-11-15.md`, `claude/scale-strong-legs-2026-11-15.md`, `claude/scale-estimated-prices-2026-11-15.md`.
- `slip.py` (15 Nov 2026, Douglas, after a five-fold at 6.6 and an eleven-fold at 3.0: "a better way of reading and automating picks") **The slip** on the Bets tab (`slipSection` in `index.html`, under the Card): one accumulator a UK day, 3 to 5 legs paying 3x to 6x (`LEGS`, `TARGET`), chosen for expected return, each leg's chance the landed rate its sport and price band have shown on the results ledger (`band_rates`, `RATES_MIN_N` 50, else the pooled band), legs refused from bands returning worse than `LEG_RET_MIN` (-2%), where the model sits more than `ABOVE_MAX` (5 points) above the price's implied chance, or away college picks; offered only when the expected return covers the stake (`EV_MIN`). Archived to `slip-archive/<day>.json` (frozen at the first leg's start), graded from the ledger, the pre-registered gate `GATE_N` 100 / `GATE_P` 0.10, a walk-forward replay over the ledger's past days (`replay`) printed beside the record; since 22 Nov 2026 a tracker under it (`slipTracker`, Douglas: "is there a visual tracker for performance?"): running profit a unit a slip against the expected line, live and replayed slips, All / Live only / Last 14 days, every settled slip kept in `slip.json` (`RECENT_KEEP`, `REPLAY_KEEP`), `claude/slip-tracker-2026-11-22.md`. Reads `results-ledger.json.gz` only; runs after `scale.py` in deploy.yml; writes `slip.json` / `slip.js` (gitignored). Display and record only. `claude/the-slip-2026-11-15.md`.
- `racing.py` (19 Nov 2026, Douglas: horse racing "marked as trial ... but I want it published") the **Horse racing** tab, after Tennis in the sports row (`renderRacing` in `index.html`, the `racing` view): UK and Irish racecards from The Racing API (`RACING_API_USERNAME` / `RACING_API_PASSWORD`, silent and a "not connected" page without them; `--probe` prints the feed's field names), every runner's chance (racecard score of rating, form, trainer's 14 days and freshness, blended with the bookies' fair chance, `ALPHA` / `BETA` starter values refit by hand at `FIT_MIN` graded races), place chance (Harville), the day's tips (22%+, best UK price 8%+ over the chance, fields of 3-16, at most `MAX_TIPS` 6, most likely first, win or each-way, a take price), each race frozen at its off in `predictions-racing/`, graded into `racing-record.json` (results kept so a race is fetched once), written to `racing.js` (gitignored). Boards: Tips (record, a tracker by day, tips by betting window, changes, races left alone), Every race, Racecards, Record (chance v winners, profit, by band, what the model is learning). `TRIAL` puts Trial on the tab. Since 20 Nov 2026 the tab says when the plan sends no prices or results (`feed_of`, `feed_note`; the free plan: racecards only, so no tips and nothing graded). `claude/horse-racing-2026-11-19.md`.
- `score_tennis.py` grades archived tennis picks against the winner, writes `tennis-record.json` / `tennis-record.js` (with `liveBands`, which `build_tennis.accuracy_for` quotes). Only prices published before the match started count.
- `brandassets.py` redraws icon PNGs in Pillow (the one exception to stdlib-only, local use only).

Front end: `index.html` is the template (loads `data.js`). The tab bar (16 Nov 2026, Douglas: option 4 of the nav mock-ups) is two rows inside `#views.almanac`: `.nav-sections` (italic Anton on black: Daily List, Bets, Scale, Starred, How it went, Analysis, Mailer; HQ removed 17 Nov 2026, Douglas: nothing on the site may point to the code or HQ, and README.md is no longer published) and `.nav-sports` (a yellow strip of sport tabs); same buttons and `data-view` as before, so anything reading `#views button` is unchanged. `analysis.html` carries the same two rows as links, and since 17 Nov 2026 opens with About the Sports Almanac (`#about`: the site, the sports, how calls are made and checked, a beta risk warning, and the Daily List, the Card and Scale with risk chips and eight day tiles from `daylist.js`, `groupings-data.js` and `scale.js`). Never link the repository or HQ from a published page. Every page ends with the responsible-gambling banner (`.rg`). **The Mailer** (16 Nov 2026): the last tab, `#mailer` in `index.html` (a view like the others since 16 Nov 2026 evening, same cover and bar; `mailer.html` only forwards to `./#mailer`), signs readers up for the Daily List email; sign-ups go through `almanac_subscribe` to Supabase (the Inbox Innovation project, schema `almanac`, not exposed to the API; rows `pending` until confirmed). Sending (Resend) is not set up yet. Every new sign-up sends Douglas an ntfy push (17 Nov 2026): the trigger `almanac_signup_push` on `almanac.subscribers` calls `almanac.notify_signup()`, which posts through `pg_net` to the topic in Supabase Vault (`almanac_ntfy_topic`, a topic of its own, not `NTFY_TOPIC`); the push names the emails chosen and the running count, never the address, and a failed push never fails the sign-up. The corner flash is a thick 45-degree ribbon quoting Back to the Future (Marty: "Wait a minute, Doc..."), running from the 2026 band to the tab bar, clipped by the red panel (`.meta` overflow hidden); `.meta .flash` overrides `.meta div`. The week ahead panel (10 Nov 2026) was removed the same evening at Douglas's request ("entirely redundant ... too cluttered"); in its place **Coming up** (`weekNext`), one line under the plan naming each later day that already has a plan bet, nothing when none does (`weekDays` stays for it and Today at a glance). Filters (22 Nov 2026, Douglas: "the daily list needs filter by sport", "all sports and daily list need a filter by banding", the starred page "to filter ... see all fixture information and links ... sort by time and other tags"): a confidence band on the Daily List, Football, Tennis and every sport tab (`BANDS`, `bandCtl`, `inBand`, per tab in `localStorage` `bandBy`), a Sport filter on the Daily List (`LIST_SPORTS`, several sports at once since the same day, `toggleSport`; Groups A and B unlabelled while filtered), and on Starred an order (strongest, time, sport, list first), sports (`STAR.sports`, several at once), tag (`STAR_TAGS`), band and Every row open (`STAR`, `rowOpen`, `OPEN_ALL`). Display only. Results on every tab (20-21 Nov 2026, Douglas: "the won or lost tab should be on every tab"): each sport's tab opens with Played today and Played yesterday (`playedSection` / `playedDay`, from `daylist.js` `played`, every started game of the two UK days, list or not, with its result), a started row still on the board shows its result in place of the score (`boardResult`, read from `played` by `playedResults`), and Starred keeps a starred game after its start. Display only. Live scores (10 Nov 2026): a started Daily List pick in a US sport polls ESPN's public scoreboard from the browser once a minute (`liveTick`, `parseScoreboard`), display only and marked unofficial; grading never reads it. Cloudflare Web Analytics beacon in its head (5 Nov 2026, Douglas's Cloudflare account, `spa: true` so tab changes count as views); the dashboard is at dash.cloudflare.com under Web Analytics. Google Tag Manager (`GTM-WP7C2F6B`, 16 Nov 2026, Douglas: "add this to every page and make sure it gets added to all future pages") sits straight after `<head>` in every page (`index.html`, `analysis.html`, `mailer.html`), with Google Analytics 4 loaded directly after it (`G-35788M25WE`, `tools/tag_pages.GA_TAG`, 16 Nov 2026: the GTM container held no Google tag, so GA received nothing; never also add a Google tag for this ID inside GTM, or every view counts twice): **any new page must carry both**; `tests/test_tag_pages.py` fails CI on a page without it, and deploy.yml runs `tools/tag_pages.py _site` before the upload, adding it to any published page that lacks it. Every tab change (and the landing tab) pushes `{event: "tab_view", tab, tab_name, page_path}` to the dataLayer and sends the same as a GA4 `tab_view` event (`gtag("event", ...)`) from the view switch in `index.html`, as tabs change without a page load; GA shows tab names once a custom dimension on `tab_name` exists (Admin, Custom definitions). `dashboard.html` is
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
(refreshed by the build when FIFA publishes), `sports-graded.json`, `results-ledger.json.gz`, `predictions-markets/`, `markets-record.json` (14 Nov 2026), `scale-archive/`, `slip-archive/` (15 Nov 2026), `periods/` (16 Nov 2026), `predictions-racing/`, `racing-record.json` (19 Nov 2026). `history-sports/` and
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
- `office-agents.yml` runs two sprints a day, 06:30 and 18:30 UTC (four from 9 Nov 2026, Douglas: "double output"; back to two on 15 Nov 2026 when the Claude API allowance ran out, `claude/api-allowance-2026-11-15.md`; skips when more than 16 office pull requests exist that day, and idles when `MAX_OPEN` (12) agent pull requests are already open) (Douglas's
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
- **Scheduled build sessions** (9 Nov 2026): a claude.ai scheduled task, "Almanac Card build sessions", runs six times a day (00:34, 04:34, 08:34, 12:34, 16:34, 20:34 London; four times to 9 Nov) in a cloud sandbox with this file as its law: health first, then the `office-backlog` issues titled "Card:" and HQ's backlog, ships tested changes on a branch, merges its own pull requests once Tests and Evaluation pass (Douglas's authorisation), `.github/` and `agents/` changes included since 15 Nov 2026 (he no longer reviews them), and tidies stale pull requests: rebase and merge what still passes and is worth keeping, close what is superseded with a comment saying why. Managed from the Claude app's scheduled tasks, not from this repo.
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
   Since 14 Nov 2026 `release-tags.yml` tags every entry whose header reads
   `## YYYY-MM-DD[-N]: title` on each push to `main` (`tools/release_tags.py`,
   on the merge that added it, never moving a tag), so a missed or impossible
   tag (cloud sessions cannot push tags) is made anyway. Give every entry an id
   of that shape, unique (`tests/test_release_tags.py` fails on a repeat from
   14 Nov 2026 on); a word id (`## 2026-11-16-comp3:`) is tagged too, and an
   entry renumbered later names its commit with `**Shipped in:** <sha>` so its
   tag lands on the merge that shipped it (16 Nov 2026).
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
Douglas's mismatch rule (11 Nov 2026, #224, `claude/mismatch-rule-2026-11-11.md`): a top-quarter home side in form, scoring a lot and conceding little, at home to a bottom-half side with the opposite, 1.15-1.60: 185 legs over five football-data seasons land 74.1% v 72.2% quoted, -1.2% at the best price, ahead in 3 seasons of 5; it does not beat the price. Only the 11-20 games-played band passes (55 legs), and 21+ loses, so no flag; `card_legs_history.py` keeps reporting it (`mismatch`).
Goals market value (29 Oct 2026, `tools/goals_value.py`, `goals-value.json`): over/under 2.5 against football-data.co.uk prices, the market beats the model on log loss both seasons (0.679 v 0.686, 0.655 v 0.675) and 5-point value picks lose at best price (ROI -4.6% / -19.0%) and against the closing line (CLV -3.2% / -3.9%); the model's over number runs low in the 55-65% bands, under picks worst. No goals-market bets without a goals calibration that passes the gates.
Backing sides against habitual losers (22 Oct 2026, from #68): picks against sides that lost over half their games land at or slightly under quote (51.8% v 53.2%, 1,003 picks); the ratings already price it. `claude/tuning-evidence.md`.
Separate attack and defence shrinkage (6 Nov 2026, from #148, `tools/att_def_shrink_eval.py`, `claude/att-def-shrink-2026-11-06.md`): nine pairs, none passes both seasons.
A Championship total-goals scale (29 Oct 2026, from #106, `tools/championship_goals_scale.py`, `claude/championship-goals-scale-2026-10-29.md`): flips sign by season, fails the gates.
Card prices by hour of first pricing (10 Nov 2026, from #215, `claude/price-by-first-hour-2026-11-10.md`): prices lengthen from first to last in both pricing windows, so no earlier push.
Damping the FIFA ranking's big lifts (12 Nov 2026, `tools/fifa_lift_damping.py`, `claude/fifa-lift-damping-2026-11-12.md`): 11 shrink/cap variants, fit 2022-23, check 2023-24; none passes (best on fit, cap 15 points, +0.0000 on check). The Wary mark stays the treatment.
A price cap on the Card's legs (18 Nov 2026, `m7cap160`, `claude/card-m7cap160-2026-11-18.md`): 60%+ picks at 1.60-1.90 land 50% v the model's 64% singly (76 football legs on the ledger), but capping `CARD_ODDS` at 1.60 is behind live on both football-data seasons (pooled -0.15 units a day, p(worse) 0.91, 370 legs) and level on the pool; `m7short` (1.50) fails too.
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
  at 9 Nov). Since 14 Nov 2026 a sport with its own floor (`CARD_SPORT_MIN`,
  tennis 85%) is judged on the legs that floor admits (`atFloor`; every leg
  stays shown, `tripwireAll`): all 41 tennis legs to 14 Nov were under 85%,
  none since (`claude/card-tripwire-at-floor-2026-11-14.md`).
- **The page's empty-day filler (the wider rule) is on watch.** Replayed for
  the first time on 10 Nov (`claude/card-fillers-2026-11-10.md`): 2 of 12
  groups won against 4.14 expected on the pool at first real prices (-54%,
  36 legs); on football-data, football only, at or above quote but under
  the price (2025-26 -0.9%, 2026-27 -11.7%). Pre-registered: when `fillwide`'s own legs reach 100 on the pool
  and its p(worse) against live is 0.70 or more, and the football-data
  `cardFillWide` agrees on both seasons, the next session drops the filler
  (an empty day stays empty; CARD_RULE bump, note, release) without asking.
  `fillrule5` replaces it only if it passes the gate on its own legs.
- **The Card is the model's own picks (CARD_RULE 7, 11 Nov 2026, Douglas: "The
  model rules").** The owner's call, not a gate pass: replay 23 groups +37% v
  rule 6's 10 groups -7% on 69 legs; football-data 2025-26 -8.2%. `rule6`
  replays the old Card nightly; the 30 Nov review reads the two side by side
  (`claude/card-model-rules-2026-11-11.md`).
- **The Card builds the 2x alone (CARD_RULE 8, 11 Nov 2026, Douglas: "Just do
  better on the groups").** `CARD_BUILD`; football-data five seasons +9.6% v
  -3.3% pooled, pool +69% v +37% (p(worse) 0.29, 36 legs). `with3x` replays
  the 3x beside it (`claude/card-2x-only-2026-11-11.md`).
- **The empty-day filler is off (11 Nov 2026, Douglas: "The groups must win
  at all costs. The source of truth is my model.").** `CARD_FILLER` False:
  the filler was the one part chosen on the bookmakers' numbers, pool 2 of 12
  v 4.14 expected (-54%), live 1 of 3. The pre-registered drop was not
  reached; the owner's call. `fillwide` keeps replaying it.
- **The context check vetoes Card picks (CARD_RULE 9, 11 Nov 2026, Douglas:
  "I want this contextual review now").** `context_review.py` reads each Card
  pick with web search; "against" with a source keeps it off. The owner's
  call, untested; graded forward (`cardContext`). Review at 30 "against"
  picks: if they land at or above the model's number, `CARD_CONTEXT = False`; the nightly Card review prints the tally and
  says in bold when this has fired (`card_review_post.context_section`), and
  the next session acts without asking.
- **Tennis on the Card at 85%+ (CARD_RULE 10, 11 Nov 2026, Douglas after
  Casper Ruud lost at 1.22: "Tennis score must go lower", then "Both").** The
  owner's call: graded tennis is on quote from 70% up, the Card's tennis legs
  are not (22 of 40). Tennis rows under 80% show "Under 80" (`tennisWary`).
  `tennis75` replays the old floor; back at 30 legs if it beats live
  (`claude/tennis-floor-85-2026-11-11.md`).
- **The Card takes the wider leagues (CARD_RULE 11, 11 Nov 2026, Douglas on
  Leotar: "This should have been on. So relax all rules that would of said
  otherwise.").** `CARD_CORE_ONLY` False. The owner's call against the
  replay (wider 28 groups +32% v core 12 groups +69%, p(worse) 0.44).
  `m7core` replays core only; back at the 30 Nov review if it beats live at
  p(worse) 0.30 or under (`claude/card-wider-leagues-2026-11-11.md`).
- **Two-day groups (12 Nov 2026, Douglas: "look to the next day ahead to
  combine fixtures").** `CARD_SPAN`: a day with no group tries one with the
  next day's picks, at least one of its own. Pool `span2`: 17 days with a
  group v 15, +31% v +33%, p(worse) 0.49. The owner's call; `CARD_SPAN =
  False` rolls it back (`claude/card-span-2026-11-12.md`).
- **The opposition at 5.0+ on football Card picks (CARD_RULE 12, 16 Nov 2026,
  Douglas on the group record: "what can you do here to actually win", then
  "Yes").** `CARD_MODEL_OPP_MIN` `{"football": 5.0}`, the pre-registered
  `m7opp5`, set live before its pool gate: football-data +17.5% v +9.6% on 450
  legs (p(worse) 0.014), pool +34% v rule 11's -4% (p(worse) 1.00, 14 days).
  `m7noopp` replays rule 11. Beside it the **List card** (`build_list_card`; 17 Nov 2026 in the open on
  the Bets tab, Douglas: "having no cards is awful"): the **List 2x**, the
  Daily List's picks at 1.15+, strongest first, to 2x in six, else the **List
  long**, any price to 2x in ten (`LIST_KINDS`, college sports out,
  `LIST_SPORTS_OFF`), each with a Tested chance from the ledger's band rates
  (`list_tested`), on their own record lines (`cardList`, `cardListLong`);
  staked by Douglas, never pushed; read at 30 settled groups each
  (`claude/card-opp5-list2x-2026-11-16.md`, `claude/list-card-2026-11-17.md`).
- **The Card on the model alone (CARD_RULE 13, 17 Nov 2026, Douglas: "forget
  about comparison to bookies... let's just follow the model", "just drop both
  of those").** `CARD_MODEL_EDGE` None (the value demand off) and
  `CARD_MODEL_OPP_MIN` {} (rule 12's opposition floor, live one day). The
  owner's call against the record: pool rule 13 41 groups 41% won -4%, rule 12
  20 groups 55% +34%, p(worse) 0.09. Every Card leg carries `rule12Fault`, graded into `cardRule13Split` (rule 12 would have built it v a pick only rule 13 admits, `claude/card-rule13-split-2026-11-17.md`; re-asked on every re-check since 18 Nov 2026, `claude/card-rule12-fault-recheck-2026-11-18.md`);
  `rule12` and `m7value` replay beside live; read at 30 Nov or 50 settled
  groups, and put a reversal to Douglas with the numbers, since the switch
  was his (`claude/card-rule13-model-only-2026-11-17.md`).
- **Rule 8's constants again (CARD_RULE 14, 19 Nov 2026, Douglas, shown every
  rule rebuilt on the same days: "let's then group to rule 8").** The value
  demand back on (`CARD_MODEL_EDGE` 0.0), `CARD_CORE_ONLY` True, tennis at
  75% (`CARD_SPORT_MIN`), `CARD_SPAN` False, the 2x alone. Pool at the
  switch: rule 8 8 groups 5 won +64% (24 legs, +14% a leg) v rule 13 46
  groups -4%; p(worse) 0.15 on 24 legs, under the gate. The owner's call on
  a small sample; `rule13` and `span2` replay what was switched off. The
  Bets scoreboard headlines the live rule's own groups (`cardLive`). Read at
  30 Nov beside `rule13`; no rule change before then
  (`claude/card-rule14-rule8-2026-11-19.md`).
- **The Daily 2x (17 Nov 2026, Douglas: "we have to have one card every day ... aiming for above a 2x").** `groupings.daily_group`: one slip a day at the top of the Bets tab, the model's strongest picks at 1.10+ (list, then reserve, then football 65%+, then any sport 65%+; college out), up to eight, until 2x; a short day is still published, marked. Ledger replay 3 Oct to 16 Nov: 14 of 28 won, +22%. Graded as `cardDaily`, tracked by `dailyTracker`; judged at 50 settled slips (`claude/daily-2x-2026-11-17.md`).
- **No Reports page for the weekly PDF.** It adds nothing to the return;
  the Sunday email is the delivery.
- **Opposition 9+ (rule 6) stays**: the one condition that holds in every
  season (`claude/card-seasons-2026-11-09.md`). Under rule 7+ it is not read
  (`model_fault`); `CARD_MODEL_OPP_MIN` carries it for the pre-registered
  `m7opp9` / `m7opp5` (15 Nov 2026): if either passes the gate on the
  football-data seasons and the pool, the next session sets it live with a
  `CARD_RULE` bump, without asking (`claude/card-m7opp-2026-11-15.md`).

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
- The green **Edge** flag (10 Nov 2026, Douglas): football fixtures in football-data's leagues where the model's pick is the bookmakers' favourite at 1.15-1.90, the bookmakers 60%+, the opposition 9+ (4/1, decimal 5.0, from 11 Nov 2026 at Douglas's call: `EDGE_OPP_MIN`, `EDGE_RULE` 2, record split `byRule`, `claude/edge-floor-2026-11-11.md`; the five-season figures are for 9+) and the model no more than 5 points above the market (`groupings.edge_flag`, computed in `build.py`, archived as `edge`, shown by `edgeFlag` in `index.html`; the football board's Show control has **Edge only**, and each day's header counts the flags). The Bets tab's **Edge picks** section (`edgeSection`) lists the day's flagged fixtures with the Edge double and the whole-day slip, priced, beside their five-season test (`claude/edge-accas-2026-11-10.md`; `build.edge_tested` reads `card-legs-history.json` `edgeAccas`). It ends with the **Tracker** (21 Nov 2026, `edgeTracker`): running profit at the best and average price, one unit a pick, All time / Last 14 days, a day strip and each day's picks, and the record split by the opponent's price (9.0+ v 5.0-9.0), from `record.json` `edge.days`. Display only. Graded by `score.py` (`edge_record` in `record.json`: live from 10 Nov, replayed on archived prices before; 27 of 34 at 10 Nov, -2.1% average, +0.5% best), quoted on the page and in the nightly review. Every other sport tested on the pool (`tools/edge_sports.py`, 10 Nov 2026): none passes the gate (100+ legs, landed above the bookmakers, best-price return positive, p(loss) <= 0.30); the nightly Card review prints each sport's line from 11 Nov, and a sport that passes gets the flag in a release.
- Market input to the Daily List: on 909 archived priced fixtures the market beats the model on log loss (0.979 v 1.013) and picks the model rates 5+ points above the market land at the market's rate (`tools/market_check.py`). The list takes no bookmaker input by Douglas's standing decision; the evidence is there if he wants to revisit it.
- Past cup rows in the record carry the untempered confidence (fixed for new rows 24 Oct 2026). Whether to regrade their bands is Douglas's call.
- No dark theme. The flag sprite covers every country code in `engine.LEAGUES`
  (126 symbols since 21 Nov 2026: the API-Football-only countries through `engine.EXTRA_ISO` / `iso_of`, `FLAG_ONLY` keeping their clubs out of continental cups as before); a new country needs a symbol and an `EXTRA_ISO` entry, and `tests/test_flags.py` fails CI until it has both. Rows end their league or sport name with the sport's emoji (`sportEmoji`), and a football league with 50+ graded picks landing 1.5+ standard errors under the model carries a ⚠️ with its record on hover (`build.unpredictable_leagues`, `cautionMark`; Douglas chose 1.5 over 2, 21 Nov 2026; `claude/flags-emoji-caution-2026-11-21.md`).

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
