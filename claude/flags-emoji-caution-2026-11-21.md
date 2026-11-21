# Flags on every football row, a sport emoji, and the caution mark (21 Nov 2026)

Douglas: "Not all football games have the flag ... add a sports emoji at the
end of each league or sports name on the fixture rows ... any fixture from a
league that has proven unpredictable ... a little caution emoji discreetly,
with the correct alt text on hover."

## Missing flags

82 of the API-Football wider leagues (`engine.AF_EXTRA`) carried `iso` ""
because their country never appeared in a native league, or appeared under
another spelling ("Macedonia", "United Arab Emirates"); `flag()` renders
nothing for an iso the sprite lacks. 44 countries in all.

- `engine.EXTRA_ISO` gives each its code and `iso_of` reads every spelling;
  wider leagues and API-Football cups both use it.
- index.html's sprite gains 42 simplified 16x11 symbols (Algeria to
  Zimbabwe; Guadeloupe as the French tricolour under `glp`).
- `engine.FLAG_ONLY`: the codes that gained a flag. `eligible_league` reads
  iso for a continental cup's confederation, so a club rated in one of these
  leagues (North Macedonia's, the UAE's, Kazakhstan's) stays out of those
  cups exactly as before. Display only; no rating or lookup changes.
- `tests/test_flags.py` fails CI on any league or cup country without a
  drawn flag, and on a flag-only league becoming cup-eligible.

## Sport emoji

`sportEmoji` puts the sport's emoji after the league or sport name on the
football board, every sport's board (tennis included) and pinned Daily List
rows: ⚽ 🎾 🏈 ⚾ 🏀 🏉 🏒. Decorative, `aria-hidden`.

## Caution mark

`build.unpredictable_leagues` (in the inlined record summary as `caution`):
a football league with 50+ graded picks whose top pick landed 1.5+ standard
errors under the model's number (`CAUTION_MIN_N`, `CAUTION_Z`), from
`record.json` `byLeague`, every build. `cautionMark` draws ⚠️ at 75% opacity
after the league name, with the record as its hover text and `aria-label`
("Unpredictable league: ... landed 20 of 63 (32%) against the 44% it
quoted").

Douglas chose 1.5 standard errors over the site's usual 2 (the sport-off
rule), told that only one league clears 2 and that across 123 leagues with
50+ picks the spread is about what chance alone makes (mean z +0.34, sd
1.12), so some marks will be noise. At 21 Nov: Serie B (z -1.61), Liga MX
(-1.57), Colombia Primera B (-2.24), Turkey 3. Lig Group 1 (-1.82), Italy
Serie D Girone C (-1.95). Display only: nothing ranks, prices or grades
differently.

## Checked

Rendered at 1280 and 400 wide on a page built from the 21 Nov archive: 8
caution marks on the football board with their hover text, every football
row's competition with a flag, new flags (Uzbekistan, Kazakhstan) on rows.
