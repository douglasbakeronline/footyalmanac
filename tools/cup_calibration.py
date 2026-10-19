#!/usr/bin/env python3
"""Fit a calibration temperature for domestic cup ties (19 Oct 2026). Advisory.

    python3 tools/cup_calibration.py

Reads every priced tie the cup replay keeps (`current/af-cup-replay.json`
"rows", build.cup_replay version 4+): the model's home / draw / away chance
for each played tie, as of its own morning, and the result. A cup
temperature T softens those toward a coin flip, p' proportional to p^(1/T),
on top of the league calibration they already carry. T is fitted on ties
before 1 July 2026 and checked on ties after, paired and bootstrapped against
T = 1 (today's numbers), under tune.py's gates. Never fitted on record.json.
"""
import json, math, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import tune as T

SPLIT = "2026-07-01"
GRID = [round(1.0 + 0.05 * i, 2) for i in range(0, 31)]       # 1.00 to 2.50


def soften(p, t):
    q = [max(x, 1e-12) ** (1.0 / t) for x in p]
    s = sum(q)
    return [x / s for x in q]


def losses(rows, t):
    out = []
    for r in rows:
        p = soften(r["p"], t)
        out.append(-math.log(max(p["hda".index(r["res"])], 1e-12)))
    return out


def bands(rows, t, los=(0.55, 0.60, 0.70, 0.80)):
    out = []
    for lo in los:
        sel = []
        for r in rows:
            p = soften(r["p"], t)
            k = max(range(3), key=lambda i: p[i])
            if k != 1 and p[k] >= lo:
                sel.append((p[k], "hda"[k] == r["res"]))
        if sel:
            out.append((lo, len(sel), sum(h for _, h in sel) / len(sel), sum(q for q, _ in sel) / len(sel)))
    return out


def main():
    with open(os.path.join(ROOT, "current", "af-cup-replay.json")) as f:
        doc = json.load(f)
    raw = doc.get("rows") or []
    if not raw:
        sys.exit("no rows in current/af-cup-replay.json: needs cup replay version 4 (the daily build writes it)")
    rows = [{"date": d, "cup": c, "p": [ph, pd, pa], "res": res, "cross": x, "thin": th}
            for d, c, ph, pd, pa, res, x, th in raw]
    fit = [r for r in rows if r["date"] < SPLIT]
    chk = [r for r in rows if r["date"] >= SPLIT]
    print(f"{len(rows)} priced ties ({doc.get('from')} to {doc.get('to')}): fit {len(fit)} before {SPLIT}, check {len(chk)} after")
    best = min(GRID, key=lambda t: sum(losses(fit, t)) / len(fit))
    base_f, new_f = losses(fit, 1.0), losses(fit, best)
    base_c, new_c = losses(chk, 1.0), losses(chk, best)
    m_f, sd_f, pw_f = T.paired(new_f, base_f)
    m_c, sd_c, pw_c = T.paired(new_c, base_c)
    print(f"fitted cup temperature T = {best}")
    print(f"  fit   log loss {sum(base_f)/len(fit):.4f} -> {sum(new_f)/len(fit):.4f}  ({m_f:+.4f}, p(worse) {pw_f:.3f})")
    print(f"  check log loss {sum(base_c)/len(chk):.4f} -> {sum(new_c)/len(chk):.4f}  ({m_c:+.4f}, sd {sd_c:.4f}, p(worse) {pw_c:.3f})")
    gates = {"enoughData": len(chk) >= T.MIN_HOLDOUT, "notWorse": pw_c <= T.MAX_P_WORSE, "worthIt": -m_c >= T.MIN_GAIN}
    print("  gates: " + ", ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in gates.items()))
    for name, rs in (("fit", fit), ("check", chk)):
        for t in (1.0, best):
            print(f"  {name} T={t}: " + "  ".join(f"{lo:.0%}+ {n} landed {h:.1%} quoted {q:.1%}"
                                                 for lo, n, h, q in bands(rs, t)))
    return best, gates


if __name__ == "__main__":
    main()
