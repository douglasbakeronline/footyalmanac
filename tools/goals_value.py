#!/usr/bin/env python3
"""
Value backtest on the goals market: over / under 2.5 against football-data.co.uk
prices. Advisory, writes goals-value.json, changes nothing on the site.
29 Oct 2026, Douglas: "do a value backtest on the goals market".

    python3 tools/goals_value.py            fit season (2025-26) and check season (2026-27 to date)
    python3 tools/goals_value.py --out FILE write the report elsewhere

The question: does the model's over-2.5 number, which falls out of the same
Dixon-Coles grid as the match-winner numbers (engine.probabilities_from_xg,
with the two-way shrink the site publishes), out-price the goals market the
way it failed to out-price the match-winner market (odds.py: the market wins
on log loss, 0.979 v 1.013)?

Method, the same walk-forward as odds.backtest: tune.lambdas replays each
season a day at a time, so every expected-goals pair is what the site would
have published that morning; football-data's main-league files carry the
average and best pre-match over/under 2.5 prices and the closing average.
Matched on league, date and club name (odds.match). For each match:

  model     P(over 2.5) from the grid, shrunk as published
  market    the average price's fair chance (margin removed)
  pick      over or under, whichever side the model rates above the market
            by EDGE or more at the best price; one bet a match at most
  grade     landed or not, profit at best price, closing-line value
            (best price taken x the closing fair chance - 1)

Reports log loss of model v market on over 2.5, calibration of the model's
over number by band, and the value picks' hit rate, ROI and CLV with a
bootstrap, per season. Rule 1 holds: nothing is fitted here. Standard library only.
"""
import csv, io, json, math, os, random, sys, time
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import engine as E, odds as O, tune

EDGE = 0.05
BANDS = [(0.0, 0.40), (0.40, 0.45), (0.45, 0.50), (0.50, 0.55), (0.55, 0.60), (0.60, 0.65), (0.65, 1.01)]


def parse_goals(text):
    """football-data rows with over/under 2.5 prices: avg, max, closing avg, and the total goals."""
    out = []
    if not text:
        return out
    for r in csv.DictReader(io.StringIO(text.lstrip("﻿"))):
        code = O.DIVS.get((r.get("Div") or "").strip())
        d = O._date(r.get("Date") or "")
        home = (r.get("HomeTeam") or r.get("Home") or "").strip()
        away = (r.get("AwayTeam") or r.get("Away") or "").strip()
        if not code or not d or not home or not away:
            continue
        avg = (O._num(r, "Avg>2.5"), O._num(r, "Avg<2.5"))
        if not all(avg):
            avg = (O._num(r, "B365>2.5"), O._num(r, "B365<2.5"))
        if not all(avg):
            continue
        try:
            goals = int(r.get("FTHG")) + int(r.get("FTAG"))
        except (TypeError, ValueError):
            goals = None
        mx = (O._num(r, "Max>2.5"), O._num(r, "Max<2.5"))
        close = (O._num(r, "AvgC>2.5"), O._num(r, "AvgC<2.5"))
        if not all(close):
            close = (O._num(r, "PC>2.5"), O._num(r, "PC<2.5"))
        out.append({"code": code, "date": d, "home": home, "away": away, "avg": avg,
                    "max": mx if all(mx) else None, "close": close if all(close) else None,
                    "goals": goals, "result": 0 if goals is not None and goals >= 3 else 1 if goals is not None else None})
    return out


def model_over(rows):
    """tune.lambdas meta rows -> {(code, date, home, away): P(over 2.5)} as the site publishes it."""
    out = {}
    for lh, la, y, code, d, h, a in rows:
        out[(code, d, h, a)] = E.probabilities_from_xg(lh, la)["over25"]
    return out


def fair2(odds):
    inv = [1.0 / o for o in odds]; s = sum(inv)
    return [x / s for x in inv]


def best2(r):
    a, m = r["avg"], r.get("max")
    if not m: return list(a)
    return [mx if mx <= av * O.MAX_SANE else av for mx, av in zip(m, a)]


