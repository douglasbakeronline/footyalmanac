# The day before's two-day group, held after midnight (15 Nov 2026)

Build session, 15 Nov 2026 21:17 London.

## What was wrong

On 15 Nov the Card staked the same two picks twice. 14 Nov's two-day group
(Card 2x at 2.36: VVV-Venlo, Pistoiese v Coriano, Philadelphia 76ers v
Indiana Pacers; first built 14 Nov 12:12 UTC, locked at VVV-Venlo's 19:00
start) held two 15 Nov picks. A second 15 Nov Card 2x (2.09: Pistoiese,
Manacor, the 76ers) was first built at 00:44 UTC on 15 Nov.

`CARD_SPAN` (`claude/card-span-2026-11-12.md`) keeps a two-day group's next-day
picks off the next day through `span_taken`, but `groupings.main` only carried
it from a day the same build had just built. After midnight the build's dates
start at the new day, so the day before (and its two-day group) was not among
them and `span_taken` started empty. Every first build after a two-day group
could repeat its picks. Both copies of each pick are in the record: a loss on
Pistoiese or the 76ers costs both groups.

## The fix

- `groupings.span_held(date, prev, archived)`: the events of every Card group
  from the day before whose `span` covers `date`, from the day before's archive
  (locked groups) and its last published groups. `main` seeds `span_taken`
  with it for the first day built. On the live archive,
  `span_held("2026-11-15")` returns the three events of 14 Nov's group.
- `tools/card_integrity.py` `card-pick-twice`: a fixture in two Card groups on
  one day (a two-day group counts on both days), from `TWICE_FROM` 16 Nov, so
  the nightly Card review opens an `office-backlog` issue if it ever recurs.
  15 Nov's own double is recorded here instead of re-flagged every night.

Tests: `tests/test_card_span.py` (two new), `tests/test_card_integrity_twice.py`.

## Not changed

No Card rule (`CARD_RULE` stays 11), no constant, nothing in the record. The
15 Nov groups stand as published and are graded as they were staked: the
record is never edited by hand.
