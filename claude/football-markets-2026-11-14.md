# Football markets beyond the match winner, 14 November 2026

Douglas, 14 Nov 2026: "For football fixtures I want to start looking at winner
and btts, as well as just btts, goals over 2.5, and any other things you
suggest. Let's go hard on setting this up to track on football. Then we can
find something similar for all other sports." And: "a lot of time I'm spending
reviewing things. I need this to be more automated."

## What was built

`markets.py`, run by deploy.yml after the ledger step on every build:

- **Ten markets a fixture**, each read from the match model's own scoreline
  grid (Dixon-Coles, from the fixture's expected goals) with the grid's home /
  draw / away totals rescaled to the published chances: both teams to score,
  over / under 1.5, 2.5 and 3.5, the pick to win and both score, to win and
  over 2.5, to win to nil, double chance, draw no bet, the pick's team to
  score. The pick is the likelier of home and away; a two-sided market's
  selection is its likelier side. BTTS and over 2.5 are the numbers already
  published on the row. `RULE` 1.
- **Prices** from API-Football, one unfiltered `/odds?date=` sweep a date
  (today and tomorrow), cached five hours in `.afcache`. Checked on the live
  feed first (`tools/markets_probe.py` on the `odds-probe-run` branch, report
  on `odds-probe-report`): an unfiltered sweep is the same number of pages as
  the match-winner sweep (57 on Sat 14 Nov, 40 on Sun 15 Nov), so about 400
  calls a day; it stands down under 2,000 calls left. Bet ids and labels are
  in `markets.LABELS`. Per selection: average over every book, best UK book,
  William Hill, books, and the bookmakers' fair chance where the whole market
  is priced. William Hill prices BTTS, double chance, draw no bet, win and
  both score, win to nil and the team to score; not the goals lines or win and
  over 2.5 in this feed (Bet365 does).
- **Archive**: `predictions-markets/<build date>.json.gz`, a fixture's row
  replaced until kick-off and never after.
- **Record**: `markets-record.json` (also on the site): by market, landed v
  the model and v the bookmakers, return at the average, best and Hill price,
  bands by chance and by model-minus-bookmakers gap, and the gate. Fixtures
  from before the archive are replayed from the copy of `predictions/` that
  score.py graded: calibration only, no prices, kept apart.
- **The gate**, pre-registered: 150+ settled priced picks, landed above the
  bookmakers' fair chance, return at the best UK price positive, day-resampled
  p(loss) 0.10 or less. Two rules a market: `value` (model 5+ points above the
  bookmakers) and `all`. Read on live priced picks only.
- **Where it shows**: a table in the nightly Card review issue
  (`card_review_post.markets_section`), a pass in bold. No page change.

## First read: calibration on 11,112 replayed fixtures (21 Aug to 14 Nov)

| Market | Landed | Model | z |
|---|---|---|---|
| Both teams to score | 55.7% | 54.0% | +3.7 |
| Over / under 1.5 | 76.6% | 74.2% | +5.9 |
| Over / under 2.5 | 57.8% | 54.3% | +7.4 |
| Over / under 3.5 | 67.0% | 71.8% | -11.6 |
| Win and both score | 24.1% | 21.5% | +6.6 |
| Win and over 2.5 | 33.1% | 29.7% | +8.2 |
| Win to nil | 26.9% | 27.0% | -0.3 |
| Double chance | 75.6% | 75.1% | +1.3 |
| Draw no bet | 67.6% | 66.1% | +3.0 |
| Pick's team to score | 81.2% | 78.4% | +7.2 |

- The model's goals run low: over 1.5 and over 2.5 land more often than
  quoted and under 3.5 less (it is usually the under that is the selection).
  Every market leaning on goals inherits it. Same finding as
  `tools/goals_value.py` (29 Oct). A goals calibration would have to be fitted
  on the replay, never this record (Rule 1); not done here.
- The result-led markets are on quote: double chance, draw no bet, win to nil.
- Win and both score is on quote from 25% up (25-30%: 27.4% v 27.3%; 30-40%:
  32.6% v 33.6%; 40-50%: 41.2% v 43.2%), and lands above quote below that.
  About half of winning picks have both sides score; 39% for 80%+ favourites.
- High-chance selections are plentiful and land as quoted: at 85%+ over the
  whole record, the team to score 89.3% v 89.2% (2,470), double chance 88.5% v
  89.3% (1,222), draw no bet 88.7% v 89.8% (594), over 1.5 86.3% v 88.4%
  (1,513). In November that is about 47, 25, 15 and 26 fixtures a day. Whether
  their prices pay is what the tracking is for.

None of this says any market makes money: there is no price history for these
markets (football-data.co.uk carries over / under 2.5 only, and that lost on
both seasons). Prices start with the first build after this ships.

## Not done

- No page view and no Bets tab section; a market that passes earns one in a
  release, Douglas's call.
- No goals calibration.
- The other sports (totals, handicaps): next, once football's shape is settled.
- European handicap (-1) left out: the feed's label direction could not be
  confirmed without prices.
