#!/usr/bin/env python3
"""
Test the model's constants against data it has never seen, and refit the
calibration curve when the evidence supports it.

    python3 tune.py --report          full sweep, prints a table, changes nothing
    python3 tune.py --fit             refit calibration.json if it passes the gates
    python3 tune.py --fit --dry-run   as above, but write nothing

Why this exists
---------------
backtest.py answers "how good is the model". This answers the harder question,
"is any individual constant set to the wrong number", and it has to answer it
without fooling itself. Three rules do that work:

  1. NOTHING IS EVER FITTED ON THE LIVE RECORD. record.json is the scoreboard.
     A scoreboard you tune against stops being a scoreboard, and the site's one
     honest claim is that its published numbers were published in advance.

  2. Every comparison is PAIRED. The same fixtures are scored under both
     settings and the difference is bootstrapped, so the shared difficulty of a
     particular season cancels out. An unpaired comparison of two log losses
     around 1.016 has a noise band of +/-0.005, which is wider than every real
     effect in this model, and would have said "no signal" to all of them.

  3. Anything fitted on the previous season must survive on the CURRENT one
     before it is allowed anywhere near the site.

Standard library only, like the rest of the project.
"""
import argparse, json, math, os, sys
from datetime import date as _date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

HERE = os.path.dirname(os.path.abspath(__file__))
EPS = 1e-12
MAXG = E.MAX_GOALS

# A fit is only allowed to ship if it clears all three.
MIN_HOLDOUT = 250      # fixtures in the current season before a fit means anything
MAX_P_WORSE = 0.30     # bootstrapped chance the change is actually worse
MIN_GAIN = 0.0005      # log loss improvement worth the churn


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

def codes():
    """Competitions with a league table of their own. A cup has no table to be
    average in, and ratings-only leagues carry no fixtures."""
    return [c for c, m in E.LEAGUES.items()
            if not m.get("cup") and not m.get("ratingsOnly")]


def splits(code):
    """(test, prior) for the season we fit on and the season we check on.

    Per-competition, because Brazil and the Nordics run calendar years.
    """
    m = E.LEAGUES[code]
    cur = m.get("season", "2026-27")
    prev = m.get("prev", ["2025-26", "2024-25"])
    return {"fit": (prev[0], prev[1]), "check": (cur, prev[0])}


def load(cache):
    out = {}
    for c in codes():
        for test, prior in splits(c).values():
            for s in (test, prior):
                if (c, s) in out:
                    continue
                rows, ok = S.fetch_season(c, s, cache)
                out[(c, s)] = rows if ok else []
    return out


# ---------------------------------------------------------------------------
# the rating stage, walked forward
# ---------------------------------------------------------------------------

DEFAULTS = dict(shrink=E.SHRINK_FULL_SEASON, blend_k=E.BLEND_K,
                form_cap=E.FORM_MAX, form_n=5, ha_scale=1.0)


def _strength(tbl, mu, k):
    out = {}
    for t, r in tbl.items():
        p = r[0]
        if not p:
            out[t] = (1.0, 1.0)
            continue
        w = p / (p + k)
        out[t] = (min(max(w * ((r[1] / p) / mu) + (1 - w), E.ATT_BOUNDS[0]), E.ATT_BOUNDS[1]),
                  min(max(w * ((r[2] / p) / mu) + (1 - w), E.DEF_BOUNDS[0]), E.DEF_BOUNDS[1]))
    return out


def _form(res, cap, n):
    if len(res) < 2:
        return 1.0
    last = res[-n:]
    if len(last) * 3 < 6:
        return 1.0
    dev = (sum(last) / len(last) - 1.35) / 1.65
    return 1.0 + max(-1.0, min(1.0, dev)) * cap


