# What the constants are actually worth — 9 September 2026

Method: walk-forward on 2025/26 (5,281 fixtures) to fit, 2026/27 to date
(545 fixtures) to check. Every comparison paired and bootstrapped, because an
unpaired comparison of two log losses around 1.016 has a noise band of ±0.005,
which is wider than every real effect in this model.

## Result of sweeping every constant

| Constant | Shipped | Best found | Δ log loss | Verdict |
|---|---|---|---|---|
| TEMPERATURE | 1.15 | 1.00–1.05 | −0.0012 | wrong *shape*, see below |
| RHO | −0.06 | −0.06 | 0.0000 | already optimal |
| BLEND_K | 6 | 8 | −0.0001 | already optimal |
| form window | 5 | 5 | −0.0001 | already optimal |
| home advantage scale | 1.0 | 0.9 | −0.0001 | already optimal |
| SHRINK_FULL_SEASON | 6 | 2–3 | −0.0016 | **evaporates after calibration** |
| FORM_MAX | 0.05 | 0.15–0.20 | −0.0013 | **evaporates after calibration** |

Total gain available from re-tuning all seven: about 0.3% of log loss. The
constants are not where the problem is.

## The one real finding: the model is under-confident at the top

Calibration on the fit season, shipped T = 1.15:

| Quoted band | n | Quoted | Landed |
|---|---|---|---|
| ≥70% | 170 | 76.0% | 84.7% |
| 62–70% | 287 | 65.3% | 72.1% |
| 55–62% | 567 | 58.0% | 64.7% |
| <55% | 4257 | 44.0% | 44.6% |

One temperature applies the same correction to a 40% call and an 85% one, and
those need opposite corrections. Replaced with `calibration.json`:
**T = 1.075 − 0.45 × (confidence − 0.45)**, fitted on 2025/26, checked on
2026/27 (−0.0017 log loss, p(worse) 0.195, all three gates passed).

Effect is on volume, not accuracy:

| | Shipped | Calibrated |
|---|---|---|
| Strong (≥70%) fixtures | 170 (3.2%) | 317 (6.0%) |
| Strong hit rate | 84.7% | 79.2% |
| Strong quoted vs landed | 76.0 vs 84.7 | 78.1 vs 79.2 |
| Fixtures at 55%+ | 1,024 | 1,321 |

Expected correct Strong calls per season: 144 → 251.

Tier labels in index.html updated to the recalibrated backtest: Strong 79%,
Firm 66%, Lean 61%, No read 44%. Headline figures now 5,281 fixtures,
49.5% correct, 43.7% baseline, top decile 75.0%.

## Tested and rejected

- **Separate home/away ratings per team** (roadmap item 5): clearly worse,
  +0.0124 log loss, p(worse) 1.00, confirmed on holdout. Halving the sample per
  rating costs more than the venue split adds. Remove from the roadmap.
- **Rest days** (roadmap item 4): no effect at any coefficient from −0.008 to
  +0.020. Δ 0.0000. Remove from the roadmap.
- **Ten free per-band temperatures**: fits better, generalises worse than the
  two-parameter line. Rejected in favour of the line.

## The trap worth remembering

SHRINK_FULL_SEASON and FORM_MAX both looked like real wins in isolation
(p(worse) 0.01 and 0.04). After the calibration curve went in, both fell to
Δ ≈ 0.0000 on the fit season. They were compensating for the miscalibration,
not adding information. Fit one thing, then re-test everything else.

## The machinery

`tune.py` — `--report` sweeps every constant, `--fit` refits calibration.json
behind three gates: ≥250 check-season fixtures, p(worse) ≤ 0.30, gain ≥ 0.0005.
Standard library only. `.github/workflows/tune.yml` runs it Mondays 04:40 UTC.
Calibration auto-applies when it passes; structural constants are advisory
output only and never move on their own.

