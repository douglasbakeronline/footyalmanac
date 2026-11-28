# A withdrawn Card group said on the page (28 Nov 2026)

Build session, 28 Nov 21:17 London slot. Follows
`claude/card-withdrawn-groups-2026-11-28.md`, which put withdrawn groups in the
nightly review. This puts them where a reader holding one would look.

## What happened

27 Nov's Card 2x (Al Qadsiah, Philadelphia 76ers, Detroit Pistons, Hill 2.55)
was on the Bets tab from 20:11 UTC on 26 Nov over 11 builds and taken off at
07:10 when Al Qadsiah's fair chance passed the model's by under a point (rule
14's value demand, read again at each build's prices). All three won. After
07:10 the Card box said only "No group on this day: ... A blank day is the rule
working." The withdrawal sat in the re-check fold further down ("1 group
dropped by the re-check on this day"), closed after the build that dropped it.
A reader who had placed the group at 20:11 saw it vanish with no word.

## The change

- `groupings.build_card`: each Card re-check log entry keeps `first`, when the
  page first showed the group (both appends: a failed re-check and a pick held
  by the day before's two-day group). Nothing else in the entry changed.
- `index.html` `cardWithdrawnHtml(day)`: on a day whose Card box is empty, every
  Card log entry with a `first` stamp is named under the reason the day is
  empty: kind, price, picks, shown from, withdrawn at, and why. "A bet already
  placed stands as placed; withdrawn groups are not graded in the record."
- Log entries written before this change have no `first`, so the notice starts
  with the first group withdrawn after it ships. 27 Nov's entry is not in any
  live day now.

Display only. Nothing graded, no Card constant touched (`CARD_RULE` 14). Rule 1
stands: the record is the archive, and a withdrawn group never reached it.

## Checked

`tests/test_groupings_card.py` (the log entry carries the group's `first`);
the full suite; nametest; a fast build; the Bets tab rendered with a stub day
at 1280 and 400 wide (the notice sits under the empty-day reason, one 1px rule
above it).

## What it does not settle

Whether a published group should hold through a sub-point miss is the hold-band
question, pre-registered at 10 settled withdrawn groups
(`claude/card-hold-band-row-2026-11-28.md`). This only tells the reader.
