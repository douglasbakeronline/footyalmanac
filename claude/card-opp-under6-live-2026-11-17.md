# Card legs with the opposition under 6: the live run against the seasons (17 Nov 2026)

Task (HQ planner): 18 of 21 live Card legs with the opposition priced under 6
landed (86%) v 73% quoted, z +1.3. Does the live run agree with the replay?
Live record used only to locate the gap (Rule 1).

## Read (`card-legs-history.json` legs, model 60%+, price 1.15-1.90, bootstrap 2,000)

| season | band | legs | landed | model | gap | p(gap <= 0) | ROI at avg price |
|---|---|---|---|---|---|---|---|
| fit 2025-26 | opp < 6 | 76 | 64.5% | 64.4% | +0.1 | 0.48 | -4.3% |
| fit 2025-26 | opp 6+ | 454 | 78.4% | 70.1% | +8.3 | 0.00 | +2.2% |
| fit 2025-26 | opp 9+ | 205 | 84.4% | 73.2% | +11.2 | 0.00 | +3.4% |
| check 2026-27 | opp < 6 | 17 | 88.2% | 64.6% | +23.6 | 0.00 | +29.8% |
| check 2026-27 | opp 6+ | 103 | 79.6% | 68.5% | +11.1 | 0.00 | +0.5% |
| check 2026-27 | opp 9+ | 60 | 81.7% | 70.0% | +11.7 | 0.01 | -1.2% |

(Football only; the replay's leg set holds almost no legs under 5.0, so the
under-6 band is 5.0-6.0.)

## Verdict

The live run agrees with the current season (88% on 17) and not with last
season (64.5% on 76, exactly the model's number, -4.3% at price). Pooled,
under-6 legs: 93 legs, 69.9% landed v 64.5% modelled, ROI +2.7%, but the two
seasons point opposite ways and 17 and 21 legs are far under any gate. No
rule change: the Card no longer reads the opposition at all (rule 13, 17 Nov
2026), so the only possible action would be adding an opposition ceiling or
floor back, and neither season-set supports a floor going down: the 6+ and 9+
bands land above the model on both seasons, 9+ most on the fit season.
Nothing is fitted on the live legs.

`opp7` and `opp12` (the opposition floor at 7 and at 12) are not rerun here:
`opp7` is registered on the rule 6 family (`tools/card_replay.py`) and ran 4
groups, 0 won on the fit season and 1 of 1 on check in
`card-legs-history.json` (`cardOpp7`), far too few to compare; no `opp12`
variant exists and would build fewer still. `m7opp5` / `m7noopp` remain the
registered pair for the 30 Nov review (`claude/card-rule13-split-2026-11-17.md`).

Revisit if under-6 football legs on the pool reach 100.
