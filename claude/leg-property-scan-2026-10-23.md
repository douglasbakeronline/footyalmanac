# Which legs land at their quote? Leg-property scan, no rule found (23 Oct 2026)

**Result: no leg property separates legs that land at quote from legs that fall short, on both seasons. No rule shipped.** `tools/leg_property_test.py` reproduces it (run `tools/odds_edge_test.py /tmp/w/legs.json` first; needs football-data.co.uk).

## Method

Football replay, not the record. Legs from `tools/odds_edge_test.py`: every home or away outcome (draws out) of priced matches, fit season 2025-26 and check season 2026-27 to date, model chance as the site quoted it (live calibration), fair chance with the margin removed. A leg joins the pool as the Wider groups do: chance = min(model, fair) at 65%+ (`WIDE_MIN`). Statistic: mean(hit - chance), 90% bootstrap interval. Nothing fitted; `record.json` not read. Tested rate is not in the historic data, so it is not a cut here; Celtic's Law is not either (flags are not archived with the legs).

## Pool-wide: legs land ABOVE their quote

| Season | Legs | Landed | Gap to chance | 90% interval |
|---|---|---|---|---|
| Fit 2025-26 | 321 | 80.1% | +7.4 pts | +3.6 to +11.0 |
| Check 2026-27 | 44 | 84.1% | +11.8 | +1.6 to +20.8 |

This agrees with `midband-calibration-2026-10-21.md`: 65-80% calls land above quote in football. min(model, fair) is conservative.

## Cuts (fit / check gap, points)

- Home +8.0 (273) / +12.0 (39); away +4.4 (48) / +10.0 (5). Both positive.
- Chance 65-70: +9.3 / +21.3; 70-75: +7.1 / +11.3; 75-80: +8.6 / -4.7 (11 legs); 80-90: +0.8 / +17.1 (3 legs).
- Price under 1.15: +0.4 / +3.7 (9); 1.15-1.30: +9.9 / +11.1; 1.30-1.45: +6.6 / +30 (5).
- Model minus fair, at or below 0: +11.1 (149) / +14.1 (34); 0 to +5: +5.3 (103) / -6.1 (7); above +5: ~+2 / n 4.
- Top flight (code .1): +6.8 / +11.8; other: +16.8 (22) / n 0.
- By league (fit n 8-63): Spain +13.9, Netherlands +10.5, Portugal +7.5, Germany +7.6, Italy -1.8, England -3.7. Check season cells have 0-14 legs.

Only one cut keeps its sign and a lead on both seasons: model at or below the market lands higher than model above it (+11.1 / +14.1 v +5.3 / -6.1). That is the finding of 21 and 23 Oct (`odds-edge-test-2026-10-23.md`) again, and it is already the rule (`MAX_ABOVE_BOOK`, 5 points).

## The one rule replayed: model must not exceed the market (cap 5 -> 0)

Of 321 eligible legs on the fit season, the rule keeps the 149 with model at or below fair and removes the other 172 (54%); the live cap of 5 already removes 25 (8%). Either way the loss is far past the "no more than a fifth of eligible legs" limit, and the check season has 44 legs against the 250 the gates need. Kept legs land +11.1 pts v +7.4 for all. Rejected: it loses too many legs for a gap that cannot be told from noise.

## Live archive, descriptive only (285 unique settled legs, 4-23 Oct)

Not fitted on (Rule 1), shown for the direction. Landed v chance: football priced 74.3% v 76.7% (-2.4, 175 incl. unpriced), tennis 67.8% v 83.1% (-15.3, 59), college football 70.4% v 85.4% (-15.1, 27), NFL 64.7% v 73.6% (17), rugby 85.7% v 86.9% (7). Unpriced (estimated) legs -10.6 pts v priced -4.7. Football legs under 1.15 landed 91.3% v 83.9% (+7.4, 23), 1.30+ landed 68.3% v 73.4% (-5.1, 82). The shortfalls sit in sports `GROUP_SPORTS` already excludes (football and rugby only since 19 Oct) and in unpriced legs, which the strict rule already refuses. Football's -2.4 is inside noise.

## Verdict

No rule change. Sport, tier, home or away, price, rating gap and chance band do not separate quoting from falling short on both seasons; the live shortfall is already handled by sport exclusion and the priced-leg requirement. Do not repeat the tighter model-over-market cap. Open: the tested rate, Celtic's Law flag and Daily List membership cannot be cut on history until each leg's tested rate is archived with the prediction; re-run when about 100 settled Doubles and Trebles exist.
