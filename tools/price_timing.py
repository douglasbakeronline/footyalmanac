#!/usr/bin/env python3
"""
Where and when the Card's legs get their best price (9 Nov 2026). Advisory.

From the pool archives (groupings-archive/pool-<date>.json.gz: first price
as published, last price before the start, every UK book's price):
  timing   first price v last pre-start price on legs that pass the Card's
           rule: how often the price shortened or drifted, and the mean move.
           A mean drift (last > first) says take the price late; a mean
           shortening says take it when published.
  books    for the same legs, each UK bookmaker's price against the average
           and how often it was the best: the book to write the Card for.
  hours    the first-price hour of day (UTC) v the move to the start.
Writes price-timing.json with --json FILE. Standard library only.
"""
import glob, gzip, json, os, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import groupings as G


def legs():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "groupings-archive", "pool-*.json.gz"))):
        d = json.load(gzip.open(f))
        for l in d.get("legs", []):
            if l.get("est") or not l.get("odds") or not l.get("lastOdds"): continue
            if G.card_fault(dict(l)) is not None and G.card_fault(dict(l), wide=True) is not None: continue
            out.append(l)
    return out


def main():
    L = legs()
    rep = {"legs": len(L)}
    if L:
        mv = [l["lastOdds"] / l["odds"] - 1 for l in L]
        rep["timing"] = {"drifted": sum(m > 0.005 for m in mv), "shortened": sum(m < -0.005 for m in mv), "unchanged": sum(abs(m) <= 0.005 for m in mv),
                         "meanMovePct": round(sum(mv) / len(mv) * 100, 2),
                         "read": "take the price late" if sum(mv) > 0 else "take the price when published"}
        books = defaultdict(lambda: {"n": 0, "vsAvgPct": 0.0, "best": 0})
        for l in L:
            bo = l.get("bookOdds") or {}
            if not bo: continue
            top = max(bo.values())
            for b, o in bo.items():
                books[b]["n"] += 1; books[b]["vsAvgPct"] += (o / l["odds"] - 1) * 100; books[b]["best"] += o >= top - 1e-9
        rep["books"] = {b: {"n": v["n"], "vsAvgPct": round(v["vsAvgPct"] / v["n"], 2), "bestShare": round(v["best"] / v["n"], 2)} for b, v in books.items() if v["n"] >= 10}
        hours = defaultdict(list)
        for l, m in zip(L, mv):
            fa = l.get("firstAt") or l.get("pricedAt")
            if fa: hours[fa[11:13]].append(m)
        rep["hours"] = {h: {"n": len(v), "meanMovePct": round(sum(v) / len(v) * 100, 2)} for h, v in sorted(hours.items())}
    print(json.dumps(rep, indent=1))
    if "--json" in sys.argv: json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
