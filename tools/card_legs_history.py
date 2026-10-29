#!/usr/bin/env python3
"""
The Card's leg rule replayed on past seasons with football-data.co.uk prices.
Advisory, writes card-legs-history.json, changes nothing on the site.
29 Oct 2026, Douglas: "Why can't you grab data from last season and learn
that way?"

    python3 tools/card_legs_history.py            fit season (2025-26) and check season (2026-27 to date)
    python3 tools/card_legs_history.py --out FILE

The live Card (groupings.build_card) admits a football pick when the
bookmakers' fair chance is 60%+ at a price of 1.15 to 1.90, the league is a
core league, and the model's own number is at least 5 points UNDER the
market's. The evidence for that last cut is seven weeks of the live archive
(tools/market_check.py). This replays the same cut over whole seasons:

  model     the walk-forward replay's number for the pick, with the live
            calibration applied (odds.model_probs over tune.lambdas), so each
            number is what the site would have quoted that morning
  market    football-data's average price with the margin removed (odds.fair)
  result    the final result; a draw is a loss for a win pick

For each cut (under the market by 5+, near, above by 5+, and all 60%+) it
reports picks, landed, quoted, and singles return at the average and best
price with a bootstrap; by price band; and, for the under-market cut, the
closing-line value against the Pinnacle closing price where the file has it.
Then the simplest card: each day's three best under-market picks as one
treble (highest combined fair chance, combined price 2.0 to 3.0), won only
when all three win, with its return and the expected win rate.

football-data covers the main leagues of England, Scotland, Germany, Italy,
Spain, France, the Netherlands, Belgium, Portugal, Turkey and Greece
(odds.DIVS): most of the core leagues, not all. Rule 1 holds: nothing is
fitted here. Standard library only.
"""
import json, math, os, sys, time
from collections import defaultdict
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import engine as E, odds as O, groupings as G, tune

CUTS = {
    "all60": lambda m, f: True,
    "under5": lambda m, f: m <= f - G.CARD_UNDER_MARKET,
    "near": lambda m, f: abs(m - f) < G.CARD_UNDER_MARKET,
    "above5": lambda m, f: m >= f + G.CARD_UNDER_MARKET,
    "under8": lambda m, f: m <= f - 0.08,
}
BANDS = [(1.15, 1.35), (1.35, 1.55), (1.55, 1.75), (1.75, 1.91)]


def legs(pairs):
    """(model probs, price row) -> candidate legs passing the price gate."""
    out = []
    lo, hi = G.CARD_ODDS
    for mp, r in pairs:
        pick = max(range(3), key=lambda i: mp[i])
        if pick == 1: continue
        f = O.fair(r["avg"])[pick]; price = r["avg"][pick]
        if f < G.CARD_FAIR_MIN or not (lo <= price <= hi): continue
        bp = O.best(r)[pick]
        clv = (bp * O.fair(r["close"])[pick] - 1) if r.get("close") else None
        out.append({"date": r["date"], "code": r["code"], "home": r["home"], "away": r["away"], "side": "h" if pick == 0 else "a",
                    "time": r.get("time"), "model": mp[pick], "fair": f, "price": price, "best": bp, "margin": sum(1 / o for o in r["avg"]),
                    "won": r["result"] == pick, "clv": clv, "core": not r["code"].startswith("af.")})
    return out


def summary(L):
    n = len(L)
    if not n: return {"n": 0}
    w = sum(l["won"] for l in L); q = sum(l["fair"] for l in L)
    pnl = [(l["price"] - 1) if l["won"] else -1.0 for l in L]; pnlb = [(l["best"] - 1) if l["won"] else -1.0 for l in L]
    roi, p = O._boot(pnl); roib, pb = O._boot(pnlb)
    clv = [l["clv"] for l in L if l["clv"] is not None]; cm, cp = O._boot(clv) if clv else (None, None)
    bands = {}
    for lo, hi in BANDS:
        b = [l for l in L if lo <= l["price"] < hi]
        if b: bands[f"{lo:.2f}-{min(hi, 1.90):.2f}"] = {"n": len(b), "landed": round(sum(x["won"] for x in b) / len(b), 3), "quoted": round(sum(x["fair"] for x in b) / len(b), 3),
                                                       "roi": round(sum((x["price"] - 1) if x["won"] else -1 for x in b) / len(b), 4)}
    return {"n": n, "landed": round(w / n, 4), "quoted": round(q / n, 4), "gap": round((w - q) / n, 4), "se": round(math.sqrt(q / n * (1 - q / n) / n), 4),
            "roi": round(roi, 4), "pRoiNotPositive": round(p, 3), "roiBest": round(roib, 4), "pRoiBestNotPositive": round(pb, 3),
            "clvBets": len(clv), "clv": round(cm, 4) if cm is not None else None, "pClvNotPositive": round(cp, 3) if cp is not None else None,
            "bands": bands}


