# Belgium: undated rounds kept the Pro League off the board (14 Nov 2026)

## What was wrong

openfootball's Belgian 2026-27 file (`belgium/master/2026-27/be1.txt`) dates
rounds 1 to 7 only. Rounds 8 to 34 are listed as "(datum TBC)" with no date
line, and `parse_fixture_txt` drops an undated match on purpose (shown wrong
is worse than not shown, the 16-19 Sep bug that stamped 250 Belgian fixtures
with one Saturday). So the file's last dated fixture is 20 Sep 2026, and:

- no Belgian Pro League fixture has been on the board since 20 Sep
  (`predictions/`: 1 to 9 a day to 20 Sep, none after), so none could reach
  the Daily List, the Edge flag or the Card, whose wider leagues are in since
  rule 11;
- the lagging-league fill of 13 Nov (`build.fill_lagging`) could score only
  the 61 dated fixtures; ESPN's other 37 results (rounds 8 onwards) had no
  fixture to fill and were dropped, so every club's table stopped at seven
  games of eleven played.

#294 (13 Nov) fixed the parse junk and the five aliases; this is the rest.

## The fix

- `build.exhausted_codes`: an openfootball league (same eligibility as
  `lagging_codes`) with no fixture dated on or after the build's first day.
  On 14 Nov only `be.1` (checked against every eligible 2026-27 file; Austria
  and Greece would qualify after their regular seasons end in Feb / Mar, and
  get their split rounds the same way).
- `build.fill_window`: ESPN's fixtures in the build window are added to that
  league's rows under openfootball's spelling, unless the file already lists
  the same home and away clubs within 21 days. All or nothing on names
  (Rule 6), a `::warning::` naming any club that misses.
- `fill_lagging(..., append=True)` for an exhausted league: a result for a
  pair the file does not list at all (an undated round) is added as a row.
  A pair the file lists anywhere is never added, so a dated fixture is never
  counted twice.

## Checked here, on the cached ESPN rows (`current/be.1-2026-27.json`, 99 results to 13 Nov)

- Every ESPN spelling maps to one openfootball club (Waasland-Beveren to SK
  Beveren, Racing Genk to KRC Genk, Union St.-Gilloise to Royale Union
  Saint-Gilloise, ...), none twice.
- Before: 61 filled, 37 dropped. After: 61 filled, 37 added, 0 dropped; 99
  scored rows, no ordered pair twice, every club on 11 games.

Not checked here: the window fetch (the sandbox cannot reach ESPN). The first
CI build should print `window be.1: N fixture(s) from ESPN` and
`lag be.1: 98 result(s) filled`. The Belgian top flight is in the
international break on 14-15 Nov, so expect the first fixtures on the board
from the 20-22 Nov round once it is inside the 7-day window.

Not changed: the model, its constants, the calibration, any Card rule.
