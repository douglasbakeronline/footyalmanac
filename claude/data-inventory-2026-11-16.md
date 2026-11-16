# What the Almanac keeps, where, and how big (16 Nov 2026)

Douglas, 16 Nov 2026: "I just want to make sure that we are on top of
tracking as much as we can ... efficient, and cost efficient." This is the
list to check against. Sizes are the files in the repository on 16 Nov; the
whole repository, every version of every file included, is 88 MB on GitHub
(git compresses each file, so a 737 KB day of predictions is held as about
100 KB). Nothing here is loaded by the page unless it says so; an archive is
read only by the script that needs it, so its size does not slow a build.

## Kept, every sport

| What | Where | Since | Size now | Grows by |
|---|---|---|---|---|
| Football predictions as published (every fixture, chances, expected goals, tier, list flag, prices where known) | `predictions/<date>.json` | 20 Aug 2026 | 37 MB (85 days) | ~0.4 MB a day on disk, ~0.1 MB in git |
| Football results, graded | `record-graded.json` (full), `record.json` (summary) | 20 Aug 2026 | 5.2 MB | ~40 KB a day |
| Football half-time scores, for graded fixtures | `periods/football-YYYY-MM.json` | **16 Nov 2026, new** | 0 | ~2 KB a day |
| Football markets (both score, goals lines, win and over 2.5, to nil, double chance, draw no bet, team to score): the model's number and prices | `predictions-markets/<date>.json.gz` | 14 Nov 2026 | 128 KB | ~40 KB a day |
| Football extra bookmaker lines (Asian handicap, handicap result, half-time/full-time, half winners, first-half goals, team totals, win both halves, clean sheets), average and William Hill | inside the same rows, key `x` | **16 Nov 2026, new** | | ~20 KB a day compressed |
| Football results by competition, the season so far | `current/` | Sep 2026 | 1.3 MB | replaced, not grown |
| Tennis predictions as published | `predictions-tennis/<date>.json` | Sep 2026 | 2.4 MB | ~40 KB a day |
| Tennis results with every set score (games handicaps and set betting settle from them) | `tennis-record.json`, `history-tennis/` | Sep 2026 | 0.8 MB + 2.1 MB | small |
| NBA, NFL, rugby, college sports, baseball, WNBA predictions as published | `predictions-sports/<date>.json` | 27 Sep 2026 | 18 MB | ~0.3 MB a day |
| ... with the rating gap the pick rests on (`eloDiff`) and ESPN's line at the time (`line`: spread, total, money lines) | same rows | **16 Nov 2026, new** (the ratings themselves since 27 Sep) | | a few bytes a game |
| Every game those sports played, with scores | `history-sports/` | each sport's history start | 11 MB | ~20 KB a day |
| ... with points by quarter / half / inning (`hp`, `ap`) and the line | same games | **16 Nov 2026, new** | | ~30% more a game |
| Every graded pick of those sports | `sports-graded.json` | 14 Nov 2026 | 0.7 MB | small |
| Every prediction, every sport, with result and pre-start price | `results-ledger.json.gz` | 14 Nov 2026 | 1.0 MB | small |
| The Card: every group as published, every rule version, and the priced pool of every leg | `groupings-archive/`, `groupings-record.json` (`cardByRule`) | 25 Oct 2026 (pool 30 Oct) | 1.6 MB | small |
| Scale picks and groups as published | `scale-archive/` | 15 Nov 2026 | 0.2 MB | small |
| The slip as published | `slip-archive/` | 15 Nov 2026 | tiny | tiny |

## Not kept, and why

| What | Why not | What it would take |
|---|---|---|
| Half-time scores before 16 Nov | the API-Football day files cached before then dropped them | nothing: forward only |
| Quarter scores before 16 Nov | games already walked are not re-fetched | a one-off re-walk (ESPN, free) if ever needed |
| Tennis set-betting and games-handicap prices | no free source; The Odds API charges per call | a paid plan; not worth it until the tracker shows a bet worth pricing |
| The NBA and NFL handicap ladder beyond the main spread | ESPN shows the main line only; API-Sports would cost calls | revisit if the main-spread bet shows an edge |
| Corners, cards, scorers, player bets | the model has no read on them | out of scope |
| Douglas's own bets | needs his slips | a slip log, when he is ready |

## Cost

No new API calls. The half-time score rides in API-Football's day sweep,
which the build already makes; ESPN's lines and period scores come in the
scoreboard calls already made; the football extra lines come in the odds
sweep markets.py already makes. The one cost: markets.py's cache version
moved to 2, so each date's odds sweep is fetched once more than usual on the
first build (well inside the 7,500-a-day allowance).

## Not done, on purpose

Compressing the daily prediction files: git already stores them compressed
(the 88 MB above), so it would save almost nothing and about twenty scripts
read them as plain JSON.
