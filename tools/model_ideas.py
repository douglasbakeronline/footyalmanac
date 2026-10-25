#!/usr/bin/env python3
"""
Douglas's model ideas, tested on the walk-forward replay (25 Oct 2026).
Advisory: changes nothing, writes nothing but its own report.

    python3 tools/model_ideas.py [--json audit-out/model-ideas.json]

Douglas: "Home teams have an advantage. Teams at the bottom end of the table
have a disadvantage. Goals for and against is a big one. We need to find
greater recent form variables."

The model already has a home advantage (one per tier), attack and defence
ratings built from goals for and against, and a capped last-5 points nudge.
So each idea is tested as what it would add on top:

  A  home advantage per league   each league's own home/away goal ratio from
                                 its prior season, against its tier's default
  B  table position              where each side sits in the table that
                                 morning (points per game rank, 5+ games)
  C  recent goals                goals scored and conceded over the last 5
                                 against the side's own season average
  D  recent goal difference      last-5 goal difference, both sides
  E  last-3 points               a shorter, sharper points form window

Each has one strength k, fitted on the last completed season (fit split) by
log loss under the live calibration, then checked on the current season
(check split), paired and bootstrapped against the live model on the same
fixtures. CLAUDE.md gates: >= 250 check fixtures, p(worse) <= 0.30, gain
>= 0.0005. Rule 1 holds: nothing is fitted on record.json.
Standard library only.
"""
import argparse, json, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import engine as E
import replay as R
import tune as T

NEUTRAL = R.NEUTRAL if hasattr(R, "NEUTRAL") else {"att": 1.0, "def": 1.0}


def walk(prior, test, tier):
    """replay.replay_league with what each idea needs alongside. The lambdas
    are the live model's, unchanged."""
    shrink, blend_k = E.SHRINK_FULL_SEASON, E.BLEND_K
    ptbl = E.build_table(prior)
    mu = E.league_goal_rate(ptbl)
    prior_rt = E.strength_from_table(ptbl, k=shrink)
    hg = sum(m[3] for m in prior); ag = sum(m[4] for m in prior)
    home_ratio = (hg + 20) / (ag + 20) if prior else None
    by_date = defaultdict(list)
    for m in test:
        by_date[m[0]].append(m)
    running, log = [], defaultdict(list)       # team -> [(gf, ga, pts)]
    for d in sorted(by_date):
        tbl = E.build_table(running)
        cur = E.strength_from_table(tbl, k=shrink) if running else {}
        ranked = sorted((t for t, r in tbl.items() if r["P"] >= 5), key=lambda t: tbl[t]["PPG"])
        pos = {t: (i + 0.5) / len(ranked) for i, t in enumerate(ranked)} if len(ranked) >= 6 else {}
        for m in by_date[d]:
            _, h, a, g1, g2 = m
            rows = {t: tbl.get(t) for t in (h, a)}
            rate = {t: E.blend(prior_rt.get(t, NEUTRAL), cur.get(t),
                               rows[t]["P"] if rows[t] else 0, k=blend_k) for t in (h, a)}
            fh = E.form_factor(E.form_points(rows[h]))
            fa = E.form_factor(E.form_points(rows[a]))
            lh, la = E.expected_goals(rate[h]["att"], rate[h]["def"], rate[a]["att"], rate[a]["def"],
                                      mu, tier=tier, form_h=fh, form_a=fa)

            def recent(t, n=5):
                lg = log[t]
                if len(lg) < n: return None
                r = lg[-n:]; s = lg
                return {"gf": sum(x[0] for x in r) / n, "ga": sum(x[1] for x in r) / n,
                        "sgf": sum(x[0] for x in s) / len(s), "sga": sum(x[1] for x in s) / len(s),
                        "pts3": sum(x[2] for x in lg[-3:]) / 3}
            feat = {"ratio": home_ratio, "tier": tier, "posH": pos.get(h), "posA": pos.get(a),
                    "rH": recent(h), "rA": recent(a)}
            y = 0 if g1 > g2 else (1 if g1 == g2 else 2)
            yield lh, la, y, feat
        for _, h, a, g1, g2 in by_date[d]:
            p1 = 3 if g1 > g2 else 1 if g1 == g2 else 0
            p2 = 3 if g2 > g1 else 1 if g1 == g2 else 0
            log[h].append((g1, g2, p1)); log[a].append((g2, g1, p2))
        running.extend(by_date[d])


