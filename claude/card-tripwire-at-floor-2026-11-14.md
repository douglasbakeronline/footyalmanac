# The tennis tripwire reads the legs today's floor admits (14 Nov 2026)

## The finding

The sport-off tripwire (9 Nov 2026, CLAUDE.md "The Card's return: decisions
delegated") takes a sport off the Card at 50+ settled legs two standard errors
or more under quote. It counted every tennis leg in `groupings-record.json`.
At 14 Nov those were 41 legs, 23 landed v 29.1 expected (56% v 71%, z -2.13),
and every one was priced under today's tennis floor of 85% (`CARD_SPORT_MIN`,
`CARD_RULE` 10, 11 Nov 2026):

| rule the group ran under | tennis legs | landed |
|---|---|---|
| 1 (no tennis floor) | 30 | 15 |
| 4 | 1 | 1 |
| 5 | 6 | 3 |
| 6 | 4 | 4 |
| 7 to 11 (85% floor) | 0 | 0 |

So nine more tennis legs would have fired it on legs the Card no longer takes:
had the next nine (at 85%+, quoted about 88%) landed as quoted, the 50 would
sit about two standard errors under and tennis would come off, an 85% rule
judged on a 60-75% population. The pool agrees the shortfall sits low: the
60-70% model calls land under quote, 70%+ on quote, 85%+ four legs, all won
(`claude/pool-order-of-play-2026-11-14.md`).

## The change

`groupings.card_legs_by_sport` keeps the every-leg tally as before (the page
and the review still show 23 / 41) and, for a sport with its own floor, adds
`floor`, `atFloor` (the legs whose chance reaches today's floor) and
`tripwireAll` (the old every-leg test). `tripwire` now reads `atFloor`. Sports
without a floor are unchanged. The leg's archived chance `p` stands in for
"today's floor would admit it": under rules 1 to 6 `p` was the lowest of the
tested rate, the model and the fair chance, so `p` at 85%+ means all three
were; a leg whose `p` sat under 85% with the model above it is left out, which
undercounts slightly and never admits a leg the floor would refuse.

The page's "Picks by sport" row for tennis reads "Under; judged at 85%+ (0 so
far)" in amber instead of "Watch: 9 more legs decide" in red, and the nightly
Card review adds one line per floored sport with the floor's own tally and
whether the every-leg test would fire.

## What this is not

Not a Card rule change: no `CARD_*` constant moved and `CARD_RULE` stays 11.
Tennis still needs 50 legs at the floor two standard errors under to come off;
`notennis` and `tennis75` keep replaying nightly. A tally of the scoreboard,
nothing fitted (Rule 1). If the floor moves again, the test follows it.

Roll back: `git revert` the merge commit.
