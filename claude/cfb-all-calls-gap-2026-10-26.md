# College football landing below its quotes, 26 Oct 2026 (Theo) - no change shipped

HQ planner (25 Oct): every graded cfb call 109 of 173 (63%) v 119.8 expected
(69% quoted), z -1.8. Live record used only to locate the gap (Rule 1).

## Already covered

- Elo settings (K, home advantage, season carry-over, margin of victory) are
  already swept by `sports.py --tune` on the 2024-25 fit window and shipped as
  k 32, hfa 50, regress 0.25, mov 1 (`sports.json`); fitted beat defaults on
  the gates. Nothing new to sweep in that grid.
- cfb is off the Daily List (`LIST_OFF`, 19 Oct) and its reserve gap was
  written up on 26 Oct (`sports-reserve-gap-2026-10-26.md`), same picks.
  Earlier write-up: `cfb-list-shortfall-2026-10-20.md`.

## New cuts on history (never tuned on; picks 62%+, raw model, shipped params)

| Cut | Window | n | Landed | Quoted |
|---|---|---|---|---|
| All | fit 2024-25 | 615 | 78.9% | 75.0% |
| All | check 2025-26 | 863 | 83.2% | 76.2% |
| Both teams 8+ rated games | fit / check | 510 / 681 | 75.7% / 80.3% | 75.1% / 75.9% |
| A team under 8 rated games | fit / check | 105 / 182 | 94.3% / 94.0% | 74.4% / 77.3% |
| Neutral site | fit / check | 25 / 22 | 68.0% / 81.8% | 69.6% / 70.0% |
| Sep-Oct | fit / check | 332 / 563 | 78.3% / 84.4% | 74.7% / 76.1% |
| Nov onward | fit / check | 228 / 225 | 77.6% / 81.3% | 75.8% / 77.0% |
| Aug (weeks 0-1) | fit / check | 55 / 75 | 87.3% / 80.0% | 73.2% / 74.5% |

(The "under 8 games" rows are mostly lopsided FBS v unrated opponents, which
land far above quote. Note the cold rows are under-quoted, if anything.)

No slice of history lands below its quote: not early season, late season,
neutral sites, or by experience. The model is on or above quote in both
windows, so no constant in the Elo grid would move the log loss by the
0.0005 gate, and nothing in history locates the live shortfall.

## Decision

No code or model change. The 2026 live gap (z -1.8, selected as the worst of
many cuts by the planner) is not reproduced on 1,478 held-out calls at 62%+.
Fitting to it would be fitting on the scoreboard. Revisit when roughly 150
reserve cfb picks are graded; if still 8+ points short, test a reserve floor
by per-band hit rate on both windows (see the reserve-gap note).
