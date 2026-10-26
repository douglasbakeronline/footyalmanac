#!/usr/bin/env python3
"""
Is the home/away tilt overstated? (26 Oct 2026)

    python3 tools/home_away_tilt.py [--json audit-out/home-away-tilt.json]
    python3 tools/home_away_tilt.py --snapshot FILE      (replay.py --freeze)

Why: on the live record (diagnostic only, never fitted on) away picks quote
44.7% and land 51.7% (n 1,834, z 5.1 on clean rows) while home picks land on
quote; the mean quoted triple is 0.443 / 0.266 / 0.291 against an actual
0.436 / 0.253 / 0.311. The calibration curve acts on the top probability
only, so it cannot move probability from home to away; the tilt itself can.

What is tested, on the walk-forward replay (tune.lambdas, the live engine
functions), under the live calibration curve (tune.live_baseline), paired and
bootstrapped against the live configuration on the same fixtures:

  1. ha_scale   the home/away tilt (engine.venue_multipliers), 0.80 to 1.00
                in 0.02 steps. 1.00 is live. The goal level is untouched.
  2. RHO        the Dixon-Coles draw term, the one draw multiplier the engine
                has, around the live -0.06.
  3. both       the best ha_scale with the best RHO, declared after 1 and 2.

The candidate for each is the best value on the fit season (last completed
season); it is then checked on the current season under CLAUDE.md's gates:
>= 250 check fixtures, p(worse) <= 0.30, gain >= 0.0005. Rule 4: the
candidate is also scored with the calibration curve refitted for it on the
fit season, so a gain cannot be the curve compensating.

Alongside the log loss, the thing the change is meant to fix: for the picks
the model makes (its top probability), quoted against landed, home and away
apart, and the mean quoted triple against the actual split, before and after.

Only the core leagues (tune.codes) are in the replay. The API-Football wider
leagues (AF_EXTRA) have no check season there at all, so a tilt by family
cannot be gated and is not tried: one global scale, gated on the core.
Advisory: writes nothing but its own JSON report. Standard library only.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import engine as E
import replay as R
import tune as T

HA_GRID = [round(0.80 + 0.02 * i, 2) for i in range(11)]       # 0.80 .. 1.00
RHO_GRID = [-0.10, -0.08, -0.07, -0.06, -0.05, -0.04, -0.03, -0.02, 0.0]


def probs_under(raws, b):
    """The tempered (home, draw, away, y) the site would publish, under a
    baseline or candidate as tune.score_under takes it."""
    out = []
    for h, d, a, y in raws:
        if b["kind"] == "curve":
            t = T.curve_T(max(h, d, a), {"a": b["a"], "b": b["b"]})
        else:
            t = b["T"]
        p = (h, d, a)
        if t != 1.0:
            q = [max(x, T.EPS) ** (1.0 / t) for x in p]
            s = sum(q)
            p = (q[0] / s, q[1] / s, q[2] / s)
        out.append(p + (y,))
    return out


def side_report(probs):
    """Quoted v landed for the model's picks, by side, and the mean triple
    against the actual split. `probs` are tempered (h, d, a, y)."""
    sides = {0: "home", 1: "draw", 2: "away"}
    by = {s: {"n": 0, "quoted": 0.0, "landed": 0} for s in sides.values()}
    tri_q = [0.0, 0.0, 0.0]; tri_a = [0, 0, 0]
    for h, d, a, y in probs:
        p = (h, d, a)
        k = p.index(max(p))
        b = by[sides[k]]
        b["n"] += 1; b["quoted"] += p[k]; b["landed"] += (y == k)
        for i in range(3):
            tri_q[i] += p[i]
        tri_a[y] += 1
    n = len(probs)
    out = {}
    for s, b in by.items():
        if b["n"]:
            q = b["quoted"] / b["n"]; l = b["landed"] / b["n"]
            sd = (q * (1 - q) / b["n"]) ** 0.5
            out[s] = {"n": b["n"], "quoted": round(q, 4), "landed": round(l, 4),
                      "gap": round(l - q, 4), "z": round((l - q) / sd, 2) if sd else None}
        else:
            out[s] = {"n": 0}
    out["meanQuoted"] = [round(x / n, 4) for x in tri_q]
    out["actual"] = [round(x / n, 4) for x in tri_a]
    return out


def fmt_side(r):
    def one(s):
        b = r[s]
        if not b["n"]:
            return f"{s} picks: none"
        return (f"{s} picks n {b['n']}: quoted {b['quoted']:.1%}, landed {b['landed']:.1%} "
                f"({b['gap']:+.1%}, z {b['z']:+.1f})")
    q, a = r["meanQuoted"], r["actual"]
    return (f"    {one('home')}\n    {one('away')}\n    {one('draw')}\n"
            f"    mean quoted {q[0]:.3f} / {q[1]:.3f} / {q[2]:.3f}; "
            f"actual {a[0]:.3f} / {a[1]:.3f} / {a[2]:.3f}")


def refit_curve(fit_raw):
    """tune.fit_calibration's grid search, on raw probabilities already in
    hand: the curve a candidate would get under rule 4."""
    def search(a_lo, a_hi, a_step, b_lo, b_hi, b_step):
        best = (float("inf"), None)
        a = a_lo
        while a <= a_hi + 1e-9:
            b = b_lo
            while b <= b_hi + 1e-9:
                cal = {"a": round(a, 3), "b": round(b, 3)}
                ll = T.mean(T.score_raw(fit_raw, cal=cal)[0])
                if ll < best[0]:
                    best = (ll, cal)
                b += b_step
            a += a_step
        return best
    coarse = search(0.90, 1.35, 0.025, -2.0, 2.0, 0.25)
    a0, b0 = coarse[1]["a"], coarse[1]["b"]
    best = search(a0 - 0.025, a0 + 0.025, 0.005, b0 - 0.25, b0 + 0.25, 0.05)
    return (coarse if coarse[0] < best[0] else best)[1]


def gates_for(n, m, pw):
    return {"enoughData": n >= T.MIN_HOLDOUT, "notWorse": pw <= T.MAX_P_WORSE,
            "worthIt": -m >= T.MIN_GAIN}


def run(data, out_json=None):
    live = T.live_baseline()
    for split in ("fit", "check"):
        R.report_exclusions(T.exclusions(data, split))
    usable_fit, _ = R.coverage(data, T.codes(), T.splits, "fit")
    usable_chk, _ = R.coverage(data, T.codes(), T.splits, "check")

    # replay once per ha_scale, grid once per (ha_scale, rho)
    rows = {}
    for s in ("fit", "check"):
        for v in HA_GRID:
            rows[(s, v)] = T.lambdas(data, s, {"ha_scale": v} if v != 1.0 else None)
    raw = {}
    def raws(s, v, rho):
        key = (s, v, rho)
        if key not in raw:
            raw[key] = T.raw_probs(rows[(s, v)], rho)
        return raw[key]
    def per(s, v, rho, b=live):
        return T.score_under(raws(s, v, rho), b)

    live_ha, live_rho = 1.0, E.RHO
    base_fit, acc_fit, _ = per("fit", live_ha, live_rho)
    base_chk, acc_chk, _ = per("check", live_ha, live_rho)
    n_fit, n_chk = len(base_fit), len(base_chk)
    print(f"\nbaseline = live: {T.describe(live)} [{live['source']}], ha_scale {live_ha:g}, RHO {live_rho:g}")
    print(f"fit season ({len(usable_fit)} competitions): {n_fit} fixtures, log loss {T.mean(base_fit):.4f}, acc {acc_fit:.2%}")
    print(f"check season ({len(usable_chk)} competitions): {n_chk} fixtures, log loss {T.mean(base_chk):.4f}, acc {acc_chk:.2%}")
    print("\nlive picks, quoted v landed")
    side_live = {"fit": side_report(probs_under(raws("fit", live_ha, live_rho), live)),
                 "check": side_report(probs_under(raws("check", live_ha, live_rho), live))}
    for s in ("fit", "check"):
        print(f"  {s}:\n{fmt_side(side_live[s])}")

    report = {"baseline": {**live, "ha_scale": live_ha, "rho": live_rho,
                           "fit": {"n": n_fit, "logLoss": round(T.mean(base_fit), 4), "acc": round(acc_fit, 4)},
                           "check": {"n": n_chk, "logLoss": round(T.mean(base_chk), 4), "acc": round(acc_chk, 4)},
                           "sides": side_live},
              "sweeps": {}, "candidates": {}}

    def sweep(name, grid, key):
        print(f"\n{name} sweep (everything else live; Δ log loss against live, negative better)")
        print(f"  {'value':>7} {'fit Δ':>9} {'sd':>7} {'p(worse)':>9} {'acc':>7} | {'check Δ':>9} {'sd':>7} {'p(worse)':>9} {'acc':>7}")
        out = []
        for v in grid:
            ha, rho = (v, live_rho) if key == "ha" else (live_ha, v)
            pf, af, _ = per("fit", ha, rho)
            pc, ac, _ = per("check", ha, rho)
            mf, sf, pwf = T.paired(pf, base_fit)
            mc, sc, pwc = T.paired(pc, base_chk)
            print(f"  {v:>7g} {mf:>+9.4f} {sf:>7.4f} {pwf:>9.2f} {af:>7.2%} | {mc:>+9.4f} {sc:>7.4f} {pwc:>9.2f} {ac:>7.2%}")
            out.append({"value": v, "fit": {"delta": round(mf, 5), "sd": round(sf, 5), "pWorse": round(pwf, 3), "acc": round(af, 4)},
                        "check": {"delta": round(mc, 5), "sd": round(sc, 5), "pWorse": round(pwc, 3), "acc": round(ac, 4)}})
        report["sweeps"][key] = out
        best = min(out, key=lambda r: r["fit"]["delta"])
        return best["value"]

    best_ha = sweep("ha_scale", HA_GRID, "ha")
    best_rho = sweep("RHO", RHO_GRID, "rho")

    def candidate(label, ha, rho):
        pf, af, _ = per("fit", ha, rho)
        pc, ac, _ = per("check", ha, rho)
        mf, sf, pwf = T.paired(pf, base_fit)
        mc, sc, pwc = T.paired(pc, base_chk)
        g = gates_for(n_chk, mc, pwc)
        # rule 4: refit the curve for the candidate on the fit season, then
        # score the check season with that curve against live-with-live-curve
        cal = refit_curve(raws("fit", ha, rho))
        pf2, af2, _ = per("fit", ha, rho, T.as_curve(cal))
        pc2, ac2, _ = per("check", ha, rho, T.as_curve(cal))
        mf2, sf2, pwf2 = T.paired(pf2, base_fit)
        mc2, sc2, pwc2 = T.paired(pc2, base_chk)
        g2 = gates_for(n_chk, mc2, pwc2)
        sides = {"fit": side_report(probs_under(raws("fit", ha, rho), live)),
                 "check": side_report(probs_under(raws("check", ha, rho), live))}
        ok = all(g.values())
        print(f"\ncandidate {label}: ha_scale {ha:g}, RHO {rho:g}")
        print(f"  live curve:   fit {mf:+.4f} (sd {sf:.4f}, p(worse) {pwf:.2f}); "
              f"check {n_chk} fixtures {mc:+.4f} (sd {sc:.4f}, p(worse) {pwc:.2f}), acc {acc_chk:.2%} -> {ac:.2%}")
        print(f"  gates: " + ", ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in g.items()) + f"  =>  {'PASS' if ok else 'FAIL'}")
        print(f"  refit curve T = {cal['a']} + {cal['b']} x (conf - 0.45): fit {mf2:+.4f} (p {pwf2:.2f}); "
              f"check {mc2:+.4f} (sd {sc2:.4f}, p(worse) {pwc2:.2f}), acc {ac2:.2%}; gates "
              + ", ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in g2.items()))
        print("  picks, quoted v landed (live curve):")
        for s in ("fit", "check"):
            print(f"  {s}:\n{fmt_side(sides[s])}")
        report["candidates"][label] = {
            "ha_scale": ha, "rho": rho,
            "fit": {"delta": round(mf, 5), "sd": round(sf, 5), "pWorse": round(pwf, 3), "acc": round(af, 4)},
            "check": {"n": n_chk, "delta": round(mc, 5), "sd": round(sc, 5), "pWorse": round(pwc, 3),
                      "accLive": round(acc_chk, 4), "acc": round(ac, 4)},
            "gates": g, "pass": ok,
            "refitCurve": {"cal": cal,
                           "fit": {"delta": round(mf2, 5), "pWorse": round(pwf2, 3)},
                           "check": {"delta": round(mc2, 5), "sd": round(sc2, 5), "pWorse": round(pwc2, 3), "acc": round(ac2, 4)},
                           "gates": g2, "pass": all(g2.values())},
            "sides": sides}
        return ok

    results = {}
    results["ha_scale"] = candidate("ha_scale", best_ha, live_rho) if best_ha != live_ha else None
    if best_ha == live_ha:
        print("\ncandidate ha_scale: the live 1.0 is best on the fit season; nothing to check")
    results["rho"] = candidate("rho", live_ha, best_rho) if best_rho != live_rho else None
    if best_rho == live_rho:
        print("\ncandidate rho: the live RHO is best on the fit season; nothing to check")
    if best_ha != live_ha and best_rho != live_rho:
        results["both"] = candidate("both", best_ha, best_rho)

    # by tier on the check season, for the record: the check set is nearly all tier 1
    if results.get("ha_scale") is not None:
        tiers = {}
        meta = T.lambdas(data, "check", {"ha_scale": best_ha} if best_ha != 1.0 else None, meta=True)
        base_meta = T.lambdas(data, "check", None, meta=True)
        pl = T.score_under(T.raw_probs([r[:3] for r in base_meta]), live)[0]
        pc = T.score_under(T.raw_probs([r[:3] for r in meta]), live)[0]
        for r, x, y in zip(base_meta, pl, pc):
            t = E.LEAGUES[r[3]]["tier"]
            tiers.setdefault(t, []).append((x, y))
        print(f"\ncheck season by tier, ha_scale {best_ha:g} v live (live curve)")
        for t in sorted(tiers):
            xs = tiers[t]
            d = sum(y - x for x, y in xs) / len(xs)
            print(f"  tier {t}: {len(xs)} fixtures, Δ {d:+.4f}")
            report.setdefault("checkByTier", {})[str(t)] = {"n": len(xs), "delta": round(d, 5)}

    report["results"] = results
    if out_json:
        os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)
        json.dump(report, open(out_json, "w"), indent=1)
        print(f"\nwrote {out_json}")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(HERE, ".tunecache"))
    ap.add_argument("--snapshot", metavar="FILE", help="frozen snapshot (replay.py --freeze)")
    ap.add_argument("--json", help="write the full report here")
    args = ap.parse_args()
    if args.snapshot:
        data, _, digest = R.load_snapshot(args.snapshot)
        print(f"snapshot {digest} ({len(data)} seasons)", file=sys.stderr)
    else:
        os.makedirs(args.cache, exist_ok=True)
        data = T.load(args.cache)
    run(data, args.json)


if __name__ == "__main__":
    main()
