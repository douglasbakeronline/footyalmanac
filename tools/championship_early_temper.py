#!/usr/bin/env python3
"""Championship (en.2): does the model deserve extra flattening early in the
season, while the clubs have few games behind them? Extra temperature
T += k when the less-played side has fewer than N games, on top of the live
curve. Fit on 2025-26, confirm on 2026-27, paired bootstrap. History only;
record.json is never read. See claude/championship-early-temper-2026-11-26.md.

    python3 tools/championship_early_temper.py
"""
import os, sys, math
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine as E, replay as R, tune as T, sources as S

SEASONS = {"2023-24": "2022-23", "2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26"}
N_GRID = [4, 6, 8, 10]
K_GRID = [0.1, 0.2, 0.4]


def rows_for(prior_s, test_s):
    prior, ok1 = S.fetch_season("en.2", prior_s, None)
    test, ok2 = S.fetch_season("en.2", test_s, None)
    if not (ok1 and ok2):
        return []
    out, played = [], defaultdict(int)
    by_date = defaultdict(list)
    rep = list(R.replay_league(prior, test, 2))
    for m, lh, la, _ in rep:
        by_date[m[0]].append((m, lh, la))
    for d in sorted(by_date):
        for m, lh, la in by_date[d]:       # games before this date only
            g = min(played[m[1]], played[m[2]])
            out.append((T.outcome(lh, la, E.RHO) + ((0 if m[3] > m[4] else 1 if m[3] == m[4] else 2),), g))
        for m, lh, la in by_date[d]:
            played[m[1]] += 1; played[m[2]] += 1
    return out


def score(rows, base, n, k):
    per = []
    for (h, d, a, y), g in rows:
        p = (h, d, a)
        t = T.curve_T(max(p), {"a": base["a"], "b": base["b"]})
        if g < n:
            t += k
        q = [max(x, T.EPS) ** (1.0 / t) for x in p]
        s = sum(q)
        per.append(-math.log(max(q[y] / s, T.EPS)))
    return per


def main():
    base = T.live_baseline()
    print("live", T.describe(base))
    data = {s: rows_for(p, s) for s, p in SEASONS.items()}
    for s, r in data.items():
        if not r:
            print(s, "unavailable"); continue
        early = [x for x in r if x[1] < 8]
        ref = score(r, base, 0, 0)
        e_ref = [v for v, x in zip(ref, r) if x[1] < 8]
        print(f"{s}: n={len(r)} ll {T.mean(ref):.4f}; early(<8) n={len(early)} ll {T.mean(e_ref):.4f}")
    fit = data["2025-26"]
    best = None
    for n in N_GRID:
        for k in K_GRID:
            m = T.mean(score(fit, base, n, k))
            if best is None or m < best[0]:
                best = (m, n, k)
    print(f"best on fit: N {best[1]} k {best[2]}")
    print("\ndelta v live (p(worse)):")
    for n in N_GRID:
        for k in K_GRID:
            cells = []
            for s, r in data.items():
                if not r:
                    continue
                d, sd, pw = T.paired(score(r, base, n, k), score(r, base, 0, 0))
                cells.append(f"{s} {d:+.4f} (p {pw:.2f})")
            print(f"N {n} k {k}: " + " | ".join(cells))


if __name__ == "__main__":
    main()
