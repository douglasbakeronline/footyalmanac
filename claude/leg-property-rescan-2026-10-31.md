# Which legs land at their quote? Re-scan, no rule found (31 Oct 2026)

**Result: rejected again. No leg-selection change shipped.** Repeats `claude/leg-property-scan-2026-10-23.md` on the refreshed pull (`tools/odds_edge_test.py` then `tools/leg_property_test.py`; football-data.co.uk prices, never `record.json`, no price feeds a model). Fit 2025-26, check 2026-27 to date. Pool as the Wider groups: chance = min(model, fair) at 65%+, draws out. Statistic: mean(hit - chance), 90% bootstrap interval.

## Pool-wide

Fit 310 legs, landed 81.9%, +9.3 pts [+5.7, +13.0]. Check 42 legs, 81.0%, +8.8 [-1.4, +18.6]. Eligible legs land above their quote, as before.

## Cuts (fit / check, points, n)

- Home +9.6 (254) / +10.2 (35); away +8.1 (56) / +2.2 (7).
- Chance 65-70 +15.1 / +15.6; 70-75 +4.8 / +10.3; 75-80 +9.4 / -5.0 (11); 80-90 -0.5 / n 2.
- Price under 1.15 +0.7 / +4.0 (9); 1.15-1.30 +11.1 / +7.5; 1.30-1.45 +10.0 / n 4.
- Model minus fair: at or below 0 +14.4 (154) / +7.9 (33); within 5 above +3.4 (93) / +5.1 (n 6).
- Top flight +8.8 (289) / +8.8 (42); lower +16.7 (21) / n 0.
- Leagues (fit n 23-64): Spain +14.1, Netherlands +13.5, France +12.6, Portugal +7.9, Germany +8.3, Italy +1.6, England -2.2. Check cells are 0-15 legs.

## The one rule replayed: model no higher than the market (cap 5 -> 0)

Keeps the 154 legs with model at or below fair and removes the other 156 (50%), well past the fifth allowed. The kept legs gain +14.4 v +9.3 on fit but only +7.9 v +8.8 on check, so the lead does not hold on both seasons, and the check season has 33 legs against the 250 the Rule 3 gate needs. Rejected.

## Verdict

Sport, tier, home or away, price, rating gap and chance band separate nothing that holds on both seasons. Shortfalls on the live archive sit in sports already off the groups and in unpriced legs, both already refused. Do not repeat. Still open: tested rate and Celtic's Law flag are not archived per leg; since 30 Oct `groupings-archive/pool-<date>.json.gz` keeps the pool, so cut on those at the 30 Nov review.
