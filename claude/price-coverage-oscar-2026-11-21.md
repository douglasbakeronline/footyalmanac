# Pricing more Odds tab legs: no change shipped (21 Nov 2026, Oscar)

Task: find a free source or a better API-Football match that prices more legs.

## Checked
- The matcher (`price_football`, `af_same`, `AF_SPELLINGS`) already carries 11 spellings and the 90-minute kick-off window; `AF_RETIME` / `AF_UNTIMED` fix times.
- `claude/football-card-unpriced-2026-11-20.md`: core-league 60%+ legs 41 priced, 2 unpriced over 13 to 23 Nov; both France's women's D1, which sits outside the Card under rule 14. `claude/price-coverage-oscar-2026-11-13.md` found the same under earlier rules.
- No `groupings.json` or keys in this sandbox, and the pool archive keeps priced legs only, so the unpriced count and a before/after on today's pool cannot be measured here.

## Decision
No change. The measured gap is about two legs in eleven days and none was one leg short of a group. A Odds API soccer fallback would spend shared credits for almost nothing; the neighbouring-day lookup adds calls and cannot be tested offline (Rule 10). Prices still never feed a model.

## Reopen when
"football Card unpriced" in the build log shows core-league legs on two or more days in a week.