def rows_for(data, split):
    out = []
    usable, _ = R.coverage(data, T.codes(), T.splits, split)
    for code in usable:
        test_s, prior_s = T.splits(code)[split]
        out += list(walk(data[(code, prior_s)], data[(code, test_s)], E.LEAGUES[code]["tier"]))
    return out


# each idea: (k grid, adjust(lh, la, feat, k) -> (lh, la))
def idea_home(lh, la, f, k):
    if not f["ratio"]: return lh, la
    t = f["tier"]; default = E.HOME_MULT.get(t, 1.16) / E.AWAY_MULT.get(t, 0.87)
    s = (f["ratio"] / default) ** (k / 2)
    return lh * s, la / s

def idea_table(lh, la, f, k):
    if f["posH"] is None or f["posA"] is None: return lh, la
    s = math.exp(k * (f["posH"] - f["posA"]))
    return lh * s, la / s

def idea_goals(lh, la, f, k):
    h, a = f["rH"], f["rA"]
    if not h or not a: return lh, la
    att_h = math.log((h["gf"] + 0.5) / (h["sgf"] + 0.5)); def_h = math.log((h["ga"] + 0.5) / (h["sga"] + 0.5))
    att_a = math.log((a["gf"] + 0.5) / (a["sgf"] + 0.5)); def_a = math.log((a["ga"] + 0.5) / (a["sga"] + 0.5))
    return lh * math.exp(k * (att_h + def_a)), la * math.exp(k * (att_a + def_h))

def idea_gd(lh, la, f, k):
    h, a = f["rH"], f["rA"]
    if not h or not a: return lh, la
    s = math.exp(k * ((h["gf"] - h["ga"]) - (a["gf"] - a["ga"])) / 2)
    return lh * s, la / s

def idea_pts3(lh, la, f, k):
    h, a = f["rH"], f["rA"]
    if not h or not a: return lh, la
    s = math.exp(k * (h["pts3"] - a["pts3"]) / 3)
    return lh * s, la / s

IDEAS = [
    ("A home advantage per league", idea_home, [0.25, 0.5, 0.75, 1.0]),
    ("B table position", idea_table, [-0.2, -0.1, 0.05, 0.1, 0.2, 0.3]),
    ("C recent goals for and against", idea_goals, [-0.1, 0.05, 0.1, 0.2, 0.3]),
    ("D recent goal difference", idea_gd, [-0.05, 0.02, 0.05, 0.1, 0.15]),
    ("E last-3 points", idea_pts3, [-0.05, 0.03, 0.06, 0.1, 0.15]),
]


def per_fixture(rows, fn, k, live):
    adj = [(fn(lh, la, f, k) if k else (lh, la)) + (y,) for lh, la, y, f in rows]
    per, acc, _ = T.score_under(T.raw_probs(adj), live)
    return per, acc


HOME_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]
HOME_FILE = os.path.join(HERE, "home-advantage.json")


def live_home_k():
    try:
        return float(json.load(open(HOME_FILE)).get("k", 0.0))
    except (OSError, ValueError):
        return 0.0


def league_factors(data, k):
    """{code: home factor} from each league's last completed season, as the
    check split's prior uses it."""
    out = {}
    for code in T.codes():
        prev = T.splits(code)["check"][1]
        rows = data.get((code, prev)) or []
        if len(rows) < 60: continue
        hg = sum(m[3] for m in rows); ag = sum(m[4] for m in rows)
        f = {"ratio": (hg + 20) / (ag + 20), "tier": E.LEAGUES[code]["tier"]}
        s, _ = idea_home(1.0, 1.0, f, k)
        out[code] = round(s, 4)
    return out


