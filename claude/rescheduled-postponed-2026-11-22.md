# Rescheduled postponed games back on the board (22 Nov 2026)

## What was wrong

The 22 Nov 11:05 UTC build warned of 30 unplayed fixtures dated before the
build day that are not on the board. Some were yesterday's games still to be
scored, but others were months old: La Liga's Rayo Vallecano v Athletic Club
(10 Oct), Brazil's Chapecoense v Vasco da Gama (29 Jul). These are postponed
games. openfootball keeps the row under its first date, so when the game is
replayed it never reaches the board, the Daily List or the Card, and is never
priced or archived.

`build.fill_untimed` (the `AF_UNTIMED` and `AF_RETIME` leagues: La Liga, the
Süper Lig, Brazil's Serie A, the Premier League, the Championship, Serie A)
already moves a row to API-Football's date, but only for rows up to 3 days
before the window (#477), so a nominal Saturday's Sunday games stay on the
board. Older rows were left alone on purpose then (`test_older_rows_untouched`).

## The change

These six leagues play each ordered pair (home v away) once a season. So an
unplayed row older than the 3-day look-back whose pair API-Football lists
exactly once, in the window, is that game rescheduled: it takes API-Football's
date and time (`rescheduledFrom` keeps the old date on the row). Left alone:

- a pair API-Football lists before the window (played or postponed again);
- a pair listed twice in API-Football's window;
- a pair the source already holds as a second unplayed row (the relisted row
  is the one placed);
- any played row; any league whose names do not all match (rule 6, unchanged).

A played game openfootball has not scored cannot be moved by this: its pair is
not in API-Football's future window.

## Evidence and checks

`tests/test_untimed.py`: five cases replace `test_older_rows_untouched`
(rescheduled game moved; listed before the window; relisted by the source;
listed twice; played). The sandbox has no API-Football key, so the first CI
build is the live check: Rayo v Athletic and Chapecoense v Vasco should leave
the "unplayed fixture(s)" warning once API-Football lists their new dates in
the window, and the "untimed es.1" / "untimed br.1" counts rise by one each
then.

## Not covered

Leagues outside `AF_UNTIMED` / `AF_RETIME` (the Primeira Liga's Braga v Gil
Vicente, 16 Aug; Scotland's Dundee United v Hearts, 31 Oct; Greece's Atromitos
v AEK). They have no API-Football id on file, and Scotland and Greece play
pairs more than once a season, so the one-listing rule does not hold there.
A follow-up would need ids per league and a split-season guard.
