# UX release 1: foundations (23 Nov 2026)

Release 1 of the seven-release UX programme Douglas approved on 23 Nov 2026
("Filter and nav options consistent across pages ... Tracking sports and cards
consistent"). Small and nearly invisible: one control, one scale, one empty
state, so the filter bar, day ribbon and ledger releases have one thing to build on.

## One segmented control: `.seg`

Before: seven looks for the same job. `.seg` (joined bar, aria-pressed),
`.dayseg` (gapped, count in `<i>`), `.boards` (joined, ink border, 13.5px),
`.et-seg` (joined, class `on`, surface background, paper text when on),
`.sc-days` (gapped, cover-ink), `.gl-tabs` (borderless, class `on` plus
aria-selected) and racing's `button.chip` meeting and race pickers.

Now every toggle group carries `class="seg ..."` and `.seg` is the only rule set
with a look (CSS under `/* ---------- one segmented control` in `index.html`):

- separate buttons, `gap: var(--s1)`, 1px `--rule` border, 2px radius,
  600 `--t-sm` Barlow Semi Condensed, `--ink-2` text; it wraps on a phone.
- selected: `[aria-pressed="true"]` or `[aria-selected="true"]` (the glance's
  tablist): `--ink` background, `--yellow` text. Class `on` is still set where
  code reads it (`glanceSync`, `.gl-tabs .on`), but the look keys off aria only.
  `slipTracker` and `edgeTracker` now set `aria-pressed` on their ranges.
- the count slot: a number after the label in `<i>` or `.n`, mono `--t-xs`,
  `--mute`, `--yellow-soft` when selected. `.none` (a Bets day with no card)
  is muted unless selected (before, a selected empty day was muted too).
- `.seg--sm`: the compact size (tracker ranges). `.seg--scroll`: one line that
  scrolls sideways (the glance's day tabs, between its arrows).
- phones (860px and under): 44px tap targets, as before.

The old names (`.dayseg`, `.boards`, `.et-seg`, `.sc-days`, `.gl-tabs`) stay in
the markup beside `.seg` because scripts select by them (`#dayseg`,
`.gl-tabs .on`, ...); they carry only layout extras now (`.boards` margin,
`.gl-tabs` gap and `.past` colour). Racing's meeting and race pickers dropped
`button.chip` for `.seg` with `role="group"`; the football competition chips
stay chips (a filter panel, not a toggle group).

## Tokens

In `:root`: spacing `--s1` 4px, `--s2` 8, `--s3` 12, `--s4` 16, `--s5` 24,
`--s6` 40; type `--t-xs` 11px, `--t-sm` 12.5, `--t-base` 14, `--t-md` 16,
`--t-lg` 20, `--t-xl` 26 (the sizes the page used most). About 200 sizes moved
onto the scale where the move was exact or half a pixel smaller (13 to 12.5,
11.5 to 11, 14.5 to 14, 16.5 to 16), never larger, so nothing can newly
overflow; the cover (masthead to corner flash) and the tab bar keep their own
sizes. 12, 10.5, 13.5, 10, 9.5, 15, 22, 18 and 17px are still written out:
moving them changes what a reader sees and is for a release that touches those
components. `#100e0c` is now `var(--cover-ink)` everywhere (42 places).

## One empty state: `.empty`

`.empty` is a boxed note: `--surface`, 1px `--rule`, `--s3` 14px padding,
`--t-base`, `--ink-2`, line-height 1.5, `margin-top: var(--s3)`. An optional
title goes first as `<b class="empty-t">` (Anton `--t-lg`, uppercase: Scale's
old bold heading, and the "Nothing graded yet." leads in How it went). `.tb-empty`
and `.sc-empty` are gone; every caller uses `.empty`. Wording pattern for a
missing build: "No X in this build yet. It appears after the next build."
(Bets, Scale, tennis, the sport tabs); each state keeps its own facts (the
racing feed not connected, the Edge flag's rarity, the slip's reason).

## Checked

Unit suite and nametest; `check.js` (every tab, 1280 and 400, no errors or
overflow); screenshots against main's; a click-through
(`scratchpad/r1-click.js`) of the glance tab, list sport filter, both tracker
ranges, Bets, Scale and How it went day pickers, and every selected button's
background. Racing's pickers could not be seen locally (no racing data off disk).

## Next

Release 2 (the filter bar) builds its controls from `.seg` and `bandCtl`;
release 3 (the day ribbon) replaces the day pickers above with one navigator,
still a `.seg` underneath. New CSS should use the tokens.
