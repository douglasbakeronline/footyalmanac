#!/usr/bin/env python3
"""Championship (en.2): do two draw signals the earlier notes never used fit
better? (A) a draw lift that grows as the expected total goals falls
(low-scoring games draw more); (B) each club's own draw rate so far this
season, shrunk to the league rate. Both act on the raw grid output before the
live curve. Paired bootstrap against live. History only; record.json never
read. See claude/championship-draw-signals-2026-11-19.md.

    python3 tools/championship_draw_total.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine as E, replay as R, tune as T, sources as S

SEASONS = {"2023-24": "2022-23", "2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26"}
LEAGUE_DRAW = 0.265
KSHR = 10.0   # games of pseudo-evidence pulling a club's draw rate to the league's


def rows(s):
    r, ok = S.fetch_season("en.2", s, None)
    return r if ok else []


def renorm(h, d, a, d2):
    s = h + a + d2
    return h / s, d2 / s, a / s


def build(prior, test):
    """Per fixture: raw probs, outcome, expected total, each side's shrunk draw
    rate from games before the date (replay order is by date; same-day games
    are not counted)."""
    out, seen = [], {}
    last = None
    pend = []
    for m, lh, la, info in R.replay_league(prior, test, 2):
        if m[0] != last:
            for (h, a, dr) in pend:
                for t in (h, a):
                    n, k = seen.get(t, (0, 0)); seen[t] = (n + 1, k + dr)
            pend, last = [], m[0]
        def rate(t):
            n, k = seen.get(t, (0, 0))
            return (k + KSHR * LEAGUE_DRAW) / (n + KSHR)
        h, d, a = T.outcome(lh, la, E.RHO)
        y = 0 if m[3] > m[4] else 1 if m[3] == m[4] else 2
        out.append((h, d, a, y, lh + la, (rate(m[1]) + rate(m[2])) / 2))
        pend.append((m[1], m[2], 1 if y == 1 else 0))
    return out


def main():
    base = T.live_baseline()
    print("live", T.describe(base))
    for test_s, prior_s in SEASONS.items():
        prior, test = rows(prior_s), rows(test_s)
        if not prior or not test:
            print(test_s, "unavailable"); continue
        B = build(prior, test)
        ref, acc0, _ = T.score_under([b[:4] for b in B], base)
        print(f"\n== {test_s}: n={len(ref)} live ll {T.mean(ref):.4f} acc {acc0:.3f}")
        tots = sorted(b[4] for b in B); med = tots[len(tots) // 2]
        print(f"  median expected total {med:.2f}")
        for k in (0.1, 0.2, 0.4):   # A: lift per goal below the median
            raws = []
            for h, d, a, y, tot, _ in B:
                d2 = d * max(0.3, 1 + k * (med - tot) / 0.5)
                raws.append(renorm(h, d, a, d2) + (y,))
            per, acc, _ = T.score_under(raws, base)
            dd, sd, pw = T.paired(per, ref)
            print(f"  A total k {k:.1f} delta {dd:+.4f} p(worse) {pw:.3f} acc {acc:.3f}")
        for g in (0.5, 1.0, 2.0):   # B: draw x (rate/league)^g
            raws = []
            for h, d, a, y, _, r in B:
                d2 = d * (r / LEAGUE_DRAW) ** g
                raws.append(renorm(h, d, a, d2) + (y,))
            per, acc, _ = T.score_under(raws, base)
            dd, sd, pw = T.paired(per, ref)
            print(f"  B team g {g:.1f}   delta {dd:+.4f} p(worse) {pw:.3f} acc {acc:.3f}")


if __name__ == "__main__":
    main()
