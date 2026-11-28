"""Log-space (geometric) shrinkage of attack/defence ratings (Ben, 28 Nov 2026).
Run: python3 tools/log_shrink_eval.py  (fetches via tune.load, cached in /tmp/work)"""
import sys, pickle, random, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune, engine as E
P = '/tmp/work/data.pkl'
if os.path.exists(P): data = pickle.load(open(P, 'rb'))
else:
    os.makedirs('/tmp/work/cache', exist_ok=True)
    data = tune.load('/tmp/work/cache'); pickle.dump(data, open(P, 'wb'))
orig = E.strength_from_table
def make(kk, floor=0.25):
    def f(table, k=None):
        k = E.SHRINK_FULL_SEASON if k is None else k
        if kk: k = kk
        mu = E.league_goal_rate(table); out = {}
        for t, r in table.items():
            p = r["P"]
            if p == 0: out[t] = {"att": 1.0, "def": 1.0}; continue
            w = p/(p+k)
            # goals smoothed by half a goal per side so log is defined
            ar = max((r["GF"]/p)/mu, floor*0.2); dr = max((r["GA"]/p)/mu, floor*0.2)
            att = math.exp(w*math.log(ar)); dfn = math.exp(w*math.log(dr))
            out[t] = {"att": min(max(att, E.ATT_BOUNDS[0]), E.ATT_BOUNDS[1]),
                      "def": min(max(dfn, E.DEF_BOUNDS[0]), E.DEF_BOUNDS[1])}
        return out
    return f
def raws(split, kk=None, geo=False):
    E.strength_from_table = make(kk) if geo else orig
    try: return tune.raw_probs(tune.lambdas(data, split))
    finally: E.strength_from_table = orig
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
base = {s: raws(s) for s in ('fit', 'check')}
bp = {s: tune.score_raw(base[s], cal=live)[0] for s in base}
print({s: len(v) for s, v in base.items()}, flush=True)
for kk in (None, 3, 4, 6):
    rs = {s: raws(s, kk, True) for s in base}
    _, a, b = fitcal(rs['fit']); cal = {'a': a, 'b': b}
    out = []
    for mode, c in (('live', live), ('refit', cal)):
        out.append((mode, [(s,) + boot(tune.score_raw(rs[s], cal=c)[0], bp[s]) for s in base]))
    print('geo k', kk or 'live4', cal, out, flush=True)
