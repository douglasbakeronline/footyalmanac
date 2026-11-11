"""Separate shrink constants for attack and defence (Ben, 6 Nov 2026).
Run: python3 tools/att_def_shrink_eval.py  (fetches via tune.load, cached in /tmp/work)"""
import sys, pickle, random, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune, engine as E
P = '/tmp/work/data.pkl'
if os.path.exists(P): data = pickle.load(open(P, 'rb'))
else:
    os.makedirs('/tmp/work/cache', exist_ok=True)
    data = tune.load('/tmp/work/cache'); pickle.dump(data, open(P, 'wb'))
orig = E.strength_from_table
def make(ka, kd):
    def f(table, k=None):
        a = orig(table, k=ka if ka else k); d = orig(table, k=kd if kd else k)
        return {t: {"att": a[t]["att"], "def": d[t]["def"]} for t in a}
    return f
def raws(split, ka=None, kd=None):
    E.strength_from_table = make(ka, kd)
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
print({s: len(v) for s, v in base.items()})
for ka, kd in [(4,6),(4,8),(4,12),(4,2),(2,4),(3,4),(6,4),(8,4),(2,8)]:
    rs = {s: raws(s, ka, kd) for s in base}
    _, a, b = fitcal(rs['fit']); cal = {'a': a, 'b': b}
    out = []
    for mode, c in (('live', live), ('refit', cal)):
        out.append((mode, [(s,) + boot(tune.score_raw(rs[s], cal=c)[0], bp[s]) for s in base]))
    print('att k', ka, 'def k', kd, out, flush=True)
