# The replays' check season stopped on 20 Sep (15 Nov 2026)

## What was wrong

`claude/openfootball-lag-2026-11-13.md` found that openfootball's 2026-27
files stopped scoring matches after 20 Sep 2026, and fixed the live build
(`build.fill_lagging`, ESPN results under openfootball's spelling). The fix
did not reach `tune.load`, the one loader behind `tune.py`, `backtest.py`,
`replay.py`, `tools/card_legs_history.py`, `tools/goals_value.py`,
`tools/model_ideas.py` and the rest. It reads openfootball's files alone
(`sources.fetch_season`), so every openfootball league's check season still
ended on 20 Sep, and Belgium's held one match.

Found from the Card: the football-data replay's 2026-27 season
(`card-legs-history.json`, 9 Nov) had 70 candidate legs in August, 76 in
September and 7 in October, and 772 of 2,263 priced matches joined. Every
rule 7 variant's 2026-27 read was one live group, so the gate's check-season
side could not be read for any of them (`m7opp5` built nothing there).

The same truncation sits under the weekly gated refits (`tune.py --fit` for
`calibration.json`, `model_ideas.py --fit-home` for `home-advantage.json`):
their "confirm on the current season" step was confirming on August and
September only.

## Measured (sandbox, 15 Nov, football-data's extra leagues unreachable here)

| | check fixtures | log loss | accuracy |
|---|---|---|---|
| before (openfootball alone) | 903 | 1.0253 | 47.2% |
| after (filled from the ESPN cache) | 1,638 | 0.9964 | 51.8% |

735 results filled across 14 leagues: en.1 50, en.2 85, sco.1 33, es.1 50,
de.1 45, it.1 60, fr.1 45, nl.1 45, pt.1 35, be.1 98, tr.1 63, at.1 30,
gr.1 34, br.1 62. No league refused on names. The fit season (5,262) is
unchanged. The log loss gap is the later fixtures being easier to call (more
of the season known), not a model change; nothing was refitted.

## The fix

- `tune.fill_current(code, season, rows)`: for the check season of a league
  the build would fill (`tune.lag_eligible`, the same test as
  `build.lagging_codes`: an ESPN slug, not a cup, an international, an
  API-Football or a football-data league), read the ESPN results the daily
  build commits in `current/<code>-<season>.json`, take openfootball's full
  fixture list (`sources.fetch_fixtures`) and fill it with
  `build.fill_lagging` (its own pair within 21 days, never a pair the source
  scored nearby, all or nothing on names; `append` for a league with no
  fixture dated ahead, as the build does for Belgium). The filled matches are
  added to the played rows. No network beyond what `tune.load` already
  fetched: the cache is in the repo.
- `tune.load(cache, fill=True, log=None)` calls it for the check season only
  and prints one line a league to stderr. A split without a check season
  (`card_legs_history.py`'s past seasons) is untouched.
- `replay.py --freeze` passes `fill=False`, so a frozen snapshot's
  openfootball seasons hold openfootball rows only (the licensing filter in
  `filter_snapshot` relies on it). The evaluation harness reads frozen
  snapshots and is unaffected.

## What it changes

- The Card's football-data check season (2026-27) now runs to the cache's
  last day, so a rule 7 variant's check-season read means something.
  `card-legs-history.yml` runs on this pull request (it touches the tool's
  docstring) with the new read.
- The Monday refits gate on about twice the check fixtures. A candidate
  still needs two consecutive weekly passes; nothing auto-applies sooner.
- Leagues ESPN supplies whole (the "gap" leagues, `current/` holds their
  season) are not added here: that is `replay.py --include-current`'s
  advisory question, with its own overlap checks.

## Not changed

Any model constant, `calibration.json`, `home-advantage.json`, any Card
rule, the live build, the page.