**Gate baseline (fixed 3 Oct 2026).** The gates compare a candidate curve
with the calibration the site is using (`tune.live_baseline()`: the
`calibration.json` curve, or the flat 1.15 only when there is no file), both
scored on the same fixtures. Before, the baseline was always the flat 1.15,
so any curve that beat 1.15 could replace a live curve it did not beat. Every
refit from 14 to 30 Sep was gated that way. On the frozen snapshot
`aa19d05b...` the Monday candidate (1.155 / −0.30) passed against 1.15
(−0.0006, p(worse) 0.09) but against the live 1.135 / −0.30 it is +0.0001,
p(worse) 0.75: it fails, and the live curve stays. The `--report` sweep's
baseline is the live configuration too (curve, RHO, shrinkage, blend, form,
home advantage, read from `engine.py`); with a curve live its flat
temperature rows ask whether replacing the curve with one constant would do
better. Sweep on `aa19d05b...` (fit season, 6,474, baseline log loss
1.0239 under the live curve): no flat temperature beats the curve (best
1.10, +0.0001); BLEND_K 8 (−0.0005, p(worse) 0.02) and home advantage 0.9
(−0.0004, p(worse) 0.04) are flagged on the fit season only, at or below the
0.0005 gain gate and not checked on the current season. Advisory; nothing
changed. Tests: `tests/test_calibration_gate.py`.

Rules that keep it honest, in priority order:

1. Nothing is ever fitted on record.json. The live record is the scoreboard.
2. Every comparison is paired on the same fixtures and bootstrapped.
3. Anything fitted on the last completed season must survive on the current one.

## Still untested

The 74 league strength coefficients, which the roadmap calls the single largest
weakness. A league-only walk-forward cannot test them: within a league they
cancel out entirely. Testing them needs a cross-competition harness built on
European ties and cross-division cups. That is now the highest-value open item.


## Re-test, 29 September 2026: a form-led model

Douglas asked for the model to be led by this season's form after Needham
Market (a league not covered) won on form. Every setting was scored with the
calibration curve refitted for it, on 2025/26 (6,272 fixtures) and 2026/27
(789; ESPN-sourced leagues were not reachable from the cloud session).

| Setting | 2025/26 | 2026/27 | Verdict |
|---|---|---|---|
| FORM_MAX 0.10 | -0.0003, p 0.12 | -0.0006, p 0.17 | wash on fit |
| FORM_MAX 0.30 | +0.0011 | +0.0009 | worse |
| FORM_MAX 0.50 | +0.0050 | +0.0050 | worse |
| form 0.30, last 3 | +0.0029 | +0.0020 | worse |
| BLEND_K 3 (season takes over after 3 games) | +0.0017 | +0.0027 | worse |
| Form-led: shrink 2, blend 3, form 0.30 | +0.0049 | +0.0059 | worse |
| SHRINK_FULL_SEASON 3 | -0.0004, p 0.14 | -0.0009, p 0.23 | passes |
| **SHRINK_FULL_SEASON 4** | **-0.0004, p 0.04** | **-0.0007, p 0.18** | **shipped** |
| shrink 3 + form 0.10 | -0.0004, p 0.20 | -0.0009, p 0.29 | no better than shrink alone |

Heavy form weighting chases noise: a five-game run is mostly luck at these
goal rates. What holds up is letting this season's full record count sooner,
which is the honest version of "this season's form". calibration.json was fit
at shrink 6; Monday's tune.yml refits it on the full data.


## Re-test, 30 September 2026: table-position and goal-record penalties

Douglas asked for clubs in the bottom 10% of their table playing away, and
clubs substantially low for goals scored and high for goals conceded
(z <= -1 and z >= +1 against their league), to be weighted to lose. Tested as
multipliers on the flagged side's expected goals (and the inverse on the
opponent's), calibration refitted per setting, both seasons.

| Setting | Flagged (fit / check) | 2025/26 | 2026/27 |
|---|---|---|---|
| bottom-10% away x0.90 | 495 / 34 | +0.0010, p(worse) 0.98 | +0.0017, 0.94 |
| bottom-10% away x0.80 | | +0.0030, 1.00 | +0.0047, 0.99 |
| bottom-10% away x0.70 | | +0.0053, 1.00 | +0.0083, 1.00 |
| weak attack and defence x0.90 | 447 / 27 | +0.0009, 0.98 | +0.0019, 0.98 |
| weak attack and defence x0.80 | | +0.0029, 1.00 | +0.0048, 1.00 |
| both x0.85 | | +0.0036, 1.00 | +0.0062, 1.00 |

Worse at every strength. The ratings are built from goals scored and
conceded, so these sides are already priced to lose; a second penalty counts
the same evidence twice. Rejected.

## Re-test, 30 September 2026: recency built into the ratings

Douglas again asked for recent form to be weighted heavily. Unlike the 29 Sep
variants (a form multiplier on top), this weights each team's own season so
its k-th most recent match counts decay^k in the attack/defence rating.
Calibration refitted per setting, 2025/26 fit, 2026/27 check (789).