def trebles(L):
    """One treble a day from the under-market legs: the three with the highest
    combined fair chance whose combined price is 2.0 to 3.0."""
    by = defaultdict(list)
    for l in L: by[l["date"]].append(l)
    out = []
    import itertools
    for d, legs_ in by.items():
        if len(legs_) < 3: continue
        cands = sorted(legs_, key=lambda l: -l["fair"])[:12]
        top = None
        for c in itertools.combinations(cands, 3):
            o = math.prod(l["price"] for l in c)
            if not (2.0 <= o <= 3.0): continue
            p = math.prod(l["fair"] for l in c)
            if not top or p > top[0]: top = (p, o, c)
        if top:
            p, o, c = top
            out.append({"date": d, "p": p, "odds": o, "won": all(l["won"] for l in c)})
    if not out: return {"n": 0}
    n = len(out); w = sum(g["won"] for g in out); exp = sum(g["p"] for g in out)
    pnl = [(g["odds"] - 1) if g["won"] else -1.0 for g in out]; roi, p = O._boot(pnl)
    return {"n": n, "won": w, "landed": round(w / n, 3), "expected": round(exp / n, 3), "roi": round(roi, 4), "pRoiNotPositive": round(p, 3),
            "z": round((w - exp) / math.sqrt(sum(g["p"] * (1 - g["p"]) for g in out)), 2) if n else None}


def card_season(L):
    """The whole Card, as groupings.build_card builds it today, over a season
    of football-data legs: one window a day, Card 2x and 3x then a second of
    each, CARD_STAKE units, graded strictly. Returns the summary and the
    day-by-day running profit in units."""
    sys.path.insert(0, os.path.join(HERE, "tools"))
    import card_replay as CR
    by = defaultdict(list)
    for l in L:
        when = f"{l['date']}T{l['time'] or '15:00'}:00Z"
        leg = {"sport": "football", "event": f"{l['home']} v {l['away']}", "pick": l["home"] if l["side"] == "h" else l["away"],
               "comp": l["code"], "code": l["code"], "when": when, "date": l["date"], "odds": round(l["price"], 2), "best": round(l["best"], 2),
               "margin": round(l["margin"], 4), "est": False, "pModel": round(l["model"], 4), "p": round(l["model"], 4),
               "hit": 0.8, "n": 100, "won": l["won"], "core": l["core"]}
        G.honest(leg)
        slot = G.uk_slot(leg)
        if slot: by[slot[0]].append(leg)
    days, run, series, months = {}, 0.0, [], defaultdict(lambda: [0, 0, 0.0, 0.0])
    for d in sorted(by):
        gs = CR.build(by[d], d, "live")
        if not gs: continue
        days[d] = gs
        pnl = sum(g["stake"] * (g["odds"] - 1) if g["won"] else -g["stake"] for g in gs)
        run += pnl; series.append([d, round(run, 2)])
        m = months[d[:7]]; m[0] += len(gs); m[1] += sum(g["won"] for g in gs); m[2] += sum(g["stake"] for g in gs); m[3] += pnl
    gs = [g for d in days.values() for g in d]
    if not gs: return {"groups": 0}
    n, w = len(gs), sum(g["won"] for g in gs); exp = sum(g["p"] for g in gs)
    st_ = sum(g["stake"] for g in gs); ret = sum(g["stake"] * g["odds"] for g in gs if g["won"]); best = sum(g["stake"] * g["bestOdds"] for g in gs if g["won"])
    kinds = {}
    for name, _, _, _ in G.CARD_KINDS:
        k = [g for g in gs if g["name"] == name]
        if k:
            ks = sum(g["stake"] for g in k); kr = sum(g["stake"] * g["odds"] for g in k if g["won"])
            kinds[name] = {"n": len(k), "won": sum(g["won"] for g in k), "expected": round(sum(g["p"] for g in k) / len(k), 3), "return": round(kr / ks, 3)}
    # bootstrap over days for the return per unit
    import random
    random.seed(7); keys = list(days); vals = []
    for _ in range(2000):
        pick = [days[random.choice(keys)] for _ in keys]
        s_ = sum(g["stake"] for d in pick for g in d); r_ = sum(g["stake"] * g["odds"] for d in pick for g in d if g["won"])
        vals.append(r_ / s_ if s_ else 1)
    vals.sort()
    return {"days": len(days), "groups": n, "won": w, "expected": round(exp, 2), "landed": round(w / n, 3), "expectedRate": round(exp / n, 3),
            "z": round((w - exp) / math.sqrt(sum(g["p"] * (1 - g["p"]) for g in gs)), 2),
            "units": st_, "returned": round(ret, 2), "return": round(ret / st_, 3), "returnBest": round(best / st_, 3),
            "return90": [round(vals[100], 3), round(vals[1899], 3)], "pLoss": round(sum(v < 1 for v in vals) / len(vals), 3),
            "kinds": kinds, "months": {m: {"groups": v[0], "won": v[1], "units": v[2], "pnl": round(v[3], 2)} for m, v in sorted(months.items())},
            "series": series}


