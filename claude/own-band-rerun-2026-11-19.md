# Own-band List admission: third ask, already shipped (19 Nov 2026)

Nina, from the HQ planner (18 Nov). The task is the one shipped on 20 Oct 2026 (`sports.own_bands_clear`, `list_threshold`, `claude/own-band-admission-2026-10-20.md`) and re-run on 11 Nov (`claude/own-band-rerun-2026-11-11.md`). Nothing new to test, so no replay was rerun and nothing was fitted (Rule 1).

Checked today: `sports.stored_threshold` on the committed `sports.json` gives the live bars the own-band rule sets: NFL 80%, NBA 80%, rugby 80%, college football 80% (off the list by `LIST_OFF`), college basketball 85%, WNBA 85%; MLB, NHL, NRL none. The `listMin` saved in `sports.json` (rugby 70%, cfb 70%, NBA 75%, WNBA 80%) is the older cumulative-only value and is not what the board reads. The planner's cfb / rugby / ncaab wording describes the state before 20 Oct.

Held-out results are in the two earlier notes (rugby 78.9% -> 84.1%, college basketball 78.9% -> 87.4%, NFL 71.8% -> 77.4%). Tennis has its own rule (`claude/tennis-list-own-band-2026-11-06.md`). Football's 60-80% calls land at or above quote (`claude/midband-calibration-2026-10-21.md`), so an own-band cut has nothing to remove there.

Action for HQ: retire this planner task. The gap it points at is closed.