| Decay | Half-life | 2025/26 | 2026/27 |
|---|---|---|---|
| 0.98 | 34 games | -0.0002, p(worse) 0.20 | -0.0001, 0.38 |
| 0.95 | 13.5 | +0.0001 | -0.0001 |
| 0.92 | 8.3 | +0.0010 | +0.0001 |
| 0.90 | 6.6 | +0.0018, 0.96 | +0.0002 |
| 0.85 | 4.3 | +0.0042, 1.00 | +0.0006 |
| 0.80 | 3.1 | +0.0067, 1.00 | +0.0010 |

A long half-life is a wash; anything that makes recent games dominate is
worse, and more so the harder it leans. Over a full season, what a side did
in August is still evidence in March. Rejected; nothing shipped.


## Test, 5 October 2026: between-season carry-over and a prior for sides new to the league (Ben)

Two untested ratings ideas, scored paired and bootstrapped under the live
calibration curve (1.135 / -0.30), 2025/26 fit (6,474 fixtures) and 2026/27
check (1,386), frozen on the data the session could fetch. Harness: the
`replay.replay_league` loop with the prior ratings edited.

**1. Carry-over of last season's rating.** Prior rating pulled toward 1.00 by
a factor (`1 + c * (prior - 1)`), a "decay between seasons".

| c | 2025/26 | 2026/27 |
|---|---|---|
| 0.70 | +0.0020, p(worse) 1.00 | +0.0041, 1.00 |
| 0.85 | +0.0008, 1.00 | +0.0017, 0.99 |
| 1.10 | -0.0003, 0.08 | -0.0007, 0.08 |
| 1.25 | -0.0003, 0.28 | -0.0011, 0.19 |

Extra decay is clearly worse. Less decay (c > 1) gains under 0.0005 on the
fit season, so it fails the gain gate. Last season's rating is already
shrunk enough (SHRINK_FULL_SEASON 4). Rejected.

**2. A prior below 1.00 for sides with no prior season in the league**
(replay gives them 1.00 / 1.00).

| att / def | 2025/26 | 2026/27 |
|---|---|---|
| 0.95 / 1.05 | -0.0008, p(worse) 0.00 | -0.0008, 0.09 |
| 0.90 / 1.10 | -0.0014, 0.00 | -0.0011, 0.18 |
| 0.85 / 1.15 | -0.0017, 0.00 | -0.0009, 0.31 |

These clear the gates numerically, but **nothing shipped**, for three reasons:

