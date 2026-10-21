# Odds tab group rules: backtest (5 Oct 2026)

Task: replay the group rules (65% tested rate over 30 games, spread rules, three bands) on past days and compare each band's win rate with its stated chance.

## What can be replayed

The Odds tab launched 4 Oct 2026. `groupings-record.json` holds 7 groups, 5 settled: 1 won, 4 lost, expected 1.49 wins. Steady 1 of 2 (expected 0.70), Balanced 0 of 2 (0.52), Stretch 0 of 1 (0.26). Legs: 13 of 18 won. Too few to say anything.

History cannot rebuild the groups faithfully. `predictions/` stores the model's confidence but not the tested rate the board showed that day (the rule's 65% / 30 bar), and no bookmaker price is archived anywhere. A faithful replay needs both, so it has to wait for the live archive to grow, or for the tested rate to be archived with each prediction.

## Approximate replay

`python3 tools/groupings_backtest.py` runs `groupings._best` unchanged on the 14 graded football days in `record.json`. A leg is a non-draw, non-Celtic pick with calibrated confidence of 65%+, its chance is that confidence, its price is the fair price (1 / confidence), the estimate cap is lifted.

Result: 3 groups, all Steady and all first choice, 3 won, stated chance 35% on average. No Balanced or Stretch group could be built: priced fairly, 65%+ picks are 1.0 to 1.5 and five of them rarely multiply past 4 while meeting the "one leg 1.60+" spread rule. In the live tab those bands exist only because real bookmaker prices run longer than fair ones, or because mixed sports add longer legs.

## Verdict

No rule change. Three groups is noise (3 wins at 35% stated is p about 0.04 by itself but on 3 correlated-by-day samples, not evidence of under-stated chances), and the live record points the other way. Rules 2 and 3 apply: no change without a paired, gated comparison.

Next steps if Douglas wants this answered: (1) archive each leg's tested rate and price in `predictions/` or keep `groupings-archive/` going until about 100 settled groups; (2) re-run `groupings.grade()` and compare stated against actual per band, with a bootstrap. Prices never feed a model.

## Live archive rerun (12 Oct 2026)

The 5 Oct note said to wait for about 100 settled groups. The archive now holds 31 groups, 30 settled (`groupings-record.json`, 4 to 12 Oct). Still no archived tested rate or bookmaker price in `predictions/`, so a historical replay of the 65% / 30 bar remains impossible. This is the live comparison of stated chance against outcome.

| Band | Settled | Won | Stated (expected wins) | Returned per 1 staked |
|---|---|---|---|---|
| Steady | 13 | 3 | 4.97 | 8.17 |
| Balanced | 8 | 5 | 2.50 | 20.87 |
| Stretch | 9 | 1 | 2.04 | 7.11 |
| All | 30 | 9 | 9.51 | 36.15 |

Overall 9 won against 9.51 expected. Bootstrap over groups (5000 resamples) of won minus expected: -0.51, 90% interval -4.5 to +3.5. Consistent with the stated chances. The band differences (Steady under, Balanced over) are inside noise at these counts.

Legs, settled: 106 of 140 won against 110.4 expected. By sport: football 61 of 81 (62.6 expected), tennis 18 of 26 (21.1), NFL 9 of 12 (8.7), college football 12 of 14 (11.9), rugby 6 of 7 (6.1). Estimated-price legs 37 of 49 (40.3 expected), priced legs 69 of 91 (70.2). The only visible gap is tennis, about 3 legs short, which matches the known tennis shortfall (`claude/tennis-hit-rate-2026-10-12.md`) and is the same legs' tested rate, not a group rule.

Lost groups: 10 lost on one leg, 9 on two, 2 on three. A single-leg-loss group is where a looser or tighter spread rule could matter, but 10 cases cannot separate any rule from luck.

## Verdict

No rule change. No candidate rule beats the current one on a paired, gated comparison, and the data cannot support one: 30 groups, correlated by day, with no historical prices. Rules 2 and 3 apply. Revisit at about 100 settled groups, or once each leg's tested rate and price are archived at publish time. Prices never feed a model.

## The 13-18 Oct collapse and what changed (19 Oct 2026)

To 12 Oct the groups were on their stated chances (9 won, 9.51 expected). From 13 to 18 Oct they won 0 of 25 against about 8 expected, far outside noise. The legs show why (unique settled legs, 12-18 Oct):

| Sport | Legs | Landed | Quoted | Bookmakers implied |
|---|---|---|---|---|
| Football | 78 | 73.1% | 77.2% | 74.2% |
| Tennis | 34 | 61.8% | 85.4% | 79.8% |
| College football | 13 | 53.8% | 85.7% | 77.1% |
| NFL | 5 | 40.0% | 75.7% | 73.3% |

