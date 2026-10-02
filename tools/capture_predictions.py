#!/usr/bin/env python3
"""Capture per-fixture probabilities from tune.py and backtest.py in a given
code directory, on one frozen data snapshot. Advisory; writes only --out.

    python3 replay.py --freeze audit-out/snapshot.json
    python3 tools/capture_predictions.py --code-dir . --snapshot audit-out/snapshot.json --out audit-out/after.json
    git worktree add /tmp/fa-main main
    python3 tools/capture_predictions.py --code-dir /tmp/fa-main --snapshot audit-out/snapshot.json --out audit-out/before.json
    python3 tools/compare_predictions.py audit-out/before.json audit-out/after.json

Keys are "split|code|date|home|away"; values [p_home, p_draw, p_away, outcome].
Standard library only.
"""
import argparse, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--code-dir", required=True, help="the checkout whose tune.py/backtest.py to run")
ap.add_argument("--snapshot", required=True, help="frozen data from replay.py --freeze")
ap.add_argument("--out", required=True)
args = ap.parse_args()
code_dir, snap, out = (os.path.abspath(p) for p in (args.code_dir, args.snapshot, args.out))
sys.path.insert(0, code_dir)
os.chdir(code_dir)                 # calibration.json and friends come from that checkout
import tune as T, backtest as B, engine as E, sources as S

with open(snap) as f:
    doc = json.load(f)
data = {tuple(k.split("|")): v for k, v in doc["data"].items()}
cal = E.CALIBRATION
res = {"snapshot": doc.get("sha256"), "codeDir": code_dir, "tune": {}, "backtest": {}}
for split in ("fit", "check"):
    for lh, la, y, code, d, h, a in T.lambdas(data, split, meta=True):
        p = T.outcome(lh, la, E.RHO)
        t = T.curve_T(max(p), cal) if cal else E.TEMPERATURE
        q = [max(x, 1e-12) ** (1 / t) for x in p]
        s = sum(q)
        res["tune"][f"{split}|{code}|{d}|{h}|{a}"] = [x / s for x in q] + [y]
    orig = S.fetch_season
    S.fetch_season = lambda c, s, cache=None: ((data.get((c, s)) or []), bool(data.get((c, s))))
    try:
        for code in T.codes():
            ts, ps = T.splits(code)[split]
            test = sorted(data.get((code, ts)) or [], key=lambda m: m[0])
            rows = B.evaluate([code], ts, ps, verbose=False)
            if not rows:
                continue
            keys = ([(r["date"], r["home"], r["away"]) for r in rows] if "home" in rows[0]
                    else [(m[0], m[1], m[2]) for m in test])   # older backtest.py rows carry no teams
            for r, (d, h, a) in zip(rows, keys):
                res["backtest"][f"{split}|{code}|{d}|{h}|{a}"] = (
                    list(r["p"]) + [{"h": 0, "d": 1, "a": 2}[r["actual"]]])
    finally:
        S.fetch_season = orig
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(res, f)
print({k: len(v) for k, v in res.items() if isinstance(v, dict)}, file=sys.stderr)
