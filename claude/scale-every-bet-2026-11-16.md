# Every scale bet, every sport, tracked (16 Nov 2026)

## What Douglas asked for

After a list of every way to scale a winner in each sport: "can we track all
of these across all sports please? I'm not sure how to though."

## How

`scale_ladder.py` (standard library, reads the three graded files, writes
nothing itself). For every graded pick at 55%+ in every sport it checks each
scale bet the final score can settle and tallies how often it landed: on the
whole record, by confidence band (55-65, 65-75, 75-85, 85+), by tier (Daily
List, reserve, everything else) and over the last 28 days, with the price
each rate needs to break even. `scale.py` adds it to scale.json as `ladder`;
the Scale tab shows it as **Every scale bet**, a table per sport (`scLadder`).
It updates on every build as results are graded. A tally, never a fit: no
model, pick or group reads it.

| Sport | Bets tracked |
|---|---|
| Football | win or draw, win, win and over 1.5 / 2.5 / 3.5, win to nil, win by 2+ / 3+, pick scores 2+ / 3+, win and both score |
| Tennis | win, first set and match, straight sets, win by 4+ / 6+ / 8+ games |
| NBA, college basketball | win, by 4+ / 6+ / 8+ / 10+ / 13+ / 16+ |
| NFL | win, by 3+ / 4+ / 7+ / 8+ / 10+ / 14+ |
| College football | win, by 3+ / 7+ / 10+ / 14+ / 17+ / 21+ |
| Rugby | win, by 4+ / 8+ / 11+ / 13+ / 16+ / 21+ |
| Baseball | win, by 2+ / 3+ |

Not tracked, as the files hold final scores only: half-time and quarter bets,
team totals against a bookmaker's line, corners, cards, scorers and player
bets (listed under each table).

## First read (whole record)

- Football at 85%+ (85 picks): win by 2+ 82%, pick scores 2+ 92%, win and
  over 2.5 74%, win to nil 61%. Win and both score 31%, flat at every band.
  Daily List picks (188): win and over 2.5 61%, win by 2+ 59%.
- Tennis at 85%+ (80): win by 4+ games 84% against straight sets 78%; by 6+
  games 75%.
- College basketball at 85%+ (214): by 10+ 84%, by 13+ 78%, by 16+ 71%.
- NBA, NFL and rugby at 85%+ are 1 to 10 picks: read their Daily List and
  75-85% columns instead.

## Not changed

The Scale tab's own bets, picks and groups; any model; the record.
