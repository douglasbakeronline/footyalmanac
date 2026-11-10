# The Edge flag tested on every sport (10 Nov 2026)

Douglas, 10 Nov 2026, after the green Edge flag shipped for football
(`claude/edge-flag-2026-11-10.md`): "I want you to test and run on all
sports." Result: no other sport passes the gate yet, so the flag stays
football only. One cross-sport pattern is pre-registered and tracked nightly.
Nothing on the page changed.

## Why football alone had evidence

The flag's key condition, the opposition priced 9+, is about how much of a
three-way market the draw takes. Football has five seasons of bookmaker
prices (football-data.co.uk). For every other sport the only prices on file
are the pool archive from 30 Oct 2026 (`groupings-archive/pool-*.json.gz`):
11 days. The sports' prediction archives (`predictions-sports/`,
`predictions-tennis/`) hold no prices at all.

## The tool

`tools/edge_sports.py` reads every settled pool leg where the model's pick
is also the bookmakers' favourite (`card_replay.pool_legs`, first real
price; `--recover` adds legs before 10 Nov at their last price, approximate)
and for each sport reports landed v the bookmakers' chance, return at the
average and best price, z and a day-bootstrap p(loss): overall, by price
band, by the model's gap to the market, by the opposition's price, and for
two candidates:

- **candidate**: the flag without the opposition condition (price 1.15-1.90,
  bookmakers 60%+, model no more than 5 points above them);
- **short**: the short favourite, 1.15-1.30, registered on this first read
  because it was the band above the bookmakers in most sports.

The gate for switching a sport's flag on: 100+ legs, landed above the
bookmakers, best-price return positive, p(loss) at most 0.30.

## The read, pool 30 Oct to 9 Nov

First real prices only (548 favourite legs):

| sport | candidate legs | landed v bookies | best price | short legs | landed v bookies | best price |
|---|---|---|---|---|---|---|
| football | 100 | 75.0% v 67.9% | +3.0% | 28 | 85.7% v 75.3% | +6.2% |
| tennis | 27 | 59.3% v 69.6% | -18.1% | 5 | 80.0% v 76.3% | +0.6% |
| NBA | 5 | 40.0% v 70.2% | -46.2% | 1 | | |
| NFL | 12 | 91.7% v 75.9% | +16.2% | 7 | 100% v 80.0% | +20.1% |
| college football | 44 | 79.5% v 72.3% | +4.8% | 19 | 100% v 78.5% | +22.4% |
| college basketball | 10 | 70.0% v 70.5% | -4.9% | 2 | | |
| all sports | 198 | 73.7% v 69.8% | -0.3% | 62 | 90.3% v 77.0% | +11.0% |

With `--recover` (1,300 legs, approximate): candidate over all sports 476
legs, 71.6% v 70.5%, -3.1% at best; tennis 99 legs, 66.7% v 70.2%, -9.6%;
NBA 39 legs, -7.4%; the short favourite over all sports 162 legs, 83.3% v
77.8%, +2.0% at best, p(loss) 0.26, which clears the gate's numbers but on the
same sample the band was chosen from, so it proves nothing yet.

## Decisions

- **No flag for tennis, the NBA, the NFL, rugby or college sports.** None
  passes on its own; the NFL and college football look good on 12 and 44
  legs, far under the gate. Tennis favourites land under the bookmakers
  again (the same leak as on the Card).
- **The short favourite (1.15-1.30) is tracked out of sample.** For football
  it has prior support (the Card's `short` variant, 1.15-1.35, was the one
  band positive on both football-data seasons). The nightly Card review
  prints every sport's candidate and short lines on legs from 11 Nov only
  (`card_review_post.edge_section`), and a sport whose line passes the gate
  there gets the flag, with its numbers, in a release.
- The football flag's own conditions are unchanged. Its tested-league legs
  are scarce in the pool (most pool football is the wider API-Football
  leagues), so the pool cannot grade it yet; the archive can
  (`predictions/<date>.json` `edge`).
