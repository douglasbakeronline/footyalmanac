# Round-date rows graded from the copy published the day before, and the Süper Lig's two spellings (21 Nov 2026)

## What was wrong

The 07:01 UTC build's ungraded report (`ledger.py`) listed core-league
football 3 to 14 days past its start with no result: La Liga 5, the Süper Lig
5 (Valencia v Real Madrid, Galatasaray v Amed, all archived under 8 Nov), the
Premier League's Everton v Coventry City. The committed ESPN cache holds every
one of those results, played 6 or 7 Nov. Two faults in `score.nearby_results`:

1. **Played the day before the round date, refused as late.** A match played
   before its archived date is graded only when the prediction was published
   before the match day began (UTC), as its real kick-off is unknown.
   `load_predictions` keeps the *last* build's copy of every fixture, and for
   La Liga's 8 Nov round that copy was written at 05:53 UTC on 7 Nov, the match
   day. The build at 23:49 UTC on 6 Nov had published the same fixture, so a
   copy that passes the guard was in the archive all along.
2. **The Süper Lig archived under two spellings.** Until October the league's
   rows carried ESPN's spelling (Eyupspor, Amed SFK, Konyaspor); since then
   openfootball's (Eyüpspor, Amed, Atiker Konyaspor). The all-or-nothing name
   map ran over the whole season's predictions, so `match_team` sent each
   cached club to its exact ESPN spelling and November's rows never met their
   results.

## The change (`score.py`)

- `earlier_copy(key, before)`: the latest archived copy published before the
  match day, read from `predictions/<date>.json` dated before it, newest
  first, at most 10 days back, only a copy `verification` grades. When the
  last copy fails the late guard, `nearby_results` grades that earlier copy
  instead and puts it in `preds`, so the row judged on the record is the price
  shown in advance (its probabilities, list and reserve flags, published
  time). No earlier copy: left out as before.
- Pending predictions are read in runs of nearby dates (`_runs`, split where
  dates sit more than `NEAR_DAYS` apart), and each run maps names over the
  predictions archived near its own results. A club with no archived row near
  those dates takes the whole season's spelling, as before; a near spelling
  always wins. All or nothing still holds.
- `_owned`: a result whose own date has another prediction of the same clubs,
  under any spelling (`match_team` both ways), belongs to that prediction. The
  October rounds sit on the archive twice (Caykur Rizespor v Fenerbahce on 10
  Oct, Çaykur Rizespor v Fenerbahçe on 11 Oct); the exact-name check alone
  could have graded the round-date copy beside it.
- `lag_results` passes `earlier` through and keeps the copy it chose.

## Measured on the committed archive (21 Nov 2026, settled cache as results)

| | before | after |
|---|---|---|
| graded by `nearby_results` | 60 | 126 |
| refused as late | 22 | 0 |
| graded from an earlier copy | 0 | 39 |

The 66 newly graded: Süper Lig 25, La Liga 15, Austria 8, Greece 6, Scotland
5, Brazil 4, Belgium, the Premier League and Ligue 1 one each; 39 in October,
26 in November, 1 in September. The picks won 40 against 32.1 expected. No
Daily List pick, 4 reserve, no Card leg (the Card grades from its own
archive). 44 verified by date, 21 verified, 1 legacy. Nothing lost: every row
graded before is still graded with the same result. Checked against
`record-graded.json`: none of the 66 has a twin within 3 days under any
spelling already graded.

## Found, not fixed here

The record already grades 27 fixtures twice under two spellings on the same
day or within 3 days (National League 8, India 6, China 3, A-League 3,
Süper Lig 2, J1 2, Norway, the Champions League and one API-Football league),
none on the Daily List: Besiktas v Kocaelispor and Beşiktaş v Kocaelispor on
11 Oct, Southend United and Southend on 30 Sep. That is `load_predictions`
keying on names, not `nearby_results`; filed as an issue for its own change.

## What the first CI build should print

The score step's line: about 126 graded from a result dated off the archive's
round date, about 39 from an earlier copy, 0 left out as late. The next
ledger's ungraded report without es.1 and tr.1 in its top competitions.
