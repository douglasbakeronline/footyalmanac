# The Model card on the replay (10 Nov 2026)

The 30 Nov review compares the Card (the bookmakers' favourites the model
rates 5 to 10 points under the market, opposition 9+) with the Model card
(the model's own picks at or above the bookmakers' chance, on paper since
31 Oct). On the paper record that is 14 Model card groups, far too few to
decide. So the Model card's rule is now pre-registered as a replay variant,
`modelcard` in `tools/card_replay.py`, built on the same legs as the Card,
graded and staked as the Card kind it mirrors (two units on a 2x, one on a
3x), and as `cardModel` in `tools/card_legs_history.py` on every
football-data season (legs admitted on the model's own 60%+, `legs(model=True)`).
Nothing on the page or in the Card's rule changed.

## The read, the pool from 30 Oct

| read | variant | days | groups | won | legs landed v bookmakers | return | paired v live |
|---|---|---|---|---|---|---|---|
| first real prices | live | 0 | 0 | | | | |
| first real prices | modelcard | 4 | 5 | 3 | 13 of 15, 86.7% v 65.9% | +60% | +1.36 a day, p(worse) 0.19 |
| `--recover` | live | 6 | 10 | 4 | 21 of 31, 67.7% v 73.8% | -7% | |
| `--recover` | modelcard | 8 | 12 | 7 | 29 of 36, 80.6% v 68.1% | +58% | +1.60 a day, p(worse) 0.02 |

The Model card's legs landed well above the bookmakers' chance on the pool,
the Card's under. But 36 legs is a third of the decision gate (100+ legs,
p(worse) at most 0.30, and the football-data seasons agreeing), and the
football-data replay found the opposite over 2025-26: picks the model rates
above the market landed at the market's rate at every gap size. The
football-data `cardModel` line (run on this pull request by
`card-legs-history.yml`, then weekly by `tune.yml`) is the other half of the
gate.

## Decision

None today. If `modelcard` beats live on the pool at 100+ legs with
p(worse) at most 0.30 and `cardModel` is not worse than `card` on both
football-data seasons, the 30 Nov review (or the first session after the
gate is met) switches the Card to the Model card's rule, with a CARD_RULE
bump and a release. If football-data disagrees, the Card stays and the note
says so.
