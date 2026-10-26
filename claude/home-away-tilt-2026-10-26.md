# Is the home/away tilt overstated? — 26 October 2026

Not shipped. The finding is real on the live record, the fix helps on the
season it is fitted on, and the current season is too short to pass the
gates. Tooling: `tools/home_away_tilt.py` (advisory, writes only its own
report into `audit-out/`). Nothing in `engine.py`, `calibration.json` or
`europe.json` changed.

## The finding (live record, diagnostic only, never fitted on)

`record-graded.json`, clean rows (not Celtic's Law, not unrated), 5,404
graded football picks to 26 Oct 2026:

| Picks | n | Quoted | Landed | Gap | z |
|---|---|---|---|---|---|
| home | 3,936 | 50.6% | 51.4% | +0.8 | +1.1 |
| away | 1,389 | 44.8% | 52.3% | +7.5 | +5.6 |
| draw | 79 | 37.0% | 38.0% | +1.0 | +0.2 |

Mean quoted triple 0.445 / 0.264 / 0.291 against actual 0.442 / 0.246 / 0.311.
Home picks land on quote; away picks land well over it; draws are quoted
about 2 points too often. By family: the core leagues (1,669) have the
sharpest away gap (45.3% quoted, 57.0% landed, z +4.8, actual split
0.432 / 0.234 / 0.334); the API-Football wider leagues (3,382) a smaller one
(44.4% v 51.3%, z +4.2, actual 0.445 / 0.254 / 0.301). Cups and the small
families point the other way on tiny samples.

Why the calibration curve cannot fix it: `temper` scales all three
probabilities by one temperature chosen from the top probability. It can make
a pick more or less confident; it cannot move mass from home to away. Only
the tilt (`HOME_MULT` / `AWAY_MULT`, through `venue_multipliers(ha_scale)`)
and the draw term (`RHO`) do that.

## What was tested

`tools/home_away_tilt.py`, on the walk-forward replay (`tune.lambdas`, the
live engine functions), under the live curve T = 1.135 − 0.30 × (conf − 0.45),
every comparison paired and bootstrapped against the live configuration on
the same fixtures. Fit on the last completed season, check on the current one
(rule 3). Candidates declared before the check was read: the best `ha_scale`
on the fit season, the best `RHO`, then both together. Rule 4: each
candidate was also scored with the curve refitted for it on the fit season.

Replay coverage (`python3 replay.py --audit`, 26 Oct 2026, from the committed
cache; football-data.co.uk was unreachable from this session, so its five
leagues count as missing, as they did in the September fits):

- **fit (2025-26):** 30 competitions, 5,262 fixtures. en.1, en.2, en.4,
  sco.1, es.1, es.2, de.1, de.2, it.1, it.2, fr.1, fr.2, nl.1, pt.1, be.1,
  tr.1, at.1, gr.1, br.1, au.1, nor.1, dnk.1, swe.1, isl.1, geo.1, ltu.1,
  lva.1, est.1, blr.1, fro.1. Tiers: 1 mostly, en.2 / es.2 / de.2 / it.2 /
  fr.2 tier 2, en.4 tier 4.
- **check (2026-27):** 13 competitions, 902 fixtures. en.1 50, en.2 95,
  sco.1 42, es.1 69, de.1 36, it.1 50, fr.1 45, nl.1 63, pt.1 62, tr.1 36,
  at.1 42, gr.1 35, br.1 277. 807 are tier 1, 95 tier 2.
- **Not in the replay at all:** the API-Football wider leagues (`AF_EXTRA`,
  227 of them, 63% of the live record's clean rows), `AF_NEW`, the English
  step 3, every cup and international. `tune.codes` leaves them out by
  design (30 Sep 2026). So a tilt by family cannot be gated on anything: the
  only evidence is the core leagues, and one global scale is all that can be
  tested honestly. The AF_EXTRA away gap is a live-record observation with no
  replay behind it.

Live baseline on the replay: fit log loss 1.0190, accuracy 49.18%; check
1.0262, 47.89%.

### The same bias is in the replay, smaller

Live picks on the replay, live curve:

| Season | Picks | n | Quoted | Landed | Gap | z |
|---|---|---|---|---|---|---|
| fit 2025-26 | home | 3,916 | 50.4% | 49.7% | −0.8 | −0.9 |
| fit 2025-26 | away | 1,337 | 45.8% | 47.9% | +2.1 | +1.6 |
| check 2026-27 | home | 694 | 48.5% | 47.5% | −0.9 | −0.5 |
| check 2026-27 | away | 206 | 44.7% | 49.5% | +4.8 | +1.4 |

Mean quoted triple, fit: 0.446 / 0.260 / 0.295 against actual
0.432 / 0.261 / 0.306. Check: 0.438 / 0.266 / 0.296 against
0.430 / 0.263 / 0.307. The draw is quoted correctly on the replay; the live
draw gap is not in these leagues.

### ha_scale sweep (0.80 to 1.00, everything else live, Δ log loss v live)

| ha_scale | Fit Δ | sd | p(worse) | Fit acc | Check Δ | sd | p(worse) | Check acc |
|---|---|---|---|---|---|---|---|---|
| 0.80 | −0.0006 | 0.0005 | 0.16 | 49.24% | −0.0002 | 0.0012 | 0.45 | 47.34% |
| 0.82 | −0.0006 | 0.0005 | 0.13 | 49.32% | −0.0002 | 0.0011 | 0.43 | 47.67% |
| 0.84 | −0.0006 | 0.0004 | 0.10 | 49.39% | −0.0003 | 0.0010 | 0.41 | 47.34% |
| 0.86 | −0.0005 | 0.0004 | 0.09 | 49.45% | −0.0003 | 0.0009 | 0.39 | 47.34% |
| 0.88 | −0.0005 | 0.0003 | 0.06 | 49.54% | −0.0003 | 0.0007 | 0.37 | 47.67% |
| 0.90 | −0.0005 | 0.0003 | 0.05 | 49.58% | −0.0003 | 0.0006 | 0.35 | 47.67% |
| 0.92 | −0.0004 | 0.0002 | 0.03 | 49.56% | −0.0002 | 0.0005 | 0.33 | 47.45% |
| 0.94 | −0.0003 | 0.0002 | 0.03 | 49.51% | −0.0002 | 0.0004 | 0.31 | 47.56% |
| 0.96 | −0.0002 | 0.0001 | 0.01 | 49.35% | −0.0001 | 0.0002 | 0.29 | 47.78% |
| 0.98 | −0.0001 | 0.0001 | 0.01 | 49.26% | −0.0001 | 0.0001 | 0.27 | 47.67% |
| 1.00 (live) | 0 | | | 49.18% | 0 | | | 47.89% |

Every value under 1.0 is better on the fit season, flat from 0.80 to 0.90
(−0.0006 to −0.0005), with the gain shrinking toward 1.0. On the check
season every value is on the right side of zero but by 0.0001 to 0.0003 with
p(worse) 0.27 to 0.45: the sign is consistent, the size is under the gate
and the noise band (sd up to 0.0012 on 902 fixtures) is wider than the
effect. The `tune.py --report` sweep says the same (0.9: −0.0005, p 0.05 on
the fit season; 0.8: −0.0006, p 0.16), as it has since the 3 Oct snapshot.

### RHO sweep

| RHO | Fit Δ | p(worse) | Check Δ | p(worse) |
|---|---|---|---|---|
| −0.10 | +0.0001 | 0.67 | +0.0002 | 0.67 |
| −0.08 | +0.0000 | 0.53 | +0.0001 | 0.62 |
| −0.07 | −0.0000 | 0.47 | +0.0000 | 0.59 |
| −0.06 (live) | 0 | | 0 | |
| −0.05 | +0.0000 | 0.66 | −0.0000 | 0.47 |
| −0.04 | +0.0001 | 0.71 | +0.0000 | 0.50 |
| 0.00 | +0.0005 | 0.90 | +0.0003 | 0.61 |

RHO is at its optimum, as it was in September. The engine has no other draw
multiplier; the live draw over-quote is not something the Dixon-Coles term
can take out, and on the replay's leagues the draw is quoted right anyway.

### Gate table

Check season 2026-27, 902 fixtures, against the live configuration:

| Candidate | Fit Δ | Fit p(worse) | Check Δ | Check sd | Check p(worse) | ≥250 | p ≤ 0.30 | gain ≥ 0.0005 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| ha_scale 0.82 | −0.0006 | 0.13 | −0.0002 | 0.0011 | 0.43 | PASS | FAIL | FAIL | not shipped |
| ha_scale 0.82, curve refit 1.085 / −0.20 | −0.0006 | 0.07 | −0.0004 | 0.0010 | 0.37 | PASS | FAIL | FAIL | not shipped |
| RHO −0.07 | −0.0000 | 0.47 | +0.0000 | 0.0002 | 0.59 | PASS | FAIL | FAIL | not shipped |
| ha_scale 0.82 + RHO −0.07 | −0.0006 | 0.13 | −0.0002 | 0.0011 | 0.45 | PASS | FAIL | FAIL | not shipped |
| both, curve refit 1.08 / −0.20 | −0.0007 | 0.07 | −0.0004 | 0.0010 | 0.36 | PASS | FAIL | FAIL | not shipped |

Accuracy on the check season moves from 47.89% to 47.67% (two fixtures) under
the tilt. By tier: tier 1 (807) −0.0002, tier 2 (95) −0.0002, the same small
size everywhere.

### What the tilt does to the side bias (ha_scale 0.82, live curve)

| Season | Picks | n before → after | Quoted → | Landed → | Gap before → after |
|---|---|---|---|---|---|
| fit | home | 3,916 → 3,725 | 50.4 → 49.6% | 49.7 → 50.3% | −0.8 → +0.8 |
| fit | away | 1,337 → 1,526 | 45.8 → 45.9% | 47.9 → 46.9% | +2.1 → +1.0 |
| check | home | 694 → 661 | 48.5 → 47.5% | 47.5 → 48.0% | −0.9 → +0.4 |
| check | away | 206 → 240 | 44.7 → 44.8% | 49.5 → 46.7% | +4.8 → +1.8 |

Mean quoted triple after, fit: 0.431 / 0.262 / 0.308 (actual
0.432 / 0.261 / 0.306); check: 0.423 / 0.268 / 0.309 (actual
0.430 / 0.263 / 0.307). So 0.82 does what it was meant to: the quoted split
lands on the actual split and the away gap closes to within noise. It does it
by moving about 190 fit picks (34 check) from the home side to the away side
and taking roughly a point off every home quote. It is a small, correctly
signed, consistent effect that the check season cannot yet confirm at the
bar.

## Why nothing shipped

Rule 3 and the gates. The check season is 902 fixtures and the effect is
0.0002-0.0004 of log loss; the bootstrap sd on that sample is 0.0010-0.0012,
so p(worse) sits at 0.36-0.45 whichever way the curve is handled. The gate
needs p(worse) ≤ 0.30 and gain ≥ 0.0005. Both fail, and the gain gate would
fail even on the fit season's own number for most of the grid (−0.0005 to
−0.0006, at the bar). Loosening a gate for a change that the live record
suggests would be fitting on the scoreboard by the back door (rule 1).

Two honest caveats about the live evidence too. The live away gap (z +5.6)
is 2-3 times the replay's (fit +2.1 points, check +4.8), and 63% of the live
rows come from leagues the replay does not cover. Either the wider leagues
have less home advantage than the tier default gives them (plausible: the
tier table was set on English football), or ten weeks of one season are
running away-heavy, or both. The replay cannot tell these apart and the
record must not be fitted on.

## What would settle it

1. **Let the check season grow.** At the current effect size the bootstrap
   needs roughly 3,000 check fixtures to put 0.0003 at p(worse) 0.30 (sd
   scales with 1/√n from 0.0011 at 902), and the gain gate still needs the
   effect itself to reach 0.0005; that is about January at the earliest.
   `tools/home_away_tilt.py` reruns in a minute from the cache. If the sign
   holds and the size holds, ship 0.85-0.90 then.
2. **Per-league home advantage** (`tools/model_ideas.py --fit-home`,
   `home-advantage.json`, weekly in `tune.yml`) is the finer version of this
   change and already learns on its own under the same gates. A global
   `ha_scale` under 1.0 and a per-league factor would double count; if the
   weekly refit switches itself on first, re-run this tool before touching
   `ha_scale`.
3. **A replay for the wider leagues.** The AF_EXTRA family is where most of
   the live rows and a clear away gap sit, and `tune.codes` keeps them out of
   every fit. Giving them a prior season in the replay (API-Football has it)
   would let a tilt by family be gated instead of guessed. Until then the
   tier defaults stand for them.

## Strength coefficients (`tune_strengths.py --fit`)

Not run. `tune_strengths.py` reads the openfootball/champions-league archive
(`fetch_repo`, a codeload tarball) and there is no cached copy in the repo;
the session's proxy refused the download (HTTP 403) and the request to attach
the repository went unanswered. Read `tune_strengths.py` first: it is a
Poisson log-linear fit of one strength per country on single-match UEFA
results, England fixed at 1.00, regularised toward the hand-set values
(REG_K 40), fit on every complete season and checked on the last one, with
its own gates (≥150 check matches, p(worse) ≤ 0.30, gain ≥ 0.0003). It
writes `engine_strengths.json` on a pass for a human to apply by hand, so it
would not have touched `europe.json` or `engine.py` either way (rule 5).
`current/af-cup-replay.json` is present (version 5, domestic cups) but holds
domestic ties only, so it is not a check on cross-country strengths. Run it
from a session that can reach GitHub and record the numbers here.

## Files

- `tools/home_away_tilt.py` (new, advisory): the fine `ha_scale` sweep, the
  RHO sweep, the three declared candidates with and without a refit curve,
  quoted-v-landed by side before and after, by-tier breakdown.
  `--json audit-out/home-away-tilt.json` keeps the full run (gitignored).
- `claude/home-away-tilt-2026-10-26.md` (this note).
- No change to `engine.py`, `tune.py`, `calibration.json`, `europe.json`,
  the golden tests or any bot-written file. `python3 -m unittest discover
  -s tests` (510 tests) and `python3 nametest.py` pass unchanged.
