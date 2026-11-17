# The Card on the model alone: rule 13 (17 Nov 2026)

Douglas, 17 Nov 2026, 02:58: "I think we need to forget about comparison to
bookies... let's just follow the model", then, told what each of the Card's
two bookmaker conditions cost and offered the choice: "Yeah, just drop both
of those. I'm obviously still going to win if we are high confidence and the
opposition is priced 4 to 1. We need a daily card bet every single day, at
least 2x. Doesn't matter how many fixtures are on it. We just want confidence
and we want the betting groups to win as much as possible."

The owner's call, set live before any gate. This note records what changed,
what the record said at the moment of the change, and what to read on
30 Nov.

## What changed

Under rule 7 to 12 a Card pick had to be priced 1.15 to 1.90, rated 60%+ by
the model, and (the two bookmaker conditions) rated by the model **at or
above the bookmakers' chance** (`CARD_MODEL_EDGE` 0.0, rule 7) and, for
football since 16 Nov, have **the opposition priced 5.0+** (`CARD_MODEL_OPP_MIN`,
rule 12). Rule 13 drops both:

- `CARD_MODEL_EDGE = None`: `model_fault` no longer reads `fair`. The
  bookmakers' chance is still computed and shown; it decides nothing.
- `CARD_MODEL_OPP_MIN = {}`: the opposition's price is shown, never read.
- `CARD_RULE = 13`; the record tallies it apart (`cardByRule`).

What still holds: the price band (a bookmaker must price the pick 1.15 to
1.90, which is the one bookmaker number left in the rule, and it is there so
the slip pays 2x in three to five legs), the model's 60% floor, tennis at
85%+ on model and tested rate, NFL and the college sports off, the wider
leagues in (cups and internationals out), the Daily List's blind-spot
exclusions, two picks a competition, the context veto (paused until 1 Dec),
two-day groups, up to three 2x groups a day, no filler.

Replay variants: `rule12` (both conditions back, the Card as it ran on
16 Nov), `m7value` (the value demand alone, rule 11), `m7noopp` (now
identical to live), `m7opp5` (the opposition floor alone). All four are in
`tools/card_replay.py` (the pool, nightly) and `tools/card_legs_history.py`
(football-data, Mondays, `cardM7Paired`).

The funnel (`tools/card_funnel.py`): the `no-value` key and relief join only
while the value demand is live, as the opposition relief already did
(`MODEL_VALUE_RELIEF`). Under rule 13 neither appears.

The page: the Card's rule text and each group's footer read `modelEdge` from
`groupings.json` `rules.card` (new, with `modelOppMin`) and say "the model's
number alone" from 17 Nov.

## The every-day card

Rule 13 widens the Card; it does not make it daily. The part of Douglas's
instruction that says "a daily card bet every single day, at least 2x,
doesn't matter how many fixtures" is the **Daily 2x** shipped earlier on
17 Nov (`groupings.daily_group`, `claude/daily-2x-2026-11-17.md`): the
model's strongest picks at 1.10+, up to eight, until 2x, published short if
nothing reaches 2x. It already takes no bookmaker comparison. So from 17 Nov
the Bets tab has three model-only slips: the Daily 2x (always), the Card's
2x groups (most days under rule 13), and the List 2x / List long.

## What the record said at the switch

Everything below is the pool replay (`tools/card_replay.py`, every sport,
first real price, 30 Oct to 17 Nov, settled legs only) and the football-data
replay (football only). None of it is the scoreboard.

### Pool, every sport, at a flat stake

| Rule | Days with a group | Groups | Won | Expected | Return | Legs landed v quoted |
|---|---|---|---|---|---|---|
| **rule 13 (live)** | 21 | 41 | 17 (41%) | 15.8 (38%) | **-4%** (90% -30 to +23) | 90/123, 73.2% v 69.2% |
| rule 12 | 12 | 20 | 11 (55%) | 8.3 (41%) | +34% (90% +3 to +62) | 49/60, 81.7% v 68.5% |
| m7value (value demand only, rule 11) | 14 | 23 | 9 (39%) | 9.2 | -4% | 50/69, 72.5% v 67.7% |
| m7opp5 (opposition only) | 21 | 38 | 17 (45%) | 14.8 | +0% | 88/114, 77.2% v 70.2% |

Paired by day, rule 12 against rule 13: +0.79 units a day, 90% band -0.15
to +1.78, p(worse) 0.09. Rule 13 builds twice the groups and wins fewer of
them. Its legs still land above quote (73% v 69%), which is the model's
calibration showing through; the groups lose because the extra legs are the
ones priced shorter than the model's number, and those return less than
their chance.

