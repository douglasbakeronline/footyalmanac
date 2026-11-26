# Four API-Football spellings (26 Nov 2026)

The 00:14 UTC build of 26 Nov named four football legs on 29 Nov under
`noFixture`, each beside its own fixture in API-Football's day list:

| board (openfootball / ESPN) | API-Football | league |
|---|---|---|
| WSG Tirol | WSG Wattens | Austrian Bundesliga |
| Stade Rennais FC 1901 | Rennes | Ligue 1 |
| LAFC | Los Angeles FC | MLS |
| Dinamo Moscow | Dynamo | Russian Premier League |

Every pool row of these four clubs since 30 Oct 2026 was archived as an
estimate (LASK v WSG Tirol 31 Oct, Dinamo Moscow v Akhmat 31 Oct, LAFC v
Minnesota 2 Nov, Fakel v Dinamo Moscow 7 Nov and the four on 29 Nov), so the
miss is systematic, not a one-off.

**Why the one-fixture fallback missed them.** `groupings.af_same` takes
`same()` (normalised equality, containment or ratio 0.8), then
`AF_SPELLINGS`, then `odds.ALIASES`, then `sources._norm` equality. None of
the four pairs passes any of those. In the bulk match (`odds.name_sim`, 0.5
each side) three of the four already pass (Rennes 1.0, WSG 0.50, Dynamo
0.53); LAFC scores 0.27, so it is missed by both paths.

**What changed.** The four board names join `AF_SPELLINGS`. A match still
needs both names and the kick-off within 90 minutes.

**What was tried and left out.** `"LAFC": "Los Angeles FC"` in
`odds.ALIASES` would fix the bulk match too, but it makes `name_sim("LAFC",
"Los Angeles Galaxy")` 1.0 (token prefixes "los", "angeles"), a collision
risk across the whole bulk match. Left out: a wrong match is worse than a
missed one. `af_same` also reads the alternative through `same()`'s
containment test ("los angeles" is inside "los angeles galaxy", "dynamo"
inside "dynamo kyiv"); with both names and the kick-off required, a wrong
fixture would need the same opponent at the same time, as with the existing
"West Ham United" entry.

**For the Card.** None of the four legs on 29 Nov is Card-reachable (model
45-49%); Ligue 1 and the Austrian Bundesliga are core leagues, so a future
Rennes or WSG pick at 60%+ would now be priced days ahead rather than only
once the bulk sweep reaches its date (and never, for LAFC).

Test: `tests/test_football_unpriced.py` `test_af_spellings_26_nov` (failed
0 of 4 matched before the change).
