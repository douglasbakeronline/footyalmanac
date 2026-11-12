#!/usr/bin/env python3
"""
The Card's leg rule replayed on past seasons with football-data.co.uk prices.
Advisory, writes card-legs-history.json, changes nothing on the site.
29 Oct 2026, Douglas: "Why can't you grab data from last season and learn
that way?"

    python3 tools/card_legs_history.py            fit season (2025-26) and check season (2026-27 to date)
    python3 tools/card_legs_history.py --out FILE
    python3 tools/card_legs_history.py --seasons 2022-23,2023-24,2024-25   (#153) past seasons too, each
                                                  with the season before as its prior

The live Card (groupings.build_card) admits a football pick when the
bookmakers' fair chance is 60%+ at a price of 1.15 to 1.90, the league is a
core league, and the model's own number is at least 5 points UNDER the
market's. The evidence for that last cut is seven weeks of the live archive
(tools/market_check.py). This replays the same cut over whole seasons:

  model     the walk-forward replay's number for the pick, with the live
            calibration applied (odds.model_probs over tune.lambdas), so each
            number is what the site would have quoted that morning
  market    football-data's average price with the margin removed (odds.fair)
  result    the final result; a draw is a loss for a win pick

For each cut (under the market by 5+, near, above by 5+, and all 60%+) it
reports picks, landed, quoted, and singles return at the average and best
price with a bootstrap; by price band; and, for the under-market cut, the
closing-line value against the Pinnacle closing price where the file has it.
Then the simplest card: each day's three best under-market picks as one
treble (highest combined fair chance, combined price 2.0 to 3.0), won only
when all three win, with its return and the expected win rate.

football-data covers the main leagues of England, Scotland, Germany, Italy,
Spain, France, the Netherlands, Belgium, Portugal, Turkey and Greece
(odds.DIVS): most of the core leagues, not all. Rule 1 holds: nothing is
fitted here. Standard library only.
"""
import json, math, os, sys, time
from collections import defaultdict
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import engine as E, odds as O, groupings as G, tune

CUTS = {
    "all60": lambda m, f: True,
    "under5": lambda m, f: m <= f - G.CARD_UNDER_MARKET,
    "near": lambda m, f: abs(m - f) < G.CARD_UNDER_MARKET,
    "above5": lambda m, f: m >= f + G.CARD_UNDER_MARKET,
    "under8": lambda m, f: m <= f - 0.08,
}
BANDS = [(1.15, 1.35), (1.35, 1.55), (1.55, 1.75), (1.75, 1.91)]


def legs(pairs, wide=False, model=False):
    """(model probs, price row) -> candidate legs passing the price gate.
    wide=True takes the wider rule's gate too (1.08-2.10 at 60%+ since 11 Nov 2026, 55%+ before; the page's
    empty-day filler; 10 Nov 2026, #155), for the fillwide Card only."""
    out = []
    lo, hi = G.CARD_ODDS
    fair_min = G.CARD_FAIR_MIN
    if wide:
        lo, hi = min(lo, G.CARD_WIDE_ODDS[0]), max(hi, G.CARD_WIDE_ODDS[1]); fair_min = min(fair_min, G.CARD_WIDE_FAIR_MIN)
    for mp, r in pairs:
        pick = max(range(3), key=lambda i: mp[i])
        if pick == 1: continue
        f = O.fair(r["avg"])[pick]; price = r["avg"][pick]
        # model=True (10 Nov 2026): the Model card's gate, the model's own
        # chance at CARD_FAIR_MIN+ whatever the bookmakers say
        if (mp[pick] < G.CARD_FAIR_MIN if model else f < fair_min) or not (lo <= price <= hi): continue
        bp = O.best(r)[pick]
        clv = (bp * O.fair(r["close"])[pick] - 1) if r.get("close") else None
        out.append({"date": r["date"], "code": r["code"], "home": r["home"], "away": r["away"], "side": "h" if pick == 0 else "a",
                    "time": r.get("time"), "model": mp[pick], "fair": f, "price": price, "best": bp, "margin": sum(1 / o for o in r["avg"]),
                    "won": r["result"] == pick, "clv": clv, "core": not r["code"].startswith("af."),
                    # 6 Nov 2026: the opposition's and the draw's average price, so the
                    # whole-Card replay runs the live rule (CARD_OPP_MIN). Landed on
                    # main only on 9 Nov: #144 shipped card_season's use of them
                    # without this line, and tune.yml's weekly run died on KeyError.
                    "opp": r["avg"][2 if pick == 0 else 0], "draw": r["avg"][1]})
    return out


