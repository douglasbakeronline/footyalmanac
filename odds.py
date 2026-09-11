#!/usr/bin/env python3
"""
Bookmaker prices, and the test of whether the model can find value in them.

    python3 odds.py --report          run the backtest, print it, write the report
    python3 odds.py --live            fetch this week's prices and show the matches

Where the prices come from
--------------------------
football-data.co.uk, free, no key. Two kinds of file:

  fixtures.csv       the next round in 22 divisions (England down to the
                     National League, Scotland, the big five and their second
                     tiers, Netherlands, Belgium, Portugal, Turkey, Greece).
                     Collected Friday afternoon for the weekend, Tuesday
                     lunchtime for midweek. So the prices shown are a snapshot,
                     not live: they will have moved by kick-off.
  mmz4281/<yy>/<div>.csv
                     every past match of a season with its result, the same
                     prices, and the closing prices. This is what the test
                     below is built on.

What "value" means here, and why it is gated
--------------------------------------------
A price is value if the model thinks the outcome is likelier than the price
implies: model probability x best price > 1. That test is only worth anything
if the model is actually better than the market somewhere. Most models are not,
and one that is badly calibrated finds "value" exactly where it is wrong: this
model is under-confident about big favourites, so an ungated value finder would
mostly point at the underdogs in those games.

So value is never shown on trust. backtest() replays the last completed season
and the current one: the model's morning-of prediction against the prices on
the file for the same matches. It measures three things:

  1. Log loss, model against market. Who prices matches better overall.
  2. Closing line value on the bets the model would have made: did the price
     taken beat the closing price? The least noisy evidence of an edge there
     is, because it does not wait for results to wash out luck.
  3. Profit on the same bets at the best price, flat stakes.

Value flags appear on the site only when the report says the model beats the
closing line on both seasons. Otherwise the site shows the market's number and
the best price beside the model's, and nothing more. The report lives in
current/odds-report.json, is refreshed weekly by the daily build, and is
committed with the rest of current/.

Standard library only.
"""
import csv, io, json, math, os, random, sys, time, urllib.request
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "current", "odds-report.json")
BASE = "https://www.football-data.co.uk"
LIVE_URL = BASE + "/fixtures.csv"
HIST_URL = BASE + "/mmz4281/{yy}/{div}.csv"
REFRESH_DAYS = 7

# football-data division -> this project's competition code
DIVS = {
    "E0": "en.1", "E1": "en.2", "E2": "en.3", "E3": "en.4", "EC": "en.5",
    "SC0": "sco.1", "SC1": "sco.2",
    "D1": "de.1", "D2": "de.2", "I1": "it.1", "I2": "it.2",
    "SP1": "es.1", "SP2": "es.2", "F1": "fr.1", "F2": "fr.2",
    "N1": "nl.1", "B1": "be.1", "P1": "pt.1", "T1": "tr.1", "G1": "gr.1",
}

# A "best price" more than this far above the market average is a stale or
# mistyped line, not a price anyone could have taken.
MAX_SANE = 1.25

# The value gate. A bet is a model pick of Lean or better (>= 55%) whose best
# price beats the model's own fair price by EDGE.
EDGE = 0.05
PICK_MIN = 0.55
MIN_BETS = 60          # fewer bets than this in a season proves nothing
MAX_P_WORSE = 0.10     # closing line value must be positive with this confidence

# football-data's own abbreviations that the club matcher cannot see through.
# Everything else is handled by sources._norm plus the similarity test below.
ALIASES = {
    "Ein Frankfurt": "Eintracht Frankfurt", "M'gladbach": "Monchengladbach",
    "Sp Lisbon": "Sporting CP", "Sp Braga": "Braga", "Sp Gijon": "Sporting Gijon",
    "Ath Madrid": "Atletico Madrid", "Ath Bilbao": "Athletic Bilbao",
    "Sociedad": "Real Sociedad", "Vallecano": "Rayo Vallecano",
    "Espanol": "Espanyol", "La Coruna": "Deportivo La Coruna",
    "Santander": "Racing Santander", "Queen of Sth": "Queen of the South",
    "Inverness C": "Inverness Caledonian Thistle", "Bristol Rvs": "Bristol Rovers",
    "Raith Rvs": "Raith Rovers", "Sheffield Weds": "Sheffield Wednesday",
    "Peterboro": "Peterborough", "For Sittard": "Fortuna Sittard",
    "Buyuksehyr": "Basaksehir", "Goztep": "Goztepe", "St. Gilloise": "Union Saint-Gilloise",
    "Nijmegen": "NEC", "Den Haag": "ADO Den Haag", "St Etienne": "Saint-Etienne",
    "QPR": "Queens Park Rangers", "Wolves": "Wolverhampton",
}


