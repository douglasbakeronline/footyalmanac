# The Card's 1.30-1.60 legs (19 Nov 2026)

Build session, Kofi (Value Analyst). Planner flag: Card legs priced 1.30-1.60
since 29 Oct landed 30 of 50 (60%) v 33.8 expected, z -1.2.

## Read (results ledger, settled, 60%+ picks, first real price, all sports)

| band | from | legs | landed | model | z | flat return |
|---|---|---|---|---|---|---|
| 1.15-1.30 | 29 Oct | 268 | 207 | 199.7 | +1.04 | -5.8% |
| 1.30-1.60 | 29 Oct | 400 | 266 | 273.2 | -0.78 | -5.4% |
| 1.30-1.60 football | 29 Oct | 203 | 139 | 135.1 | +0.58 | -2.3% |
| 1.30-1.60 tennis | 29 Oct | 34 | 22 | 22.4 | -0.14 | -10% |
| 1.30-1.60 nba | 29 Oct | 32 | 21 | 22.0 | -0.38 | -7% |
| 1.60-1.90 | 29 Oct | 133 | 69 | 87.3 | -3.36 | -11.5% |
| 1.30-1.60 | 3 Oct | 514 | 343 | 349.9 | -0.66 | -5.2% |

On every pick the model rated 60%+, the 1.30-1.60 band lands on quote (z -0.8
on 400 legs; football above it). The Card's own 50 legs (z -1.2) are a small
sample of the same band, not a leak. The band's return is about that of the
short band, so nothing singles it out.

## Why no variant

Removing the middle band leaves 1.15-1.30 and 1.60-1.90. The long band is the
one that does land under its chance (z -3.4), and `m7cap160` (cap at 1.60,
claude/card-m7cap160-2026-11-18.md) and `m7short` (1.50) already replayed
behind live on both football-data seasons; `short` (1.15-1.35) is a standing
variant. A hole at 1.30-1.60 would force the Card toward the long band, the
opposite of what the evidence supports, and a three-leg 2x needs legs near
1.26, so the Card needs the middle band to form groups at all.

Tested and rejected on the ledger; not run as a group replay because the
ledger read fails the precondition (no shortfall). Nothing changed:
`CARD_ODDS`, `CARD_RULE` 13, the record, the page. Revisit only if the band's
ledger z reaches -2 on 150+ football legs.

Written under rule 13; rule 14 (19 Nov 2026) keeps `CARD_ODDS` as it was, so the read stands.
