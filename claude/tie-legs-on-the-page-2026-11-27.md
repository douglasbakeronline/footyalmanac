# Tie legs marked on the page (27 Nov 2026)

Build session, 27 Nov 2026, 12:34 London slot.

## Why

The 12:15 UTC build's price log read "football Card unpriced: 1 ... Liga MX:
Cruz Azul v León (67%, 63h out)". That fixture is the Liguilla quarter-final
return leg: León 0-4 Cruz Azul was played on 27 Nov (03:10 UTC), and the model
gives Cruz Azul 67% at home on 30 Nov as if it were a league game. It cannot
see the aggregate. `tools/card_ties.py` (25 Nov) already finds these legs, but
only for the nightly review; nothing on the page said so, and Douglas bets
from the page.

The same leg is `moved` in the price log (board 30 Nov 03:00 UTC, API-Football
28 Nov), so it is never priced and cannot reach the Card. A web search did not
settle which date is right; the guard holds either way.

## What shipped

`build.tie_marks`: a football row is a tie leg when its league's fixture list
for the season (played and to come, the build's own `fixtures` plus the
season-so-far cache) holds the reverse fixture 1 to `TIE_DAYS` (8) days away,
the rule `card_ties.py` uses on the archive (a test keeps the two windows
equal). The row carries `tie`: `leg` 1 or 2, `other` (the reverse fixture's
date), and on a second leg whose first is played, `first` (the score as
played) and `lead` (the first meeting from the pick's side).

The page (`tieChip` in `index.html`, through `rowChips`, so every place a
football row is drawn) shows "1st leg" or "2nd leg", and on a played first
leg "won 1st 4-0" / "lost 1st 1-2" / "drew 1st 0-0". Worded as the first
meeting's result, not an aggregate lead: MLS's first round is best of three,
where "3-0 up" would be wrong. The hover says the model cannot see the
aggregate and to weigh it before using the pick in a group.

## The first read (the 27 Nov archive, 27 to 30 Nov)

14 tie legs, all second legs: Liga MX 4 (Cruz Azul v León, Atlas v Toluca,
América v Monterrey, Guadalajara v Pachuca), MLS 8, Série B 2. Only Cruz Azul
is above 60%.

## Not changed

No pick, list flag, grade, record or Card condition reads `tie`; it is not
archived. The `notie` Card variant stays pre-registered at 30 settled tie legs
clear of the live rule (`claude/card-ties-2026-11-25.md`). `CARD_RULE` stays 14.