- The replay's "no prior" sides are all newly promoted clubs. Live,
  `build.rating_for` already gives a club promoted from a covered division a
  `transfer_rating` carry, not 1.00 (see `claude/evaluation-audit.md`, "Not
  replayed"). Only a club with no resolvable prior gets 1.00 live, and those
  are already flagged unrated (Celtic's Law). The gain here is measured on a
  population the live build mostly does not price this way, so it is not
  evidence for changing the live 1.00.
- The calibration curve was not refitted per setting (the trap above), so
  the gain may partly be the curve compensating.
- It confirms the direction, though: promoted sides are weaker than league
  average, so 1.00 flatters them.

**Next test worth running (not done):** make the replay carry promoted sides
through `transfer_rating` from the division below (data for en.2, es.2, de.2,
it.2, fr.2 is already fetched), then test SHRINK_ON_TRANSFER and a promoted
discount on that, refitting calibration. Only then change `build.rating_for`.


## Re-test, 19 October 2026: form by stage of the season

Douglas asked again for recent form to count, "so much can change between
seasons". New angle: score the model by how many games each side has played
this season, then test the weighting there. Frozen snapshot `aa19d05b...`,
live calibration curve, paired.

Where the model is weak (log loss, top-pick accuracy):

| Games played (fewer of the two) | 2025/26 | 2026/27 |
|---|---|---|
| 0-3 | 1.0185, 49.0% (1,100) | 1.0072, 49.3% (582) |
| **4-6** | **1.0552, 45.2%** (725) | **1.0533, 45.9%** (314) |
| 7-12 | 1.0231, 48.6% (1,252) | 1.0000, 54.1% (185) |
| 13+ | 1.0193, 49.1% (3,397) | 1.0480, 44.9% (305) |

Games 4-6 are the weak spot in both seasons: the point where this season's
results start moving the ratings. Not the first games, where last season
carries the ratings.

Weighting changes, paired change in log loss (negative better):

| Setting | 2025/26 at 4-6 | 2025/26 all | 2026/27 at 4-6 | 2026/27 all |
|---|---|---|---|---|
| BLEND_K 4 (season counts faster) | +0.0040 | +0.0012 | +0.0002 | +0.0004 |
| FORM_MAX 0.15 | +0.0035 | +0.0006 | +0.0004 | -0.0004 |
| BLEND_K 10 (slower) | -0.0031, p 0.01 | -0.0006, p 0.09 | +0.0013 | +0.0001 |
| BLEND_K 15 | -0.0043 | -0.0002 | +0.0032 | +0.0007 |
| SHRINK 8 | -0.0025 | +0.0011 | -0.0001 | +0.0026 |
| last season only | -0.0027 | +0.0138 | +0.0137 | +0.0068 |

More weight on recent results is worse; less weight helps games 4-6 in one
season and not the other, so it fails rule 3. Ignoring this season is far
worse, so this season's results are already doing real work. The 4-6 dip is
real but no weighting of results fixes it. What changes between seasons and
is not in the results (transfers, injuries, line-ups) is the untested lever:
API-Football Pro carries injuries, line-ups and transfers. Nothing shipped.


## Test, 19 October 2026: team news (injuries and suspensions) from API-Football

The lever left after the stage-of-season test: what changes and is not in the
results. API-Football Pro lists, per fixture, every player missing (injured or
suspended) or doubtful. Fetched for the Premier League, Championship, La Liga,
Bundesliga, Serie A, Ligue 1, Eredivisie and Primeira Liga (730 calls; data
kept out of the repo in `audit-out/team-news/`, not for redistribution):
2,500-6,000 rows a league for 2025-26, Portugal almost none. Player importance
from the previous season's league minutes. Harness `tools/team_news_eval.py`:
each fixture priced as the replay would that morning, then
`lh *= exp(-a*missH + b*missA)` (and the mirror), a and b fitted on 2025-26,
checked on 2026-27, paired, live calibration curve.

| Measure | Fitted a, b | 2025-26 (2,919) | 2026-27 (470) |
|---|---|---|---|
| count of players missing | 0, 0 | 0 | 0 |
| missing minutes (regulars ~1) | -0.02, +0.02 | -0.0002, p(worse) 0.30 | -0.0010, p 0.16 |
| new absences since last match | -0.02, +0.04 | -0.0001 | -0.0000 |

Sides average 3.7 players listed missing (about one regular), barely related
to strength (r 0.08), so the data is real and varied. The first two measures
were declared with a, b >= 0 (absences hurt); both fitted to zero. The grid was
then opened to both signs and "new absences" added: post hoc. The one
measure that clears the check gates does so by about one standard deviation,
gains 0.0002 on the season it was fitted on (under the 0.0005 bar), and has
the wrong sign for attack (a side missing regulars "scores more"). Not
shipped. Listed absences are mostly long-term, and a long absence is already
in the side's recent results, which the ratings read.

Revisit with the tool when 2026-27 has about 1,500 fixtures (re-fetch the
2026 injuries, 8 calls): a real effect would show the right sign and hold.
Not tested: confirmed line-ups (published about an hour before kick-off,
after the site's morning prices; using them means re-pricing late).


## Test, 19 October 2026: hot form, big clubs and cups, against the quoted chance

Douglas: recent form (last 3, last 5) should carry more weight, bigger clubs
are more consistent, and cups hold more opportunity. Tested as "at the same
quoted chance, do these picks land more often than quoted?" If they did, the
model would be under-rating them. Frozen snapshot `aa19d05b...`, both seasons,
favourites quoted 60%+ under the live curve (1,121). Big club: last season's
top four by points per game in its league (a free stand-in for squad value).

| Group | n | Landed | Quoted | Gap (95%) |
|---|---|---|---|---|
| favourite won all of last 3 | 192 | 68.2% | 70.8% | -2.5% (6.4) |
| favourite won 2 of last 3 | 413 | 70.9% | 69.4% | +1.6% (4.4) |
| favourite won 0-1 of last 3 | 342 | 66.7% | 66.4% | +0.2% (5.0) |
| favourite won 4-5 of last 5 | 285 | 71.9% | 71.2% | +0.7% (5.3) |
| favourite won 0-2 of last 5 | 286 | 67.8% | 66.1% | +1.7% (5.5) |
| underdog won 2-3 of last 3 | 144 | 71.5% | 68.3% | +3.2% (7.6) |
| favourite is a big club | 744 | 72.3% | 70.1% | +2.2% (3.3) |
| favourite is not | 377 | 66.3% | 65.8% | +0.5% (4.8) |
| big club, quoted 70%+ | 324 | 78.1% | 77.6% | +0.5% (4.5) |

Hot favourites land slightly under their quote, cold ones on it: form beyond
what the ratings hold carries nothing, as the weighting tests found. Big clubs
supply two thirds of the confident picks and land as quoted: consistent, and
already priced as such.

Cups, the opposite of an opportunity: the cup replay (`current/af-cup-replay.json`,
1,968 priced ties) has clean 75%+ calls landing 47% (n 19, Jan-Jun) and 80%
(n 20, Jul-Oct), cross-division 39-66%; live cup picks quoted 60%+ landed 56.5%
against 69.7% (46), 70%+ 60.0% against 80.3% (15). Cups stay off the Daily List
on the daily gate. If anything, cup confidence is too high.

Nothing shipped.


## Domestic cup calibration, 19 October 2026 (shipped)

Douglas chose honest cup numbers. The cup replay (`build.cup_replay`, version
4+) now keeps every priced tie: the model's home / draw / away as of the tie's
morning, and the result. `tools/cup_calibration.py` fits a cup adjustment on
ties before 1 Jul 2026 (747) and checks it on ties after (1,221), paired,
against no cup adjustment, under tune.py's gates. Two candidates, declared in
order:

| Candidate | Fit (747) | Check (1,221) | Gates |
|---|---|---|---|
| one temperature, T = 1.4 | -0.0076, p(worse) 0.064 | -0.0007, p(worse) 0.426 | fails notWorse |
| curve T = 0.90 + 2.75 x (conf - 0.45) | -0.0141, p 0.009 | -0.0047, p 0.164 | passes |

Confident cup calls before and after, check ties: 60%+ landed 62.0% against
69.9% quoted before, 66.7% against 63.9% after. A raw 75% cup favourite now
shows about 59%. Shipped as `engine.CUP_CALIBRATION` / `engine.cup_temper`,
applied to API-Football domestic cups (`afCup`) live and inside the cup
replay's gate (version 5, which still stores the raw prices for refits).
Continental cups are not covered: the replay has no evidence on them. A
structural constant: refit by hand with the tool, never automatically.


## Test, 21 October 2026: capping blowout goals in the ratings (Ben)

Idea not tested before: a 7-0 inflates an attack and a defence rating more
than a 2-0 tells us about either, so cap each side's goals per match at c
when building the table (`GF` / `GA`, and so the league goal rate) and leave
the results alone. Replay as in `replay.replay_league`, `build_table` wrapped
to cap; frozen fetch of the harness seasons, 2025/26 fit (6,474 fixtures),
2026/27 check (1,490). Paired change in log loss against the shipped model
under the live curve (negative better), 1,000-draw bootstrap. "Refit" picks
the best (a, b) on the fit season for that cap, then applies it to the check
(rule 4, so a cap cannot hide behind the curve).

| Cap | Calibration | 2025/26 | 2026/27 |
|---|---|---|---|
| 5 | live | -0.0002, p(worse) 0.19 | +0.0005, 0.96 |
| 5 | refit 1.15 / -0.30 | -0.0002, 0.22 | +0.0006, 0.96 |
| 4 | live | +0.0005, 0.90 | +0.0011, 0.94 |
| 4 | refit 1.15 / -0.45 | +0.0005, 0.90 | +0.0010, 0.94 |
| 3 | live | +0.0025, 1.00 | +0.0031, 0.98 |
| 3 | refit 1.05 / -0.45 | +0.0019, 1.00 | +0.0018, 0.94 |

Worse or a wash at every cap, and worse the harder it bites. Heavy wins are
information about a side's level, not noise to trim; the only cap that is
not worse on the fit season (5) gains 0.0002, under the 0.0005 gate, and loses
on the check season. Rejected; nothing shipped. (Capping both sides can turn a
6-5 into a 5-5 for the form points; this touches a handful of games and does
not change the verdict.) Harness: `tools/goal_cap_eval.py` (fetches the seasons
via `tune.load`, about a minute).
