# The Card's legs by sport, in the record (9 Nov 2026)

Scheduled build session, 9 Nov 2026 morning. Douglas's objective: consistent
returns on the group accumulators. CLAUDE.md's delegated decisions (9 Nov)
keep tennis on the Card with a tripwire: when tennis Card legs reach 50 and
sit two standard errors or more under quote, the next session takes tennis
off (`CARD_SPORTS_OFF`). Until now that count lived in a session's scratch
arithmetic; the record carried only groups, not legs by sport.

## What shipped

- `groupings.card_legs_by_sport(days)`: over the Card's full rule (not wide,
  not late), each pick once a day, settled legs by sport: legs, landed,
  expected, rate, quoted, `z` (landed against expected in standard errors)
  and `tripwire`, true at `CARD_FLOOR_N` (50) legs or more with `z` at or
  under `CARD_FLOOR_Z` (-2.0), the Daily List's rule for taking a sport off.
  Written to `groupings-record.json` as `cardLegsBySport` by `grade()`.
- The Bets scoreboard ("Is it working?") shows a tile a sport: landed v
  quoted, z, and the state in words (on or above quote; under quote, inside
  noise; two standard errors under with the legs to go; fired).
- The nightly Card review issue (`tools/card_review_post.py`) prints the
  table and says in bold when a tripwire has fired, so the next build
  session acts on it from the issue.

Nothing is fitted (Rule 1): it is a tally of the scoreboard, and the rule it
reports is the one already written down.

## The read, record at 9 Nov 2026 (read only)

| sport | legs | landed | quoted | z |
|---|---|---|---|---|
| tennis | 40 | 22 (55%) | 71% | -2.23 |
| NBA | 32 | 24 (75%) | 71% | +0.51 |
| football | 30 | 22 (73%) | 67% | +0.71 |
| rugby | 5 | 3 (60%) | 72% | -0.59 |

Tennis is two standard errors under on 40 legs, ten short of the floor. At
the current rate (about one tennis leg a day since rule 6) the floor is
reached around 19 Nov; if the shortfall holds, tennis comes off the Card
then. Football and the NBA land above their quotes. (CLAUDE.md's "25 of 44"
was a wider cut: with the wider-rule and late groups in, tennis is 29 of 48.
The tally here is the full rule only, the record the floor applies to.)

## Not changed

`CARD_SPORTS_OFF`, `CARD_SPORT_MIN`, `CARD_RULE`, any record file. The
decision stays as delegated: the session acts at 50 legs, not before.
