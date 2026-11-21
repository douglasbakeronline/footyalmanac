# Postponed fixtures re-listed later, not chased as ungraded (21 Nov 2026)

## What was wrong

`ledger.py` groups every football prediction by pairing and treats copies
within `MOVE_DAYS` (10) of each other as one fixture. A game postponed by
more than that comes back as a second fixture, and the first copy can
never meet a result. The ungraded report chased it for a fortnight, then
counted it as "stale" for ever.

The 18:18 UTC build of 21 Nov reported 99 picks to chase and 418 stale.
Two examples:

- Tajikistan's Vysshaya Liga (`af.571`): the whole 7 Nov round was
  re-listed for 27 Nov (Istiqlol v Istaravshan was a Daily List pick, 84%).
- Pistoiese v Coriano (Serie D, 15 Nov), a Card leg settled void as
  "no result" by `groupings.grade`: LiveSoccerTV lists the fixture for
  9 Dec, so it was a postponement.

## The change

`ledger.predictions` marks an earlier football copy with `movedTo` (the
later copy's date) when the same pairing has another copy whose start
falls within `RESCHEDULE_DAYS` (45). It is dropped on any row that has a
result, so a played game followed by a rematch is never marked.
`ungraded` counts marked rows apart as `moved` (`movedByComp`), and the
build log line ends "N re-listed for a later date (postponed, not chased)".
It is a mark only. The earlier pick is never graded from the later game,
because a bookmaker voids a bet on a postponed match.

## Numbers (the committed ledger, rebuilt in the sandbox)

| | before | after |
|---|---|---|
| to chase (3+ days) | 99 | 92 |
| stale (14+ days) | 418 | 227 |
| moved | n/a | 199 (2 list, 10 reserve) |

Of the 199 moved rows, the later copy is already graded for 134 and still
to come for 65. None is missing, which is what you would expect from
postponements. The largest leagues are Kenya (`af.276`, 31), Tercera RFEF
Group 13 (`af.451`, 19) and Group 6 (`af.444`, 12), and Tajikistan (9).

## What is left to chase

Three Daily List picks are still on the chase line, none of them a
grading fault:

- Pistoiese v Coriano. Its 9 Dec copy is not archived yet (the build
  looks 7 days ahead), so it moves across when that copy appears.
- Oregon v Pepperdine and UNC Wilmington v Louisiana (college basketball,
  15 Nov). Neither game is in ESPN's history: Oregon's was postponed for
  travel (KPTV, 15 Nov). `sports.not_played` voids them on 22 Nov,
  `NOT_PLAYED_DAYS` (7) after the start.

No Card rule, record or grading changed.
