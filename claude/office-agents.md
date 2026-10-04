# Office agents (2 Oct 2026, sprint and no owner review from 4 Oct 2026)

**4 Oct 2026 change (Douglas: "I want this to happen without my review. Give
all agents a task.")** The daily run is now a sprint: every agent in
`SPRINT` works in turn on its most urgent task (the list below) or its own
standing task in `STANDING`, and each pull request merges as soon as its
checks pass (nametest.py, the unittest suite, a fast build for pipeline
code), with no 12-hour wait and no `needs-owner` step. Closed instead of
merged: failed checks, model changes without every gate passed, or the agent
setting automerge false. One agent at a time, each starting from the main
the previous agent merged into. The rest of this note describes the original
loop; the gates on protected files, conflicts and `hold` are unchanged.


Douglas asked for the Footyalmanac HQ office
(github.com/douglasbakeronline/footyalmanac-hq) to develop this project
unattended, with him reviewing whenever he chooses.

## The loop
1. **06:30 UTC, `office-agents.yml`.** Open issues labelled `office-backlog` come first, oldest first; an `agent:<id>` label picks the agent. Otherwise `agents/pick_task.py` reads `record.json`,
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
- Cost: one Claude session a day on Sonnet (the Claude Max subscription token, `CLAUDE_CODE_OAUTH_TOKEN`), at most 50 turns. Days with nothing new to do use no tokens.
