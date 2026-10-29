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

Rules compared:
  market   the live rule: bookmakers 60%+, model within 5 points, chance =
           the bookmakers' fair number, best combined chance first
  model    confidence first: the same vetoes, but ranked and quoted on the
           model's number
  core     model, restricted to the core leagues (not the 227 wider
           API-Football leagues, not cups) and the model at 65%+
  core70   core, model at 70%+

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


def build(day_legs, date, rule):
    """One day's Card under a rule: best_card unchanged, the candidate set and
    the leg's quoted chance decided by the rule."""
    L = []
    for l in day_legs:
        l = dict(l)
        if rule in ("core", "core70") and not l["core"]: continue
        if rule == "core" and l["pModel"] < 0.65: continue
        if rule == "core70" and l["pModel"] < 0.70: continue
        L.append(l)
    after = G.lock_time(date, "Day")
    if rule == "market":
        pick = lambda L_, used, name: G.best_card(L_, used, after, name)
    else:
        # the same vetoes (card_fault), the model's number as the chance
        def pick(L_, used, name):
            lo, hi = G.CARD_RANGE[name]
            cands = [dict(l, p=l["pModel"], basis="model") for l in L_
                     if l["event"] not in used and G.card_fault(l) is None and (G.parse(l["when"]) or after) >= after]
            cands = sorted(cands, key=lambda l: (-math.log(l["p"]) / math.log(l["odds"]), -l["p"]))[:G.CARD_POOL]
            best = None
            for k in G.CARD_LEGS:
                for c in __import__("itertools").combinations(cands, k):
                    o = G.mult_combo(c, lo, hi)
                    if o is None: continue
                    pr = math.prod(l["p"] for l in c)
                    if pr < G.MIN_CHANCE[name]: continue
                    if best is None or pr > best[0]: best = (pr, o, c)
            if not best: return None
            pr, o, c = best
            return {"name": name, "odds": round(o, 2), "p": round(pr, 4), "legs": list(c)}
    groups, used = [], set()
    for name, _, _, _ in G.CARD_KINDS:
        g = pick(L, used, name)
        if not g: continue
        used |= {l["event"] for l in g["legs"]}
        g["won"] = all(l["won"] for l in g["legs"])
        g["bestOdds"] = round(math.prod(max(l.get("best") or l["odds"], l["odds"]) for l in g["legs"]), 2)
        groups.append(g)
    return groups


def summarise(days, label):
    gs = [g for d in days.values() for g in d]
    if not gs:
        print(f"{label:<8} no groups"); return
    n, w = len(gs), sum(g["won"] for g in gs)
    exp = sum(g["p"] for g in gs)
    ret = sum(g["odds"] for g in gs if g["won"]); best = sum(g["bestOdds"] for g in gs if g["won"])
    legs = [l for g in gs for l in g["legs"]]
    lw = sum(l["won"] for l in legs); lq = sum(l["p"] for l in legs)
    # bootstrap the return per unit by day
    keys = list(days); vals = []
    for _ in range(4000):
        pick = [days[random.choice(keys)] for _ in keys]
        st = sum(len(d) for d in pick); rt = sum(g["odds"] for d in pick for g in d if g["won"])
        vals.append(rt / st - 1 if st else 0)
    vals.sort()
    print(f"{label:<8} days {len(days):>2}  groups {n:>3}  won {w:>3} ({w/n*100:4.0f}%)  expected {exp/n*100:4.0f}%  "
          f"return {ret:6.2f}/{n} ({(ret/n-1)*100:+5.0f}%, 90% {vals[200]*100:+.0f} to {vals[3799]*100:+.0f})  best {(best/n-1)*100:+5.0f}%  "
          f"legs {lw}/{len(legs)} landed {lw/len(legs)*100:4.1f}% v quoted {lq/len(legs)*100:4.1f}%")
    for name, _, _, _ in G.CARD_KINDS:
        k = [g for g in gs if g["name"] == name]
        if k:
            kw = sum(g["won"] for g in k); kr = sum(g["odds"] for g in k if g["won"])
            print(f"         {name}: {kw}/{len(k)} won, expected {sum(g['p'] for g in k)/len(k)*100:.0f}%, return {(kr/len(k)-1)*100:+.0f}%")
    return gs


def main():
    rows = M.rows()
    by = legs_of(rows)
    dates = sorted(by)
    print(f"{len(rows)} priced archive rows, {sum(len(v) for v in by.values())} clean win-pick legs over {len(dates)} days, {dates[0]} to {dates[-1]}")
    out = {}
    for rule in ("market", "model", "core", "core70"):
        days = {d: build(by[d], d, rule) for d in dates}
        days = {d: g for d, g in days.items() if g}
        out[rule] = (days, summarise(days, rule))
    # paired by day: model rules against the market rule
    for rule in ("model", "core", "core70"):
        a, b = out["market"][0], out[rule][0]
        common = sorted(set(a) & set(b))
        diffs = []
        for d in common:
            ra = sum(g["odds"] for g in a[d] if g["won"]) - len(a[d])
            rb = sum(g["odds"] for g in b[d] if g["won"]) - len(b[d])
            diffs.append(rb - ra)
        if not diffs: continue
        bs = sorted(sum(random.choice(diffs) for _ in diffs) / len(diffs) for _ in range(4000))
        print(f"paired {rule} - market on {len(common)} days: {sum(diffs)/len(diffs):+.2f} units a day, "
              f"90% {bs[200]:+.2f} to {bs[3799]:+.2f}, p(worse) {sum(x < 0 for x in bs)/len(bs):.2f}")


if __name__ == "__main__":
    main()
