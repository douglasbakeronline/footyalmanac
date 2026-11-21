"""Venue-balanced goals in the season tables (Ben, 21 Nov 2026).
A side's attack / defence is built from goals scored and conceded, home and away mixed.
Early in a season a side with more home games has inflated goals. Here each match's goals are
divided by the venue multiplier (home goals by H, away by A) before the table is built, so
the rating is a neutral-venue rate; expected_goals re-applies the multiplier. f scales how much.
Run: python3 tools/venue_balance_eval.py  (fetches via tune.load, cached in /tmp/work)"""
import sys, pickle, random, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tune, engine as E
P = '/tmp/work/data.pkl'
if os.path.exists(P): data = pickle.load(open(P, 'rb'))
else:
    os.makedirs('/tmp/work/cache', exist_ok=True)
    data = tune.load('/tmp/work/cache'); pickle.dump(data, open(P, 'wb'))
orig = E.build_table
H, A = 1.17, 0.86
def make(f):
    dh, da = 1 + f * (H - 1), 1 + f * (A - 1)
    def bt(matches):
        t = orig(matches)
        for date, h, a, hg, ag in matches:
            rh, ra = t[h], t[a]
            rh["GF"] += hg / dh - hg; rh["GA"] += ag / da - ag
            ra["GF"] += ag / da - ag; ra["GA"] += hg / dh - hg
        return t
    return bt
def raws(split, f=None):
    if f: E.build_table = make(f)
    try: return tune.raw_probs(tune.lambdas(data, split))
    finally: E.build_table = orig
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
for f in (0.5, 1.0, 1.5):
    rs = {s: raws(s, f) for s in base}
    _, a, b = fitcal(rs['fit']); cal = {'a': a, 'b': b}
    out = []
    for mode, c in (('live', live), ('refit', cal)):
        out.append((mode, [(s,) + boot(tune.score_raw(rs[s], cal=c)[0], bp[s]) for s in base]))
    print('f', f, 'cal', cal, out, flush=True)
