#!/usr/bin/env python3
"""Damping the FIFA ranking's big lifts (12 Nov 2026): eleven pre-registered
variants (shrink the lift, cap it, shrink only above 10 points) fitted on
Oct 2022-Sep 2023 and checked on Oct 2023-Oct 2024 against the live
adjustment, pick log loss, paired bootstrap. Advisory. Run: python3
tools/fifa_lift_damping.py from the repo root (needs ranktest.py's cache).
claude/fifa-lift-damping-2026-11-12.md."""
import runpy, sys, io, contextlib, math, random, json
sys.path.insert(0, '.')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path('ranktest.py')
out = g['out']; ll = g['ll']; boot = g['boot']
print(buf.getvalue()[-2500:])
def variant(o, kind, x):
    lift = o['adj'] - o['raw']
    if kind == 'live': return o['adj']
    if kind == 'shrink': return o['raw'] + x * lift
    if kind == 'cap': return o['raw'] + min(lift, x)
    if kind == 'shrinkbig': return o['raw'] + (lift if lift <= 0.10 else 0.10 + x * (lift - 0.10))
grid = [('shrink', s) for s in (0.6, 0.7, 0.8, 0.9)] + [('cap', c) for c in (0.08, 0.10, 0.15, 0.20)] + [('shrinkbig', s) for s in (0.3, 0.5, 0.7)]
fit = [o for o in out if o['date'] < '2023-10-01']; chk = [o for o in out if o['date'] >= '2023-10-01']
def L(sel, k, x): return [ll(variant(o, k, x), o['y']) for o in sel]
base_f, base_c = L(fit, 'live', 0), L(chk, 'live', 0)
print(f"fit n={len(fit)} check n={len(chk)}; live LL fit {sum(base_f)/len(fit):.4f} check {sum(base_c)/len(chk):.4f}")
res = []
for k, x in grid:
    f = L(fit, k, x); c = L(chk, k, x)
    mf, pf = boot(f, base_f); mc, pc = boot(c, base_c)
    res.append((mf, k, x, mc, pc, pf))
    print(f"{k:9s} {x:4}: fit {mf:+.4f} (p {pf:.2f})  check {mc:+.4f} (p(worse) {pc:.2f})")
best = min(res)
print("best on fit:", best[1], best[2], "check gain", -best[3], "p(worse)", best[4])
k, x = best[1], best[2]
big = [o for o in out if o['adj'] - o['raw'] >= 0.20]
print("20+ lifts: n", len(big), "landed", sum(o['y'] for o in big)/len(big), "live quoted", sum(o['adj'] for o in big)/len(big), "variant quoted", sum(variant(o,k,x) for o in big)/len(big))
for lo, hi in ((0, .05), (.05, .10), (.10, .15), (.15, .20), (.20, 1)):
    s = [o for o in chk if lo <= o['adj'] - o['raw'] < hi]
    if s: print(f" check uplift {lo:.2f}-{hi:.2f} n={len(s)} landed {sum(o['y'] for o in s)/len(s):.3f} live {sum(o['adj'] for o in s)/len(s):.3f} variant {sum(variant(o,k,x) for o in s)/len(s):.3f}")
