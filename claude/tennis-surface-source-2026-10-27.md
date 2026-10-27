# Tennis surface: source check, nothing to ship (27 October 2026)

HQ planner task of 26 Oct: give ESPN tennis results a surface. The tournament-name
map was already tested and rejected on 13 Oct (`claude/tennis-surface-test-2026-10-13.md`:
WTA +0.0024 log loss worse, p(worse) 0.88, n=2,686; ATP +0.0031, 0.95, n=1,523), so
that test was not repeated. This note checks whether a better source exists.

## What was checked (27 Oct, from the CI sandbox)

- ESPN `site.api.espn.com/.../tennis/wta/scoreboard?dates=20260601` is reachable.
  The event (Roland Garros), its grouping and each competition carry no surface
  field. The only location data is `venue` (`Paris, France`, `Court 8`). A
  "surface" would still be a hand-kept lookup by tournament name, the thing
  already rejected.
- Sackmann `tennis_wta/wta_matches_2026.csv` on raw.githubusercontent.com: 404
  (the archive has not been extended past early June, as `CLAUDE.md` says).
- tennis-data.co.uk 2026 file: 403 to the sandbox. It carries a surface column,
  but is a download by hand-picked URL behind a block, not something CI can rely on.

No free, automatable source found. No code or model change.

## Why it is also low value for now

The remaining 2026 calendar (Asian swing, indoor hard Europe, tour finals) is
all hard court, which is what every result is already rated as. A surface map
changes nothing until the clay swing in April 2027, so a half-tested map
shipped now would add maintenance and no gain. The 13 Oct test also found the
named surface made pricing worse where it differed, so the live WTA shortfall
is more likely noise and thin per-player surface ratings than the hard-court
default.

## What would settle it

A surface column that CI can fetch (tennis-data.co.uk if it unblocks, or the
Sackmann files if they resume), then the same paired walk in
`tools/tennis_surface_eval.py` on true surfaces, fitted on 2025 and confirmed
on 2026 with the Rule 3 gates. Revisit in March 2027, before the clay swing.
