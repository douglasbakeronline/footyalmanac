# The Premier League's nominal 15:00 and Serie A's untimed round (19 Nov 2026)

## What the 19:39 UTC build showed

The untimed fill (#425, #431) now works on all three of its leagues: the
19:39 UTC deploy (run 44600510375) logged `untimed br.1: 11`, `es.1: 15` and
`tr.1: 13 fixture(s) took API-Football's date and time`, no tr.1 warning and
no Süper Lig game under "football moved:". #417's close condition is met.

The same build's pricing line left the Premier League as the gap:

- `kickoff 4 (Premier League 2, ...)`: both names found on API-Football's
  day, the kick-offs 90+ minutes apart. In the 21 Nov pool Manchester City v
  Fulham (model 61%, a Card-reachable leg) and Newcastle v Arsenal are
  estimates only.
- `moved 1`: Liverpool v Manchester United, board 21 Nov, API-Football 22 Nov.
- `noFixture`: Brentford v Everton on 21 Nov (no fixture of that pair on the day).

## Why

openfootball's `2026-27/en.1.json` dates the Premier League by round with a
placeholder time: all ten games of the 21 Nov round and all ten of the 28 Nov
round at Saturday 15:00. The board read them as real kick-offs. That costs
more than a price: a Card group holding a 12:30 game counted it as unstarted
until 15:00, so it could be re-checked and replaced after the real start, and
a pick published between the real and the nominal kick-off would grade as
published in advance.

Fetched the same night from openfootball, the times of 20-30 Nov by league:
en.1 20 of 20 at 15:00; it.1 the 29 Nov round 10 of 10 with no time; de.1
and fr.1 a few repeated slots but mixed, nl.1 and pt.1 varied. Only en.1 is
plainly nominal, and only it.1 is untimed.

## The change

- `sources.AF_UNTIMED` adds `it.1` (API-Football 135, Italy, country checked).
- `sources.AF_RETIME = {"en.1": 39}`: leagues whose times are nominal.
  `build.fill_untimed(..., retime=iso)` then also changes a timed row when its
  UTC kick-off (`sources.kickoff_utc`, the league's zone) differs from
  API-Football's, under the fill's own rules: unplayed, today or later, all
  or nothing on names, exactly one fixture of the pair within three days,
  never a TBD time. A row already right is left alone (15:00 UK in November
  is 15:00 UTC; in BST it is 14:00 UTC).
- API-Football names checked against the board's spellings for en.1 and
  it.1 with `match_team`: all twenty Premier League clubs map.

Tests: `tests/test_untimed.py` `Retime` (TV times taken, a moved day taken,
agreeing times left, BST agreement left, nothing without `retime`, all or
nothing on names, the leagues registered).

## Not changed

Any Card constant, the matcher, the 90-minute guard in `price_football`
(it now sees the right time instead), the archive.

## What the next CI build should print

`untimed en.1: N fixture(s)` and `untimed it.1: N` (it.1 only once the
29 Nov round is in the window), no en.1 or it.1 warning, and no Premier
League games under `kickoff` or "football moved:". Brentford v Everton should
leave noFixture if it is played on 22 or 23 Nov. If a spelling shows as
unmatched, add it to `sources.ALIASES`.