# 6 Nov 2026, Douglas: his own winning picks were favourites at about 1.40
# whose opposition was priced 10-12, and his losers favourites whose
# opposition was priced about 4. Same favourite price, a different game: the
# opposition's price says how much of the rest of the market is the draw. This
# buckets every candidate leg by the opposition's price, within favourite
# price bands, and reports landed v quoted and the singles return. Advisory.
# (Run on PR #143; restored to main 9 Nov 2026.)
OPP_BANDS = [(1.0, 4.0), (4.0, 6.0), (6.0, 9.0), (9.0, 99.0)]


def lopsided(L):
    out = {}
    for lo, hi in [(1.15, 1.91)] + BANDS:
        row = {}
        for olo, ohi in OPP_BANDS:
            b = [l for l in L if lo <= l["price"] < hi and olo <= l["opp"] < ohi]
            if len(b) < 10: continue
            w = sum(x["won"] for x in b); q = sum(x["fair"] for x in b) / len(b)
            pnl = [(x["price"] - 1) if x["won"] else -1.0 for x in b]
            roi, pr = O._boot(pnl)
            row[f"opp {olo:.0f}-{ohi:.0f}" if ohi < 99 else f"opp {olo:.0f}+"] = {
                "n": len(b), "landed": round(w / len(b), 3), "quoted": round(q, 3), "gap": round(w / len(b) - q, 3),
                "se": round(math.sqrt(q * (1 - q) / len(b)), 3), "roi": round(roi, 4), "pRoiNotPositive": round(pr, 3),
                "roiBest": round(sum((x["best"] - 1) if x["won"] else -1 for x in b) / len(b), 4),
                "drawPrice": round(sum(x["draw"] for x in b) / len(b), 2)}
        if row: out[f"{lo:.2f}-{min(hi, 1.90):.2f}"] = row
    return out


# 9 Nov 2026 (#153): the gap bands the Card rule is judged on (model under the
# bookmakers' chance, in points) and the opposition-price bands, for the
# per-season report.
GAP_BANDS = [("5-8 under", 0.05, 0.08), ("8-10 under", 0.08, 0.10), ("10+ under", 0.10, 9.0)]


def by_gap(L):
    out = {}
    for name, lo, hi in GAP_BANDS:
        b = [l for l in L if lo <= l["fair"] - l["model"] < hi]
        if len(b) >= 10: out[name] = summary(b)
    for olo, ohi in OPP_BANDS[1:]:
        b = [l for l in L if olo <= l["opp"] < ohi]
        if len(b) >= 10: out[f"opp {olo:.0f}-{ohi:.0f}" if ohi < 99 else f"opp {olo:.0f}+"] = summary(b)
    return out


def summary(L):
    n = len(L)
    if not n: return {"n": 0}
    w = sum(l["won"] for l in L); q = sum(l["fair"] for l in L)
    pnl = [(l["price"] - 1) if l["won"] else -1.0 for l in L]; pnlb = [(l["best"] - 1) if l["won"] else -1.0 for l in L]
    roi, p = O._boot(pnl); roib, pb = O._boot(pnlb)
    clv = [l["clv"] for l in L if l["clv"] is not None]; cm, cp = O._boot(clv) if clv else (None, None)
    bands = {}
    for lo, hi in BANDS:
        b = [l for l in L if lo <= l["price"] < hi]
        if b: bands[f"{lo:.2f}-{min(hi, 1.90):.2f}"] = {"n": len(b), "landed": round(sum(x["won"] for x in b) / len(b), 3), "quoted": round(sum(x["fair"] for x in b) / len(b), 3),
                                                       "roi": round(sum((x["price"] - 1) if x["won"] else -1 for x in b) / len(b), 4)}
    return {"n": n, "landed": round(w / n, 4), "quoted": round(q / n, 4), "gap": round((w - q) / n, 4), "se": round(math.sqrt(q / n * (1 - q / n) / n), 4),
            "roi": round(roi, 4), "pRoiNotPositive": round(p, 3), "roiBest": round(roib, 4), "pRoiBestNotPositive": round(pb, 3),
            "clvBets": len(clv), "clv": round(cm, 4) if cm is not None else None, "pClvNotPositive": round(cp, 3) if cp is not None else None,
            "bands": bands}


def edge_legs(L):
    """The green Edge flag's football legs (groupings.edge_flag, 10 Nov 2026):
    the bookmakers 60%+ at CARD_ODDS (the legs() gate), the opposition priced
    CARD_OPP_MIN+, the model no more than MULT_ABOVE_BOOK above the market.
    The replay's leagues are football-data's, the flag's own."""
    omin = getattr(G, "EDGE_OPP_MIN", None) or G.CARD_OPP_MIN.get("football") or 9.0   # the Edge flag's own floor (4/1 from 11 Nov 2026)
    return [l for l in L if l["opp"] >= omin and l["model"] - l["fair"] <= G.MULT_ABOVE_BOOK]


