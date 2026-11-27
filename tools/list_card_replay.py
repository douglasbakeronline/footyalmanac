#!/usr/bin/env python3
"""
The Daily 2x and the List card replayed with their picks ordered by
confidence alone, list and reserve together, against live (#569, 27 Nov
2026). Advisory: changes nothing, fits nothing, writes nothing unless
--json is given.

    python3 tools/list_card_replay.py [--json FILE]

Douglas, 27 Nov 2026 (the Daily List review): on the results ledger a pick
lands at its confidence whether it sits on the list or the reserve, so the
Daily List page shows them together. The two List-built slips still put
the list first:

  live        groupings.daily_group: list, then reserve, then football 65%+,
              then any sport 65%+, strongest first within a tier;
              build_list_card: the List 2x (list picks 1.15+, six) else the
              List long (list picks, any price, ten).
  confidence  pre-registered here: the same functions on the same legs with
              every reserve pick read as a list pick, so list and reserve
              form one tier ordered by the model's number. Floors, prices,
              leg caps, targets, the later football and any-sport tiers and
              the college exclusion are unchanged.

Two sources, each built as at 07:00 UK on the slip's day (the hour the
slips are held from since 23 and 24 Nov 2026):
  ledger  results-ledger.json.gz, every settled prediction with a pre-start
          price, at its first recorded price (and the last with --closing)
  pool    the archived priced pool (tools/card_replay.pool_legs), first real
          price, list and reserve flags as first written

Each slip stakes one unit and is won only when every pick won. Paired by
day (card_replay.pair_days): the variant's profit minus live's, a day
bootstrap for p(worse), and the days and legs the two differ on, since a
day with the same picks adds nothing. The gate (CLAUDE.md): 100+ legs
where they differ and p(worse) at most 0.30 on both sources; a pass goes
to Douglas, it is not set live from here.
"""
import gzip
import json
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G  # noqa: E402

LEDGER = os.path.join(HERE, "results-ledger.json.gz")
VARIANTS = ("live", "confidence")
CARDS = ("daily", "list")
GATE_LEGS = 100
GATE_P = 0.30


def merged(day_legs, variant):
    """The legs a variant builds from: under `confidence` a reserve pick is
    read as a list pick (one tier, the model's number orders it)."""
    if variant == "live": return day_legs
    return [dict(l, list=True) if l.get("reserve") and not l.get("list") else l for l in day_legs]


def build_daily(day_legs, after, variant):
    g = G.daily_group(merged(day_legs, variant), after)
    return [g] if g else []


def build_list(day_legs, after, variant):
    """The List card as build_list_card makes a fresh day: the List 2x, else
    the List long."""
    L = merged(day_legs, variant)
    for name, target, odds_min, legs_max in G.LIST_KINDS:
        g = G.list_group(L, set(), after, name, target, odds_min, legs_max)
        if g: return [g]
    return []


BUILD = {"daily": build_daily, "list": build_list}


def grade(g):
    g = dict(g, stake=1)
    g["won"] = all(l.get("won") for l in g["legs"])
    return g


def ledger_legs(rows, closing=False):
    """Ledger rows -> settled, priced legs by Card day, in groupings' shape."""
    by = defaultdict(list)
    for r in rows:
        if r.get("result") not in ("won", "lost") or not r.get("sport") or r.get("conf") is None: continue
        px = (r.get("last") if closing else None) or r.get("first")
        o = (px or {}).get("o")
        if not o or o <= 1: continue
        l = {"sport": r["sport"], "event": r.get("key") or f"{r.get('home')} v {r.get('away')}", "pick": r.get("pick"),
             "when": r.get("start") or f"{r['date']}T12:00:00Z", "odds": round(o, 2), "best": (px or {}).get("b") or o,
             "pModel": r["conf"], "list": bool(r.get("list")), "reserve": bool(r.get("reserve")),
             "implied": round(1 / o, 4), "fair": None, "est": False, "won": r["result"] == "won"}
        slot = G.uk_slot(l)
        if slot: by[slot[0]].append(l)
    return by


