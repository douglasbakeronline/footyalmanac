# Scale: three tiers, five sports, ten games a day (15 Nov 2026)

Follows `claude/scale-2026-11-15.md` (the tab's first version, the same
morning). Read that first for the archive and grading; this note is what
changed and why.

## What Douglas said

On the first live day the tab showed two football picks and no group: "it's
just kind of showing like one game per day ... we're going to have to be a
little bit more flexible with our floor ... I think we're going to need at
least 10 games per day ... break it down into tiers with lines on that
infographic that say daily list pick, daily list reserve pick, everything
else, and list it from strongest to weakest in whatever way you see fit ...
football it's going to be winner and both teams to score. Tennis, winner and
straight sets ... NFL, basketball, you're going to need to propose something
based on the data ... I need every day to have at least 5 games, to add into
some sort of scale accumulator."

## What changed (`scale.py` `RULE` 2)

**Tiers** (`TIERS`), shown in this order on the glance and the list:

| Tier | What it is |
|---|---|
| `list` | a Daily List pick, at the list's own bar |
| `reserve` | a Daily List reserve pick (under the bar, Firm 62%+, clean) |
| `else` | everything else the model picks at `FLOOR` (55%+), strongest first, only as many as bring the day to `TARGET` (10) games |

Within a tier the order is the chance the Scale bet lands (`rank`). The
"else" tier is a top-up (`choose`): only games still to start are taken, and
an "else" game that has started is never added after the fact, so the tier
cannot be picked with hindsight. `daylist.pinned(..., every=True)` returns
the games on neither the list nor the reserve.

**Sports** (`SPORTS`). The proposal for the margin sports, from every graded
pick in `sports-graded.json`:

| Sport | Scale bet | At William Hill | Picks at 55%+: won, landed | Picks at 75%+: won, landed |
|---|---|---|---|---|
| Football | win and both teams score | priced on the feed | see below | see below |
| Tennis | win in straight sets | set betting 2-0 | 1,052: 67%, 48% | 243: 88%, 66% |
| NBA | win by 10 or more | handicap -9.5 | 152: 70%, 43% | 31: 94%, 65% |
| NFL | win by 7 or more | handicap -6.5 | 69: 67%, 43% | 17: 88%, 65% |
| Rugby | win by 8 or more | handicap -7.5 | 69: 81%, 58% | 35: 91%, 66% |

Why those lines: at the list's level each lands about two times in three,
the same shape as tennis in straight sets, and each is a line every UK book
offers as an alternative handicap. A smaller margin (the NBA by 5+: 72-89%
at 75%+) would barely move the price; a bigger one (by 12+: 39-56%) is a
coin toss even for list picks. The samples are small (the NBA 183 graded
games, the NFL 90, rugby 88), so the chance shown is the record's rate in the
narrowest confidence band holding 30 picks (`band_rate`: `FINE`, then each
of `WIDE`), written out as "N of M picks like it". A tally, never a fit.

College basketball and college football are left out: UK books rarely price
them (the Daily List already hides college basketball without a Hill price).
Baseball, the WNBA and ice hockey have no margin data worth a line yet.

**Football by tier**, picks graded before the tab in leagues Hill prices now
(results only): list 43 picks, 81% won, 33% with both scoring; reserve 86,
65% won, 33%; everything else at 55%+ 300, 60% won, 26%. The reserve wins
less often but lands the Scale bet as often as the list, because strong
favourites win to nil more.

**Groups** (`KINDS`): a threefold, fourfold and fivefold from the top of the
list's order, any sport, and a **Football threefold** of the top three
football picks, the one group priced on every leg (so the one with a profit
and loss). The football threefold is skipped when it is the threefold.

**The page**: Scale at a glance is a grid, a column a tier with ruled lines
and headers (Daily List, Reserve, Everything else). The day's list has a
band per tier. An unpriced pick says what to look for at William Hill
(handicap -9.5, set betting 2-0) and the price its chance needs. The
scoreboard has the record by tier and by sport, then the tallies behind the
chances.

## A grading bug fixed

New Zealand v India was played on 12 Nov (5-0) and again on 15 Nov. The 15
Nov Scale pick was graded "won to nil, 5-0" hours before it kicked off:
`markets._result_for` matched any result of the pairing within three days.
It now refuses a result dated two or more days before the fixture's own
date (a moved fixture's newest archived copy carries its new date). The
same guard covers `markets.py`'s own record. `tests/test_scale.py`
`test_a_result_from_an_earlier_meeting_is_not_this_game`.

## The first day under the rule

15 Nov: 19 picks (6 list, 13 reserve, none needed from everything else), four
groups. 16 Nov: 10 picks (1 list, 7 reserve, 2 from everything else).

## What to be straight about

- **The margin bets and straight sets have no price behind them.** The tab
  says how often they land, not that they pay. A price feed check is next
  (API-Sports lists handicap markets; a probe on `odds-probe-run`, names and
  counts only).
- **Lower tiers land less.** A reserve NBA pick by 10+ is about 42-44%, a
  list pick about 50% on the bands that hold 30 picks. A fivefold of legs at
  45% lands about 1 in 50. That is what scaling the odds means; the tab shows
  "Lands 1 in N" on every group.
- **Ten is a target, not a promise.** On a day with no NBA, NFL or tennis and
  little football at Hill the list will be short; nothing under 55% is
  added to pad it.
- **Football's Hill prices have so far been under what the model's number
  needs.** The football threefold is marked "Price too short" when that is so.

## Not changed

No model, the Daily List, the reserve's rule, the Card. Picks already
archived under rule 1 keep their place (read as the `list` tier).

Roll back: `git revert` the merge. Files in `scale-archive/` written under
rule 2 carry `tier` and are harmless to rule 1.
