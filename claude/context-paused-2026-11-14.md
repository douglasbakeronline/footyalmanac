# The context check paused by the API usage limit (14 Nov 2026)

## What happened

The 00:24 UTC build on 14 Nov made six context reads (5 verdicts, 1
unreadable reply for Almere City), then the Messages API refused:

> You have reached your specified API usage limits. You will regain access on
> 2026-12-01 at 00:00 UTC.

The ledger shows 25 reads on 12 Nov and 25 on 13 Nov (the `DAILY_READS` cap,
Sonnet for Card, football and NBA picks), so the key's monthly limit was spent
in under four days of the Daily List reads that began on 12 Nov.

The same limit is the likely cause of the office sprints failing from 13 Nov
19:55 UTC: every agent ends in under a second with `is_error: true`, zero
cost and no turns (runs 43496729367, 43529615302). That is workflow and
secret territory, so not touched here.

## What it did to the Card

Nothing to the picks: only an "against" verdict vetoes (`CARD_CONTEXT`), so
an unread pick is admitted as it was before rule 9. But every build after the
limit asked for every due pick again, failed each one, and nothing on the
page or in the nightly review said the check had stopped. The page still
said "with the context check" over picks nobody had read.

## The change

- `context_review.py`: a usage-limit refusal (HTTP 400/402/403/429 whose body
  names a usage limit, credit balance, billing or quota) raises `UsageLimit`.
  The check stops for the build and writes the time the API names
  (`limit_until`, else 24 hours on) to `context-ledger.json` as `pausedUntil`.
  While paused, each build makes one probe call (a refused call costs
  nothing); if it gets through, the pause is cleared and reads resume in the
  same build. At the named time the key is cleared anyway. `review()`
  reports `paused` in `report["context"]`.
- `groupings.py`: `contextPaused` in `groupings-data.js`; the build log says
  "paused until ... (API usage limit)".
- `index.html`: the Card section says the check is paused until the date and
  that no pick is being kept off for news (`cxPaused`, `cxPausedHtml`); the
  backed-picks fold drops "with the context check" while paused.
- `tools/card_review_post.py`: the nightly review prints the pause in bold
  above the context table (`context_pause_line`).

## The decision for Douglas

The check resumes on its own on 1 Dec. To have it sooner, raise the key's
monthly limit in the Anthropic console: the next build's probe call gets
through and reads resume, nothing to do by hand. At the current reads (25 a
day, mostly Sonnet) the limit lasted about three and a half days from the
list reads starting on 12 Nov; `DAILY_READS` or `CX_LIST_MIN` is the lever if
the budget is to last the month.