def edge_accas(L, sizes=(1, 2, 3, 4)):
    """Edge-flag legs combined (10 Nov 2026, Douglas bets accumulators): for
    each day with at least k flagged legs, the k most likely by the
    bookmakers' chance as one accumulator, and every flagged leg of the day
    as one. Won, expected (product of the bookmakers' chance), return per
    unit at the average and the best price, with a bootstrap p(return <= 0)."""
    return accas(edge_legs(L), sizes)


def accas(legs_, sizes=(1, 2, 3, 4)):
    """Any set of legs as edge_accas combines the Edge flag's (11 Nov 2026:
    split out so the mismatch rule, #224, is slipped the same way)."""
    by = defaultdict(list)
    for l in legs_: by[l["date"]].append(l)
    out = {}
    for k in list(sizes) + ["all"]:
        gs = []
        for d, ls in sorted(by.items()):
            ls = sorted(ls, key=lambda l: -l["fair"])
            if k == "all":
                if len(ls) < 2: continue
                c = ls
            else:
                if len(ls) < k: continue
                c = ls[:k]
            gs.append({"date": d, "won": all(l["won"] for l in c), "p": math.prod(l["fair"] for l in c),
                       "odds": math.prod(l["price"] for l in c), "best": math.prod(l["best"] for l in c), "legs": len(c)})
        if not gs: out[str(k)] = {"n": 0}; continue
        n = len(gs); w = sum(g["won"] for g in gs)
        pnl = [(g["odds"] - 1) if g["won"] else -1.0 for g in gs]; pnlb = [(g["best"] - 1) if g["won"] else -1.0 for g in gs]
        roi, p = O._boot(pnl); roib, pb = O._boot(pnlb)
        months = defaultdict(float)
        for g, x in zip(gs, pnl): months[g["date"][:7]] += x
        out[str(k)] = {"n": n, "won": w, "landed": round(w / n, 3), "expected": round(sum(g["p"] for g in gs) / n, 3),
                       "avgOdds": round(sum(g["odds"] for g in gs) / n, 2), "avgLegs": round(sum(g["legs"] for g in gs) / n, 2),
                       "roi": round(roi, 4), "pRoiNotPositive": round(p, 3), "roiBest": round(roib, 4), "pRoiBestNotPositive": round(pb, 3),
                       "losingMonths": sum(1 for v in months.values() if v < 0), "months": len(months)}
    return out


# 11 Nov 2026 (#224), Douglas, after an 8-fold at 8.16 won: "finding teams
# near the top of the table, on a good run of recent form, who have scored
# relatively a lot and conceded relatively few in their league, then finding a
# home fixture where the opponent has the opposite on all those variables."
# The question is whether these home wins BEAT THEIR PRICE, not whether they
# win. The rule was fixed on the issue before any result was read; nothing
# here is tuned. Interpretations of the wording, fixed with the code:
#   - the table is every league match in football-data's season file played on
#     an EARLIER date (same-day games never count), 3 / 1 / 0, ranked on
#     points, goal difference, goals for; the league's size is every team in
#     the file
#   - top quarter: position <= size / 4; bottom half: position > size / 2
#   - "top third" of a per-game rate: fewer than a third of the teams that have
#     played are strictly better on it (ties share the better place); goals
#     scored is better when higher, goals conceded when lower
#   - last-5 points: the side's last five league games before the date
# Price band 1.15-1.60 on the home side's average price. Advisory.
MM_PRICE = (1.15, 1.60)
MM_MIN_GAMES = 6
MM_GP_BANDS = [("6-10", 6, 10), ("11-20", 11, 20), ("21+", 21, 999)]
MM_SIZES = (1, 2, 4, 6, 8)


def results_rows(text):
    """Every finished match in a football-data file, priced or not: the table
    needs them all (odds.parse keeps only the priced ones)."""
    import csv, io
    out = []
    if not text: return out
    for r in csv.DictReader(io.StringIO(text.lstrip("﻿"))):
        d = O._date(r.get("Date") or "")
        h = (r.get("HomeTeam") or r.get("Home") or "").strip(); a = (r.get("AwayTeam") or r.get("Away") or "").strip()
        try: hg, ag = int(float(r.get("FTHG") or r.get("HG") or "")), int(float(r.get("FTAG") or r.get("AG") or ""))
        except ValueError: hg = ag = None
        if d and h and a: out.append({"date": d, "home": h, "away": a, "hg": hg, "ag": ag})
    return out


def _share_rank(vals, team, higher_better):
    """1 + the number of teams strictly better than `team` on vals."""
    v = vals[team]
    return 1 + sum(1 for t, x in vals.items() if (x > v if higher_better else x < v))


