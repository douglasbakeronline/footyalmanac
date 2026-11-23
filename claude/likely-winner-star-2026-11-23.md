# The likely winner star and Most nailed on (23 Nov 2026)

Douglas, after nine lost slips over the weekend of 21-22 Nov (eight at £100,
one at £20, each beaten by one or two legs): "Can you add a ⭐ emoji next to
all games that meet the likely winner conditions - next to the team name ...
in an effort to continue to pick winners. [State] the most nailed on team to
win by prediction and our model."

## What it does

- `likelyWinner(g, sport)` in `index.html`: a ⭐ beside the picked side's name
  (`winStar`, in `appendFixture` and `sportRow`, so every tab, Starred and
  pinned rows carry it) when the pick is
  - on the Daily List;
  - football: not Celtic's Law or unrated, and priced under `WIN_FB_MAX`
    (1.40) where a price is known (Hill, else the board average, else the
    football archive's best; an unpriced list pick keeps the star);
  - not marked Under 80 (tennis), Away / Neutral / Behind .500 (college),
    Bookies (model 10+ points above the bookmakers), or a context check
    "against".
- Each UK day's **Most nailed on**: the strongest starred pick of the day's
  Daily List (list strength order: confidence, then tested rate), shown as a
  yellow line under the day's head (`nailedLine`) and a larger star on its
  row. Worked out from the unfiltered list (`computeNailed`), so it does not
  move with the sport or band filters.
- A key line in the list's lede explains the star.

Display only. No pick, confidence, list flag, record or grade changes.

## Evidence (the weekend read, `claude/bet-mistakes-proof-2026-11-23.md`)

Football archive 23 Aug to 22 Nov (13,714 graded picks, 6,161 priced):

| Cut | Won | Drawn |
|---|---|---|
| Daily List | 83.8% (185) | 11.4% |
| Reserve | 67.3% (620) | 18.5% |
| Below the bar, 55-70% | 62.1% (2,130) | 20.7% |
| Priced 1.30-1.40 | 78.1% (219) | 12.8% |
| Priced 1.40-1.50 | 68.5% (362) | 17.7% |
| Priced 1.50-1.70 | 59.2% (807) | 24.5% |

Sports: list 91.4% (430) v off-list 75%+ 79.0%. College basketball at 70%+:
home 87% (599), neutral 62% (32), away 46% (24). The Bookies mark: 51% of 193
(`claude/bookies-mark-2026-11-20.md`).

Nine of the weekend's ten losing legs were off the list, reserve or flagged;
the tenth was a list pick bet in another market (Nasaf over 2.5, model 52%).

## Not done

- Football away picks are not excluded: at 75%+ they won 91% (33) v home 83%.
- The 1.40 line is cut from all priced picks; list-only bands are thin
  (1.40-1.50 list picks 5 of 6). Revisit with 50+ starred football picks.
- No record line for starred picks yet. If the star is kept, grade it apart
  (a `winStar` flag archived at publish) so it can be judged on its own.

## Tracked, not shipped: football and tennis at 85%+ (23 Nov 2026)

Looking back (28 Sep to 22 Nov), stars landed 585 of 652 (90%); football and
tennis stars at 85%+ 460 of 496 (93%) v the stars that variant drops 125 of
156 (80%). Football: star 144/173 (83%), 85%+ 49/54 (91%). Tennis: star 65/76
(86%), 85%+ 35/39 (90%). Douglas: "No. But keep track". `tools/star_record.py`
tallies the live star, the variant and unstarred list picks, replayed and live
from 23 Nov; the nightly Card review prints it (`star_section`). Read the two
at 14 days live; put the variant to Douglas only if it is ahead on both spans.

## Roll back

`git revert` the merge. Everything is in `index.html` (`likelyWinner`,
`winStar`, `computeNailed`, `nailedLine`, the `.winstar` / `.nailed` CSS).
