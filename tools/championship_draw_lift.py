#!/usr/bin/env python3
"""Championship (en.2): does a gap-dependent draw lift fit better? Extra draw
mass when the home and away win chances are close, applied to the raw grid
output before the live calibration curve. Paired bootstrap against the live
configuration. History only; record.json is never read.
See claude/championship-draw-lift-2026-10-22.md.

    python3 tools/championship_draw_lift.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine as E, replay as R, tune as T, sources as S

SEASONS = {"2023-24": "2022-23", "2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26"}
WIDTH = 0.30


def rows(s):
    r, ok = S.fetch_season("en.2", s, None)
    return r if ok else []


def lift(raws, k, width=WIDTH):
    out = []
    for h, d, a, y in raws:
        d2 = d * (1 + k * max(0.0, width - abs(h - a)) / width)
        s = h + a + d2
        out.append((h / s, d2 / s, a / s, y))
    return out


def base_raws(prior, test):
    return [T.outcome(lh, la, E.RHO) + ((0 if m[3] > m[4] else 1 if m[3] == m[4] else 2),)
            for m, lh, la, _ in R.replay_league(prior, test, 2)]


def main():
    base = T.live_baseline()
    print("live", T.describe(base))
    for test_s, prior_s in SEASONS.items():
        prior, test = rows(prior_s), rows(test_s)
        if not prior or not test:
            print(test_s, "unavailable"); continue
        raws = base_raws(prior, test)
        ref, acc0, _ = T.score_under(raws, base)
        pd = sum(r[1] for r in raws) / len(raws)
        ad = sum(1 for r in raws if r[3] == 1) / len(raws)
        print(f"\n== {test_s}: n={len(ref)} live ll {T.mean(ref):.4f} acc {acc0:.3f} "
              f"pred draw {pd:.3f} actual {ad:.3f}")
        for k in (0.1, 0.2, 0.3, 0.5, 0.8):
            per, acc, _ = T.score_under(lift(raws, k), base)
            d, sd, pw = T.paired(per, ref)
            print(f"  k {k:.1f}  delta {d:+.4f}  p(worse) {pw:.3f}  acc {acc:.3f}")


if __name__ == "__main__":
    main()
