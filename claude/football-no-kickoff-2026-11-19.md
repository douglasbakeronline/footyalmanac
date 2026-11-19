# Football legs with no kick-off time, and the second spelling read (19 Nov 2026)

## What the 07:13 UTC build showed (deploy run 44478001048)

- football unpriced: noOdds 271, noFixture 14, moved 9, kickoff 6. The four
  spellings fixed in #414 no longer appear.
- the twelve named noFixture legs held six more spellings, each beside its
  fixture in `near`, in leagues the Card admits:

| board | API-Football | league |
|---|---|---|
| Royale Union Saint-Gilloise | Union St. Gilloise | Pro League |
| Hertha Berlin | Hertha BSC | 2. Bundesliga |
| Universidad Católica | U. Catolica | Chile |
| Liga de Quito | LDU de Quito | Ecuador |
| Montevideo City Torque | Atletico Torque | Uruguay |
| West Ham United | West Ham W | WSL |

  The rest (Brentford v Everton, three Brazilian Serie A games, OL Lyonnes v
  Strasbourg, Sporting Cristal v Cienciano) had no fixture sharing both names.
- the nine `moved` legs are La Liga (3), Süper Lig (2), Brazil's Serie A (2),
  the Premier League and D1 Arkema, one each.

## The finding behind the second change

`predictions/2026-11-19.json` has 29 football rows with no kick-off, and they
are every row of three leagues: Brazil's Serie A (10 of 10), La Liga (10 of
10) and the Süper Lig (9 of 9). openfootball dates their rounds before the TV
picks, with no time. Four are list or reserve picks (Trabzonspor v Eyüpspor
86% on the list; Galatasaray v Samsunspor, Barcelona v Villarreal, Real
Madrid v Celta in the reserve).

A football leg takes its `when` from the board row's kick-off, and every
"has it started" test in `groupings.py` reads `(parse(l["when"]) or after) >=
after`: a leg with no time never starts. Priced (API-Football matches a leg
with no time on names and date alone), such a leg could reach the Card, and a
group holding it would stay open, re-checked and rebuildable, after the game
had kicked off, and the pool would offer it to the next build too. None has
yet: every one of the 540 Card legs in `groupings-archive/` carries a time.

## What changed

- `price_football`: a leg matched to an API-Football fixture that has no
  board kick-off takes the fixture's (`when`, `whenSrc` "API-Football"). The
  board row is not changed. A fixture API-Football marks "TBD" (time to be
  defined, a stand-in time) gives none. Counted as `football.timed`, logged as
  "football timed:".
- `card_fault` (rule 7+): a leg with no `when` is refused, "no kick-off time
  or order of play yet, the start is unconfirmed", the football twin of the
  tennis `timeEst` guard. The funnel reads it as `no-time`.
- `recheck_card`: a published leg's kick-off stands when this build could not
  read it again, as its price does (`stale_price`).
- `whenSrc` joins `POOL_KEYS`, so the pool says where a start came from.
- `AF_SPELLINGS`: the six spellings above.

## Not changed

No `CARD_*` constant and no `CARD_RULE` bump: this is a start-time integrity
guard, not a selection rule, and a bump would rebuild every open group. The
replays (`card_replay.py`, `card_legs_history.py`) read `model_fault`, not
`card_fault`, so they are unchanged. The board, the Daily List, the archive's
`kickoff` and `score.py` are unchanged: a no-time list pick is still graded
`timing-unverifiable` as before.

## What next

- The next CI build's "football timed:" line says how many legs took a time.
- The board's own dates for these three leagues are the round's nominal date
  (`moved` shows API-Football a day either side). Taking the date and time
  from API-Football for the board itself is a `build.py` change that also
  moves a Daily List pick between days; it needs its own test against the
  archive and is filed as an issue, not done here.