# ---------------------------------------------------------------------------
# fetching and parsing
# ---------------------------------------------------------------------------

def _get(url, tries=3, log=None):
    """The file as text, or None. Backs off politely on a rate limit."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "football-almanac/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8-sig", errors="replace")
        except Exception as e:
            if log is not None:
                log.append(f"{url}: {e}")
            time.sleep(2 + 4 * i)
    return None


def _num(r, key):
    try:
        v = float(r.get(key) or "")
        return v if v > 1.0 else None
    except ValueError:
        return None


def _triple(r, keys):
    t = [_num(r, k) for k in keys]
    return t if all(t) else None


def _date(s):
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s.strip(), fmt).date().isoformat()
        except (ValueError, AttributeError):
            pass
    return None


def parse(text):
    """Rows of a football-data file: one dict per match with prices."""
    out = []
    if not text:
        return out
    for r in csv.DictReader(io.StringIO(text.lstrip("\ufeff"))):
        code = DIVS.get((r.get("Div") or "").strip())
        d = _date(r.get("Date") or "")
        home = (r.get("HomeTeam") or r.get("Home") or "").strip()
        away = (r.get("AwayTeam") or r.get("Away") or "").strip()
        if not code or not d or not home or not away:
            continue
        avg = _triple(r, ("AvgH", "AvgD", "AvgA"))
        if not avg:
            continue
        ftr = (r.get("FTR") or "").strip()
        out.append({
            "code": code, "date": d, "time": (r.get("Time") or "").strip() or None,
            "home": home, "away": away,
            "avg": avg,
            "max": _triple(r, ("MaxH", "MaxD", "MaxA")),
            "close": (_triple(r, ("PSCH", "PSCD", "PSCA"))
                      or _triple(r, ("AvgCH", "AvgCD", "AvgCA"))),
            "result": {"H": 0, "D": 1, "A": 2}.get(ftr),
        })
    return out


def fair(odds):
    """Market probabilities with the bookmaker's margin taken out."""
    inv = [1.0 / o for o in odds]
    s = sum(inv)
    return [x / s for x in inv]


def best(row):
    """The best price per outcome that is plausibly real."""
    a, m = row["avg"], row.get("max")
    if not m:
        return list(a)
    return [mx if mx <= av * MAX_SANE else av for mx, av in zip(m, a)]


# ---------------------------------------------------------------------------
# matching a price to a fixture
# ---------------------------------------------------------------------------

def _tokens(name):
    return S._norm(ALIASES.get(name, name)).split()


