# Odds tab price coverage (12 Oct 2026)

Task: price more legs. No code change: the sandbox cannot reach ESPN (403) and has no API_FOOTBALL_KEY, so no candidate source could be tested.

## Measured, from groupings-archive/ (4 to 12 Oct, legs in published groups)
- football: 81 priced, 12 estimated (87% priced, not two thirds).
- tennis: 0 of 29 priced. Rugby: 0 of 7. NFL 12 of 12. College football 9 of 14.
- The 12 football estimates are Spanish Tercera RFEF, an international friendly, and small AF leagues (Lebanon, Lesotho, Myanmar, Slovakia 3. liga, Turkey 3. Lig, Bavarian Oberliga, Russia second tier). None is a team-name or date matching failure; the bookmakers simply do not list them. Looser matching would add risk of wrong matches (Rule 6) for no gain.

## Where the gap really is
Tennis and rugby. ESPN tennis scoreboards carry no moneyline in the usual feed and rugby feeds have none; this was not testable offline. Any free source for either needs a live check from CI (`python3 groupings.py --probe`) before code is written. The Odds API style free tiers need a key and a terms review, and bookmaker input must stay out of every model (it does).

## Next step
Add a probe of ESPN tennis (`tennis/atp`, `tennis/wta`) and rugby scoreboards to `--probe` so CI reports whether odds blocks exist.

## Re-check, 21 Oct 2026
ESPN is reachable from CI-type sandboxes but carries no odds on tennis (ATP 162, WTA 124 matches) or rugby scoreboards, so it cannot price them; the Odds API (key needed) remains the only route. Football legs still unpriced 4-21 Oct are leagues no bookmaker lists. The one major-competition miss (Al Ittihad v Shabab Al-Ahli, AFC Champions League Elite, 13 Oct) matches ESPN's names under `same()`, so it was not a name or date failure. No code change: looser matching risks wrong matches (Rule 6).
