# Same-date results from the committed cache, and the Segunda refusal (21 Nov 2026)

## What was wrong

Two faults in `score.nearby_results` (20 Nov 2026, `claude/nominal-date-grading-2026-11-20.md`):

1. **A prediction could not claim a result on its own date.** The guard "never
   when a prediction exists on the result's own date" also caught the
   prediction itself, on the reasoning that a same-date result is graded the
   ordinary way. It is not when the ordinary way lost it: ESPN-only results
   were graded only inside `LIVE_LOOKBACK` (10 days) until the settled cache
   arrived on 6 Oct 2026, so September's ESPN-only and lagging-league results
   fell out and were never graded, though the build's committed ESPN cache
   (`current/<code>-<season>.json`) holds them on the same date. The 20 Nov
   note's "780 nominal copies left alone beside a real-date copy" was mostly
   these: the prediction counted as its own real-date copy.
2. **One stale club refused a whole league.** The build log read
   `es.2: cached results not used, unmatched: Málaga`. The 2026-27 Segunda
   cache still holds June 2026's promotion play-offs (Málaga, since promoted),
   and the all-or-nothing name map ran over every cached result, so no es.2
   result was used. (`us.1` was refused the same way on the MLS All-Star game.)

## The change

- A prediction now takes the one result of its pair on its own date; a result
  on another prediction's date still belongs to that prediction.
- Only cached results within `NEAR_DAYS` of an ungraded prediction enter the
  name map. All or nothing on names still holds over those results.

## Measured on the committed archive and `record-graded.json` (21 Nov 2026)

- **778 predictions graded that were not**, all on their own date: 674 dated
  September, 66 August, 29 October, 9 November. Largest leagues: League One and
  League Two 53 each, the Segunda 37, 2. Bundesliga 31, MLS 31, Argentina 30,
  National League 30, Ligue 2 30, Serie B 30, the USL Championship 30, the
  Belgian Pro League 29, Colombia 29, the Süper Lig 28.
- Timing: 740 legacy-unverified (archived before publish times were kept,
  graded as every row of that age is), 33 verified, 5 verified by date. None
  late (those are filtered before grading).
- They landed **46.5% against 47.7% quoted** (362 of 778): on quote, so the
  record does not flatter itself. One Daily List pick (83.7%, lost), no Card
  leg: the Card's record and replays read the pool and football-data, not
  this.
- No result graded twice: 5 of the 778 have a nominal copy within 3 days, and
  that copy stays ungraded.
- The Segunda's play-off rows no longer block it; a club within the window
  that matches nothing still refuses the league (tested).

## Still ungraded, not this fault

1,751 past predictions remain without a result. The largest group is the
Belgian Pro League's 246 September rows, which are parser debris from the
undated rounds (`--:--  STVV`, `Lommel SK (*)`, Cercle Brugge v five clubs on
20 Sep: `claude/belgium-undated-rounds-2026-11-14.md`), then API-Football
leagues, cups and internationals the cache does not hold. Worth an issue if
the ungraded report keeps counting the Belgian debris.

## Files

`score.py` (`nearby_results`), `tests/test_score_nearby.py` (11 tests, 3 new or changed).
