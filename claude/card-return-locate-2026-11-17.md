# The Card's 0.831 return: where the gap sits (17 Nov 2026)

Task from the HQ planner: 9 of 27 settled groups landed against 9.7 expected
(z -0.3), return 0.831 a unit. Slices below are from `groupings-record.json`
legs (full rule 5+, staked, not filler), used only to locate, never to fit.

- Landing is on quote (33% v 36%). The shortfall is the price, not the picks.
- By sport (legs, landed, mean quoted, flat return a leg): football 43, 33, 0.708,
  +0.074; NBA 33, 27, 0.712, +0.129; rugby 6, 4, 0.768, -0.16; tennis 14, 9,
  0.783, -0.19; college basketball 3, 1, 0.752, -0.50. The losers are tennis
  (under 85%, closed by rule 10 and the floor tripwire read at `atFloor`: 0 legs
  at the floor) and college basketball (off the Card). Football and NBA are positive.
- By price: under 1.30 +0.04 (34 legs), 1.30-1.50 -0.12 (39), 1.50+ +0.21 (26). Not monotone.
- By weekday: Wednesday -0.43 on 10 legs, Friday +0.39 on 9. Noise at this size.
- By rule: 5 (71 legs) -0.005, 6 (18) +0.17, 11 (10) -0.03.

Result: no class with 50+ legs loses that today's rule still admits, so there is
no variant to register and no replay to gate. A weekday, price-band or rugby
rule would be fitted to a handful of legs (Rule 1 spirit; the p(worse) 0.30 gate
cannot be met on under 50 legs). Rule 13's own read (`cardRule13Split`, the
`rule12` / `m7value` replays) at 30 Nov or 50 settled groups is the place to
act. Tested nothing new; this is a note, not a change.
