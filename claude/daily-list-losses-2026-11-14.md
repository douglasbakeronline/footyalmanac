# Daily List losses, Saturday 14 November 2026

Douglas asked (02:47 Sunday) for a review of the morning's losses: college
basketball, college football and whatever else lost in the reserve, why the
almanac got them wrong, and what to learn. Read from the pinned lists
(`daylist.pinned`), `record-graded.json`, `tennis-record.json` and
`sports.graded_games()` at the 02:00 archive commit. The overnight slate of
Sunday 15 Nov (starting 00:00 to 02:30 UK) is not graded until the 05:15
build and is not in these numbers.

## The day in one line

The list landed as quoted. 37 settled list picks, 33 landed (89.2%), 32.7
expected from the quotes. Group A 5 of 5; Group B 5 of 5. The reserve: 103
settled, 76 landed (73.8%), 76.0 expected. The losses are the 11% the
numbers said would come.

| Group | sport | landed | quoted | expected |
|---|---|---|---|---|
| List | college basketball | 25/28 | 90.7% | 25.4 |
| List | football | 6/7 | 81.0% | 5.7 |
| List | NBA, tennis | 2/2 | | |
| Reserve | college football | 22/30 | 75.7% | 22.7 |
| Reserve | college basketball | 35/46 | 74.9% | 34.5 |
| Reserve | football | 15/20 | 68.3% | 13.7 |
| Reserve | NBA | 3/6 | 72.3% | 4.3 |

## The list's four losses

- Stephen F. Austin 90% v Rice, 78-81: 3-0, 270 rating points better, at
  home. Nothing flagged it.
- Gonzaga 89% v LSU, 80-81: one point. Check ESPN's neutral-site flag.
- Colorado State 88% v Loyola Chicago, 58-73: the rating is mostly last
  season's team (25% summer regression, K 32).
- Pipinsried 80%, 1-1: the draw, 13% on the row.

## The reserve's 27 losses, in patterns

1. College football away favourites (4 of 8 cfb losses). Live cfb 70%+: away
   36 of 54 (67% v 78%, z -2.0), home 94 of 117 on quote.
2. College basketball sides carrying last season's rating (Winthrop 0-3 at
   85%). Tested on the replay the next hour and found not to be a signal:
   see `claude/college-side-mark-2026-11-15.md`.
3. NBA away picks 1 of 4: a night, not a pattern (NBA above quote in Nov).
4. Football: three draws, two lower-league away wins; reserve football above
   its quote.

## The two college sports on the record

College basketball since 1 Nov (517 picks at 62%+): above quote in every
band, 90%+ 120 of 124. College football since 1 Nov: 73% v 76%; before, 70%
v 77%; the historical replay has it above quote in both windows. That gap is
the open question for college football and why it stays off the list.

## What followed

- The Away / Neutral mark on college picks and the by-side tripwire
  (`claude/college-side-mark-2026-11-15.md`), shipped the same night.
- Still owed: a faster early-season K and a higher summer regression for the
  college sports, tested through `sports.py --tune`'s gates; the neutral-site
  flag check before the tournament week (17-27 Nov).
