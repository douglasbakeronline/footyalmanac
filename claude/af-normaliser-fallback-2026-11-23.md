# The one-fixture price fallback reads the build's club normaliser (23 Nov 2026)

Build session, 23 Nov 03:17 London slot (run 04:35 UTC).

## What the log showed

The 02:41 UTC build's price report:

    football noFixture: 2026-11-25 Serie A: CA Mineiro v SC Corinthians Paulista (near: Atletico-MG v Corinthians)

The game is the one postponed from 21 Nov and moved to 25 Nov by
`build.fill_untimed` (`claude/lookback-postponed-2026-11-23.md`), so the board
had it right; the price lookup did not. `groupings.price_football`'s
one-fixture fallback matches names with `af_same`, which read `same()`
(substring and a 0.8 fuzzy ratio), `AF_SPELLINGS` and `odds.ALIASES`. None of
them bridges "CA Mineiro" and "Atletico-MG". The build's own club normaliser
does: `sources._norm` (aliases, then cities) reduces both to `mineiro`, as it
reduces CA Paranaense and Athletico-PR to `paranaense`, and `odds.name_sim`
(the bulk match) already reads it.

## The change

`af_same` also accepts a pair whose `sources._norm` forms are equal, never one
that reduces to a bare city (`sources._bare_place`). Exact equality only, no
score. Both names and the kick-off must still agree, as before.

## Checks

- On every board name in `predictions/2026-11-*.json` (306 leagues), two
  distinct names in one league share a normalised form, both one club spelled
  two ways (CD Tenerife / Tenerife in Liga F, US Oyem / Oyem): no cross-club
  collision.
- `tests/test_football_unpriced.py`: `test_brazil_club_normaliser` (CA Mineiro
  and CA Paranaense priced from API-Football's spellings) and
  `test_normaliser_never_crosses_clubs`; both fail on the old code.
- Not fixed here: `same()` already treats "AC Milan" and "Inter Milan" alike
  (substring on "milan"); the kick-off and the other name guard it, and it is
  older than this change.

## What it is worth

Brazil's Serie A is not a core league, so under rule 14 no Card leg is gained
today; the price shows on the board and the Daily List, and the next build's
"football noFixture:" line should no longer name the game. No Card rule changed.