def lambdas(data, split, params=None):
    """Every fixture of the season, with the two expected-goal numbers the
    model would have published the morning before it kicked off.

    The table is updated incrementally rather than rebuilt per fixture, which is
    the only reason a full sweep finishes in minutes rather than hours.
    """
    p = {**DEFAULTS, **(params or {})}
    rows = []
    for code in codes():
        test_s, prior_s = splits(code)[split]
        prior, test = data.get((code, prior_s)) or [], data.get((code, test_s)) or []
        if not prior or not test:
            continue

        ptbl = E.build_table(prior)
        mu = E.league_goal_rate(ptbl)
        prior_rt = _strength({t: (r["P"], r["GF"], r["GA"]) for t, r in ptbl.items()},
                             mu, p["shrink"])

        tier = E.LEAGUES[code]["tier"]
        hm, am = E.HOME_MULT.get(tier, 1.16), E.AWAY_MULT.get(tier, 0.87)
        if p["ha_scale"] != 1.0:
            # move the home/away tilt without touching the overall goal level
            mid = math.sqrt(hm * am)
            hm, am = mid * (hm / mid) ** p["ha_scale"], mid * (am / mid) ** p["ha_scale"]

        tbl, form = {}, {}
        for d, h, a, hg, ag in sorted(test, key=lambda m: m[0]):
            cur = _strength(tbl, mu, p["shrink"]) if tbl else {}

            def rate(team):
                pri = prior_rt.get(team, (1.0, 1.0))
                n = tbl[team][0] if team in tbl else 0
                if not n or team not in cur:
                    return pri
                w = n / (n + p["blend_k"])
                c = cur[team]
                return (w * c[0] + (1 - w) * pri[0], w * c[1] + (1 - w) * pri[1])

            rh, ra = rate(h), rate(a)
            lh = max(0.15, rh[0] * ra[1] * mu * hm * _form(form.get(h, []), p["form_cap"], p["form_n"]))
            la = max(0.15, ra[0] * rh[1] * mu * am * _form(form.get(a, []), p["form_cap"], p["form_n"]))
            rows.append((lh, la, 0 if hg > ag else (1 if hg == ag else 2)))

            for t, gf, ga, pts in ((h, hg, ag, 3 if hg > ag else (1 if hg == ag else 0)),
                                   (a, ag, hg, 3 if ag > hg else (1 if hg == ag else 0))):
                r = tbl.get(t) or (0, 0, 0)
                tbl[t] = (r[0] + 1, r[1] + gf, r[2] + ga)
                form.setdefault(t, []).append(pts)
    return rows


# ---------------------------------------------------------------------------
# the grid stage
# ---------------------------------------------------------------------------

_FACT = [math.factorial(i) for i in range(MAXG + 1)]


def outcome(lh, la, rho):
    """P(home), P(draw), P(away) from the Dixon-Coles corrected grid."""
    ph = [math.exp(-lh) * lh ** i / _FACT[i] for i in range(MAXG + 1)]
    pa = [math.exp(-la) * la ** i / _FACT[i] for i in range(MAXG + 1)]
    run, home, draw, total = 0.0, 0.0, 0.0, 0.0
    for x in range(MAXG + 1):
        home += ph[x] * run          # run = P(away goals < x)
        draw += ph[x] * pa[x]
        run += pa[x]
        total += ph[x]
    total *= sum(pa)
    # the correction only touches four cells, so it is four deltas, not a regrid
    d00 = ph[0] * pa[0] * (-lh * la * rho)
    d01 = ph[0] * pa[1] * (lh * rho)
    d10 = ph[1] * pa[0] * (la * rho)
    d11 = ph[1] * pa[1] * (-rho)
    home += d10
    draw += d00 + d11
    total += d00 + d01 + d10 + d11
    return home / total, draw / total, (total - home - draw) / total


def curve_T(conf, cal):
    """Temperature as a straight line in raw confidence.

    Two parameters, deliberately. Ten free per-band temperatures fit the
    training season better and generalise worse; a line cannot chase a bin.
    """
    return min(max(cal["a"] + cal["b"] * (conf - 0.45), 0.6), 2.0)


def raw_probs(rows, rho=None):
    """The uncorrected grid output, computed once. Temperature and the
    calibration curve act on these, so a search over them never has to touch a
    Poisson grid again."""
    rho = E.RHO if rho is None else rho
    return [outcome(lh, la, rho) + (y,) for lh, la, y in rows]


