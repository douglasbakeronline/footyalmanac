#!/usr/bin/env python3
"""Compare two captures from tools/capture_predictions.py on the fixtures
present in all four runs (old/new x tune/backtest). Advisory; prints only.

    python3 tools/compare_predictions.py audit-out/before.json audit-out/after.json
"""
import json, math, random, sys

if len(sys.argv) != 3:
    sys.exit(__doc__)
with open(sys.argv[1]) as f:
    B = json.load(f)
with open(sys.argv[2]) as f:
    A = json.load(f)
if B.get("snapshot") != A.get("snapshot"):
    sys.exit("captures were made on different snapshots; refusing to compare")


def metrics(rows):
    n = len(rows)
    ll = [-math.log(max(r[r[3]], 1e-12)) for r in rows]
    hit = sum(1 for r in rows if max(range(3), key=lambda j: r[j]) == r[3])
    br = sum(sum((r[j] - (j == r[3])) ** 2 for j in range(3)) for r in rows) / n
    return n, sum(ll) / n, hit / n, br, ll


def paired(a, b, reps=2000, seed=17):
    rng = random.Random(seed)
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    ms = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return sum(d) / n, ms[int(.025 * reps)], ms[int(.975 * reps)], sum(x > 0 for x in ms) / reps


def pick(r):
    return max(range(3), key=lambda j: r[j])


print(f"snapshot {A.get('snapshot')}")
for split in ("fit", "check"):
    runs = {"old tune": B["tune"], "old backtest": B["backtest"],
            "new tune": A["tune"], "new backtest": A["backtest"]}
    keys = sorted(set.intersection(*[{k for k in r if k.startswith(split + "|")} for r in runs.values()]))
    print(f"\n{split}: {len(keys)} identical fixtures in all four runs")
    print(f"  {'run':14} {'n':>5} {'log loss':>9} {'accuracy':>9} {'Brier':>7}")
    per = {}
    for name, r in runs.items():
        n, ll, acc, br, per[name] = metrics([r[k] for k in keys])
        print(f"  {name:14} {n:5} {ll:9.5f} {acc:9.2%} {br:7.5f}")
    md = max(abs(x - y) for k in keys for x, y in zip(A["tune"][k][:3], A["backtest"][k][:3]))
    print(f"  new tune vs new backtest: max probability difference {md:.1e}")
    for x, y in (("old tune", "old backtest"), ("new tune", "old tune"), ("new backtest", "old backtest")):
        d, lo, hi, pw = paired(per[x], per[y])
        diff = [max(abs(p - q) for p, q in zip(runs[x][k][:3], runs[y][k][:3])) for k in keys]
        flips = sum(pick(runs[x][k]) != pick(runs[y][k]) for k in keys)
        print(f"  {x} minus {y}: {d:+.5f} log loss, 95% [{lo:+.5f}, {hi:+.5f}], "
              f"share worse {pw:.2f}; {sum(v > 1e-9 for v in diff)} fixtures differ "
              f"(mean {sum(diff) / len(diff):.4f}, max {max(diff):.3f}), top pick differs on {flips}")
    gone = sorted({k.split("|")[1] for k in B["tune"] if k.startswith(split + "|")}
                  - {k.split("|")[1] for k in A["tune"] if k.startswith(split + "|")})
    print(f"  competitions in the old run but excluded by the new: {gone or 'none'}")
