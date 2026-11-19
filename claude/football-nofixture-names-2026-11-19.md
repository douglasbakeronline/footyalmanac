# The first named noFixture read: four spellings and a moved-fixture reason (19 Nov 2026)

#410 named every football leg `price_football` filed under `noFixture`. The
first build to print them (deploy run 44450821083, 19 Nov 03:21 UTC) logged:

- football unpriced: noOdds 273, **noFixture 26** (Serie A 5, La Liga 4, Pro
  League 2), kickoff 6, capped 5.
- the twelve named (the cap, `NOFIXTURE_KEEP`), with the day's fixtures
  sharing one of their names:

| leg (board) | API-Football near | read |
|---|---|---|
| Superliga: AGF v Lyngby Boldklub | Aarhus v Lyngby | spelling (AGF) |
| Championship: Inverness Caledonian Thistle v Ayr United | Inverness CT v Ayr Utd | spelling (Inverness) |
| Pro League: Sporting Charleroi v STVV | Charleroi v St. Truiden | spelling (STVV) |
| Liga F: Dux Logroño v Alavés | Edf Logrono W v Deportivo Alavés W | spelling (the club's old name) |
| Premier League: Liverpool v Manchester United, Brentford v Everton | only women's fixtures sharing a name | not on API-Football's 21 Nov day |
| Brazil Serie A: five games on 21 Nov | none | not on API-Football's 21 Nov day |
| Süper Lig: Galatasaray v Samsunspor | Galata v Orduspor 1967 (another club) | not on its day |

`groupings.same` passes Lyngby, Ayr, Charleroi and Alavés; each of the four
spelt legs failed on one side. These are core and wider leagues the Card
admits (`card_league`), so each was off the Card and the Edge flag for a
spelling alone.

## What changed

- `groupings.AF_SPELLINGS`: board name to API-Football's spelling for the four
  above, read only by `af_same` when a football leg is matched to an
  API-Football fixture. Both names and the 90-minute kick-off check still
  apply, so the alias cannot price a different game
  (`test_af_spelling_still_needs_both_names_and_kickoff`).
- A leg with no fixture on its date whose names both appear on another day in
  the window is counted `moved` (with `afDate`), not `noFixture`, and is
  never priced: the board's source has the date wrong, and the price would sit
  on the wrong day. Logged as "football moved:" and kept in `groupings.json`
  `football.moved`. The Premier League and Brazilian games above are the
  candidates; the next build says which.

## Not changed

`same` itself (used across every sport), `LIVE_NAMES` (the board's names are
right; the gap is API-Football's spelling), any `CARD_*` constant, the page.

## What next

Read the next build's "football noFixture:" and "football moved:" lines. A
`moved` cluster in one league (Brazil's Serie A, rescheduled often) points at
the board's fixture source for that league, a fix in `build.py`, not here.
