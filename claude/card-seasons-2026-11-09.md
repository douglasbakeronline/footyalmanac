# The Card's leg rule over five seasons (9 Nov 2026)

Issue #153. Douglas, 9 Nov 2026: the goal is consistent returns on the group
accumulators, and the whole evidence base was one season (2025-26) plus ten
weeks. `tools/card_legs_history.py --seasons 2022-23,2023-24,2024-25` (shipped
in #161) replayed each past season with the season before as its prior, on
football-data.co.uk prices, in CI (run 42543472973 on the report-only PR
#162; the sandbox cannot fetch). The full output is
`claude/card-seasons-2026-11-09-output.txt`. Nothing here is fitted: the
numbers are the model's walk-forward quotes against the market's, graded.

Coverage: 4,200 to 4,900 priced matches joined per season, 780 to 1,000
candidate legs (bookmakers' 60%+ at 1.15 to 1.90, core football-data
leagues). The replay walks every league forward from its prior season, so a
2022-23 number is what the site would have quoted that morning.

## The legs: under the market by 5+ (the Card's football cut)

| season | legs | landed | quoted | singles, avg price | at best | CLV |
|---|---|---|---|---|---|---|
| 2022-23 | 320 | 70.9% | 68.4% | -1.0% | +1.7% | -1.5% |
| 2023-24 | 483 | 73.3% | 69.1% | +0.6% | +3.3% | -1.1% |
| 2024-25 | 445 | 73.3% | 68.5% | +0.8% | +3.3% | -1.8% |
| 2025-26 | 417 | 72.7% | 68.0% | -0.2% | +2.4% | -3.4% |
| 2026-27 to 9 Nov | 110 | 70.0% | 69.3% | -7.0% | -4.5% | -3.3% |

The cut lands 2 to 5 points above its quote in every full season, which at
these prices is about break-even at the average price and +2 to +3% at the
best price. It never beats the closing line. The same as the 29 Oct read,
now on four seasons rather than one.

## By how far the model sits under the market (the 5-10 cap, CARD_RULE 5)

Singles return at the average price, under-market legs:

| band | 2022-23 | 2023-24 | 2024-25 | 2025-26 | 2026-27 |
|---|---|---|---|---|---|
| 5-8 under | -1.2% (124) | +6.1% (105) | -0.5% (150) | +9.6% (118) | under 10 legs |
| 8-10 under | +1.7% (56) | -15.4% (88) | -3.2% (81) | +1.5% (87) | +7.9% (11) |
| 10+ under | -2.0% (140) | +3.4% (290) | +3.1% (214) | -6.5% (212) | -9.8% (90) |

The 31 Oct cap (`CARD_UNDER_MAX` 10, "10+ under lost on every sample") rested
on 2025-26 and the live archive. Over the past seasons the 10+ band was the
best of the three in 2023-24 and 2024-25 and the worst in 2025-26 and this
season; 5-8 was positive in two seasons of four and 8-10 in two of five. No
gap band is positive on every season. The gap is not where the edge is.

Note the check season: 100 of its 110 under-market legs sit 10+ under, and
fewer than 10 sit 5-8 under. This season's model runs much further under the
market than in any past season, which is a calibration question
(`claude/calibration-rerun-2026-11-06.md`), not a Card one, and it is why the
live Card's football cut admits so little.

## By the opposition's price (CARD_RULE 6)

Under-market legs, singles return at the average price (best in brackets):

| opposition | 2022-23 | 2023-24 | 2024-25 | 2025-26 | 2026-27 |
|---|---|---|---|---|---|
| 4-6 | -5.6% (49) | -0.9% (85) | -8.7% (90) | -3.9% (77) | -25.9% (22) |
| 6-9 | +1.5% (178) | -0.9% (251) | +0.9% (229) | -2.5% (234) | -7.0% (49) |
| 9+ | -3.5% (93) | +4.0% (147) | +7.3% (126) | +7.5% (106) | +3.7% (39) |

Landed against quoted for the 9+ legs: 76.3 v 75.8, 83.7 v 76.7, 86.5 v
76.4, 86.8 v 75.4, 84.6 v 76.5. All 60%+ legs (not only under-market) at
9+: 81.7 v 76.3, 81.8 v 76.9, 80.9 v 76.4, 84.0 v 75.9, 80.8 v 76.8, return
+1.9, +1.5, +0.3, +3.3, -1.7% (at best +4.4, +3.8, +2.5, +5.8, +1.1%).

So the opposition's price is the one condition that holds up: 9+ legs land
about 5 points above quote in every one of five seasons (one of them, 2022-23,
only on quote), and the 4-6 legs land under quote and lose in every season.
Over the five seasons the under-market 9+ cut is 511 legs, 83.8% landed v
76.2% quoted, about +4% at the average price and +7% at the best. Four of
five seasons positive; 2022-23 is the one that was not, so "every season" is
not quite true and the review should say so.

## The whole Card on football-data legs

Live rule (6, opposition 9+, 3 to 5 legs): one group in 2022-23, none in
2023-24, 2024-25, 2025-26 or this season. On the football-data leagues
alone the live Card does not exist: 9+ legs are short and about one a day,
so three from different fixtures on one day almost never happen. The live
Card's groups are tennis and NBA legs with one football leg at most
(`groupings-record.json`, 6 to 8 Nov), and there has been no Card 3x since
6 Nov (#155).

Rule 5 (no opposition condition, the Card as it ran 31 Oct to 6 Nov):

| season | days | groups | won | expected | return | best | losing months | Card 2x | Card 3x |
|---|---|---|---|---|---|---|---|---|---|
| 2022-23 | 23 | 25 | 10 | 8.2 | +3.8% | +12.3% | 3 of 8 | 8/18, +6.2% | 2/7, -8.4% |
| 2023-24 | 19 | 19 | 8 | 6.5 | +15.8% | +24.4% | 3 of 9 | 8/15, +31.2% | 0/4, -100% |
| 2024-25 | 23 | 24 | 9 | 8.4 | -1.6% | +5.3% | 5 of 10 | 9/18, +14.8% | 0/6, -100% |
| 2025-26 | 23 | 25 | 10 | 8.0 | +2.0% | +10.5% | 5 of 9 | 8/18, +4.4% | 2/7, -10.4% |

Four seasons together: 93 groups, 37 won against 31.0 expected, 162 units
staked, +4.4% at the average price and +12.5% at the best. The Card 2x
is where it comes from: 33 of 69 won (48%) against 36% expected, positive in
all four seasons. The Card 3x lost in all four: 4 of 24 won against about
6.3 expected. Only 19 to 25 groups a season qualify on these leagues, so a
season's return swings between -2% and +16% on a handful of groups, and
three to five months in each season lose. "Consistent" is not what the
football-only Card delivers on its own; the daily Card needs the other
sports' legs for volume, and those are not in this replay.

The 29 Oct replay of the uncapped rule (rule 4) on 2025-26 made 77 groups
and +16.5%; capping the gap at 10 under (rule 5) cut that to 25 groups and
+2%. Given the gap table above, the cap removed volume without a consistent
reason.

Simplest card, one treble a day from the under-market legs: 12/38 (-23%),
31/65 (+8%), 33/66 (+19%), 26/55 (+10%), 4/11 (-24%). Three of five positive.

## What this means (nothing changes today)

- `CARD_OPP_MIN` 9+ is the best-supported condition in the Card: it holds
  in four of five seasons and the 4-6 legs lose in all five. Keep it.
- `CARD_UNDER_MAX` 10 (rule 5) is not supported over 2022-25: the 10+ band
  was the best gap band in two seasons. The pre-registered `uncapped`
  variant in `tools/card_replay.py` is the right comparison at the 30 Nov
  review; on the pool it has not yet had the data (#154).
- The Card 3x loses on every football-data season under rule 5 and has not
  been built since 6 Nov. Whether to keep offering a 3x is Douglas's call;
  the evidence says the 2x carries the return.
- The check season's model sits far under the market (100 of 110 legs 10+
  under). Read with `claude/calibration-rerun-2026-11-06.md`.
- Rule for a change stands (CLAUDE.md): a pre-registered variant beats live
  on both football-data seasons and the archive, p(worse) at most 0.30 on
  100+ legs. The `uncapped` variant now has the football-data side of that
  case; the archive side is the pool from mid-November.

## How to rerun

`card-legs-history.yml` (restored in PR #158, for Douglas) with the
`seasons` input `2022-23,2023-24,2024-25`; about ten minutes in CI. Until it
lands, a pull request that touches the tool runs the workflow from its own
branch, which is how #162 produced this.
