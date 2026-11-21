# API-Football's short club names in the football price fallback (21 Nov 2026)

## What the build showed

The 03:11 UTC build of 21 Nov named one core-league leg under `noFixture`:

    2026-11-24 Championship: Norwich City v Queens Park Rangers (near: Norwich v QPR)

API-Football spells the club "QPR". The 20 Nov fix (`claude/championship-af-spellings-2026-11-20.md`)
added "qpr" to `sources.ALIASES`, which feeds `build.fill_untimed` (the kick-off), not the price
matcher. `groupings.price_football`'s one-fixture fallback matches with `af_same`, which read only
`same()` and the hand list `AF_SPELLINGS`, so every short form API-Football shares with
football-data.co.uk (QPR, Wolves, Sheffield Weds, Ath Bilbao...) failed there, although
`odds.ALIASES` already spells them out for the bulk match (`odds.match_af` via `odds._tokens`).

## The change

`af_same` now also reads `odds.ALIASES`: when API-Football's name is an exact key, its full form
must pass `same()` against the board name. The other name and the kick-off must still agree, so
an alias widens a spelling and never a club (tests: QPR is not Queen of the South, Wolves is not
Wolfsburg).

## Checks

- `tests/test_football_unpriced.py`: Norwich v QPR (Championship) and Wolves v Fulham (Premier
  League) now price through the fallback; the cross-club guard.
- nametest.py clear; 1,315 tests pass.
- The previous session's open check, read off the committed record: `record.json` went from
  13,042 graded (00:30 UTC) to 13,821 (00:49 UTC), the 778 same-date cache grades plus one, and
  has held since; the 03:11 build printed no Segunda refusal.

## What to look for on the next CI build

"football noFixture:" without Norwich City v Queens Park Rangers, and the leg priced (it is a
Card-reachable league under rule 14 if the model reaches 60%). Nothing on the Card's rule changed.

## Also seen, left alone

- Three Serie B (Italy) fixtures on 24 Nov under `kickoff`: board 18:00-19:00 UTC, API-Football
  14:00 for all three. Three games at one round hour on a Tuesday reads as API-Football's stand-in
  time without the TBD status; not a case for `AF_RETIME` until a later build confirms it.
- `racing results failed: HTTP Error 401`: the Racing API free plan sends no results, as the
  tab's feed note says (`claude/kickoff-legs-racing-feed-2026-11-20.md`).
