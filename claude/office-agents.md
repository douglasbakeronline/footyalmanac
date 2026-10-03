# Office agents (2 Oct 2026)

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
4. **21:00 UTC, `office-merge.yml`.** `agents/merge_gate.py` decides from evidence, never from labels.
   See `claude/evaluation-layer.md` (3 Oct 2026) for every condition. Docs-only changes can merge
   unattended. Model, calibration, source-data, evaluation-rule, workflow/security, UI and unknown
   paths need Douglas's approval of the exact head commit.

## Controls
- Stop one change: add the `hold` label, or close the pull request.
- Stop everything: disable "Office agents" in the Actions tab.
- Force a task: run "Office agents" with a task key (e.g. `calibration-gap`).
- Cost: one Claude session a day on Sonnet (the Claude Max subscription token, `CLAUDE_CODE_OAUTH_TOKEN`), at most 50 turns. Days with nothing new to do use no tokens.
