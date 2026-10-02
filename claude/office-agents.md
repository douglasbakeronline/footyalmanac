# Office agents (2 Oct 2026)

Douglas asked for the Footyalmanac HQ office
(github.com/douglasbakeronline/footyalmanac-hq) to develop this project
unattended, with him reviewing whenever he chooses.

## The loop
1. **06:30 UTC, `office-agents.yml`.** `agents/pick_task.py` reads `record.json`,
   `tennis-record.json`, the latest `predictions/` file and recent `deploy.yml`
   runs, then picks the first task in priority order:
   build failure (Allan) → unrated fixtures (Cory) → weakest league under 45% (Mia) →
   calibration gap over 5pt (Andrew) → Strong tier below expected (Ben) →
   tennis below expected (Theo) → new free data source (Ava).
   - It skips a task that has an open pull request or one opened in the last 7 days.
   - It skips the whole day if two agent pull requests are already open.
2. **Claude works under the task's prompt.** It reads CLAUDE.md and AGENTS.md first, never commits, and writes `/tmp/office-agent/report.md` and `meta.json`.
3. **`agents/open_pr.sh` checks the work and opens a pull request.**
   - It throws away changes to protected files: bot-written and fitted files, plus `.github/`.
   - It runs `nametest.py`, plus a fast build if pipeline code changed.
   - It opens a pull request labelled `office-agent`, `agent:<id>`, `objective:<key>` and `checks-passed` or `checks-failed`.
   - It adds `auto-merge-ok` or `needs-owner`.
4. **21:00 UTC, `office-merge.yml`.** `agents/merge_gate.py` squash-merges every pull request that meets all of these:
   - labelled `auto-merge-ok` and `checks-passed`
   - not labelled `hold` or `needs-owner`
   - at least 12 hours old
   - no protected files
   - no conflicts

   It then tags `release-YYYY-MM-DD[-n]` and dispatches `deploy.yml`. A push made with
   the Actions token does not trigger `deploy.yml` on its own, which is why the
   gate dispatches it.

## Controls
- Stop one change: add the `hold` label, or close the pull request.
- Stop everything: disable "Office agents" in the Actions tab.
- Force a task: run "Office agents" with a task key (e.g. `calibration-gap`).
- Cost: one Claude session a day, at most 80 turns.
