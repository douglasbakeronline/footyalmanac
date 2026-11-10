# The empty-day fillers, on the replay (10 Nov 2026)

Scheduled build session, issue #155. Since rule 6 (the opposition priced 9+,
6 Nov 2026) the full rule leaves some days empty and the page fills them with
the wider-rule group (1.08-2.10 at the bookmakers' 55%+, three to five picks,
no under-market or opposition condition; `groupings.build_card`'s last block,
graded apart as `cardWide`). The issue asked whether that filler pays, and
whether a different filler would pay better. Until today the replay could not
say: `tools/card_replay.py` built the full rule only, so the page's own
fallback had never been replayed. Nothing changed on the page or in the rule.

## What was added

Four variants, pre-registered for the 30 Nov review. Each is the live Card
exactly; only on a day the full rule builds nothing does it add groups under
the filler, marked `fill`:

| variant | filler on an empty day |
|---|---|
| fillwide | the page's wider-rule group, as `build_card` builds it (`card_replay.build_wide`) |
| fillopp7 | the Card with the opposition at 7+ |
| fillrule5 | the Card with no opposition condition (rule 5) |
| fillshort | the Card at 1.15-1.35 only |

Paired against live, a filler differs only on the empty days, so the pairing
is the filler's own return. The report carries the filler's own days, groups,
won, expected, units, return and legs (`variants.<v>.fill`), and the nightly
Card review prints them (`card_review_post.fill_lines`). The decision gate
counts the filler's own legs, not live's plus its own (`gate_legs`): a filler
with 20 legs of its own is not a 100-leg result because live had 300.

The football-data side (`tools/card_legs_history.py`) replays `fillwide`
(on legs taken through the wider price gate, `legs(wide=True)`, for that
Card only), `fillrule5` and `fillopp7` on every season, as `cardFillWide`,
`cardFillRule5` and `cardFillOpp7`. It needs football-data.co.uk, so its first
numbers come from `tune.yml` on Monday 16 Nov (or a hand run of the
`card-legs-history.yml` workflow once it lands).

## The read, the pool from 30 Oct to 9 Nov

11 Card days. Live (the full rule) built groups on 6 of them with `--recover`
and on none at first real prices only, because most of the live Card's legs
before 10 Nov were archived as estimates (`claude/card-pool-coverage-2026-11-09.md`);
from 10 Nov every leg carries its first real price and the two reads converge.

| read | filler | days | groups | won | expected | legs | return |
|---|---|---|---|---|---|---|---|
| first real price only | fillwide | 7 | 12 | 2 | 4.14 | 36 | -54% |
| first real price only | fillrule5 | 3 | 4 | 2 | 1.28 | 12 | +12% |
| `--recover` (last price before 10 Nov) | fillwide | 4 | 7 | 2 | 2.45 | 21 | -24% |
| `--recover` | fillrule5 | 1 | 1 | 1 | 0.41 | 3 | +104% |

`fillopp7` and `fillshort` built nothing on any empty day: when the full rule
is empty, the opposition at 7+ or the short price band do not bring a group
back. The relief that does is dropping the opposition condition, which the
funnel showed too (`claude/card-funnel-2026-11-10.md`).

Paired against live on the strict read: fillwide -1.47 units a day (90%
-2.86 to +0.01), p(worse) 0.95; fillrule5 +0.29 a day, p(worse) 0.30. On the
review's window from 29 Oct: fillwide 13 groups, 2 won v 4.46 expected,
-59%, p(worse) 0.98. The live record agrees in direction on a tiny sample:
`cardWide` 1 of 2 settled.

## What it means for the return

The page's filler has landed under its own quote on every read so far: its
picks are near the market (no under-market cut) and its opposition is
often short, the two conditions the five-season replay found carry the edge.
That is what the evidence would predict. But 36 legs is a third of the gate,
so per the delegated-decision rule (100+ legs, p(worse) at most 0.30, both
samples agreeing) nothing changes today.

The decision is pre-registered so it is not made on a lucky or unlucky week:

- **Drop the wider-rule filler** when `fillwide`'s own legs reach 100 on the
  pool and live beats it with p(worse) of keeping it at 0.70 or more (the
  gate the other way round), and the football-data `cardFillWide` agrees on
  both the fit and check seasons. An empty day then stays empty, which the
  page already says honestly.
- **Swap in `fillrule5`** only if it passes the gate on its own legs and the
  football-data seasons. It is the opposition condition relaxed for the empty
  days alone, and that condition is the one rule that holds in all five
  seasons, so it starts as the less likely of the two.

The nightly Card review shows the fillers' own line from tonight, so the
count can be watched rather than worked out by hand.

## Files

`tools/card_replay.py` (the fill variants, `build_wide`, the `fill` report),
`tools/card_legs_history.py` (`legs(wide=True)`, `cardFillWide`,
`cardFillRule5`, `cardFillOpp7`), `tools/card_review_post.py` (`fill_lines`,
`gate_legs`), `tests/test_card_fillers.py`, `tests/test_card_legs_history.py`.
