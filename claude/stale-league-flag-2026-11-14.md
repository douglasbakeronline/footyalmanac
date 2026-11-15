# A league table still missing results is flagged (14 Nov 2026)

## The gap

The lagging fill of 13 Nov (`claude/openfootball-lag-2026-11-13.md`) scores
openfootball's blank fixtures from ESPN. It mended fourteen leagues. The
Czech First League (`cze.1`) was the one it could not: ESPN's `cze.1` slug
returns nothing for 2026-27, so every build since prints
`lag cze.1: 0 result(s) filled`, and the table behind every Czech fixture
still stops at the start of October. On the 06:08 UTC build of 14 Nov the
league held 41 unplayed fixtures dated from 9 Oct, most of the build's 92
"unplayed fixture(s) dated before" warning.

Nothing on the page said so. Czech rows were priced and published as
ordinary rows: four to five a matchday since October, one at 86% on 8 Nov,
seven Czech legs in the Card's pool from 31 Oct to 8 Nov (none reached a
Card group). With the wider leagues admitted to the Card since 11 Nov
(`CARD_CORE_ONLY` False), a Czech favourite could reach a group on ratings
six weeks old.

## The change

`build.stale_leagues(fixtures, start)` runs after the lagging fill. A league
(not a cup, not an international) with `STALE_MIN` (5) or more unplayed
fixtures dated more than `STALE_GRACE` (3) days before the build's first day
has a table the model is blind to. Its fixtures, and a cup tie with a side
rated from it, carry a Celtic's Law reason (`stale_reason`): "the First
League (Czechia) table is missing 41 results from 9 Oct on, as its source has
stopped scoring them". Celtic's Law already does the rest: the row drops a
tier on the page, stays off the Daily List and the reserve, and is kept out
of the Card's pool, the Edge flag and every group (`groupings.legs`,
`edge_flag`). The build log warns with the leagues and counts.

Why five: a postponed match leaves one or two such rows a league (Rayo v
Athletic, Dundee United v Hearts, Braga v Gil Vicente on this build); a
source that has stopped leaves a round or more. Three days of grace keep a
weekend's results still on their way from tripping it.

Only openfootball leagues are flagged. API-Football and football-data
leagues that meet the same count are printed as `stale watch` and not
flagged, because their counts have not been read on a CI build yet (this
sandbox reaches neither source). A later session reads that line on the
first CI build and widens the flag if it shows real gaps rather than
postponements.

## What it does not do

It does not mend the Czech table. That needs a second source for Czech
results (API-Football carries the league; mixing its spellings into
openfootball's history needs the all-or-nothing name check the lagging fill
uses). The flag clears by itself the build a source fills the table.

No price is read, no constant in `engine.py` moved, no Card rule changed:
the probabilities on the row are unchanged, only the Celtic flag is added.

## Checked

Local build with the cached ESPN rows (`--days 9 --no-odds`): only `cze.1`
flagged (41 unplayed from 9 Oct); the 21 and 22 Nov Czech rows carry the
reason, the top one at 66%; every lagging league ESPN filled is clear.
`tests/test_lagging_results.py` `StaleLeagues` (count and grace, cups
skipped, API-Football watched not flagged, the reason's wording).
