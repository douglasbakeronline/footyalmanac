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

The front page is the **Daily List**: the most likely results across every
sport, one ranking per day, strongest tested hit rate first. One rule for
all sports: a pick qualifies only if calls at its level landed ≥80% in
testing on games never tuned on (`sports.list_threshold`), plus football's
blind-spot exclusions and no draws, no tennis qualifying rounds, and a
ranked international must clear its bar before the FIFA ranking too. Raised
from 75% on 29 Sep 2026 at Douglas's request (`claude/ranking-review.md`). Every
row shows its tested rate. See `claude/multi-sport.md`. It is the
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
  List is the front page; no bookmaker input into any model; no manual data
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
| `claude/daily-list.md` | The Daily List rule and its evidence, what does and doesn't predict a pick landing (`predictability.py`), the ESPN slug audit, the US Eastern/UTC day bug. Read before touching the list, `LIST_MIN`, or ESPN fetching. |
| `claude/world-rankings.md` | Which world rankings are in the model, the tests behind them, sources and name mapping. Read before touching `rankings.py`. |
| `claude/ranking-review.md` | Burundi v Algeria: the FIFA adjustment re-checked on 2022-24, why ranked internationals need 65%, the goals line fix, the open question on big lifts. |
| `claude/multi-sport.md` | NFL, baseball, basketball, rugby: the model, its evidence, which sports earn a Daily List place and why. Read before touching `sports.py` or `sports.json`. |
| `claude/tennis-record.md` | How tennis picks are archived and graded, the publish-before-start rule, the seed from git history. Read before touching `build_tennis.py` or `score_tennis.py`. |
| `claude/data-integrity.md` | The two-source name-matching failures, the season-so-far cache, `nametest.py`, matching rules. Read before touching `sources.py` or anything that looks up a club. |
| `claude/tuning-evidence.md` | What every constant is worth, the calibration curve, what was tested and rejected, the tuning rules. Read before touching `engine.py` constants, `tune.py` or `calibration.json`. |
| `claude/coverage-expansion.md` | Why 61 competitions come from ESPN, `backfill.py`, which leagues still lack a prior season. |
| `claude/results-review-board.md` | The "How it went" board, tier ladder, live calibration. |
| `claude/data-expansion-plan.md` | API-Football Pro (bought 30 Sep 2026), where the key lives, the order of work: coverage, lower leagues, replay test, U21, UFC, boxing. Read before any paid-data or new-sport work. |
| `claude/brand-identity.md` | Mark, type, colour tokens with contrast ratios, sticky bar, assets. |

**The code on `main` is the source of truth.** The notes are snapshots from
September 2026 and some have been overtaken (see "Known drift" below). Where a
note and the code disagree, trust the code and tell Douglas the note is stale.

## Files

Pipeline, all Python 3.12, **standard library only, no pip, no requirements.txt**:

- `engine.py` ratings and match model. Every number on a row comes from here.
- `sources.py` openfootball + ESPN + football-data.co.uk (`FDX`) + API-Football (`AF`, paid, key `API_FOOTBALL_KEY` in secrets and the cloud env) fetchers, `match_team`, `LIVE_NAMES`, `ESPN_SLUGS`, `topup_current`.
- `build.py` fetch, rate, price, write `data.js` / `data.json` / `dashboard.html`, archive `predictions/<date>.json`.
- `score.py` grades every archived prediction, writes `record.json`. Has its own copy of the tier ladder.
- `backtest.py` walk-forward backtest.
- `tune.py` constant sweep and calibration refit, behind gates.
- `predictability.py` tests signals beyond the model's confidence (did the pick land?). Advisory only, changes nothing.
- `eurotest.py` cross-competition harness for league strength, writes `europe.json`.
- `nametest.py` guards the club-name matcher. Runs before every deploy.
- `backfill.py` walks a past season from ESPN into `history/`.
- `odds.py` football-data.co.uk prices and the value backtest.
- `build_tennis.py`, `tune_tennis.py` separate tennis pipeline, `tennis.json` ratings. Football must never depend on it.
- `sports.py` NFL, MLB, NBA, rugby: Elo per sport keyed by ESPN team id, `--tune` (by hand, writes `sports.json`), `--daily` (CI). Separate from football and tennis.
- `ranktest.py` out-of-time check of the FIFA adjustment (2022-24). Advisory only.
- `rankings.py` FIFA and ATP/WTA world rankings: fetch, and the tested adjustments (FIFA for men's internationals, ATP for men's tennis; WTA shown only).
- `score_tennis.py` grades archived tennis picks against the winner, writes `tennis-record.json` / `tennis-record.js`. Only prices published before the match started count.
- `brandassets.py` redraws icon PNGs in Pillow (the one exception to stdlib-only, local use only).

Front end: `index.html` is the template (loads `data.js`). `dashboard.html` is
the self-contained build output and is what gets published as the site's
index. Edit `index.html`, never `dashboard.html`.

Config the model reads: `calibration.json` (auto-refitted weekly),
`europe.json` (structural, refitted by hand only), `adjustments.json`
(deliberately empty, see rules).

`RELEASES.md` is the release log; every release gets an entry and a tag.
`README.md` is the public overview (rewritten 28 Sep 2026, current).
`AGENTS.md` is the guide for any AI agent; `.github/copilot-instructions.md`
points Copilot at it. `.gitignore` keeps `data.js`, `data.json` and caches out.

