# One graded row per match: two spellings counted once (21 Nov 2026, #464)

## The finding

`score.load_predictions` keys every prediction on (league, date, home, away), so a match archived
under two spellings (ESPN's and openfootball's, or API-Football's capitals) was graded twice. On the
committed `record-graded.json` at 21 Nov (13,938 rows): 24 second copies, 13 won v 12.48 expected.

| league | copies | example |
|---|---|---|
| National League (en.5) | 8 | Southend / Southend United, Hartlepool / Hartlepool United, Carlisle / Carlisle United |
| India (in.1) | 4 | SC East Bengal / East Bengal / EAST BENGAL (three copies of two matches) |
| China (cn.1) | 3 | BEIJING GUOAN / Beijing Guoan |
| A-League (au.1) | 3 | MELBOURNE VICTORY / Melbourne Victory |
| Süper Lig (tr.1) | 2 | Besiktas / Beşiktaş v Kocaelispor; Çorum FK / Çorum |
| J1 (jp.1) | 2 | KYOTO SANGA / Kyoto Sanga |
| Norway, Champions League | 1 each | Viking FK / VIKING FK |

None on the Daily List; one reserve copy (the other copy of that match is reserve too and stays);
no Card leg (the Card grades from its own archive). The issue counted 27 with Managua / UNAN
Managua (Nicaragua, af.396): they are two clubs (they met on 2 Nov; one build published both on
14 Oct against different opponents), so both San Marcos results stand.

## The fix

`score.drop_duplicates`, run at the end of `graded_rows`: two graded rows are one match when they
share a league, sit within `NEAR_DAYS` (3) days, carry the same final score and both clubs match
under `match_team` both ways, home and away in the same order. Never joined: names the archive
shows are two clubs (`distinct_names`: they met each other, or one build published both within the
window against opponents that are not one club). Kept: a Daily List copy, else a reserve copy, else
the one published earliest, then the earlier date. Flags never move between copies.

The second copies are written to `record-graded.json` `duplicates` (with the kept copy's key), and
`record.json` `verification.duplicates` counts them. `ledger.result_of` reads `duplicates` and marks
those ledger rows `duplicate`, so they leave the ledger's tallies and are never chased as ungraded
(the ledger keeps old results, so without this the copy would have stayed counted).

## Not changed

The model, the Card and its grading, the Daily List rule, `load_predictions` (the archive is not
rewritten; the dedupe is at grading). The record moves by 24 rows of 13,938.

## What the first CI build should print

`24 graded twice under two spellings, counted once` (or close: new spellings may add a few).
