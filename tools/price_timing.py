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
  bySport  timing and books for each sport apart (9 Nov 2026, issue #156):
           the Card is mostly tennis and NBA, football a leg at most, and a
           book that is best on football says nothing about the rest.
The first price is the first real bookmaker price: the row's own, or its
`priced` block when the leg was archived before any book priced it (9 Nov
2026, #159); `pricedAt` in that block dates the first price for `hours`.
Writes price-timing.json with --json FILE. Standard library only.
"""
import glob, gzip, json, os, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G
import card_replay as CR

MIN_BOOK = 10    # a book needs this many priced legs before it is ranked


def legs(pool_dir=os.path.join(HERE, "groupings-archive")):
    out = []
    for f in sorted(glob.glob(os.path.join(pool_dir, "pool-*.json.gz"))):
        d = json.load(gzip.open(f))
        for row in d.get("legs", []):
            mk = CR.pool_market(row)
            if mk is None or not row.get("lastOdds"): continue
            l = dict(row, **mk, est=False)
            if G.card_fault(dict(l)) is not None and G.card_fault(dict(l), wide=True) is not None: continue
            l["firstPriceAt"] = (row.get("priced") or {}).get("at") or row.get("firstAt") or row.get("pricedAt")
            out.append(l)
    return out


def timing(L):
    mv = [l["lastOdds"] / l["odds"] - 1 for l in L]
    return {"n": len(L), "drifted": sum(m > 0.005 for m in mv), "shortened": sum(m < -0.005 for m in mv), "unchanged": sum(abs(m) <= 0.005 for m in mv),
            "meanMovePct": round(sum(mv) / len(mv) * 100, 2),
            "read": "take the price late" if sum(mv) > 0 else "take the price when published"}


def book_table(L, min_n=MIN_BOOK):
    books = defaultdict(lambda: {"n": 0, "vsAvgPct": 0.0, "best": 0})
    for l in L:
        bo = l.get("bookOdds") or {}
        if not bo: continue
        top = max(bo.values())
        for b, o in bo.items():
            books[b]["n"] += 1; books[b]["vsAvgPct"] += (o / l["odds"] - 1) * 100; books[b]["best"] += o >= top - 1e-9
    return {b: {"n": v["n"], "vsAvgPct": round(v["vsAvgPct"] / v["n"], 2), "bestShare": round(v["best"] / v["n"], 2)} for b, v in books.items() if v["n"] >= min_n}


def report(L):
    rep = {"legs": len(L)}
    if not L: return rep
    rep["timing"] = timing(L)
    rep["books"] = book_table(L)
    hours = defaultdict(list)
    for l in L:
        fa = l.get("firstPriceAt")
        if fa: hours[fa[11:13]].append(l["lastOdds"] / l["odds"] - 1)
    rep["hours"] = {h: {"n": len(v), "meanMovePct": round(sum(v) / len(v) * 100, 2)} for h, v in sorted(hours.items())}
    by = defaultdict(list)
    for l in L: by[l.get("sport") or "?"].append(l)
    rep["bySport"] = {s: {"timing": timing(v), "books": book_table(v)} for s, v in sorted(by.items(), key=lambda kv: -len(kv[1]))}
    return rep


def main():
    rep = report(legs())
    print(json.dumps(rep, indent=1))
    if "--json" in sys.argv: json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
