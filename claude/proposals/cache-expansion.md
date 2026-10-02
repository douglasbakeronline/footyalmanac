# Proposal: expand replay coverage with the current-season cache

Status: advisory comparison done; change not implemented. Calibration was
not refitted or applied. Follows `claude/evaluation-audit.md`.

## Problem

`tune.load` reads `history/`, openfootball, football-data.co.uk and
API-Football, never `current/`, the season-so-far cache the live build uses
for ESPN-sourced competitions. So most of those competitions have no
2026-27 test season in the harness, and the check season that gates every
Monday calibration refit covers 17 competitions.

## Advisory comparison

Frozen snapshot `aa19d05b33faf7e5044a78bd5e6cfe13938a4475793e570d66a43b46dd6e7bda`
(360 harness seasons + 40 cached current seasons). Shipped calibration,
unchanged. Reproduce:

```
python3 replay.py --freeze audit-out/snapshot.json      # or reuse the frozen file
python3 replay.py --audit --snapshot audit-out/snapshot.json --include-current
```

Fit season: unchanged (the cache holds only current seasons).

Check season 2026-27:

| | Competitions | Fixtures | Log loss | Accuracy | Brier |
|---|---|---|---|---|---|
| original | 17 | 1,386 | 1.0256 | 48.2% | 0.6153 |
| expanded | 39 | 5,432 | 1.0390 | 46.9% | 0.6246 |
| added by the cache only | 22 | 4,046 | 1.0435 | 46.4% | 0.6277 |

Quoted vs landed, shipped calibration:

| Band | original | added only |
|---|---|---|
| 30-40% | 38% -> 40% (335) | 37% -> 38% (1,085) |
| 40-50% | 45% -> 43% (583) | 44% -> 43% (1,762) |
| 50-60% | 54% -> 53% (294) | 54% -> 55% (820) |
| 60-70% | 64% -> 73% (122) | 64% -> 64% (300) |
| 70%+ | 75% -> 79% (52) | 74% -> 80% (79) |

Added competitions: ar.1, br.2, cl.1, cn.1, co.1, de.2, ec.1, en.4, es.2,
fr.2, it.2, jp.1, nl.2, nor.1, pe.1, sa.1, sco.2, swe.1, tr.1, us.1, us.2,
uy.1.

Offered by the cache but still excluded: en.3 and mx.1 (prior rows outside
the season window), ru.1 and dnk.1 (prior/test overlap), and en.5, svn.1,
za.1, py.1, ve.1, cr.1, hn.1 and four women's leagues (no prior season).
`current/svn.1-2026-27.json` is the El Salvador feed from before the wrong
slug was removed (Sep 2026): stale data that should be deleted.

## Reading it

- Four times the check evidence (5,432 v 1,386), which makes the 250-fixture
  gate and the bootstrap far more meaningful.
- The added competitions are harder (log loss 1.0435 v 1.0256), so the
  check-season log loss rises for reasons that are not a model change.
  Comparisons must stay paired on one fixture set; never compare an
  expanded-set number with an original-set number.
- The shipped calibration holds up on the added set without refitting
  (54/55, 64/64); its top band under-quotes there too (74 -> 80, 79 games).

## Proposed change, gated

1. Add the cache to `tune.load` for test seasons only, behind the existing
   validation (overlap, window, missing seasons), with the source recorded
   per season in the exclusion report.
2. Run `tune.py --fit --dry-run` on both coverages and report, without
   writing: the fitted curve, the check-season gate results, and the
   paired difference on the original 17 competitions alone.
3. Only then decide whether the Monday refit should use the expanded set.
   That is a change to what calibration is judged on, so it needs the
   owner's sign-off; nothing auto-applies from this proposal.
4. Delete `current/svn.1-2026-27.json` (El Salvador data).

## Risk

Medium. It changes which fixtures gate calibration. Steps 1-2 are advisory
and reversible; step 3 is the decision.
