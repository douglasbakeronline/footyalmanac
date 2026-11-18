# Card price gaps under rule 13 (18 Nov 2026)

Build session, 18 Nov 2026. Follows `claude/card-price-gaps-2026-11-12.md`.

## What was wrong

The nightly Card review's price-gap section (`card_funnel.gap_lines`) closed
with "A priced leg must still clear the value demand". Since `CARD_RULE` 13
(17 Nov 2026) there is no value demand (`CARD_MODEL_EDGE` None), so a leg
kept off only by a missing price would reach the Card once priced inside
`CARD_ODDS`. The line now reads the live rule.

## What was added

The section now says how many of the started-day legs fell on days the live
Card left empty (`card_review_post.empty_card_days`: started days from 10 Nov
to yesterday with no full-rule Card group in `groupings-archive/`), and
whether those were enough on their own for a group.

## The read at 18 Nov (pool from 10 Nov, read under rule 13)

- 108 legs pass every Card condition but the price: 39 on started days
  (football 38, tennis 1), 69 still to come (football 59, NBA 10).
- 6 of the 39 fell on 4 empty days (11, 12, 13 and 16 Nov), at most 2 on one
  day, against the 3 picks a group needs.
- The started-day gaps are lower leagues no UK book prices (NB III, Oberliga
  Bayern Nord, Tercera RFEF, Regionalliga SudWest, Ýokary Liga): the
  `noOdds` cause in `claude/football-unpriced-2026-11-14.md`. A fuller feed
  would not make them bettable at William Hill.

So the 12 Nov conclusion holds under rule 13: price coverage is not the
Card's lever. Days 11 to 13 Nov ran under rules 8 to 11 with the value
demand; they are read here under today's rule, as the funnel reads every day.

## Files

`tools/card_funnel.py` (`gap_lines(g, empty=None)`), `tools/card_review_post.py`
(`empty_card_days`), `tests/test_card_funnel_gaps.py`, `tests/test_empty_card_days.py`.
Advisory; no Card rule, record or page changed.
