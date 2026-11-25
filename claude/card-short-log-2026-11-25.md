# The page's own read of each Card day (25 Nov 2026)

## Why

The pool replay reads every leg at its first real price, and those prices are
written days apart (Salisbury and Torquay first priced 22 Nov 23:54 UTC for
24 Nov; the NBA lines much later). So the replay's live row can build a group
whose picks were never clear of the rule at the same build. The 25 Nov review
named two days like that, both empty on the page:

- 23 Nov: Hammarby IF, Oklahoma City Thunder, San Antonio Spurs (at the last
  pre-start price Hammarby had no value: 79% v the bookmakers' 81%).
- 24 Nov: Boston Celtics, Salisbury, Torquay (at the last price the Celtics
  had none: 77% v 78%).

The page leaves only `cardShort` on the day it builds, overwritten each build,
and the day archive holds only groups that were published. Nothing said what
the page saw at 06:00, 12:00 or 17:00.

## What

`groupings.log_short` appends one entry per day built, only when it changed:

```
{"2026-11-24": [{"at": "...Z", "why": "few" | "spread" | "long" | "short" | "chance" | "built",
                 "best": 3.51, "groups": [[picks]], "clear": [[pick, odds, pModel], ...]}, ...]}
```

`clear` is `card_cands`: picks clear of `card_fault`, placed on the day by UK
start, not held by a two-day group, starting 20+ minutes out (what
`best_card` and `card_short` can use). 30 days kept, 40 entries a day.

The nightly review's Fidelity block (`card_review_post._page_read`) adds, for
each replay-only group: "the page's own reads, N logged from ...: never all
clear together (clear in: Boston Celtics 0, Salisbury 4, Torquay 4); last
read few", or "all clear together at k" when the page had them and grouped
otherwise or held a group.

## Reading it

- Never together: the gap is the price timing, the replay's live row is
  optimistic on that day, and the 30 Nov read should weigh the last-price
  replay (`card-replay-closing.json`) more.
- Together but no group: the page's choice or hold; worth a look at
  `best_card`.

Only from 25 Nov; earlier days stay as the 24 Nov notes left them
(`claude/card-replay-fidelity-why-2026-11-24.md`).
