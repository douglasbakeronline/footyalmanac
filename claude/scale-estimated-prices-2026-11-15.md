# Scale: estimated prices where the feed has none (15 Nov 2026)

## What Douglas asked for

15 Nov 2026: "If you're missing data on prices, just give an estimate,
please." Four of the five Scale bets (tennis straight sets, the NBA by 10+,
the NFL by 7+, rugby by 8+) have no price feed, and many football picks have
no William Hill price either, so most rows and every mixed group showed only
"needs" and the line to look for.

## What was built (`scale.py`)

- `EST_MARGIN`: the bookmaker's margin assumed per sport. Football's
  result-and-goals bets 15% (William Hill kept about 16% a leg on win and both
  score over 69 priced fixtures, `claude/scale-strong-legs-2026-11-15.md`);
  alternative handicaps and set betting 8% a selection.
- `est_price(sport, chance)` = 1 / (chance x (1 + margin)), floor 1.01.
  `price_or_est(p)` gives the real price when there is one, else the estimate.
- A group with no real price for every leg carries `est`, the product of each
  leg's price or estimate. A graded group carries `estRet` (0 when lost, the
  estimated payout when won) beside the real `ret`, never in place of it.
- Tallies by sport, tier and group kind gain `estN` / `estRet`, kept apart
  from `priced` / `ret`. Archived picks need no rewrite: the estimate is worked
  from each pick's archived chance at grading time, so the replay days have
  one too.

## The page

An estimated price shows as "≈ 2.13" in italic with a dotted rule and the
word "estimate", the line to look for at William Hill and "needs" under it.
Groups read "Pays about 4.83". The scoreboard and group lists show "≈ +8.1%
est." where no real price exists. A real price is unchanged and always wins.

## What to be straight about

An estimate is built from the chance the tab shows. So an estimated return
of about minus the margin means the bets landed as often as their chance
said; above that, more often. It does **not** say a bookmaker would have
paid that price: the real handicap or set-betting line may be shorter. Real
prices still need the feed probe (`odds-probe-run`), and the Scale group gate
pre-registered in the review (50 priced groups) still counts real prices
only.

First read on the replay before the tab (1 to 14 Nov, estimated): doubles 7
of 14, -15%; threefolds 3 of 12, -29%; fourfolds 2 of 10, +8%; fivefolds 1 of
7, -60%.

## Not changed

Any pick, chance, tier or group rule (`RULE` stays 3), the real-price record,
any model.

Tests: `tests/test_scale.py` `EstimatedPrices`. Roll back: `git revert`.