def table_before(rows, day):
    """Each team's record from league matches before `day`: played, points,
    gf, ga, the last five games' points, and its table position."""
    st = {}
    teams = {r["home"] for r in rows} | {r["away"] for r in rows}
    for t in teams: st[t] = {"gp": 0, "pts": 0, "gf": 0, "ga": 0, "seq": []}
    for r in sorted((r for r in rows if r["date"] < day and r["hg"] is not None), key=lambda r: r["date"]):
        for t, f, a in ((r["home"], r["hg"], r["ag"]), (r["away"], r["ag"], r["hg"])):
            p = 3 if f > a else 1 if f == a else 0
            s = st[t]; s["gp"] += 1; s["pts"] += p; s["gf"] += f; s["ga"] += a; s["seq"].append(p)
    order = sorted(teams, key=lambda t: (-st[t]["pts"], -(st[t]["gf"] - st[t]["ga"]), -st[t]["gf"], t))
    for i, t in enumerate(order): st[t]["pos"] = i + 1; st[t]["last5"] = sum(st[t]["seq"][-5:])
    played = [t for t in teams if st[t]["gp"]]
    gf = {t: st[t]["gf"] / st[t]["gp"] for t in played}; ga = {t: st[t]["ga"] / st[t]["gp"] for t in played}
    for t in played:
        st[t]["gfTop"] = _share_rank(gf, t, True) <= len(played) / 3        # scores a lot
        st[t]["gfBottom"] = _share_rank(gf, t, False) <= len(played) / 3    # scores little
        st[t]["gaFew"] = _share_rank(ga, t, False) <= len(played) / 3       # concedes few
        st[t]["gaMany"] = _share_rank(ga, t, True) <= len(played) / 3       # concedes a lot
    return st, len(teams)


def mismatch_rule(h, a, size):
    """The pre-registered rule on two table rows (#224)."""
    if h["gp"] < MM_MIN_GAMES or a["gp"] < MM_MIN_GAMES: return False
    home = h["pos"] <= size / 4 and h["last5"] >= 10 and h["gfTop"] and h["gaFew"]
    away = a["pos"] > size / 2 and a["last5"] <= 5 and a["gfBottom"] and a["gaMany"]
    return home and away


def mismatch_legs(texts, edge_keys=frozenset()):
    """Home-win legs passing the rule, from each division's season file.
    edge_keys: (code, date, home, away) of the Edge flag's home legs, to say
    how many of these the flag already catches."""
    out = []
    for text in texts:
        rows = results_rows(text)
        if not rows: continue
        cache = {}
        for r in O.parse(text):
            if r["result"] is None: continue
            price = r["avg"][0]
            if not (MM_PRICE[0] <= price <= MM_PRICE[1]): continue
            if r["date"] not in cache: cache[r["date"]] = table_before(rows, r["date"])
            st, size = cache[r["date"]]
            h, a = st.get(r["home"]), st.get(r["away"])
            if not h or not a or not mismatch_rule(h, a, size): continue
            out.append({"date": r["date"], "code": r["code"], "home": r["home"], "away": r["away"], "time": r.get("time"),
                        "fair": O.fair(r["avg"])[0], "price": price, "best": O.best(r)[0], "won": r["result"] == 0,
                        "opp": r["avg"][2], "draw": r["avg"][1], "gp": h["gp"], "clv": None,
                        "edge": (r["code"], r["date"], r["home"], r["away"]) in edge_keys})
    return out


def mismatch_report(M):
    """Singles, slips and the games-played split for one season's legs (or
    the pooled legs of several)."""
    s = summary(M)
    s.pop("bands", None)
    res = {"singles": s, "slips": accas(M, MM_SIZES), "edgeCaught": sum(l["edge"] for l in M),
           "notEdge": summary([l for l in M if not l["edge"]]), "byGamesPlayed": {}}
    res["notEdge"].pop("bands", None)
    for name, lo, hi in MM_GP_BANDS:
        b = [l for l in M if lo <= l["gp"] <= hi]
        row = summary(b); row.pop("bands", None)
        row["slips4"] = accas(b, (4,))["4"]
        res["byGamesPlayed"][name] = row
    return res


