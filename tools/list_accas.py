#!/usr/bin/env python3
"""
Daily List picks combined into accumulators, on the graded record and on
the priced pool. Advisory: changes nothing, fits nothing, writes nothing
unless --json is given. 10 Nov 2026, Douglas: "I'm losing too much on daily
list picks" (he bets accumulators of many list picks).

    python3 tools/list_accas.py [--since YYYY-MM-DD] [--json out.json]

Part 1, the record (every sport's graded Daily List picks, record-graded.json,
tennis-record.json, sports.graded_games()): for each UK day the picks are
ordered as the page orders them (confidence first), and the top N are taken
as one accumulator for N = 1, 2, 3, 4, 5, 6, 8, 10 and "the whole day". It
reports how many such accumulators landed against how many the quoted
chances expected (the product of each pick's confidence), so it says whether
the list's numbers hold up when picks are combined. No prices here.

Part 2, the pool (groupings-archive/pool-*.json.gz from 30 Oct 2026, list
picks with a real bookmaker price and a settled result, tools/card_replay.py's
reader): the same accumulators at the average price, the return per unit
staked, and the bookmakers' margin each leg carries. `--recover` admits legs
archived before 10 Nov at their last price (approximate).

Rule 1 holds: the record is read, never fitted. Standard library only.
"""
import json, math, os, sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
UK = ZoneInfo("Europe/London")
SIZES = (1, 2, 3, 4, 5, 6, 8, 10)


def uk_day(when):
    try:
        t = datetime.fromisoformat(str(when).replace("Z", "+00:00"))
    except ValueError:
        return None
    if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
    return t.astimezone(UK).date().isoformat()


def record_picks():
    """Every graded Daily List pick, all sports: (day, confidence, won, sport)."""
    out = []
    try:
        for g in json.load(open(os.path.join(HERE, "record-graded.json")))["graded"]:
            if g.get("list") and g.get("verified") != "legacy-unverified" and g.get("won") is not None:
                out.append((g["date"], g["confidence"], bool(g["won"]), "football"))
    except (OSError, ValueError, KeyError):
        pass
    try:
        for g in json.load(open(os.path.join(HERE, "tennis-record.json"))).get("graded") or []:
            if g.get("list") and not g.get("void") and g.get("ok") is not None:
                out.append((g["date"], g["confidence"], bool(g["ok"]), "tennis"))
    except (OSError, ValueError):
        pass
    try:
        import sports
        for g in sports.graded_games()[0]:
            if g.get("list") and not g.get("void") and g.get("ok") is not None and uk_day(g.get("when")):
                out.append((uk_day(g["when"]), g["confidence"], bool(g["ok"]), g.get("sport") or "sports"))
    except Exception:
        pass
    return out


def accas(days, key_p, key_won, sizes=SIZES):
    """days: {day: [pick, ...]}. The top-N accumulator of each day with at
    least N picks, and the whole day's: n, won, expected, z."""
    res = {}
    for n in list(sizes) + ["all"]:
        won = exp = var = 0.0; k = 0
        for d, ps in days.items():
            ps = sorted(ps, key=lambda x: -key_p(x))
            if n != "all" and len(ps) < n: continue
            legs = ps if n == "all" else ps[:n]
            if n == "all" and len(legs) < 2: continue
            p = math.prod(key_p(x) for x in legs)
            k += 1; won += all(key_won(x) for x in legs); exp += p; var += p * (1 - p)
        if k:
            res[str(n)] = {"n": k, "won": int(won), "expected": round(exp, 2), "landed": round(won / k, 3),
                           "quoted": round(exp / k, 3), "z": round((won - exp) / math.sqrt(var), 2) if var else None}
    return res


def priced(since=None, recover=False):
    import card_replay as CR
    by, _ = CR.pool_legs(since=since, recover=recover)
    days = {d: [l for l in ls if l.get("list")] for d, ls in by.items()}
    days = {d: ls for d, ls in days.items() if ls}
    res = {}
    for n in list(SIZES) + ["all"]:
        k = won = 0; staked = returned = exp = fair_exp = 0.0
        for d, ls in days.items():
            ls = sorted(ls, key=lambda l: -l["pModel"])
            if n != "all" and len(ls) < n: continue
            legs = ls if n == "all" else ls[:n]
            if n == "all" and len(legs) < 2: continue
            odds = math.prod(l["odds"] for l in legs)
            k += 1; staked += 1; w = all(l["won"] for l in legs); won += w; returned += odds if w else 0
            exp += math.prod(l["pModel"] for l in legs); fair_exp += math.prod(l["fair"] for l in legs) * odds
        if k:
            res[str(n)] = {"n": k, "won": won, "modelExpected": round(exp, 2), "return": round(returned / staked - 1, 3),
                           # the bookmakers' own expectation of the return: their fair chance times the price
                           "bookExpectedReturn": round(fair_exp / k - 1, 3)}
    legs = [l for ls in days.values() for l in ls]
    margin = sum(l.get("margin") or 0 for l in legs) / len(legs) if legs else None
    single = (sum(l["odds"] for l in legs if l["won"]) / len(legs) - 1) if legs else None
    return {"legs": len(legs), "days": len(days), "avgOdds": round(sum(l["odds"] for l in legs) / len(legs), 3) if legs else None,
            "avgMargin": round(margin, 4) if margin else None, "singlesReturn": round(single, 3) if single is not None else None,
            "accas": res}


def main():
    since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else None
    recover = "--recover" in sys.argv
    picks = [p for p in record_picks() if not since or p[0] >= since]
    days = defaultdict(list)
    for p in picks: days[p[0]].append(p)
    rec = accas(days, lambda x: x[1], lambda x: x[2])
    print(f"The record: {len(picks)} graded Daily List picks over {len(days)} days"
          f" ({', '.join(f'{s} {sum(1 for p in picks if p[3] == s)}' for s in sorted({p[3] for p in picks}))})")
    for n, r in rec.items():
        print(f"  top {n:>3}: {r['n']:3d} days, landed {r['won']:3d} ({r['landed'] * 100:5.1f}%) v quoted {r['quoted'] * 100:5.1f}%, z {r['z']}")
    pr = priced(since, recover)
    print(f"The pool at bookmaker prices{' (recover)' if recover else ''}: {pr['legs']} priced list picks over {pr['days']} days, "
          f"average price {pr['avgOdds']}, margin {pr['avgMargin']}, singles return {pr['singlesReturn']}")
    for n, r in pr["accas"].items():
        print(f"  top {n:>3}: {r['n']:3d} accas, {r['won']:3d} won (model expected {r['modelExpected']}), return {r['return'] * 100:+6.1f}%, "
              f"the bookmakers' own expectation {r['bookExpectedReturn'] * 100:+6.1f}%")
    out = {"record": rec, "pool": pr, "since": since, "recover": recover}
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as f: json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    main()
