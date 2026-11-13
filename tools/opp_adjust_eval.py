"""Opponent-adjusted attack/defence ratings (Ben, 13 Nov 2026).
Each side's goals for / against divided by what its opponents' ratings said
they would give / concede (iterated), then shrunk exactly as the live ratings.
lam blends raw (0) and adjusted (1). Calibration refitted per setting.
Run: python3 tools/opp_adjust_eval.py  (fetches via tune.load, cached in /tmp/work)"""
import sys, pickle, random, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune, engine as E
P = '/tmp/work/data.pkl'
if os.path.exists(P): data = pickle.load(open(P, 'rb'))
else:
    os.makedirs('/tmp/work/cache', exist_ok=True)
    data = tune.load('/tmp/work/cache'); pickle.dump(data, open(P, 'wb'))
ob, os_ = E.build_table, E.strength_from_table
def bt(matches):
    t = ob(matches)
    for r in t.values(): r["_m"] = []
    for d, h, a, hg, ag in matches:
        t[h]["_m"].append((a, hg, ag)); t[a]["_m"].append((h, ag, hg))
    return t
def make(lam, iters=3):
    def f(table, k=None):
        raw = os_(table, k)
        if lam == 0 or not any("_m" in r for r in table.values()): return raw
        k = E.SHRINK_FULL_SEASON if k is None else k
        mu = E.league_goal_rate(table); cur = raw
        for _ in range(iters):
            nxt = {}
            for t, r in table.items():
                p = r["P"]
                if not p: nxt[t] = raw[t]; continue
                ea = sum(mu * cur[o]["def"] for o, _, _ in r["_m"])
                ed = sum(mu * cur[o]["att"] for o, _, _ in r["_m"])
                ar = sum(g for _, g, _ in r["_m"]) / ea
                dr = sum(g for _, _, g in r["_m"]) / ed
                w = p / (p + k)
                a = w * ar + (1 - w); d = w * dr + (1 - w)
                a = lam * a + (1 - lam) * raw[t]["att"]; d = lam * d + (1 - lam) * raw[t]["def"]
                nxt[t] = {"att": min(max(a, E.ATT_BOUNDS[0]), E.ATT_BOUNDS[1]),
                          "def": min(max(d, E.DEF_BOUNDS[0]), E.DEF_BOUNDS[1])}
            cur = nxt
        return cur
    return f
def raws(split, lam):
    E.build_table = bt; E.strength_from_table = make(lam)
    try: return tune.raw_probs(tune.lambdas(data, split))
    finally: E.build_table = ob; E.strength_from_table = os_
def fitcal(rw):
    best = None
    for a in [x/100 for x in range(95, 176, 5)]:
        for b in [-0.6, -0.45, -0.3, -0.15, 0]:
            per, _, _ = tune.score_raw(rw, cal={'a': a, 'b': b}); m = sum(per)/len(per)
            if best is None or m < best[0]: best = (m, a, b)
    return best
def boot(x, y, n=1000):
    d = [a-b for a, b in zip(x, y)]; r = random.Random(1); N = len(d)
    ms = [sum(d[r.randrange(N)] for _ in range(N))/N for _ in range(n)]
    return round(sum(d)/N, 4), sum(1 for m in ms if m > 0)/n
live = E.CALIBRATION
base = {s: raws(s, 0) for s in ('fit', 'check')}
bp = {s: tune.score_raw(base[s], cal=live)[0] for s in base}
print({s: len(v) for s, v in base.items()})
for lam in (0.25, 0.5, 1.0):
    rs = {s: raws(s, lam) for s in base}
    _, a, b = fitcal(rs['fit']); cal = {'a': a, 'b': b}
    out = []
    for mode, c in (('live', live), ('refit', cal)):
        out.append((mode, [(s,) + boot(tune.score_raw(rs[s], cal=c)[0], bp[s]) for s in base]))
    print('lam', lam, 'cal', cal, out, flush=True)
