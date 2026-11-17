# Tennis surface, fourth issue: nothing new to test, nothing to ship (17 November 2026)

HQ planner task of 15 Nov (WTA live calls under quote, ESPN results carry no surface). Same idea as
13 Oct, 27 Oct, 9 Nov and 15 Nov. Checked first, as the task asks:

- The tournament-to-surface map was tested and rejected on both tours
  (`claude/tennis-surface-test-2026-10-13.md`: WTA +0.0024 log loss worse, p(worse) 0.88, n=2,686;
  ATP +0.0031, 0.95, n=1,523; only ATP clay improved, p(worse) 0.13 on 187 games, under the 250 gate).
- Probed again 17 Nov from the CI sandbox: Sackmann `wta_matches_2026.csv` and `atp_matches_2026.csv`
  404; tennis-data.co.uk 2026 file 403. ESPN carries no surface field (notes of 27 Oct and 9 Nov).
  No free automatable surface column exists, so there is no true-surface test to run.
- Every event since June 2026 outside the clay and grass swings, and every one from 18 Oct on, is hard
  court, which is what each result is already rated as. A map changes no rating in the window the
  WTA shortfall sits in. Using the live record to pick a fix would also break Rule 1.

No code or model change; gates n/a. Revisit March 2027 if a surface column CI can fetch appears.
Planner: stop issuing this task; try WTA by round and rating-gap band on history instead.
