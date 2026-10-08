#!/usr/bin/env python3
"""Advisory: tennis confidence bands, shrink and list bar from the walk-forward
replay, tour-level matches only (7 Oct 2026). Writes nothing.

    python3 tools/tennis_bands.py              ratings fed with qualifying/Challenger/ITF too
    python3 tools/tennis_bands.py --tour-only  tour-level files only (the old pool)

Constants are chosen on 2025 (tune_tennis), the shrink on 2025 log loss, and
the bands read on both years; 2026 was never used to choose anything."""
import argparse, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune_tennis as T

EDGES = (0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85)
SHRINKS = (0.8, 0.85, 0.9, 0.95, 1.0)


def walk(matches, sw, kb, rw):
    """(year, p of the favourite, favourite won, min matches) per tour-level match, pre-match."""
    overall, surf, n, out = {}, {}, {}, []
    for m in matches:
        w, l, s = m["winner"], m["loser"], m["surface"]
        ow, ol = overall.setdefault(w, 1500.0), overall.setdefault(l, 1500.0)
        sW, sL = surf.setdefault((w, s), 1500.0), surf.setdefault((l, s), 1500.0)
        p = 1 / (1 + 10 ** ((((1 - sw) * ol + sw * sL) - ((1 - sw) * ow + sw * sW)) / 400))
        nw, nl = n.get(w, 0), n.get(l, 0)
        if not m.get("below"):
            # ranks of the favourite and the other player, at the time
            rk = lambda x: int(x) if (x or "").isdigit() else None
            rw_, rl_ = rk(m.get("w_rank")), rk(m.get("l_rank"))
            fav, opp = (rw_, rl_) if p > 0.5 else (rl_, rw_)
            out.append((m["date"][:4], max(p, 1 - p), p > 0.5, min(nw, nl), fav, opp))
        kw, kl = T.dynamic_k(nw, kb), T.dynamic_k(nl, kb)
        wt = rw if m["retired"] else 1.0
        e = 1 / (1 + 10 ** ((ol - ow) / 400)); overall[w] = ow + kw * wt * (1 - e); overall[l] = ol - kl * wt * (1 - e)
        e = 1 / (1 + 10 ** ((sL - sW) / 400)); surf[(w, s)] = sW + kw * wt * (1 - e); surf[(l, s)] = sL - kl * wt * (1 - e)
        n[w], n[l] = nw + 1, nl + 1
    return out


def bands(rows, shrink, min_matches=0):
    out = []
    for lo in EDGES:
        sel = [(0.5 + (p - 0.5) * shrink, h) for _, p, h, mm, *_ in rows if 0.5 + (p - 0.5) * shrink >= lo and mm >= min_matches]
        if sel:
            out.append({"from": lo, "hit": round(sum(h for _, h in sel) / len(sel), 4), "n": len(sel),
                        "quoted": round(sum(q for q, _ in sel) / len(sel), 4)})
    return out


def logloss(rows, shrink):
    return sum(-math.log(0.5 + (p - 0.5) * shrink if h else 1 - (0.5 + (p - 0.5) * shrink)) for _, p, h, *_ in rows) / len(rows)


CAP = 151


def _x(q, fav, opp):
    if not fav and not opp:
        return None
    rf, ro = min(fav or CAP, CAP), min(opp or CAP, CAP)
    return (1.0, math.log(q / (1 - q)), math.log(ro / rf))


