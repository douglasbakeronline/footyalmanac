# Sports Almanac (repo: footyalmanac)

A multi-sport prediction site. Six times a day it collects the world's fixtures,
rates every team and player it has data for, gives each game a probability,
publishes the strongest calls as the **Daily List**, and grades every published
call against what happened. Nothing is graded unless it was published before
the start.

- **Live site:** https://douglasbakeronline.github.io/footyalmanac/
- **This repo:** the models, the build and the site (Python 3.12, standard library only)
- **Sister repo:** [footyalmanac-hq](https://github.com/douglasbakeronline/footyalmanac-hq), the AI agent office that reports on this one (stand-ups, KPIs, daily briefing, slips). It only reads this site's published files.
- **Owner:** Douglas Baker. UK English, no em dashes, direct.

> **Picking this up as an AI?** Read this file, then [`CLAUDE.md`](CLAUDE.md)
> (the rulebook) and [`AGENTS.md`](AGENTS.md) (how to ship). Then read the
> dated note in [`claude/`](claude/) that matches your task, and the top of
> [`RELEASES.md`](RELEASES.md) for what changed last. **The code on `main` is
> the source of truth.** Where a note disagrees with it, trust the code and
> say the note is stale.

---

## The objective, stated honestly

The owner's goal is to **surface results you can rely on from every daily
sports fixture in the world**. No model can guarantee a sporting result. Even
the best calls here miss about one time in five, and a higher bar doesn't
remove that. So the objective is made measurable, and every change is judged
on it:

1. **Coverage:** as many of the world's daily fixtures as possible are on the
   board with an honest probability. A fixture the model can't rate is flagged,
   never guessed.
2. **Reliability of the Daily List:** every List pick comes from a level whose
   calls landed **at least 80%** in testing, on games the model was never
   tuned on. The live record must keep landing close to what it quotes.
3. **Honesty:** a quoted 80% should land about 80% of the time, on the live
   record, in every band and every sport. A gap between quoted and landed is
   a bug, whichever direction it goes.

"Guaranteed" in this project means **verified in advance and graded in
public**, never "certain". Any change that raises the headline hit rate by
hiding misses, grading late picks or fitting on the live record breaks the
project. Read `CLAUDE.md` rule 1 before anything else.

### Where it stands (export of 19 Oct 2026, `tools/julius_export.py`)

| Measure | Now | Target |
|---|---|---|
| Graded calls, all sports | 6,586 (66.9% won, quoted 66.2%) | honest in every band |
| Competitions graded | 358 | every fixture with data |
| Daily List, since 28 Sep | 170 of 214 won (79.4%), quoted 82.1% | at least 80%, quoted equals landed |
| Daily List, since 6 Oct | 112 of 146 (76.7%), 120.1 expected | the same |
| Reserve (62% to the List bar) | 303 of 449 (67.5%), quoted 68.5% | honest |

By sport on the List since 6 Oct (won / picks, expected from quotes): football
48 / 59 (48.9), college football 30 / 41 (33.6), tennis 25 / 36 (29.4), rugby
8 / 8 (6.6), NFL 1 / 2 (1.6). Live tennis and college football fell short of
their quotes, which is why both were changed (see Recent decisions). Regenerate
these numbers before relying on them: they go stale daily.

---

## How a day works

```
fixtures (ESPN, API-Football, openfootball, football-data.co.uk)
   -> ratings (football Dixon-Coles Poisson; Elo for tennis and other sports)
   -> calibrated probability per game
   -> tested rate: how often calls at that level landed on held-out games
   -> Daily List (clears its sport's bar) / reserve (62% up to the bar) / board
   -> archived before the start (predictions*/)
   -> graded after the result (record*.json) -> "How it went" and Analysis
   -> Odds tab: five-leg groups priced by bookmakers, graded the same way
```

`deploy.yml` runs this at 00:10, 05:15, 12:00, 17:00, 19:30 and 22:15 UTC, on
manual dispatch and on every push to `main`. Results update on those rebuilds,
not live.

## Sports and their Daily List bars

One rule for every sport: the lowest confidence whose calls landed at least
80% in every held-out window (at least 30 games each). The bar differs by sport
because the evidence does.

| Sport | Model | List bar | Notes |
|---|---|---|---|
| Football leagues (main set) | Dixon-Coles Poisson + calibration curve | 80% | no draw picks; blind-spot fixtures (Celtic's Law) excluded |
| Wider API-Football leagues (227) | same, own bands | 75% (`build.LIST_MIN_AFX`) | tier 2, kept out of the calibration fit |
| Men's internationals | own ratings + FIFA ranking | 75%, and 75% before the ranking | |
| English step 3, domestic cups, U21, new leagues | | not on the List | board and reserve only, until a replay passes |
| Tennis (ATP, WTA) | surface-blended Elo + ATP ranking | **off the List** (`build_tennis.LIST_ON`) | since 15 Oct 2026; main-draw calls from 62% go to the reserve |
| College football | Elo | 80% (`sports.LIST_FLOOR`) | backtest found 70%; own bands below 80% missed |
| NFL, WNBA | Elo | 80% | |
| NBA | Elo | 75% | |
| Rugby union, college basketball | Elo | 70% | watch: their 70-75% bands are weaker in testing |
| Baseball (MLB), rugby league (NRL) | Elo | not on the List | strongest calls don't land often enough |
| Ice hockey (NHL) | Elo | unpublished | doesn't beat backing the home side |

The sport bars live in `sports.json` (written by `sports.py --tune`), raised by
`sports.LIST_FLOOR`; football's are in `build.LIST_MIN`; tennis's are in
`build_tennis.LIST_MIN`. Every List pick is shown, with no cap. Rows display a
tested rate; note that it's the cumulative band (all calls at or above that
level), which can read higher than the pick's own 5-point band.

## The Odds tab (`groupings.py`)

Three bands of five-leg groups a day (Steady 2.5-4, Balanced 4-7, Stretch
7-14), plus alternatives, archived each morning and graded in
`groupings-record.json`.

- **Prices:** API-Football (football), ESPN (NFL, MLB, NBA, NHL, college
  sports, WNBA, some soccer) and The Odds API (tennis, rugby; free plan, capped
  at 15 credits a day and 480 a month, each sport cached for 4 hours in
  `.afcache`).
- **Honest chances (since 19 Oct 2026):** a leg's chance is the lower of its
  tested rate and the bookmaker's fair chance (price less the book's margin).
  Legs without a bookmaker price are never grouped. From 4 to 18 Oct, 8 of 48
  groups won against 15.9 expected, because tested rates overstated legs by
  about 7 points and the old rule picked exactly the legs where the model and
  the bookmakers disagreed most.
