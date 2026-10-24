#!/usr/bin/env python3
"""
Model against market on the live archive. Advisory only: changes nothing,
fits nothing, writes nothing. 24 Oct 2026, after a day of slips where most
losses were draws and the model's "value" legs lost.

    python3 tools/market_check.py

Joins every archived football prediction that carried a bookmaker price
(predictions/<date>.json "market", published before kick-off; the latest such
copy of each fixture) to its graded result (record-graded.json), then reports:

  1. log loss: the model, the market, and blends of the two, with a paired
     bootstrap of the model against a 50/50 blend
  2. pick landing by how far the model sits above the market on its side
  3. pick landing by draw share, at a fixed win chance (does a high draw
     chance make a pick land less than its quote?)
  4. clean legs priced 1.30-1.90, the Multiplier range (groupings.py): landed
     against fair, profit per unit at the average price, with intervals

Rule 1 still holds: nothing here is fitted on the record. It is the
scoreboard read to decide whether a rule is worth proposing.
Standard library only.
"""
import glob, json, math, os, random, re, sys, unicodedata

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = {"h": 0, "d": 1, "a": 2}
CLEAN_WHY = (None, "below")


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def rows():
    res = {}
    with open(os.path.join(HERE, "record-graded.json")) as f:
        for g in json.load(f).get("graded") or []:
            if g.get("result") and g.get("verified") != "late":
                res[(g["date"], norm(g["home"]), norm(g["away"]))] = g
    keep = {}
    for path in sorted(glob.glob(os.path.join(HERE, "predictions", "*.json"))):
        with open(path) as f:
            for x in json.load(f):
                k = (x.get("date"), norm(x.get("home")), norm(x.get("away")))
                if k not in res or not x.get("market") or not (x["market"].get("avg") and x["market"].get("p")):
                    continue
                ko, pub = x.get("kickoff") or "", x.get("published") or ""
                if pub and ko and pub > ko:
                    continue
                keep[k] = x
    out = []
    for k, x in keep.items():
        h, a = res[k]["result"]
        out.append(dict(x, actual="h" if h > a else "a" if a > h else "d"))
    return out


def ll(p, a): return -math.log(max(p[IDX[a]], 1e-9))


def boot(xs, n=4000, seed=1):
    rnd = random.Random(seed)
    m = sorted(sum(rnd.choice(xs) for _ in xs) / len(xs) for _ in range(n))
    return m[int(n * 0.05)], m[int(n * 0.95)]


def main():
    R = rows()
    if not R:
        print("no archived predictions with a market price and a result"); return
    print(f"{len(R)} fixtures with a pre-kick-off price and a result, "
          f"{min(r['date'] for r in R)} to {max(r['date'] for r in R)}\n")
    mp = lambda r: [r["p"]["h"], r["p"]["d"], r["p"]["a"]]
    print("1. Log loss (lower is better)")
    for w in (0, 0.25, 0.5, 0.75, 1):
        L = [ll([(1 - w) * m + w * k for m, k in zip(mp(r), r["market"]["p"])], r["actual"]) for r in R]
        print(f"   {int(w * 100):3}% market  {sum(L) / len(L):.4f}")
    d = [ll(mp(r), r["actual"]) - ll([.5 * m + .5 * k for m, k in zip(mp(r), r["market"]["p"])], r["actual"]) for r in R]
    lo, hi = boot(d)
    print(f"   model minus 50/50 blend {sum(d) / len(d):+.4f} (90% {lo:+.4f} to {hi:+.4f}; positive = blend better)\n")

    picks = []
    for r in R:
        p = r["p"]; s = max(("h", "a"), key=lambda k: p[k])
        avg = r["market"]["avg"]; m = sum(1 / x for x in avg)
        fair = 1 / avg[IDX[s]] / m
        picks.append({"model": p[s], "fair": fair, "odds": avg[IDX[s]], "won": r["actual"] == s, "draw": p["d"],
                      "clean": not r.get("celtic") and not r.get("unrated") and r.get("why") in CLEAN_WHY})
    print("2. Picks (model 50%+) by the model's lead over the market on its side")
    for lo_, hi_ in [(-1, -.05), (-.05, 0), (0, .05), (.05, .10), (.10, 1)]:
        S = [x for x in picks if lo_ <= x["model"] - x["fair"] < hi_ and x["model"] >= .5]
        if S:
            print(f"   {lo_:+.2f} to {hi_:+.2f}  n={len(S):4}  model {sum(x['model'] for x in S) / len(S):.3f}  "
                  f"market {sum(x['fair'] for x in S) / len(S):.3f}  landed {sum(x['won'] for x in S) / len(S):.3f}")
    print("\n3. Picks at 50-70% by draw share (landed against quoted)")
    S = [x for x in picks if .5 <= x["model"] < .7]
    for lo_, hi_ in [(0, .20), (.20, .24), (.24, 1)]:
        T = [x for x in S if lo_ <= x["draw"] < hi_]
        if T:
            print(f"   draw {lo_:.2f}-{hi_:.2f}  n={len(T):4}  model {sum(x['model'] for x in T) / len(T):.3f}  "
                  f"landed {sum(x['won'] for x in T) / len(T):.3f}")
    print("\n4. Clean legs priced 1.30-1.90, the market 45%+, model no more than 5 points above it")
    T = [x for x in picks if x["clean"] and 1.30 <= x["odds"] <= 1.90 and x["fair"] >= .45
         and x["model"] - x["fair"] <= .05 and x["model"] >= .40]
    if T:
        prof = [(x["odds"] if x["won"] else 0) - 1 for x in T]
        gap = [x["won"] - x["fair"] for x in T]
        print(f"   n={len(T)}  fair {sum(x['fair'] for x in T) / len(T):.3f}  landed {sum(x['won'] for x in T) / len(T):.3f}  "
              f"average price {sum(x['odds'] for x in T) / len(T):.2f}")
        a, b = boot(gap); print(f"   landed minus fair {sum(gap) / len(gap):+.3f} (90% {a:+.3f} to {b:+.3f})")
        a, b = boot(prof); print(f"   profit per unit {sum(prof) / len(prof):+.3f} (90% {a:+.3f} to {b:+.3f})")


if __name__ == "__main__":
    sys.exit(main())