Written by the bot, never hand-edit: `predictions/`, `current/`,
`record.json`, `tennis-data.js`, `tuning-report.json`, `predictions-tennis/`,
`tennis-record.json`, `tennis-record.js`, `predictions-sports/`,
`sports-data.js`, `sports-record.json`, `sports-record.js`, `fifa-rankings.json`
(refreshed by the build when FIFA publishes). `history-sports/`
is topped up by CI; its first walk was committed by hand. `history/` is written
by `backfill.py` and committed by hand.

## Commands

```
python3 nametest.py                          # must pass before any push
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

- `deploy.yml` runs daily at 05:15 UTC, on manual dispatch, **and on every
  push to `main`**. Order: `nametest.py`, build, refuse-if-empty, `score.py`,
  tennis build, `score_tennis.py`, `sports.py --daily` (both allowed to fail),
  commit the archives back
  to `main`, rebuild, publish to Pages.
- `tune.yml` runs Mondays 04:40 UTC: `tune.py --fit` (auto-applies only if it
  passes all gates), then `--report` and `eurotest.py --report` as advisory
  output for a human.
- `office-agents.yml` runs daily at 06:30 UTC (Douglas's instruction, 2 Oct
  2026: fully automated, he reviews when he chooses). `agents/pick_task.py`
  picks the most important objective that is behind and the owning office
  agent works on it, then `agents/open_pr.sh` checks it and opens a pull
  request labelled `office-agent`. At most two agent pull requests stay
  open, and each objective rests for 7 days. See `claude/office-agents.md`.
- `office-merge.yml` runs daily at 21:00 UTC. `agents/merge_gate.py` merges
  only pull requests labelled `auto-merge-ok` and `checks-passed`, at least
  12 hours old, with no `hold` or `needs-owner` label and no protected files.
  It then tags `release-YYYY-MM-DD[-n]` and dispatches `deploy.yml`.
  Visual changes, failed gates and model changes the agent is unsure of
  always wait for Douglas.
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
   auto-applies. Everything else is advisory until a human commits it.
6. **A name mismatch or a missing current season must fail loudly.** A wrong
   match is worse than a missed one. When a "not rated" row turns out to be a
   spelling, fix it and add the spelling to `LIVE_NAMES`. In normalisation,
   aliases before city exonyms, and founding years are stripped only at the
   last-resort step, never in the normalised form.
7. **The tier ladder lives in two places**: `TIERS` in `index.html` and in
   `score.py`. Change one, change the other.
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
- **Tiers**: Strong ≥70%, Firm ≥62%, Lean ≥55%, No read below.
- **Calibration**: `T = 1.075 − 0.45 × (confidence − 0.45)` from
  `calibration.json`, replacing the old flat temperature of 1.15.
- **Sources**: openfootball spells clubs in full (*FC Bayern München*), ESPN
  abbreviates (*Bayern Munich*). football-data.co.uk's extra-league files
  are the sole source for Poland, Switzerland, Romania, Finland and Ireland
  (`sources.FDX`), history and fixtures both, so each league has one spelling. Cup ties are rated against the club's
  domestic league via `domestic_of`.

## Tested and rejected, don't reopen without new evidence

Separate home/away ratings (+0.0124 log loss), rest days (no effect), ten free
per-band temperatures (overfit), heavier recent-form weighting, tuning on the
live record. Form re-tested 29 Sep 2026 at Douglas's request, calibrated, both
seasons: a form-led model (form cap 0.30-0.50, or current season taking over
after 3 games) is +0.005 log loss worse on both; FORM_MAX 0.10 a wash. What
passed was this season counting sooner (SHRINK_FULL_SEASON 6 -> 4, shipped).
Bottom-10%-away and weak-goal-record penalties (30 Sep 2026): worse at every
strength, the ratings already carry it. See `claude/tuning-evidence.md`.

## Open items

- Slugs were audited against ESPN on 27 Sep 2026 and 14 leagues backfilled
  (see `claude/daily-list.md`). ESPN does not carry Poland, Croatia, Serbia,
  Ukraine, Hungary, Korea, the UAE, the 3. Liga, Liga Portugal 2 or most small
  European leagues. Covering them needs a second free source, not a slug.
- The backfilled leagues have no walk-forward of their own yet (needs a
  second prior season).
- Whether unrated rows should compete for the top of the board on raw
  confidence. Currently they do, deliberately. Douglas's call.
- Tier ladder duplication (rule 7) could be collapsed to one definition.
- "Lean or better only" filter on the fixtures board, not built.
- No dark theme. The flag sprite covers every country code in `engine.LEAGUES`
  (84 symbols); a new league with a new `iso` needs a symbol added.

- 227 wider leagues from API-Football (`af-leagues.json`, `engine.AF_EXTRA`): tier 2, own bands, list bar 75% (`build.LIST_MIN_AFX`), out of the calibration fit. National League, North and South also come from `AF` now.
- English step 3 (four leagues, `sources.AF`) is on the board and reserve, never the Daily List: replayed below the bar (`build.NO_LIST`).
- The Daily List fills to 20 a day with a **reserve** (below the bar, Firm
  62%+, clean), flagged per pipeline as `reserve` and graded as its own group
  (`record.json` / `tennis-record.json` / `sports-record.json` "reserve").
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