- **Prices never feed a model or the Daily List.** At bookmaker prices five-leg
  groups lose on average; the tab says so.

## Data sources and secrets

| Source | Used for | Secret |
|---|---|---|
| ESPN public scoreboards | fixtures, results, US sports, tennis results, some prices | none |
| API-Football (paid Pro, since 30 Sep 2026) | 227 wider leagues, cups, step 3, football prices | `API_FOOTBALL_KEY` |
| openfootball | football history (public domain) | none |
| football-data.co.uk | Poland, Switzerland, Romania, Finland, Ireland; history | none |
| FIFA ranking API, ESPN tennis rankings | ranking adjustments | none |
| Jeff Sackmann tennis archive | tennis history (frozen at 1-2 Jun 2026; topped up from ESPN in `history-tennis/`) | none |
| The Odds API | Odds tab prices for tennis and rugby | `ODDS_API_KEY` |

Other secrets: `OFFICE_APP_ID` / `OFFICE_APP_KEY` (the office GitHub App that
pushes the archive and opens agent PRs), `CLAUDE_CODE_OAUTH_TOKEN` (office
agents), `EVAL_DATA_READ` / `EVAL_DATA_WRITE` (private evaluation snapshots).
`BOXING_DATA_KEY` and `BIGBALLS_KEY` are set but no code uses them yet.
API allowance is precious: shared fetching and persistent caches (`.afcache`,
`current/`) exist so each build spends as little as possible. Keep it that way.

## Repo map

