# Today's bets: the weekend's lessons as a front page (25 Oct 2026)

Douglas staked about £100 a slip across the weekend of 24-25 Oct and lost
more than he won (four slips on Sunday: £400 staked, £361.34 back, the one
winner five short favourites at 3.39). He asked for a rebuild that takes
in the lessons and surfaces what serves making money. He chose: a new front
page, no forced groups, no stake advice.

## What the weekend showed

- Most losing slips failed on one pick, and several of those picks were
  ones the almanac had already flagged: Oita Trinita (model 63%, bookmakers
  50%), North Carolina (college football, off the Daily List), Folgore and
  Ordino (weakest on the slip), Wolves (52%, No read).
- Long slips (six to ten picks) lost on one late goal; each pick adds the
  bookmaker's margin again.
- After losses, the ask moved to bigger prices (16x). Declined, and said why.
- On the archive (909 priced picks) the bookmakers price better than the
  model. Under 70%, picks the model rates 8+ points above the market: 31,
  quoted 61%, landed 35%. At 70%+, only 5 such picks (all won): too thin,
  so those are marked Caution, not Avoid.

## What changed

- `index.html` `renderToday`: the front page. Built to land (strict Double /
  Treble), Multipliers, older groups folded away, Leave these out
  (`day.avoid`), Check a slip (matches typed names to `OG.check`, then the
  football board, then the other sports; Back / Caution / Avoid / No read),
  Is it working? (closing-price tally, strict and Multiplier records, "model
  v bookmakers: not yet"), and the six rules in a fold.
- `groupings.py`: `MIN_GROUPS` 0 (no Wider fill); `listOff` on every non-football
  leg, refused by `mult_fault`; `avoid_list` (`AVOID_GAP` 0.08, `AVOID_MIN`
  0.55, level avoid / caution); `check_pool` written into `groupings-data.js`
  as `check` for the slip checker.

## The six rules (shown on the page)

1. Only what qualifies; a blank day is the right answer.
2. Never back a pick the model rates well above the bookmakers.
3. Never back a sport kept off the Daily List.
4. Fewer picks: every extra pick adds the margin again.
5. Take the best price.
6. Judge by weeks: the closing price first, then the profit record.

## Open

- The Multiplier floor lets a leg in at model 40%+ when the bookmakers give
  60%+ (the model is a veto, the market the guide). Those rows show "No
  read" on the board beside a 60%+ quote, which reads oddly. Raising
  `MULT_MODEL_MIN` to 0.50 is the simple fix; on the archive, legs at model
  40-50% in this range landed 64.6% against 56% fair, so it would cost picks
  that have done well.
