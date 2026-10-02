#!/usr/bin/env python3
"""
One walk-forward replay for football, shared by backtest.py and tune.py, and
the season checks that decide which competitions it may use.

    python3 replay.py --audit                      which competitions are usable, which are not, and why
    python3 replay.py --freeze FILE                freeze the data (harness seasons + current/ cache) with a sha256
    python3 replay.py --audit --snapshot FILE      the same report from a frozen snapshot
    python3 replay.py --filter-snapshot FULL OPENFOOTBALL   openfootball-only copy of a frozen snapshot
    python3 replay.py --audit --snapshot FILE --include-current
                                                   advisory: original vs cache-expanded coverage, shipped
                                                   calibration, nothing refitted or written

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

def season_window(season):
    """The widest dates a season's matches can fall on: a calendar year, or
    1 June to 31 July of the next year for a split-year season (play-offs
    and rearrangements included). A row outside it is mis-dated or belongs
    to another season."""
    import re
    if re.fullmatch(r"\d{4}-\d{2}", season or ""):
        y = int(season[:4])
        return f"{y}-06-01", f"{y + 1}-07-31"
    if re.fullmatch(r"\d{4}", season or ""):
        return f"{season}-01-01", f"{season}-12-31"
    return None                      # not a season string this check understands: no check


def validate_split(code, split, prior, test, prior_season=None, test_season=None):
    """{"code","split","ok","reasons",...}. prior/test: (date, home, away, hg, ag).
    With season strings, rows outside each season's window are refused too
    (en.3 2025-26 holds January 2025; mx.1 2025-26 holds August 2026)."""
    out = {"code": code, "split": split, "ok": True, "reasons": [],
           "priorMatches": len(prior or []), "testMatches": len(test or [])}
    for label, rows, s in (("prior", prior, prior_season), ("test", test, test_season)):
        if not rows or not s:
            continue
        win = season_window(s)
        if not win:
            continue
        lo, hi = win
        bad = [r[0] for r in rows if not (lo <= r[0] <= hi)]
        if bad:
            out["reasons"].append(f"{label} season {s}: {len(bad)} of {len(rows)} matches dated "
                                  f"outside {lo}..{hi} ({min(bad)} to {max(bad)})")
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
                           data.get((code, test_s)) or [], prior_s, test_s)
        v["seasons"] = {"prior": prior_s, "test": test_s}
        (usable if v["ok"] else excluded).append(code if v["ok"] else v)
    return usable, excluded


def report_exclusions(excluded, out=sys.stderr):
    by_reason = defaultdict(list)
    for v in excluded:
        key = ("overlap" if any("overlap" in r or "outside" in r for r in v["reasons"])
               else "; ".join(v["reasons"]))
        by_reason[key].append(v)
    for key, vs in sorted(by_reason.items()):
        if key == "overlap":
            for v in vs:
                print(f"  EXCLUDED {v['code']} ({v['split']}, {v['seasons']['prior']} -> "
                      f"{v['seasons']['test']}): {'; '.join(v['reasons'])}", file=out)
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


# ---------------------------------------------------------------------------
# frozen snapshots and the advisory cache-expansion comparison
# ---------------------------------------------------------------------------

def _digest(obj):
    import hashlib, json
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def freeze(data, path):
    """Write the harness data plus the live build's season-so-far cache
    (current/, played matches only) to one file with its SHA-256."""
    import glob, json, time
    cur = {}
    here = os.path.dirname(os.path.abspath(__file__))
    for p in sorted(glob.glob(os.path.join(here, "current", "*.json"))):
        name = os.path.basename(p)[:-5]
        code, season = name.rsplit("-", 2)[0], "-".join(name.rsplit("-", 2)[1:])
        if "-" not in season or len(season) != 7:          # calendar year, e.g. us.1-2026
            code, season = name.rsplit("-", 1)
        with open(p) as f:
            doc = json.load(f)
        rows = [[r["date"], r["home"], r["away"], r["hg"], r["ag"]]
                for r in doc.get("rows", []) if r.get("hg") is not None]
        if rows:
            cur[f"{code}|{season}"] = sorted(rows)
    body = {"data": {f"{c}|{s}": [list(r) for r in v] for (c, s), v in data.items()}, "current": cur}
    body["sha256"] = _digest({"data": body["data"], "current": cur})
    body["created"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(body, f, separators=(",", ":"))
    return body


def load_snapshot(path):
    import json
    with open(path) as f:
        body = json.load(f)
    if _digest({"data": body["data"], "current": body["current"]}) != body["sha256"]:
        raise SystemExit(f"{path}: contents do not match its sha256; refusing to use it")
    data = {tuple(k.split("|")): [tuple(r) for r in v] for k, v in body["data"].items()}
    cur = {tuple(k.split("|")): [tuple(r) for r in v] for k, v in body["current"].items()}
    return data, cur, body["sha256"]


def season_source(code, season):
    """Where sources.fetch_season takes a season from, in its own order:
    a committed backfill (ESPN), football-data.co.uk, API-Football, else
    openfootball. Attribution for snapshot filtering and licensing."""
    import sources as S
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(here, "history", f"{code}-{season}.json")):
        return "espn-backfill"
    if code in S.FDX:
        return "football-data"
    if code in getattr(S, "AF", {}):
        return "api-football"
    return "openfootball"


def filter_snapshot(src, dst, keep=("openfootball",)):
    """Derive a snapshot holding only seasons from the sources in `keep`
    (the season-so-far cache is ESPN and is dropped). Records what was left
    out and the parent snapshot's hash."""
    import json, time
    data, cur, parent = load_snapshot(src)
    kept, dropped = {}, []
    for (code, season), rows in sorted(data.items()):
        srcname = season_source(code, season) if rows else "empty"
        if rows and srcname in keep:
            kept[f"{code}|{season}"] = [list(r) for r in rows]
        elif rows:
            dropped.append({"code": code, "season": season, "source": srcname, "matches": len(rows)})
    for (code, season), rows in sorted(cur.items()):
        dropped.append({"code": code, "season": season, "source": "espn-current-cache", "matches": len(rows)})
    body = {"data": kept, "current": {}}
    body["sha256"] = _digest({"data": kept, "current": {}})
    body.update({"created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "derivedFrom": parent, "sources": list(keep), "dropped": dropped})
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with open(dst, "w") as f:
        json.dump(body, f, separators=(",", ":"))
    return body


def expand_with_current(data, cur, codes, splits):
    """Advisory: fill each missing test season from the season-so-far cache.
    Returns (expanded copy, [(code, split, season, matches)] added)."""
    out, added = dict(data), []
    for code in codes:
        for split, (test_s, _) in splits(code).items():
            if not data.get((code, test_s)) and cur.get((code, test_s)):
                out[(code, test_s)] = cur[(code, test_s)]
                added.append((code, split, test_s, len(cur[(code, test_s)])))
    return out, added


def score_rows(rows):
    """log loss, accuracy, Brier and calibration bands with the shipped
    calibration, unchanged (advisory: nothing is refitted)."""
    import math, tune
    n = len(rows)
    if not n:
        return None
    ll = hit = br = 0.0
    bands = defaultdict(lambda: [0, 0, 0.0])
    for lh, la, y, *_ in rows:
        p = tune.outcome(lh, la, E.RHO)
        t = tune.curve_T(max(p), E.CALIBRATION) if E.CALIBRATION else E.TEMPERATURE
        q = [max(x, 1e-12) ** (1 / t) for x in p]
        s = sum(q)
        p = [x / s for x in q]
        ll += -math.log(max(p[y], 1e-12))
        k = p.index(max(p))
        hit += k == y
        br += sum((p[j] - (j == y)) ** 2 for j in range(3))
        b = min(int(max(p) * 10) / 10, 0.7)
        bands[b][0] += 1; bands[b][1] += k == y; bands[b][2] += max(p)
    return {"n": n, "logLoss": ll / n, "accuracy": hit / n, "brier": br / n,
            "bands": {f"{b:.1f}+": (v[0], v[1] / v[0], v[2] / v[0]) for b, v in sorted(bands.items())}}


def advisory_expansion(data, cur, sha):
    import tune
    codes = tune.codes()
    expanded, added = expand_with_current(data, cur, codes, tune.splits)
    print(f"frozen snapshot {sha}", file=sys.stderr)
    print("advisory only: calibration.json is used as shipped; nothing is refitted or written", file=sys.stderr)
    for split in ("fit", "check"):
        print(f"\n{split}", file=sys.stderr)
        orig_codes, orig_ex = coverage(data, codes, tune.splits, split)
        exp_codes, exp_ex = coverage(expanded, codes, tune.splits, split)
        add = [a for a in added if a[1] == split]
        print(f"  cache supplies a test season for {len(add)} competition(s): "
              f"{', '.join(f'{c} ({n})' for c, _, _, n in add) or 'none'}", file=sys.stderr)
        rows_o = [r for r in tune.lambdas(data, split, meta=True)]
        rows_e = [r for r in tune.lambdas(expanded, split, meta=True)]
        new_codes = sorted(set(exp_codes) - set(orig_codes))
        rows_new = [r for r in rows_e if r[3] in new_codes]
        for label, codes_, rows_ in (("original", orig_codes, rows_o), ("expanded", exp_codes, rows_e),
                                      ("added by the cache only", new_codes, rows_new)):
            m = score_rows(rows_)
            if not m:
                print(f"  {label:24} 0 competitions", file=sys.stderr)
                continue
            print(f"  {label:24} {len(codes_):3} competitions {m['n']:5} fixtures  "
                  f"log loss {m['logLoss']:.4f}  accuracy {m['accuracy']:.1%}  Brier {m['brier']:.4f}",
                  file=sys.stderr)
            print("  " + " " * 24 + " quoted vs landed: " + "  ".join(
                f"{b} n={v[0]} {v[2]:.0%}->{v[1]:.0%}" for b, v in m["bands"].items()), file=sys.stderr)
        bad = lambda v: any("overlap" in r or "outside" in r for r in v["reasons"])
        newly = [v for v in exp_ex if bad(v) and v["code"] not in {w["code"] for w in orig_ex if bad(w)}]
        if newly:
            print("  newly visible overlaps, excluded:", file=sys.stderr)
            report_exclusions(newly)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true", help="report usable and excluded competitions")
    ap.add_argument("--freeze", metavar="FILE", help="write a frozen data snapshot (harness data + current/) and stop")
    ap.add_argument("--snapshot", metavar="FILE", help="run --audit from a frozen snapshot instead of fetching")
    ap.add_argument("--filter-snapshot", nargs=2, metavar=("SRC", "DST"),
                    help="derive an openfootball-only snapshot from a frozen one and stop")
    ap.add_argument("--include-current", action="store_true",
                    help="advisory: also report coverage with test seasons filled from current/")
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tunecache"))
    args = ap.parse_args()
    if not (args.audit or args.freeze or args.filter_snapshot):
        ap.error("nothing to do: pass --audit, --freeze or --filter-snapshot")
    import tune
    if args.filter_snapshot:
        body = filter_snapshot(*args.filter_snapshot)
        print(f"kept {len(body['data'])} openfootball seasons, dropped {len(body['dropped'])} "
              f"(parent {body['derivedFrom'][:12]}...), sha256 {body['sha256']}", file=sys.stderr)
        return
    if args.freeze:
        os.makedirs(args.cache, exist_ok=True)
        body = freeze(tune.load(args.cache), args.freeze)
        print(f"froze {len(body['data'])} harness seasons and {len(body['current'])} cached "
              f"current seasons to {args.freeze}, sha256 {body['sha256']}", file=sys.stderr)
        return
    if args.snapshot:
        data, cur, sha = load_snapshot(args.snapshot)
    else:
        os.makedirs(args.cache, exist_ok=True)
        data, cur, sha = tune.load(args.cache), {}, None
    if args.include_current:
        if not args.snapshot:
            ap.error("--include-current needs --snapshot (freeze first), so both coverages use one frozen data set")
        advisory_expansion(data, cur, sha)
        return
    for split in ("fit", "check"):
        usable, excluded = coverage(data, tune.codes(), tune.splits, split)
        n = sum(len(data.get((c, tune.splits(c)[split][0])) or []) for c in usable)
        print(f"{split}: {len(usable)} usable competitions, {n} test fixtures; "
              f"{len(excluded)} excluded", file=sys.stderr)
        report_exclusions(excluded)


if __name__ == "__main__":
    main()