def mismatch_verdict(per_season, pooled):
    """The issue's gate: the singles land above the bookmakers' fair chance in
    at least 4 of 5 seasons, and pooled p(return <= 0) at the best price is
    0.30 or less. Applied to all legs and to each games-played band."""
    def gate(rows, pool):
        ahead = sum(1 for r in rows if r.get("n") and r["landed"] > r["quoted"])
        ok = ahead >= 4 and len(rows) >= 5 and pool.get("n", 0) and pool["pRoiBestNotPositive"] <= 0.30
        return {"seasons": len(rows), "aheadOfPrice": ahead, "pBest": pool.get("pRoiBestNotPositive"), "passes": bool(ok)}
    out = {"all": gate([r["singles"] for r in per_season], pooled["singles"])}
    for name, _, _ in MM_GP_BANDS:
        out[name] = gate([r["byGamesPlayed"][name] for r in per_season], pooled["byGamesPlayed"][name])
    return out


def trebles(L):
    """One treble a day from the under-market legs: the three with the highest
    combined fair chance whose combined price is 2.0 to 3.0."""
    by = defaultdict(list)
    for l in L: by[l["date"]].append(l)
    out = []
    import itertools
    for d, legs_ in by.items():
        if len(legs_) < 3: continue
        cands = sorted(legs_, key=lambda l: -l["fair"])[:12]
        top = None
        for c in itertools.combinations(cands, 3):
            o = math.prod(l["price"] for l in c)
            if not (2.0 <= o <= 3.0): continue
            p = math.prod(l["fair"] for l in c)
            if not top or p > top[0]: top = (p, o, c)
        if top:
            p, o, c = top
            out.append({"date": d, "p": p, "odds": o, "won": all(l["won"] for l in c)})
    if not out: return {"n": 0}
    n = len(out); w = sum(g["won"] for g in out); exp = sum(g["p"] for g in out)
    pnl = [(g["odds"] - 1) if g["won"] else -1.0 for g in out]; roi, p = O._boot(pnl)
    return {"n": n, "won": w, "landed": round(w / n, 3), "expected": round(exp / n, 3), "roi": round(roi, 4), "pRoiNotPositive": round(p, 3),
            "z": round((w - exp) / math.sqrt(sum(g["p"] * (1 - g["p"]) for g in out)), 2) if n else None}


def card_season(L, variant="live"):
    """The whole Card, as groupings.build_card builds it today, over a season
    of football-data legs: one window a day, Card 2x and 3x then a second of
    each, CARD_STAKE units, graded strictly. Returns the summary and the
    day-by-day running profit in units."""
    sys.path.insert(0, os.path.join(HERE, "tools"))
    import card_replay as CR
    by = defaultdict(list)
    for l in L:
        when = f"{l['date']}T{l['time'] or '15:00'}:00Z"
        leg = {"sport": "football", "event": f"{l['home']} v {l['away']}", "pick": l["home"] if l["side"] == "h" else l["away"],
               "comp": l["code"], "code": l["code"], "when": when, "date": l["date"], "odds": round(l["price"], 2), "best": round(l["best"], 2),
               "margin": round(l["margin"], 4), "est": False, "pModel": round(l["model"], 4), "p": round(l["model"], 4),
               "hit": 0.8, "n": 100, "won": l["won"], "core": l["core"], "opp": round(l["opp"], 2), "draw": round(l["draw"], 2)}
        G.honest(leg)
        slot = G.uk_slot(leg)
        if slot: by[slot[0]].append(leg)
    days, run, series, months = {}, 0.0, [], defaultdict(lambda: [0, 0, 0.0, 0.0])
    for d in sorted(by):
        gs = CR.build(by[d], d, variant)
        if not gs: continue
        days[d] = gs
        pnl = sum(g["stake"] * (g["odds"] - 1) if g["won"] else -g["stake"] for g in gs)
        run += pnl; series.append([d, round(run, 2)])
        m = months[d[:7]]; m[0] += len(gs); m[1] += sum(g["won"] for g in gs); m[2] += sum(g["stake"] for g in gs); m[3] += pnl
    gs = [g for d in days.values() for g in d]
    if not gs: return {"groups": 0}
    n, w = len(gs), sum(g["won"] for g in gs); exp = sum(g["p"] for g in gs)
    st_ = sum(g["stake"] for g in gs); ret = sum(g["stake"] * g["odds"] for g in gs if g["won"]); best = sum(g["stake"] * g["bestOdds"] for g in gs if g["won"])
    kinds = {}
    for name in dict.fromkeys(g["name"] for g in gs):   # 11 Nov 2026: payout variants carry their own kinds
        k = [g for g in gs if g["name"] == name]
        if k:
            ks = sum(g["stake"] for g in k); kr = sum(g["stake"] * g["odds"] for g in k if g["won"])
            kinds[name] = {"n": len(k), "won": sum(g["won"] for g in k), "expected": round(sum(g["p"] for g in k) / len(k), 3), "return": round(kr / ks, 3)}
    # bootstrap over days for the return per unit
    import random
    random.seed(7); keys = list(days); vals = []
    for _ in range(2000):
        pick = [days[random.choice(keys)] for _ in keys]
        s_ = sum(g["stake"] for d in pick for g in d); r_ = sum(g["stake"] * g["odds"] for d in pick for g in d if g["won"])
        vals.append(r_ / s_ if s_ else 1)
    vals.sort()
    return {"days": len(days), "groups": n, "won": w, "expected": round(exp, 2), "landed": round(w / n, 3), "expectedRate": round(exp / n, 3),
            "z": round((w - exp) / math.sqrt(sum(g["p"] * (1 - g["p"]) for g in gs)), 2),
            "units": st_, "returned": round(ret, 2), "return": round(ret / st_, 3), "returnBest": round(best / st_, 3),
            "return90": [round(vals[100], 3), round(vals[1899], 3)], "pLoss": round(sum(v < 1 for v in vals) / len(vals), 3),
            "kinds": kinds, "months": {m: {"groups": v[0], "won": v[1], "units": v[2], "pnl": round(v[3], 2)} for m, v in sorted(months.items())},
            "series": series,
            # 9 Nov 2026: every group, for tools/staking.py
            "groupList": [{"date": d, "name": g["name"], "p": round(g["p"], 4), "odds": round(g["odds"], 2), "stake": g["stake"], "won": bool(g["won"])}
                          for d in sorted(days) for g in days[d]]}


