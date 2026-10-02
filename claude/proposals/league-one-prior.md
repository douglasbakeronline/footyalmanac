# Proposal: replace the corrupt League One 2025-26 prior

Status: proposed, not implemented. Follows `claude/evaluation-audit.md`.

## Problem

openfootball's `2025-26/en.3.json` (as fetched 2 Oct 2026) holds 356
matches: 271 from August to December 2025, then stops, plus 85 dated
January-February 2025, which belong to 2024-25 (42 of them repeat 2024-25
fixtures exactly by home and away). A full League One season is 552
matches.

The live build uses this file as League One's prior for 2026-27, via
`pick_prior`, which marks it partial (well under 80% complete) and blends
it with 2024-25. The 85 stray rows therefore feed the prior as if they
were recent 2025-26 evidence. The replay now refuses the file (85 rows
outside the 2025-26 window).

## Options

| Option | Source | For | Against |
|---|---|---|---|
| A. Backfill from ESPN | `backfill.py --season 2025-26 --only en.3` (slug `eng.3` answers) | same path as 14 other leagues; full season; validated by the new checks | ESPN spells clubs differently from openfootball; en.3's current season comes from ESPN too, so this is actually more consistent |
| B. API-Football | `sources.AF` (paid key) | complete, already integrated for wider leagues | adds a paid dependency to a core English league; another spelling |
| C. Trim openfootball | drop rows outside the window | smallest change | leaves a season that stops in December: still partial |

Recommendation: **A**, then check:

- 552 matches (or within a handful), dates inside 2025-06-01..2026-07-31;
- `python3 nametest.py` passes (ESPN League One names against the pool);
- `python3 replay.py --audit` lists en.3 as usable for the check season
  once the cache-expansion proposal lands;
- a fast build shows League One rated, nothing newly unrated.

`history/en.3-2025-26.json` then takes precedence over openfootball
automatically (`sources.fetch_season` reads `history/` first).

## Effect

Live: League One's prior becomes the real 2025-26 season instead of a
partial one with stale rows, so its ratings change (that is the point).
Worth a paired check of League One fixtures before and after on the
2026-27 results so far, reported, not tuned on.

## Risk

Moderate: it changes live League One numbers. Rollback: delete the
history file and revert.
