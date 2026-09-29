# Releases

Newest first. Every release is an annotated git tag (`release-YYYY-MM-DD`,
with `-2`, `-3` for a second release the same day) and an entry here.

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
