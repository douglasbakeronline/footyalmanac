# The football markets' two gate passes, read for where they come from (23 Nov 2026)

The nightly Card review of 23 Nov said in bold that two football market rules
had passed the pre-registered gate (`markets.py`, `claude/football-markets-2026-11-14.md`)
and were "ready to be offered on the Bets tab": over / under 2.5 goals and the
pick's team to score, both on the value rule (the model 5+ points above the
bookmakers' fair chance). Before anyone offers them, this is where each pass
comes from, on the committed archive (`predictions-markets/`, 14 to 23 Nov,
graded from `record-graded.json`).

## Over / under 2.5, value rule: 222 settled priced picks, +11.0% at the best price, p(loss) 0.0

| cut | picks | landed | bookmakers' fair | best price |
|---|---|---|---|---|
| under | 160 | 53% | 44% | +15.9% |
| over | 62 | 47% | 45% | -1.7% |
| 21 Nov (busiest day) | 77 | 47% | 44% | +1.3% |
| 15 and 22 Nov | 104 | 53% | 45% | about +12% |
| gap 5-10 | 160 | 54% | 46% | +10.1% |
| gap 10-15 | 49 | 41% | 41% | -4.9% |
| gap 15+ | 13 | 62% | 33% | +81% |

- The pass is the under side alone. The over picks lose.
- 82% of the picks sit on three days (15, 21, 22 Nov), so the day-resampled
  p(loss) is close to a three-weekend sample, not ten days.
- The return does not rise with the gap (10-15 points is negative).
- William Hill prices none of these picks, so none of it can be placed at
  Douglas's book.
- The same value rule over football-data.co.uk's prices (`goals-value.json`,
  `tools/goals_value.py`, run every Monday): 2025-26 -4.6% on 2,314 bets
  (under -7.3% on 1,184), 2026-27 -12.3% on 809 bets (under -14.8% on 679).
  The side carrying the live pass is the side that lost most on both seasons.
  CLAUDE.md's "Tested and rejected" already says: no goals-market bets without
  a goals calibration that passes the gates.

## Pick's team to score, value rule: 194 picks, +5.0% at the best price, p(loss) 0.088

- Home picks 156 at +5.1%, away 38 at +4.6%: not one-sided.
- 72% of the picks on the busiest three days; 15 Nov carries much of it
  (41 picks, +10.6%), 17 to 22 Nov +3.4% on 148.
- William Hill priced 41 of 194 (+6.7% at its price, too few to read).
- p(loss) 0.088 is just under the 0.10 line.

## Chance

The gate reads 20 rules (ten markets, `value` and `all`) at p(loss) 0.10, so
about two would pass by luck alone with no edge anywhere. Two passed.

## What changed

Nothing in the gate: it stays as pre-registered and its verdict is unchanged.
`markets.gate` now also returns where a verdict comes from (`days`, `top3`
the busiest three days' share, `bySel` each selection's picks, landed and
best-price return, `hill` William Hill's picks and return), and
`markets-record.json` carries `tests` (the rules read). The nightly review's
markets section prints, under any pass, one line a passing rule with those
numbers, the football-data seasons for over / under 2.5, and the chance line
(`card_review_post.market_pass_lines`).

## Read

Not a reason to offer either market yet. Over / under 2.5 should not be
offered while the football-data seasons say its value unders lose and Hill
does not price it. The pick's team to score is the more even of the two; it
needs more weekends (and Hill prices) before it means anything. Douglas's
call either way; the gate re-reads both every build.