def score_raw(raws, T=None, cal=None):
    """Per-fixture log loss, accuracy, and mean confidence of the top pick."""
    per, hit, confs = [], 0, []
    for h, d, a, y in raws:
        p = (h, d, a)
        c = max(p)
        t = curve_T(c, cal) if cal else (E.TEMPERATURE if T is None else T)
        if t != 1.0:
            q = [max(x, EPS) ** (1.0 / t) for x in p]
            s = q[0] + q[1] + q[2]
            p = (q[0] / s, q[1] / s, q[2] / s)
        per.append(-math.log(max(p[y], EPS)))
        if p.index(max(p)) == y:
            hit += 1
        confs.append(max(p))
    return per, hit / len(raws), sum(confs) / len(confs)


def score(rows, rho=None, T=None, cal=None):
    return score_raw(raw_probs(rows, rho), T=T, cal=cal)


# ---------------------------------------------------------------------------
# significance
# ---------------------------------------------------------------------------

def paired(a, b, reps=1500, seed=17):
    """Bootstrap the difference between two settings scored on the same
    fixtures. Returns (mean change, sd, probability the change is worse).

    Paired, because an unpaired comparison of two numbers this close is
    swamped by which season you happened to test on.
    """
    import random
    rng = random.Random(seed)
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    means = []
    for _ in range(reps):
        means.append(sum(diff[rng.randrange(n)] for _ in range(n)) / n)
    mu = sum(diff) / n
    var = sum((m - mu) ** 2 for m in means) / len(means)
    return mu, math.sqrt(var), sum(1 for m in means if m > 0) / len(means)


def mean(xs):
    return sum(xs) / len(xs)


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def report(data):
    fit = lambdas(data, "fit")
    base, base_acc, _ = score(fit)
    print(f"\nfit season: {len(fit)} fixtures, log loss {mean(base):.4f}, "
          f"accuracy {base_acc:.2%}\n")
    print(f"  {'constant':30} {'shipped':>9} {'trying':>8} {'Δ log loss':>11} "
          f"{'sd':>7} {'p(worse)':>9} {'acc':>7}")

    def trial(label, shipped, value, params=None, rho=None, T=None):
        rows = lambdas(data, "fit", params) if params else fit
        per, acc, _ = score(rows, rho=rho, T=T)
        m, sd, pw = paired(per, base)
        mark = "  <-" if pw < 0.05 and m < 0 else ""
        print(f"  {label:30} {shipped:>9} {value:>8} {m:>+11.4f} {sd:>7.4f} "
              f"{pw:>9.2f} {acc:>7.2%}{mark}")

    for T in (1.00, 1.05, 1.10, 1.25):
        trial("TEMPERATURE", 1.15, T, T=T)
    for r in (-0.12, -0.08, -0.04, 0.0):
        trial("RHO", -0.06, r, rho=r)
    for v in (2, 3, 4, 8, 12):
        trial("SHRINK_FULL_SEASON", 6, v, {"shrink": v})
    for v in (3, 4, 8, 12, 20):
        trial("BLEND_K", 6, v, {"blend_k": v})
    for v in (0.0, 0.10, 0.15, 0.20, 0.30):
        trial("FORM_MAX", 0.05, v, {"form_cap": v})
    for v in (3, 8, 10):
        trial("form window", 5, v, {"form_n": v})
    for v in (0.8, 0.9, 1.1, 1.2):
        trial("home advantage scale", 1.0, v, {"ha_scale": v})
    print("\n  a change is worth making only where p(worse) is small AND the "
          "same change\n  survives on the current season. Run --fit for that check.")


# ---------------------------------------------------------------------------
# calibration fit
# ---------------------------------------------------------------------------

