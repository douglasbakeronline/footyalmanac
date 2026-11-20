# The Bookies mark (20 Nov 2026)

Douglas, 20 Nov 2026, after reviewing a ten-pick slip by hand with Claude
(sources, team news, tables, prices): "Can we learn from this method to apply
to anything in the almanac for automation of cards", then "build now please".

## Which of the hand review's checks had evidence

The review made five kinds of check. Each was set against what the repo has
already tested before anything was built (Rule 10):

| check | example on 20 Nov | already on file | built? |
|---|---|---|---|
| model v bookmakers | SFA 83% v 63% (DraftKings via ESPN), SDSU 81% v 68% | `tools/market_check.py`: picks the model rates 5+ above the market land at the market's rate | **yes, the Bookies mark** |
| table and form (is the favourite good, or only the opponent bad?) | Lok Leipzig, GD 0 v RSV Eintracht, bottom | `claude/mismatch-rule-2026-11-11.md`: Douglas's top-v-bottom rule wins as often as priced over five seasons; table position, last-5 GD and last-3 points make the model worse (`claude/model-ideas-2026-10-25.md`) | no |
| team news, rotation | Bayern's injuries, Dortmund II before the first team's game | `tools/team_news_eval.py`: API-Football injury lists add nothing that passes | no; the context check (`context_review.py`) reads it, paused to 1 Dec |
| draw risk (draw no bet) | Dortmund II, Lok, Ouchy | `markets.py` tracks draw no bet, on quote; no draw-risk rule tested | no; tracked by `markets.py` |
| started picks | Bronzetti, Shakhtar in play | the page pins started rows | nothing to add |

The noise the review threw out (user polls, tipster scorelines, unchecked AI
overviews, pre-match formations, bet builder legs with no evidence such as
cards) is not automated either.

## The evidence for the mark

`tools/market_gap.py` on `results-ledger.json.gz`, 3 Oct to 20 Nov 2026,
every sport, model 60%+, settled picks with a first real price. The ledger
keeps the pick's price only, so the bookmakers' fair chance is 1 / price /
1.05 (an assumed margin; the page uses each leg's real fair chance).

| model above bookmakers | picks | landed | model | bookmakers | return |
|---|---|---|---|---|---|
| under | 706 | 80.0% | 71.9% | 79.1% | -4.1% |
| 0-5 | 330 | 75.8% | 74.9% | 72.5% | -0.6% |
| 5-10 | 204 | 57.8% | 71.8% | 64.8% | -14.3% |
| 10-15 | 94 | 56.4% | 70.4% | 57.8% | -7.6% |
| 15+ | 99 | 46.5% | 72.0% | 48.4% | -9.7% |

At the 10-point mark: 193 picks landed 51.3% against the model's 71.2% and
the bookmakers' 53.0%; the other 1,190 landed 74.2% against 71.9%. College
basketball 15+ above: 48 picks, 37.5% v 75.3%. Football 10+: 81 picks, 55.6%
v 67.8%. The 5-10 band is also poor (57.8% v 71.8%); the mark starts at 10
because that is where the read was registered before this tally was run, and
the existing 5-point veto already covers the Card, the slip and the
Multipliers.

## The mark

`bookGapChip(g, sport)` in `index.html`, on the football board's rows, the
sport tabs and pinned Daily List rows, beside the Neutral / Away / Behind
.500 marks and in the same style: **Bookies NN** when the model is
`BOOK_GAP` (0.10) or more above the bookmakers' fair chance, NN that chance.
The fair chance, first found:

1. the build's own price, `groupings.board_prices` `f` (the leg's `fair`; on
   past prices the pool's `fair` or `priced.fair`), only when its pick is the
   row's pick;
2. the football fixture's market line (`g.market.p`), the outcome the model
   favours (no mark on a draw read);
3. ESPN's moneyline on a US game (`g.line` `mlH` / `mlA`, the margin removed
   in proportion: `mlFair`, the same as `market_gap.ml_fair`). This is what
   marks college basketball games no UK book prices.

Display only. The number on the row is unchanged, the Daily List still takes
no bookmaker input (Douglas's standing decision) and nothing feeds a model.
Checked at 1280 px and 400 px on the 20 Nov build: 22 marks on college
basketball, SFA "Bookies 63" and SDSU "Bookies 68", no console errors.

## What to watch

- The tally is a read of the past seven weeks, not a pre-registered test.
  Re-run `python3 tools/market_gap.py` at the 30 Nov review: if marked picks
  stop landing under the model, the mark goes.
- If it holds, the next step is a rule, not a mark: a 10-point (or 5-point)
  model-above-market veto on the Daily List 2x / List card legs, replayed on
  the ledger first. The Card already vetoes model-above-market legs under
  rule 14's value demand.
- The ESPN moneyline is DraftKings' US line, not a UK price; the hover names
  the source.
