#!/usr/bin/env python3
"""
The green Edge flag tested on every sport (10 Nov 2026, Douglas: "test and
run on all sports"). Advisory: changes nothing, fits nothing.

    python3 tools/edge_sports.py [--recover] [--closing] [--json out.json]

The flag (groupings.edge_flag) is football only: its one tested condition,
the opposition priced 9+, is about how much of a three-way market the draw
takes, and only football-data.co.uk has seasons of prices to test it on. For
the other sports the only bookmaker prices on file are the archived pool
(groupings-archive/pool-*.json.gz, every sport, from 30 Oct 2026). This
reads every settled pool leg at its first real price (tools/card_replay.py's
reader; --recover admits legs archived before 10 Nov at their last price,
approximate) and, for each sport, where the model's pick is also the
bookmakers' favourite:

  - landed against the bookmakers' chance, return at the average and best
    price, z and a day-bootstrap p(return <= 0), overall and by price band,
    by the model's gap to the market, and by the opposition's price;
  - the pre-registered candidate flag for a sport without a draw: the
    football flag's other conditions (price CARD_ODDS, the bookmakers
    CARD_FAIR_MIN+, the model no more than MULT_ABOVE_BOOK above them), and
    for football the live flag itself;
  - a second candidate registered on the first read (10 Nov 2026): the short
    favourite at 1.15 to 1.30 (SHORT), the band above the bookmakers in most
    sports that day; and both candidates over every sport together.

A sport earns the flag only when its candidate passes the gate (GATE): 100+
legs, landed above the bookmakers' chance, a positive return at the best
price with p(return <= 0) at most 0.30, on the pool's first real prices.
The tool reports which sports pass; switching one on is a code change with
its numbers. Rule 1 holds: the pool is read, never fitted. Standard library.
"""
import json, math, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G

GATE = {"legs": 100, "pLoss": 0.30}
PRICE_BANDS = [(1.0, 1.15), (1.15, 1.30), (1.30, 1.50), (1.50, 1.90), (1.90, 99.0)]
GAP_BANDS = [("model 5+ above", 0.05, 9), ("near (within 5)", -0.05, 0.05), ("model 5-10 under", -0.10, -0.05), ("model 10+ under", -9, -0.10)]
OPP_BANDS = [(1.0, 4.0), (4.0, 6.0), (6.0, 9.0), (9.0, 999.0)]


def summary(legs, seed=7):
    """n, landed, quoted (the bookmakers' chance), return at average and best
    price per unit, z, and a bootstrap over days of p(return <= 0)."""
    if not legs: return {"n": 0}
    n = len(legs); w = sum(l["won"] for l in legs); q = sum(l["fair"] for l in legs)
    var = sum(l["fair"] * (1 - l["fair"]) for l in legs)
    ret = sum(l["odds"] for l in legs if l["won"]) / n - 1
    best = sum(max(l.get("best") or l["odds"], l["odds"]) for l in legs if l["won"]) / n - 1
    by = defaultdict(list)
    for l in legs: by[l["day"]].append(l)
    days = list(by); rnd = random.Random(seed); vals = []
    for _ in range(2000):
        pick = [l for _ in days for l in by[rnd.choice(days)]]
        vals.append(sum(l["odds"] for l in pick if l["won"]) / len(pick) - 1 if pick else 0)
    return {"n": n, "landed": round(w / n, 3), "quoted": round(q / n, 3), "z": round((w - q) / math.sqrt(var), 2) if var else None,
            "return": round(ret, 3), "returnBest": round(best, 3), "pLoss": round(sum(v <= 0 for v in vals) / len(vals), 3),
            "avgOdds": round(sum(l["odds"] for l in legs) / n, 2)}


def candidate(l):
    """The flag's conditions other than the opposition's price."""
    return (G.CARD_ODDS[0] <= l["odds"] <= G.CARD_ODDS[1] and l["fair"] >= G.CARD_FAIR_MIN
            and l["pModel"] - l["fair"] <= G.MULT_ABOVE_BOOK)


SHORT = (1.15, 1.30)

def short(l):
    """The pre-registered second candidate (10 Nov 2026): the short favourite,
    1.15 to 1.30, the bookmakers' chance and the model's gap as the flag."""
    return SHORT[0] <= l["odds"] < SHORT[1] and l["pModel"] - l["fair"] <= G.MULT_ABOVE_BOOK


def live_flag(l):
    """The live flag on a pool leg (football): the candidate, a tested league,
    clean, and the opposition priced CARD_OPP_MIN+."""
    omin = G.CARD_OPP_MIN.get("football")
    return (l["sport"] == "football" and candidate(l) and l.get("code") in G.edge_leagues()
            and l.get("why") in G.CLEAN_WHY and bool(l.get("opp")) and l["opp"] >= omin)