def season_split(season):
    """A tune.splits stand-in for one past season: every competition replayed
    on `season` with the season before as its prior (9 Nov 2026, #153)."""
    prior = E.season_prev(season)[0]
    return lambda code: {"season": (season, prior)}


def replay_split(split, splits_fn, log):
    """One season through the replay and football-data: fetch, rate, price,
    join, and every table of the report. splits_fn stands in for tune.splits
    while it runs (tune.load, tune.lambdas and replay.coverage all read it)."""
    saved = tune.splits; tune.splits = splits_fn
    try:
        data = tune.load(None)
        preds = O.model_probs(tune.lambdas(data, split, meta=True))
        prices, season, texts = [], None, []
        for div, code in O.DIVS.items():
            if code not in E.LEAGUES: continue
            s = splits_fn(code)[split][0]
            if "-" not in s: continue
            season = season or s
            text = O._get(O.HIST_URL.format(yy=O._yy(s), div=div), log=log)
            texts.append(text)      # 11 Nov 2026 (#224): the mismatch rule's table
            prices += O.parse(text)
            time.sleep(1.0)
    finally:
        tune.splits = saved
    prices = [r for r in prices if r["result"] is not None]
    fixtures = [((c, d, h, a), c, d, h, a) for (c, d, h, a) in preds]
    joined = O.match(prices, fixtures)
    L = legs([(preds[k], r) for k, r in joined.items()])
    Lw = legs([(preds[k], r) for k, r in joined.items()], wide=True)
    under = [l for l in L if CUTS["under5"](l["model"], l["fair"])]
    res = {"season": season, "pricedMatches": len(prices), "matched": len(joined), "candidates": len(L), "cuts": {}}
    for name, f in CUTS.items():
        res["cuts"][name] = summary([l for l in L if f(l["model"], l["fair"])])
    res["trebles"] = trebles(under)
    res["card"] = card_season(L)
    # 11 Nov 2026: "card" is the live rule (8); cardRule5, cardUncapped and
    # cardOpp7, and the rule5 / opp7 fillers, are built on the rule 6 Card
    # (card_replay.RULE6_FAMILY): on live they rebuilt live exactly
    res["cardRule5"] = card_season(L, "rule5")   # 6 Nov 2026: the Card as it was before the opposition-price condition
    # 9 Nov 2026 (Douglas: "take all decisions on providing the highest return
    # consistently"): the two open rule questions, replayed as whole Cards on
    # every season so the 30 Nov review has the football-data side of the gate
    res["cardUncapped"] = card_season(L, "uncapped")   # rule 4: no 10-under cap
    res["cardOpp7"] = card_season(L, "opp7")           # the opposition at 7+ rather than 9+
    # 10 Nov 2026 (#155): the empty-day fillers, live plus a filler only on a
    # day the full rule leaves empty; fillwide is the page's fallback today
    res["cardFillWide"] = card_season(Lw, "fillwide")
    res["cardFillRule5"] = card_season(L, "fillrule5")
    res["cardFillOpp7"] = card_season(L, "fillopp7")
    # 10 Nov 2026: the Model card's rule on the same seasons, for the 30 Nov review
    res["cardModel"] = card_season(legs([(preds[k], r) for k, r in joined.items()], model=True), "modelcard")
    # 11 Nov 2026 (CARD_RULE 7, Douglas: "Just do better on the groups"): the
    # live Card is now the model's own picks; it and its pre-registered shape
    # variants on the model's legs, for choosing the group shape
    Lm = legs([(preds[k], r) for k, r in joined.items()], model=True)
    res["cardM7"] = {v: card_season(Lm, v) for v in ("live", "m7edge3", "m7edge6", "m7legs3", "m7short", "m7only2x", "m7legs2",
                                          # 11 Nov 2026: payout bands (Douglas: 3x, then 2.5x, 2x, 1.5x)
                                          "pay15", "pay25", "pay3", "ladder")}
    res["edgeAccas"] = edge_accas(L)   # 10 Nov 2026: the Edge flag's legs as accumulators
    # 11 Nov 2026 (#224): Douglas's mismatch rule, judged against the price
    ek = frozenset((l["code"], l["date"], l["home"], l["away"]) for l in edge_legs(L) if l["side"] == "h")
    M = mismatch_legs(texts, ek)
    res["mismatch"] = mismatch_report(M)
    res["mismatch"]["legs"] = [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in l.items()} for l in M]
    res["lopsided"] = {"all": lopsided(L), "under5": lopsided(under)}
    res["byGap"] = {"all60": by_gap(L), "under5": by_gap(under)}   # 9 Nov 2026 (#153)
    res["legs"] = [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in l.items()} for l in L]
    return res


