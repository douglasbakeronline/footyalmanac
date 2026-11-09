#!/usr/bin/env python3
"""
Stake size and bankroll for the Card (9 Nov 2026, Douglas: "consistent
returns"). Advisory. Reads card-legs-history.json (the whole Card replayed
over past seasons, tune.yml) and groupings-record.json (the live Card).

For each source: the groups' prices and outcomes, then by bootstrap the
return and the worst drawdown at a flat 1% of the bankroll, half Kelly and
quarter Kelly (Kelly from the bookmakers' chance and the price per group),
and the bankroll, in units, that keeps a 95%-worst month's and season's
drawdown to half of it at the page's stake (CARD_STAKE: two units on a 2x,
one on a 3x). Standard library only.

9 Nov 2026, second pass: `unitsForSeason` was 0.5 / p95 drawdown x 100,
which inverts the scaling (a 17% drawdown at 1% stakes gave 289 units; the
bankroll that halves at that drawdown is about 35), and a "season" was the
sample's own length (42 groups). The bankroll now comes from the drawdown
in units at the page's fixed stakes over a month and a season of groups at
the source's own rate; `unitsForSeason` keeps its name and now means that.
Late and wider-rule groups are left out of the live sample, as the record's
Card line leaves them out.
"""
import json, math, os, random, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAKE = {"Card 2x": 2, "Card 3x": 1}   # groupings.CARD_STAKE, read without importing the pipeline
random.seed(11)


def _d(s):
    from datetime import date
    return date.fromisoformat(s[:10])


def groups_from_history():
    """[(p, odds, won, stake)], groups a day, groups a season: the replayed
    Card on every season it holds."""
    try: d = json.load(open(os.path.join(HERE, "card-legs-history.json")))
    except Exception: return [], None, None
    gs, days, n = [], 0, 0
    for s in d.get("seasons", {}).values():
        gl = (s.get("card") or {}).get("groupList") or []
        gs += [(g["p"], g["odds"], bool(g["won"]), g.get("stake") or STAKE.get(g.get("name"), 1)) for g in gl]
        ds = sorted({g["date"] for g in gl})
        # a football season runs August to May: the replay's span, not 365 days
        if ds: days += (_d(ds[-1]) - _d(ds[0])).days + 1; n += 1
    return gs, (len(gs) / days if days else None), (round(len(gs) / n) if n else None)


def groups_from_record():
    try: r = json.load(open(os.path.join(HERE, "groupings-record.json")))
    except Exception: return [], None, None
    gs, dates = [], set()
    for d in r.get("days", []):
        for g in d.get("groups", []):
            if not str(g.get("name", "")).startswith("Card") or g.get("status") not in ("won", "lost"): continue
            if g.get("wide") or g.get("late"): continue
            gs.append((g["p"], g["odds"], g["status"] == "won", STAKE.get(g["name"], 1))); dates.add(d["date"])
    span = (_d(max(dates)) - _d(min(dates))).days + 1 if dates else 0
    rate = len(gs) / span if span else None
    # the live Card runs every sport all year: a season is 365 days at its rate
    return gs, rate, (round(rate * 365) if rate else None)


def sim(gs, frac, n=4000, per_season=None, lift=1.0):
    """frac 0: a flat 1% of the bankroll a group. Otherwise that fraction of
    Kelly, where the group's chance is the bookmakers' chance scaled by
    `lift`, the ratio of landed to expected on the same sample (the
    bookmakers' chance alone never gives a positive Kelly stake: their
    margin is in the price). Kelly is zero on a group whose lifted chance
    still does not beat its price, so on a sample at or under quote the
    Kelly lines read 0: no stake has an edge. Sizing advice only."""
    per_season = per_season or len(gs)
    rets, dds = [], []
    for _ in range(n):
        bank, peak, dd = 100.0, 100.0, 0.0
        for p, o, won, *_ in (random.choice(gs) for _ in range(per_season)):
            q = min(0.95, p * lift)
            kelly = max(0.0, (q * o - 1) / (o - 1)) if o > 1 else 0
            stake = bank * (frac * kelly if frac else 0.01)
            bank += stake * (o - 1) if won else -stake
            peak = max(peak, bank); dd = max(dd, (peak - bank) / peak)
        rets.append(bank / 100 - 1); dds.append(dd)
    rets.sort(); dds.sort()
    return {"median": round(rets[n // 2], 3), "p10": round(rets[n // 10], 3), "p90": round(rets[9 * n // 10], 3),
            "medianDrawdown": round(dds[n // 2], 3), "p95Drawdown": round(dds[int(n * 0.95)], 3)}


def bankroll(gs, k, n=4000):
    """k groups drawn from gs at the page's fixed stakes (units, not a share
    of the bankroll): the 95%-worst peak-to-trough drawdown in units, the
    median profit in units and the units staked. A bankroll of twice the
    drawdown keeps that drawdown to half of it."""
    dds, pnls = [], []
    for _ in range(n):
        pnl, peak, dd = 0.0, 0.0, 0.0
        for p, o, won, st in (random.choice(gs) for _ in range(k)):
            pnl += st * (o - 1) if won else -st
            peak = max(peak, pnl); dd = max(dd, peak - pnl)
        dds.append(dd); pnls.append(pnl)
    dds.sort(); pnls.sort()
    d95 = dds[int(n * 0.95)]
    return {"groups": k, "p95DrawdownUnits": round(d95, 1), "medianPnlUnits": round(pnls[n // 2], 1),
            "staked": round(k * sum(g[3] for g in gs) / len(gs), 1), "units": max(1, math.ceil(2 * d95))}


def report(sources):
    rep = {}
    for name, (gs, rate, per_season) in sources.items():
        if len(gs) < 10: rep[name] = {"groups": len(gs), "note": "too few groups"}; continue
        flat = sim(gs, 0)
        lift = sum(w for _, _, w, _ in gs) / max(1e-9, sum(p for p, *_ in gs))
        res = {"groups": len(gs), "won": sum(w for _, _, w, _ in gs), "expected": round(sum(p for p, *_ in gs), 1), "landedOverExpected": round(lift, 3),
               "flat1pct": flat, "halfKelly": sim(gs, 0.5, lift=lift), "quarterKelly": sim(gs, 0.25, lift=lift)}
        if rate:
            res["groupsPerDay"] = round(rate, 2)
            # a month at the source's rate, and a season: the replay's own groups a
            # season (football, August to May), 365 days of the live Card
            res["bankroll"] = {"month": bankroll(gs, max(1, round(rate * 30))), "season": bankroll(gs, max(1, per_season or len(gs)))}
            res["unitsForSeason"] = res["bankroll"]["season"]["units"]
        rep[name] = res
    return rep


def main():
    rep = report({"replay": groups_from_history(), "live": groups_from_record()})
    print(json.dumps(rep, indent=1))
    if "--json" in sys.argv: json.dump(rep, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