def passes(s):
    return bool(s.get("n", 0) >= GATE["legs"] and s["landed"] > s["quoted"] and s["returnBest"] > 0 and s["pLoss"] <= GATE["pLoss"])


def favourites(by):
    """Settled pool legs where the model's pick is the bookmakers' favourite
    (its price is shorter than the other side's)."""
    out = []
    for d, ls in by.items():
        for l in ls:
            if l.get("fair") is None or not l.get("odds"): continue
            if l.get("opp") and l["opp"] < l["odds"]: continue
            out.append(dict(l, day=d))
    return out


def report(legs):
    rep = {}
    for sp in sorted({l["sport"] for l in legs}):
        L = [l for l in legs if l["sport"] == sp]
        r = {"all": summary(L), "byPrice": {}, "byGap": {}, "byOpp": {}}
        for lo, hi in PRICE_BANDS:
            s = summary([l for l in L if lo <= l["odds"] < hi])
            if s["n"]: r["byPrice"][f"{lo:.2f}-{hi:.2f}"] = s
        for name, lo, hi in GAP_BANDS:
            s = summary([l for l in L if lo <= l["pModel"] - l["fair"] < hi])
            if s["n"]: r["byGap"][name] = s
        for lo, hi in OPP_BANDS:
            s = summary([l for l in L if l.get("opp") and lo <= l["opp"] < hi])
            if s["n"]: r["byOpp"][f"opp {lo:g}-{hi:g}"] = s
        r["candidate"] = summary([l for l in L if candidate(l)])
        r["candidatePasses"] = passes(r["candidate"])
        # 10 Nov 2026, pre-registered on the first read: the short favourite
        # (1.15-1.30) was the one band above the bookmakers in most sports
        r["short"] = summary([l for l in L if short(l)])
        r["shortPasses"] = passes(r["short"])
        if sp == "football":
            r["liveFlag"] = summary([l for l in L if live_flag(l)])
        rep[sp] = r
    rep["_all"] = {"candidate": summary([l for l in legs if candidate(l)]), "short": summary([l for l in legs if short(l)])}
    rep["_all"]["candidatePasses"] = passes(rep["_all"]["candidate"]); rep["_all"]["shortPasses"] = passes(rep["_all"]["short"])
    return rep


def line(label, s):
    if not s.get("n"): return f"  {label:22s} none"
    return (f"  {label:22s} n {s['n']:4d}  landed {s['landed'] * 100:5.1f}% v bookies {s['quoted'] * 100:5.1f}%  z {s['z']:+5.2f}  "
            f"avg {s['avgOdds']:.2f}  return {s['return'] * 100:+6.1f}%  best {s['returnBest'] * 100:+6.1f}%  p(loss) {s['pLoss']:.2f}")


def main():
    import card_replay as CR
    recover, closing = "--recover" in sys.argv, "--closing" in sys.argv
    by, skipped = CR.pool_legs(recover=recover, closing=closing)
    legs = favourites(by)
    rep = report(legs)
    print(f"Pool from {CR.POOL_FROM}: {len(legs)} settled favourite legs over {len(by)} days"
          f"{' (recover: legs before 10 Nov at their last price)' if recover else ''}{' at closing prices' if closing else ''}")
    for sp, r in rep.items():
        if sp == "_all": continue
        print(f"\n{sp.upper()}")
        print(line("all favourites", r["all"]))
        for k, s in r["byPrice"].items(): print(line(f"price {k}", s))
        for k, s in r["byGap"].items(): print(line(k, s))
        for k, s in r["byOpp"].items(): print(line(k, s))
        print(line("candidate flag", r["candidate"]) + ("   PASSES the gate" if r["candidatePasses"] else ""))
        print(line("short 1.15-1.30", r["short"]) + ("   PASSES the gate" if r["shortPasses"] else ""))
        if "liveFlag" in r: print(line("live flag (football)", r["liveFlag"]))
    a = rep["_all"]
    print("\nALL SPORTS TOGETHER")
    print(line("candidate flag", a["candidate"]) + ("   PASSES the gate" if a["candidatePasses"] else ""))
    print(line("short 1.15-1.30", a["short"]) + ("   PASSES the gate" if a["shortPasses"] else ""))
    passing = [f"{sp} {k}" for sp, r in rep.items() for k in ("candidate", "short") if r.get(k + "Passes")]
    print(f"\nGate: {GATE['legs']}+ legs, landed above the bookmakers, best-price return positive, p(loss) <= {GATE['pLoss']}. "
          f"Passing: {', '.join(passing) or 'none'}.")
    out = {"recover": recover, "closing": closing, "legs": len(legs), "gate": GATE, "sports": rep, "passing": passing}
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as f: json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    main()
