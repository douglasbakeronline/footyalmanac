# The 30 Nov Card review: the agenda (27 Nov 2026)

Build session, 27 Nov 03:17 London slot. Three days before the 30 Nov review.
Forty-one notes in `claude/` name "the 30 Nov review"; none lists what it has
to decide. This note gathers every item, its pre-registered trigger as the
note behind it wrote it, who acts, and where the number comes from, so the
session that runs it reads one page. Standings are the 27 Nov Card review
(issue #557, the replay to 26 Nov); the 30 Nov issue replaces them.

No rule changed. `CARD_RULE` stays 14 until the read.

## 1. The rule: rule 14 v rule 13 and rule 12 (Douglas's)

- Trigger: 30 Nov, `rule13` and `rule12` paired against live on the same days,
  at the first and the last pre-start price
  (`card-rule14-rule8-2026-11-19.md`, `card-replay-price-fidelity-2026-11-24.md`).
- Read: a variant ahead at one price and behind at the other is not ahead. Weigh
  the last-price replay where the page's own read logged the picks never clear
  together (`card-short-log-2026-11-25.md`). Rules 11 to 14 are a fair replay of
  their own days; rules 1 to 6 are not (`card-review-coverage-by-rule-2026-11-24.md`).
  Beside it, `cardRule13Split`: picks only rule 13 admits, landed v the model
  (`card-rule13-split-2026-11-17.md`).
- 27 Nov: live record 1 of 3 v 1.23 expected; first price `rule13` -0.09 a day
  (p(worse) 0.57, 135 legs), `rule12` -0.29 (0.67, 81); last price `rule13`
  -0.59 (0.84), `rule12` -0.20 (0.62). Rule 13's split: 4 groups, 1 won v 1.39,
  rule-13-only picks 4 of 7 v 4.62. Nothing says switch.
- Acts: Douglas. A reversal goes to him with the numbers; rolling back to rule
  13 is the `rule13` constants and `CARD_RULE` 15.

## 2. Gates the session acts on without asking

| item | trigger | 27 Nov | note |
|---|---|---|---|
| Tennis off the Card | 50+ legs at the floor, z -2 | 15 legs, z -0.57 | `card-tripwire-at-floor-2026-11-14.md` |
| Context veto off | 30 settled "against" picks at or above the model | 0 settled (paused to 1 Dec) | `context-check-2026-11-11.md` |
| Daily 2x rule | 50 settled slips, z -2 | 10 slips, z -0.6 | `daily-2x-2026-11-17.md` |
| List 2x / List long | 30 settled each | 2 and 3 | `list-card-2026-11-17.md` |
| `m7opp5` / `m7opp9` | both football-data seasons and the pool, 100+ legs, p(worse) <= 0.30 | 33 and 9 pool legs | `card-m7opp-2026-11-15.md` |
| `modelcard` | pool 100+ legs at p(worse) <= 0.30 and `cardModel` not worse on both seasons | pool 48 legs, p(worse) 0.85 | `card-modelcard-2026-11-10.md` |
| Fillers (`fillwide`, `fillrule5`) | filler's own legs 100+ | 30 and 18 | `card-fillers-2026-11-10.md` |
| Hold band for published groups (added 28 Nov) | 10 settled withdrawn groups at or above the model | 1 settled, 1 won v 0.48 | `card-hold-band-row-2026-11-28.md` |

None is due at 30 Nov on today's numbers. The rule-change items (`m7opp5`,
`modelcard`) name Douglas while the rule 14 read stands ("no Card rule change
before the 30 Nov read").

## 3. Re-reads the notes asked for at 30 Nov

- `python3 tools/card_replay.py --since 2026-11-10` (no `--recover`): with
  `card-leg-unreplayable` silent, its live row is the real Card's legs
  (`card-pool-coverage-2026-11-09.md`).
- `flatstake` on the pool from 10 Nov, judged on return a unit, for
  `CARD_STAKE` (`card-staking-2026-11-09.md`, `card-record-at-stakes-2026-11-11.md`).
  Moot while the Card builds the 2x alone: every group is staked two units.
- Price timing: the lead table and books by sport; a push-time proposal needs
  30+ legs a bucket outside football (`price-lead-time-2026-11-09.md`). 27 Nov:
  NBA 106 legs drift +2.79% (late), football +0.39%; Bet365 v William Hill
  +0.52% a pick, p 0.004 (`CARD_BOOK` is Douglas's).
- `python3 tools/market_gap.py`: if Bookies-marked picks stop landing under the
  model, the mark goes (`bookies-mark-2026-11-20.md`).
- Re-cut tested rate and Celtic's Law on the pool's real-priced legs
  (`leg-property-third-2026-11-09.md`).
- `uncapped`, `opp7` and the rest of the rule 6 family: read only as rule 6
  variants (`card-replay-rule6-family-2026-11-11.md`); under rule 14 they are
  not candidates for the live rule.

## 4. Settled before the review

`tennis75` and `m7core` equal live under rule 14 and their rows are retired
(`card-decisions-rule14-2026-11-22.md`). The two-day groups (`span2`) and the
filler stay off by the owner's calls; they are read beside `rule13`, not gated
(`card-empty-days-fillers-again-2026-11-20.md`).

## How much the read can say

Rule 14 has 3 live groups and about a dozen on the pool replay. At 0.35 groups
a day it reaches 30 around the new year. The 30 Nov read can reject a rule
that is clearly behind; it cannot prove one ahead. Every rule change resets
that clock (`card-rules-timeline-2026-11-19.md`).
