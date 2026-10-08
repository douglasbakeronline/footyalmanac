#!/usr/bin/env python3
"""Advisory: what the tennis ratings lose by stopping at the archive's end
(8 Oct 2026, claude/tennis-ratings-gap-2026-10-08.md). Changes nothing.

    python3 tools/tennis_gap_eval.py [--cache .tenniscache]

Reads tennis.json, history-tennis/ and the Sackmann archive (cached).

A: production today. tennis.json (archive to ~1 Jun 2026) + the last 6 days
   of ESPN results before the match day.
B: tennis.json + every ESPN result since the archive ends, in date order.
C1: B with a more responsive Elo after the archive (k x1.5).
C2: B plus an in-tournament wins term, logit += beta * (wins_a - wins_b),
    beta fitted on Jun-Aug, checked on Sep-Oct.
Every match priced from results on earlier days only. Paired bootstrap.
"""
import copy, json, math, random, sys
from collections import defaultdict
from datetime import date, timedelta
import argparse, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build_tennis as BT
import tune_tennis as TT

ap = argparse.ArgumentParser()
ap.add_argument("--cache", default=os.path.join(ROOT, ".tenniscache"))
CACHE = ap.parse_args().cache
snap = json.load(open(os.path.join(ROOT, "tennis.json")))
espn = {t: [{**m, "completed": True} for m in BT.load_history(t)[0].values()] for t in ("atp", "wta")}

def surface(r):
    return "Hard"       # as build_tennis.py: ESPN carries no surface


def walkover(r):
    return BT.is_walkover(r)


def logit(p):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))


def sig(x):
    return 1 / (1 + math.exp(-x))


