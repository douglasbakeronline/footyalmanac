# Multipliers, the cup confidence bug, and what Saturday's slips taught (24 Oct 2026)

Douglas placed six bookmaker slips on Saturday 24 Oct (rugby, college
football, Nordic and Kazakh football, an English 3pm six-fold, a non-league
treble, a Bundesliga/Primeira/Serie A five-fold) and asked what the almanac
could learn. Then: fix it, and add a way of surfacing groups that multiply a
stake with some confidence ("Arsenal, Reading, Wolves today were good").

## What the day showed

26 settled legs by about 17:40: 17 won, 9 lost. Six of the nine losses were
draws. Strong-tier legs went 8 of 10, on their tested rate. Every slip but
one was beaten by a single leg. Nothing in one afternoon is evidence (rule 1),
so each lesson was tested on the archive.

## Tested on the archive (`tools/market_check.py`)

909 football picks with a bookmaker price archived before kick-off
(`predictions/` "market"), 11 Sep to 24 Oct, joined to `record-graded.json`.

| Test | Result |
|---|---|
| Log loss, model / market / 50-50 blend | 1.013 / 0.979 / 0.990. Blend better than the model by 0.023 (90% 0.017 to 0.029) |
| Picks, model 5-10 points above the market | landed 47% (model said 60%, market 53%) |
| Picks, model 10+ points above | landed 42% (model 59%, market 43%) |
| Picks, model at or below the market | landed 69-72% (model 59%, market 62-70%) |
| 50-70% picks by draw share | landed with their win chance in every draw band; no draw effect |
| Clean legs 1.30-1.90, market 45%+, model ≤ market + 5 (n=181) | landed 66.9% v 58.2% fair; +8.6 pts (90% +2.7 to +14.0); profit per unit +6.0% (90% -3.6 to +14.8) |

The office's replay found the same on 12,510 legs (`claude/odds-edge-test-2026-10-23.md`).

## What changed

1. **The cup confidence bug** (`engine.cup_temper`). The cup curve tempered
   home / draw / away but left `confidence` at the raw number, so 200 cup rows
   on 24 Oct ranked, tiered and banded on a figure up to 20 points above the
   win chance they showed (Berkhamsted 80% beside 61%; Bridlington 67% beside
   56%). Fixed going forward. The record's past cup rows still carry the old
   confidence: `score.py` grades the number that was published, and a regrade
   is Douglas's call (rule 1 is about fitting, but the published number is the
   site's honest claim). Cup rows are never on the Daily List or reserve, so
   neither record changes.
2. **Draws.** My first read (filter legs with a high draw chance) was wrong:
   at a fixed win chance the draw share does not change how often a pick
   lands. A draw is simply one of the ways a win bet loses. No filter.
3. **Model above the market.** Already a veto in every Odds tab group
   (`MAX_ABOVE_BOOK`, `WIDE_ABOVE_BOOK`). The Daily List takes no bookmaker
   input by Douglas's standing decision, so it is unchanged; the evidence
   above is the case for revisiting that, and it is his call.
4. **Groups that compound.** Already Double / Treble (and Fourfold at most);
   the card shows the combined chance. Saturday's nine-folds were placed by
   hand, not built here.
5. **Multipliers** (new, `groupings.py`).

## The Multipliers

For each target (3x, 5x) the 2-4 legs with the highest combined chance whose
combined price reaches it, from the football picks the safer groups left.

- A leg: football, clean (the same blindness exclusions as every group),
  bookmaker price 1.30-1.90 (`MULT_ODDS`, the range tested), the bookmakers'
  fair chance 45%+ (`MULT_FAIR_MIN`), the model 40%+ (`MULT_MODEL_MIN`) and no
  more than 5 points above the market (`MULT_ABOVE_BOOK`).
- Its chance is the **bookmakers' fair chance** (`as_mult`): at these prices
  it has been the better guide and has run conservative (landed 66.9% v 58.2%).
  The model is a veto only. The card says so.
- Chosen to maximise combined chance within the price range and floor
  (3x: 3.0-4.6, 25%; 5x: 5.0-7.6, 15%). Each extra leg adds the bookmaker's
  margin again, so for the same payout fewer, longer legs win; the chooser
  finds that by itself (`tests/test_groupings_multiplier.py`). 1/20 legs are
  out: they barely move the price and still carry the margin.
- The pool keeps the 24 legs that give up least chance per unit of price
  (-log fair / log odds), not the 24 likeliest: sorted by chance alone it held
  only the shortest legs, which cannot reach 3x in four (found on 24 Oct's
  board, 128 eligible legs and no group).
- Re-checked on every build like every other group (`recheck_mult`), archived
  and graded on their own line ("Multipliers won", `record["multiplier"]`).
  They do not count toward `MIN_GROUPS`.
- Mid-priced legs enter the pool marked `multOnly` and are priced from the
  bulk day prices only, so they cost no per-fixture API-Football or ESPN call.

On 24 Oct's 09:00 board the 3x was Dinamo Moscow and Krasnodar at 3.05 (30%),
the 5x Manchester City, Columbus Crew and Inter Miami at 5.05 (17%).

## On Arsenal, Reading and Wolves

They won, but two of the three would not have been chosen on the evidence:
Wolves was a 52% model read (no tier), and Reading's model number sat 6
points above the market, which is the pattern that has landed least. Arsenal
qualifies (1.43, the market 66%, the model 57%). A result is not a reason; the
rule is graded over weeks, not afternoons.

## Honest limits

- The +6% profit interval crosses zero. Nothing here claims an edge over the
  bookmaker; the Multipliers are the best-chance way to reach a target return,
  not a way to beat the market.
- 909 priced fixtures over six weeks, mostly the bigger leagues API-Football
  prices. Re-run `tools/market_check.py` as the archive grows.
- No other sport has been tested at these prices, so Multipliers are football
  only (`MULT_SPORTS`).

## Rule 2, the same evening (Douglas)

"At least 2-3 groups per day, at least 3 teams in each group with the
corresponding multiplier effect good. All picks must be likely to come in."
So: up to `MULT_PER_DAY` (3) Multipliers a day, one kind (`Multiplier`), each
three or four picks (`MULT_LEGS`), every pick at 60%+ by the bookmakers'
fair chance (`MULT_FAIR_MIN`, was 45%), paying 2.8x to 5.0x with a 20% floor.
Ranked first, second, third by combined chance. Old 3x / 5x groups are
rebuilt (`MULT_RULE` 2). Archive evidence at the 60% floor: 67 legs landed
76.1% against 64.8% fair. The honest limit stands: three 65% picks land
together about 28% of the time. Every pick being likely does not make the
group likely.

## 25 Oct 2026: beating the bookmakers, what is measured now

Douglas lost a six-fold at 17.02 on one late equaliser and asked for every
group at that price, then for the model to beat the bookmakers. Declined
the first (six ~60% picks land together about 4% of the time, returning
about 73p in the pound); built the measures for the second.

Profit per £1 on the 909 archived priced picks, average price then best:
every model pick -6.8p / -3.8p (both 90% intervals below or touching zero);
model 5+ points above the market -15.8p / -12.8p; clean 1.30-1.90 legs the
market rates 60%+ (n=72) +6.8p / +9.8p, 90% about -2p to +22p.

Built: best price and bookmaker on every leg, groups priced at best too;
the closing-line tally (each leg's published price against its last price
before kick-off, `update_closing`); the record at both prices. Read the
closing-line tile first: if picks shorten more often than they drift, the
edge is real before the profit can prove it.