| Area | Files |
|---|---|
| Football model and build | `engine.py`, `sources.py`, `build.py`, `calibration.json`, `europe.json`, `international*.json`, `af-leagues.json` |
| Tennis | `build_tennis.py`, `score_tennis.py`, `tune_tennis.py`, `tennis.json`, `history-tennis/` |
| Other sports | `sports.py`, `sports.json`, `history-sports/` |
| Rankings | `rankings.py`, `fifa-rankings.json` |
| Daily List and coverage | `daylist.py` (what each day's List was chosen from, and gaps) |
| Grading | `score.py`, `score_tennis.py`, `sports.py --daily`; outputs `record*.json`, `tennis-record.*`, `sports-record.*` |
| Odds tab | `groupings.py`, `groupings-archive/`, `groupings-record.json` |
| Testing and tuning (advisory) | `replay.py`, `tune.py`, `backtest.py`, `predictability.py`, `eurotest.py`, `ranktest.py`, `tools/` |
| Evaluation gate | `evaluation/` (`predict.py`, `score_pair.py`, approved frozen snapshots) |
| Office agents and merge gate | `agents/` (`pick_task.py`, `open_pr.sh`, `merge_gate.py`, `policy.json`) |
| Front end | `index.html` (template; edit this), `dashboard.html` (build output; never edit), `analysis.html` |
| Notes and history | `CLAUDE.md`, `AGENTS.md`, `claude/`, `RELEASES.md`, `julius/` (review exports) |

Bot-written, never hand-edit: `predictions*/`, `current/`, `record*.json`,
`tennis-data.js`, `tennis-record.*`, `sports-data.js`, `sports-record.*`,
`fifa-rankings.json`, `tuning-report.json`, `groupings-archive/`,
`groupings-record.json`, `dashboard.html`.

## How to change something

1. **Pull.** The bot commits to `main` several times a day.
2. **Find out why it is the way it is:** the comment above the code, the
   `claude/` note, `RELEASES.md`, `git log -p`. Most odd choices were tested.
3. **Branch** `<platform>/<YYYY-MM-DD>-<topic>` (main is protected).
4. **Test:** `python3 nametest.py` and `python3 -m unittest discover -s tests`
   with `API_FOOTBALL_KEY` unset. Model changes need held-out evidence: fit on
   the last completed season, confirm on the current one, paired bootstrap,
   gates (250+ check games, p(worse) at most 0.30, gain at least 0.0005 log
   loss).
5. **Log it:** a `RELEASES.md` entry ("tag pending") with what changed, the
   evidence, files, what didn't change, and how to roll back.
6. **Open a PR** with labels `office-agent`, your `platform:` label and
   `auto-merge-ok`. `evaluation.yml` and the tests run on it.
   `office-merge.yml` merges at 09:00, 15:00 and 21:00 UTC if
   `agents/merge_gate.py` passes. Agents never edit `.github/`, `agents/`,
   `CLAUDE.md` or `AGENTS.md`; workflow changes are made by the owner.
7. **Roll back** with `git revert`, never `git reset`.

```
python3 nametest.py                              # always, before any push
python3 -m unittest discover -s tests -v         # regression tests
python3 build.py --days 2 --no-topup --no-odds   # fast local football build
python3 build_tennis.py --out /tmp/t.js          # tennis (restore predictions-tennis/ after)
python3 sports.py --build                        # other sports
python3 groupings.py --probe                     # Odds tab pricing report, writes nothing
python3 tools/julius_export.py --date YYYY-MM-DD # every graded call as CSVs, for review
python3 replay.py --audit                        # what the football replay can use
python3 tune.py --report                         # advisory constant sweep
```

## Where the biggest improvements are

Ordered by what would most move the objective. Each needs evidence before it
ships; none is a licence to skip the gates.

1. **List quotes run about 3 points above what lands** (82.1% quoted, 79.4%
   landed). Find where: by sport, band and league. Candidates are the
   cumulative tested rate shown on rows (own-band rates are stricter) and
   tier-2 leagues at 75%.
2. **Own-band admission everywhere.** College football showed a sport can pass
   the cumulative 80% rule while its 70-80% calls land in the low 70s. Rugby
   union and college basketball (70% bars) have the same shape in testing.
   Test an own-band rule for all sports in one replay before changing any bar.
3. **Tennis back on the List, on evidence.** Live calls ran below quotes,
   mostly WTA (18 of 27 against 22.3 expected); ATP ran above (21 of 24 against
   19.8). ESPN results carry no surface, so everything since June is rated as
   hard court. A surface source and a live-period replay come first.
4. **Coverage.** No free source yet for Croatia, Serbia, Ukraine, Hungary,
   Korea, the UAE and several small European leagues; check API-Football's
   list first. Domestic cups failed their replay; U21 and senior-versus-academy
   ties are unpriced. Boxing and UFC have keys set but no code.
5. **Draws.** The model never picks a draw for the List, and draws are its
   most common football miss: 10 of the 19 football List losses, and 33 of 64
   lost football calls at 70% or more. A draw-risk flag needs the
   predictability harness, not a guess.
6. **Odds tab and The Odds API.** Several tennis tournaments (Almaty, the
   European Open, the Japan Open) didn't match a sport key on 19 Oct; logging
   the active key list in the report (no credits) would show why. Group chances
   are now honest but still lose to the bookmakers' margin by design.
7. **Results latency.** Results update on six rebuilds a day, not live.

## Recent decisions (newest first; details in `RELEASES.md`)

- 19 Oct 2026: Odds tab groups use honest chances and bookmaker-priced legs only (#47).
- 19 Oct 2026: The Odds API prices tennis and rugby legs on the Odds tab (#44), with the key passed to the groupings step only (#45).
- 15 Oct 2026: tennis off the Daily List on both tours (#43).
- 13 Oct 2026: college football List bar 70% to 80% (#42).
- 8 Oct 2026: tennis rated from every result since the archive; domestic cups kept off the List after their replay failed; no cap on List size.

## Known stale notes

- `CLAUDE.md` and some `claude/` notes still describe tennis on the List at 80%
  or 75%; it is off (see `build_tennis.LIST_ON`).
- `AGENTS.md` says "no new services or API keys"; The Odds API was added at the
  owner's request on 19 Oct 2026, for the Odds tab only.
- `CLAUDE.md` describes the Odds tab's estimate rule (at most two estimates);
  estimates are now never grouped.
- Only the owner edits `CLAUDE.md` and `AGENTS.md`. Agents report drift in
  their PR instead.

## Limitations

- On average it is worse than the betting market: it sees no team news,
  line-ups or injuries, by design. Prices are never used as model input.
- Free data limits coverage, and so does the paid plan's daily allowance.
- Tennis surface is missing for ESPN results.
- Nothing here is betting advice.

## Copyright

Copyright (c) 2026 Douglas Baker. All rights reserved. This repository is
proprietary: no licence is granted to copy, modify, distribute or use any part
of it without written permission. See [LICENSE](LICENSE).
