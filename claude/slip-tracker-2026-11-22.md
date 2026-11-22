# The slip's tracker (22 Nov 2026)

Douglas: "I like the slip section in bets tab - but is there a visual tracker
for performance?" There was none: the slip showed its record as one line of
text. The Edge picks section has had a tracker since 21 Nov (`edgeTracker`),
so the slip now has the same, under its section (`slipTracker` in
`index.html`, state `SKT`).

## What it shows

- A running profit line, one unit on every settled slip, at the price the
  slip was archived at, beside a dashed **expected** line: each slip's tested
  chance times its price, less the stake. The gap between the two is the read:
  the line the slip's own numbers promised against what happened.
- Slips won against expected wins, profit and profit a slip, and how many
  are live v replayed.
- **All**, **Live only** and **Last 14 days**.
- A strip of slip days (replayed days dashed), tap one for its legs and prices.
- Days left of the Live mark are the rule walked forward over the results
  ledger (`slip.replay`), never published. A void slip counts as no stake.
- Under 30 settled slips it says plainly the record is too short to read; the
  slip's own gate is 100 (`slip.GATE_N`).

## Data

`slip.json` already carried the live slips (`record.recent`, last 30) and the
replayed ones (`replayDays`, last 20). Both now keep every settled slip
(`RECENT_KEEP`, `REPLAY_KEEP` 400), and each live slip carries its `chance`
so the expected line can be drawn. Nothing else in `slip.py` changed.

## The record at 22 Nov

Built from the committed ledger and `slip-archive/`: live 1 of 4 won against
1.5 expected, -0.34 units (-8.5% a slip); with the 11 replayed days, 2 of 15
against 5.2 expected, -8.02 units. The expected line rose +3.26 over the same
slips: the slip's tested chances have run well ahead of what landed. 15 slips
is too few to judge (one win is worth two to three units), but the replay's
1 of 11 is the thing to watch as the live count grows.

Checked in a browser at 1280 and 400 wide on the committed archive; no page
errors.