def evaluate(pairs):
    n = len(pairs)
    if not n: return {"n": 0}
    ll_m = ll_k = 0.0
    bands = {f"{int(lo*100)}-{int(hi*100)}": [0, 0, 0.0, 0.0] for lo, hi in BANDS}
    pnl, clv, hits, quoted = [], [], [], []
    by_side = {"over": [0, 0, []], "under": [0, 0, []]}
    for p_over, r in pairs:
        y = r["result"]                      # 0 = over, 1 = under
        mp = (p_over, 1 - p_over); mk = fair2(r["avg"])
        ll_m += -math.log(max(mp[y], 1e-12)); ll_k += -math.log(max(mk[y], 1e-12))
        for lo, hi in BANDS:
            if lo <= p_over < hi:
                b = bands[f"{int(lo*100)}-{int(hi*100)}"]; b[0] += 1; b[1] += (y == 0); b[2] += p_over; b[3] += mk[0]
        bp = best2(r)
        side = None
        for i in (0, 1):
            if mp[i] * bp[i] - 1 >= EDGE and (side is None or mp[i] * bp[i] > mp[side] * bp[side]): side = i
        if side is None: continue
        won = (y == side)
        pnl.append((bp[side] - 1) if won else -1.0); hits.append(won); quoted.append(mk[side])
        k = "over" if side == 0 else "under"; by_side[k][0] += 1; by_side[k][1] += won; by_side[k][2].append(pnl[-1])
        if r.get("close"): clv.append(bp[side] * fair2(r["close"])[side] - 1)
    roi, roi_p = O._boot(pnl); clv_mu, clv_p = O._boot(clv)
    return {"n": n, "logLossModel": round(ll_m / n, 4), "logLossMarket": round(ll_k / n, 4),
            "bands": {k: {"n": v[0], "landed": round(v[1] / v[0], 3) if v[0] else None,
                          "model": round(v[2] / v[0], 3) if v[0] else None, "market": round(v[3] / v[0], 3) if v[0] else None}
                      for k, v in bands.items()},
            "bets": len(pnl), "hit": round(sum(hits) / len(hits), 3) if hits else None,
            "quoted": round(sum(quoted) / len(quoted), 3) if quoted else None,
            "roi": round(roi, 4), "pRoiNotPositive": round(roi_p, 3),
            "clvBets": len(clv), "clv": round(clv_mu, 4), "pClvNotPositive": round(clv_p, 3),
            "bySide": {k: {"bets": v[0], "won": v[1], "roi": round(sum(v[2]) / len(v[2]), 4) if v[2] else None} for k, v in by_side.items()}}


def main():
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "goals-value.json")
    log = []
    data = tune.load(None)
    report = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "market": "over/under 2.5",
              "source": "football-data.co.uk", "edge": EDGE, "seasons": {}}
    for split in ("fit", "check"):
        preds = model_over(tune.lambdas(data, split, meta=True))
        prices, season = [], None
        for div, code in O.DIVS.items():
            if code not in E.LEAGUES: continue
            s = tune.splits(code)[split][0]
            if "-" not in s: continue
            season = season or s
            prices += parse_goals(O._get(O.HIST_URL.format(yy=O._yy(s), div=div), log=log))
            time.sleep(1.0)
        prices = [r for r in prices if r["result"] is not None]
        fixtures = [((c, d, h, a), c, d, h, a) for (c, d, h, a) in preds]
        joined = O.match(prices, fixtures)
        pairs = [(preds[k], r) for k, r in joined.items()]
        res = evaluate(pairs); res["season"] = season; res["pricedMatches"] = len(prices)
        report["seasons"][split] = res
        print(f"{split} {season}: matched {res.get('n')} of {len(prices)} priced; log loss model {res.get('logLossModel')} v market {res.get('logLossMarket')}; "
              f"bets {res.get('bets')} hit {res.get('hit')} v quoted {res.get('quoted')} roi {res.get('roi')} (p not +ve {res.get('pRoiNotPositive')}) "
              f"clv {res.get('clv')} on {res.get('clvBets')} (p not +ve {res.get('pClvNotPositive')})")
        for k, v in res.get("bands", {}).items():
            if v["n"]: print(f"   over {k}%: n {v['n']} landed {v['landed']} model {v['model']} market {v['market']}")
        print("   by side:", res.get("bySide"))
    fit, chk = report["seasons"].get("fit", {}), report["seasons"].get("check", {})
    def beats(s): return s.get("clvBets", 0) >= O.MIN_BETS and s.get("clv", 0) > 0 and s.get("pClvNotPositive", 1) <= O.MAX_P_WORSE
    report["valueGate"] = bool(beats(fit) and beats(chk))
    report["verdict"] = ("The model's over/under picks beat the closing price on both seasons." if report["valueGate"] else
                         "No proven value on the goals market: the picks do not beat the closing price on both seasons.")
    report["log"] = log[-20:]
    with open(out_path, "w") as f: json.dump(report, f, indent=1)
    print(report["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
