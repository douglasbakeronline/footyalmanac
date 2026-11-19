"""Horse racing: UK and Irish racecards, a chance for every runner, a short
list of tips, and a public record (19 Nov 2026, on trial).

Douglas, 19 Nov 2026, after testers asked for horse racing: "we just want to
surface like what we believe is going to be accurate for that day, or the most
accurate", "I'm happy to have it marked as trial somewhere, but I want it
published", "I lean to your suggestion" (UK and Ireland first, UK bookies).
The mock-ups he signed off are on the "Horse Racing tab mockups" canvas;
claude/horse-racing-2026-11-19.md is the note.

How a runner's chance is made (Benter 1994, "Computer based horse race
handicapping and wagering systems"; Bolton and Chapman 1986):

  1. A fundamental score from the racecard alone (FACTORS): official rating
     against the field, recent finishing positions, the trainer's last 14 days,
     time since the last run. Softmax within the race, so every race sums to 1.
  2. The second stage: the fundamental chance combined with the bookmakers'
     fair chance (the average price, margin removed), p ~ fund^ALPHA * mkt^BETA,
     renormalised. The market is the stronger forecaster; the model only moves
     a horse where it has a reason to. ALPHA and BETA are starter values, not
     fitted: they are refitted by hand once FIT_MIN graded races exist, and the
     record says so (Rule 1: nothing is ever fitted on the record itself; the
     fit uses the logged runners, checked on later days).

A tip is one horse in a race where the chance is clear AND the best UK price
pays more than it (TIP_*). Accuracy first: the day's tips are ranked by
chance, never by price, and capped (MAX_TIPS). Most races get no tip.

The racing feed is The Racing API (https://www.theracingapi.com, HTTP basic
auth, secrets RACING_API_USERNAME / RACING_API_PASSWORD). Without them this
writes an empty, honest racing.js and exits 0. `--probe` prints the first
racecard's keys so the field names in `race_of` / `runner_of` can be checked
against the live feed on the first build with keys.

Writes predictions-racing/<date>.json (each race frozen at its off time),
racing-record.json (graded, never trimmed) and racing.js (the page).
Standard library only.
"""
import argparse
import base64
import datetime as dt
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")
API = "https://api.theracingapi.com/v1"
REGIONS = ("gb", "ire")            # UK and Irish racing (Douglas, 19 Nov 2026)
TRIAL = True                       # the page says Trial until this is False

ARCHIVE = "predictions-racing"
RECORD = "racing-record.json"
PAGE = "racing.js"

RULE = 1                           # bump when the model, the tip rule or grading changes

# The fundamental model: weights on within-race z-scores. Starter values.
FACTORS = {"rating": 0.55, "form": 0.45, "trainer": 0.15, "fresh": 0.10}
ALPHA, BETA = 0.30, 0.85           # second stage: fundamental ^ ALPHA x market ^ BETA
FIT_MIN = 500                      # graded races before ALPHA / BETA are refitted

# A tip (accuracy first, value second)
TIP_MIN_CHANCE = 0.22              # the horse's chance after the second stage
TIP_MIN_EDGE = 0.08                # best UK price x chance - 1
TAKE_EDGE = 0.04                   # "take at": the lowest price still worth it
TIP_MAX_FIELD = 16                 # no big-field handicaps
TIP_MIN_RUNS = 2                   # the horse needs at least two runs of form
EW_MIN_PRICE = 4.0                 # each-way only at 3/1 or longer
EW_MIN_PLACE = 0.45                # and a good chance of placing
MAX_TIPS = 6                       # a day, most likely first

TIERS = ((0.50, 3, "Strong"), (0.33, 2, "Firm"), (0.22, 1, "Lean"))


# ---------- the feed ----------

def _auth():
    u, p = os.environ.get("RACING_API_USERNAME"), os.environ.get("RACING_API_PASSWORD")
    if not u or not p:
        return None
    return "Basic " + base64.b64encode(f"{u}:{p}".encode()).decode()


# The region filter's name on each endpoint, as the published docs give it; a
# 422 drops the filter and the regions are kept locally instead (`fetch_region`).
CARD_REGION_PARAM = "region_codes"
RESULT_REGION_PARAM = "region"
RESULT_PAGE = 50


