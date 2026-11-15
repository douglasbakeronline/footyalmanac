# Own-band List admission: re-run, already shipped (11 Nov 2026)

Nina, from the HQ planner. The task asked for a rule admitting a pick only if its own 5-point band landed the bar, replayed for every sport. That rule shipped on 20 Oct 2026 (`sports.own_bands_clear`, `list_threshold`, `claude/own-band-admission-2026-10-20.md`). The planner's wording (cfb, rugby, ncaab) describes the state before that release.

Re-ran `tools/own_band_replay.py` on history only (Rule 1: record not read). Results match 20 Oct. `sports.stored_threshold` on today's `sports.json` gives the live bars: NFL 80%, NBA 80%, rugby 80%, college basketball 85%, WNBA 85%, college football 80% (off the list by `LIST_OFF`); MLB, NHL, NRL none.

Held out (bar from Jul 2024-Jun 2025, applied since Jul 2025):

| Sport | old picks, hit | new picks, hit | dropped, hit | p(new worse) |
|---|---|---|---|---|
| Rugby | 426, 78.9% | 232, 84.1% | 194, 72.7% | 0.002 |
| College basketball | 3,792, 78.9% | 1,884, 87.4% | 1,908, 70.5% | 0.000 |
| NFL | 110, 71.8% | 62, 77.4% | 48, 64.6% | 0.07 |
| NBA, WNBA, CFB | unchanged on the fit season alone | | | |

Both windows, bar as set today: rugby check 337 at 81.6% -> 141 at 90.1%; ncaab 3,172 at 82.1% -> 1,258 at 91.6%; NBA 298 at 82.2% -> 165 at 86.7%; WNBA 101 at 81.2% -> 47 at 87.2%.

Nothing left to ship for this idea. Not worth repeating; a different idea would be needed (e.g. tennis already has its own-band rule, `claude/tennis-list-own-band-2026-11-06.md`).
