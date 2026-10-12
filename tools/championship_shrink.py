#!/usr/bin/env python3
"""Championship (en.2): does a league-specific SHRINK_FULL_SEASON fit better
than the global 4? Paired bootstrap against the live configuration under the
live curve. History only; record.json is never read.
See claude/championship-shrink-2026-10-12.md.

    python3 tools/championship_shrink.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine as E, replay as R, tune as T, sources as S

SEASONS = {"2023-24": "2022-23", "2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26"}


def rows(s):
    r, ok = S.fetch_season("en.2", s, None)
    return r if ok else []


def scored(prior, test, params, base):
    out = list(R.replay_league(prior, test, 2, params=params))
    raws = [T.outcome(lh, la, E.RHO) + ((0 if m[3] > m[4] else 1 if m[3] == m[4] else 2),)
            for m, lh, la, _ in out]
    return T.score_under(raws, base)[0]


def main():
    base = T.live_baseline()
    print("live shrink", E.SHRINK_FULL_SEASON, "blend_k", E.BLEND_K, T.describe(base))
    for test_s, prior_s in SEASONS.items():
        prior, test = rows(prior_s), rows(test_s)
        if not prior or not test:
            print(test_s, "unavailable"); continue
        ref = scored(prior, test, {}, base)
        print(f"\n== {test_s}: n={len(ref)} live ll {T.mean(ref):.4f}")
        for name, p in [("shrink 2", {"shrink": 2}), ("shrink 3", {"shrink": 3}),
                        ("shrink 6", {"shrink": 6}), ("shrink 8", {"shrink": 8}),
                        ("shrink 12", {"shrink": 12}),
                        ("blend_k 12", {"blend_k": 12}), ("blend_k 16", {"blend_k": 16})]:
            per = scored(prior, test, p, base)
            d, sd, pw = T.paired(per, ref)
            print(f"  {name:11s} delta {d:+.4f}  p(worse) {pw:.3f}")


if __name__ == "__main__":
    main()
