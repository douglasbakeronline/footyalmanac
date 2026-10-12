# England Championship: a league-specific rating shrink (rejected, 12 Oct 2026)

Task (Priya): one untested idea for en.2 after the 4 Oct (home advantage, rho)
and 5 Oct (newcomers' prior) notes. Idea: the Championship is the most even
league, so its season ratings may deserve more (or less) shrink toward the
mean than the global `SHRINK_FULL_SEASON` 4, or a slower hand-over from the
prior (`BLEND_K` 6). History only; record.json not read (Rule 1).
Reproduce: `python3 tools/championship_shrink.py` (needs network for openfootball).

Walk-forward `replay.replay_league`, live RHO and live curve (1.135 / -0.30),
paired bootstrap 1500 reps. Negative delta = better.

| Setting | 2023-24 | 2024-25 | 2025-26 (fit) | 2026-27 (95, confirm) |
|---|---|---|---|---|
| shrink 2 | +0.0004 | +0.0018 (p .96) | +0.0006 | +0.0011 |
| shrink 3 | +0.0001 | +0.0007 | +0.0002 | +0.0005 |
| shrink 6 | -0.0001 | -0.0010 (p .12) | -0.0002 (p .41) | -0.0008 (p .33) |
| shrink 8 | +0.0000 | -0.0014 (p .18) | -0.0001 | -0.0012 (p .34) |
| shrink 12 | +0.0004 | -0.0012 | +0.0004 | -0.0017 (p .36) |
| blend_k 12 | +0.0001 | -0.0008 | +0.0007 | -0.0020 (p .31) |
| blend_k 16 | +0.0005 | -0.0006 | +0.0015 | -0.0025 (p .32) |

Live log loss: 1.053, 1.035, 1.063, 1.090 (2023-24 to 2026-27).

Verdict: rejected. On the fit season (2025-26) the best setting gains 0.0002,
under the 0.0005 gate, with p(worse) 0.41. The sign flips between seasons
(2024-25 and 2026-27 like more shrink or a slower blend, 2023-24 and 2025-26
do not), and 2026-27 has 95 fixtures against the 250 gate. Fewer shrink
(2, 3) is worse in every season, which supports the global 4 as a floor.
The surface is flat within 0.002 everywhere: the Championship's misses are
the coin-flip middle and draws (see the 5 Oct note), not mis-sized ratings.

Nothing shipped; no model number changed. Do not repeat a en.2 shrink or blend
test unless 2026-27 passes 250 fixtures and the sign has held across two
completed seasons. Untested still: a gap-dependent draw lift (extra draw mass
when |lh - la| is small), which the calibration curve, being a function of
top-pick confidence only, cannot express.
