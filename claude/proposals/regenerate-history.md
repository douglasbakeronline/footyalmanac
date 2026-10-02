# Proposal: regenerate the three contaminated history files

Status: proposed, not implemented. Follows `claude/evaluation-audit.md`.

## Problem

`history/mx.1-2025-26.json`, `history/ru.1-2025-26.json` and
`history/dnk.1-2025-26.json` were walked on 27 Sep 2026 with a window
running to 31 July 2026. Each holds the opening weeks of 2026-27 (21, 9 and 6
matches, all also in `current/`); Denmark's also starts with the 2024-25
European play-off (1 June 2025, Randers v Silkeborg).

The audit branch protects against this at run time (the live build drops
matches present in both seasons; the replay refuses the overlap), but the
files themselves are still wrong, and any future reader of them inherits it.

## Proposed change

1. With `backfill.SEASON_BOUNDS` (1 July to 30 June for these three) and
   `clip_to_next_season` in place, re-walk only these seasons:
   `rm history/{mx.1,ru.1,dnk.1}-2025-26.json` then
   `python3 backfill.py --season 2025-26 --only mx.1,ru.1,dnk.1`.
2. Before committing, check each new file:
   - every date inside 2025-07-01..2026-06-30;
   - no (date, home, away) shared with `current/<code>-2026-27.json`;
   - match count against the old file minus the contaminated rows
     (expected 358-21 = 337, 249-9 = 240, 200-6-1 = 193, give or take
     rearranged fixtures ESPN reports differently);
   - `python3 replay.py --audit` no longer lists them for overlap or window.
3. Commit the three files by hand with the counts in the message, as
   `history/` always is.

## Effect

Live: none beyond what the run-time de-duplication already does, except
Denmark loses one 2024-25 play-off match from its prior. Evaluation: mx.1
returns to the fit season once its 2025-26 file is clean; ru.1 and dnk.1
become usable in an expanded check season (see `cache-expansion.md`).

## Risk

Low. Three files, regenerated from the same source with tighter dates; the
old versions remain in git history. Rollback: `git revert`.
