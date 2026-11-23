# UX release 7: Analysis in the same shell (23 Nov 2026)

The last release of the seven-release UX programme Douglas approved on 23 Nov
2026 ("Every page needs to be able to be navigated in the same way ... Filter
and nav options consistent across pages"). Almanac Analysis had drifted from
the Almanac: an older copied `:root`, its own nav markup and link styles, a
joined segmented control, and cumulative brackets where the site uses bands.

## Why copies, and a test

The site ships self-contained pages (`dashboard.html` is one file on purpose),
so the fix is not a shared stylesheet. `analysis.html` carries word-for-word
copies of three pieces of `index.html`, and `tests/test_shell_sync.py` fails CI
when they differ, naming the token, tab or line and where to fix it:

- **Tokens.** Every custom property in `index.html`'s first `:root` block must
  be in `analysis.html`'s with the same value. Before: `--row-cols`' middle
  column 72px v 96px, no `--edge-soft`, none of release 1's `--s1..--s6` /
  `--t-xs..--t-xl`. Now the block is index's, verbatim.
- **The tab bar.** CSS from `/* ---------- top-level views` to the new marker
  `/* ---------- end of the shared tab bar (23 Nov 2026, UX release 7)` in
  `index.html` is the same block in `analysis.html` (so Analysis's bar is now
  pinned on scroll, as the Almanac's is; section anchors carry
  `scroll-margin-top` so a heading lands below it). The markup lists the same
  tabs in the same order with the same labels: index's `data-view="<v>"`
  is Analysis's `href="./#<v>"` (the Daily List is `./#list`, which the
  Almanac normalises to its plain front page); index's `hq-link` to
  `analysis.html` is Analysis's own `<a href="analysis.html" aria-current="page">`.
  The open tab's look keys off `[aria-current="page"]` (added beside
  `[aria-pressed="true"]` and `.nav-on` in the shared block); the old
  `span.nav-on` and `.views a.nav-a` rules are gone. The sport tabs still hide
  by the Almanac's rule in a small script of their own (now reading the hrefs,
  no `data-sport`).
- **`.seg`.** The block from `/* ---------- one segmented control` to
  `.seg--scroll button{flex:0 0 auto}`, with the selected-state rule checked on
  its own too. Analysis adds index's phone rule (44px buttons under 860px).

The test also checks that `analysis.html`'s `const BANDS` equals index's and
that the cumulative bracket buttons are gone. Change `index.html` first, then
copy the block across.

## Day by day on the site's bands

`#brkseg` was All / 50%+ / 60%+ / 70%+ / 80%+ / 90%+ plus two from/to selects.
Now it is the Almanac's Confidence group (`.fbar-g`, `.ctl-label`, a `.seg`
with `aria-pressed`): All, 90%+, 85-89%, 80-84%, 70-79%, 60-69%, Under 60%,
each with its game count, a band with no graded games not offered, built by
`setupBracket` from `BANDS` (`bandSlots` maps a band onto `byDay[].b5`'s
5-point slots; every edge is on a 5-point line, so the sums are exact).

- **Shared choice.** It opens on the band in `localStorage.almanacFilters`
  (the filter bar's `FILT`, release 2) and a tap writes the band back, leaving
  `show` and `order` alone (`filtRead`, `filtBand`, `filtSave`, all in
  try/catch; a bad stored value opens All). With nothing stored it opens on All
  (it opened on 70%+ before).
- **Kept as a line.** The cumulative figures the brackets gave are
  `#brkcum`, "Running figures": 60%+, 70%+ and 80%+ (the Daily List's bar),
  won v quoted over every graded day (`renderCum`).
- **Rounding.** The record bins on the raw chance and the Almanac's rows on the
  rounded one, so a call at 89.6% is 85-89% here and 90% on a row; the page
  says so. Nothing was regraded.

## Links into the site (release 4's addresses)

The day-by-day summary ends with today's picks in that band on the Almanac:
`./#list?band=85` and `./#fixtures?band=85` (`bandHref`). Opening a 5-point row
of the banding table adds a line naming the Almanac filter it sits in
(`bandOfFrom`) with the same two links. Checked: the link opens the Daily List
with 85-89% pressed and the hash kept.

## Not changed

The cover (Analysis's own words), GTM and GA4, the responsible-gambling banner,
the banding table's 5-point rows, the calibration chart, the prose, `record.json`.
No link to the repository or HQ. On `index.html` only the two `aria-current`
selectors, the end-of-block marker and a line in the `BANDS` comment.

## Checked

Unit suite (with the new test) and nametest. The new test shown failing on a
scratch copy with `--row-cols` back at 72px, `--s3` at 13px, an extra Starred
tab and the `.seg` selected text in white, each message naming the difference,
then passing on the real files. `check.js` on `analysis.html` and on
`index.html` at 1280 and 400 (no overflow; Analysis's only error is the
`file://` record fetch, as before). Served over `http.server`:
`scratchpad/r7-click.js` (band labels and order, one pressed, the count equal
to the table's rows, the shared filter written and read both ways, reload,
garbage storage, the band links, the current tab's look) and screenshots of the
cover (unchanged), the tab bar, day by day and an opened band at both widths.

## Next

The programme is complete. A new page must carry the same three blocks and be
added to `tests/test_shell_sync.py`.
