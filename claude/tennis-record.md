# Tennis on "How it went" — 27 September 2026

## The gap

Tennis was priced every morning and never checked. `build_tennis.py`
overwrote `tennis-data.js` daily, nothing was archived, and the results tab
said "not tracked yet". Douglas wanted each pick checked against the winner.

## What was built

- **build_tennis.py** archives every priced match to
  `predictions-tennis/<build date>.json` via `archive()`, merged into the
  day's file rather than written over it (a later same-day build no longer
  prices a match that has started, and overwriting would lose the earlier
  pre-match price). Each entry carries `published` (UTC), the ESPN match
  `id` and the raw ESPN names (`espn`). `generated` is now UTC with a `Z`.
- **In-play pricing fixed.** The build skipped only finished matches, so a
  match already under way at 05:15 UTC (Asian events) was priced and
  published mid-match. It now prices `state == "pre"` only. The seed found
  89 such prices in the published history.
- **score_tennis.py** grades. Rules:
  - a price counts only if `published` < scheduled start (`date` + `time`,
    or the start of the day when there is no time);
  - latest qualifying price wins per prediction key;
  - result matched by ESPN id, else by (tour, both rating-pool names via
    `match_player`) within ±2 days, only if exactly one match fits;
  - walkover (`w/o` in the note) or `STATUS_CANCELED` is void; retirement
    (`ret` in the note) is graded and flagged;
  - several predictions resolving to one result (a rescheduled match) are
    graded once, latest published price;
  - graded matches persist in `tennis-record.json` and are never refetched;
    ungraded ones are chased for 21 days.
  Writes `tennis-record.json` (full, with `graded`) and `tennis-record.js`
  (`window.__TENNIS_RECORD__`, without `graded`) for the page.
- **index.html** tennis branch of `renderResults`: scoreline (overall, ATP,
  WTA, log loss vs 0.693 coin flip), day picker, one row per match
  (picked + confidence beside winner + score, tick or cross), tier table,
  and the rules in prose. Loads `tennis-record.js` beside `tennis-data.js`.
- **deploy.yml** runs `score_tennis.py` after the tennis build (non-fatal),
  commits `predictions-tennis/` and `tennis-record.*`, publishes
  `tennis-record.js`.

## The seed

The archive was rebuilt from git: every committed `tennis-data.js` since
22 Sep (18 versions), commit time as publish time, only matches whose start
was after it. 626 prices kept, 89 dropped as published after the start.

## First reading (105 graded, 1 void)

| | n | picked winner | quoted |
|---|---|---|---|
| All | 105 | 53.3% | 58.9% |
| ATP | 43 | 62.8% | 60.1% |
| WTA | 62 | 46.8% | 58.2% |

WTA is under a coin flip on a small sample. Not fitted on (rule 1 applies
to tennis too). If it persists past a few hundred matches, `tune_tennis.py`
is where to look, with its own walk-forward, not this record.

## Open

- Tennis tiers are football's thresholds, uncalibrated for tennis.
- `CONFIDENCE_SHRINK = 0.8` is still a judgement call; this record is now
  the thing that can show whether it helps, over time.
- Surface is hard-coded to Hard (ESPN carries none). Fine until clay season.
- The catch-up Elo pass still applies walkovers as wins.
