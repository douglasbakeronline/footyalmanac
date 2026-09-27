# NFL, baseball, basketball, rugby, and the all-sports Daily List — 27 September 2026

## What Douglas asked for

Rugby, NFL, basketball and baseball as tabs; the Daily List to carry the
most likely results across every sport; enough picks every day.

## Why football alone can't fill every day

Club football runs 170-370 fixtures a day at weekends and 17-46 midweek or in
an international break (live build, 27 Sep). At 75%+ that is 1-3 list picks a
day. The fix is sports that play on the days football doesn't.

## sports.py

One module, one model, four sports as config (`SPORTS`). A feed is an ESPN
scoreboard path, its months, the weekdays to walk for history (rugby is
walked Friday-Sunday only; midweek rugby is rare and every other day would be
thousands of empty calls), and season types to skip (1 = preseason in the US
leagues; rugby labels its whole season type 1, so nothing is skipped there).

- **Elo keyed by ESPN team id.** No name matching anywhere.
- HFA (none at a neutral site), 538-style margin-of-victory multiplier,
  regression toward 1500 after 90 days without a game.
- Rugby rates in three pools: club (Premiership, URC, Top 14, Champions Cup,
  Challenge Cup), international (Six Nations, Rugby Championship, tests,
  World Cup), Super Rugby.
- A team needs 8 rated games before its games are priced or evaluated.
- ESPN sometimes lists one game under two ids (Racing 92 v Perpignan,
  3 Oct 2026). `_same_game` de-duplicates on pool, teams and kick-off to the
  minute. Not to the day: that collapsed 1,019 baseball doubleheaders.

`--tune` fits K, HFA, regression and MOV on 1 Jul 2024 - 30 Jun 2025 and
judges on 1 Jul 2025 onward. Gates as tune.py. A sport is published only if
it beats backing the home side; fitted constants replace the defaults only if
they beat them. List threshold: the lowest of 75/80/85% where calls landed
78%+ in both windows with 30+ check calls. `sports.json` holds the result and
is committed by hand; CI never refits it (rule 5).

## Results (check window, never fitted on)

| Sport | Games | Picked winner | Backing home | 75%+ landed | List |
|---|---|---|---|---|---|
| Basketball | 1,322 | 67.5% | 54.5% | 82.9% (293) | 75% |
| Rugby | 731 | 70.6% | 68.9% | 84.0% (232) | 75% |
| NFL | 317 | 63.5% | 54.7% | 77.4% (62) | 80% (80.7% of 31) |
| Baseball | 3,629 | 55.0% | 52.7% | 90% of 10 | none |

NFL is over-confident at the top (quoted 81%, landed 77%), hence 80%.
Baseball has a real but thin edge; almost nothing reaches 75%.

## Tennis on the list

Walk-forward on the tour-level archive, shipped constants, live shrink, both
players 10+ matches: 75%+ landed ATP 85.5% (262) 2025 / 85.8% (127) 2026,
WTA 84.6% (201) / 86.4% (154). The archive is main draw only, and the live
WTA record is weak on qualifying rounds, so tennis list picks are main draw
only (`build_tennis.list_eligible`). The backtest also shows the 0.8 shrink
under-quotes (75% quoted, 85% landed): worth revisiting with its own test.

## Files and automation

- `history-sports/` results per feed (committed; CI tops up the last 3 days).
- `predictions-sports/`, `sports-data.js`, `sports-record.json/.js` are
  written by CI (`sports.py --daily`, non-fatal step in deploy.yml).
- `index.html`: NFL / Baseball / Basketball / Rugby tabs (`renderSport`),
  Daily List merges football, tennis and sports picks per day, "How it went"
  has an "Other sports" board. The nav wraps three to a row on phones.
- Fixed on the way: results rows used `.trow`, which the tennis fixtures tab
  already used; renamed `.xrow`.

## Open

- NFL calibration at the top end; a calibration curve like football's.
- NBA regular season starts late October; until then the tab is empty.
- Sports window is 7 days (football 5) so Friday-Sunday rugby is always seen.

## Update, same day: accuracy on every row, calibration, tennis shrink

- Every row carries `accuracy` {from, hit, n[, season]}: the highest tested
  band at or below its confidence, from games never tuned on. Football:
  `build.ACCURACY_BANDS` (league 2026/27 if the band has 30+, else 2025/26;
  internationals 2026 holdout). Tennis: `build_tennis.ACCURACY_BANDS` (2026).
  Sports: `sports.json` `bandsCheck`.
- `sports.py` tests a two-parameter calibration per sport. Ships only if it
  passes the gates AND the quoted-minus-landed gap at 65%+ does not widen by
  more than a point. Basketball: applied. NFL, baseball, rugby: rejected.
- Tennis shrink per tour: ATP 0.9, WTA 0.95 (was 0.8), tested 2025 -> 2026.
- Shared two-sided row in `index.html` (`sportRow`, `sportDetail`,
  `tennisAsGame`): star, expandable detail, accuracy chip, Starred board.
