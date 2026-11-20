# Predictions archived under a round's date, never graded (20 Nov 2026)

Build session, 20 Nov 2026 16:40 UTC.

## What looked wrong

The results ledger's ungraded report (`results-ledger.json.gz` `ungraded`) listed core-league football with no result days after the start: six Premier League games archived for Saturday 7 Nov (Crystal Palace v Liverpool, Sunderland v Chelsea, Manchester United v Aston Villa among them), La Liga's 25 Oct and 1 Nov rounds, Ligue 1 and Brazil's Serie A through October.

## Why

`score.py` keys a result on (league, date, home, away). openfootball dates some leagues by round: the Premier League a nominal Saturday 15:00, La Liga and Brazil's Serie A by round with no time (`claude/premier-league-nominal-times-2026-11-19.md`, `claude/football-no-kickoff-2026-11-19.md`). Its 2026-27 files stopped scoring after 20 Sep, so these games are graded only by `live_results`, which asks ESPN for the archived day (and the day before) and needs the same date. Crystal Palace v Liverpool was archived for 7 Nov and played on 8 Nov (1-3): the build's ESPN cache in `current/en.1-2026-27.json` has it, the grader never looked.

Since 19 Nov (`build.fill_untimed`, `AF_RETIME`) new fixtures in those leagues carry API-Football's date, so the gap is in the archive before then, plus any league still dated by round.

## What changed

`score.nearby_results`: for every league with an ungraded past prediction, read the season-so-far cache the build commits in `current/`, map ESPN's spelling to the archive's all or nothing (`build._map_names`, Rule 6), and grade a prediction from the one result of the same home and away clubs within `NEAR_DAYS` (3) days. Kept in `current/settled-results.json` like a live result. Refused:

- a result whose own date has a prediction of the same pair: that row owns it (780 ungraded nominal copies sit beside a prediction archived on the real date; none is graded twice);
- a result two predictions could claim, or a prediction two results could;
- a match played earlier than the archived date when the prediction was not published before that day began (UTC): its real kick-off is unknown, so the price cannot be shown to be early. 22 such, Barcelona v Alavés among them (archived 1 Nov, played 31 Oct, last copy published 31 Oct 05:30).

## The numbers (archive and record at 20 Nov)

46 predictions graded that were not: Brazil's Serie A 31, Premier League 5, Ligue 1 4, La Liga 2, and one each in Brazil's Serie B, Colombia, Portugal and the USL Championship. None a Daily List pick, one reserve, three at 60%+. Two leagues refused whole on names: Spain's Segunda (Málaga) and MLS (the All-Star game's sides). The Ligue 1, Colombian and USL games were archived with a real kick-off and played a day later (moved), published before the first time, so before the second. Counted offline against the committed `record-graded.json`; the first CI `score.py` prints its own count ("graded from a result dated off the archive's round date").

The Card's own grading (`groupings.settle`) is separate and its integrity check found no pending leg, so the Card's record does not change. The Daily List record does not change. This is the board's record and the ledger made more complete, and an honest one: the missing rows were lost for a date-keying reason, not at random by result, but they were not a list or Card sample either.

## Not changed

The model, any constant, the tier ladder, the Card, `live_results`, how the build fills lagging leagues. `NEAR_DAYS` reads only the committed cache; no new fetch.

## Roll back

`git revert` the merge. Rows already written to `current/settled-results.json` stay graded after a revert (`score.py` keeps a settled result for any prediction the source has not scored); to take them out, drop those keys from that file in the same revert.
