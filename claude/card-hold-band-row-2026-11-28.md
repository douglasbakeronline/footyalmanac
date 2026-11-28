# The hold band as a measured decision (28 Nov 2026)

Build session, 28 Nov 15:17 London slot.

## Why

The morning session found 27 Nov's Card 2x (Al Qadsiah, Philadelphia 76ers,
Detroit Pistons, Hill 2.55) withdrawn at 07:10 on a sub-point value-demand
miss, all three winners (`claude/card-withdrawn-groups-2026-11-28.md`). It
left the follow-up in prose: at 10 settled withdrawn groups, set their landed
rate beside the model's number, and pre-register a hold band if they land at
or above it. A trigger that lives only in a note is not read; the decisions
table is where every other one sits.

## What changed

`tools/card_review_post.withdrawn_tally` counts every withdrawn Card group
from `WITHDRAWN_FROM` (26 Nov, when `publog.py` began recording withdrawals)
to today, settled on the results ledger, in the record's tally shape.
`decisions_section(withdrawn=)` adds the row "Hold band for published Card
groups": trigger `HOLD_REVIEW_AT` (10) settled withdrawn groups landing at or
above the model's number; **due** when met (the next session pre-registers a
hold-band variant; a rule change stays Douglas's), "reviewed, no hold band"
when ten have settled under the model. The groups' totals now come from one
helper (`_withdrawn_settled`) shared with the review's withdrawn line.

## Standing at 28 Nov

1 withdrawn, 1 settled: 1 won v 0.48 expected, +155.0% at the page's stakes
and last shown price. Waiting.

## What it cannot say

The pool replay reads each leg at one price, so it cannot rebuild a hold;
the withdrawn groups are the only evidence, and they come slowly (one in the
log's first three days). A hold band would also hold groups that later fail
by a wide margin, which this tally does not see: a variant needs to name the
band (for example, a value-demand miss under one point) before it is read.

## Files

`tools/card_review_post.py`, `tests/test_review_live_days.py`, this note,
`claude/card-review-agenda-2026-11-30.md`, `CLAUDE.md`, `RELEASES.md`.
`CARD_RULE` stays 14; nothing enters the record (Rule 1).
