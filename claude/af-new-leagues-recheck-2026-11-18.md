# Croatia, Serbia, Ukraine, Hungary, Korea, UAE: third re-check (18 Nov 2026)

Nothing missing, nothing added. See `claude/af-new-leagues-coverage-2026-10-30.md` and `claude/af-new-leagues-recheck-2026-11-10.md`.

- Top flights in `sources.AF_NEW` (HNL 210, NB I 271, SuperLiga 286, Ukrainian PL 333, K League 1 292); UAE Pro League is `af.301`, UAE Division 1 `af.303`.
- The 17 Nov 2026 archive (`predictions/2026-11-17.json`) holds fixtures for all of them: hrv.1 5, hun.1 6, srb.1 7, ukr.1 8, kr.1 6, af.301 7, af.303 7.
- Extra API allowance per build: 0 (shared date pool).
- Still off the Daily List (`NEW_BOARD_ONLY`, `LIST_MIN_AFX` 75%).
- `nametest.py` clear. Replay still blocked: no API key here and `history/` has none of the five top flights, so the Rule 3 gates cannot be run and no hit-rate claim is made.
- The only open step is a CI backfill of two prior seasons for `AF_NEW` and a `replay.py` run. The planner should stop reissuing this task until that exists.
