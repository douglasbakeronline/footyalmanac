# Guide for AI coding agents

This file is for any AI agent working on this repository: Claude Code
(terminal, IDE, or claude.ai/code in the cloud), the Claude GitHub agent
(`@claude` on issues and pull requests), GitHub Copilot, Codex or others.

**[`CLAUDE.md`](CLAUDE.md) is the rulebook and the source of truth.** Read it in
full before changing anything. This file summarises how to add value without
undoing the work that is already here.

## What this project is

A daily-refreshed, multi-sport prediction site whose one claim is honesty: its
numbers are published before kick-off, graded afterwards in public, and every
pick shows how often calls at its level actually landed in testing. See
[`README.md`](README.md) for the overview.

## Before you start

1. Pull: a bot commits the daily archive to `main` every morning.
2. Read `CLAUDE.md`, then the note in `claude/` that matches your task (the
   table in `CLAUDE.md` says which). The code on `main` beats any note.
3. Check `RELEASES.md` for what changed recently and why.

## Guardrails: the previous good work these protect

These each exist because something went wrong without them. Do not work
around them; if you think one is wrong, say so in your pull request instead.

- **Never fit anything on the live record** (`record.json`,
  `tennis-record.json`, `sports-record.json`). It is the scoreboard.
- **Every model change is tested before it ships**: fit on the last
  completed season, confirm on the current one, paired bootstrap, gates (250+
  check games, p(worse) at most 0.30, gain at least 0.0005 log loss), plus the
  honesty guard (the quoted-vs-landed gap for strong calls may not widen).
  "It looks better" is not evidence. Harnesses: `tune.py`, `predictability.py`,
  `sports.py --tune`.
- **Structural constants never move on their own.** Only `calibration.json`
  auto-applies. Anything else a human commits, with the test in the commit or
  pull request.
- **Do not reopen what was tested and rejected** (listed in `CLAUDE.md`) without
  new evidence.
- **A wrong match is worse than a missed one.** Club and player name matching
  must fail loudly. `python3 nametest.py` must pass.
- **Never hand-edit bot-written files**: `predictions*/`, `current/`,
  `record.json`, `tennis-data.js`, `tennis-record.*`, `sports-data.js`,
  `sports-record.*`, `fifa-rankings.json`, `tuning-report.json`,
  `dashboard.html`. Edit `index.html`, never `dashboard.html`. Do not commit
  `data.js` or `data.json`. If a local build rewrote a bot file, restore it
  (`git checkout -- <file>`) before committing.
- **Standard library only.** No pip, no `requirements.txt`, no new services or
  API keys. Python 3.12 in CI; code that must also run on the owner's Mac
  should avoid 3.8+ only syntax (see `CLAUDE.md`, Known drift).
- **No manual data entry, no bookmaker input into the models.** Both were
  deliberate decisions by the owner.
- **Honesty over confidence.** Weak calls are labelled weak, blind spots are
  flagged, and a failing upstream keeps yesterday's site rather than publishing
  an empty or wrong one.
- **Keep the look.** The cover header, colours and row layout were chosen by the
  owner. Visual changes respect the contrast tokens in
  `claude/brand-identity.md`; no dark border thicker than 1px.

## How to ship

- **Unattended agents (claude.ai/code sessions, the GitHub agent, Copilot):**
  work on a branch and open a pull request. claude.ai/code sessions cannot
  push tags, so write "tag pending" in the `RELEASES.md` entry; a local
  session tags the merge commit. Put the would-be `RELEASES.md`
  entry in the pull request description (or in the file). A push to `main`
  deploys the live site, so merging stays with the owner.
- **An agent working live with the owner** follows the release process in
  `CLAUDE.md`: pull, `nametest.py`, fast build, restore bot files, add a
  `RELEASES.md` entry, commit, annotated tag `release-YYYY-MM-DD[-n]`,
  `git push --follow-tags`. Roll back with `git revert`, never `git reset`.

## How to verify a change

```
python3 nametest.py                              # always
python3 build.py --days 2 --no-topup --no-odds   # football page builds
python3 sports.py --build                        # if you touched sports.py
python3 build_tennis.py --out /tmp/t.js          # if you touched tennis (restore predictions-tennis/ after)
```

Then open `dashboard.html` and look at it, at desktop width and at phone width
(about 400px). If your environment blocks network access to ESPN, openfootball
or football-data.co.uk, say so in the pull request and let CI's build be the
check; never commit the output of a build that could not fetch its data.

## Adding value without breaking things

Good contributions: a new free data source for an uncovered league (with a
name-matching test); a tested model improvement with its paired bootstrap
result; a new sport through `sports.py`'s config, published only if it beats
backing the home side; accessibility and layout fixes within the current look;
clearer copy that stays accurate. Open items are listed in `CLAUDE.md`.

After a significant change, add a dated note to `claude/` in the style of the
existing ones and update `CLAUDE.md` if a rule, file or open item changed.
