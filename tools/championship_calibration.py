#!/usr/bin/env python3
"""Championship (en.2): does a league-specific calibration curve fit better
than the global one? Grid over (a, b) of T = a + b x (confidence - 0.45),
fitted on 2025-26, confirmed on 2026-27 (and shown on 2023-24, 2024-25).
Paired bootstrap against the live curve. History only; record.json is never
read. See claude/championship-calibration-2026-11-11.md.

    python3 tools/championship_calibration.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine as E, replay as R, tune as T, sources as S

SEASONS = {"2023-24": "2022-23", "2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26"}
A_GRID = [0.9, 1.0, 1.1, 1.135, 1.2, 1.3, 1.4, 1.5]
B_GRID = [-0.6, -0.45, -0.30, -0.15, 0.0, 0.3]


def raws_for(prior_s, test_s):
    prior, ok1 = S.fetch_season("en.2", prior_s, None)
    test, ok2 = S.fetch_season("en.2", test_s, None)
    if not (ok1 and ok2):
        return []
    return [T.outcome(lh, la, E.RHO) + ((0 if m[3] > m[4] else 1 if m[3] == m[4] else 2),)
            for m, lh, la, _ in R.replay_league(prior, test, 2)]


def main():
    base = T.live_baseline()
    print("live", T.describe(base))
    data = {s: raws_for(p, s) for s, p in SEASONS.items()}
    fit = data["2025-26"]
    best = None
    for a in A_GRID:
        for b in B_GRID:
            per = T.score_under(fit, {"kind": "curve", "a": a, "b": b})[0]
            m = T.mean(per)
            if best is None or m < best[0]:
                best = (m, a, b)
    print(f"best on 2025-26 fit: a {best[1]} b {best[2]} ll {best[0]:.4f}")
    cand = {"kind": "curve", "a": best[1], "b": best[2]}
    for s, raws in data.items():
        if not raws:
            print(s, "unavailable"); continue
        ref = T.score_under(raws, base)[0]
        per = T.score_under(raws, cand)[0]
        d, sd, pw = T.paired(per, ref)
        print(f"{s}: n={len(raws)} live {T.mean(ref):.4f} cand {T.mean(per):.4f} "
              f"delta {d:+.4f} p(worse) {pw:.3f}")
    print("\nfit-season surface (delta v live, 2025-26 / 2024-25 / 2026-27):")
    refs = {s: T.score_under(r, base)[0] for s, r in data.items() if r}
    for a in A_GRID:
        row = []
        for b in B_GRID:
            c = {"kind": "curve", "a": a, "b": b}
            row.append("/".join(f"{T.mean(T.score_under(data[s], c)[0]) - T.mean(refs[s]):+.4f}"
                                for s in ("2025-26", "2024-25", "2026-27")))
        print(f"a {a}: " + "  ".join(f"b{b}:{x}" for b, x in zip(B_GRID, row)))


if __name__ == "__main__":
    main()
