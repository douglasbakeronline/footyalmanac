# UX release 3: the day ribbon (23 Nov 2026)

Release 3 of the seven-release UX programme Douglas approved on 23 Nov 2026
("The whole site needs to feel like a familiar book one can navigate and filter
through"). The review's "turning pages": one day navigator, past and future, on
every page with days, in the same place on each.

## What was there

Eight ways of choosing a day: the Daily List's At a glance tabs (with their own
arrows and swipe track, `GL_IDX`), the list's Jump to strip (`#listDays`) and
the floating Days button (`#toDays`), Bets' `#tbDay` (`OG_DAY`), Scale's
`#scDays` (`SC_DAY`, past days hidden), racing's day buttons (`RC_DAY`), and How
it went's `#dayseg`, `#tdayseg`, `#sdayseg`, `#ldayseg` (`resState`). Football,
Tennis and the sport tabs had no day choice at all: the whole week, with Played
today and Played yesterday sections on top (`playedSection` / `playedDay`).

## The component

`dayRibbon(view, days, sel)` in `index.html` (after the filter bar's script)
returns the ribbon's HTML: prev arrow, a `.seg .seg--scroll` tablist of day
buttons, next arrow. `days` are `{d, n, none}` in any order ("week" first); `n`
goes in the count slot (`dayTally(won, lost, n)` gives "23/25" for a day
behind). Labels from `dayLabel`: Week, Yday, Today, Tmrw, "Wed 25" within a
week, "Mon 16 Nov" further out. Past days are muted; `none` mutes a day with
nothing (Bets with no Card group). One `role="tablist"` with `aria-selected`
and a roving tabindex; Arrow Left / Right, Home and End move the day and keep
focus on it (`RB_FOCUS`). The fade on a clipped edge is two gradients on
`.rb-wrap` (`fl`, `fr`), set by `ribbonFade` on scroll; `ribbonSync` keeps the
selected day in view after every draw (queued by `dayRibbon` itself).

## Shared state

`DAY` (null, "week" or a UK date) is the one variable, set only by
`setDay(d)`, which redraws the open page. Each page reads it through
`dayPick(keys, default)`: DAY when the page has that day, else the page's own
default, without overwriting DAY (as `fShow` does for Show). So Sat 21 picked
on the Daily List leaves Football on Week, and the list is still on Sat 21 when
you come back. `OG_DAY`, `SC_DAY`, `RC_DAY` and `resState.day / tday / sday /
lday` stay and are set from the pick on each draw, for the code that reads them
(`ogPlacedNote`, `resultDetailFootball`, ...). Release 4 should serialise
`DAY` beside `FILT`: `setDay` is the one place it changes.

## Per page

Order on every page: running head, ribbon, filter bar, the day(s), the record.

- **Daily List**: Week (default), the week behind from `daylist.js` `past`,
  each day ahead. A day ahead shows that day's section alone. A day behind is
  drawn by `listPastDay` as rows (`pinnedRow` via `pastAsPin`, which turns the
  archive's `status` into a result) with Won / Lost; the archive keeps no
  reserve, scores or prices for those days, and At William Hill does not apply.
  At a glance (`todayGlance(sel)`) draws the ribbon's day only (on Week: today,
  or the first day after it with picks); a swipe across it turns the day.
- **Football, Tennis, each sport** (`boardDays`): Week, Yday (when yesterday
  has started games), Today, the days ahead. Yday shows yesterday's started
  games (`playedDaySec`, capped at the board's 50 with Show all); Today and
  Week put today's started games inside today's section under a Started label
  (`playedRows`, after the games still to come, before them in kick-off
  order). Started games follow the page's filters, as before; football's Both
  to score and Edge only have none (the archive keeps no flag), and Yday says so.
  The football ribbon sits in `#fbDays`, above `#fbBar`.
- **Starred**: Week and each starred day.
- **Bets**: OG's days, Today by default, Card groups in the count; the ribbon
  shares a line with the stake box.
- **Scale**: every day on file (past days included, landed of settled),
  Today by default. The ribbon, the bar and the day's list and groups now come
  before Scale at a glance, which is the record over days; its rows call
  `setDay` and scroll up to the ribbon.
- **Horse racing**: the feed's days, its own default (the first with a race
  to come) when DAY is not one of them; the count is tips on the Tips board,
  races otherwise. Checked only on a stubbed feed (no racing data off disk).
- **How it went**: each board's graded days, latest by default; Days at a
  glance rows call `setDay`.

A day with nothing after the filters keeps its button (count 0) and shows the
shared empty state with Clear filters.

## Judgement calls

- **Scale's glance moved below the day.** The brief's order puts the record
  after the day; the glance is the record across days and its rows still open
  any day. Moving it back above the ribbon is one line in `renderScale`.
- **The filter bar's chips still count the week** on a single day; only the
  count line follows the day. Counting chips per day would drop a stored sport
  choice on a day without that sport.
- **The glance's swipe track went**: it is one panel now; a horizontal swipe
  calls `setDay` for the day before or after on the ribbon.

## Checked

Unit suite and nametest; `check.js` (every tab at 1280 and 400, no errors,
no overflow); `scratchpad/r3-click.js` (all pass at both
widths) and `r3-racing.js` (stub feed);
screenshots of every affected tab at both widths.

## Next

Release 4 (the address bar) puts the view, `DAY` and `FILT` in the hash.
Release 6 (the ledger) can take How it went's boards off their day ribbons
once each page's own ribbon reaches back far enough.
