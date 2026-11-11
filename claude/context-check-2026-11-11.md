# The context check on the Card's picks (11 Nov 2026, CARD_RULE 9)

Douglas, 11 Nov 2026: "I think the groups pick fixtures on statistical
insight. But with added human contextual review it does much better. I need
the groups to have the same contextual reading" and, offered a shadow trial
first: "I want this contextual review now. But also just a better
understanding of the numbers... goals and points and other things."

## What it does

`context_review.py`, run by `groupings.py` before the Card is built:

- Every pick the Card's rule admits (`card_fault` None: the model's own
  pick, 60%+, at or above the bookmakers, priced 1.15-1.90) starting within
  30 hours is read by Claude (`CONTEXT_MODEL`, default `claude-sonnet-5-5`)
  with live web search (up to 5 searches a pick): team news, rotation before
  a bigger game, manager, what the game means, travel; and the season's
  numbers: position, points, goals for and against, home or away form, last
  five, head-to-head.
- Verdict: **clear**, **caution** or **against**, with a one-line reason,
  the news, the numbers and up to four sources. An "against" without a
  source is downgraded to caution. Prompt: "against" only for a concrete,
  sourced reason the pick is clearly less likely than the model's number.
- One read a pick, a second within 3 hours of the start (line-ups), at most
  16 calls a build. Verdicts kept in `groupings-archive/context-<date>.json`.
- `groupings.CARD_CONTEXT` True: an "against" pick fails `card_fault`, so it
  never goes on the Card or the bench, and an open group holding it is
  replaced at the next build (logged). `CARD_RULE` 9.
- The page: every Card pick shows its verdict and reason, with the news,
  numbers and sources in a fold (`ogContext`).
- Silent without `ANTHROPIC_API_KEY` (passed to the groupings step in
  `deploy.yml`). The build log prints the check's line every run.

## How it is judged

It cannot be replayed: the news of past days is not archived. So every
verdict goes into the pool (`context`, the latest before the start) and the
record grades it forward: `groupings-record.json` `cardContext`, by verdict,
landed v the model's number (`zModel`) and the bookmakers' chance. The veto
earns its place if "against" picks land under the model's number and "clear"
ones do not. Review at 30 "against" picks; if they land at or above the
model's number, set `CARD_CONTEXT = False` (the reads still show).

## Limits

- The owner's call, untested; the model is the source of truth and the check
  only removes picks, never adds them.
- A web read can be wrong or stale, and a story can already be in the
  price. Every verdict carries its sources so it can be checked.
- Cost: a few picks a day, each a handful of searches; pennies a day.
- The web search tool version is `web_search_20250305` unless
  `CONTEXT_TOOL` is set; a refused call logs the API's own words.
