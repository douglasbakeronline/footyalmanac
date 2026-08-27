#!/usr/bin/env python3
"""
Walk-forward backtest.

For each match of the test season, the model may only use:
  - the previous season's completed results, and
  - matches from the test season that kicked off before this one.

That is exactly the information the live dashboard has, so the numbers below
are an honest estimate of what it will do in production rather than a fit to
data it has already seen.

    python3 backtest.py --season 2025-26 --prior 2024-25

Metrics
  Accuracy   how often the highest-probability outcome was the result
  Log loss   penalises confident errors hard. Lower is better.
  Brier      mean squared error across the three outcomes. Lower is better.
  Calibration  when the model says 70%, does it happen 70% of the time?
"""
import argparse, os, sys
from collections import defaultdict
from math import log

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

EPS = 1e-9


def evaluate(codes, season, prior_season, cache=None, blend_k=None, verbose=True):
    if blend_k is not None:
        E.BLEND_K = blend_k

    rows = []
    for code in codes:
        prior, ok_p = S.fetch_season(code, prior_season, cache)
        test, ok_t = S.fetch_season(code, season, cache)
        if not ok_p or not ok_t or not prior or not test:
            continue

        prior_tbl = E.build_table(prior)
        prior_rt = E.strength_from_table(prior_tbl)
        mu = E.league_goal_rate(prior_tbl)
        tier = E.LEAGUES[code]["tier"]

        # Teams that were not in this division last season need their rating
        # imported. Without a full pyramid to hand we fall back to league
        # average, which is roughly right for a promoted side anyway.
        base = {}
        for t in {m[1] for m in test} | {m[2] for m in test}:
            base[t] = prior_rt.get(t, {"att": 1.0, "def": 1.0})

        test = sorted(test, key=lambda m: m[0])
        played = defaultdict(list)   # team -> list of (date, res, pts)
        running = []                 # matches so far this season

        for date, h, a, hg, ag in test:
            tbl = E.build_table(running)
            cur = E.strength_from_table(tbl) if running else {}

            def rt(team):
                r = tbl.get(team)
                p = r["P"] if r else 0
                return E.blend(base[team], cur.get(team), p), r

            rh, rowh = rt(h)
            ra, rowa = rt(a)
            fh = E.form_factor(E.form_points(rowh))
            fa = E.form_factor(E.form_points(rowa))

            p = E.match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"],
                                      mu, tier=tier, form_h=fh, form_a=fa)
            actual = "h" if hg > ag else ("a" if ag > hg else "d")
            rows.append({
                "code": code, "date": date, "played": (rowh["P"] if rowh else 0),
                "p": (p["home"], p["draw"], p["away"]),
                "actual": actual, "conf": p["confidence"],
                "pick": max((p["home"], "h"), (p["draw"], "d"), (p["away"], "a"))[1],
            })
            running.append((date, h, a, hg, ag))

    return rows


def summarise(rows, label=""):
    if not rows:
        return None
    n = len(rows)
    idx = {"h": 0, "d": 1, "a": 2}
    hit = sum(1 for r in rows if r["pick"] == r["actual"])
    ll = -sum(log(max(r["p"][idx[r["actual"]]], EPS)) for r in rows) / n
    br = sum(sum((r["p"][i] - (1 if idx[r["actual"]] == i else 0)) ** 2
                 for i in range(3)) for r in rows) / n
    # baselines
    home_hit = sum(1 for r in rows if r["actual"] == "h") / n
    base_ll = -sum(log(max([home_hit, (1 - home_hit) / 2, (1 - home_hit) / 2][idx[r["actual"]]], EPS))
                   for r in rows) / n
    print(f"\n{label}  n={n}")
    print(f"  accuracy        {hit/n:6.1%}   (always-home baseline {home_hit:.1%})")
    print(f"  log loss        {ll:6.4f}   (baseline {base_ll:.4f})")
    print(f"  Brier score     {br:6.4f}")
    return {"n": n, "acc": hit / n, "ll": ll, "brier": br}


def calibration(rows, bins=8):
    print("\n  calibration of the top pick")
    print("  confidence band     picks    hit rate   expected")
    buckets = defaultdict(list)
    for r in rows:
        buckets[min(int(r["conf"] * bins), bins - 1)].append(r)
    for b in sorted(buckets):
        g = buckets[b]
        lo, hi = b / bins, (b + 1) / bins
        hit = sum(1 for r in g if r["pick"] == r["actual"]) / len(g)
        exp = sum(r["conf"] for r in g) / len(g)
        flag = "" if abs(hit - exp) < 0.05 else ("  over-confident" if exp > hit else "  under-confident")
        print(f"  {lo:5.0%} - {hi:5.0%}   {len(g):7d}   {hit:8.1%}   {exp:8.1%}{flag}")


def by_confidence(rows):
    print("\n  if you only backed the most confident games")
    ranked = sorted(rows, key=lambda r: -r["conf"])
    for cut in (0.05, 0.10, 0.25, 0.50, 1.00):
        g = ranked[:max(1, int(len(ranked) * cut))]
        hit = sum(1 for r in g if r["pick"] == r["actual"]) / len(g)
        print(f"  top {cut:4.0%} by confidence   n={len(g):5d}   hit rate {hit:6.1%}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", default="2025-26")
    ap.add_argument("--prior", default="2024-25")
    ap.add_argument("--cache", default=None)
    ap.add_argument("--tune", action="store_true", help="sweep the blend constant")
    args = ap.parse_args()

    codes = list(E.LEAGUES.keys())
    print(f"backtesting {args.season} using {args.prior} as the prior ...", file=sys.stderr)
    rows = evaluate(codes, args.season, args.prior, args.cache)
    if not rows:
        print("no data", file=sys.stderr); return

    summarise(rows, "ALL COMPETITIONS")
    calibration(rows)
    by_confidence(rows)

    print("\n  by competition")
    per = defaultdict(list)
    for r in rows:
        per[r["code"]].append(r)
    print(f"  {'league':22} {'n':>5} {'acc':>7} {'logloss':>9}")
    for c in sorted(per, key=lambda c: E.LEAGUES[c]["order"]):
        g = per[c]
        idx = {"h": 0, "d": 1, "a": 2}
        acc = sum(1 for r in g if r["pick"] == r["actual"]) / len(g)
        ll = -sum(log(max(r["p"][idx[r["actual"]]], EPS)) for r in g) / len(g)
        nm = f"{E.LEAGUES[c]['country']} {E.LEAGUES[c]['name']}"[:22]
        print(f"  {nm:22} {len(g):5d} {acc:7.1%} {ll:9.4f}")

    print("\n  early season only (fewer than 6 matches played)")
    early = [r for r in rows if r["played"] < 6]
    summarise(early, "  cold start")

    if args.tune:
        print("\n  blend constant sweep")
        for k in (2, 4, 6, 8, 12, 20):
            rs = evaluate(codes, args.season, args.prior, args.cache, blend_k=k)
            idx = {"h": 0, "d": 1, "a": 2}
            ll = -sum(log(max(r["p"][idx[r["actual"]]], EPS)) for r in rs) / len(rs)
            acc = sum(1 for r in rs if r["pick"] == r["actual"]) / len(rs)
            print(f"    K={k:3d}   logloss {ll:.4f}   accuracy {acc:.1%}")


if __name__ == "__main__":
    main()