def main():
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "card-legs-history.json")
    log = []
    data = tune.load(None)
    report = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": "football-data.co.uk",
              "rule": {"fairMin": G.CARD_FAIR_MIN, "odds": G.CARD_ODDS, "underMarket": G.CARD_UNDER_MARKET}, "seasons": {}}
    for split in ("fit", "check"):
        preds = O.model_probs(tune.lambdas(data, split, meta=True))
        prices, season = [], None
        for div, code in O.DIVS.items():
            if code not in E.LEAGUES: continue
            s = tune.splits(code)[split][0]
            if "-" not in s: continue
            season = season or s
            prices += O.parse(O._get(O.HIST_URL.format(yy=O._yy(s), div=div), log=log))
            time.sleep(1.0)
        prices = [r for r in prices if r["result"] is not None]
        fixtures = [((c, d, h, a), c, d, h, a) for (c, d, h, a) in preds]
        joined = O.match(prices, fixtures)
        L = legs([(preds[k], r) for k, r in joined.items()])
        res = {"season": season, "pricedMatches": len(prices), "matched": len(joined), "candidates": len(L), "cuts": {}}
        for name, f in CUTS.items():
            res["cuts"][name] = summary([l for l in L if f(l["model"], l["fair"])])
        res["trebles"] = trebles([l for l in L if CUTS["under5"](l["model"], l["fair"])])
        res["card"] = card_season(L)
        res["legs"] = [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in l.items()} for l in L]
        report["seasons"][split] = res
        print(f"{split} {season}: {len(prices)} priced, {len(joined)} matched, {len(L)} candidate legs")
        for name, c in res["cuts"].items():
            if c.get("n"): print(f"  {name:8s} n {c['n']:5d} landed {c['landed']*100:5.1f} quoted {c['quoted']*100:5.1f} (se {c['se']*100:.1f}) roi {c['roi']*100:+5.1f}% (p {c['pRoiNotPositive']}) best {c['roiBest']*100:+5.1f}% clv {c['clv']}")
        t = res["trebles"]
        if t.get("n"): print(f"  trebles n {t['n']} won {t['won']} landed {t['landed']*100:.0f}% expected {t['expected']*100:.0f}% roi {t['roi']*100:+.0f}% z {t['z']}")
        c = res["card"]
        if c.get("groups"): print(f"  card: {c['days']} days, {c['groups']} groups, won {c['won']} (exp {c['expected']}), z {c['z']}, units {c['units']}, return {c['return']} (best {c['returnBest']}), 90% {c['return90']}, p(loss) {c['pLoss']}, kinds {c['kinds']}")
    u_fit = report["seasons"]["fit"]["cuts"].get("under5", {}); u_chk = report["seasons"]["check"]["cuts"].get("under5", {})
    holds = lambda c: c.get("n", 0) >= O.MIN_BETS and c.get("gap", 0) > 0 and c.get("roi", 0) > 0
    report["verdict"] = ("The under-market cut lands above its quote and returns a profit on both seasons." if holds(u_fit) and holds(u_chk) else
                         "The under-market cut does not hold on both seasons; read the per-season figures.")
    report["log"] = log[-20:]
    with open(out_path, "w") as f: json.dump(report, f, indent=1)
    print(report["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
