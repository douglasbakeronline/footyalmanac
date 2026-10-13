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

CLAY = ("roland garros", "estoril", "gstaad", "umag", "nordea open", "kitzb", "hamburg", "palermo",
        "prague", "iasi", "ljubljana", "makarska", "puglie", "brescia", "tolentino", "lisboa",
        "porto", "samsun", "montreux", "warsaw", "eugenio fontana", "antalya", "adana",
        "generali open")
GRASS = ("wimbledon", "boss open", "mallorca", "ilkley", "nottingham", "birmingham", "eastbourne",
         "libéma", "terra wortmann", "hsbc championships", "bad homburg")


def surface(r):
    t = (r.get("tournament") or "").lower()
    if any(k in t for k in GRASS):
        return "Grass"
    if any(k in t for k in CLAY):
        return "Clay"
    return "Hard"


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
        rows.append({**r, "a": a, "b": b, "w": w, "l": b if w == a else a, "surf": surface(r), "surfH": "Hard"})
    rows.sort(key=lambda r: (r["date"], r["time"] or ""))
    days = sorted({r["date"] for r in rows})
    by_day = defaultdict(list)
    for r in rows:
        by_day[r["date"]].append(r)

    def price(pool, r, key="surf"):
        return BT.dampen(BT.price_match(pool[r["a"]], pool[r["b"]], r[key], sw), shrink)

    out = []
    poolB = copy.deepcopy(base)   # all hard, as production
    poolD = copy.deepcopy(base)   # named surface, priced and updated
    for d in days:
        for r in by_day[d]:
            qual = "qualif" in (r.get("round") or "").lower()
            nmin = min(poolB[r["a"]].get("matches", 0), poolB[r["b"]].get("matches", 0))
            out.append({"date": d, "y": 1 if r["w"] == r["a"] else 0,
                        "pB": price(poolB, r, "surfH"), "pD": price(poolD, r), "surf": r["surf"],
                        "qual": qual, "nmin": nmin, "t": r["tournament"]})
        for r in by_day[d]:
            BT.apply_result(poolB, r["w"], r["l"], "Hard", kb)
            BT.apply_result(poolD, r["w"], r["l"], r["surf"], kb)
    return out, {"archiveLast": last, "applied": len(rows), "dupSkipped": dup, "unmatched": unmatched}



def ll(p, y):
    q = p if y else 1 - p
    return -math.log(max(q, 1e-12))


def bar(rows, key, lo=0.75):
    sel = [r for r in rows if max(r[key], 1 - r[key]) >= lo and not r["qual"] and r["nmin"] >= 10]
    return len(sel), (sum(1 for r in sel if (r[key] >= 0.5) == (r["y"] == 1)) / len(sel) if sel else None)


for tour in ("atp", "wta"):
    rows, meta = run(tour)
    print(f"\n=== {tour.upper()} {meta}")
    cuts = [("all", rows), ("Jun-Jul", [r for r in rows if r["date"] < "2026-08-01"]),
            ("Aug-Oct", [r for r in rows if r["date"] >= "2026-08-01"]),
            ("clay events", [r for r in rows if r["surf"] == "Clay"]),
            ("grass events", [r for r in rows if r["surf"] == "Grass"]),
            ("hard events", [r for r in rows if r["surf"] == "Hard"])]
    for label, sel in cuts:
        if len(sel) < 30:
            continue
        lb = sum(ll(r["pB"], r["y"]) for r in sel) / len(sel)
        ld = sum(ll(r["pD"], r["y"]) for r in sel) / len(sel)
        m, sd, pw = paired([ll(r["pD"], r["y"]) for r in sel], [ll(r["pB"], r["y"]) for r in sel])
        print(f"  {label:12} n {len(sel):5}  hard {lb:.4f}  named {ld:.4f}  D-B {m:+.4f} sd {sd:.4f} p(worse) {pw:.3f}  "
              f"75%+ md: hard {bar(sel,'pB')}  named {bar(sel,'pD')}")