def fit_home(data, live, write):
    """The weekly learning step (25 Oct 2026): refit k for per-league home
    advantage on the last completed season, check it on the current one
    against the live k, and write home-advantage.json only if every gate
    passes, as tune.py does for calibration.json."""
    fit, chk = rows_for(data, "fit"), rows_for(data, "check")
    k_live = live_home_k()
    base_fit = per_fixture(fit, idea_home, k_live, live)[0]
    best = min(HOME_GRID, key=lambda k: T.mean(per_fixture(fit, idea_home, k, live)[0]))
    m_f = T.mean(per_fixture(fit, idea_home, best, live)[0]) - T.mean(base_fit)
    base_chk = per_fixture(chk, idea_home, k_live, live)[0]
    per_c = per_fixture(chk, idea_home, best, live)[0]
    m_c, sd_c, pw_c = T.paired(per_c, base_chk)
    gates = {"changed": best != k_live, "enoughData": len(chk) >= T.MIN_HOLDOUT,
             "notWorse": pw_c <= T.MAX_P_WORSE, "worthIt": -m_c >= T.MIN_GAIN}
    ok = all(gates.values())
    print(f"home advantage per league: live k {k_live:g}, fitted k {best:g}; fit {m_f:+.4f}; "
          f"check {len(chk)} fixtures {m_c:+.4f}, p(worse) {pw_c:.2f}; "
          + ("PASS" if ok else "not applied: " + ", ".join(g for g, v in gates.items() if not v)))
    if ok and write:
        json.dump({"k": best, "fitted": __import__("datetime").date.today().isoformat(),
                   "check": {"n": len(chk), "delta": round(m_c, 5), "pWorse": round(pw_c, 3)},
                   "leagues": league_factors(data, best)}, open(HOME_FILE, "w"), indent=1)
        print("wrote home-advantage.json: the build picks it up next run")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(HERE, ".tunecache"))
    ap.add_argument("--json")
    ap.add_argument("--fit-home", action="store_true",
                    help="refit per-league home advantage; write home-advantage.json if it passes")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.cache, exist_ok=True)
    data = T.load(args.cache)
    if args.fit_home:
        fit_home(data, T.live_baseline(), write=not args.dry_run)
        return
    live = T.live_baseline()
    fit, chk = rows_for(data, "fit"), rows_for(data, "check")
    b_fit, acc_fit = per_fixture(fit, None, 0, live)
    b_chk, acc_chk = per_fixture(chk, None, 0, live)
    print(f"live model: fit {len(fit)} fixtures, log loss {T.mean(b_fit):.4f}, acc {acc_fit:.2%}; "
          f"check {len(chk)} fixtures, log loss {T.mean(b_chk):.4f}, acc {acc_chk:.2%}\n")
    out = []
    for name, fn, grid in IDEAS:
        best = None
        for k in grid:
            per, acc = per_fixture(fit, fn, k, live)
            m = T.mean(per) - T.mean(b_fit)
            if best is None or m < best[1]: best = (k, m, acc)
        k = best[0]
        m_f, sd_f, pw_f = T.paired(per_fixture(fit, fn, k, live)[0], b_fit)
        per_c, acc_c = per_fixture(chk, fn, k, live)
        m_c, sd_c, pw_c = T.paired(per_c, b_chk)
        gates = {"enoughData": len(chk) >= T.MIN_HOLDOUT, "notWorse": pw_c <= T.MAX_P_WORSE,
                 "worthIt": -m_c >= T.MIN_GAIN, "fitGain": -m_f >= T.MIN_GAIN}
        ok = all(gates.values())
        print(f"{name:32} best k {k:+.2f} | fit {m_f:+.4f} p(worse) {pw_f:.2f} | "
              f"check {m_c:+.4f} p(worse) {pw_c:.2f} acc {acc_c - acc_chk:+.2%} | {'PASS' if ok else 'fail'}")
        out.append({"idea": name, "k": k, "fit": {"delta": round(m_f, 5), "pWorse": round(pw_f, 3)},
                    "check": {"delta": round(m_c, 5), "pWorse": round(pw_c, 3), "accDelta": round(acc_c - acc_chk, 4)},
                    "gates": gates, "pass": ok})
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        json.dump({"fit": len(fit), "check": len(chk), "ideas": out}, open(args.json, "w"), indent=1)


if __name__ == "__main__":
    main()