def run(by, card):
    """{variant: {day: [graded slips]}} on every day with legs."""
    out = {v: {} for v in VARIANTS}
    for d in sorted(by):
        after = G.lock_time(d, G.CARD_WINDOWS[0][0])
        for v in VARIANTS:
            gl = [grade(g) for g in BUILD[card](by[d], after, v)]
            if gl: out[v][d] = gl
    return out


def tally(days):
    gs = [g for gl in days.values() for g in gl]
    legs = [l for g in gs for l in g["legs"]]
    n = len(gs)
    return {"slips": n, "won": sum(g["won"] for g in gs), "expected": round(sum(g["p"] for g in gs), 2),
            "return": round(sum(g["odds"] for g in gs if g["won"]) / n - 1, 3) if n else None,
            "legs": len(legs), "legsWon": sum(bool(l.get("won")) for l in legs),
            "reserveLegs": sum(bool(l.get("reserve")) for l in legs), "short": sum(bool(g.get("short")) for g in gs)}


def paired(live, var, seed=569):
    from card_replay import pair_days
    alld, diffs, ddays, dlegs = pair_days(live, var)
    res = {"days": len(alld), "daysDiffer": ddays, "legsDiffer": dlegs}
    if not diffs or not any(diffs):
        return dict(res, perDay=0.0, pWorse=None)
    rnd = random.Random(seed)
    bs = [sum(rnd.choice(diffs) for _ in diffs) / len(diffs) for _ in range(4000)]
    return dict(res, perDay=round(sum(diffs) / len(diffs), 3), pWorse=round(sum(x < 0 for x in bs) / len(bs), 3))


def gate(pairs):
    """Pass only when every source has 100+ differing legs and p(worse) <= 0.30."""
    return all(p.get("pWorse") is not None and p["pWorse"] <= GATE_P and p["legsDiffer"] >= GATE_LEGS for p in pairs)


def main():
    closing = "--closing" in sys.argv
    with gzip.open(LEDGER, "rt", encoding="utf-8") as f:
        rows = json.load(f).get("rows") or []
    sources = {"ledger": ledger_legs(rows, closing)}
    try:
        import card_replay as CR
        sources["pool"], _ = CR.pool_legs(closing=closing)
    except Exception as e:  # the pool needs the committed results caches
        print(f"pool: not read ({e})")
    report = {"closing": closing, "cards": {}}
    for card in CARDS:
        report["cards"][card] = {}
        for src, by in sources.items():
            out = run(by, card)
            r = {v: tally(out[v]) for v in VARIANTS}
            r["paired"] = paired(out["live"], out["confidence"])
            r["from"], r["to"] = (min(by), max(by)) if by else (None, None)
            report["cards"][card][src] = r
            print(f"\n{'Daily 2x' if card == 'daily' else 'List card'} on the {src} ({r['from']} to {r['to']}):")
            for v in VARIANTS:
                t = r[v]
                ret = f"{t['return'] * 100:+.1f}%" if t["return"] is not None else "n/a"
                print(f"  {v:<11} {t['slips']:>3} slips, {t['won']:>3} won v {t['expected']:>6} expected, return {ret}, "
                      f"legs {t['legsWon']}/{t['legs']} ({t['reserveLegs']} reserve), short {t['short']}")
            p = r["paired"]
            print(f"  confidence v live: {p['perDay']:+.3f} a day on {p['days']} days, p(worse) {p['pWorse']}, "
                  f"differs on {p['daysDiffer']} days / {p['legsDiffer']} legs")
        pairs = [report["cards"][card][s]["paired"] for s in sources]
        report["cards"][card]["gate"] = gate(pairs) if len(pairs) == 2 else None
        print(f"  gate (both sources, {GATE_LEGS}+ differing legs, p(worse) <= {GATE_P}): "
              f"{'pass, for Douglas' if report['cards'][card]['gate'] else 'not met'}")
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as f: json.dump(report, f, indent=1)
    return report


if __name__ == "__main__":
    main()
