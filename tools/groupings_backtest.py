#!/usr/bin/env python3
"""
Replay of the Odds tab group rules on past football days (advisory, writes nothing).

    python3 tools/groupings_backtest.py

Limits, stated plainly: record.json keeps each graded game's calibrated
confidence and result, but not the tested rate shown that day nor any bookmaker
price. So a leg here is a football pick (no draw, not Celtic-flagged) with
confidence >= MIN_HIT, its stated chance is that confidence, and its price is
the fair price 1 / confidence (the Odds tab's own "estimate" rule). Every game
is also bucketed, so it tests the band and spread rules, not the live prices.
Uses groupings.best() unchanged, with the estimate cap lifted (all legs are
estimates here).
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import groupings as G

def day_legs(day):
    out = []
    for i, g in enumerate(day["games"]):
        if g.get("celtic") or g.get("pick") == "d" or not g.get("result"): continue
        p = g["confidence"]
        if p < G.MIN_HIT: continue
        out.append({"sport": "football", "event": f"{day['date']}-{i}", "comp": g["league"], "when": "2000-01-01T00:00:00Z",
                    "pick": g["pick"], "p": p, "pModel": p, "odds": round(1 / p, 2), "est": True,
                    "implied": p, "edge": 0.0, "won": g["actual"] == g["pick"]})
    return out

def run(mutate=None):
    rec = json.load(open(os.path.join(G.HERE, "record.json")))
    rows = []
    for day in rec["days"]:
        L = day_legs(day)
        if mutate: L = mutate(L)
        used = set()
        for rank in ("main", "alternative"):
            for name, lo, hi in G.BANDS:
                g = G._best(L, used, G.datetime(1970,1,1,tzinfo=G.timezone.utc), name, lo, hi, 5) if L else None
                if not g: continue
                used |= {l["event"] for l in g["legs"]}
                won = all(next(x for x in L if x["event"] == l["event"])["won"] for l in g["legs"])
                rows.append((name, rank, g["p"], g["odds"], won, day["date"]))
    return rows

def report(rows):
    print(f"{'band':9}{'rank':13}{'n':>4}{'won':>5}{'stated':>8}{'actual':>8}{'return':>8}")
    for name in [b[0] for b in G.BANDS] + ["all"]:
        for rank in ("main", "alternative", "both"):
            r = [x for x in rows if (name == "all" or x[0] == name) and (rank == "both" or x[1] == rank)]
            if not r: continue
            w = sum(x[4] for x in r)
            ret = sum(x[3] for x in r if x[4]) / len(r)
            print(f"{name:9}{rank:13}{len(r):>4}{w:>5}{sum(x[2] for x in r)/len(r):>8.3f}{w/len(r):>8.3f}{ret:>8.2f}")

if __name__ == "__main__":
    report(run())
