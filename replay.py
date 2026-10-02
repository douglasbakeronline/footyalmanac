#!/usr/bin/env python3
"""
One walk-forward replay for football, shared by backtest.py and tune.py, and
the season checks that decide which competitions it may use.

    python3 replay.py --audit          which competitions are usable, which are not, and why

Why this exists (audit, 2 Oct 2026)
-----------------------------------
backtest.py and tune.py each had their own replay, and they disagreed:

  - tune.py normalised this season's ratings by LAST season's goal rate;
    backtest.py and the live build use THIS season's (engine.strength_from_table).
    tune.py fits calibration.json, which the live build applies, so the curve
    was fitted on a calculation the site never makes.
  - Both updated their tables after every fixture, in file order. The data
    carries dates only, so on a busy Saturday a 15:00 match could be priced
    with another 15:00 result already counted.
  - Neither checked season boundaries. Prior seasons that run into the test
    season (backfill windows drawn past a mid-July kick-off; corrupt upstream
    dates) leaked test matches into the prior.

What this does instead
----------------------
  - Ratings, form and expected goals come from engine.py, the functions the
    live build uses: strength_from_table (this season's goal rate), blend,
    form_points / form_factor, expected_goals.
  - Results are batched by date. A match is priced only from results on
    strictly earlier dates, because the data has no kick-off times. The live
    build publishes each morning from the previous day's results, so this is
    also what it actually knew.
  - validate_split refuses a prior/test pair whose dates overlap, or where
    either season is missing, and says why. Nothing is repaired silently.

Standard library only.
"""
import argparse, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

NEUTRAL = {"att": 1.0, "def": 1.0}


# ---------------------------------------------------------------------------
# season checks
# ---------------------------------------------------------------------------

def validate_split(code, split, prior, test):
    """{"code","split","ok","reasons",...}. prior/test: (date, home, away, hg, ag)."""
    out = {"code": code, "split": split, "ok": True, "reasons": [],
           "priorMatches": len(prior or []), "testMatches": len(test or [])}
    if not prior:
        out["reasons"].append("no prior season")
    if not test:
        out["reasons"].append("no test season")
    if prior and test:
        pmax, tmin = max(r[0] for r in prior), min(r[0] for r in test)
        out["priorEnds"], out["testStarts"] = pmax, tmin
        if pmax >= tmin:
            same = ({(r[0], r[1], r[2]) for r in prior}
                    & {(r[0], r[1], r[2]) for r in test})
            out["reasons"].append(
                f"prior/test overlap: prior ends {pmax}, test starts {tmin}; "
                f"{sum(1 for r in prior if r[0] >= tmin)} prior matches on or after the test start, "
                f"{sum(1 for r in test if r[0] <= pmax)} test matches on or before the prior end, "
                f"{len(same)} identical in both")
    out["ok"] = not out["reasons"]
    return out


def coverage(data, codes, splits, split):
    """(usable codes, exclusions) for one split. splits(code)[split] ->
    (test season, prior season), as tune.splits."""
    usable, excluded = [], []
    for code in codes:
        test_s, prior_s = splits(code)[split]
        v = validate_split(code, split, data.get((code, prior_s)) or [],
                           data.get((code, test_s)) or [])
        v["seasons"] = {"prior": prior_s, "test": test_s}
        (usable if v["ok"] else excluded).append(code if v["ok"] else v)
    return usable, excluded


def report_exclusions(excluded, out=sys.stderr):
    by_reason = defaultdict(list)
    for v in excluded:
        key = "overlap" if any("overlap" in r for r in v["reasons"]) else "; ".join(v["reasons"])
        by_reason[key].append(v)
    for key, vs in sorted(by_reason.items()):
        if key == "overlap":
            for v in vs:
                print(f"  EXCLUDED {v['code']} ({v['split']}, {v['seasons']['prior']} -> "
                      f"{v['seasons']['test']}): {v['reasons'][0]}", file=out)
        else:
            print(f"  excluded, {key}: {len(vs)} competition(s): "
                  f"{', '.join(v['code'] for v in vs)}", file=out)


# ---------------------------------------------------------------------------
# the replay
# ---------------------------------------------------------------------------

def replay_league(prior, test, tier, params=None):
    """Price every match of `test` as the model would have the morning of its
    date. Yields (match, lh, la, info) in date order.

    params (all optional; defaults are the shipped engine constants):
      shrink    engine.SHRINK_FULL_SEASON   shrinkage of season ratings
      blend_k   engine.BLEND_K              this season vs the prior
      form_cap  engine.FORM_MAX             cap on the form nudge
      form_n    5                           matches in the form window
      ha_scale  1.0                         home/away tilt
    """
    p = params or {}
    shrink = p.get("shrink", E.SHRINK_FULL_SEASON)
    blend_k = p.get("blend_k", E.BLEND_K)
    form_cap = p.get("form_cap", E.FORM_MAX)
    form_n = p.get("form_n", 5)
    ha_scale = p.get("ha_scale", 1.0)

    ptbl = E.build_table(prior)
    mu = E.league_goal_rate(ptbl)              # the level, as the live build uses
    prior_rt = E.strength_from_table(ptbl, k=shrink)

    by_date = defaultdict(list)
    for m in test:
        by_date[m[0]].append(m)

    running = []
    for d in sorted(by_date):
        # Everything known before this date, and nothing from it.
        tbl = E.build_table(running)
        cur = E.strength_from_table(tbl, k=shrink) if running else {}
        for m in by_date[d]:
            _, h, a, hg, ag = m
            rows = {t: tbl.get(t) for t in (h, a)}
            rate = {t: E.blend(prior_rt.get(t, NEUTRAL), cur.get(t),
                               rows[t]["P"] if rows[t] else 0, k=blend_k) for t in (h, a)}
            fh = E.form_factor(E.form_points(rows[h], n=form_n), cap=form_cap)
            fa = E.form_factor(E.form_points(rows[a], n=form_n), cap=form_cap)
            lh, la = E.expected_goals(rate[h]["att"], rate[h]["def"],
                                      rate[a]["att"], rate[a]["def"], mu, tier=tier,
                                      form_h=fh, form_a=fa, ha_scale=ha_scale)
            info = {"mu": mu, "rows": rows, "prior": {t: prior_rt.get(t) for t in (h, a)},
                    "current": {t: cur.get(t) for t in (h, a)}, "form_n": form_n}
            yield m, lh, la, info
        running.extend(by_date[d])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true", help="report usable and excluded competitions")
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tunecache"))
    args = ap.parse_args()
    if not args.audit:
        ap.error("nothing to do: pass --audit")
    import tune
    os.makedirs(args.cache, exist_ok=True)
    data = tune.load(args.cache)
    for split in ("fit", "check"):
        usable, excluded = coverage(data, tune.codes(), tune.splits, split)
        n = sum(len(data.get((c, tune.splits(c)[split][0])) or []) for c in usable)
        print(f"{split}: {len(usable)} usable competitions, {n} test fixtures; "
              f"{len(excluded)} excluded", file=sys.stderr)
        report_exclusions(excluded)


if __name__ == "__main__":
    main()
