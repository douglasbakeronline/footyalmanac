# Croatia, Serbia, Ukraine, Hungary, Korea, UAE: second re-check (10 Nov 2026)

The planner set this task again. Nothing is missing, so nothing was added.
See `claude/af-new-leagues-coverage-2026-10-30.md` for the full coverage list.

- `af-leagues.json` carries 16 lower-division leagues for the six countries (Croatia Second NL, Hungary NB II and four NB III groups, Serbia Prva Liga and four Srpska Liga groups, Ukraine Persha and Druha, Korea K League 2 and K3, UAE Division 1). The top flights are in `sources.AF_NEW`, and the UAE Pro League is `af.301`. All are already in the build.
- API allowance per build: 0 extra (current seasons share the date pool). Only prior-season backfills cost calls, once each.
- Still off the Daily List (`NEW_BOARD_ONLY`, `LIST_MIN_AFX` 75% for `AF_EXTRA`).
- `python3 nametest.py`: all clear.
- Replay blocked again: no `API_FOOTBALL_KEY` in this sandbox and `history/` holds none of the five top flights, so the Rule 3 gates cannot be evaluated and no hit-rate claim is made.
- Next step is unchanged: backfill two prior seasons for `AF_NEW` from CI, replay through `replay.py`, check the own-band rate against 75%. Do not use `record.json` to choose the bar (Rule 1). The planner should stop reissuing this task until that CI replay exists.
