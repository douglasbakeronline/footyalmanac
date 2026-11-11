# The Card's record at the page's stakes (11 Nov 2026)

Scheduled build session, 11 Nov 2026 00:40 UTC.

## The gap

The Bets tab tells people to stake two units on a Card 2x and one on a 3x
(`CARD_STAKE`, since 29 Oct 2026), and the plan's Card rung says so. But every
return on the page, and in `groupings-record.json`, was one unit a group. The
2x has been the weaker kind live, so the flat figure flattered what a reader
who staked as told actually got.

## The numbers (archive to 10 Nov, full rule, graded locally)

| | groups | won | staked | back | return |
|---|---|---|---|---|---|
| one unit a group | 35 | 11 | 35 | 30.72 | -12.2% |
| the page's stakes | 35 | 11 | 49 units | 39.55 | **-19.3%** |
| the page's stakes, best price | | | 49 units | 40.06 | -18.2% |

Groups archived before 29 Oct carry no stake and count one unit, which is
what the page staked then. By kind (every Card group, wide and late included):
2x 9 of 29, -31.5% flat; 3x 7 of 16, +41.1%.

## What changed

- `groupings.grade()`: each graded group carries `stake` (as published, else 1);
  every tally adds `unitsStaked`, `unitsReturned`, `unitsReturnedBest`.
  `staked` / `returned` are unchanged, so every replay comparison still reads
  one unit a group.
- The Card scoreboard tiles add "at the page's stakes ... per N units"
  wherever the two differ. `planRungs` quotes both ("-12.2% at one unit a
  group, **-19.3%** at these stakes"), though the plan panel itself was
  removed the same night at Douglas's request (#228).

## Not changed

`CARD_STAKE`, `CARD_RULE`, any rule or replay. This is bookkeeping, not
evidence for a stake change: the replay (football only) has the 3x losing in
every season and the 2x positive, the opposite of the live split, and 35
groups is far under any gate. Whether the stakes should follow the live split
is a question for the 30 Nov review, on the pool, with `flatstake`
pre-registered (`claude/card-staking-2026-11-09.md`).
