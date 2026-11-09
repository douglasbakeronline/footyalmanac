# The live Card against the pool archive (9 Nov 2026)

Scheduled build session, 9 Nov 2026 (11:20 UTC). Read only: `groupings-record.json`
and `groupings-archive/pool-*.json.gz`; nothing fitted, no rule changed.

## What was found

`tools/card_replay.py` (pool from 30 Oct, #159) rebuilt **no live Card at all**
on any day under rule 6, while the live Card built a group on every day from
6 to 8 Nov. The reason is the pool, not the replay: the legs the live Card
actually picks were mostly archived as the model's estimate, before any
bookmaker priced them, and before 9 Nov the pool never recorded the first
real price.

Each live Card leg looked up in the pool (the Card day's file and the files
either side, since a pool file is the start's UTC date and a late US game
sits in the next one):

| Card days | Card legs | in the pool at a real price | estimate only |
|---|---|---|---|
| 30 Oct to 8 Nov | 59 | 17 | 42 (71%) |
| 4 to 8 Nov | 23 | 3 | 20 (87%) |

The missing ones are nearly all NBA and tennis, which is where the live Card's
volume is (`claude/card-seasons-2026-11-09.md`: the rule 6 Card on football
alone makes one group in five seasons). A replay that cannot see those legs
compares every variant on a different, football-heavy Card, so a 30 Nov
verdict read off it would be about the wrong thing.

## What the fix already in place does, and what this adds

The `priced` block (#159, 9 Nov) records the first real price on legs first
archived as estimates. It is working: in `pool-2026-11-10` all 8 NBA legs and
19 of 37 priced college basketball legs carry it. So from 10 Nov
(`PRICED_FROM`) the live Card should be fully replayable.

This change makes that a nightly check rather than an assumption:
`tools/card_integrity.py` gains `card-leg-unreplayable`, one finding for
every Card leg from `PRICED_FROM` that the pool does not hold at a real
price ("not in the pool" or "pool holds the model's estimate only"), and
prints the coverage as "x of y". A finding opens the usual `office-backlog`
issue through the nightly Card review.

## Two tennis variants, pre-registered

Tennis legs are the Card's one consistent leak (22 of 40 full-rule legs v 71%
quoted, `claude/card-legs-by-sport-2026-11-09.md`). The tripwire takes tennis
off at 50 legs and two standard errors under; the 30 Nov review should also
see the alternatives on the pool, so `tools/card_replay.py` now carries:

- `notennis`: tennis added to `CARD_SPORTS_OFF` (the tripwire's action);
- `tennis80`: tennis legs at 80%+ on model and tested rate (live 75%).

They are registered now, before the pool holds enough real-priced tennis legs
to read them. For the record only, the approximate `--recover` read (legs at
their last price with a typical margin, 6 comparable days): both +0.74 units a
day against live, p(worse) 0.22, on 3 groups. Far too few to act on; the
gate is 100+ legs and both samples.

## What would change the reading

At the 30 Nov review, run `tools/card_replay.py --since 2026-11-10` (no
`--recover`): if `card-leg-unreplayable` stayed silent, the live variant
there is the real Card and every comparison is on its legs.
