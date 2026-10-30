# Croatia, Serbia, Ukraine, Hungary, Korea, UAE: coverage re-check (30 Oct 2026)

Task (HQ planner, 29 Oct): add the leagues API-Football carries for these six countries.

## Finding: already covered, nothing to add

- Top flights Croatia (210), Hungary (271), Serbia (286), Ukraine (333), South Korea (292) are in `sources.AF_NEW` since 20 Oct 2026, board only (`build.NEW_BOARD_ONLY`), out of the calibration fit (`tune.codes`).
- UAE Pro League arrives as `af.301` (`AF_EXTRA`); UAE Division 1 is `af.303`.
- Lower divisions in `af-leagues.json`: Croatia Second NL (946); Hungary NB II (272) and four NB III groups; Serbia Prva Liga (287) and four Srpska Liga groups; Ukraine Persha (334) and Druha (336); Korea K League 2 (293), K3 (295).
- The 30 Oct 2026 predictions archive holds fixtures for all six: ukr.1 11, srb.1 7, hun.1 6, kr.1 6, hrv.1 5, af.301 3.
- Name matching: `tests/test_af_new_leagues.py` and `nametest.py` pass.

## API allowance

Current seasons ride the shared date pool: 0 extra calls per build. Finished seasons are one-off (5 leagues x 2 seasons = 10 calls), then on disk. Adding the lower divisions would not change the per-build cost either (same pool); it is the one-off prior-season calls that grow.

## Replay: not possible here

No `API_FOOTBALL_KEY` in this sandbox and `history/` holds none of the five top flights, so no walk-forward, no hit-rate claim, and no List place. Rule 3 gates cannot be evaluated. They stay off the List and the reserve.

## Next step

Run the replay from CI, where the key lives: backfill the two prior seasons for `AF_NEW`, replay through `replay.py` and check the own-band rate against `LIST_MIN_AFX` (75%). Do not use `record.json` to choose the bar (Rule 1). The Pro plan runs to 30 Oct 2026, so renewal decides whether this route stays open.
