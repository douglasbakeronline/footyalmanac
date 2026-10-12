"""Replay of the Daily List league bar (advisory, writes nothing).

Walk-forward league picks (tune.lambdas, live calibration), win picks only.
For each candidate bar: n, hit rate, and a paired bootstrap of the hit-rate
change from the live 80% list. Celtic's Law and prior-season gates are not
applied, so rates are slightly harsher than the live list.
Usage: python3 tools/list_bar_replay.py [--cache DIR]
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E, tune as T

BARS = [0.70, 0.75, 0.775, 0.80, 0.825, 0.85]


def picks(data, split):
    rows = T.lambdas(data, split, meta=True)
    out = []
    for lh, la, y, code, d, h, a in rows:
        raw = T.outcome(lh, la, E.RHO)
        c = max(raw)
        t = T.curve_T(c, E.CALIBRATION) if E.CALIBRATION else E.TEMPERATURE
        q = [max(x, 1e-9) ** (1 / t) for x in raw]
        s = sum(q)
        p = [x / s for x in q]
        i = p.index(max(p))
        if i == 1:
            continue
        out.append((p[i], int(i == y), code))
    return out


def boot(ps, lo, hi=None, reps=2000, seed=7):
    """Hit-rate change of the bar `lo` list against the 80% list, resampling fixtures."""
    rng = random.Random(seed)
    n = len(ps)
    d = []
    for _ in range(reps):
        a = [0, 0]; b = [0, 0]
        for _ in range(n):
            c, hit, _c = ps[rng.randrange(n)]
            if c >= lo: a[0] += 1; a[1] += hit
            if c >= 0.80: b[0] += 1; b[1] += hit
        if a[0] and b[0]:
            d.append(100 * (a[1] / a[0] - b[1] / b[0]))
    d.sort()
    return d[len(d) // 2], d[int(.05 * len(d))], d[int(.95 * len(d))]


def main():
    cache = sys.argv[sys.argv.index("--cache") + 1] if "--cache" in sys.argv else "cache"
    data = T.load(cache)
    for split in ("fit", "check"):
        ps = picks(data, split)
        print(f"\n{split}: {len(ps)} win picks")
        for bar in BARS:
            sel = [p for p in ps if p[0] >= bar]
            n = len(sel); h = sum(p[1] for p in sel)
            m = boot(ps, bar) if n > 10 and len(ps) > 100 else (0, 0, 0)
            print(f"  >= {bar:.3f}: n={n:4d} hit={100*h/max(n,1):5.1f}%  vs 80%: {m[0]:+.1f} ({m[1]:+.1f} to {m[2]:+.1f})")
        by = {}
        for c, hit, code in ps:
            if c >= 0.80:
                by.setdefault(code, [0, 0]); by[code][0] += 1; by[code][1] += hit
        top = sorted(by.items(), key=lambda kv: -kv[1][0])[:8]
        print("  per league at 80%:", ", ".join(f"{k} {v[1]}/{v[0]}" for k, v in top))


if __name__ == "__main__":
    main()