def paired(a, b, reps=2000, seed=11):
    rng = random.Random(seed)
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    ms = [sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    mu = sum(d) / n
    sd = (sum((m - mu) ** 2 for m in ms) / reps) ** 0.5
    return mu, sd, sum(1 for m in ms if m > 0) / reps


def run(tour):
    c = snap[tour]["constants"]
    kb, sw, shrink = c["kBase"], c["surfaceWeight"], BT.CONFIDENCE_SHRINK[tour]
    base = snap[tour]["ratings"]
    by_full, by_init = BT.build_index(base)
    # archive's last tournaments, to avoid applying their matches twice
    # the same boundary rule as build_tennis.results_to_apply
    arch = TT.load_tour(tour, CACHE)
    bnd = TT.archive_boundary(arch)
    last = bnd["through"]
    hi = (date.fromisoformat(last) + timedelta(days=BT.BOUNDARY_DAYS)).isoformat()
    recent_pairs = {frozenset(p) for p in bnd["pairs"]}
    rows, dup, unmatched = [], 0, 0
    for r in espn[tour]:
        if not (r["completed"] and r["winner"]) or walkover(r) or r["date"] < last:
            continue
        a = BT.match_player(r["p0"], by_full, by_init)
        b = BT.match_player(r["p1"], by_full, by_init)
        if not a or not b:
            unmatched += 1
            continue
        if r["date"] <= hi and frozenset((a, b)) in recent_pairs:
            dup += 1
            continue
        w = a if r["winner"] == r["p0"] else b
        rows.append({**r, "a": a, "b": b, "w": w, "l": b if w == a else a, "surf": surface(r)})
    rows.sort(key=lambda r: (r["date"], r["time"] or ""))
    days = sorted({r["date"] for r in rows})
    by_day = defaultdict(list)
    for r in rows:
        by_day[r["date"]].append(r)

    def price(pool, r):
        return BT.dampen(BT.price_match(pool[r["a"]], pool[r["b"]], r["surf"], sw), shrink)

    out = []
    poolB = copy.deepcopy(base)
    poolC = copy.deepcopy(base)
    wins = defaultdict(int)          # (tournament, player) -> wins so far
    for d in days:
        # A: snapshot + results from the 6 days before d
        poolA = copy.deepcopy(base)
        d0 = (date.fromisoformat(d) - timedelta(days=6)).isoformat()
        for dd in days:
            if d0 <= dd < d:
                for r in by_day[dd]:
                    BT.apply_result(poolA, r["w"], r["l"], r["surf"], kb)
        for r in by_day[d]:
            pA, pB, pC = price(poolA, r), price(poolB, r), price(poolC, r)
            y = 1 if r["w"] == r["a"] else 0
            tw = wins[(r["tournament"], r["a"])] - wins[(r["tournament"], r["b"])]
            qual = "qualif" in (r.get("round") or "").lower()
            nmin = min(poolB[r["a"]].get("matches", 0), poolB[r["b"]].get("matches", 0))
            out.append({"date": d, "y": y, "pA": pA, "pB": pB, "pC1": pC, "tw": tw,
                        "qual": qual, "nmin": nmin, "a": r["a"], "b": r["b"],
                        "t": r["tournament"], "round": r.get("round")})
        for r in by_day[d]:
            BT.apply_result(poolB, r["w"], r["l"], r["surf"], kb)
            BT.apply_result(poolC, r["w"], r["l"], r["surf"], kb * 1.5)
            wins[(r["tournament"], r["w"])] += 1
    return out, {"archiveLast": last, "applied": len(rows), "dupSkipped": dup, "unmatched": unmatched}


def ll(p, y):
    q = p if y else 1 - p
    return -math.log(max(q, 1e-12))


def summary(rows, key):
    l = [ll(r[key], r["y"]) for r in rows]
    acc = sum(1 for r in rows if (r[key] >= 0.5) == (r["y"] == 1)) / len(rows)
    return sum(l) / len(l), acc


def bar(rows, key, lo=0.75):
    sel = [r for r in rows if max(r[key], 1 - r[key]) >= lo and not r["qual"] and r["nmin"] >= 10]
    if not sel:
        return 0, None
    hit = sum(1 for r in sel if (r[key] >= 0.5) == (r["y"] == 1)) / len(sel)
    return len(sel), hit


for tour in ("atp", "wta"):
    rows, meta = run(tour)
    print(f"\n=== {tour.upper()}  {meta}  priced {len(rows)}")
    for label, sel in (("Jun-Jul", [r for r in rows if r["date"] < "2026-08-01"]),
                       ("Aug-Oct", [r for r in rows if r["date"] >= "2026-08-01"]),
                       ("Sep-Oct", [r for r in rows if r["date"] >= "2026-09-01"]),
                       ("all", rows)):
        if not sel:
            continue
        la, aa = summary(sel, "pA")
        lb, ab = summary(sel, "pB")
        lc, ac = summary(sel, "pC1")
        m, sd, pw = paired([ll(r["pB"], r["y"]) for r in sel], [ll(r["pA"], r["y"]) for r in sel])
        m1, sd1, pw1 = paired([ll(r["pC1"], r["y"]) for r in sel], [ll(r["pB"], r["y"]) for r in sel])
        nA, hA = bar(sel, "pA")
        nB, hB = bar(sel, "pB")
        print(f"  {label:8} n {len(sel):5}  A {la:.4f} {aa:.1%}  B {lb:.4f} {ab:.1%}  "
              f"B-A {m:+.4f} sd {sd:.4f} p(worse) {pw:.3f}  |  C1-B {m1:+.4f} p(worse) {pw1:.3f}  "
              f"|  75%+ main draw: A {nA} at {hA if hA is None else round(hA,3)}, B {nB} at {hB if hB is None else round(hB,3)}")
    # C2: in-tournament wins, beta fitted Jun-Aug on top of B, checked Sep-Oct
    fit = [r for r in rows if r["date"] < "2026-09-01"]
    chk = [r for r in rows if r["date"] >= "2026-09-01"]
    best = min((sum(ll(sig(logit(r["pB"]) + bt * r["tw"]), r["y"]) for r in fit) / len(fit), bt)
               for bt in [x / 100 for x in range(-30, 31, 2)])
    bt = best[1]
    pc2 = [sig(logit(r["pB"]) + bt * r["tw"]) for r in chk]
    m2, sd2, pw2 = paired([ll(p, r["y"]) for p, r in zip(pc2, chk)], [ll(r["pB"], r["y"]) for r in chk])
    print(f"  C2 in-tournament wins: beta {bt} fitted on {len(fit)}, check {len(chk)}: "
          f"{m2:+.4f} sd {sd2:.4f} p(worse) {pw2:.3f}")
    for r in rows:
        if "Bartunkova" in r["a"] + r["b"] and "Muchova" in r["a"] + r["b"]:
            fav = r["a"]
            print(f"  >> {r['date']} {r['a']} v {r['b']} ({r['round']}): P({fav}) A {r['pA']:.3f}  B {r['pB']:.3f}  "
                  f"C1 {r['pC1']:.3f}  tw {r['tw']}  won by {'a' if r['y'] else 'b'}")