Over the whole archive (5-18 Oct, 234 legs) legs landed 73.1% against 79.8% quoted; the shortfall sat in legs quoted 80%+ (landed about 75%) and in those three sports. Football's 70-80% legs were on their quotes.

Tennis was re-tested on every main-draw match since 1 Sep with both players on 10+ matches (1,096, walk-forward from `history-tennis/`): 75%+ calls landed about 85%, live prices match the replay to 0.002, and refitting the confidence shrink on Jun-Aug fails the tennis gates on Sep-Oct (ATP worse, WTA -0.0008 against a 0.005 bar). So the tennis model is sound and the fortnight was a bad run; it stays out on caution, as it is off the Daily List (15 Oct).

What changed in `groupings.py`:

- **Legs from football and rugby only** (`GROUP_SPORTS`). Tennis, college football and NFL return when their live legs hold their tested rates.
- **A leg's chance is min(tested rate, model's number)**. It used to be the tested rate pulled toward the model's number, which is the side that runs high at the top end.
- **Banker**: three legs paying 1.5 to 2.5, built first each day. A group's price all but sets its chance: five legs paying 2.5+ is a 25-40% shot even when every leg is honest, so a group meant to land most days has to pay less.
- **Legs settle from each sport's full graded history** (`record-graded.json`, `tennis-record.json` "graded", `sports.graded_games()`). Before, only the records' last 14 days were read, so older legs fell back to Pending on each regrade (5 Oct showed 0/5; it is now lost, 4 of 5).

Alongside: tennis grading voids a match its two priced players did not both play (`score_tennis.played_by_both`; ESPN reuses an id when a draw slot changes hands), which corrected 7 of 765 stored grades (5 losses, 2 wins, among them a Daily List pick, Jovic on 12 Oct); and college football is off the Daily List (`sports.LIST_OFF`), its Firm+ picks in the reserve.

No group can be made to always win. The stated chance on each card is the honest one; check the record against it, not against every group landing.

## Double and Treble: groups built to land (21 Oct 2026)

Douglas: groups that come in, nothing risky. Live record 4-21 Oct: 11 of 58
groups won (19%) against 18.7 expected; legs 205 of 283 (72.4%), which is the
bookmakers' fair chance, so the legs had no edge on the market and every leg
compounded its margin. Returned 40.50 from 58 staked.

Where the losses came from (football legs unless stated):

| Leg | n | Landed |
|---|---|---|
| Price under 1.15 | 47 | 85% |
| 1.15-1.30 | 94 | 77% |
| 1.30-1.45 | 63 | 70% |
| 1.45-1.60 | 31 | 61% |
| 1.80+ | 15 | 47% |
| Model 5+ points above the bookmaker's fair chance | 53 | 70% |
| Model at or below the bookmaker | 71 | 82% |
| On the Daily List / off it (all sports) | 111 / 172 | 78% / 69% |

The spread rule forced a 1.30-1.60 leg, and above Steady a 1.60+ leg, into
every group: the weakest legs by some way. Choosing for "best tested chance
for the odds" also picked the legs where the model disagreed with the market
most, which landed least.

What changed in `groupings.py`:

- Two kinds only: **Double** (two legs, combined chance 60%+, "Lowest risk")
  and **Treble** (three, 50%+, "Low risk"), built in that order, then a
  second of each from the legs left if it clears the same floor. No group
  when nothing clears: sitting a day out is the rule.
- A leg needs the tested rate, the model and the bookmaker's fair chance all
  at 75%+ (`LEG_MIN`; `MIN_HIT` raised from 65%), and the model no more than
  5 points above the market (`MAX_ABOVE_BOOK`). `safe_leg()`.
- Football legs exclude everything the Daily List keeps out for blindness:
  Celtic's Law, unrated, thin history, new competition, unreplayed cup, step 3,
  under-21 (`CLEAN_WHY`). Before, only unrated and draw picks were excluded,
  although the docstring said "one the board does not flag".
- No price-spread rule, no sport-mix bonus; a 2% nudge per Daily List leg.
- Banker, Steady, Balanced and Stretch are retired; the record keeps them
  under their names (`RETIRED`, `byBand`, `current`).

Evidence for the new gate: archived legs 4-21 Oct that would have passed it
landed 42 of 49 (85.7%) at an average 1.15. Replay on the full graded history
(`tools/groupings_backtest.py`, now on `record-graded.json`, fair prices,
model and flag gates only): 43 groups, 31 won (72%); Doubles 24 of 33, Trebles
7 of 10. Those are upper bounds on volume (the live rule also needs the
market to agree) and small samples.

Not changed: any model, the Daily List, pricing sources, grading, the archive.
Bookmaker prices still never feed a model; here they only veto legs.

The honest limit, as before: no group lands every time. At 86% legs a Double
lands about 3 in 4 and a Treble about 3 in 5. They pay roughly 1.2 to 1.7,
and at the market's own rate they still lose its margin over time.
