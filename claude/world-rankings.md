# World rankings as a model input — 28 September 2026

Douglas asked for world rankings to be a variable when picking winners.
Rankings are built from results, and the models already rate from results,
so each was tested before it was allowed to move a number: fit on 2025,
judged on 2026, paired bootstrap, tune.py gates, honesty guard.

| Ranking | Where | Result on 2026 | Verdict |
|---|---|---|---|
| FIFA points gap | men's internationals, win picks | -0.0361 log loss, p(worse) 0.00; top 20% 80.9% -> 84.3% | **in the model** |
| ATP rank gap (log ratio, capped 151) | ATP | -0.0037, p(worse) 0.03 | **in the model** |
| WTA rank gap, same form | WTA | -0.0004, p(worse) 0.30 | shown only |
| World Rugby | rugby tests | no reachable source (API and Pulselive both refuse) | not available |
| Club competitions | leagues | no world ranking exists; league results are already the input | n/a |

The FIFA test first froze the international ratings on 1 January, which let
the in-year ranking look better than it is. Re-run with the ratings refitted
quarterly (both sides equally fresh), the gain held (-0.0361 vs -0.0405).
The live site's international ratings are refitted by hand every few weeks.

## How it works

`rankings.py`:
- FIFA from FIFA's own API (`inside.fifa.com/api/ranking-overview?dateId=idN`).
  Release ids step irregularly; `fifa-rankings.json` holds the latest and
  `refresh_fifa` scans the next 160 ids when the file is over 21 days old.
  CI commits the file. History for the test: Dato-Futbol's archive (to Sep
  2024) plus the 13 releases since (Oct 2024 - Jul 2026).
- `FIFA_NAMES` maps the site's spellings to FIFA's (19 entries). Non-FIFA
  sides (Martinique, Guadeloupe, Bonaire, Zanzibar...) have no ranking and
  keep the unadjusted number.
- ATP/WTA from ESPN's rankings (top 150, keyed by athlete id, which the
  scoreboard carries). Outside the top 150 counts as 151, as in the test.
- Both re-score only the pick's probability (what the test measured):
  p' = sigmoid(w0 + w1 logit(p) + w2 gap [+ w3]). For football the other two
  outcomes are rescaled to keep the total at 1.

Adjusted rows carry `rankAdjusted`, their own accuracy bands and their own
list threshold (internationals 60%, ATP 65%, both by the shared 75%-landed
rule). Rows show `FIFA #57` / `ATP #6` / `WTA #108`, and the expanded row
says when a ranking changed the number.

## Open

- World Rugby rankings, if a source becomes reachable.
- Women's internationals (FIFA women's ranking) untested.
- Retest the WTA ranking once more 2026 data is in.
