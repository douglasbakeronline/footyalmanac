#!/usr/bin/env python3
"""Championship (en.2): where the misses are, and whether carrying promoted /
relegated clubs' ratings across divisions (as the live build does) beats the
replay's 1.00 / 1.00 start, and what transfer shrink fits best.
History only; record.json is never read. See claude/championship-newcomers-2026-10-05.md.

    python3 tools/championship_newcomers.py
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import engine as E, replay as R, tune as T, sources as S

# test season, prior season (same league), and the season the newcomers came from
SEASONS = {"2024-25": "2023-24", "2025-26": "2024-25", "2026-27": "2025-26"}


def rows(code, s):
    r, ok = S.fetch_season(code, s, None)
    return r if ok else []


def carried(prior_season, k, prior_en2):
    """{team: rating in en.2 terms} for clubs in en.1 or en.3 of `prior_season`.
    Names are matched to the en.2 spelling lazily by the caller (see lookup)."""
    out = {}
    for src in ("en.1", "en.3"):
        rt = E.strength_from_table(E.build_table(rows(src, prior_season)), k=E.SHRINK_FULL_SEASON)
        for t, r in rt.items():
            out[t] = E.transfer_rating(r, src, "en.2", k=k)
    return out


def run(test_s, prior_s, k):
    prior, test = rows("en.2", prior_s), rows("en.2", test_s)
    params = {}
    if k is not None:
        pool = carried(prior_s, k, prior)
        known = {t for m in prior for t in (m[1], m[2])}
        extra = {}
        for m in test:
            for t in (m[1], m[2]):
                if t in known or t in extra:
                    continue
                n = t if t in pool else S.match_team(t, set(pool))
                if n:
                    extra[t] = pool[n]
        params["extra_prior"] = extra
    out = list(R.replay_league(prior, test, 2, params=params))
    return prior, out


def main():
    base = T.live_baseline()
    print("live calibration:", T.describe(base))
    for test_s, prior_s in SEASONS.items():
        prior, ref = run(test_s, prior_s, None)
        known = {t for m in prior for t in (m[1], m[2])}
        raws = [T.outcome(lh, la, E.RHO) + ((0 if m[3] > m[4] else 1 if m[3] == m[4] else 2),)
                for m, lh, la, _ in ref]
        per, acc, _ = T.score_under(raws, base)
        n = len(per)
        print(f"\n== {test_s}: {n} matches, log loss {T.mean(per):.4f}, acc {acc:.3f}")
        # breakdown
        def grp(name, pred):
            idx = [i for i, (m, lh, la, inf) in enumerate(ref) if pred(i, m, lh, la, inf)]
            if idx:
                hits = sum(1 for i in idx if raws[i][:3].index(max(raws[i][:3])) == raws[i][3])
                print(f"  {name:34s} n={len(idx):4d} ll={T.mean([per[i] for i in idx]):.4f} acc={hits/len(idx):.3f}")
        grp("both sides in prior", lambda i, m, lh, la, inf: m[1] in known and m[2] in known)
        grp("a newcomer plays", lambda i, m, lh, la, inf: m[1] not in known or m[2] not in known)
        grp("first 8 games per side (early)", lambda i, m, lh, la, inf: min((inf["rows"][m[1]] or {"P": 0})["P"], (inf["rows"][m[2]] or {"P": 0})["P"]) < 8)
        grp("later", lambda i, m, lh, la, inf: min((inf["rows"][m[1]] or {"P": 0})["P"], (inf["rows"][m[2]] or {"P": 0})["P"]) >= 8)
        grp("big gap |lh-la|>0.5", lambda i, m, lh, la, inf: abs(lh - la) > 0.5)
        grp("small gap |lh-la|<0.2", lambda i, m, lh, la, inf: abs(lh - la) < 0.2)
        grp("actual draws", lambda i, m, lh, la, inf: m[3] == m[4])
        grp("actual non-draws", lambda i, m, lh, la, inf: m[3] != m[4])
        # test
        for k in (None, 10.0, 5.0, 20.0, 40.0):
            _, o = run(test_s, prior_s, k)
            r2 = [T.outcome(lh, la, E.RHO) + (raws[i][3],) for i, (m, lh, la, _) in enumerate(o)]
            p2, a2, _ = T.score_under(r2, base)
            m_, sd, pw = T.paired(p2, per)
            new = [i for i, (m, *_r) in enumerate(ref) if m[1] not in known or m[2] not in known]
            dn = T.mean([p2[i] - per[i] for i in new]) if new else 0
            print(f"  carry k={k}: ll {T.mean(p2):.4f} delta {m_:+.4f} p(worse) {pw:.3f} "
                  f"acc {a2:.3f}; delta on newcomer games ({len(new)}) {dn:+.4f}")


if __name__ == "__main__":
    main()