def fit_calibration(data, verbose=True):
    """Fit the temperature curve on the last completed season, then check it on
    the current one. Returns (calibration, verdict dict)."""
    fit_raw = raw_probs(lambdas(data, "fit"))
    chk_raw = raw_probs(lambdas(data, "check"))

    def search(a_lo, a_hi, a_step, b_lo, b_hi, b_step):
        best = (float("inf"), None)
        a = a_lo
        while a <= a_hi + 1e-9:
            b = b_lo
            while b <= b_hi + 1e-9:
                cal = {"a": round(a, 3), "b": round(b, 3)}
                ll = mean(score_raw(fit_raw, cal=cal)[0])
                if ll < best[0]:
                    best = (ll, cal)
                b += b_step
            a += a_step
        return best

    # coarse, then one refinement pass around the winner. A finer grid than
    # this is fitting the third decimal of a number whose noise band is wider.
    coarse = search(0.90, 1.35, 0.025, -2.0, 2.0, 0.25)
    a0, b0 = coarse[1]["a"], coarse[1]["b"]
    best = search(a0 - 0.025, a0 + 0.025, 0.005, b0 - 0.25, b0 + 0.25, 0.05)
    if coarse[0] < best[0]:
        best = coarse
    cal = best[1]

    ship_fit, _, _ = score_raw(fit_raw)
    ship_chk, ship_acc, ship_conf = score_raw(chk_raw)
    new_chk, new_acc, new_conf = score_raw(chk_raw, cal=cal)
    m, sd, pw = paired(new_chk, ship_chk)

    verdict = {
        "fitted": cal,
        "fitSeason": {"n": len(fit_raw), "shipped": round(mean(ship_fit), 4),
                      "fitted": round(best[0], 4)},
        "checkSeason": {"n": len(chk_raw), "shipped": round(mean(ship_chk), 4),
                        "fitted": round(mean(new_chk), 4),
                        "delta": round(m, 4), "sd": round(sd, 4), "pWorse": round(pw, 3),
                        "shippedAcc": round(ship_acc, 4), "fittedAcc": round(new_acc, 4)},
        "gates": {
            "enoughData": len(chk_raw) >= MIN_HOLDOUT,
            "notWorse": pw <= MAX_P_WORSE,
            "worthIt": -m >= MIN_GAIN,
        },
    }
    verdict["pass"] = all(verdict["gates"].values())

    if verbose:
        c = verdict["checkSeason"]
        print(f"\nfitted on the last completed season ({verdict['fitSeason']['n']} fixtures)")
        print(f"  T(confidence) = {cal['a']} + {cal['b']} x (confidence - 0.45)")
        print(f"  log loss there {verdict['fitSeason']['shipped']} -> {verdict['fitSeason']['fitted']}")
        print(f"\nchecked on the current season ({c['n']} fixtures, never fitted on)")
        print(f"  log loss {c['shipped']} -> {c['fitted']}  ({c['delta']:+.4f}, sd {c['sd']:.4f})")
        print(f"  accuracy {c['shippedAcc']:.2%} -> {c['fittedAcc']:.2%}")
        print(f"  probability this is actually worse: {c['pWorse']:.1%}")
        print("\ngates")
        for k, v in verdict["gates"].items():
            print(f"  {'PASS' if v else 'FAIL'}  {k}")
    return cal, verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="sweep every constant")
    ap.add_argument("--fit", action="store_true", help="refit the calibration curve")
    ap.add_argument("--dry-run", action="store_true", help="fit but write nothing")
    ap.add_argument("--cache", default=os.path.join(HERE, ".tunecache"))
    args = ap.parse_args()
    if not (args.report or args.fit):
        ap.error("nothing to do: pass --report or --fit")

    os.makedirs(args.cache, exist_ok=True)
    print(f"fetching {len(codes())} competitions ...", file=sys.stderr)
    data = load(args.cache)

    if args.report:
        report(data)

    if args.fit:
        cal, verdict = fit_calibration(data)
        verdict["generated"] = _date.today().isoformat()
        out = os.path.join(HERE, "calibration.json")
        if args.dry_run:
            print("\ndry run, nothing written")
        elif verdict["pass"]:
            json.dump({**cal, "fitted": verdict["generated"],
                       "check": verdict["checkSeason"]},
                      open(out, "w"), indent=1)
            print(f"\nwrote {os.path.basename(out)} — engine.py will pick it up "
                  f"on the next build")
        else:
            failed = [k for k, v in verdict["gates"].items() if not v]
            print(f"\nnot written: failed {', '.join(failed)}. The shipped "
                  f"TEMPERATURE of {E.TEMPERATURE} stays.")
        json.dump(verdict, open(os.path.join(HERE, "tuning-report.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
