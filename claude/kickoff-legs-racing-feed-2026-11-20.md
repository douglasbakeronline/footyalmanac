# Kick-off misses named, OL Lyonnes, and the racing feed's plan (20 Nov 2026)

## What the 03:08 UTC build showed (run 44665628327)

- `football unpriced: ... noFixture 4 (D1 Arkema 1, MLS 1, NWSL 1); kickoff 2 (Championship (England) 1, Serie A (Italy) 1)`.
- `football Card unpriced: 2`: OL Lyonnes v Strasbourg (D1 Arkema, 74%, 22 Nov) and Nashville v FC Cincinnati (MLS, 72%, 22 Nov).
  OL Lyonnes sat under noFixture beside "Lyon W v Strasbourg W": a spelling. Nashville v Cincinnati had no fixture
  near on API-Football's day (the play-off fixture may not be set yet); left alone.
- The two `kickoff` misses (both names on API-Football's day, kick-offs 90+ minutes apart) were counted but not
  named, so a league with nominal board times (as the Premier League's were, `sources.AF_RETIME`) could not be
  spotted from the log.
- `racing: racecards/standard answered 401 ... racecards from racecards/free`, `results answered 401: Standard Plan
  required`, `85 races on 2 day(s), 0 tips`. The free plan sends racecards with no bookies' prices and refuses
  results, so the tab can make no tip and grade nothing, and it showed "0 tips" with no reason.

## The change

- `groupings.AF_SPELLINGS` adds `"OL Lyonnes": "Lyon W"`. Both names and the kick-off are still required.
- `price_football` names each `kickoff` leg (`football.kickoff` in `groupings.json`, "football kickoff:" in the
  build log, up to `NOFIXTURE_KEEP`): date, competition with country, both teams, the board's UTC time,
  API-Football's time(s), and whether the leg is Card-reachable. The 90-minute guard is unchanged: without a
  league check in `price_football`, the time is what keeps a women's or reserve fixture of the same names from
  being priced as the senior game.
- `racing.feed_of` / `feed_note`: the racecard plan that answered, whether any runner carried a price, whether
  results were refused; `racing.js` carries `feed` and a `note`, and the tab shows the note above the boards
  (checked at 1280 and 400 wide).

## Not changed

Any Card constant, the matcher's rules, the racing model or tip rule, the record.

## What the next session should read

The "football kickoff:" line. A core league that shows repeatedly with the board on a round hour and API-Football
elsewhere is nominal: add it to `sources.AF_RETIME` (tests in `tests/test_untimed.py`). Racing needs The Racing
API's Standard plan (prices and results) before it can tip or grade: Douglas's call.
