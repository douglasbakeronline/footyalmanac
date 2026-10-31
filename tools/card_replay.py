#!/usr/bin/env python3
"""
The Card replayed on the priced archive, under several leg rules. Advisory:
changes nothing, fits nothing, writes nothing. 29 Oct 2026, Douglas: "I need
this to be the minimum performance of the groups bets over time".

    python3 tools/card_replay.py

Every archived football prediction that carried a bookmaker price before
kick-off (predictions/<date>.json "market", the latest copy per fixture, as
tools/market_check.py joins them) is a candidate leg with the model's number,
the bookmakers' average and best price, and its result. Days follow the
29 Oct 2026 window (07:00 UK to 07:00 next day). For each rule the Card is
built exactly as groupings.build_card builds it today (best_card, card_fault,
mult_combo, the 2x and 3x kinds, three or four picks, no fixture twice) and
graded strictly: a group is won only when every pick won.

Variants compared (29 Oct 2026 afternoon, pre-registered for the 30 Nov
review so no variant is picked because it happened to look good):
  live     the Card exactly as groupings.py builds it today
  under8   the model at least 8 points under the market (live: 5)
  under10  the model at least 10 points under the market
  four3x   Card 3x groups of four picks, 2x unchanged
  wider    wider API-Football leagues admitted, under the market (CARD_CORE_ONLY False)
  uncapped the gap uncapped, as the Card was from 29 to 31 Oct 2026 (10+ under
           lost on the live archive and both football-data seasons; capped 31 Oct)
  short    prices 1.15 to 1.35 only (the one band positive on both seasons)
Each is built with build_card's own pieces (best_card, card_fault, the kinds,
the cap, the stake weights) with one constant patched, so the replay and the
live card cannot drift apart. `--since YYYY-MM-DD` limits the days.

Rule 1 holds: nothing is fitted here, it is the scoreboard read. The archive
has prices from 11 Sep 2026, so this is seven weeks and the intervals are
wide; read the direction, not the decimals. Standard library only.
"""
import json, math, os, random, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G, engine as E, sources as S
import market_check as M

random.seed(7)
IDX = {"h": 0, "d": 1, "a": 2}
CORE = {c for c, m in E.LEAGUES.items() if not c.startswith("af.") and not m.get("cup") and not m.get("international")}


def legs_of(rows):
    """Archive rows -> legs in groupings' shape, by Card day."""
    by = defaultdict(list)
    for i, x in enumerate(rows):
        p = x.get("p") or {}
        if not p or x.get("celtic") or x.get("unrated") or x.get("why") not in G.CLEAN_WHY: continue
        side = max(p, key=p.get)
        if side == "d": continue
        mk = x["market"]; j = IDX[side]
        avg, best = mk["avg"][j], (mk.get("best") or mk["avg"])[j]
        margin = sum(1 / o for o in mk["avg"] if o)
        l = {"sport": "football", "event": f"{x['home']} v {x['away']}", "pick": x["home"] if side == "h" else x["away"],
             "comp": x["league"], "code": x["league"], "when": x.get("kickoff") or f"{x['date']}T12:00:00Z", "date": x["date"], "odds": round(avg, 2),
             "best": round(best, 2), "margin": round(margin, 4), "est": False, "pModel": round(p[side], 4), "p": round(p[side], 4),
             "hit": 0.8, "n": 100, "won": x["actual"] == side, "core": x["league"] in CORE}
        G.honest(l)
        slot = G.uk_slot(l)
        if slot: by[slot[0]].append(l)
    return by


VARIANTS = {
    "live": {},
    "under8": {"CARD_UNDER_MARKET": 0.08},
    "under10": {"CARD_UNDER_MARKET": 0.10},
    "four3x": {"CARD_LEGS_3X": (4,)},
    "wider": {"CARD_CORE_ONLY": False},
    "uncapped": {"CARD_UNDER_MAX": 0},     # rule 4, before the 31 Oct 2026 cap
    "short": {"CARD_ODDS": (1.15, 1.35)},
}


