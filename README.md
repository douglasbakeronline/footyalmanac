# Sports Almanac

A daily-refreshed sports prediction site. It rates every team and player it can
find free data for, prices each upcoming game, and leads with a **Daily List**
of the most likely results across every sport, strongest first. Every pick
shows how often calls at its level actually landed on games the model was
never tuned on, and the site grades itself publicly against what happened.

- **Live:** https://douglasbakeronline.github.io/footyalmanac/
- **Sports:** football (more than seventy competitions rated, internationals
  included), tennis
  (ATP/WTA), NFL, baseball (MLB), basketball (NBA), rugby union.
- **Rebuilt daily** at 05:15 UTC by GitHub Actions. No server, no paid data,
  Python standard library only.

The point of the site is honest confidence: surface the genuinely predictable
games, say plainly when a call is weak, and never inflate a number to look good.

> **Working on this repo with an AI agent?** Read [`CLAUDE.md`](CLAUDE.md)
> first (the rules, learned the hard way), then [`AGENTS.md`](AGENTS.md).
> Handover notes for each area live in [`claude/`](claude/). The release log,
> with rollback instructions, is [`RELEASES.md`](RELEASES.md).

---

## The Daily List

The front page. One rule for every sport: a pick qualifies only if calls at its
level **landed at least 75% of the time in testing** on games the model never
saw. The level differs by sport because the numbers do:

| Sport | List threshold | Tested hit rate at that level |
|---|---|---|
| Football leagues | 75% | 78.9% of 242 (2025/26) |
| Men's internationals (with FIFA ranking) | 60% | 77.8% of 536 (2025), 75.3% of 190 (2026) |
| Tennis, main draw (ATP with ranking) | 65-70% | 78-80% across ATP/WTA, 2025 and 2026 |
| Basketball | 70% | 79.7% / 80.4% |
| Rugby | 60% | 78.0% / 75.1% |
| NFL | 75% | 81.6% / 77.4% |
| Baseball | not on the list | its strongest calls do not land often enough |

Football also leaves out anything the model is structurally blind to (see
Celtic's Law below) and never picks a draw; tennis leaves out qualifying
rounds. Each day is one ranking across every sport by tested hit rate. Roughly
one pick in four or five still misses: that is sport, and a higher bar does not
remove it. The list is the model's own independent read, with no bookmaker
input.

## How the numbers are made

**Football.** Attack and defence ratings from completed results, blended with
the current season (`w = played / (played + 6)`), into a Dixon-Coles adjusted
Poisson score matrix for home / draw / away. A two-parameter calibration curve
(`calibration.json`, refitted weekly behind gates) corrects the raw model's
over-confidence. Men's internationals use their own ratings
(`international.json`) re-scored with the FIFA ranking. Cup ties are rated
against each club's domestic league via fitted league strengths
(`europe.json`).

**Tennis.** Surface-blended Elo from the tour-level archive, pulled toward a
coin flip by a per-tour amount testing found honest (ATP 0.9, WTA 0.95), and
re-scored with the ATP ranking for men's matches.

**NFL, baseball, basketball, rugby.** Elo per sport, keyed by ESPN team id,
with home advantage, margin of victory and off-season regression, fitted on
2024/25 and judged on 2025/26 (`sports.json`). A sport is only published if it
beats simply backing the home side.

### Why not a points tally?

The obvious scheme (points for wins, add goal difference, add a form tally)
double-counts (points already encode wins), uses arbitrary scales, cannot
compare across leagues, and above all a score difference is not a probability.
So ratings feed models that produce probabilities directly, and the raw
statistics stay on screen as the reasoning, not the engine.

### What was tested and found not to help

Recent form, last season's head-to-head, rating drift, games played, separate
home/away ratings, rest days, per-band temperatures, and the WTA ranking all
add nothing measurable beyond the models' own numbers (`predictability.py`,
`tune.py`; details in `claude/`). What a person adds when checking a fixture by
hand is mostly team news, which the betting market prices and this site
deliberately does not use.

## Honesty mechanisms

- **Published in advance, graded afterwards.** Every prediction is archived
  (`predictions/`, `predictions-tennis/`, `predictions-sports/`) and graded
  daily (`record.json`, `tennis-record.json`, `sports-record.json`). Only
  prices published before kick-off count. Nothing is ever fitted on the record.
- **Every change is tested.** Fit on the last completed season, confirm on the
  current one, paired bootstrap, gates: 250+ check games, p(worse) at most
  0.30, gain at least 0.0005 log loss.
- **Celtic's Law.** Fixtures where the model is blind before kick-off
  (promoted sides, unrated clubs, cross-division cup ties) are flagged and
  dropped a confidence tier, never hidden.
- **Fail loudly, keep yesterday.** A failed upstream keeps yesterday's site
  rather than publishing an empty or wrong one.

## Data sources

All free, no keys: [openfootball](https://github.com/openfootball) (public
domain), ESPN's public scoreboards, [football-data.co.uk](https://www.football-data.co.uk)
(results and fixtures for five leagues; its odds columns are not used by the
models), FIFA's ranking API, ESPN tennis rankings, and Jeff Sackmann's tennis
archive for history.

## Files

| File | What it is |
|---|---|
| `engine.py` | Football ratings and match model |
| `sources.py` | Football data fetching, name matching, ESPN slugs |
| `build.py` | Football build: fetch, rate, price, write the page, archive |
| `score.py` | Grades football predictions, writes `record.json` |
| `build_tennis.py`, `score_tennis.py`, `tune_tennis.py` | Tennis pipeline |
| `sports.py` | NFL, baseball, basketball, rugby: history, tuning, build, grading |
| `rankings.py` | FIFA and ATP/WTA world rankings and their tested adjustments |
| `tune.py`, `backtest.py`, `predictability.py`, `eurotest.py`, `odds.py` | Testing and tuning harnesses (advisory) |
| `nametest.py` | Guards the club-name matcher; runs before every deploy |
| `backfill.py` | Walks a past season from ESPN into `history/` |
| `index.html` | The page template. Edit this, never `dashboard.html` |
| `dashboard.html` | Self-contained build output, published as the site |
| `RELEASES.md` | Release log with rollback instructions |
| `CLAUDE.md`, `AGENTS.md`, `claude/` | Rules and handover notes for people and AI agents |

## Commands

```
python3 nametest.py                              # must pass before any push
python3 build.py --days 2 --no-topup --no-odds   # fast local football build
python3 build_tennis.py                          # tennis
python3 sports.py --daily                        # other sports: top up, price, grade
open dashboard.html                              # the page, straight off disk
python3 tune.py --report                         # advisory constant sweep
python3 predictability.py                        # which signals separate hits from misses
```

## Limitations

- Worse than the betting market on average: it sees no team news, line-ups or
  injuries, by design.
- Free data caps coverage. Several European leagues (Croatia, Serbia, Ukraine,
  Hungary, Korea and others) have no free source this project can reach.
- World Rugby rankings have no reachable source; rugby uses Elo alone.
- Nothing here is betting advice.
