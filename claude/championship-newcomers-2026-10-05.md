# England Championship: where the misses are, and carrying newcomers' ratings (held, 5 Oct 2026)

Task (Priya, Championship Specialist): follow Mia's 4 Oct rejection of league
home advantage and rho (`championship-test-2026-10-04.md`) with one new idea.
History only; record.json not read (Rule 1). Reproduce:
`python3 tools/championship_newcomers.py` (needs network; en.3 comes from API-Football).

## Where the misses are (live model, live calibration, walk-forward replay)

| Slice | 2024-25 ll / acc | 2025-26 ll / acc | 2026-27 (95) ll / acc |
|---|---|---|---|
| All | 1.035 / 48% | 1.063 / 44% | 1.090 / 36% |
| Both sides in prior season | 1.071 / 42% | 1.060 / 45% | 1.084 / 32% |
| A promoted/relegated side plays | 0.990 / 55% | 1.067 / 43% | 1.096 / 41% |
| Each side under 8 games | 1.017 / 49% | 1.145 / 31% | 1.090 / 36% |
| Later in the season | 1.038 / 48% | 1.046 / 47% | n/a |
| Big gap (xG diff > 0.5) | 0.988 / 53% | 1.030 / 49% | 1.001 / 57% |
| Small gap (< 0.2) | 1.102 / 37% | 1.087 / 40% | 1.113 / 25% |
| Actual draws (~27%) | 1.328 | 1.271 | 1.281 |
| Actual non-draws | 0.921 / 67% | 0.988 / 60% | 1.006 / 52% |

Reading: draws cost about 0.3 log loss each and are never the top pick, so a
27% draw rate alone puts the floor near 1.0. The big-gap games are fine; the
misses are the coin-flip middle. Newcomers are not consistently worse
(better in 2024-25, level in 2025-26). Early season was bad in 2025-26 only.

## The one idea tested: newcomers' prior

The live build carries a promoted or relegated club's rating across divisions
(`transfer_rating`, `SHRINK_ON_TRANSFER` 10). The shared replay starts them at
1.00 / 1.00, so the replay never exercised that path for en.2. Added an optional
`extra_prior` to `replay.replay_league` (default off, no behaviour change) and
replayed with newcomers carried from en.1 (relegated) and en.3 (promoted),
paired bootstrap, 1500 reps, positive delta = carrying is worse:

| Season | Transfer k | Delta log loss | p(worse) | Delta on newcomer games |
|---|---|---|---|---|
| 2024-25 (n 557) | 10 (live) | +0.0040 | 0.998 | +0.0091 (249) |
| 2025-26 (n 557) | 10 (live) | +0.0018 | 0.831 | +0.0041 (248) |
| 2026-27 (n 95) | 10 (live) | +0.0088 | 0.941 | +0.0199 (42) |

More shrink is monotonically better (k 5, 10, 20, 40 give +0.0022, +0.0018,
+0.0013, +0.0009 on 2025-26), i.e. the best carried rating is no carried
rating. Split by source, relegated en.1 clubs hurt more than promoted en.3
clubs (2024-25 +0.0030 vs +0.0011), but only 3 clubs a source a season, so
this is a handful of teams.

## Verdict: held, nothing shipped

Direction is consistent across three seasons, but Rule 3 cannot be met:
2026-27 has 95 Championship fixtures against the 250 gate, the three clubs a
source are too few to separate a rating effect from a few team stories, and
the replay's carry is an approximation of the live path (name matching,
`last_league`). No model number changed, and `engine.py` is untouched.

Revisit when 2026-27 has 250+ en.2 fixtures (about November): if carried
newcomers are still worse, test setting `SHRINK_ON_TRANSFER` higher for tier-2
destinations (or a neutral start) with the full gates, and check the other
divisions too (this is a cross-league question, not a Championship one).
Do not repeat the draws, rho or home advantage tests.
