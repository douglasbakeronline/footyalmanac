"""Core-league mid-band check on the walk-forward replay (22 Oct 2026).

Advisory, writes audit-out/core-midband.json only. History only (Rule 1).

claude/midband-calibration-2026-10-21.md found core-league 65-75% calls on
the live record landing ~87% against ~69% quoted. This asks the same of the
replay, which Rule 1 allows: every core-league fixture (tune.codes(), the
leagues the calibration curve is fitted on), live engine and live curve,
win picks only, the strict test (did the pick win).

For each season (fit 2025/26, check 2026/27) and band: n, quoted, landed,
the gap, and a 95% bootstrap interval on the gap, resampled by fixture.
A gap is real for a decision only if it holds on BOTH seasons (Rule 3);
one season alone is a candidate, not a change.

    python3 tools/core_midband_replay.py [--cache .tunecache]
"""
import argparse, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import predictability as P
import tune

BANDS = [(0.55, 0.60), (0.60, 0.65), (0.65, 0.70), (0.70, 0.75), (0.75, 0.80), (0.80, 1.01)]


def ci(rows, reps=2000, seed=5):
    rng = random.Random(seed)
    n = len(rows)
    gaps = []
    for _ in range(reps):
        s = [rows[rng.randrange(n)] for _ in range(n)]
        gaps.append(sum(r["hit"] for r in s) / n - sum(r["conf"] for r in s) / n)
    gaps.sort()
    return round(gaps[int(0.025 * reps)], 4), round(gaps[int(0.975 * reps)], 4)


def table(rows):
    out = []
    for lo, hi in BANDS + [(0.65, 0.75)]:
        b = [r for r in rows if lo <= r["conf"] < hi and r["pick"] != 1]
        if not b:
            continue
        q = sum(r["conf"] for r in b) / len(b)
        h = sum(r["hit"] for r in b) / len(b)
        lo_ci, hi_ci = ci(b) if len(b) >= 20 else (None, None)
        out.append({"band": f"{lo:.0%}-{min(hi, 1):.0%}", "n": len(b), "quoted": round(q, 4),
                    "landed": round(h, 4), "gap": round(h - q, 4), "ci": [lo_ci, hi_ci]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tunecache"))
    args = ap.parse_args()
    data = tune.load(args.cache)
    res = {}
    for split in ("fit", "check"):
        rows = P.build_rows(data, split)
        res[split] = {"fixtures": len(rows), "bands": table(rows)}
        print(f"\n{split} season: {len(rows)} fixtures (win picks only below)")
        print(f"  {'band':9} {'n':>5} {'quoted':>7} {'landed':>7} {'gap':>7}  95% interval")
        for b in res[split]["bands"]:
            c = "" if b["ci"][0] is None else f"[{b['ci'][0]:+.3f}, {b['ci'][1]:+.3f}]"
            print(f"  {b['band']:9} {b['n']:5} {b['quoted']:7.1%} {b['landed']:7.1%} {b['gap']:+7.3f}  {c}")
    os.makedirs("audit-out", exist_ok=True)
    json.dump(res, open(os.path.join("audit-out", "core-midband.json"), "w"), indent=1)
    print("\n  advisory only. A gap must hold on both seasons before anything changes (rule 3).")


if __name__ == "__main__":
    main()
