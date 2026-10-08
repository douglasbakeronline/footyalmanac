# Sports Almanac: graded predictions for review (2026-10-08)

Every prediction the site published and has since graded, across every
sport, exported on 2026-10-08 by `tools/julius_export.py` from the site's own
grading files. Nothing is regraded or filtered beyond what the site grades.
Site: https://douglasbakeronline.github.io/footyalmanac/

## Files

| File | What |
|---|---|
| `all_picks.csv` | every graded pick, all sports, one row each (2439 rows) |
| `daily_list.csv` | picks flagged for the Daily List (80) |
| `reserve.csv` | picks flagged for the reserve (126) |
| `by_sport/<sport>.csv` | the same rows split by sport |
| `summary.csv` | picks, won, lost, void, hit rate and mean `quoted_chance` by group and sport |
| `by_day.csv` | the same tallies per day, group and sport |
| `calibration_bands.csv` | hit rate against mean `quoted_chance`, in 5-point bands of `confidence`, by sport |

## Columns (`all_picks.csv` and the files split from it)

| Column | Meaning |
|---|---|
| `date` | the event's date as archived (football: fixture date; others: UTC date of the start) |
| `start_utc` | scheduled start, UTC, where recorded (blank for tennis and older football rows) |
| `published_utc` | when the graded price was published, UTC (blank for football rows archived before 2 Oct 2026) |
| `sport`, `competition` | sport, and league / tournament and round |
| `home`, `away` | the two sides (tennis: player A, player B) |
| `pick`, `pick_side` | the side the model favoured (football can be Draw, rarely) |
| `confidence`, `confidence_pct` | the model's probability for its pick, at publication (0-1 and %) |
| `tier` | Strong 70%+, Firm 62%+, Lean 55%+, No read below (football demotes Celtic's Law rows one tier) |
| `tested_rate` | how often calls at this level landed in out-of-sample testing, as shown on the site (tennis and the other sports; football's archive does not record it) |
| `group` | Daily List, Reserve or Board (graded but on neither list) |
| `on_daily_list`, `on_reserve` | 1/0 flags for the same |
| `result` | won, lost or void |
| `mark` | ✓ won, ✗ lost, – void, as on the site's "How it went" pages |
| `correct` | 1 won, 0 lost, blank void (the site's rule; football counts draw readings) |
| `top_pick_correct` | 1 if the top pick itself landed (football: draw readings count 0 here) |
| `quoted_chance` | the model's own chance of `correct`: the pick's probability, plus the draw chance for football rows whose predicted scoreline is a draw. Compare hit rates with this, not `confidence` |
| `winner`, `final_score` | who won (football: team or Draw) and the score |
| `predicted_score` | football only: the model's likeliest scoreline |
| `draw_read` | football only: 1 if counted right because the predicted scoreline was a draw and the game was drawn |
| `verification` | football: `verified` (published before a known kick-off), `verified-by-date`, `legacy-unverified` (archived before publish times were recorded, 2 Oct 2026); others: only prices published before the start are graded |
| `flags` | football `celtic` (a fixture the model is structurally blind to), `unrated`; tennis `retired` |
| `note` | tennis result line, or why a pick is void |

## How grading works

- Only a price published before the start is graded; a later price proves nothing and is left out.
  Where a game was priced several times, the latest pre-start price is graded.
- Football is home / draw / away. A pick is right if the top pick landed, or if the predicted
  scoreline was a draw and the game was drawn (`draw_read`; the site's rule since 6 Oct 2026).
  The top-pick-only hit rate is `correct` with `draw_read` rows counted as misses.
- Tennis: walkovers and abandoned matches are void. The other sports: a tie is void.
- The **Daily List** is picks whose level landed at least the bar in testing (80% for most
  football and sports; 75% for tennis from 8 Oct and the wider API-Football leagues), with
  blind spots, draws and tennis qualifying left out. The **Reserve** is clean picks under the bar,
  Firm (62%) or better. Each group is graded on its own; the reserve never counts in the list.
- Groups are the flags set when the price was published. Until 8 Oct 2026 the site's front page
  showed at most 20 picks a day, so on a busy day some list-flagged picks were graded but not shown.

## Things to know before reading the numbers

- Football rows before 2 Oct 2026 carry no publish time (`legacy-unverified`); they were archived
  by the daily build before kick-off, but that cannot be proved from the file.
- Tennis ratings missed results between 2 June and 8 Oct 2026 (fixed 8 Oct); tennis prices
  before then were made on stale ratings.
- The Daily List bar and the reserve began on 27-30 Sep 2026, and the tennis bar moved from 80%
  to 75% on 8 Oct; early days are thin.
- No bookmaker prices are in any model or in this export.

Source files as of: football 2026-10-08T14:01:20, tennis 2026-10-08T14:01:26Z.
