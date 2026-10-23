#!/usr/bin/env python3
"""Which leg properties land at their quoted chance? (23 Oct 2026, claude/odds-groupings.md)
Input: the legs file written by tools/odds_edge_test.py (argv[1]). A leg is a
home/away outcome (draws excluded) with min(model, fair) >= 0.65, the Wider
pool's own bar. Chance = min(model, fair), as groupings.honest() sets it.
Statistic: mean(hit - chance) per cell, paired bootstrap, fit v check season.
Advisory; writes nothing, feeds no model."""
import sys, json, random
L = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/w/legs.json"))
random.seed(7)
def boot(xs, n=1000):
    if not xs: return None
    m = len(xs); b = sorted(sum(xs[random.randrange(m)] for _ in range(m)) / m for _ in range(n))
    return b[int(.05 * n)], b[int(.95 * n)]
def pool(legs, floor=.65):
    out = []
    for l in legs:
        if l["i"] == 1: continue
        f = l["fc"] if False else l["f"]
        c = min(l["p"], f)
        if c < floor: continue
        out.append(dict(l, c=c, gap=l["p"] - f, side="home" if l["i"] == 0 else "away", d=l["hit"] - c))
    return out
def cut(name, fn, S):
    row = [name]
    for s in ("fit", "check"):
        xs = [l["d"] for l in S[s] if fn(l)]
        if not xs: row.append("n 0"); continue
        lo, hi = boot(xs)
        row.append(f"n {len(xs):5d} gap {100*sum(xs)/len(xs):+5.1f} [{100*lo:+.1f},{100*hi:+.1f}] landed {100*(sum(xs)/len(xs)+sum(l['c'] for l in S[s] if fn(l))/len(xs)):.1f}")
    print(" | ".join(row))
S = {s: pool(L[s]) for s in ("fit", "check")}
cut("all", lambda l: True, S)
for nm, fn in [("home", lambda l: l["side"] == "home"), ("away", lambda l: l["side"] == "away"),
    ("chance 65-70", lambda l: l["c"] < .70), ("70-75", lambda l: .70 <= l["c"] < .75), ("75-80", lambda l: .75 <= l["c"] < .80),
    ("80-90", lambda l: .80 <= l["c"] < .90), ("90+", lambda l: l["c"] >= .90),
    ("price <1.15", lambda l: l["odds"] < 1.15), ("1.15-1.30", lambda l: 1.15 <= l["odds"] < 1.30),
    ("1.30-1.45", lambda l: 1.30 <= l["odds"] < 1.45), ("1.45+", lambda l: l["odds"] >= 1.45),
    ("model<=fair-3", lambda l: l["gap"] <= -.03), ("fair-3..0", lambda l: -.03 < l["gap"] <= 0),
    ("0..+3", lambda l: 0 < l["gap"] <= .03), ("+3..+8", lambda l: .03 < l["gap"] <= .08), ("above +8", lambda l: l["gap"] > .08),
    ("model<=fair (veto side)", lambda l: l["gap"] <= 0), ("model within 5 above", lambda l: 0 < l["gap"] <= .05)]:
    cut(nm, fn, S)
codes = {}
for s in S:
    for l in S[s]: codes.setdefault(l["code"], 0); codes[l["code"]] += 1
top = sorted(codes, key=lambda c: -codes[c])[:14]
print("--- by competition (top 14 by legs)")
for c in top: cut(c, lambda l, c=c: l["code"] == c, S)
print("--- tier: top flight codes ending .1 v other")
cut("code endswith .1", lambda l: l["code"].endswith(".1"), S)
cut("not .1", lambda l: not l["code"].endswith(".1"), S)
