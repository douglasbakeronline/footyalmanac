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
