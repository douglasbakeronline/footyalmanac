# UX release 4: the address bar (23 Nov 2026)

Release 4 of the seven-release UX programme Douglas approved on 23 Nov 2026
("Every page needs to be able to be navigated in the same way ... a familiar
book one can navigate and filter through"). The review's point: a book has
page numbers. The address now carries the page's place, so Back steps back
through the pages a reader turned and a link opens the same page.

## What was there

The view switch wrote `#<view>` with `history.replaceState` (an empty hash for
the Daily List), the hash was read once on load, and nothing listened for
`popstate` or `hashchange`. Back left the site; a link always opened on the
page's own default day with nothing filtered.

## The format

`#<view>[/<day>][?<key>=<value>&...]`, e.g. `#fixtures/2026-11-24?band=85&order=time`,
`#list?sport=nba,tennis`, `#sport:nba/2026-11-22`, `#results/2026-11-20?board=football`.

- **view**: a `data-view` value, as before (`today` is Bets, `sport:nba` a sport
  tab). Unknown or hidden views open the Daily List.
- **day**: a UK date, or `week`. `today`, `yday` / `yesterday` and `tmrw` /
  `tomorrow` are read (and turned into dates) but never written. Written only
  when the open page shows `DAY` (a visible ribbon has it selected); How it
  went keeps it while its records load.
- **keys**: `sport` (the page's own set, `FVIEWS[k].sport`: list, Starred,
  Bets, Scale), `band`, `show`, `order` (the shared `FILT`, written only when
  the page's filter bar is on screen and the page honours the value, through
  `fShow` / `fOrder`), `board` (football `btts`; How it went's board, any key
  of `resGrid`). Only values that differ from the defaults are written, so the
  plain front page has no hash. Unknown keys and bad values are ignored.

## The functions (in `index.html`, just above the view switch)

- `navHash()` serialises the page as it stands; `navParse(h)` reads a hash into
  `{view, day, q}`.
- `navWrite(push)`: `pushState` when `push` and the hash changed, else
  `replaceState`; the state object is `{almanac: 1, day: DAY}`. `NAV.last`
  remembers what was written. Skipped while `NAV.applying`.
- Writes hooked at the single points: the view switch (push, after the render),
  `setDay` (push), the filter bar's delegated `.fbar [data-fb]` handler and
  `data-fclear` (replace), football's `#boards` switch (replace),
  `resBoardClick` (How it went's board, push; the five copies of the old
  `#resSport` handler now share it) and the first draw of How it went once its
  records arrive (replace).
- `navApply(how)`: on load, `popstate` and `hashchange` (both fire for one
  change; a hash equal to `NAV.last` is skipped). The site's own entries
  (`history.state.almanac`) restore the view, the entry's `DAY` (even one the
  page did not show) and How it went's board, and keep the filters as they
  stand: they are shared and hold as pages turn, and filter taps replaced the
  entries, so restoring them would undo taps. A load, a typed address or a
  plain `href="#..."` link applies its filters through `navFilters`, which
  writes `FILT` (and `fSave`) and the page's sport set as a tap would. The view
  is opened by clicking its tab under `NAV.applying` (so the click sends
  `tab_view` once and pushes nothing); the same view redraws through `setDay`.
  Then `navWrite(false)` normalises the address.

## Judgement calls

- **Back keeps the filters.** Douglas chose shared filters that hold as pages
  turn; Back restores the page, not an older filter choice.
- **How it went's board is a page, football's Board a filter.** The first
  changes the whole board (push), the second sits in the filter bar (replace).
- **Not in the address:** football's competition set, the racing board, Scale's
  ladder sport, open rows and folds.
- **A date, not a word.** A link sent on Monday for "Tmrw" opens Tuesday on
  Wednesday too.

## Checked

Unit suite and nametest; `check.js` at 1280 and 400; `scratchpad/r4-nav.js`
(87 checks at both widths: old and bad hashes, the deep links, Back six steps
with `tab_view` counted, filter taps adding no entry, reload, a typed hash,
How it went's board) and `r4-extra.js` (Starred's sports, football's board, a
plain hash link).

## Next

Release 5 (the row) and 6 (the ledger) should put any new page state a reader
would want to link (a Cards board in How it went) through `navHash` /
`navParse` and call `navWrite` at its single point of change.
