# Sunday's games dated on Saturday fell off the board (22 Nov 2026)

## What happened

The 22 Nov 07:05 UTC build warned: "52 unplayed fixture(s) dated before
2026-11-22 are not on the board". Among them:

| league | openfootball date | API-Football (21 Nov archive) |
|---|---|---|
| en.1 Liverpool v Manchester United | 2026-11-21 | 2026-11-22 16:30 |
| en.1 Hull City v Brighton & Hove Albion | 2026-11-21 | 2026-11-22 14:00 |
| en.1 Brentford v Everton | 2026-11-21 | 2026-11-23 20:00 |
| br.1 CA Paranaense v Clube do Remo | 2026-11-21 | 2026-11-22 19:00 |
| br.1 CA Mineiro v SC Corinthians Paulista | 2026-11-21 | none: on the 15-20 Nov archives with no time, off from 21 Nov (not this cause; not changed) |
| br.1 Botafogo FR v São Paulo | 2026-11-21 | 2026-11-23 23:00 |

The other five were on `predictions/2026-11-21.json` with API-Football's date and
none on `predictions/2026-11-22.json`.

## Why

openfootball dates the Premier League round on its nominal Saturday (and
Brazil's Serie A by round). `build.fill_untimed` (#417, `AF_RETIME` /
`AF_UNTIMED`) gives those rows API-Football's date and time, but only read
rows dated `start` or later. On Saturday's build the 21 Nov rows were in the
window and moved to Sunday and Monday; on Sunday's build they were dated a day
before the window, were never read, and the window cut dropped them. So the
Daily List, the board and the Card lost core-league games on the day they
were played.

## Fix

`fill_untimed` reads unplayed rows from `window` (3) days before the start.
A row dated before the start moves only when API-Football's one fixture of
the pair (within 3 days, as before) is dated in the window; a pair API-Football
still lists before the start is played or postponed and is left alone (the
results fill handles it). All or nothing on names, as before.

Tests: `tests/test_untimed.py` `BeforeWindow` (four cases).

## What the first CI build should show

"untimed en.1" and "untimed br.1" counts higher than the 07:05 build's 9 and
9, and the three Premier League games gone from the unplayed warning. The
other leagues in that warning (es.1, pt.1, gr.1, sco.1 from October) are
postponements in leagues this does not touch.