def build(day_legs, date, variant):
    """One day's Card under a variant, with the live machinery."""
    patch = VARIANTS[variant]
    saved = {k: getattr(G, k) for k in patch if hasattr(G, k)}
    legs_3x = patch.get("CARD_LEGS_3X")
    for k, v in patch.items():
        if k != "CARD_LEGS_3X": setattr(G, k, v)
    try:
        after = G.lock_time(date, "Day"); groups, used = [], set()
        for seq in (1, 2, 3):
            for name, _, _, _ in G.CARD_KINDS:
                if len(groups) >= G.CARD_MAX_GROUPS: break
                if legs_3x and name == "Card 3x":
                    old_legs = G.CARD_LEGS; G.CARD_LEGS = legs_3x
                    try: g = G.best_card(day_legs, used, after, name)
                    finally: G.CARD_LEGS = old_legs
                else:
                    g = G.best_card(day_legs, used, after, name)
                if not g: continue
                used |= {l["event"] for l in g["legs"]}
                g["won"] = all(l["won"] for l in g["legs"]); g["stake"] = G.CARD_STAKE.get(name, 1); g["seq"] = seq
                groups.append(g)
        return groups
    finally:
        for k, v in saved.items(): setattr(G, k, v)


def summarise(days, label):
    gs = [g for d in days.values() for g in d]
    if not gs:
        print(f"{label:<8} no groups"); return
    n, w = len(gs), sum(g["won"] for g in gs)
    exp = sum(g["p"] for g in gs)
    st = sum(g["stake"] for g in gs); ret = sum(g["stake"] * g["odds"] for g in gs if g["won"])
    best = sum(g["stake"] * g["bestOdds"] for g in gs if g["won"])
    legs = [l for g in gs for l in g["legs"]]
    lw = sum(l["won"] for l in legs); lq = sum(l["fair"] for l in legs)
    keys = list(days); vals = []
    for _ in range(4000):
        pick = [days[random.choice(keys)] for _ in keys]
        s_ = sum(g["stake"] for d in pick for g in d); r_ = sum(g["stake"] * g["odds"] for d in pick for g in d if g["won"])
        vals.append(r_ / s_ - 1 if s_ else 0)
    vals.sort()
    print(f"{label:<8} days {len(days):>2}  groups {n:>3}  won {w:>3} ({w/n*100:4.0f}%)  expected {exp/n*100:4.0f}%  "
          f"units {st:>3}  return {(ret/st-1)*100:+5.0f}% (90% {vals[200]*100:+.0f} to {vals[3799]*100:+.0f})  best {(best/st-1)*100:+5.0f}%  "
          f"legs {lw}/{len(legs)} landed {lw/len(legs)*100:4.1f}% v quoted {lq/len(legs)*100:4.1f}%")
    for name, _, _, _ in G.CARD_KINDS:
        k = [g for g in gs if g["name"] == name]
        if k:
            kw = sum(g["won"] for g in k); ks = sum(g["stake"] for g in k); kr = sum(g["stake"] * g["odds"] for g in k if g["won"])
            print(f"         {name}: {kw}/{len(k)} won, expected {sum(g['p'] for g in k)/len(k)*100:.0f}%, return {(kr/ks-1)*100:+.0f}%")
    return gs


def main():
    since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else None
    rows = M.rows()
    by = legs_of(rows)
    dates = [d for d in sorted(by) if not since or d >= since]
    print(f"{len(rows)} priced archive rows, {sum(len(by[d]) for d in dates)} clean win-pick legs over {len(dates)} days, {dates[0]} to {dates[-1]}")
    out = {}
    for v in VARIANTS:
        days = {d: build(by[d], d, v) for d in dates}
        days = {d: g for d, g in days.items() if g}
        out[v] = days
        summarise(days, v)
    for v in VARIANTS:
        if v == "live": continue
        a, b = out["live"], out[v]
        alld = sorted(set(a) | set(b)); diffs = []
        for d in alld:
            ra = sum(g["stake"] * g["odds"] for g in a.get(d, []) if g["won"]) - sum(g["stake"] for g in a.get(d, []))
            rb = sum(g["stake"] * g["odds"] for g in b.get(d, []) if g["won"]) - sum(g["stake"] for g in b.get(d, []))
            diffs.append(rb - ra)
        if not diffs: continue
        bs = sorted(sum(random.choice(diffs) for _ in diffs) / len(diffs) for _ in range(4000))
        print(f"paired {v} - live on {len(alld)} days: {sum(diffs)/len(diffs):+.2f} units a day, "
              f"90% {bs[200]:+.2f} to {bs[3799]:+.2f}, p(worse) {sum(x < 0 for x in bs)/len(bs):.2f}")


if __name__ == "__main__":
    main()
