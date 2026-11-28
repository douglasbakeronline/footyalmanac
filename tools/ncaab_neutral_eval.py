"""College basketball: should a neutral court take the calibration's home term?

The season-phase curve (`sports.fit_phase_calibration`) is a logistic line in
the home side's log-odds, `a + b * logit(p)`. Its early-season intercept is
+0.31 for college basketball: November-December home sides win more than the
Elo's 100-point home advantage says. On a neutral court there is no home side,
but the curve still handed +0.31 to whichever team ESPN lists first. Live,
neutral college basketball picks at 70%+ had landed 48 of 76 against 79%
quoted by 27 Nov 2026 (`sports-record.json` `bySide`).

The variant (`sports.NEUTRAL0`): the curve fitted on venue games only, applied
without its intercept at a neutral site. Compared with live on the replay
`sports.py --tune` uses (live parameters, early K included), curve fitted on
`sports.FIT`, paired and bootstrapped, on the check season (Rule 3 gates and
the 65%+ honesty guard) and, as a second read, on this season's games so far
(never used to fit anything). The live record is not read.

Advisory only: writes nothing. Run: python3 tools/ncaab_neutral_eval.py
"""
import math
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports  # noqa: E402

SEASON = (date(2026, 7, 1), date(2027, 7, 1))   # this season's games, a second read


def rows_for(preds, win, cal):
    """(game, calibrated home chance) for warm decided games in a window."""
    out = []
    for g, ph, warm in preds:
        if warm and sports.in_window(g, win) and g["hs"] != g["as"]:
            out.append((g, sports.calibrate(ph, cal, g["when"], g.get("neutral"))))
    return out


def loss(rows):
    return [-math.log(max(p if g["hs"] > g["as"] else 1 - p, 1e-12)) for g, p in rows]


def top_gap(rows):
    g = [(max(p, 1 - p), (p >= 0.5) == (x["hs"] > x["as"])) for x, p in rows if max(p, 1 - p) >= 0.65]
    return abs(sum(c for c, _ in g) / len(g) - sum(h for _, h in g) / len(g)) if g else 0.0


def by_venue(rows, lo=0.65, hi=0.85):
    """Landed v quoted at lo-hi, by the pick's venue."""
    out = {}
    for g, p in rows:
        c = max(p, 1 - p)
        if not lo <= c < hi:
            continue
        k = "neutral" if g.get("neutral") else ("home pick" if p >= 0.5 else "away pick")
        t = out.setdefault(k, [0, 0, 0.0, 0.0])
        t[0] += 1
        t[1] += (p >= 0.5) == (g["hs"] > g["as"])
        t[2] += c
        t[3] += c * (1 - c)
    return {k: (n, w, q, (w - q) / math.sqrt(v) if v else 0.0) for k, (n, w, q, v) in out.items()}


def compare(preds, live_cal, var_cal, win):
    a, b = rows_for(preds, win, live_cal), rows_for(preds, win, var_cal)
    la, lb = loss(a), loss(b)
    mu, sd, pw = sports.paired(lb, la) if la else (0.0, 0.0, 1.0)
    return {"n": len(la), "live": sum(la) / max(len(la), 1), "variant": sum(lb) / max(len(lb), 1),
            "gain": -mu, "pWorse": pw, "gapLive": top_gap(a), "gapVariant": top_gap(b),
            "venueLive": by_venue(a), "venueVariant": by_venue(b)}


def main():
    sp = sports.load_params().get("ncaab") or {}
    params = sp.get("params") or {**sports.DEFAULTS, **sports.EARLY_K.get("ncaab", {})}
    games = [g for g in sports.history_for("ncaab") if g["final"]]
    preds = sports.replay(games, params)[1]
    months = sports.PHASE_MONTHS["ncaab"]
    live_cal = sports.fit_phase_calibration(preds, sports.FIT, months)
    var_cal = sports.fit_phase_calibration(preds, sports.FIT, months, neutral0=True)
    print(f"College basketball: {len(games)} games, params {params}")
    print(f"live curve    {live_cal}")
    print(f"variant curve {var_cal}")
    verdict = None
    for name, win in (("fit (in sample)", sports.FIT), ("check", sports.CHECK), ("this season", SEASON)):
        r = compare(preds, live_cal, var_cal, win)
        line = (f"\n{name}: {r['n']} games, log loss {r['live']:.4f} -> {r['variant']:.4f}, gain {r['gain']:+.5f}, "
                f"p(worse) {r['pWorse']:.3f}, 65%+ gap {r['gapLive']:.3f} -> {r['gapVariant']:.3f}")
        if name == "check":
            verdict = (r["n"] >= sports.MIN_HOLDOUT and r["pWorse"] <= sports.MAX_P_WORSE
                       and r["gain"] >= sports.MIN_GAIN and r["gapVariant"] <= r["gapLive"] + 0.01)
            line += f"  {'PASS' if verdict else 'fail'}"
        print(line)
        for k in ("home pick", "away pick", "neutral"):
            for tag, v in (("live", r["venueLive"]), ("variant", r["venueVariant"])):
                if k in v:
                    n, w, q, z = v[k]
                    print(f"   65-85% {k:9} {tag:7} {n:5}  landed {w / n:.1%}  quoted {q / n:.1%}  z {z:+.2f}")
    return verdict


if __name__ == "__main__":
    main()