# Racecard endpoints by plan, richest first: a plan refused one (401 / 403)
# falls back to the next, and the build log says which answered.
CARD_PATHS = ("racecards/standard", "racecards/basic", "racecards/free")


GAP_S = 1.2                        # the free plan allows one request a second
_last_call = [0.0]
_card_path = [None]                # the racecard endpoint the plan allows, once found


def fetch(path, params=None, auth=None):
    """One GET against The Racing API. Repeated keys (region) are allowed.
    An HTTP error carries the API's own message into the build log."""
    wait = GAP_S - (time.monotonic() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.monotonic()
    q = urllib.parse.urlencode(params or [], doseq=True)
    req = urllib.request.Request(f"{API}/{path}" + (f"?{q}" if q else ""),
                                 headers={"Authorization": auth, "User-Agent": "sportsalmanac"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            body = ""
        print(f"racing: {path} answered {e.code}: {body}")
        raise


def fetch_cards(params, auth):
    """Racecards from the richest endpoint the plan allows."""
    last = None
    paths = (_card_path[0],) if _card_path[0] else CARD_PATHS
    for path in paths:
        try:
            payload = fetch_region(path, params, CARD_REGION_PARAM, auth)
            if _card_path[0] != path:
                print(f"racing: racecards from {path}")
            _card_path[0] = path
            return payload
        except urllib.error.HTTPError as e:
            if e.code not in (401, 403):
                raise
            last = e
    raise last


def fetch_region(path, params, key, auth):
    """GET with the region filter; if the feed refuses it (422), without."""
    try:
        return fetch(path, params + [(key, r) for r in REGIONS], auth)
    except urllib.error.HTTPError as e:
        if e.code != 422:
            raise
        print(f"racing: {path} refused '{key}', fetching every region and keeping {REGIONS}")
        return fetch(path, params, auth)


def in_regions(raw):
    reg = str(_first(raw, "region") or "").lower()
    return not reg or reg in REGIONS


# ---------- reading a racecard ----------

def _num(x):
    try:
        if x in (None, "", "-"):
            return None
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def _first(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return None


def form_runs(form):
    """Finishing positions from a form string, oldest first: '3P-142' -> [3, 'P', 1, 4, 2].
    A '-' or '/' separates seasons; digits 0 means 10th or worse."""
    out = []
    for ch in str(form or ""):
        if ch.isdigit():
            out.append(10 if ch == "0" else int(ch))
        elif ch.upper() in "PFURB":
            out.append(ch.upper())
    return out


def form_score(form):
    """Recent form, 0-1: the last three runs, most recent heaviest."""
    runs = form_runs(form)[-3:]
    if not runs:
        return None
    val = {1: 1.0, 2: 0.72, 3: 0.55, 4: 0.42, 5: 0.32, 6: 0.24}
    w = [0.2, 0.3, 0.5][-len(runs):]
    s = sum(wi * (val.get(r, 0.12) if isinstance(r, int) else 0.0) for wi, r in zip(w, runs))
    return s / sum(w)


def ew_terms(field, handicap):
    """UK standard each-way terms by runners: (places, fraction)."""
    if field <= 4:
        return 1, 1.0
    if field <= 7:
        return 2, 0.25
    if handicap and field >= 16:
        return 4, 0.25
    if handicap and field >= 12:
        return 3, 0.25
    return 3, 0.2


def runner_of(r):
    odds = []
    for o in r.get("odds") or []:
        d = _num(_first(o, "decimal", "dec"))
        if d and d > 1.0:
            odds.append({"book": _first(o, "bookmaker", "book") or "", "dec": d})
    t14 = r.get("trainer_14_days") or {}
    status = str(_first(r, "status", "non_runner") or "").lower()
    return {
        "id": str(_first(r, "horse_id", "id") or _first(r, "horse") or ""),
        "horse": re.sub(r"\s*\((?:GB|IRE|FR|USA|GER)\)\s*$", "", str(_first(r, "horse", "name") or "")),
        "no": _first(r, "number", "cloth", "no"),
        "draw": _first(r, "draw"),
        "age": _first(r, "age"),
        "lbs": _num(_first(r, "lbs", "weight_lbs")),
        "or": _num(_first(r, "ofr", "or", "official_rating")),
        "form": str(_first(r, "form") or ""),
        "lastRun": _num(_first(r, "last_run", "days_since_run")),
        "jockey": str(_first(r, "jockey") or ""),
        "trainer": str(_first(r, "trainer") or ""),
        "t14": _num(_first(t14, "percent", "win_percent")),
        "gear": str(_first(r, "headgear") or ""),
        "odds": odds,
        "nr": status in ("nr", "non_runner", "true", "1", "withdrawn"),
    }


def race_of(raw):
    runners = [runner_of(r) for r in raw.get("runners") or []]
    off = _first(raw, "off_dt", "off_datetime")
    try:
        when = dt.datetime.fromisoformat(str(off).replace("Z", "+00:00")).astimezone(UK)
    except ValueError:
        when = None
    name = str(_first(raw, "race_name", "title") or "")
    handicap = "handicap" in name.lower() or bool(_first(raw, "rating_band"))
    live = [r for r in runners if not r["nr"]]
    places, frac = ew_terms(len(live), handicap)
    return {
        "id": str(_first(raw, "race_id", "id") or ""),
        "course": str(_first(raw, "course") or ""),
        "region": str(_first(raw, "region") or "").upper(),
        "date": when.date().isoformat() if when else str(_first(raw, "date") or ""),
        "off": when.strftime("%H:%M") if when else str(_first(raw, "off_time") or ""),
        "when": when.isoformat() if when else None,
        "name": name,
        "type": str(_first(raw, "type", "race_type") or ""),
        "cls": str(_first(raw, "race_class", "class") or ""),
        "dist": str(_first(raw, "distance", "dist") or ""),
        "going": str(_first(raw, "going") or "").title(),
        "surface": str(_first(raw, "surface") or ""),
        "handicap": handicap,
        "field": len(live),
        "places": places,
        "frac": frac,
        "runners": runners,
    }


# ---------- the model ----------

def _z(vals):
    xs = [v for v in vals if v is not None]
    if len(xs) < 2:
        return [0.0] * len(vals)
    m = sum(xs) / len(xs)
    sd = (sum((v - m) ** 2 for v in xs) / len(xs)) ** 0.5 or 1.0
    # missing values sit half a standard deviation under the field
    return [((v - m) / sd) if v is not None else -0.5 for v in vals]


def fresh_score(days):
    """Time since the last run: 2-6 weeks is best; a long break or a debut costs."""
    if days is None:
        return None
    if days < 7:
        return 0.6
    if days <= 45:
        return 1.0
    if days <= 90:
        return 0.75
    if days <= 180:
        return 0.5
    return 0.3


def softmax(xs):
    m = max(xs)
    e = [math.exp(x - m) for x in xs]
    s = sum(e)
    return [v / s for v in e]


def market_fair(runner):
    """The bookmakers' average price as a raw chance (margin removed later)."""
    ds = [o["dec"] for o in runner["odds"]]
    if not ds:
        return None
    return 1.0 / (sum(ds) / len(ds))


def best_price(runner):
    ds = [(o["dec"], o["book"]) for o in runner["odds"]]
    return max(ds) if ds else (None, None)


def chances(race):
    """Every non-runner-free runner's chance: fundamental, market and combined.
    Each set sums to 1 within the race."""
    live = [r for r in race["runners"] if not r["nr"]]
    if not live:
        return []
    z = {k: _z(v) for k, v in {
        "rating": [r["or"] for r in live],
        "form": [form_score(r["form"]) for r in live],
        "trainer": [r["t14"] for r in live],
        "fresh": [fresh_score(r["lastRun"]) for r in live],
    }.items()}
    score = [sum(FACTORS[k] * z[k][i] for k in FACTORS) for i in range(len(live))]
    fund = softmax(score)
    raw = [market_fair(r) for r in live]
    have = all(v is not None for v in raw)
    if have:
        s = sum(raw)
        mkt = [v / s for v in raw]
        comb = [f ** ALPHA * m ** BETA for f, m in zip(fund, mkt)]
        s = sum(comb)
        comb = [c / s for c in comb]
    else:
        mkt, comb = [None] * len(live), fund
    return [{"runner": r, "fund": f, "mkt": m, "p": p} for r, f, m, p in zip(live, fund, mkt, comb)]


def place_chance(ps, i, places):
    """Chance runner i finishes in the first `places` (Harville, exact up to 3, 4 approximated)."""
    n = len(ps)
    if places >= n:
        return 1.0
    pi = ps[i]
    total = pi
    if places >= 2:
        for j in range(n):
            if j == i:
                continue
            total += ps[j] * pi / (1 - ps[j])
    if places >= 3:
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) < 3:
                    continue
                total += ps[j] * ps[k] / (1 - ps[j]) * pi / (1 - ps[j] - ps[k])
    if places >= 4:
        # the fourth place, approximated: the remaining chance spread by win share
        rest = 1 - total
        total += rest * min(1.0, pi * (n - 3) / max(1e-9, 1 - pi)) / max(1, n - 3)
    return min(1.0, total)


def tier_of(p):
    for floor, k, name in TIERS:
        if p >= floor:
            return k, name
    return 0, "No read"


def read_race(race):
    """The race as the page shows it: runners by chance, the top pick, its danger, a tip or not."""
    rows = chances(race)
    rows.sort(key=lambda x: -x["p"])
    ps = [x["p"] for x in rows]
    out = []
    for i, x in enumerate(rows):
        r = x["runner"]
        price, book = best_price(r)
        out.append({**{k: r[k] for k in ("id", "horse", "no", "draw", "age", "lbs", "or", "form",
                                          "lastRun", "jockey", "trainer", "t14", "gear")},
                    "p": round(x["p"], 4), "fund": round(x["fund"], 4),
                    "mkt": round(x["mkt"], 4) if x["mkt"] is not None else None,
                    "place": round(place_chance(ps, i, race["places"]), 4),
                    "price": price, "book": book})
    nrs = [{"horse": r["horse"], "no": r["no"]} for r in race["runners"] if r["nr"]]
    tip = tip_for(race, out)
    k, name = tier_of(out[0]["p"]) if out else (0, "No read")
    return {**{k2: race[k2] for k2 in ("id", "course", "region", "date", "off", "when", "name", "type",
                                        "cls", "dist", "going", "surface", "handicap", "field",
                                        "places", "frac")},
            "tier": k, "tierName": name, "runners": out, "nonRunners": nrs, "tip": tip,
            "skip": None if tip else skip_reason(race, out)}


def tip_for(race, rows):
    if not rows or race["field"] > TIP_MAX_FIELD or race["field"] < 3:
        return None
    top = rows[0]
    if top["price"] is None or top["mkt"] is None:
        return None
    if len(form_runs(top["form"])) < TIP_MIN_RUNS:
        return None
    p, price = top["p"], top["price"]
    edge = p * price - 1
    if p < TIP_MIN_CHANCE or edge < TIP_MIN_EDGE:
        return None
    ew = (p < 0.33 and price >= EW_MIN_PRICE and top["place"] >= EW_MIN_PLACE and race["places"] >= 2)
    danger = rows[1] if len(rows) > 1 else None
    return {"horse": top["horse"], "id": top["id"], "bet": "each-way" if ew else "win",
            "p": p, "place": top["place"], "price": price, "book": top["book"],
            "take": round((1 + TAKE_EDGE) / p, 2), "edge": round(edge, 3),
            "fair": round(1 / p, 2),
            "danger": {"horse": danger["horse"], "price": danger["price"], "p": danger["p"]} if danger else None}


def skip_reason(race, rows):
    if not rows:
        return "no runners"
    if race["field"] > TIP_MAX_FIELD:
        return f"{race['field']} runners: too big a field to call"
    top = rows[0]
    if top["price"] is None:
        return "no bookmaker price yet"
    if len(form_runs(top["form"])) < TIP_MIN_RUNS:
        return "the top-rated horse has too little form"
    if top["p"] < TIP_MIN_CHANCE:
        return f"no horse clear of the field (top rated {round(top['p'] * 100)}%)"
    return f"priced about right ({top['price']:.2f} v a fair {1 / top['p']:.2f})"


def day_tips(races):
    """The day's tips, most likely first, capped: accuracy before volume."""
    tips = [(r, r["tip"]) for r in races if r["tip"]]
    tips.sort(key=lambda x: -x[1]["p"])
    keep = {r["id"] for r, _ in tips[:MAX_TIPS]}
    for r in races:
        if r["tip"] and r["id"] not in keep:
            r["skip"] = "a stronger tip took the day's place"
            r["tip"] = None
    return [r for r, _ in tips[:MAX_TIPS]]


# ---------- grading ----------

def finish_of(pos):
    try:
        return int(str(pos).strip())
    except ValueError:
        return None


def settle(tip, finish, places, frac, nr=False):
    """Profit to a one-point stake (each-way: half a point each way). None = void."""
    if nr:
        return None
    price = tip["price"]
    won = finish == 1
    placed = finish is not None and finish <= places
    if tip["bet"] == "win":
        return round(price - 1, 3) if won else -1.0
    win_part = 0.5 * (price - 1) if won else -0.5
    place_part = 0.5 * (price - 1) * frac if placed else -0.5
    return round(win_part + place_part, 3)


def result_of(raw):
    rid = str(_first(raw, "race_id", "id") or "")
    finish = {}
    sp = {}
    for r in raw.get("runners") or []:
        hid = str(_first(r, "horse_id", "id") or "")
        finish[hid] = finish_of(_first(r, "position", "pos"))
        sp[hid] = _num(_first(r, "sp_dec", "sp_decimal"))
        bsp = _num(_first(r, "bsp"))
        if bsp:
            sp[hid] = bsp
    return rid, finish, sp


def grade(archive_days, results):
    """Every archived race with a result: runner rows for calibration, tips settled."""
    runners, tips = [], []
    for day, races in sorted(archive_days.items()):
        for race in races:
            res = results.get(race["id"])
            if not res:
                continue
            finish, sp = res
            nr_ids = {str(x.get("id") or "") for x in race.get("nonRunners") or []}
            for r in race["runners"]:
                f = finish.get(r["id"])
                if r["id"] not in finish:
                    continue            # did not run: no row
                runners.append({"date": day, "race": race["id"], "p": r["p"], "won": f == 1,
                                "placed": f is not None and f <= race["places"], "going": race["going"],
                                "field": race["field"], "handicap": race["handicap"],
                                "lastRun": r["lastRun"], "t14": r["t14"]})
            t = race.get("tip")
            if t:
                f = finish.get(t["id"])
                nr = t["id"] not in finish or t["id"] in nr_ids
                pnl = settle(t, f, race["places"], race["frac"], nr=nr)
                close = sp.get(t["id"])
                tips.append({"date": day, "race": race["id"], "off": race["off"], "course": race["course"],
                             "horse": t["horse"], "bet": t["bet"], "p": t["p"], "price": t["price"],
                             "finish": f, "state": "void" if pnl is None else
                             ("won" if f == 1 else "placed" if (f is not None and f <= race["places"]) else "lost"),
                             "pnl": pnl, "close": close,
                             "beatClose": (t["price"] > close) if (close and pnl is not None) else None})
    return runners, tips


def summarise(runners, tips):
    bands = []
    for lo, hi in ((0, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .5), (.5, 1.01)):
        rows = [r for r in runners if lo <= r["p"] < hi]
        n = len(rows)
        bands.append({"lo": lo, "hi": min(hi, 1.0), "n": n,
                      "expected": round(sum(r["p"] for r in rows), 2),
                      "won": sum(r["won"] for r in rows)})
    conds = {
        "Going: soft or heavy": lambda r: any(w in r["going"].lower() for w in ("soft", "heavy")),
        "Going: good or firmer": lambda r: any(w in r["going"].lower() for w in ("good", "firm")) and "soft" not in r["going"].lower(),
        "All-weather (standard)": lambda r: "standard" in r["going"].lower(),
        "Fields of 12 or more": lambda r: r["field"] >= 12,
        "Handicaps": lambda r: r["handicap"],
        "Non-handicaps": lambda r: not r["handicap"],
        "First run for 120+ days": lambda r: (r["lastRun"] or 0) >= 120,
        "Back within 14 days": lambda r: r["lastRun"] is not None and r["lastRun"] <= 14,
        "Trainer 20%+ in 14 days": lambda r: (r["t14"] or 0) >= 20,
    }
    learn = []
    for name, f in conds.items():
        rows = [r for r in runners if f(r)]
        exp = sum(r["p"] for r in rows)
        won = sum(r["won"] for r in rows)
        sd = sum(r["p"] * (1 - r["p"]) for r in rows) ** 0.5
        learn.append({"name": name, "n": len(rows), "expected": round(exp, 1), "won": won,
                      "z": round((won - exp) / sd, 2) if sd else None})
    settled = [t for t in tips if t["pnl"] is not None]
    run, series = 0.0, []
    for t in settled:
        run += t["pnl"]
        series.append(round(run, 2))
    closes = [t for t in settled if t["beatClose"] is not None]
    by_day = {}
    for t in tips:
        by_day.setdefault(t["date"], []).append({"state": t["state"], "horse": t["horse"]})
    return {
        "rule": RULE, "races": len({r["race"] for r in runners}), "runners": len(runners),
        "tips": len(tips), "settled": len(settled),
        "won": sum(t["state"] == "won" for t in tips), "placed": sum(t["state"] == "placed" for t in tips),
        "profit": round(run, 2), "series": series,
        "beatClose": round(sum(t["beatClose"] for t in closes) / len(closes), 3) if closes else None,
        "beatCloseN": len(closes), "bands": bands, "learn": learn, "byDay": by_day,
        "fitReady": len({r["race"] for r in runners}) >= FIT_MIN,
    }


# ---------- archive and page ----------

def load_archive():
    days = {}
    if os.path.isdir(ARCHIVE):
        for f in sorted(os.listdir(ARCHIVE)):
            m = re.match(r"(\d{4}-\d{2}-\d{2})\.json$", f)
            if m:
                with open(os.path.join(ARCHIVE, f)) as fh:
                    days[m.group(1)] = json.load(fh)["races"]
    return days


def freeze(day, races, now):
    """Write the day's races; a race already off keeps the copy published before it."""
    os.makedirs(ARCHIVE, exist_ok=True)
    path = os.path.join(ARCHIVE, f"{day}.json")
    old = {}
    if os.path.exists(path):
        with open(path) as fh:
            old = {r["id"]: r for r in json.load(fh)["races"]}
    out = []
    for r in races:
        started = r["when"] and dt.datetime.fromisoformat(r["when"]) <= now
        out.append(old[r["id"]] if (started and r["id"] in old) else r)
    for rid, r in old.items():
        if rid not in {x["id"] for x in out}:
            out.append(r)
    out.sort(key=lambda r: r.get("when") or "")
    with open(path, "w") as fh:
        json.dump({"date": day, "rule": RULE, "races": out}, fh, separators=(",", ":"))
    return out


def write_page(status, days, record, note=""):
    payload = {"status": status, "trial": TRIAL, "rule": RULE, "note": note,
               "updated": dt.datetime.now(UK).isoformat(timespec="minutes"),
               "regions": [r.upper() for r in REGIONS], "days": days, "record": record}
    with open(PAGE, "w") as fh:
        fh.write("window.RACING = " + json.dumps(payload, separators=(",", ":")) + ";\n")


def build_day(raw_cards):
    races = [read_race(race_of(c)) for c in raw_cards]
    races = [r for r in races if r["runners"]]
    races.sort(key=lambda r: r.get("when") or "")
    day_tips(races)
    return races


def cards_of(payload):
    return payload.get("racecards") or payload.get("races") or []


def results_of(payload):
    return payload.get("results") or payload.get("races") or []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="print the first racecard's keys and exit")
    ap.add_argument("--sample", help="read racecards from a JSON file instead of the feed (tests, offline)")
    ap.add_argument("--results-sample", help="read results from a JSON file instead of the feed")
    a = ap.parse_args(argv)

    auth = _auth()
    now = dt.datetime.now(UK)
    record_old = {}
    if os.path.exists(RECORD):
        with open(RECORD) as fh:
            record_old = json.load(fh)

    if not auth and not a.sample:
        print("racing: no RACING_API_USERNAME / RACING_API_PASSWORD, writing the waiting page")
        write_page("waiting", {}, record_old.get("summary"),
                   "The racing feed is not connected yet. Tips appear here on the first build with it.")
        return 0

    days = {}
    try:
        if a.sample:
            with open(a.sample) as fh:
                cards = cards_of(json.load(fh))
            by_day = {}
            for c in cards:
                r = race_of(c)
                by_day.setdefault(r["date"], []).append(c)
        else:
            by_day = {}
            for which in ("today", "tomorrow"):
                payload = fetch_cards([("day", which)], auth)
                if a.probe:
                    first = (cards_of(payload) or [{}])[0]
                    print("race keys:", sorted(first.keys()))
                    print("runner keys:", sorted(((first.get("runners") or [{}])[0]).keys()))
                    return 0
                first = (cards_of(payload) or [None])[0]
                if first and not by_day:
                    # every build names the fields the plan sends, so a blank
                    # column on the page can be traced to the feed (19 Nov 2026)
                    print("racing: race keys:", ",".join(sorted(first.keys())))
                    print("racing: runner keys:", ",".join(sorted(((first.get("runners") or [{}])[0]).keys())))
                for c in filter(in_regions, cards_of(payload)):
                    by_day.setdefault(race_of(c)["date"], []).append(c)
        for day, cards in sorted(by_day.items()):
            races = build_day(cards)
            days[day] = freeze(day, races, now)
    except Exception as e:  # a feed failure keeps yesterday's page (Rule 9)
        print(f"::warning::racing feed failed: {e}")
        if os.path.exists(PAGE):
            return 0
        write_page("error", {}, record_old.get("summary"), "The racing feed did not answer this build.")
        return 0

    # grade every archived day up to yesterday that has a result
    archive = load_archive()
    # results kept from earlier builds, so a race is fetched once
    results = {rid: (dict(v[0]), dict(v[1])) for rid, v in (record_old.get("results") or {}).items()}
    try:
        if a.results_sample:
            with open(a.results_sample) as fh:
                raws = results_of(json.load(fh))
        elif auth:
            # the last week only: an abandoned race never gets a result and must
            # not keep the window open forever
            since = (now.date() - dt.timedelta(days=7)).isoformat()
            todo = sorted(d for d, races in archive.items()
                          if since <= d < now.date().isoformat() and any(r["id"] not in results for r in races))
            raws = []
            if todo:
                skip = 0
                while True:
                    page = results_of(fetch_region("results", [("start_date", todo[0]), ("end_date", todo[-1]),
                                                               ("limit", RESULT_PAGE), ("skip", skip)],
                                                   RESULT_REGION_PARAM, auth))
                    raws += [x for x in page if in_regions(x)]
                    if len(page) < RESULT_PAGE or skip > 2000:
                        break
                    skip += RESULT_PAGE
        else:
            raws = []
        for raw in raws:
            rid, finish, sp = result_of(raw)
            results[rid] = (finish, sp)
    except Exception as e:
        print(f"::warning::racing results failed: {e}")

    runners, tips = grade(archive, results)
    summary = summarise(runners, tips)
    record = {"rule": RULE, "summary": summary, "tips": tips, "runners": runners,
              "results": {k: [v[0], v[1]] for k, v in results.items()}}
    if runners or not record_old:
        with open(RECORD, "w") as fh:
            json.dump(record, fh, separators=(",", ":"))
    else:
        summary = record_old.get("summary") or summary

    show = {d: days.get(d) or archive.get(d) for d in sorted(set(days) | set(archive))[-2:]}
    write_page("live", show, summary)
    n = sum(len(v) for v in days.values())
    print(f"racing: {n} races on {len(days)} day(s), {sum(1 for v in days.values() for r in v if r.get('tip'))} tips; "
          f"record {summary['tips']} tips, {summary['runners']} runners graded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
