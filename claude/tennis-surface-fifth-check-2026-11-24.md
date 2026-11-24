# Tennis surface, fifth issue: nothing new to test, nothing to ship (24 November 2026)

HQ planner task of 23 Nov (same wording as 15 Nov). Read first: `tennis-surface-test-2026-10-13.md`
(the tournament-name map, rejected on both tours: WTA +0.0024 log loss worse, p(worse) 0.88, n=2,686;
ATP +0.0031, 0.95, n=1,523), `-source-2026-10-27`, `-recheck-2026-11-09`, `-third-check-2026-11-15`,
`-fourth-check-2026-11-17`.

Probed again 24 Nov from the CI sandbox: Sackmann `wta_matches_2026.csv` and `atp_matches_2026.csv`
404; tennis-data.co.uk `2026/2026.xlsx` and `2026w/2026.xlsx` 403. ESPN carries no surface field
(27 Oct, 9 Nov). So there is still no free automatable surface column, and a hand-kept map is the idea
already rejected. Every event since 18 Oct is hard court, the default, so a map changes no rating in the
window the live shortfall sits in; the live record is not a fit target (Rule 1).

No code or model change; gates n/a. Revisit March 2027 if a CI-fetchable surface column appears.
Planner: stop issuing this task (five times now); try WTA by round and rating-gap band on history.
