# Coverage expansion — 10 September 2026

## The problem

The site claimed 74 leagues and could show **21**, all European except Brazil.
The rest were cups with no published schedule and 35 competitions flagged
`ratingsOnly`, which carry ratings so their clubs can be priced in European
qualifying but whose own fixtures are never fetched. Norway, Sweden, Denmark,
Switzerland, Ireland and 30 others were in that bucket, in season, and invisible.

## The cause

openfootball publishes current-season fixtures for ten European leagues plus
Brazil. Nothing else. Eighteen candidate paths probed on 10 Sep 2026, all 404:

```
MLS (3 path shapes), Liga MX, Argentina, Brazil Serie B, Japan, Australia,
Norway 2026, Sweden 2026, Denmark 26-27, Finland, Ireland, Iceland,
Switzerland, Croatia, Czechia, Poland          -> all 404
England 2026-27                                -> 200 (sanity check)
```

That is the ceiling. No config change reaches those leagues through openfootball.

## What was built

- **61 competitions marked `"live": True`** in `engine.LEAGUES` — no openfootball
  path, sourced entirely from ESPN. 21 competitions that can appear becomes 79.
- **`backfill.py`** — walks a past season date by date and caches it to
  `history/<code>-<season>.json`. `sources.fetch_season` reads that before the
  network. ~300 requests once per league, none per build.
- **`backfill.py --probe`** — asks every slug for a recent Saturday and
  Wednesday, reports what answered. The slugs are unverified guesses at ESPN's
  naming, written in a container that cannot reach ESPN.
- **Flag fallback** — `index.html` reads its flag set off the SVG sprite, so a
  country with no flag drawn renders without one instead of an empty box.

## Season strings were a year stale

The 35 former rating sources had `season` pointing at 2025 (calendar leagues) or
`prev` at 2024-25 (split-year). Their ratings were coming from two seasons ago.
Fixed to 2026 / 2025-26 respectively.

## Split of work still needed

**16 live leagues already have a prior season** from openfootball's
football.json even though it carries no schedule for them. A working slug is all
they need, no backfill:

`ar.1, blr.1, br.2, cn.1, co.1, est.1, fin.1, fro.1, geo.1, irl.1, isl.1, jp.1,
ltu.1, lva.1, nor.1, swe.1`

**45 need backfilling** before their predictions mean anything:

`ae.1, alb.1, arm.1, au.1, aze.1, bgr.1, bih.1, ch.1, cl.1, cyp.1, cze.1, de.3,
dnk.1, ec.1, hrv.1, hun.1, in.1, isr.1, kr.1, lux.1, mda.1, mkd.1, mlt.1, mne.1,
mx.1, na.ccc, nir.1, nl.2, pe.1, pol.1, pt.2, rou.1, ru.1, sa.1, sa.lib, sa.sud,
sco.2, srb.1, svk.1, svn.1, ukr.1, us.1, us.2, uy.1, wal.1`

## Order of operations for Douglas

1. `python3 backfill.py --probe` — prune dead slugs from `sources.ESPN_SLUGS`
2. `python3 backfill.py --season 2025` then `--season 2025-26` — cache history
3. Commit `history/`, push, let the daily build pick it up

## Guards

- A backfilled season with fewer than 30 matches is not written (wrong slug or
  wrong season string; confidently wrong ratings are worse than none).
- An already-cached season is skipped, so reruns are free.
- A wrong slug returns nothing and the competition does not appear. Verified by
  running a full build with ESPN blocked: 93 fixtures across 5 days, unchanged.

## Known unverified

Every ESPN slug added. They follow ESPN's published naming but none could be
tested. Expect a meaningful fraction to be wrong on first probe, particularly
the smaller European ones (`slv.1` for Slovenia and `bih.1`, `mkd.1`, `mne.1`
are the least confident).
