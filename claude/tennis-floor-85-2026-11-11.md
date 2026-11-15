# Tennis at 85% on the Card, a warning under 80%, rows that hold their place (11 Nov 2026)

## What Douglas asked

After a William Hill five-fold lost on Casper Ruud at 1.22 (the other four
landed): "Learn from this immediately. Tennis score must go lower." Put to him:
lowering tennis numbers would make them wrong, because graded tennis lands on
or above its quote from 70% up; instead (1) the Card takes tennis only at 85%+
and (2) any tennis pick under 80% carries a warning. He said "Both". The same
evening: "whenever I click on a fixture on the daily list it auto scrolls back
to the top ... fix this immediately."

## The evidence shown to him

Graded tennis, 1,422 picks, landed v quoted: 50-60% 53.7 v 54.6, 60-70% 62.5
v 64.5, 70-80% 75.6 v 74.5, 80-90% 86.8 v 84.6, 90%+ 96.7 v 92.8. The model
is not over-confident in the bands that reach a slip. The leak is the Card:
tennis legs 22 of 40 (z -2.2), most of them 75-85%. A 1.22 leg (about 80%)
loses one time in five; that is what happened.

## What changed

- `groupings.CARD_SPORT_MIN` tennis 0.75 -> 0.85, `CARD_RULE` 10. The owner's
  call, not a gate pass: no tennis price history exists to replay the floor.
- `BOOKS_SPORT_MIN` keeps UK-book pricing (`books_wanted`) at 75%, so the
  Hill price still shows on 75-85% tennis picks.
- `tools/card_replay.py` `tennis75` replays the old floor beside live;
  `tennis80` stays (rule 6 family).
- `index.html` `tennisWary`: an "Under 80" mark on every tennis row under 80%
  (list, tennis tab, started rows), with the reason in its title.
- `index.html` `holdPlace`: opening or starring a row redraws its board, and
  the redraw emptied the board for a moment, so the browser clamped the
  scroll. The tapped row is now put back where it was on the screen. Checked
  at 390 and 1280 wide: the row's top is unchanged after opening (540 -> 540;
  on the old page a second open moved it 531 -> 82).

## What would reverse it

At 30 tennis Card legs under rule 10, if `tennis75` beats live on the pool
(p(worse) <= 0.30), the floor goes back. If 85%+ legs land under quote by two
standard errors on 50, tennis comes off the Card (the existing tripwire).
