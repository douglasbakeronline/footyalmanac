# Saturday games shown on Sunday, and several sports at once (22 Nov 2026)

## Saturday games listed on Sunday

Douglas, 22 Nov: "Some games listed on Sunday were actually Saturday games".

La Liga and the Süper Lig come from openfootball dated by round with no
kick-off. Until `build.fill_untimed` went live (19 Nov) the archive held them
under the round's Sunday with no time: Real Madrid v Celta, Sevilla v Betis,
Galatasaray v Samsunspor and the rest sat in `predictions/2026-11-16.json` to
`2026-11-19.json` dated 22 Nov. From 19 Nov the archive has them on their
real Saturday with a time.

`daylist.pinned` (behind the Daily List's day, Played today / yesterday on
every tab, and Scale's selection) keyed a football game on league, date and
both clubs. The old Sunday copy and the real Saturday copy were therefore two
games, and the Sunday copy, "kicking off" at midnight, showed among Sunday's
games. The rule it already had for US games ESPN moves (the newest copy's
day wins) never met it, because the key changed with the date.

Fix: a football copy is dropped from a day when a newer pre-start copy of the
same pair (same league, same clubs) dated within `ROUND_DAYS` (3) sits on
another day. A rematch weeks apart is untouched.

On the committed archives, Sunday 22 Nov lost 11 ghost rows (six La Liga,
five Süper Lig, all played on Friday or Saturday) and Saturday 21 Nov lost 10
(Sunday's Premier League games under their nominal Saturday, Brazil's round
under its nominal date). Nothing was added. Tests: `tests/test_daylist.py`
`RoundDateGhost` (four cases).

Not changed: grading. `score.py` already grades these from the right copy
(`nearby_results`, `earlier_copy`, 20 to 21 Nov). The results ledger still
holds the ghost copies as separate, ungraded rows dated 22 Nov (they sit in
its ungraded report, not on any page); `ledger.predictions` groups copies by
key, the same gap, left for a follow-up.

## Several sports at once

Douglas, the same day: "I want to be able to select multiple sports on the
filters at once". The Daily List's Sport filter and Starred's Sport filter
now take any set of sports: a tap toggles a sport in or out, Every sport
clears the set, and a sport with nothing this week drops out of it. Saved on
the device as before (the list as a comma list; a single sport or "all" saved
before still reads). The filter note names the sports chosen. The confidence
band filter stays one band at a time.

Checked in a browser at 1280 and 400 wide on the committed sports and tennis
files: two sports on, one toggled off, Every sport, on the Daily List and
Starred; no page errors.
