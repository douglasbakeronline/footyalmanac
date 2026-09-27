# Football Almanac

A daily-refreshed football prediction site. It rates every club from completed
results, prices each upcoming fixture as home / draw / away with a Dixon-Coles
adjusted Poisson model, ranks the slate so the most one-sided games sit at the
top, and grades itself publicly against what actually happened.

- Live: https://douglasbakeronline.github.io/footyalmanac/
- Repo: https://github.com/douglasbakeronline/footyalmanac (public)
- Owner: Douglas. At least one other collaborator has push access.

The point of the site is honest confidence: surface the genuinely predictable
games, say plainly when a call is weak, and never inflate a number to look good.

## Read before non-trivial work

`claude/` holds dated handover notes. Read the one that matches the task.

| File | Covers |
|---|---|
| `claude/data-integrity.md` | The two-source name-matching failures, the season-so-far cache, `nametest.py`, matching rules. Read before touching `sources.py` or anything that looks up a club. |
| `claude/tuning-evidence.md` | What every constant is worth, the calibration curve, what was tested and rejected, the tuning rules. Read before touching `engine.py` constants, `tune.py` or `calibration.json`. |
| `claude/coverage-expansion.md` | Why 61 competitions come from ESPN, `backfill.py`, which leagues still lack a prior season. |
| `claude/results-review-board.md` | The "How it went" board, tier ladder, live calibration. |
| `claude/brand-identity.md` | Mark, type, colour tokens with contrast ratios, sticky bar, assets. |

**The code on `main` is the source of truth.** The notes are snapshots from
September 2026 and some have been overtaken (see "Known drift" below). Where a
note and the code disagree, trust the code and tell Douglas the note is stale.

## Files

Pipeline, all Python 3.12, **standard library only, no pip, no requirements.txt**:

- `engine.py` ratings and match model. Every number on a row comes from here.
- `sources.py` openfootball + ESPN fetchers, `match_team`, `LIVE_NAMES`, `ESPN_SLUGS`, `topup_current`.
- `build.py` fetch, rate, price, write `data.js` / `data.json` / `dashboard.html`, archive `predictions/<date>.json`.
- `score.py` grades every archived prediction, writes `record.json`. Has its own copy of the tier ladder.
- `backtest.py` walk-forward backtest.
- `tune.py` constant sweep and calibration refit, behind gates.
- `eurotest.py` cross-competition harness for league strength, writes `europe.json`.
- `nametest.py` guards the club-name matcher. Runs before every deploy.
- `backfill.py` walks a past season from ESPN into `history/`.
- `odds.py` football-data.co.uk prices and the value backtest.
- `build_tennis.py`, `tune_tennis.py` separate tennis pipeline, `tennis.json` ratings. Football must never depend on it.
- `brandassets.py` redraws icon PNGs in Pillow (the one exception to stdlib-only, local use only).

Front end: `index.html` is the template (loads `data.js`). `dashboard.html` is
the self-contained build output and is what gets published as the site's
index. Edit `index.html`, never `dashboard.html`.

Config the model reads: `calibration.json` (auto-refitted weekly),
`europe.json` (structural, refitted by hand only), `adjustments.json`
(deliberately empty, see rules).

Written by the bot, never hand-edit: `predictions/`, `current/`,
`record.json`, `tennis-data.js`, `tuning-report.json`. `history/` is written
by `backfill.py` and committed by hand.

## Commands

```
python3 nametest.py                          # must pass before any push
python3 build.py --days 5 --top 50           # what CI runs
python3 build.py --days 2 --no-topup --no-odds   # fast local check
python3 score.py                             # regrade, rewrite record.json
python3 backtest.py --season 2025-26 --prior 2024-25
python3 tune.py --report                     # advisory sweep, changes nothing
python3 tune.py --fit --dry-run
python3 eurotest.py --report
python3 backfill.py --probe                  # which ESPN slugs answer
python3 odds.py --report
```

Open `dashboard.html` straight off disk to check the page.

## Automation

- `deploy.yml` runs daily at 05:15 UTC, on manual dispatch, **and on every
  push to `main`**. Order: `nametest.py`, build, refuse-if-empty, `score.py`,
  tennis, commit the archive back to `main`, rebuild, publish to Pages.
- `tune.yml` runs Mondays 04:40 UTC: `tune.py --fit` (auto-applies only if it
  passes all gates), then `--report` and `eurotest.py --report` as advisory
  output for a human.
- The bot commits to `main` every day. Pull before starting and before
  pushing. If a conflict lands on a bot-written file, take the remote copy.

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
  abbreviates (*Bayern Munich*). Cup ties are rated against the club's
  domestic league via `domestic_of`.

## Tested and rejected, don't reopen without new evidence

Separate home/away ratings (+0.0124 log loss), rest days (no effect), ten free
per-band temperatures (overfit), heavier recent-form weighting, tuning on the
live record.

## Open items

- 45 competitions still need a prior season: `backfill.py --probe`, prune dead
  slugs in `sources.ESPN_SLUGS`, then `--season 2025` and `--season 2025-26`,
  commit `history/`. The ESPN slugs were written without network access to
  ESPN and are unverified; smaller European ones are least trustworthy.
- Whether unrated rows should compete for the top of the board on raw
  confidence. Currently they do, deliberately. Douglas's call.
- Tier ladder duplication (rule 7) could be collapsed to one definition.
- "Lean or better only" filter on the fixtures board, not built.
- No dark theme. Flag sprite covers 13 countries.

## Known drift

- The notes say the 74 league strength coefficients are hand-set and
  untested. `eurotest.py` and a fitted `europe.json` now exist. Check how
  `engine.py` consumes it before treating the coefficients as untested.
- `claude/brand-identity.md` describes a three-bar mark with Anton;
  `brandassets.py` on `main` still describes a slab-serif A in Bevan. Confirm
  which identity is live before touching branding.
- `README.md` still says twenty competitions and older backtest figures.

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
