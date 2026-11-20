# The Championship and Serie A take API-Football's kick-offs (20 Nov 2026)

## What the 07:01 UTC build showed (run 44691945744)

The first named "football kickoff:" line (the read the 03:17 session asked for,
`claude/kickoff-legs-racing-feed-2026-11-20.md`):

- 2026-11-21 Championship (England): Sheffield United v Watford, board 12:30 UTC, API-Football 15:00.
- 2026-11-22 Serie A (Italy): Bologna FC 1909 v Udinese Calcio, board 17:00 UTC, API-Football 14:00.

Published fixture listings (starting11.com, searched 20 Nov) give Sheffield United v Watford at 3pm GMT:
API-Football is right and openfootball's 12:30 is stale. Bologna v Udinese could not be confirmed either way
from search. The board's other 21 Nov Championship times (two more at 12:30, eight at 15:00) agreed with
API-Football, so the Championship's file is not nominal like the Premier League's; it is occasionally stale.

## Why it matters for the Card

A `kickoff` miss (both names on API-Football's day, starts 90+ minutes apart) leaves the leg unpriced, so
it cannot reach the Card; neither of these was Card-reachable on this build. The risk is the other side of
the guard: a board time stale by less than 90 minutes is priced and carries the board's start into the Card,
so a group could freeze late (board after the real start) or early. API-Football is the source that already
prices the leg, so its time is the better one.

## The change

- `sources.AF_RETIME` adds `en.2` (API-Football 40) and moves `it.1` (135) here from `AF_UNTIMED`.
  A retime league also fills its untimed rows (`build.fill_untimed`: `retime or not time`), so Serie A's
  untimed 29 Nov round stays covered. Same rules: all or nothing on names, exactly one fixture of the pair in
  the window, TBD times left out, country checked. No extra API calls (the day pool is already fetched).
- `tests/test_untimed.py`: the registry, and a Serie A row at 18:00 Rome retimed to 14:00 UTC beside an
  untimed row filled.

## Not changed

Any Card constant, the 90-minute guard, the matcher, the model. No local build could fetch (sandbox).

## What the next session should read

The next CI build's "untimed en.2:" and "untimed it.1:" lines: a number of fixtures changed, or a
`::warning::` naming unmatched clubs (then the league is left as it was; add the spelling). Sheffield United v
Watford should leave the "football kickoff:" line and be priced.