def show(label, res):
    print(f"{label} {res['season']}: {res['pricedMatches']} priced, {res['matched']} matched, {res['candidates']} candidate legs")
    for name, c in res["cuts"].items():
        if c.get("n"): print(f"  {name:8s} n {c['n']:5d} landed {c['landed']*100:5.1f} quoted {c['quoted']*100:5.1f} (se {c['se']*100:.1f}) roi {c['roi']*100:+5.1f}% (p {c['pRoiNotPositive']}) best {c['roiBest']*100:+5.1f}% clv {c['clv']}")
    for cut, tab in res["byGap"].items():
        for band, c in tab.items():
            print(f"  gap {cut:6s} {band:10s} n {c['n']:5d} landed {c['landed']*100:5.1f} quoted {c['quoted']*100:5.1f} (se {c['se']*100:.1f}) roi {c['roi']*100:+5.1f}% best {c['roiBest']*100:+5.1f}%")
    t = res["trebles"]
    if t.get("n"): print(f"  trebles n {t['n']} won {t['won']} landed {t['landed']*100:.0f}% expected {t['expected']*100:.0f}% roi {t['roi']*100:+.0f}% z {t['z']}")
    for cut, tab in res["lopsided"].items():
        for band, row in tab.items():
            for k, v in row.items():
                print(f"  lopsided {cut:6s} fav {band} {k:9s} n {v['n']:4d} landed {v['landed']*100:5.1f} quoted {v['quoted']*100:5.1f} (se {v['se']*100:.1f}) roi {v['roi']*100:+5.1f}% best {v['roiBest']*100:+5.1f}% draw {v['drawPrice']}")
    for k, a in (res.get("edgeAccas") or {}).items():
        if a.get("n"): print(f"  edge acca {k:>3}: n {a['n']:4d} won {a['won']:4d} landed {a['landed']*100:5.1f}% v expected {a['expected']*100:5.1f}%  avg odds {a['avgOdds']:.2f} legs {a['avgLegs']}  roi {a['roi']*100:+5.1f}% (p {a['pRoiNotPositive']}) best {a['roiBest']*100:+5.1f}% (p {a['pRoiBestNotPositive']})  losing months {a['losingMonths']} of {a['months']}")
    mm = res.get("mismatch")
    if mm: show_mismatch(mm)
    for lab in ("card", "cardRule5", "cardUncapped", "cardOpp7", "cardFillWide", "cardFillRule5", "cardFillOpp7", "cardModel"):
        c = res[lab]
        if c.get("groups"):
            losing = [m for m, v in c["months"].items() if v["pnl"] < 0]
            print(f"  {lab}: {c['days']} days, {c['groups']} groups, won {c['won']} (exp {c['expected']}), z {c['z']}, units {c['units']}, return {c['return']} (best {c['returnBest']}), 90% {c['return90']}, p(loss) {c['pLoss']}, kinds {c['kinds']}, losing months {len(losing)} of {len(c['months'])}: {', '.join(losing)}")
    for v, c in (res.get("cardM7") or {}).items():
        # 11 Nov 2026: the rule 7 Card and its shape variants
        if c.get("groups"):
            losing = [m for m, x in c["months"].items() if x["pnl"] < 0]
            print(f"  cardM7 {v}: {c['days']} days, {c['groups']} groups, won {c['won']} (exp {c['expected']}), units {c['units']}, return {c['return']} (best {c['returnBest']}), p(loss) {c['pLoss']}, kinds {c['kinds']}, losing months {len(losing)} of {len(c['months'])}")
        else:
            print(f"  cardM7 {v}: no groups")


