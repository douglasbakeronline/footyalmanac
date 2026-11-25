# Kick-off misses where the board is right (25 Nov 2026)

The price log's "football kickoff:" line names a leg whose two names sit on
API-Football's day with kick-offs 90+ minutes apart. On 20 Nov two such lines
(Sheffield United v Watford, Bologna v Udinese) were the board's error, so the
Championship and Serie A joined `sources.AF_RETIME`. A kick-off line is not by
itself a case for retiming a league.

## The read

Every deploy log from the last 25 builds (to the 16:05 UTC build of 25 Nov)
names two kick-off misses, both for Saturday 28 Nov:

| league | fixture | board | API-Football | builds | published listing |
|---|---|---|---|---|---|
| Serie B (it.2) | Palermo v Benevento | 18:30 UTC | 14:00 | 10 | 19:30 Italian time (18:30 UTC), DAZN and LaB Channel, Sport Flash's 28 Nov Serie B calendar |
| Super League (gr.1) | Iraklis 1908 v Panetolikos | 19:00 UTC | 15:00 | 4 | 20:00 Madrid / 13:00 Chicago (19:00 UTC), futboltotal.futbol (fed by API-Sports, updated 7 Nov) |

Both times are openfootball's, and the listings agree with them. API-Football's
are the wrong ones: a placeholder, or a time it has since changed. Putting
it.2 or gr.1 in `AF_RETIME` would have moved both games four and a half and
four hours early. The 90-minute guard did what it should have done: it left the
legs unpriced (`kickoff`) rather than price a fixture it could not confirm.

## Decision

Neither league joins `AF_RETIME`. A league joins only when a published listing
agrees with API-Football on a named miss (as the Championship's did on 20 Nov).
No code changed for this. Read the line again if either league is named on
another round.

## In the same change

The 16:05 UTC build's one `noFixture` leg, GV San José v Real Potosí
(Bolivia's División Profesional), sat beside API-Football's "Gualberto
Villarroel SJ v Real Potosí". It joins `groupings.AF_SPELLINGS`, with a test.
Bolivia is not a core league, so this prices the board row and the list, not
the Card under rule 14.
