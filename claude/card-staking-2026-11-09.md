# The Card's bankroll, and the stake split (9 Nov 2026)

Scheduled build session, 9 Nov 2026 midday. HQ backlog task `hq-card-stake`
("the unit size for a stated bankroll that keeps a 95%-worst season's
drawdown to half, from the replay, never from the live record").

## What was wrong with `tools/staking.py`

- `unitsForSeason` was `0.5 / p95 drawdown x 100`. That inverts the scaling:
  at 1% stakes a 17% worst drawdown gave "289 units", where the bankroll that
  loses half at that drawdown is about 35. The nightly review issue printed
  the wrong number.
- A "season" was the sample's own length (42 live groups, about two weeks).
- The live sample counted late groups, which the record's Card line leaves out.
- The replay side read `groupList` from `card-legs-history.json`, which the
  file on `main` (2 Nov, before the 6-9 Nov crash) does not have, so the
  replay row says "too few groups" until `tune.yml` next runs (Monday 04:40
  UTC; GitHub's scheduler was running about eight hours late on 9 Nov).

## What shipped

- `bankroll(gs, k)`: k groups drawn at the page's fixed stakes (`CARD_STAKE`,
  two units on a 2x, one on a 3x), the 95%-worst peak-to-trough drawdown in
  units, the median profit and the units staked; the bankroll is twice the
  drawdown. Reported for a month and a season at each source's own rate: the
  replay's groups a season (football, August to May), the live Card's groups
  a day over 365 days. `unitsForSeason` now means that season figure.
- The Kelly lines read 0 when the sample lands at or under quote: no group's
  chance beats its price, so Kelly stakes nothing. Documented, not a bug.
- The review issue prints the month and season lines.
- `tools/card_replay.py` pre-registers `flatstake` (one unit on every group)
  for the 30 Nov review.

## The live read (record at 9 Nov, read only, not evidence for a rule)

35 settled full-rule groups, 26 Oct to 8 Nov, 2.5 a day:

| kind | stake | groups | won | expected | return a unit |
|---|---|---|---|---|---|
| Card 2x | 2 | 22 | 5 | 8.3 | -49% |
| Card 3x | 1 | 13 | 6 | 3.4 | +56% |

At the page's stakes the Card returned -25% on turnover; at one unit a group
-10%. A month at this rate (75 groups, 122 units staked): 95%-worst drawdown
61 units, so a 123-unit bankroll; median -31 units. A season: 960 units.

The football-data seasons say the opposite about the split: the Card 2x is
positive in every season and the Card 3x negative in every season
(`claude/card-seasons-2026-11-09.md`). The live 2x / 3x gap is 35 groups on
a Card whose legs are mostly tennis and NBA, which the football replay does
not cover. So `CARD_STAKE` is not changed: Rule 1 forbids choosing it from
the record, and the two samples disagree. `flatstake` on the pool (from
10 Nov, with `priced`) is the test at the 30 Nov review, judged on return a
unit, not units a day (flat stakes turn over less, which flatters the units
pairing either way).

## Not changed

`CARD_STAKE`, `CARD_KINDS`, `CARD_RULE`, any record file, the Bets page. The
page line HQ asked for (a unit size for a stated bankroll) waits for the
replay side: with the replay empty, the only number available is the live
one, and the brief says never from the live record.
