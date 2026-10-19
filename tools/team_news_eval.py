#!/usr/bin/env python3
"""Advisory backtest: does team news (players missing) improve football
predictions? (19 Oct 2026, Douglas.) Changes nothing.

    python3 tools/team_news_eval.py --snapshot audit-out/snapshot.json --news audit-out/team-news

Each fixture is priced exactly as replay.replay_league would have that morning
(through tune.lambdas), then each side's expected goals move with its missing
players:

    lh *= exp(-a * missH + b * missA),   la *= exp(-a * missA + b * missH)

a: a side scores less without its players; b: it concedes more. Two candidate
measures of "missing", chosen before looking at results:

  count    players API-Football lists "Missing Fixture" (injured, suspended)
  minutes  the same players weighted by last season's league minutes
           (share of a full season, 34-38 x 90), so a regular counts about 1
           and a fringe player near 0; no data from the season predicted
  new      (added after the first two came out at zero) minutes-weighted
           absences now that were not there at the side's previous match:
           a long absence is already in recent results, a new one is not

a and b are fitted on 2025-26 (grid), checked on 2026-27 against the live
model, paired and bootstrapped, scored under the live calibration curve.
Gates as tune.py: >= 250 check fixtures, p(worse) <= 0.30, gain >= 0.0005.
"""
import argparse, json, math, os, sys
from collections import defaultdict
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import replay as R
import sources as S
import tune as T

LEAGUES = {"en.1": 39, "en.2": 40, "es.1": 140, "de.1": 78, "it.1": 135, "fr.1": 61, "nl.1": 88, "pt.1": 94}
SPLITS = {"fit": 2025, "check": 2026}          # API-Football season of each split's test season


def load(news, name):
    try:
        with open(os.path.join(news, name)) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def build_news(news, rows_by_code, season):
    """{(code, date, replay team): (count, minutes-weighted)} and a name report."""
    out, report = {}, {}
    for code in LEAGUES:
        inj = load(news, f"injuries-{code}-{season}.json") or []
        prev = load(news, f"players-{code}-{season - 1}.json") or []
        pool = sorted({t for (_, _, _, c, _, h, a) in rows_by_code.get(code, []) for t in (h, a) if c == code})
        if not pool or not inj:
            report[code] = {"injuryRows": len(inj), "teams": len(pool), "note": "no data"}
            continue
        # last season's league minutes per player (a player can appear for two clubs)
        mins = defaultdict(int)
        for p in prev:
            mins[p["playerId"]] += p.get("minutes") or 0
        full = 38 * 90
        names, unmatched = {}, set()
        for r in inj:
            t = r["team"]
            if t not in names:
                names[t] = S.match_team(t, pool)
                if not names[t]:
                    unmatched.add(t)
        for r in inj:
            team = names.get(r["team"])
            if not team or r.get("type") != "Missing Fixture" or not r.get("date"):
                continue
            k = (code, r["date"], team)
            c, m = out.get(k, (0, 0.0))
            out[k] = (c + 1, m + min(mins.get(r["playerId"], 0) / full, 1.0))
        report[code] = {"injuryRows": len(inj), "teams": len(pool), "afTeams": len(names),
                        "unmatched": sorted(unmatched)}
    return out, report


def lookup(news, code, d, team):
    """A fixture's news, allowing the date to differ by a day (time zones)."""
    for k in (d, (date.fromisoformat(d) - timedelta(days=1)).isoformat(),
              (date.fromisoformat(d) + timedelta(days=1)).isoformat()):
        v = news.get((code, k, team))
        if v:
            return v
    return (0, 0.0)


def new_absences(rows, news):
    """Per row: (home, away) minutes-weighted absences beyond the side's previous match."""
    seq = defaultdict(list)
    for i, r in enumerate(rows):
        for side, team in ((0, r[5]), (1, r[6])):
            seq[(r[3], team)].append((r[4], i, side))
    out = [[0.0, 0.0] for _ in rows]
    for (code, team), lst in seq.items():
        prev = None
        for d, i, side in sorted(lst):
            now = lookup(news, code, d, team)[1]
            if prev is not None:
                out[i][side] = max(0.0, now - prev)
            prev = now
    return [tuple(x) for x in out]


def score(rows, miss, a, b, live):
    adj = []
    for (lh, la, y, *_), (mh, ma) in zip(rows, miss):
        adj.append((lh * math.exp(-a * mh + b * ma), la * math.exp(-a * ma + b * mh), y))
    per, acc, _ = T.score_under(T.raw_probs(adj), live)
    return per, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=os.path.join(ROOT, "audit-out", "snapshot.json"))
    ap.add_argument("--news", default=os.path.join(ROOT, "audit-out", "team-news"))
    args = ap.parse_args()
    data, _, digest = R.load_snapshot(args.snapshot)
    live = T.live_baseline()
    print(f"snapshot {digest[:12]}, live calibration {T.describe(live)}")
    rows = {s: [r for r in T.lambdas(data, s, meta=True) if r[3] in LEAGUES] for s in SPLITS}
    by_code = {s: defaultdict(list) for s in SPLITS}
    for s in SPLITS:
        for r in rows[s]:
            by_code[s][r[3]].append(r)
    news, reports = {}, {}
    for s, season in SPLITS.items():
        news[s], reports[s] = build_news(args.news, by_code[s], season)
        for code, rep in reports[s].items():
            print(f"  {s} {code}: {rep}")
    # both signs: a test confined to "missing players hurt" could only land on zero
    grid_a = [x / 100 for x in range(-10, 16, 2)]
    grid_b = [x / 100 for x in range(-10, 16, 2)]
    for measure, k in (("count", 0), ("minutes", 1), ("new", None)):
        if k is None:
            miss = {s: new_absences(rows[s], news[s]) for s in SPLITS}
        else:
            miss = {s: [(lookup(news[s], r[3], r[4], r[5])[k], lookup(news[s], r[3], r[4], r[6])[k]) for r in rows[s]]
                    for s in SPLITS}
        cover = {s: sum(1 for m in miss[s] if m[0] or m[1]) for s in SPLITS}
        base = {s: score(rows[s], miss[s], 0, 0, live) for s in SPLITS}
        best = min(((sum(score(rows["fit"], miss["fit"], a, b, live)[0]) / len(rows["fit"]), a, b)
                    for a in grid_a for b in grid_b))
        _, a, b = best
        out = {}
        for s in SPLITS:
            per, acc = score(rows[s], miss[s], a, b, live)
            m, sd, pw = T.paired(per, base[s][0])
            out[s] = (m, sd, pw, acc, base[s][1])
        n_chk = len(rows["check"])
        gates = {"enoughData": n_chk >= T.MIN_HOLDOUT, "notWorse": out["check"][2] <= T.MAX_P_WORSE,
                 "worthIt": -out["check"][0] >= T.MIN_GAIN}
        print(f"\n{measure}: fitted a={a}, b={b}")
        for s in SPLITS:
            m, sd, pw, acc, acc0 = out[s]
            print(f"  {s:5} n {len(rows[s]):5} with news {cover[s]:5}  log loss {m:+.4f} (sd {sd:.4f}, p(worse) {pw:.3f})"
                  f"  top pick {acc0:.2%} -> {acc:.2%}")
        print("  gates: " + ", ".join(f"{g} {'PASS' if v else 'FAIL'}" for g, v in gates.items()))


if __name__ == "__main__":
    main()
