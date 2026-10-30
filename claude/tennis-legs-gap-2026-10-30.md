# Tennis legs in groups: 22 of 40 against 28 quoted (30 Oct 2026)

HQ planner flagged tennis legs in the Odds tab / Card groups since 19 Oct at
21 of 39 (z -2.2). Task: find the kind of tennis leg that falls short and
replay a rule that leaves it out. Result: **nothing new to ship**. The kind
that fell short is the one `CARD_SPORT_MIN` (tennis needs model and tested
rate both 75%+, `CARD_RULE` 2, 29 Oct 2026) already excludes, and the
history to replay a price-based rule does not exist.

## Where the gap sits (live record, used only to locate it, nothing fitted)

Unique tennis legs in `groupings-archive/` from 19 Oct, settled with
`groupings.settle`: 41 legs, 40 settled, 22 landed (55%) against 28.4
expected (mean quoted chance 71%).

| Cut | Landed / n (quoted) |
|---|---|
| Model under 75% | 15 / 31 (48%, ~68%) |
| Model 75%+ | 7 / 9 (78%, ~80%): on quote |
| Tested rate (`hit`) 60-65% | 4 / 10 |
| Tested rate 80-85% | 6 / 11 |
| Price 1.50+ | 8 / 13 (63% quoted) |
| Price 1.05-1.35 | 8 / 13 |
| Priced by a bookmaker | 20 / 35 (69% quoted) |
| Estimated (model price, no book) | 2 / 5 |
| Model 5+ under the fair chance | 11 / 15 (on quote) |
| Model level with or above the fair chance | 5 / 11 |
| By day | 19 Oct 2/5, 26 Oct 8/10, 27 Oct 8/11, 28 Oct 3/9, 29 Oct 1/5 |

Every cut has 40 or fewer legs, so each has a standard error of 7 to 15
points. The one split that is large (model under 75% v 75%+) is the rule
already live. The weak days (28, 29 Oct) are the ones before the rule applied
to unlocked groups; they are not evidence for a further rule. No competition
tier, qualifying-round or final split is usable: every leg is "other".

## Why no replay

A tennis leg's selection rests on bookmaker price and fair chance. History
holds no tennis prices (the archived Card/group legs begin in October; the
football-data.co.uk history is football only). The model-only part (rate at
75%+) can be checked on the tennis archive, and has been:
`tennis-record.json` 75%+ landed 139 of 163 (85%) per CLAUDE.md, which is why
the 75% floor stays. Any further cut (price, gap, tour) would be chosen from
this 40-leg sample, i.e. fitted on the live record, which Rule 1 forbids.

## Do next

Let rule 2 accumulate. Re-read tennis Card legs at the mid-December review
(~300 locked legs). Rule for acting: tennis legs under quote by two standard
errors on 50+ legs at the 75% floor, then take tennis off the Card
(`CARD_SPORTS_OFF`), as was done for NFL and college football.
