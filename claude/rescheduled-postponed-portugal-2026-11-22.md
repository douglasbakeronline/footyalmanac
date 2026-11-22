# Postponed Primeira Liga games back on the board (22 Nov 2026, evening)

## What was wrong

The 16:05 UTC build of 22 Nov still warned of 30 unplayed fixtures dated
before the build day that are not on the board. #480 covered the six
`AF_UNTIMED` / `AF_RETIME` leagues; its note left out the rest. Two of the
remaining rows are Primeira Liga games, a core league the Card and the Daily
List read:

- Sporting Clube de Braga v Gil Vicente FC, 16 Aug (openfootball marks it
  `[postponed]` and keeps it under round 2's date);
- GD Estoril Praia v CS Marítimo, 8 Nov (listed with a time, no score).

When either is replayed it never reaches the board, the list, the Card or
the archive, and is never priced or graded.

## The change

`sources.AF_RESCHEDULE = {"pt.1": 94}`: a league read from API-Football only
to reschedule. `build.fill_untimed(postponed_only=True)` runs #480's last
step alone: an unplayed row older than the 3-day look-back whose ordered pair
API-Football lists exactly once, in the window, takes API-Football's date and
time (`rescheduledFrom` keeps the old date). Every row inside the look-back
keeps openfootball's own date and time, which are real for Portugal (unlike
the nominal Premier League times that put en.1 under `AF_RETIME`). The same
guards hold: listed twice, listed before the window, relisted by the source,
or any club unmatched (all or nothing, rule 6) moves nothing. The build skips
the league when it has no unplayed row before the build day, and logs
"rescheduled pt.1: N postponed fixture(s)".

Why Portugal alone: 18 clubs, a double round robin, no split, so each
ordered pair plays once a season and one listing in the window can only be
the postponed game. Scotland (Dundee United v Hearts, 31 Oct), Greece
(Atromitos v AEK, 17 Oct) and Czechia (Slovan Liberec v Baník Ostrava,
24 Oct) repeat pairs after their split, so the rule does not hold there. A
guard for them would need the split's round in hand; not built.

## Evidence and checks

- openfootball's 2026-27 `pt1.txt` read on 22 Nov: 18 clubs; every one
  matches under API-Football's usual short forms (SC Braga, Sporting CP,
  Benfica, Guimaraes, Estoril, Maritimo, Famalicao, Academico Viseu ...)
  through `S.match_team`. The sandbox has no API-Football key, so the
  spellings are unprobed: the first CI build either logs "rescheduled pt.1"
  or names the unmatched club ("API-Football kick-offs not used").
- `tests/test_untimed.py` `RescheduleOnly`: the postponed rows move; rows
  in the look-back are untouched (timed and untimed); the two-listing and
  relisted guards; the spellings above map with none left over.
- Braga v Gil Vicente and Estoril v Marítimo leave the "unplayed fixture(s)"
  warning once API-Football lists their new dates inside the build window;
  until then nothing changes.
