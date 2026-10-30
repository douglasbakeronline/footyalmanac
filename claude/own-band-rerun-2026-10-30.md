# Own-band List admission: already shipped, re-run (30 Oct 2026)

Nina, from the HQ planner (29 Oct). The task asked for an own-band admission rule
across every sport. It was built, replayed and shipped on 20 Oct 2026
(`claude/own-band-admission-2026-10-20.md`, `sports.own_bands_clear`,
`sports.list_threshold`, `tools/own_band_replay.py`). Nothing new to ship.

Re-run today of `tools/own_band_replay.py` (history only, no live record read):

| Sport | held-out old bar -> new | old picks, hit | new picks, hit | dropped, hit | p(worse) |
|---|---|---|---|---|---|
| Rugby | 65% -> 75% | 426, 78.9% | 232, 84.1% | 194, 72.7% | 0.002 |
| College basketball | 65% -> 80% | 3,792, 78.9% | 1,884, 87.4% | 1,908, 70.5% | 0.000 |
| NFL | 70% -> 75% | 110, 71.8% | 62, 77.4% | 48, 64.6% | 0.07 |
| NBA, WNBA, college football | no change on the fit season alone | | | | |
| MLB, NHL, NRL | no place either way | | | | |

Live bars from `sports.stored_threshold` on the saved bands: NFL 80%, NBA 80%,
rugby 80%, college football 80%, college basketball 85%, WNBA 85%. All six
already carry the rule, so the planner's gap (cumulative 80% hiding low-70s
bands) is closed in code; the live record only shows the earlier period.

Not tried, and why: tennis (own-band chip live since 26 Oct; 75-80% lands 82%
v 77% quoted, so a stricter bar would not help) and football (own admission via
tested bars). A different idea would need new evidence; none was found here.