def fit_logistic(xs, ys, iters=25):
    """Three weights by Newton's method (standard library)."""
    w = [0.0, 1.0, 0.0]
    for _ in range(iters):
        g = [0.0] * 3; H = [[0.0] * 3 for _ in range(3)]
        for x, y in zip(xs, ys):
            z = max(-30.0, min(30.0, sum(a * b for a, b in zip(w, x)))); pr = 1 / (1 + math.exp(-z))
            for i in range(3):
                g[i] += (y - pr) * x[i]
                for j in range(3): H[i][j] -= pr * (1 - pr) * x[i] * x[j]
        # solve H d = -g (3x3, Gaussian elimination)
        A = [H[i][:] + [-g[i]] for i in range(3)]
        for i in range(3):
            piv = max(range(i, 3), key=lambda r: abs(A[r][i])); A[i], A[piv] = A[piv], A[i]
            for r in range(3):
                if r != i:
                    f = A[r][i] / A[i][i]
                    A[r] = [a - f * b for a, b in zip(A[r], A[i])]
        w = [w[i] + A[i][3] / A[i][i] for i in range(3)]
    return w


def rank_test(y25, y26, shrink):
    """The ATP ranking layer (rankings.adjust_atp) refitted on 2025 over these
    ratings, judged on 2026 against the Elo number alone."""
    def rows(rs):
        out = []
        for _, p, h, mm, fav, opp in rs:
            q = 0.5 + (p - 0.5) * shrink
            x = _x(q, fav, opp)
            out.append((q, x, 1 if h else 0, mm))
        return out
    tr, te = rows(y25), rows(y26)
    w = fit_logistic([x for _, x, _, _ in tr if x], [y for _, x, y, _ in tr if x])
    sig = lambda z: 1 / (1 + math.exp(-max(-30.0, min(30.0, z))))
    adj = lambda q, x: sig(sum(a * b for a, b in zip(w, x))) if x else q
    base = [-math.log(q if y else 1 - q) for q, x, y, _ in te]
    new = [-math.log(adj(q, x) if y else 1 - adj(q, x)) for q, x, y, _ in te]
    mu, pw = T.paired(new, base)
    ranked_rows = [(None, adj(q, x), y == 1, mm, None, None) for q, x, y, mm in te]
    return w, mu, pw, ranked_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tour-only", action="store_true")
    ap.add_argument("--best", action="store_true", help="the shrink with the best 2025 log loss, not the live one")
    ap.add_argument("--cache", default=os.path.join(T.HERE, ".tenniscache"))
    a = ap.parse_args()
    for tour in ("atp", "wta"):
        m = T.load_tour(tour, a.cache, extra=not a.tour_only)
        v, _, c = T.tune_and_validate(m, False, tour.upper())
        rows = walk(m, c["surfaceWeight"], c["kBase"], c["retirementWeight"])
        y25, y26 = [r for r in rows if r[0] == "2025"], [r for r in rows if r[0] == "2026"]
        best = min(SHRINKS, key=lambda s: logloss(y25, s))
        # the live shrink (build_tennis.CONFIDENCE_SHRINK) unless --best
        import build_tennis as BT
        shrink = best if a.best else BT.CONFIDENCE_SHRINK[tour]
        print(f"{tour}: constants {c}; shrink {shrink}, 2025 best {best} (2025 log loss "
              + ", ".join(f"{s}: {logloss(y25, s):.4f}" for s in SHRINKS) + ")")
        print(f"  2026 log loss {logloss(y26, shrink):.4f}, accuracy {sum(r[2] for r in y26) / len(y26):.4f}")
        for yr, rs in (("2025", y25), ("2026", y26)):
            print(f"  {yr} bands (10+ matches each):", bands(rs, shrink, 10))
        print(f"  2026 bands (all):", bands(y26, shrink))
        if tour == "atp":
            w, mu, pw, rr = rank_test(y25, y26, shrink)
            print(f"  ATP ranking layer refitted on 2025: w={[round(x, 4) for x in w]}; 2026 {mu:+.4f} log loss, p(worse) {pw:.3f}")
            print("  2026 ranked bands:", bands([r[:2] + (r[2], 99, None, None) for r in rr], 1.0))
            r25 = rank_test(y25, y25, shrink)[3]
            print("  2025 ranked bands (in-sample):", bands([r[:2] + (r[2], 99, None, None) for r in r25], 1.0))


if __name__ == "__main__":
    main()
