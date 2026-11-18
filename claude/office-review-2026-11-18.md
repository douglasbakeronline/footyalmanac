# Office review, 18 Nov 2026 (Luke, Chief of Staff)

Covers `RELEASES.md` from 9 to 18 Nov and the `claude/` notes since the
9 Nov review. Record numbers are read only, never fitted (Rule 1). A report by
nature: no code or model change. Follows `office-review-2026-11-09.md`.

## What the office shipped
- **Card rules, owner's calls:** rule 7 model's own picks, rule 8 the 2x alone,
  rule 9 context veto, rule 10 tennis at 85%, rule 11 wider leagues, rule 12
  football opposition 5.0+, rule 13 the model alone (17 Nov). Two-day groups
  (`CARD_SPAN`), filler off.
- **New slips:** Daily 2x (17 Nov, one a day, ledger replay 14 of 28, +22%),
  List card (List 2x / List long), the slip (`slip.py`), the Scale tab with
  every-scale-bet ladder.
- **Data:** results ledger, markets archive, half-time and period scores, ESPN
  fill for openfootball's lag (746 unseen matches), Belgium undated rounds,
  replay check season no longer stopping 20 Sep, Czech First League scored from
  API-Football (18 Nov).
- **Machinery:** briefing chain (wait-dispatch), integrity check fixed for slim
  legs, Card review arriving in the morning, QA review of 15-16 Nov.
- **Site:** two-row nav, Mailer tab with Supabase sign-ups and push, GTM and
  GA4 on every page, new domain, About page, no links to the code.

## What it learned, including rejected tests
- **Card 1.60 price cap (`m7cap160`):** 60%+ picks at 1.60-1.90 landed 50% v
  64% (76 football legs, z -2.45), but a cap is behind live on both seasons
  (p(worse) 0.91). Rejected.
- **Edge over the price, fourth run:** no edge. **Football 50-55% band over
  quote:** rejected. **Opposition under 6:** read against the seasons, no rule.
- **Tennis surface, fourth check:** still no source; nothing changes before
  April 2027.
- **Weakest sport (18 Nov):** no other sport two standard errors under.
- **Price timing re-read, price-gap section under rule 13:** no lever; missing
  prices cost at most 2 legs on empty days, all lower leagues no UK book prices.
- **Book choice:** Hill unchanged; Bet365 +1.06% a pick paired (13 Nov), still
  Douglas's call.
- **Group bands v stated chance (18 Nov):** backtest write-up; see its note.

## Where accuracy stands (read only)
| Group | n | landed | quoted |
|---|---|---|---|
| Football, all graded reads | 8,617 | 67.8% | 66.5% |
| Football Daily List | 195 | 81.5% reads (81.0% won) | 82.0% |
| Football reserve | 598 | 65.9% | 68.2% |
| Card legs: tennis | 41 | 23 (56%) | 71% (z -2.13) |
| Card legs: NBA / football | 40 / 39 | 31 / 27 | z +0.87 / +0.21 |

Card by rule (groups won v expected, units returned on staked): rule 1 4/16
v 5.0 (12.2 on 16); rule 5 2/10 v 3.6 (8.2 on 17); rule 6 3/5 v 2.0 (13.3 on
10); rule 11 1/4 v 1.6 (6.4 on 8); rule 13 0 of 2 settled, 2 pending. Samples
are far too small to read; the first real read is 30 Nov or 50 settled groups.
The Daily 2x has 1 settled (lost), List cards none yet. The list is on quote
(football 0.5 under), the reserve 2.3 under, the known away under-quote.

Data quality: no name-match faults reported; fixed this fortnight were the
openfootball lag, Belgium's undated rounds, the replay season lag and slim-leg
crash. Open risks: API-Football and football-data as sole source for several
leagues; the Claude API allowance paused the context check until 1 Dec; the
tennis Card legs still sit 2.1 standard errors under quote (all pre-rule-10, so
the 85% floor has not yet been tested).

## Three tasks for next week
1. **Kofi (value): the 30 Nov Card review.** Fix the read before the data
   arrives: live (rule 13) v `rule12`, `m7value`, `rule6`, `nospan`, on the pool
   and both football-data seasons, p(worse) 0.30 on 100+ legs, and
   `cardRule13Split` for rule 12 v rule-13-only groups. Do not touch a rule
   before then; a reversal goes to Douglas with the numbers.
2. **Hannah (legs): the tennis 85% floor.** Count Card tennis legs admitted at
   the floor (`atFloor`, 0 so far); check each carries a real `priced` block and
   that Card groups are not emptied by it; read `tennis75` only at 30 legs.
3. **Susie (auditor): the new records' grading.** Check that the Daily 2x, List
   card, slip and Scale groups grade from the ledger without orphaned or
   duplicated legs (moved fixtures, rematches, span groups) and that
   `card-pick-twice` stays clean, before 50 settled slips are quoted anywhere.
