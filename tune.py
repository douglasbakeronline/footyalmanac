#!/usr/bin/env python3
"""
Test the model's constants against data it has never seen, and refit the
calibration curve when the evidence supports it.

    python3 tune.py --report          full sweep, prints a table, changes nothing
    python3 tune.py --fit             refit calibration.json if it passes the gates
    python3 tune.py --fit --dry-run   as above, but write nothing
    python3 tune.py --fit --snapshot FILE   advisory fit on a frozen snapshot
                                      (replay.py --freeze); writes nothing

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
import replay as R
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
    # The API-Football step-3 leagues (sources.AF) are left out on purpose:
    # a new, less predictable group should not move the shared calibration
    # curve without a deliberate decision (30 Sep 2026).
    return [c for c, m in E.LEAGUES.items()
            if not m.get("cup") and not m.get("ratingsOnly")
            and c not in S.AF_BOARD_ONLY and c not in S.AF_EXTRA]


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


def lambdas(data, split, params=None, meta=False, features=False):
    """Every fixture of the season, with the two expected-goal numbers the
    model would have published the morning before it kicked off.

    meta=True appends (code, date, home, away) to each row, for joining the
    predictions to something else (odds.py joins them to bookmaker prices).
    features=True appends a dict of what else was knowable that morning
    (games played, how far each rating has moved off its prior, recent
    points), for predictability.py. Neither changes the numbers.

    The replay itself is replay.replay_league, shared with backtest.py and
    built from the same engine functions as the live build: this season's
    ratings use this season's goal rate, and a match only sees results from
    earlier dates. Competitions whose prior and test seasons overlap, or that
    lack either season, are left out; exclusions(data, split) says which.
    """
    p = {**DEFAULTS, **(params or {})}
    rows = []
    usable, _ = R.coverage(data, codes(), splits, split)
    for code in usable:
        test_s, prior_s = splits(code)[split]
        prior, test = data[(code, prior_s)], data[(code, test_s)]
        for (d, h, a, hg, ag), lh, la, info in R.replay_league(
                prior, test, E.LEAGUES[code]["tier"], params=p):
            y = 0 if hg > ag else (1 if hg == ag else 2)
            row = (lh, la, y, code, d, h, a) if meta else (lh, la, y)
            if features:
                def drift(team):
                    # how far this season's evidence sits from the prior
                    c, pri = info["current"][team], info["prior"][team]
                    if not c or not pri:
                        return 0.0
                    return (abs(math.log(c["att"] / pri["att"]))
                            + abs(math.log(c["def"] / pri["def"])))
                rh, ra = info["rows"][h], info["rows"][a]
                row = row + ({
                    "nH": rh["P"] if rh else 0,
                    "nA": ra["P"] if ra else 0,
                    "newH": info["prior"][h] is None, "newA": info["prior"][a] is None,
                    "driftH": drift(h), "driftA": drift(a),
                    "formH": [x[2] for x in (rh["results"] if rh else [])][-5:],
                    "formA": [x[2] for x in (ra["results"] if ra else [])][-5:],
                },)
            rows.append(row)
    return rows


def exclusions(data, split):
    """Competitions lambdas() leaves out of a split, with the reason."""
    return R.coverage(data, codes(), splits, split)[1]


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
# the live calibration: what every candidate and the sweep are measured against
# ---------------------------------------------------------------------------

def live_baseline():
    """The calibration the site prices with now, exactly as engine.temper
    applies it: the calibration.json curve (E.CALIBRATION) when one is
    configured, the flat E.TEMPERATURE only when none is.

    Until 3 Oct 2026 the gate compared a candidate with the flat 1.15 even
    while a curve was live, so a curve that beat 1.15 but lost to the live
    one could still replace it."""
    if E.CALIBRATION:
        return {"kind": "curve", "a": E.CALIBRATION["a"], "b": E.CALIBRATION["b"],
                "source": "calibration.json"}
    return {"kind": "flat", "T": E.TEMPERATURE,
            "source": "engine.TEMPERATURE (no calibration.json)"}


def as_curve(cal):
    return {"kind": "curve", "a": cal["a"], "b": cal["b"]}


def describe(b):
    if b["kind"] == "curve":
        return f"T = {b['a']} + {b['b']} x (confidence - 0.45)"
    return f"flat T = {b['T']}"


def score_under(raws, b):
    """score_raw under a baseline or candidate as returned by live_baseline()
    or as_curve()."""
    if b["kind"] == "curve":
        return score_raw(raws, cal={"a": b["a"], "b": b["b"]})
    return score_raw(raws, T=b["T"])


def gate(chk_raw, candidate, baseline):
    """Paired check of a candidate curve against the baseline on one fixture
    list: the same rows scored twice, so the pairing is exact. Returns
    (checkSeason summary, gates). "shipped" is the live baseline."""
    base_per, base_acc, _ = score_under(chk_raw, baseline)
    new_per, new_acc, _ = score_under(chk_raw, as_curve(candidate))
    assert len(base_per) == len(new_per) == len(chk_raw)
    m, sd, pw = paired(new_per, base_per)
    check = {"n": len(chk_raw), "shipped": round(mean(base_per), 4),
             "fitted": round(mean(new_per), 4),
             "delta": round(m, 4), "sd": round(sd, 4), "pWorse": round(pw, 3),
             "shippedAcc": round(base_acc, 4), "fittedAcc": round(new_acc, 4)}
    gates = {
        "enoughData": len(chk_raw) >= MIN_HOLDOUT,
        "notWorse": pw <= MAX_P_WORSE,
        "worthIt": -m >= MIN_GAIN,
    }
    return check, gates


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
    """Advisory sweep: each constant moved alone, everything else at the live
    configuration, temperature included (the calibration.json curve when one
    is configured), compared paired with that live configuration."""
    for split in ("fit", "check"):
        R.report_exclusions(exclusions(data, split))
    live = live_baseline()
    fit = lambdas(data, "fit")
    base, base_acc, _ = score_under(raw_probs(fit), live)
    print(f"\nbaseline = the live configuration: {describe(live)} [{live['source']}], "
          f"RHO {E.RHO:g}, SHRINK_FULL_SEASON {E.SHRINK_FULL_SEASON:g}, "
          f"BLEND_K {E.BLEND_K:g}, FORM_MAX {E.FORM_MAX:g}, form window "
          f"{DEFAULTS['form_n']}, home advantage scale {DEFAULTS['ha_scale']:g}")
    print(f"fit season: {len(fit)} fixtures, log loss {mean(base):.4f}, "
          f"accuracy {base_acc:.2%}\n")
    print(f"  {'constant':30} {'live':>9} {'trying':>8} {'Δ log loss':>11} "
          f"{'sd':>7} {'p(worse)':>9} {'acc':>7}")

    def trial(label, shipped, value, params=None, rho=None, T=None):
        rows = lambdas(data, "fit", params) if params else fit
        per, acc, _ = score_under(raw_probs(rows, rho),
                                  {"kind": "flat", "T": T} if T is not None else live)
        m, sd, pw = paired(per, base)
        mark = "  <-" if pw < 0.05 and m < 0 else ""
        print(f"  {label:30} {shipped:>9} {value:>8} {m:>+11.4f} {sd:>7.4f} "
              f"{pw:>9.2f} {acc:>7.2%}{mark}")

    # with a curve live, a flat temperature is not in use: these rows ask
    # whether replacing the curve with one would be better
    if live["kind"] == "curve":
        for T in (1.00, 1.05, 1.10, E.TEMPERATURE, 1.25):
            trial("flat TEMPERATURE (no curve)", "curve", T, T=T)
    else:
        for T in (1.00, 1.05, 1.10, 1.25):
            trial("TEMPERATURE", f"{E.TEMPERATURE:g}", T, T=T)
    for r in (-0.12, -0.08, -0.04, 0.0):
        trial("RHO", f"{E.RHO:g}", r, rho=r)
    for v in (2, 3, 6, 8, 12):
        trial("SHRINK_FULL_SEASON", f"{E.SHRINK_FULL_SEASON:g}", v, {"shrink": v})
    for v in (3, 4, 8, 12, 20):
        trial("BLEND_K", f"{E.BLEND_K:g}", v, {"blend_k": v})
    for v in (0.0, 0.10, 0.15, 0.20, 0.30):
        trial("FORM_MAX", f"{E.FORM_MAX:g}", v, {"form_cap": v})
    for v in (3, 8, 10):
        trial("form window", DEFAULTS["form_n"], v, {"form_n": v})
    for v in (0.8, 0.9, 1.1, 1.2):
        trial("home advantage scale", f"{DEFAULTS['ha_scale']:g}", v, {"ha_scale": v})
    print("\n  a change is worth making only where p(worse) is small AND the "
          "same change\n  survives on the current season. Run --fit for that check.")


# ---------------------------------------------------------------------------
# calibration fit
# ---------------------------------------------------------------------------

def fit_calibration(data, verbose=True, baseline=None):
    """Fit the temperature curve on the last completed season, then check it on
    the current one against the live calibration (live_baseline()), on the
    same fixtures. Returns (calibration, verdict dict)."""
    baseline = baseline or live_baseline()
    excluded = {s: exclusions(data, s) for s in ("fit", "check")}
    if verbose:
        for s in ("fit", "check"):
            R.report_exclusions(excluded[s])
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

    ship_fit, _, _ = score_under(fit_raw, baseline)
    check, gates = gate(chk_raw, cal, baseline)

    verdict = {
        # what was compared: the live calibration against the candidate, each
        # scored on the same fixtures
        "baseline": {**baseline, "describe": describe(baseline)},
        "candidate": {**as_curve(cal), "describe": describe(as_curve(cal))},
        # what the fit could not use, and why: missing seasons and prior/test
        # overlaps are left out, never repaired (replay.validate_split)
        "excluded": {s: [{"code": v["code"], "reasons": v["reasons"]} for v in vs]
                     for s, vs in excluded.items()},
        "fitted": cal,
        "fitSeason": {"n": len(fit_raw), "shipped": round(mean(ship_fit), 4),
                      "fitted": round(best[0], 4)},
        "checkSeason": check,
        "gates": gates,
    }
    verdict["pass"] = all(verdict["gates"].values())

    if verbose:
        c = verdict["checkSeason"]
        f = verdict["fitSeason"]
        print(f"\nbaseline (live):  {describe(baseline)}  [{baseline['source']}]")
        print(f"candidate:        {describe(as_curve(cal))}")
        print(f"fixtures: fit {f['n']}, check {c['n']}; baseline and candidate "
              f"scored on the same rows")
        for s, vs in excluded.items():
            bad = [v["code"] for v in vs
                   if any("overlap" in r or "outside" in r for r in v["reasons"])]
            print(f"excluded from {s}: {len(vs)} competitions, {len(vs) - len(bad)} "
                  f"missing a season, {len(bad)} refused by validation"
                  f"{' (' + ', '.join(bad) + ')' if bad else ''}; reasons above")
        print(f"\nfitted on the last completed season ({f['n']} fixtures)")
        print(f"  log loss baseline {f['shipped']} -> candidate {f['fitted']}")
        print(f"\nchecked on the current season ({c['n']} fixtures, never fitted on)")
        print(f"  log loss baseline {c['shipped']} -> candidate {c['fitted']}  "
              f"({c['delta']:+.4f}, sd {c['sd']:.4f})")
        print(f"  accuracy {c['shippedAcc']:.2%} -> {c['fittedAcc']:.2%}")
        print(f"  probability the candidate is actually worse: {c['pWorse']:.1%}")
        print("\ngates (against the live baseline)")
        for k, v in verdict["gates"].items():
            print(f"  {'PASS' if v else 'FAIL'}  {k}")
    return cal, verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="sweep every constant")
    ap.add_argument("--fit", action="store_true", help="refit the calibration curve")
    ap.add_argument("--dry-run", action="store_true", help="fit but write nothing")
    ap.add_argument("--snapshot", metavar="FILE",
                    help="read a frozen snapshot (replay.py --freeze) instead of fetching; "
                         "advisory, implies --dry-run and writes no report")
    ap.add_argument("--cache", default=os.path.join(HERE, ".tunecache"))
    args = ap.parse_args()
    if not (args.report or args.fit):
        ap.error("nothing to do: pass --report or --fit")

    if args.snapshot:
        data, _, digest = R.load_snapshot(args.snapshot)
        args.dry_run = True
        print(f"snapshot {digest} ({len(data)} seasons), advisory: nothing is written",
              file=sys.stderr)
    else:
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
            print(f"\nnot written: failed {', '.join(failed)}. The live "
                  f"calibration stays: {verdict['baseline']['describe']}.")
        if not args.snapshot:
            with open(os.path.join(HERE, "tuning-report.json"), "w") as f:
                json.dump(verdict, f, indent=1)


if __name__ == "__main__":
    main()
