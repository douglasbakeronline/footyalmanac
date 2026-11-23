# College basketball tiers: Banker, Solid, Caution, Leave out (23 Nov 2026)

## The ask

Douglas, 23 Nov 2026: "I feel like the college basketball games are a bit hit and miss. Is there a way to kind of like tier real confidence levels of these games?", then "I like the idea of signaling bankers solid and caution and leave out."

## The evidence

Every graded college basketball pick in `sports-graded.json`, 1 to 23 Nov 2026 (997 games). The model lands as quoted by band overall (80-85% 84% v 82%, 85-90% 89% v 88%, 90-95% 95% v 93%). The misses gather where the venue or ESPN's spread for the pick says the game is closer than the model thinks.

Picks at 70%+, by tier:

| tier | rule | landed | quoted | z |
|---|---|---|---|---|
| Banker | at home, the line favours the pick by 12+ | 96 of 101 (95%) | 90% | +1.8 |
| Solid | at home, no line posted (mostly small-conference mismatches) | 392 of 439 (89%) | 85% | +2.7 |
| Caution | a neutral court, or the line 6 to 12 | 38 of 57 (67%) | 81% | -2.8 |
| Leave out | away, or the line under 6 (or the pick the underdog) | 36 of 69 (52%) | 78% | -5.1 |

It holds in both halves of the range: at 70-80% Caution 56% v 75% and Leave out 53% v 74%; at 80%+ Banker 98% v 91%, Caution 75% v 86%, Leave out 50% v 85%. Three weeks of one season; the weak tiers are small.

It overlaps marks already on the row: the Away / Neutral mark (`sideWary`, which the tier now replaces on a tiered college basketball row) and the Bookies mark (10+ points above the bookmakers' fair chance, which catches most "line under 6" picks).

## What was built

- `sports.college_tier` (`TIER_MIN` 0.70, `TIER_BANKER` 12, `TIER_CAUTION` 6) and `sports.by_college_tier`, a tally written to `sports-record.json` as `collegeTiers` on every build.
- `collegeTier` / `collegeTierChip` in `index.html`, the same rule: one chip under the number on every college basketball row at 70%+ (Daily List, the reserve, the college basketball tab, Starred). Banker filled green, Solid green outline, Caution amber, Leave out filled red. The hover gives the tier's live record from `collegeTiers`.
- A key at the top of the college basketball tab (`tierKey`) with each tier's record.
- An upcoming game with no line more than `TIER_WAIT_H` (18) hours out shows no tier: ESPN posts the line on the day, so "no line" there is not yet the Solid case.
- The ⭐ likely winner is not given to a Caution or Leave out pick.

Display only. The line is a bookmaker number, so it never reaches the model or the Daily List (Douglas's standing decision); the model's number, the list and the grading are unchanged.

## What to watch

`collegeTiers` in `sports-record.json` grades every tier forward. If Caution or Leave out land at or above their quote on 100+ new picks, the tier is not earning its place and comes off. Graded rows are tiered on their last pre-start copy, so a game whose line came out after the last build before its start is tallied as Solid.

## Leave out off the Daily List (23 Nov 2026, later)

Douglas: "remove leave out from daily list". A college basketball pick tiered Leave out no longer shows on the Daily List or in its reserve fold, whatever William Hill prices it at (`listShown`, `itemTier`, `resShown` in `index.html`); it stays on the college basketball tab with its chip, and the day's left-off line and the reserve note count it. The William Hill 1.05 rule was letting the closer, priced games through, so it favoured Leave out picks (6 of the 8 Leave out list picks since 1 Nov had a Hill price of 1.05+, against 8 of 223 Solid). Display only: the pick keeps its list flag and is still graded as a list pick, like the picks the 1.05 rule leaves off.
