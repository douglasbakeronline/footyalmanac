# The Claude API allowance and what spends it (15 Nov 2026)

Douglas: "I got a notification that my API reach is now finished for Claude
... let's roll back whatever we've implemented recently that's causing a lot
of these calls."

## What calls the Claude API

One secret, `ANTHROPIC_API_KEY`, used in four places:

| Caller | When | Calls |
|---|---|---|
| `office-agents.yml` | scheduled sprints | up to 6 Claude Code sessions a sprint (Sonnet, `--max-turns 50`) |
| `context_review.py` (via `groupings.py` in `deploy.yml`) | every build | up to `DAILY_READS` a UK day, Sonnet or Haiku with web search (up to 5 searches each) |
| `ceo.yml` | only on Douglas's `ceo` issues | one session a request |
| `claude.yml` | only on an `@claude` mention | one session a request |

The claude.ai scheduled tasks (the Card build sessions, the weekly report)
and sessions like this one run on the Claude plan, not this key. Nothing else
in the pipeline (Scale, markets, ledger, slip, the Card, the builds) calls
the Claude API.

## What had grown

- 9 Nov: office sprints doubled from two to four a day, so up to 24 agent
  sessions a day. Runs: 5 sprints on 10 Nov, 3 on 11 Nov, 5 on 12 Nov.
- 11 Nov: the context check on Card picks.
- 12 Nov: the context check extended to every Daily List pick at 75%+, up
  to 25 reads a day.

The key hit its limit on 14 Nov (`claude/context-paused-2026-11-14.md`, access
back 1 Dec); every office sprint since 13 Nov has failed on it.

## Rolled back

- Office sprints: two a day (06:30, 18:30 UTC), the day's pull request cap 16.
- Context check: Card picks only (`groupings.CX_LIST_MIN = None`), at most 8
  reads a day (`CONTEXT_DAILY_READS`).

Kept: the Card's context veto (Douglas's call, 11 Nov), `ceo.yml` and
`claude.yml` (only on request).

## If it runs out again

The office sprints are the biggest spender. Next steps, in order: one sprint
a day (drop the 18:30 cron); `SPRINT_SIZE` down from 5; `--model haiku` for
the agents; `CARD_CONTEXT = False` to stop the context check entirely.