def name_sim(a, b):
    """0..1. Token prefixes carry most of it, because football-data shortens
    words ("Nott'm", "Weds", "Sp") rather than rewording them."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    hit = 0
    for t in short:
        for u in long_:
            n = 0
            while n < min(len(t), len(u)) and t[n] == u[n]:
                n += 1
            if n >= min(4, len(t), len(u)):
                hit += 1
                break
    tok = hit / len(short)
    return max(tok, SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio())


def match(price_rows, fixtures):
    """{fixture key: price row}. A price is only attached when exactly one of
    the fixtures in that competition on that day (a day either side, for
    time zones) is clearly the same match. A price that fits two fixtures, or
    none well, is dropped: a missing price costs nothing, a wrong one misleads.

    fixtures: iterable of (key, code, date, home, away).
    """
    idx = {}
    for key, code, d, h, a in fixtures:
        idx.setdefault((code, d), []).append((key, h, a))
    out, used = {}, set()
    for r in price_rows:
        d0 = date.fromisoformat(r["date"])
        cands = []
        for off in (0, -1, 1):
            cands = idx.get((r["code"], (d0 + timedelta(days=off)).isoformat()), [])
            if cands:
                break
        scored = []
        for key, h, a in cands:
            sh, sa = name_sim(r["home"], h), name_sim(r["away"], a)
            if min(sh, sa) >= 0.5:
                scored.append((sh + sa, key))
        scored.sort(reverse=True)
        if not scored:
            continue
        if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.25:
            continue
        key = scored[0][1]
        if key in used:
            continue
        used.add(key)
        out[key] = r
    return out


def market_block(r, model_p=None):
    """What the page shows for one fixture."""
    fp = fair(r["avg"])
    b = best(r)
    blk = {"p": [round(x, 4) for x in fp], "best": [round(x, 2) for x in b],
           "avg": [round(x, 2) for x in r["avg"]]}
    if model_p:
        blk["ev"] = [round(mp * bp - 1, 4) for mp, bp in zip(model_p, b)]
    return blk


def fetch_live(log=None):
    return parse(_get(LIVE_URL, log=log))


# ---------------------------------------------------------------------------
# the backtest
# ---------------------------------------------------------------------------

def _yy(season):
    """'2025-26' -> '2526'."""
    return season[2:4] + season[5:7]


def _boot(xs, reps=1500, seed=11):
    """Mean, and the bootstrap probability that the true mean is <= 0."""
    if not xs:
        return 0.0, 1.0
    rng = random.Random(seed)
    n = len(xs)
    mu = sum(xs) / n
    worse = sum(1 for _ in range(reps)
                if sum(xs[rng.randrange(n)] for _ in range(n)) / n <= 0)
    return mu, worse / reps


def evaluate(pairs):
    """pairs: [(model probabilities, price row)] for matches with a result."""
    n = len(pairs)
    if not n:
        return {"n": 0}
    ll_model = ll_mkt = 0.0
    clv, pnl = [], []
    for mp, r in pairs:
        y = r["result"]
        ll_model += -math.log(max(mp[y], 1e-12))
        ll_mkt += -math.log(max(fair(r["avg"])[y], 1e-12))
        pick = max(range(3), key=lambda i: mp[i])
        if mp[pick] < PICK_MIN:
            continue
        price = best(r)[pick]
        if mp[pick] * price - 1 < EDGE:
            continue
        pnl.append((price - 1) if y == pick else -1.0)
        if r.get("close"):
            clv.append(price * fair(r["close"])[pick] - 1)
    clv_mu, clv_p = _boot(clv)
    roi_mu, roi_p = _boot(pnl)
    return {
        "n": n,
        "logLossModel": round(ll_model / n, 4), "logLossMarket": round(ll_mkt / n, 4),
        "bets": len(pnl), "roi": round(roi_mu, 4), "pRoiNotPositive": round(roi_p, 3),
        "clvBets": len(clv), "clv": round(clv_mu, 4), "pClvNotPositive": round(clv_p, 3),
    }


def model_probs(rows):
    """tune.lambdas meta rows -> {(code, date, home, away): (h, d, a)} with the
    live calibration applied, exactly as the site would have quoted it."""
    import tune
    cal = None
    path = os.path.join(HERE, "calibration.json")
    if os.path.exists(path):
        try:
            cal = json.load(open(path))
        except Exception:
            cal = None
    out = {}
    for lh, la, y, code, d, h, a in rows:
        p = tune.outcome(lh, la, E.RHO)
        t = tune.curve_T(max(p), cal) if cal else E.TEMPERATURE
        if t != 1.0:
            q = [max(x, 1e-12) ** (1.0 / t) for x in p]
            s = sum(q)
            p = tuple(x / s for x in q)
        out[(code, d, h, a)] = p
    return out


def backtest(cache=None, log=None):
    """The report dict. Network-heavy: ~40 small files plus openfootball."""
    import tune
    data = tune.load(cache)
    report = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "source": "football-data.co.uk", "edge": EDGE, "pickMin": PICK_MIN,
              "seasons": {}}
    for split in ("fit", "check"):
        preds = model_probs(tune.lambdas(data, split, meta=True))
        season = None
        for code in DIVS.values():
            if code in E.LEAGUES:
                season = tune.splits(code)[split][0]
                break
        prices = []
        for div, code in DIVS.items():
            if code not in E.LEAGUES:
                continue
            s = tune.splits(code)[split][0]
            if "-" not in s:
                continue
            prices += parse(_get(HIST_URL.format(yy=_yy(s), div=div), log=log))
            time.sleep(1.0)          # one file a second; the site is free
        prices = [r for r in prices if r["result"] is not None]
        fixtures = [((c, d, h, a), c, d, h, a) for (c, d, h, a) in preds]
        joined = match(prices, fixtures)
        pairs = [(preds[k], r) for k, r in joined.items()]
        res = evaluate(pairs)
        res["season"] = season
        res["pricedMatches"] = len(prices)
        report["seasons"][split] = res

    fit, chk = report["seasons"].get("fit", {}), report["seasons"].get("check", {})

    def beats(s):
        return (s.get("clvBets", 0) >= MIN_BETS and s.get("clv", 0) > 0
                and s.get("pClvNotPositive", 1) <= MAX_P_WORSE)

    report["valueGate"] = bool(beats(fit) and beats(chk))
    if report["valueGate"]:
        report["verdict"] = ("The model's value picks beat the closing price on both "
                             "seasons. Value is flagged on the site.")
    elif fit.get("n") and fit.get("logLossModel", 9) > fit.get("logLossMarket", 0):
        report["verdict"] = ("The bookmakers price matches better than the model, and "
                             "its value picks have not beaten the closing price. No value "
                             "is flagged; the market's number is shown beside the model's.")
    else:
        report["verdict"] = ("Not enough evidence that the model's value picks beat the "
                             "closing price. No value is flagged.")
    return report


def load_report():
    try:
        return json.load(open(REPORT))
    except Exception:
        return None


def report_is_stale(rep):
    if not rep or "generated" not in rep:
        return True
    try:
        g = datetime.fromisoformat(rep["generated"])
    except ValueError:
        return True
    if g.tzinfo is None:
        g = g.replace(tzinfo=timezone.utc)
    # a failed run is retried the next day rather than on every build
    days = 1 if rep.get("failed") else REFRESH_DAYS
    return datetime.now(timezone.utc) - g > timedelta(days=days)


def refresh_report(cache=None, log=None):
    """Rerun the backtest if the report is missing or a week old. Never raises:
    a failed refresh keeps the last good report, and no report means no value
    flags, which is the safe way round."""
    rep = load_report()
    if not report_is_stale(rep):
        return rep
    try:
        new = backtest(cache, log=log)
        if new["seasons"].get("fit", {}).get("n"):
            os.makedirs(os.path.dirname(REPORT), exist_ok=True)
            json.dump(new, open(REPORT, "w"), indent=1)
            return new
        why = "no historical prices could be matched"
    except Exception as e:
        why = str(e)
    if log is not None:
        log.append(f"odds backtest did not complete: {why}")
    if rep and not rep.get("failed"):
        return rep                 # keep the last good report
    try:
        os.makedirs(os.path.dirname(REPORT), exist_ok=True)
        json.dump({"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "failed": True, "reason": why, "valueGate": False, "verdict": None},
                  open(REPORT, "w"), indent=1)
    except Exception:
        pass
    return None


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    if a.live:
        rows = fetch_live()
        print(f"{len(rows)} priced fixtures")
        for r in rows[:20]:
            print(r["code"], r["date"], r["home"], "v", r["away"], r["avg"], best(r))
    else:
        errs = []
        rep = backtest(log=errs)
        print(json.dumps(rep, indent=1))
        os.makedirs(os.path.dirname(REPORT), exist_ok=True)
        json.dump(rep, open(REPORT, "w"), indent=1)
        for e in errs[:10]:
            print("  ", e, file=sys.stderr)
