# Daily List tennis 58/78 v 64: located, ATP bar to 80% (6 Nov 2026)

Trigger: HQ planner (5 Nov), tennis list picks over 28 days 58 of 78 (74%) v 64.3 expected, z -1.9.

## Where it sits (tennis-record.json, read only, nothing fitted: Rule 1)

List-flagged graded picks since 8 Oct: 59 of 79 v 65.1 expected. WTA 42 of 54 (quote 83%), ATP 17 of 25 (81%).
By own band: 75-80% 20 of 30 (67% v 77%), 80-85% 17 of 24 (71% v 82%), 85-90% 15 of 18, 90%+ 7 of 7.
By tournament: Wuhan 5 of 10 (before the 8 Oct ratings fix), Paris Masters 1 of 4, Shanghai 8 of 11. No other cut
has 30+ picks and two standard errors under quote. Most of this is the same Wuhan fortnight as the 30 Oct note
(`tennis-list-shortfall-2026-10-30.md`), so mostly noise; the live record alone cannot justify a rule.

## What history says (tools/tennis_bands.py, walk-forward, main draw, 10+ matches each; not the live record)

The list rule is that calls admitted landed 80%+. The shipped test used cumulative bands (75%+), which hide a weak
75-80% slice. Own band, 75-80% (cumulative 75%+ minus 80%+):

| Tour | 2025 | 2026 |
|---|---|---|
| ATP | 179 of 237 (75.5%) | 87 of 112 (77.7%) |
| WTA | 153 of 187 (81.8%) | 84 of 95 (88.4%) |
| ATP 80%+ | 235 of 262 (89.7%) | 116 of 131 (88.5%) |

ATP 75-80% fails the 80% rule in both windows (and the ATP ranked layer's 2026 band is 77.3%, n 128). WTA passes
in both. Live ATP 75-80% is 26 of 33 (79%) on the tennis-record bands, consistent with this.

## Change

`build_tennis.LIST_MIN`: ATP and ATP_RANKED 0.75 -> 0.80. WTA stays at 0.75. ATP 75-80% picks drop to the
reserve (still graded there). This is an admission rule, not a probability change: no confidence, calibration or
rating number moves, so the log loss gates do not apply; the evidence is the rule's own 80% test on two history windows.

## Not shown

The rule does not explain the WTA part of the live gap (42 of 54), which is within noise. Review at 300 graded
list picks as planned. If ATP at 80% thins the list too far, revert the constant.
