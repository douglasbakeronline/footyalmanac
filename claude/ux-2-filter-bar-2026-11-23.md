# UX release 2: the filter bar (23 Nov 2026)

Release 2 of the seven-release UX programme Douglas approved on 23 Nov 2026
("Every page needs to be able to be navigated in the same way ... Filter and nav
options consistent across pages"). The review's "index": one filter bar, in the
same place and the same order on every page that filters, with the choice
shared across tabs (his call).

## What was there

Seven sets of controls doing the same job differently: the list's Order by
(`#listSort`, `listOrder`), Show (`#listBook`, `listBook`) and sport chips
(`.list-sport`, `listSport`); `bandCtl(scope, confs)` per tab (`bandBy`, one
band per tab); `tabOrderCtl()` on tennis and the sport tabs (`tabOrder`);
Starred's `.star-ctl` block (`starView`: order, sports, tag, open); football's
`#boards`, `#show`, `#sort` and the competition toggle, in a sticky bar that the
two-row tab bar (16 Nov) had half covered. Bets, Scale and How it went had none.
On a phone the Daily List showed five rows of chips before the first pick.

## The component

`filterBar(view, opts)` in `index.html` (under `BANDS`) returns the bar's HTML.
Groups, each only where it applies, always in this order:

1. **Sport** (`opts.sports`), multi-select through `toggleSport`, on the pages
   that span sports: Daily List, Starred, Bets, Scale.
2. **Confidence** (`opts.confs`), the `BANDS`, one selected; a band with no
   rows is not offered (as before).
3. **Show** (`opts.show`), one vocabulary (`SHOW_LABEL`): Every pick, Daily
   List, Reserve, Board only, At William Hill, Edge, Still to start, Confident
   only. Football keeps "Every fixture" and "Confident only"; an option with
   no rows is not offered.
4. **Order by** (`opts.order`, `ORDER_LABEL`): Strongest and Kick-off time
   everywhere; football adds Upsets and Goals, Starred adds Sport and List first.
5. The page's own controls (`opts.extra`, built with `fbarGroup`): football's
   Board and Competition, Starred's Full details.

Under the groups, one summary line (`.fbar-sum`): the active filters as
removable chips (`data-fb="unset"`), the count ("12 of 95 picks", `opts.count`),
and Clear filters (`data-fb="clear"`). `opts.note` adds a line under it (the
list's "Groups A and B ... not shown while filtered"). Every group is
`role="group"` with `aria-label` and a visible label; toggles carry
`aria-pressed`. One delegated click handler (`.fbar [data-fb]`) updates the
state, redraws the view through `FVIEWS[view].redraw` and puts focus back on
the same button.

Empty states use `fbEmpty(view, text)`: the `.empty` box with a Clear filters
link (`data-fclear`), replacing `data-lclear`, `data-sclear` and the "Pick All"
wording.

**Phone (600px and under):** the groups fold behind one "Filters · n" button
at the front of the summary line (`aria-expanded`, `aria-controls`), the chips,
count and Clear stay on that line. Tapping opens the groups inline below it (a
disclosure, not a modal); focus moves to the first control, Escape or the
button closes it and returns focus to the button. The open state is kept per
view in memory (`FB_OPEN`) while the bar redraws. Closing football's bar also
folds the competition panel.

## Shared state

`FILT` = `{band, show, order}`, stored as `almanacFilters`, read through
`fClean` (any unknown or corrupt value reads as the default; a non-JSON value
reads as all defaults). With no `almanacFilters` yet, `fMigrate` reads the old
keys once: the band from `bandBy` (the list's first, then football, tennis,
Starred, then any), Show from `listBook` ("hill") else `starView.tag`, Order
from `listOrder` or `tabOrder` ("time") else `starView.order`. The old keys are
left in place.

`FVIEWS` says what each view can honour. `fShow(view)` and `fOrder(view)` give
the value to apply: the shared one if the page lists it, else the page's
default, without overwriting the stored value (Confident only chosen on
football shows Every pick on tennis and comes back on football). `bandOf` and
`inBand` keep their names and signatures; the scope argument is now ignored.
`bandCtl(scope, confs)` stays as a thin wrapper (nothing calls it now).

Sport stays per page: `LIST_SPORTS` (`listSport`), `STAR.sports`
(`starView`, which now keeps only `sports` and `open`), `BETS_SPORTS`
(`betsSport`) and `SCALE_SPORTS` (`scaleSport`), comma lists read by
`fSportLoad`. Clear filters (`fClear`) resets the page's sports, the band where
the page has Confidence, Show where the page honours it, and football's
competitions (`fbClearComps`); never Order.

## Per page

- **Daily List**: Sport, Confidence, Show (Every pick / At William Hill, when
  the build has `listBooks`), Order. The bar sits under the jump strip, right
  before the first day. Groups A and B unlabelled while sport or band filter, as
  before.
- **Starred**: Sport, Confidence, Show (its seven tags, `STAR_TAGS`; "Everything"
  is now "Every pick"), Order (four), Full details.
- **Football**: in `#controls` (`#fbBar`), redrawn by `render()` (now also on
  every switch to the tab, so a band set elsewhere applies). Confidence, Show
  (Every fixture, Confident only, Daily List, Reserve, Edge), Order (Strongest,
  Upsets, Goals, Kick-off time; Strongest is "Most likely" on Both to score),
  Board, Competition; the competition choice is a chip too. `state.show` and
  `state.sort` are derived from `FILT` at the top of `render()`. Switching board
  drops Upsets or Goals back to Strongest, as the old reset did. `.controls` is
  no longer sticky.
- **Tennis and the sport tabs** (`tabBar`): Confidence, Show (Every pick, Daily
  List, Reserve: the rows carry `list` and `reserve`), Order. Played today and
  yesterday follow the same filters.
- **Bets**: Sport only, under the day picker. A group (the Card, the Daily 2x,
  the List card, the slip, the old and paper groups) shows when any of its legs
  is in the chosen sports (`betsOk`); the Edge picks list and the Card's other
  picks filter their rows; a hidden section says why with Clear (`betsEmpty`).
  Trackers and the record are not filtered.
- **Scale**: Sport, Confidence (the winner's chance, `p.conf`), Order (Strongest
  is the existing tier and rank order; Kick-off time sorts within each tier),
  in the day's list under its day tabs; groups follow the Bets rule. The glance,
  scoreboard and ladder are not filtered.
- **How it went**: Confidence on the Daily List board's day rows and reserve,
  under the day picker. The tiles, the glance and the day's tally stay whole.

## Judgement calls

- **Scale's ladder sport stays with its table.** The brief put it in the bar;
  it controls the "Every scale bet" table near the foot of the page, and in the
  top bar it would read as filtering the day's rows. It is already a `.seg`.
- **Football's controls are no longer sticky.** The bar is taller with its
  summary line, and the old `top:47px` had slid half under the two-row tab bar
  since 16 Nov. Every page's bar now sits in the page the same way.
- Order is not counted as a filter: no chip, not in "Filters · n", not reset by
  Clear.

## Checked

Unit suite and nametest; `check.js` (every tab at 1280 and 400, no errors, no
overflow); `scratchpad/r2-click.js` (band, sport and chips on the list; 85-89%
held on Basketball and Tennis and after a reload; Clear; tennis Show; football
Confident only, order, board, competition chip; a football-only Show falling
back on tennis while stored; Bets on 24 Nov with Basketball: the football Daily
2x hidden with Clear, the slip with an NBA leg kept; Scale rows 15 to 5; How it
went's bar; phone fold, focus and Escape; migration from seeded old keys;
corrupt and non-JSON stored values); `scratchpad/r2-star.js` (three starred
rows filtered by sport and tag, Clear).

## Next

Release 3 (the day ribbon) replaces the jump strip, the Bets and Scale day
pickers and How it went's pickers; the bar already sits between the day picker
and the first day on those pages, which is where the ribbon will be. Release 4
(the address bar) can serialise `FILT` and the page's sport set into the hash:
`filterBar`'s click handler is the one place state changes.
