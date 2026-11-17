# The Card replay's live now spans two days (17 Nov 2026)

## What was wrong

Two-day groups (`groupings.CARD_SPAN`) have been part of the live Card since
12 Nov 2026 (`claude/card-span-2026-11-12.md`). `tools/card_replay.py` kept
building its `live` row day by day and replayed the two-day Card as a
separate variant, `span2`. So from 12 to 17 Nov:

- the nightly review's `live` row was not the Card the page builds;
- every variant was paired against that Card, so a variant that happened to
  fill the days the two-day group fills looked ahead of live when it was only
  ahead of a Card nobody runs;
- `span2`, the real live Card, sat on the "ahead of live, under the gate"
  watch list (+0.54 units a day, p(worse) 0.07).

## What changed

`card_replay.spans(variant)`: every variant built on the live machinery
spans while `CARD_SPAN` is on, under its own constants (the span pass now
sets the variant's patch, so a variant's rule decides its two-day group as
well as its one-day groups). The filler variants span on live's rule first
and fill only a day still empty. Not spanned: the rule 6 family (pinned to
how rule 6 ran, before two-day groups) and the paper Model card. `span2` is
gone; `nospan` replays the rollback (`CARD_SPAN = False`).

## The review window read again (pool, 29 Oct to 18 Nov, first real price)

| variant | before: groups, won, return | after | after, v live a day, p(worse) |
|---|---|---|---|
| live | 25, 11, +0.5% | 26, 13, +15.0% | |
| nospan (was live) | | 25, 11, +0.5% | -0.54, 0.92 |
| rule12 | 11, 5, +1.6% | 13, 4, -28.9% | -1.09, 0.90 |
| m7value | 12, 4, -24.9% | 14, 5, -13.9% | -0.83, 0.84 |
| m7opp5 | 23, 10, -6.4% | 23, 12, +13.4% | -0.12, 0.56 |
| m7under5 | 22, 11, +14.2% | 24, 12, +11.3% | -0.17, 0.59 |
| tennis75 | 27, 13, +11.1% | 28, 14, +15.9% | +0.08, 0.48 |
| pay3 | 26, 10, +18.8% | 29, 12, +28.1% | +0.61, 0.29 |

With `--recover` (legs archived before `priced` at their last price,
approximate): live 34 groups, 21 won, +42.5% (was 32, 18, +27.7%); rule12
22, 13, +39.9%, -0.63 a day v live, p(worse) 0.84.

So `m7under5` (p(worse) 0.00 before) and `tennis75` were ahead of the old
live mostly because the old live left days empty that the two-day group now
fills; neither is ahead now. `pay3` (the 3x band) is the one variant still
ahead, on 88 legs, under the 100-leg gate. Rule 13 against rule 12 reads the
other way from the rule 13 note's numbers on this window once both span:
live (rule 13) +0.6 to +1.1 units a day ahead, p(worse) for rule 12 0.84 to
0.90. That is 14 to 18 days and far from the gate; it does not settle the
30 Nov review.

## Limits

- The football-data seasons (`tools/card_legs_history.py`) built day by
  day until later the same day; they span now too
  (`claude/card-legs-history-span-2026-11-17.md`).
- The pool has no prices kept for legs first written as estimates before
  10 Nov; the replay rebuilds 25 to 26 of the record's 26 groups.

No Card rule changed; nothing on the page.
