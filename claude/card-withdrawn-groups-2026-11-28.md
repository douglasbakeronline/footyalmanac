# Card groups withdrawn after publication (28 Nov 2026)

Build session, 28 Nov 09:17 London slot.

## What happened on 27 Nov

The page published a Card 2x for 27 Nov at 20:11 UTC on 26 Nov: Al Qadsiah
(v Al Fayha, 14:20 UTC), Philadelphia 76ers (at Indiana) and Detroit Pistons
(v Milwaukee), William Hill 2.55, two units. It held over 11 builds and was in
the 21:00 UK night briefing's window. At the 07:07 UTC build Al Qadsiah left
the picks clear of the rule (`card-short.json`), and the publication log marks
the group `gone` at 07:10. The cause is rule 14's value demand
(`CARD_MODEL_EDGE` 0.0, the model at or above the bookmakers' fair chance),
re-read at each build's price: Al Qadsiah shortened from 1.19 to 1.17 and the
fair chance moved from 77.1% to about 78%, past the model's 77.2 to 77.4%.
A fraction of a point. The remaining picks paid over the 2x band ("long",
3.38), so the day ended with no Card group.

All three picks won. At the last shown price the group returned +155% on its
two units. The record shows 27 Nov as an empty day, and before this change
the nightly review said nothing: `shown_not_archived` (26 Nov) names groups
the page showed that never reached the archive, but skips withdrawn ones by
design.

This is the rule working as written (CLAUDE.md: a group "is open until its
first kick-off, re-checked on every build and holding unless a pick fails the
rule"). The point is visibility. A reader who backed the group when it was
shown still holds the bet, whatever the page does next.

## What changed

`tools/card_review_post.withdrawn_card_groups` reads the publication log for
full-rule Card groups taken off before their first pick started whose picks
no archived group of the day holds. For each one it reports when it was shown,
the withdrawal time, the picks no longer clear at the build that withdrew it
(the page's own read in `card-short.json`), each pick's result on the results
ledger, and the return at the page's stake and last shown price. It is one
line in the review's "live Card" section, after the never-archived groups.
Nothing enters the record (Rule 1) and the empty-day count is unchanged.

`shown_results` now compares starts as instants. The publication log keeps
some legs' starts without seconds (`2026-11-28T00:30Z`) where the ledger
writes `00:30:00Z`, so the exact string match found no row for those legs.

## What this cannot say yet

The publication log has recorded withdrawals only since 26 Nov, so this is
one group. Whether holding a published group through a small value-demand
miss would pay is a rule question. It would need a pre-registered variant
(a hold band on `CARD_MODEL_EDGE` for published groups) and the gate, and
the pool replay cannot test it, because it reads each leg at a single price.
Nothing to act on before the 30 Nov read. When the withdrawn line reaches 10
settled groups, set their landed rate beside the model's number. If withdrawn
groups keep landing at or above it, a hold band is worth pre-registering.

## Files

`tools/card_review_post.py`, `tests/test_review_live_days.py`, this note,
`CLAUDE.md`, `RELEASES.md`. `CARD_RULE` stays 14.
