# Football legs settled from another meeting of the pair (25 Nov 2026)

Found by the 25 Nov build session reading the Card review: the archive table's
window ran "2026-10-29 to 2026-11-28", three days ahead of the build. The pool
replay had settled legs that had not been played.

## The cause

`groupings.results_index` kept a dateless key for every graded football result,
`(None, home, away)`, the first meeting of that ordered pair in
`record-graded.json`, and `groupings.settle` fell back to it whenever the leg's
own date had no result. So a leg settled from any meeting of the pair, however
far from its date:

- Toluca v Atlas, Liga MX play-off, 26 Nov: settled won 5-2 from 12 Sep.
- Real Salt Lake v Vancouver (28 Nov), FC Cincinnati v Nashville, Charlotte v
  Chicago Fire, Philadelphia v New England (all 28 Nov, MLS play-offs): settled
  from league games on 20 Sep, 7 Nov, 26 Sep and 24 Oct.
- On the whole pool, 25 football legs settled through the fallback: 19 from a
  result 5+ days away (USL play-offs from October league games, postponed
  Spanish regional games played two weeks later), 3 a day early, 1 at 3 days,
  2 at 5 days.
- In the Card's day archives, two retired groups took the result of a postponed
  game played later: Balanced 4 Oct (Levante II v Crevillente, played 20 Oct)
  and Stretch 18 Oct (Cieza v Valencia II, played 11 Nov). A bookmaker voids a
  postponed leg.

`settle` is also how the record grades the Card, the Daily 2x and the List card
(`groupings.grade`), how `notify.py` reads a group's legs, and how the replay,
the funnel, `price_timing` and `list_at_book` settle pool legs. A live Card leg
in a play-off rematch would have been graded before kick-off.

## The fix

`_near_result`: the leg's own date first, then the same ordered pair up to
`SETTLE_NEAR_DAYS` (3, as `score.NEAR_DAYS`) either side, nearest first, the day
before first on a tie. The dateless key is gone. A reversed pair is another
fixture, as before. `tests/test_settle_rematch.py` (six).

## What it moves

Pool replay from 29 Oct, before v after (same files, same build):

- 2,217 to 2,208 settled pool legs; the window ends on 24 Nov, not 28 Nov, so
  27 days rather than 30, and every per-day comparison and empty-day count
  stops counting three unplayed days.
- live: unchanged (11 groups, 5 won v 4.53 expected, +12.5%).
- `rule12`: 25 groups to 24 (one built on a wrong result), +9% to +13%.
- `m7under5`: 7 of 19 won to 8 of 19 (-19% to -7%): a wrongly lost leg had
  kept a better group off a day.
- Every other variant's groups unchanged.

The record: the two retired groups above lose their leg's result; the grader
voids it once the other legs have settled (`VOID_AFTER`), as a bookmaker would.
Nothing in the archive or the record was edited by hand.

## Not changed

Any Card rule (`CARD_RULE` 14), the model, tennis and US-sport settling (by id,
and the name fallback already keeps to a day, `_near`).
