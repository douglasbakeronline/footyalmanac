# Tennis surface: second source check, nothing to ship (9 November 2026)

HQ planner task of 8 Nov, the same idea as 13 and 27 Oct. Not retested: the
tournament-name map was rejected on both tours (`claude/tennis-surface-test-2026-10-13.md`:
WTA +0.0024 log loss worse, p(worse) 0.88, n=2,686; ATP +0.0031, 0.95, n=1,523) and the
source check found nothing (`claude/tennis-surface-source-2026-10-27.md`).

## Probed again, 9 Nov, CI sandbox

- Sackmann `wta_matches_2026.csv` and `atp_matches_2026.csv`: both 404.
- tennis-data.co.uk 2026 and 2026w files: 403.
- ESPN WTA scoreboard (8 Nov): 200; event keys are id, name, venue ("Hong Kong, Hong Kong, China"),
  groupings, calendar and so on; no surface, clay, grass or hard-court text anywhere in the JSON.

Still no free, automatable surface source. A hand-kept map is the thing already rejected.

## Why nothing changes the live gap now

Every tournament left in 2026 is hard court, already the default, so a map changes no price
until the clay swing in April 2027. The WTA shortfall on the live record is not explained by
surface: on the 13 Oct replay a named surface was worse on WTA clay and grass events.

## What would settle it

Unchanged: a surface column CI can fetch (tennis-data.co.uk unblocking, or Sackmann resuming),
then `tools/tennis_surface_eval.py` on true surfaces, fitted on 2025, confirmed on 2026 with the
Rule 3 gates. Revisit March 2027. Planner should stop issuing this task until a source appears.
