# Why the page's Card and the replay differ (24 Nov 2026, evening)

Scheduled build session. The nightly review's Fidelity line (added this
morning, `claude/card-replay-price-fidelity-2026-11-24.md`) read rule 14's
days 19 to 23 Nov: the page published 3 Card groups, the replay's live row
rebuilt 4 at first prices with 1 matching, 3 at last prices with 1 matching.
The line put every gap down to the price the rule was read on. It now says
which, group by group.

## What the 19 to 23 Nov days show (local run on the committed pool)

| group | first published | at first prices | at last pre-start prices |
|---|---|---|---|
| page 21 Nov: Galatasaray, FK Mlada Boleslav, Rapid Wien | 20 Nov 19:07 UTC | every pick clear | every pick clear |
| page 21 Nov: Ascoli, SS Lazio, Philadelphia 76ers | 21 Nov 07:00 UTC | Lazio no value (67% v 69%), 76ers 1.14 under 1.15 | every pick clear |
| replay 21 Nov: Alianza Lima, Galatasaray, Rapid Wien | not on the page | | every pick clear |
| replay 21 Nov: Alcaraz, Timberwolves, Southampton | not on the page | | Alcaraz and Southampton no value |
| replay 23 Nov: Hammarby, Thunder, Spurs | not on the page | | Hammarby no value (79% v 81%) |

So of the two page groups the replay missed, one is the price (the second
21 Nov group passed only on the prices of the morning build) and one is not:
the first 21 Nov group was published the evening before and held, and every
pick in it was clear at both prices. The replay, seeing the whole day at
once, grouped the same legs another way (Alianza Lima for FK Mlada
Boleslav). That is the page's hold (a group stands from the build that first
published it unless a pick fails the rule), not a different rule and not the
price. 23 Nov's empty page is the price: Hammarby shortened from 1.22 to
1.16 and lost its value.

What it means for the 30 Nov read: neither price reproduces the page. The
last pre-start price is closer on 23 Nov and on the second 21 Nov group;
neither reproduces the hold. Read rule 14 v `rule13` at both prices, as the
decisions table already does, and treat a gap of a group or two between the
replay and the record as expected noise of this kind.

## The change

- `tools/card_replay.py`: the live variant writes `legFaults`, each leg's
  `card_fault` reason at the replay's price on the live rule's days
  (`leg_faults`, `live_rule_from`; sports off the Card left out; about 4 KB a
  day in the artifact, not committed).
- `tools/card_review_post.py`: `fidelity_why` under the Fidelity line, a tally
  of the page's unrebuilt groups (a pick refused at the first price / every
  pick clear / a pick not in the pool), each with its reading at both prices
  and its first-published time from the day's archive, then the replay's
  groups the page did not publish read at the last price. The Fidelity line's
  closing words now name the hold beside the price.
- `tests/test_review_fidelity_why.py` (five).

Nothing on the page, no Card rule (`CARD_RULE` 14 until the 30 Nov read), no
record touched.
