# The Card replay read at the last pre-start price, and its fidelity to the page (24 Nov 2026)

Build session, 24 Nov 2026, 12:34 London. No Card rule changed; `CARD_RULE`
stays 14 until the 30 Nov read.

## What was wrong with the read

The 30 Nov decision is rule 14 (rule 8's constants, live from 19 Nov) against
`rule13` and `rule12`, read on the pool replay (`tools/card_replay.py`). The
nightly review ran that replay at each leg's **first** real price. The pool is
written up to three days ahead, so the first price is often days before the
start. The page does not build on that price: it rebuilds every Card group on
each build until the group's first kick-off. Rule 14's value demand (the model
at or above the bookmakers' chance) reads the price, so a leg can pass at the
first price and fail at the one the page saw.

Hammarby IF, 23 Nov: first price 1.22 (fair 75.9%), model 78.7%, passes. Last
pre-start price 1.16 (fair 80.7%), fails. The replay at first prices built a
23 Nov group (Hammarby, Oklahoma City Thunder, San Antonio Spurs); the page,
correctly, built none. Rule 13 has no value demand, so it barely moves with
the price; the comparison was tilted by the price read, not by the rules.

## The numbers (pool from 30 Oct, the review's window from 29 Oct, run 24 Nov)

| variant | at first prices | at last pre-start prices |
|---|---|---|
| live (rule 14) | 10 groups, 5 won v 4.17, +23.7%, 30 legs | 7 groups, 4 won v 2.95, +43.4%, 21 legs |
| `rule13` v live | +0.23 a day, p(worse) 0.32, 120 legs | -0.31 a day, p(worse) 0.69, 117 legs |
| `rule12` v live | +0.09 a day, p(worse) 0.46, 72 legs | +0.19 a day, p(worse) 0.41, 63 legs |
| `comp3` v live | +0.13, p 0.35 | +0.86, p 0.08 (39 legs) |
| `span2` v live | +0.23, p 0.40 | -0.72, p 0.91 |

The sign of `rule13` against live flips with the price read. Nothing here is
near the gate (100+ legs, p(worse) 0.30 or under, and the football-data
seasons), so neither price says "switch". What it says is that the 30 Nov
read must be made at both prices, and a variant ahead at only one of them is
not ahead.

## Fidelity on rule 14's own days (19 to 23 Nov, 5 settled days)

The page published 3 rule 14 groups (21 Nov two, 22 Nov one). The replay's
live row:

- at first prices: 4 groups, 1 with the page's picks (22 Nov), and a group on
  23 Nov, where the page had none;
- at last prices: 3 groups, 1 with the page's picks, every day agreeing on
  whether there was a group.

21 Nov differs at both prices: the page built Mlada Boleslav, Galatasaray,
Rapid Wien and Ascoli, Lazio, 76ers on the 11:08 build's prices; the replay,
on one price per leg, picked Galatasaray, 76ers, Rapid Wien and Alianza Lima,
Timberwolves, Lazio. The pool keeps a first and a last price only, so no
replay can read the price at a group's first kick-off; the last pre-start
price is the nearer of the two for a rule that rebuilds until then.

## What changed

- `card-review.yml` runs the replay a second time with `--closing`
  (`card-replay-closing.json`, in the run's artifacts).
- `card_review_post.decisions_section(..., rep_close=)`: the rule 14 row reads
  `rule13` and `rule12` at the last pre-start price beside the first.
- `card_review_post.fidelity_lines`: one line under Coverage, the replay's
  live row against the published Card on the live rule's settled days, at
  both prices (groups, same picks, days with a group on one side only).
- `card_replay.py` `groupList` carries each group's `picks`.

Tests: `tests/test_review_fidelity.py` (three).

## For the 30 Nov read

Read the rule 14 row at both prices. If `rule13` or `rule12` is ahead at one
and behind at the other, it is not ahead. The fidelity line says which price
reproduced the page's Card more closely on the days that rule ran; on 19 to
23 Nov that was the last price.
