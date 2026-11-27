# The Daily 2x and List card ordered by confidence (27 Nov 2026, #569)

## The question

Douglas's Daily List review of 27 Nov: a pick lands at its confidence
whether it is on the list or the reserve (80-84%: list 84.4% of 154,
reserve 84.1% of 189), so the page now shows them together. The two slips
built from the list still put the list first: `groupings.daily_group` takes
list, then reserve, then football 65%+, then any sport 65%+;
`build_list_card` takes list picks only. Would ordering by confidence alone
do better?

## The variant (pre-registered in `tools/list_card_replay.py`)

`confidence`: the live functions on the same legs with every reserve pick
read as a list pick, so list and reserve are one tier ordered by the
model's number. Every floor, price rule, leg cap, target, the football and
any-sport tiers and the college exclusion are unchanged. Built as at 07:00
UK on each day (the hour both slips are held from), one unit a slip, won
only when every pick won, paired by day with a day bootstrap.

## The read (first recorded price; last pre-start price in brackets)

| Card | Source | Live | Confidence | v live a day | p(worse) | differs: days / legs |
|---|---|---|---|---|---|---|
| Daily 2x | ledger, 3 Oct to 27 Nov | 18/46 v 19.5 exp, -10.5% (22/46, +8.8%) | 19/46 v 19.6, -5.4% (23/46, +13.9%) | +0.05 (+0.05) | 0.00 (0.14) | 8 / 33 |
| Daily 2x | pool, 30 Oct to 27 Nov | 12/29 v 11.4, -1.5% | 12/29 v 11.4, -1.5% | 0.00 | n/a | 1 / 4 |
| List card | ledger | 5/12 v 5.5, -9.0% (8/12, +45%) | 16/38 v 15.6, -1.9% (19/39, +15%) | +0.01 | 0.48 (0.49) | 36 / 124 |
| List card | pool | 3/6 v 2.9, +5.5% (4/7, +24%) | 4/12 v 5.4, -25% (5/12, -5%) | -0.28 (-0.19) | 0.89 (0.81) | 7 / 22 |

- **The Daily 2x hardly moves.** On most days the list alone reaches 2x, so
  the reserve is only reached on the same days either way; the two differ
  on 8 ledger days (33 legs) and 1 pool day. Slightly ahead on the ledger,
  identical on the pool, far under the 100-leg gate.
- **The List card changes its nature.** Admitting the reserve builds a
  slip on three times as many days (38 v 12 on the ledger). Those slips
  land about as their model chance says (16 v 15.6), so the extra volume
  is roughly break-even at the price, and on the pool the extra slips lose
  (p(worse) 0.89). Live's few slips look better, on 12 slips.

## Decision

Gate not met on either card (100+ differing legs and p(worse) 0.30 or
under on both sources). Nothing changes live. The List card's review at 30
settled groups (`claude/list-card-2026-11-17.md`) stands; `confidence` is
re-run with `python3 tools/list_card_replay.py` and read beside it. If
Douglas wants the List card to fire on more days, the merged order is the
way to do it, at about the price's return, not above it.

The ledger's first and last prices give different returns for the same
slips (Daily 2x live -10.5% v +8.8%): many ledger "first" prices are early
quotes. Read the pairing, not the level.
