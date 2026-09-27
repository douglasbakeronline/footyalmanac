#!/usr/bin/env python3
"""
Which games can we actually call? Tests signals beyond the model's own
confidence, and changes nothing.

    python3 predictability.py                 every signal, fit season -> check season
    python3 predictability.py --market        add bookmaker agreement (network, ~40 files)

The question
------------
The board ranks fixtures by the probability of the top pick. A signal is only
worth adding if, among games quoted at the SAME probability, it separates the
calls that land from the ones that don't. So each test is a binary one: did the
pick land?

  baseline    logistic(a + b * logit(confidence)), fitted on the last completed
              season. A recalibration of the model's own number, so a signal
              cannot win just by fixing calibration (the trap that made
              SHRINK_FULL_SEASON and FORM_MAX look real).
  candidate   the same, plus one signal, fitted on the same season.

Both are then scored on the current season, which neither has seen, paired
and bootstrapped, against the tune.py gates. The top-10% and top-20% hit
rates show what it would do to the board.

Nothing here reads record.json.
"""
import argparse, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import tune

HERE = os.path.dirname(os.path.abspath(__file__))
EPS = 1e-12
LEAGUE_K = 200        # fixtures before a league's own record counts for half


# ---------------------------------------------------------------------------
# rows
# ---------------------------------------------------------------------------

def _ppg(pts):
    return sum(pts) / len(pts) if len(pts) >= 3 else None


def build_rows(data, split):
    """One dict per fixture: calibrated probabilities, whether the pick landed,
    and every candidate signal, all as known the morning before."""
    cal = E.CALIBRATION
    out = []
    for lh, la, y, code, d, h, a, f in tune.lambdas(data, split, meta=True, features=True):
        p = tune.outcome(lh, la, E.RHO)
        t = tune.curve_T(max(p), cal) if cal else E.TEMPERATURE
        q = [max(x, EPS) ** (1.0 / t) for x in p]
        s = sum(q)
        p = [x / s for x in q]
        pick = p.index(max(p))
        fav_form, dog_form = (f["formH"], f["formA"]) if pick != 2 else (f["formA"], f["formH"])
        ff, df = _ppg(fav_form), _ppg(dog_form)
        out.append({
            "key": (code, d, h, a), "code": code, "p": p, "pick": pick,
            "conf": p[pick], "hit": int(pick == y),
            "sig": {
                "fewest games played":  math.log1p(min(f["nH"], f["nA"])),
                "new to the division":  float(f["newH"] or f["newA"]),
                "rating drift":         max(f["driftH"], f["driftA"]),
                "draw probability":     p[1],
                "total expected goals": lh + la,
                "form against the pick": 0.0 if ff is None or df is None else (df - ff) / 3.0,
                "away pick":            float(pick == 2),
            },
        })
    return out


# ---------------------------------------------------------------------------
# logistic regression, Newton's method, standard library
# ---------------------------------------------------------------------------

def _logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _sig(z):
    return 1 / (1 + math.exp(-max(min(z, 30), -30)))


def _solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c and M[c][c]:
                k = M[r][c] / M[c][c]
                M[r] = [x - k * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] if M[i][i] else 0.0 for i in range(n)]


def fit_logistic(X, y, ridge=1e-3, iters=25):
    k = len(X[0])
    w = [0.0] * k
    for _ in range(iters):
        g = [0.0] * k
        H = [[ridge if i == j and i else 0.0 for j in range(k)] for i in range(k)]
        for x, t in zip(X, y):
            p = _sig(sum(a * b for a, b in zip(w, x)))
            e, v = p - t, p * (1 - p)
            for i in range(k):
                g[i] += e * x[i]
                for j in range(k):
                    H[i][j] += v * x[i] * x[j]
        for i in range(1, k):
            g[i] += ridge * w[i]
        step = _solve(H, g)
        w = [a - b for a, b in zip(w, step)]
        if max(abs(s) for s in step) < 1e-7:
            break
    return w


def predict(w, X):
    return [_sig(sum(a * b for a, b in zip(w, x))) for x in X]


def bll(p, y):
    """Per-fixture binary log loss."""
    return [-math.log(max(q if t else 1 - q, EPS)) for q, t in zip(p, y)]


# ---------------------------------------------------------------------------
# the tests
# ---------------------------------------------------------------------------

def design(rows, names, stats):
    X = []
    for r in rows:
        x = [1.0, _logit(r["conf"])]
        for n in names:
            m, sd = stats[n]
            x.append((r["sig"][n] - m) / sd)
        X.append(x)
    return X


def standardise(rows, names):
    st = {}
    for n in names:
        v = [r["sig"][n] for r in rows]
        m = sum(v) / len(v)
        sd = math.sqrt(sum((x - m) ** 2 for x in v) / len(v)) or 1.0
        st[n] = (m, sd)
    return st


def top_hit(p, y, frac):
    order = sorted(range(len(p)), key=lambda i: -p[i])[:max(1, int(len(p) * frac))]
    return sum(y[i] for i in order) / len(order)