def show_mismatch(mm, label="mismatch"):
    c = mm["singles"]
    if not c.get("n"): print(f"  {label}: no legs"); return
    print(f"  {label} singles n {c['n']} landed {c['landed']*100:.1f} quoted {c['quoted']*100:.1f} (se {c['se']*100:.1f}) roi {c['roi']*100:+.1f}% (p {c['pRoiNotPositive']}) best {c['roiBest']*100:+.1f}% (p {c['pRoiBestNotPositive']}); Edge already flags {mm['edgeCaught']}")
    ne = mm["notEdge"]
    if ne.get("n"): print(f"  {label} not Edge n {ne['n']} landed {ne['landed']*100:.1f} quoted {ne['quoted']*100:.1f} roi {ne['roi']*100:+.1f}% best {ne['roiBest']*100:+.1f}%")
    for k, a in mm["slips"].items():
        if a.get("n"): print(f"  {label} slip {k:>3}: n {a['n']} won {a['won']} landed {a['landed']*100:.1f}% v {a['expected']*100:.1f}% odds {a['avgOdds']} roi {a['roi']*100:+.1f}% best {a['roiBest']*100:+.1f}% (p {a['pRoiBestNotPositive']}) losing months {a['losingMonths']} of {a['months']}")
    for b, r in mm["byGamesPlayed"].items():
        if r.get("n"):
            s4 = r["slips4"]
            print(f"  {label} games {b:5s} n {r['n']} landed {r['landed']*100:.1f} quoted {r['quoted']*100:.1f} roi {r['roi']*100:+.1f}% best {r['roiBest']*100:+.1f}% (p {r['pRoiBestNotPositive']})"
                  + (f"; 4-folds n {s4['n']} won {s4['won']} best {s4['roiBest']*100:+.1f}%" if s4.get("n") else ""))


def main():
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "card-legs-history.json")
    # 9 Nov 2026 (#153): past seasons beyond the fit and check seasons, e.g.
    # --seasons 2022-23,2023-24,2024-25; each is replayed with the season
    # before as its prior and priced from football-data's season file
    extra = [x for x in (sys.argv[sys.argv.index("--seasons") + 1] if "--seasons" in sys.argv else "").split(",") if x]
    log = []
    report = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": "football-data.co.uk",
              "rule": {"fairMin": G.CARD_FAIR_MIN, "odds": G.CARD_ODDS, "underMarket": G.CARD_UNDER_MARKET, "underMax": G.CARD_UNDER_MAX,
                       "oppMin": G.CARD_OPP_MIN, "legs": list(G.CARD_LEGS), "cardRule": G.CARD_RULE}, "seasons": {}}
    for split in ("fit", "check"):
        res = replay_split(split, tune.splits, log)
        report["seasons"][split] = res
        show(split, res)
    for season in extra:
        try:
            res = replay_split("season", season_split(season), log)
        except Exception as e:     # a season with no data on either source is reported, not fatal
            print(f"{season}: not replayed ({e})"); report["seasons"][season] = {"season": season, "error": str(e)}; continue
        report["seasons"][season] = res
        show(season, res)
    # 11 Nov 2026 (#224): the mismatch rule pooled over every season replayed,
    # and the issue's gate (4 of 5 seasons ahead of the price, pooled p <= 0.30)
    done = [r for r in report["seasons"].values() if r.get("mismatch")]
    pool = [l for r in done for l in r["mismatch"]["legs"]]
    for l in pool: l.setdefault("clv", None)
    pooled = mismatch_report(pool)
    report["mismatchPooled"] = {"seasons": [r["season"] for r in done], **pooled,
                                "verdict": mismatch_verdict([r["mismatch"] for r in done], pooled)}
    show_mismatch(pooled, "mismatch pooled")
    print("mismatch verdict", json.dumps(report["mismatchPooled"]["verdict"]))
    u_fit = report["seasons"]["fit"]["cuts"].get("under5", {}); u_chk = report["seasons"]["check"]["cuts"].get("under5", {})
    holds = lambda c: c.get("n", 0) >= O.MIN_BETS and c.get("gap", 0) > 0 and c.get("roi", 0) > 0
    report["verdict"] = ("The under-market cut lands above its quote and returns a profit on both seasons." if holds(u_fit) and holds(u_chk) else
                         "The under-market cut does not hold on both seasons; read the per-season figures.")
    report["log"] = log[-20:]
    with open(out_path, "w") as f: json.dump(report, f, indent=1)
    print(report["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
