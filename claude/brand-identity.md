# Football Almanac — identity spec

Replaces the Grays Sports Almanac jacket pastiche, 10 September 2026.

## The mark

Three bars at **45 / 26 / 29** of their own height: the long-run home / draw /
away split in the English top flight. The number the model is built around and
the shape the probability bar draws on every row, so the logo is the site's own
base rate rather than decoration applied to it.

Drawing, 60-unit square: paper ground, 3-unit ink keyline inset 1.5, bars 12
wide with 4.5 gaps starting at x=7.5, baseline y=52.5, tallest 45 tall.

Source of truth is inline in `index.html`. `brandassets.py` redraws the same
geometry in Pillow for the raster assets, so there is no binary in the repo
nobody can regenerate.

## Type

| Role | Face | Notes |
|---|---|---|
| Display / wordmark | Anton | fallback `'Arial Narrow', 'Helvetica Neue Condensed', Impact` — still heavy and condensed if Google Fonts fails |
| UI | Barlow Semi Condensed | unchanged |
| Figures | IBM Plex Mono | unchanged, tabular |

Wordmark: uppercase, two lines set solid at `line-height:.82`, `letter-spacing
-.022em`, size `--wm: clamp(32px, 8.2vw, 68px)`. "Football" in ink, "Almanac" in
brand red. **No outline or shadow** — the old title needed eight text-shadows to
survive a grey ground, which is fragile at any size and illegible small.

Mark is sized off the wordmark (`calc(var(--wm) * 1.62)`) rather than its own
clamp, so the lockup cannot drift apart at an awkward viewport width.

## Colour, with measured contrast on the paper ground (#f0e8d6)

| Token | Value | Ratio | Use |
|---|---|---|---|
| `--brand-ink` | #14100c | 15.5:1 | wordmark, rules, sticky bar ground |
| `--brand-red` | #b4222b | 5.4:1 | wordmark second line, accent. Clears AA for body, so usable at any size |
| `--home` | #1f3b5c | 9.4:1 | home probability |
| `--mute-ink` | #6e6355 | 4.8:1 | **new** — small labels. Replaced `--mute` at 3.4:1 |
| `--draw-ink` | #7a5c12 | 5.1:1 | **new** — Lean tier label. Replaced `--draw` at 3.0:1 |

`--mute` and `--draw` are kept for fills and rules where the ratio does not
apply, so nothing carrying meaning changed colour.

## Responsive behaviour

- Masthead: mark + eyebrow + wordmark, tagline, stat strip. ~210px before the
  first fixture, against ~420px for the cover it replaced.
- Sticky bar: `position: sticky; top: 0`, carries a compact lockup plus the two
  board buttons. **Must be a sibling of `<header>`, not a child** — a sticky
  element only sticks inside its own containing block.
- The lockup fades in via IntersectionObserver on `.brand`, collapsing to
  `max-width: 0` when at rest so no empty slot shows. Progressive enhancement:
  no observer means it stays hidden and the masthead does the job.
- Below 560px the nav wordmark drops and only the mark shows.
- Filter controls lose `position: sticky` below 861px. Two pinned bars eat a
  quarter of a phone screen, and the control that needs to persist is now above.

## Assets

| File | Purpose | Why not inlined |
|---|---|---|
| favicon | data URI in `<link rel="icon">` | keeps dashboard.html self-contained |
| `icon-180.png` | iOS home screen | the picker fetches it |
| `og.png` (1200×630) | share card | every unfurler fetches it |

Both PNGs are copied into `_site` by `deploy.yml`. Without that step every
shared link renders as a blank card.

Metadata added: `theme-color` for light and dark, `color-scheme`, description,
full Open Graph and Twitter card set pointing at
`https://douglasbakeronline.github.io/footyalmanac/`.

## Not done

- No dark theme. The page commits to the paper ground; `theme-color` handles the
  browser chrome only.
- Flag sprite covers 13 countries. `flag()` reads the sprite at runtime and
  renders nothing for the rest, so the 60-odd new competitions show without one.