def league_shift(fit_rows, base_w):
    """Per-league logit shift from the fit season, shrunk toward zero."""
    by = {}
    for r in fit_rows:
        by.setdefault(r["code"], []).append(r)
    out = {}
    for code, rs in by.items():
        z = [base_w[0] + base_w[1] * _logit(r["conf"]) for r in rs]
        y = [r["hit"] for r in rs]
        s = 0.0
        for _ in range(20):              # 1-D Newton for the shift
            ps = [_sig(v + s) for v in z]
            g = sum(p - t for p, t in zip(ps, y))
            h = sum(p * (1 - p) for p in ps) or 1.0
            s -= g / h
        out[code] = s * len(rs) / (len(rs) + LEAGUE_K)
    return out


def run(fit, chk, names_list, label_width=26):
    yf, yc = [r["hit"] for r in fit], [r["hit"] for r in chk]
    base_w = fit_logistic(design(fit, [], {}), yf)
    pb = predict(base_w, design(chk, [], {}))
    base_loss = bll(pb, yc)
    b10, b20 = top_hit(pb, yc, 0.10), top_hit(pb, yc, 0.20)

    print(f"\n  baseline on the check season: binary log loss "
          f"{sum(base_loss)/len(base_loss):.4f}, top 10% {b10:.1%}, top 20% {b20:.1%}")
    print(f"\n  {'signal':{label_width}} {'coef':>7} {'Δ loss':>9} {'sd':>7} "
          f"{'p(worse)':>9} {'top10%':>7} {'top20%':>7}  gates")

    results = []
    for names in names_list:
        st = standardise(fit, names)
        w = fit_logistic(design(fit, names, st), yf)
        pc = predict(w, design(chk, names, st))
        results.append(_line(" + ".join(names) if len(names) < 3 else "all of the above",
                             w[2] if len(names) == 1 else None,
                             pc, yc, base_loss, label_width))

    # league record: a shift per competition, not a coefficient
    shift = league_shift(fit, base_w)
    zc = [base_w[0] + base_w[1] * _logit(r["conf"]) + shift.get(r["code"], 0.0) for r in chk]
    results.append(_line("league record", None, [_sig(z) for z in zc], yc, base_loss, label_width))
    return results


def _line(label, coef, pc, yc, base_loss, width):
    loss = bll(pc, yc)
    m, sd, pw = tune.paired(loss, base_loss)
    gates = (len(yc) >= tune.MIN_HOLDOUT, pw <= tune.MAX_P_WORSE, -m >= tune.MIN_GAIN)
    ok = "PASS" if all(gates) else "fail"
    c = f"{coef:+7.3f}" if coef is not None else f"{'':>7}"
    print(f"  {label[:width]:{width}} {c} {m:+9.4f} {sd:7.4f} {pw:9.2f} "
          f"{top_hit(pc, yc, 0.10):7.1%} {top_hit(pc, yc, 0.20):7.1%}  {ok}")
    return {"signal": label, "delta": m, "sd": sd, "pWorse": pw, "pass": all(gates)}


# ---------------------------------------------------------------------------
# bookmaker agreement, on the divisions football-data.co.uk prices
# ---------------------------------------------------------------------------

def attach_market(data, rows_by_split, cache, log=None):
    import odds, time
    for split, rows in rows_by_split.items():
        prices = []
        for div, code in odds.DIVS.items():
            if code not in E.LEAGUES:
                continue
            s = tune.splits(code)[split][0]
            if "-" not in s:
                continue
            prices += odds.parse(odds._get(odds.HIST_URL.format(yy=odds._yy(s), div=div), log=log))
            time.sleep(1.0)
        prices = [r for r in prices if r["result"] is not None]
        idx = {r["key"]: r for r in rows}
        joined = odds.match(prices, [(k, *k) for k in idx])
        for k, pr in joined.items():
            r = idx[k]
            m = odds.fair(pr["avg"])
            r["sig"]["market on the pick"] = m[r["pick"]]
            r["sig"]["market disagrees"] = float(m.index(max(m)) != r["pick"])
            r["sig"]["market minus model"] = m[r["pick"]] - r["conf"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(HERE, ".tunecache"))
    ap.add_argument("--market", action="store_true", help="also test bookmaker agreement")
    args = ap.parse_args()

    os.makedirs(args.cache, exist_ok=True)
    print(f"fetching {len(tune.codes())} competitions ...", file=sys.stderr)
    data = tune.load(args.cache)
    fit, chk = build_rows(data, "fit"), build_rows(data, "check")
    print(f"\nfit season {len(fit)} fixtures, check season {len(chk)} fixtures")
    print(f"pick landed: fit {sum(r['hit'] for r in fit)/len(fit):.1%}, "
          f"check {sum(r['hit'] for r in chk)/len(chk):.1%}")

    names = list(fit[0]["sig"])
    run(fit, chk, [[n] for n in names] + [names])

    if args.market:
        attach_market(data, {"fit": fit, "check": chk}, args.cache)
        mf = [r for r in fit if "market on the pick" in r["sig"]]
        mc = [r for r in chk if "market on the pick" in r["sig"]]
        print(f"\npriced divisions only: fit {len(mf)}, check {len(mc)} fixtures")
        if mf and mc:
            mk = ["market on the pick", "market disagrees", "market minus model"]
            run(mf, mc, [[n] for n in mk])

    print("\n  advisory only. A signal that passes is a candidate for the board, "
          "and has to be\n  re-tested alongside the others before it ships (rule 4).")


if __name__ == "__main__":
    main()