### Football-data, football only (`card-legs-history.json`, 16 Nov run)

Rule 13 has no football-data line yet (the Monday run and
`card-legs-history.yml` on this pull request add `rule12` and `m7value`).
The nearest pre-registered variant is `m7under5` (the model allowed up to 5
points under the bookmakers): 2025-26 74 groups, 30 won (41%), -3.7%;
2026-27 11 groups, 4 won, -20%; pooled 85 groups 40% won, -5.8%, against the
value-demand Card's 47 groups 51% won, +24%. Over five seasons `m7under5`
was behind in all five, p(worse) 0.99 on 912 legs
(`claude/card-m7under5-seasons-2026-11-12.md`). Rule 13 goes further than
`m7under5` (any gap), so on football it should be expected to do no better.

## The estimate for a month of every-day cards

Douglas asked for one, knowing the review is on 30 Nov. On what is
collected (41 pool groups under the rule, 85 football-data groups under its
nearest proxy):

- **Card 2x groups under rule 13: about 40 to 45% won**, against the 50%
  a 2x needs to break even at a flat stake, so **about -5% to -10% on
  turnover** over a month, with a 90% band from about -30% to +20% on 40 to
  60 groups. Roughly 1.5 to 2 groups a day, 45 to 60 a month, 90 to 120
  units staked at two a group.
- **The Daily 2x (the one that is every day): about 50% won**, the ledger
  replay 14 of 28 (+22%) with the same width of error; a month is 30 slips,
  so the band is about 32% to 68% won.
- For comparison rule 12 on the same pool days: 55% won, +34%, on 20
  groups; its 90% band already reaches +3%, which is why it was set live.

The honest reading: a month of rule 13 most likely gives a card most days,
wins two groups in five, and loses a little money; a lucky month is +20%, an
unlucky one -30%. The model's picks land as it says they will; the price is
where the money goes.

## What to collect, to learn faster

1. **Time, mostly.** Every variant is read on the same days, so nothing
   needs changing to compare them; at two groups a day rule 13 reaches 100
   groups by mid-December, when the win rate is known to about ±8 points.
   The 30 Nov review will have about 60 groups (±13 points).
2. **A placed-bet log.** The record grades the page's groups at the
   bookmakers' average and William Hill's price. Nothing records what
   Douglas placed, at what price and stake, so the page's return and his
   cannot be reconciled. A `placed.json` keyed by group id (price, stake,
   book, time), written from a button on the group or by hand in a
   file, would settle "does the site's return match my account". It is a
   bet log, not model input, so rule 8 is not touched; it is manual, so it
   is Douglas's call.
3. **Every leg's price at every book from the first build it is priced.**
   `bookOdds` is kept for legs that could reach a card since 9 Nov. Under
   rule 13 more legs can, so the coverage check (`card-leg-unreplayable`)
   matters more: any Card leg not in the pool at a real price cannot be
   replayed under a future rule.
4. **The bookmakers' chance on every pool row.** Kept since 9 Nov
   (`priced`), and now the one number rule 13 does not use. Keep it: it is
   what lets `rule12` and `m7value` be rebuilt on rule 13's days, which is
   the only way the 30 Nov review can say which rule to keep.
5. **Tennis at 85%+ and NBA by band.** The pool has four tennis legs at
   85%+ and the NBA's Card legs sit in one band (1.15 to 1.40). A hundred of
   each would say whether the sports that give the Card its volume pay.
6. **Which legs rule 13 adds.** Every leg rule 12 would have refused now
   carries nothing to say so. Worth a `rule12Fault` field on each Card leg
   as archived (the string `model_fault` returns under the `rule12` patch),
   so the review can split rule 13's groups into "rule 12 would have built
   this" and "rule 13 alone", without replaying.

Item 6 is the one cheap addition that sharpens the 30 Nov read; items 2 and
5 need Douglas or time.

## Review (30 Nov, or at 50 settled rule 13 groups)

Read `rule12` paired against live on the pool and on football-data. Keep
rule 13 if its paired difference against rule 12 is within noise (p(worse)
over 0.30) or ahead; otherwise put the choice to Douglas with the numbers,
since the switch was his. The `cardByRule` tallies carry the live record of
each rule from its own day one. Roll back: `CARD_MODEL_EDGE = 0.0`,
`CARD_MODEL_OPP_MIN = {"football": 5.0}`, `CARD_RULE` 14.
