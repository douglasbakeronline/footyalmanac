# Daily List tennis 39/51 v 42 expected: located, noise, nothing changed (30 Oct 2026)

Trigger: HQ planner (29 Oct), tennis list picks over 28 days 39 of 51 (76%) v 42.2 expected, z -1.2.

## It is the 15 Oct figure again

39 of 51 v 42.1 is the number that took tennis off the list on 15 Oct and put it back on 28 Oct
(`daily-list-order-review-2026-10-28.md`). The planner's window still holds that fortnight.
Nothing new has landed badly since.

## Where the shortfall sits

Located on `tennis-record.json` (read only, nothing fitted, rule 1). Graded main-draw picks at 75%+ (the
list bar, n=139): 115 landed (82.7%) v 82.3% quoted.

| Cut | n | landed | quoted |
|---|---|---|---|
| 1-15 Oct | 64 | 78% | 83% |
| 16-30 Oct | 69 | 86% | 82% |
| ATP | 56 | 84% | 81% |
| WTA | 83 | 82% | 83% |
| 75-80% band | 55 | 82% | 77% |
| 80-85% band | 41 | 78% | 82% |
| 85-90% band | 29 | 86% | 87% |
| 90%+ band | 14 | 93% | 92% |
| Dongfeng Voyah Wuhan Open | 12 | 50% | 82% |
| all other tournaments | 127 | 86% | 82% |

The gap is one tournament, Wuhan (6 of 12, early Oct, before the 8 Oct ratings fix in
`tennis-ratings-gap-2026-10-08.md`), plus Shanghai (8 of 11). Since 16 Oct the list picks beat their quote.

## Suspects checked

- **Cumulative tested rate on rows:** already replaced on 26 Oct. Tennis rows quote the live own-band rate
  when a band has 30 graded picks, else no chip (`build_tennis.accuracy_for`).
- **Tier-2 leagues at 75%:** does not apply. Tennis has no tier-2 leagues; the tier-2 bar is football's.
- **A stricter bar:** the 75-80% band lands above its quote (82% v 77%), so raising the bar to 80% would drop
  the best-calibrated picks and keep the one band under quote (78% v 82%, n=41, inside one standard error).
  No admission rule was fitted: the only data to fit on is the live record, which rule 1 forbids.

## Verdict

Noise plus one tournament in a period already explained by stale ratings. No code change. Review at 300
graded list picks as already planned (the list has 64 so far). Revisit only if a slice falls two standard
errors under quote on 50+ picks since 28 Oct.
