#!/usr/bin/env python3
"""
Stake size and bankroll for the Card (9 Nov 2026, Douglas: "consistent
returns"). Advisory. Reads card-legs-history.json (the whole Card replayed
over past seasons, tune.yml) and groupings-record.json (the live Card).

For each source: the groups' prices and outcomes, then by bootstrap over
months the return and the worst drawdown at a flat unit, half Kelly and
quarter Kelly (Kelly from the bookmakers' chance and the price per group),
and the bankroll, in units, that keeps the chance of losing half of it in a
season under 5%. Standard library only.
"""
import json, math, os, random, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
random.seed(11)


def groups_from_history():
    try: d = json.load(open(os.path.join(HERE, "card-legs-history.json")))
    except Exception: return []
    return [(g["p"], g["odds"], g["won"]) for s in d.get("seasons", {}).values() for g in (s.get("card") or {}).get("groupList", [])]


def groups_from_record():
    try: r = json.load(open(os.path.join(HERE, "groupings-record.json")))
    except Exception: return []
    return [(g["p"], g["odds"], g["status"] == "won") for d in r.get("days", []) for g in d.get("groups", [])
            if str(g.get("name", "")).startswith("Card") and g.get("status") in ("won", "lost") and not g.get("wide")]


def sim(gs, frac, n=4000, per_season=None, lift=1.0):
    """frac 0: a flat 1% of the bankroll a group. Otherwise that fraction of
    Kelly, where the group's chance is the bookmakers' chance scaled by
    `lift`, the ratio of landed to expected on the same sample (the
    bookmakers' chance alone never gives a positive Kelly stake: their
    margin is in the price). Sizing advice only; nothing is fitted."""
    per_season = per_season or len(gs)
    rets, dds = [], []
    for _ in range(n):
        bank, peak, dd = 100.0, 100.0, 0.0
        for p, o, won in (random.choice(gs) for _ in range(per_season)):
            q = min(0.95, p * lift)
            kelly = max(0.0, (q * o - 1) / (o - 1)) if o > 1 else 0
            stake = bank * (frac * kelly if frac else 0.01)
            bank += stake * (o - 1) if won else -stake
            peak = max(peak, bank); dd = max(dd, (peak - bank) / peak)
        rets.append(bank / 100 - 1); dds.append(dd)
    rets.sort(); dds.sort()
    return {"median": round(rets[n // 2], 3), "p10": round(rets[n // 10], 3), "p90": round(rets[9 * n // 10], 3),
            "medianDrawdown": round(dds[n // 2], 3), "p95Drawdown": round(dds[int(n * 0.95)], 3)}


def main():
    rep = {}
    for name, gs in (("replay", groups_from_history()), ("live", groups_from_record())):
        if len(gs) < 10: rep[name] = {"groups": len(gs), "note": "too few groups"}; continue
        flat = sim(gs, 0)
        lift = sum(w for _, _, w in gs) / max(1e-9, sum(p for p, _, _ in gs))
        res = {"groups": len(gs), "won": sum(w for _, _, w in gs), "expected": round(sum(p for p, _, _ in gs), 1), "landedOverExpected": round(lift, 3),
               "flat1pct": flat, "halfKelly": sim(gs, 0.5, lift=lift), "quarterKelly": sim(gs, 0.25, lift=lift)}
        res["unitsForSeason"] = round(1 / max(flat["p95Drawdown"], 1e-6) * 0.5 * 100)  # units of one group stake, so a 95% worst drawdown loses half
        rep[name] = res
    print(json.dumps(rep, indent=1))
    if "--json" in sys.argv: json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
