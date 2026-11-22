# Postponed games in the split leagues back on the board (22 Nov 2026, night)

## What was wrong

#483 moved postponed Primeira Liga games to their new date and left out
Scotland, Greece and Czechia: their seasons split, a pair the split repeats
plays again, so "API-Football lists the ordered pair once in the window" could
pick up the split's game. Two core-league games sat off the board, the Daily
List and the Card for good once replayed:

- Dundee United v Heart of Midlothian (Premiership, 31 Oct);
- Atromitos v AEK (Super League, 17 Oct).

## What the files hold

openfootball's 2026-27 files, read on 22 Nov and filled with the committed
ESPN results the way the build fills them (`fill_lagging`):

| league | rows | regular season | repeated ordered pairs | postponed left |
|---|---|---|---|---|
| sco.1 | 198 | 33 rounds, to 10 Apr 2027 | 66 | Dundee United v Hearts |
| gr.1 | 182 | 26 rounds, to 20 Mar 2027 | 0 | Atromitos v AEK |
| cze.1 | 240 | 30 rounds, to 24 Apr 2027 | 0 | (results from API-Football, `AF_LAG`) |

Each file holds the whole regular season and nothing after the split. So a
pair the regular season repeats (Scotland's 66) is already a second unplayed
row and refused by the existing guard, and a pair the split repeats can only
be listed after the file's last fixture.

## The change

- `sources.AF_RESCHEDULE` adds `sco.1` 179, `gr.1` 197, `cze.1` 345;
  `sources.AF_SPLIT` names the three.
- `build.fill_untimed(split=True)`: a postponed row never moves past the
  latest date in the league's own file. Every other guard is #480's and
  #483's (listed twice, listed before the window, relisted by the source,
  all or nothing on names).
- `sources.ALIASES`: "dundee utd" -> "dundee united". API-Football's short
  form reduced to "Dundee", so two API names met one club and the matcher
  would have refused the league whole.

If openfootball later adds the split fixtures, the repeated pair becomes a
second unplayed row and nothing moves (conservative: a postponed game whose
pair also plays after the split stays off until its row is scored).

## Checks

- `tests/test_untimed.py` `RescheduleSplit`: the postponed row moves inside
  the regular season; a listing after the file's last fixture is refused
  (and would move without `split`); a pair repeated in the file is refused;
  Scottish and Greek spellings map one to one.
- Spellings are unprobed (no API-Football key in the sandbox). The first CI
  build logs "rescheduled sco.1 / gr.1 / cze.1: N postponed fixture(s)" or
  names the unmatched club ("API-Football kick-offs not used"). Both games
  leave the unplayed warning once API-Football lists their new date inside
  the build window; until then nothing changes.

No model constant or Card rule changed.
