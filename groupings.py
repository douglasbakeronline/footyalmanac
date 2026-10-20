#!/usr/bin/env python3
"""
Groupings: the Odds tab. Five-leg groups built from the model's picks, each
with a spread of bookmaker prices. Douglas's request, 4 Oct 2026.

    python3 groupings.py            build groupings.json / groupings-data.js from the build's output
    python3 groupings.py --probe    count what the price sources return, write nothing
    python3 groupings.py --grade    regrade the archive only (no price calls)

The record
----------
The first build of each UK day archives that day's groups to
groupings-archive/<date>.json (never overwritten, so the record is of groups
published before their games). Each build grades every archived group from
the site's own graded records (record.json, tennis-record.json,
sports-record.json): a leg is Won, Lost, Void or Pending; a group is Lost as
soon as one leg loses, Won when every leg has won or been voided (a void leg
drops out of the price), Pending otherwise. groupings-record.json holds the
totals, the return per 1 unit staked on every settled group, and each day.

Nothing here feeds back into any model. The probabilities are the model's own
tested numbers; bookmaker prices are only used to say what a group pays and
to keep a spread of prices inside each group. The Daily List is untouched.

Which probability a leg carries
-------------------------------
Every pick on the site already says how often calls at its level landed in
testing ("86% landed"). That tested rate is the honest number for a leg, so a
group's chance is the product of its legs' tested rates, each capped at the
model's own number (19 Oct 2026; before, the rate was pulled toward the
model's number, which ran high):

    p_leg = min(hit, p_model)

A leg needs a tested rate (n >= 30), a tested rate of at least 65%, and must
be one the board does not flag (football: rated, not a draw pick).

Where the prices come from
--------------------------
  football        API-Football /odds (Match Winner, every bookmaker on the
                  fixture; average and best), matched to our games by date,
                  kick-off within 90 minutes, and both team names
  NFL, MLB, NBA   ESPN scoreboards (DraftKings moneyline), matched by ESPN id
  tennis, rugby,  The Odds API (the-odds-api.com, UK bookmakers, match odds),
  anything else   only when the ODDS_API_KEY secret is set and only for legs
                  the sources above did not price; free plan of 500 credits a
                  month, so capped at ODDS_API_DAY credits a UK day and
                  ODDS_API_MONTH a month, each sport's odds cached for
                  ODDS_API_TTL (see price_odds_api)
  otherwise       no bookmaker price: the leg is shown with the model's fair
                  price (1 / p), marked as an estimate, and never used in a
                  group (19 Oct 2026)

A leg's chance in a group is the lower of its tested rate (above) and the
bookmaker's fair chance (1 / price, less the book's margin; see honest()).

How a group is chosen
---------------------
Three bands by combined odds: Steady 2.5-4, Balanced 4-7, Stretch 7-14. In
each band the five legs with the highest joint tested chance, subject to:
  - a spread of prices: at least one short leg (under 1.30), at least one
    middle leg (1.30-1.60), and Balanced and Stretch at least one leg 1.60+
  - at most two very short legs (under 1.15), which add risk but little return
  - one leg per game, no more than two from one competition
  - a small preference for mixing sports
Then a second, separate group per band ("alternative") from the legs left.
Today and tomorrow, so six groups a day, none sharing a leg.

Standard library only.
"""
import itertools, json, math, os, re, sys, time, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
AF_BASE = "https://v3.football.api-sports.io"
ESPN = "https://site.api.espn.com/apis/site/v2/sports"
ESPN_PATH = {"nfl": "football/nfl", "mlb": "baseball/mlb", "nba": "basketball/nba",
             "nhl": "hockey/nhl", "cfb": "football/college-football",
             "ncaab": "basketball/mens-college-basketball", "wnba": "basketball/wnba"}
ESPN_Q = {"ncaab": "&groups=50"}   # all of Division I, as sports.py
# Banker (19 Oct 2026): three legs paying 1.5 to 2.5, the group built to land
# most often. Built first each day so it takes the strongest legs. A group's
# price all but sets its chance: five legs paying 2.5+ is a 25-40% shot even
# when every leg is honest, so a group that lands often has to pay less.
BANDS = [("Banker", 1.5, 2.5), ("Steady", 2.5, 4.0), ("Balanced", 4.0, 7.0), ("Stretch", 7.0, 14.0)]
LEGS_IN = {"Banker": 3}                 # every other band: five
# Sports whose tested rates have held up on live legs (19 Oct 2026, 234
# settled legs, 5-18 Oct): football landed 75.5% against 77.5% quoted.
# Tennis (68.5% v 83.4%, n=54), college football (70.4% v 85.4%, n=27) and
# NFL (55.6% v 72.2%, n=9) landed far under, and since 12 Oct worse still
# (61.8%, 53.8%, 40.0%), so they stay out. Rugby's held (5 of 5, and 16 of 17
# on the Daily List). Tennis re-tested the same day on every main-draw match
# since 1 Sep (1,096, walk-forward): its 75%+ calls landed about 85%, and the
# live prices match that replay, so the model is sound and the fortnight was a
# bad run; it stays out on caution, as it is off the Daily List (15 Oct).
GROUP_SPORTS = {"football", "rugby"}
MIN_N, MIN_HIT = 30, 0.65
UA = {"User-Agent": "Mozilla/5.0 (footyalmanac groupings)"}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\b(fc|afc|cf|sc|ac|fk|sk|club|the|de|cd|ud|sd)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def same(a, b):
    a, b = norm(a), norm(b)
    if not a or not b: return False
    return a == b or a in b or b in a or SequenceMatcher(None, a, b).ratio() >= 0.8

def get(url, headers=None, timeout=40):
    req = urllib.request.Request(url, headers=dict(UA, **(headers or {})))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def read_js(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path): return None
    t = open(path).read()
    return json.loads(t[t.index("=") + 1:].rstrip().rstrip(";"))

def iso(dt): return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
def parse(s):
    if not s: return None
    s = s.replace("Z", "+00:00")
    if re.match(r".*T\d\d:\d\d\+", s): s = s.replace("+", ":00+", 1)
    try: return datetime.fromisoformat(s).astimezone(timezone.utc)
    except ValueError: return None

def leg_p(p, acc):
    """A leg's chance: its band's tested rate, never above the model's own
    number. Until 19 Oct 2026 it was the tested rate pulled toward the
    model's number, which is the side that runs high at the top end (a 90%
    pick with a 77% tested rate was quoted 83%); legs landed 73.1% against
    79.8% quoted, 5-18 Oct."""
    if not acc or not acc.get("n") or acc.get("hit") is None: return None
    if acc["n"] < MIN_N or acc["hit"] < MIN_HIT: return None
    return min(acc["hit"], p)

# ---------- the board ----------
def legs(dates):
    out = []
    data = json.load(open(os.path.join(HERE, "data.json"))) if os.path.exists(os.path.join(HERE, "data.json")) else {}
    for day in data.get("days") or []:
        if day["date"] not in dates: continue
        for g in day.get("games", []):
            p = g.get("p") or {}
            if not p or g.get("unrated"): continue
            side = max(p, key=p.get)
            if side == "d": continue
            pl = leg_p(p[side], g.get("accuracy"))
            if pl is None: continue
            h, a = g["home"]["name"], g["away"]["name"]
            out.append({"sport": "football", "event": f"{h} v {a}", "home": h, "away": a, "side": side,
                        "pick": h if side == "h" else a, "code": g.get("league"), "comp": g.get("leagueName"), "country": g.get("country"),
                        "when": g.get("kickoff"), "date": day["date"], "pModel": round(p[side], 4), "p": round(pl, 4),
                        "hit": g["accuracy"].get("cumHit", g["accuracy"]["hit"]), "n": g["accuracy"].get("cumN", g["accuracy"]["n"]), "list": bool(g.get("list"))})
    td = (read_js("tennis-data.js") or {}) if "tennis" in GROUP_SPORTS else {}
    for m in td.get("matches") or []:
        when = f"{m['date']}T{m['time']}:00Z" if m.get("time") else None
        d = m.get("date")
        if d not in dates or "qualif" in (m.get("round") or "").lower(): continue
        pl = leg_p(m.get("confidence") or 0, m.get("accuracy"))
        if pl is None: continue
        out.append({"sport": "tennis", "event": f"{m['playerA']} v {m['playerB']}", "pick": m["pick"], "tour": m.get("tour"), "tournament": m.get("tournament"),
                    "players": [m.get("playerA"), m.get("playerB")],
                    "comp": f"{m.get('tournament')} {m.get('round') or ''}".strip(), "when": when, "date": d, "id": m.get("id"),
                    "pModel": round(m["confidence"], 4), "p": round(pl, 4), "hit": m["accuracy"].get("cumHit", m["accuracy"]["hit"]), "n": m["accuracy"].get("cumN", m["accuracy"]["n"]),
                    "list": bool(m.get("list"))})
    sd = read_js("sports-data.js") or {}
    for key, sp in (sd.get("sports") or {}).items():
        if not sp.get("published") or key not in GROUP_SPORTS: continue
        for g in sp.get("games") or []:
            t = parse(g.get("when"))
            if not t or t.date().isoformat() not in dates: continue
            pl = leg_p(g.get("confidence") or 0, g.get("accuracy"))
            if pl is None: continue
            out.append({"sport": key, "event": f"{g['home']} v {g['away']}", "home": g["home"], "away": g["away"],
                        "pick": g["pick"], "comp": g.get("label") or sp.get("name"), "when": g.get("when"), "date": t.date().isoformat(),
                        "id": g.get("id"), "pModel": round(g["confidence"], 4), "p": round(pl, 4),
                        "hit": g["accuracy"].get("cumHit", g["accuracy"]["hit"]), "n": g["accuracy"].get("cumN", g["accuracy"]["n"]), "list": bool(g.get("list"))})
    return out

# ---------- prices ----------
def af(path, key):
    return get(AF_BASE + path, {"x-apisports-key": key})

ODDS_TTL = 90 * 60     # a fixture's prices are re-read at most every 90 minutes


def _odds_for(fid, key, cache_dir):
    """Match Winner prices for one fixture, cached on disk for ODDS_TTL.
    Returns (response items, calls made)."""
    path = os.path.join(cache_dir, f"odds-{fid}.json")
    try:
        if time.time() - os.path.getmtime(path) < ODDS_TTL:
            with open(path) as f:
                return json.load(f), 0
    except (OSError, ValueError):
        pass
    r = af(f"/odds?fixture={fid}&bet=1", key)
    items = r.get("response") or []
    os.makedirs(cache_dir, exist_ok=True)
    with open(path, "w") as f:
        json.dump(items, f)
    return items, 1


def price_football(L, dates, report):
    """API-Football prices for the football legs.

    Until 6 Oct 2026 this paged through /odds?date= for every date, ten
    fixtures a page and up to 60 pages, to price twenty-odd legs. Now the legs
    are matched to fixtures first, from the day pool the build already holds
    (sources._af_day, no call when cached), and only those fixtures are
    priced, one call each, cached for ODDS_TTL."""
    key = os.environ.get("API_FOOTBALL_KEY")
    fb = [l for l in L if l["sport"] == "football"]
    if not key or not fb:
        report["football"] = "no key" if not key else "no legs"; return
    sys.path.insert(0, HERE)
    import sources as S
    from datetime import date as _date
    calls, matched = 0, 0
    for d in sorted(dates):
        try:
            fx = S._af_day(_date.fromisoformat(d))
        except Exception as e:
            report.setdefault("errors", []).append(f"fixtures {d}: {type(e).__name__}"); continue
        teams = {f["fixture"]["id"]: (f["teams"]["home"]["name"], f["teams"]["away"]["name"], parse(f["fixture"]["date"]))
                 for f in fx}
        for l in fb:
            if l["date"] != d or l.get("odds"): continue
            t = parse(l["when"])
            fid = next((fid for fid, (h, a, ft) in teams.items()
                        if not (t and ft and abs((t - ft).total_seconds()) > 5400)
                        and same(h, l["home"]) and same(a, l["away"])), None)
            if fid is None: continue
            try:
                items, n = _odds_for(fid, key, S.AF_CACHE_DIR); calls += n
            except Exception as e:
                report.setdefault("errors", []).append(f"odds {fid}: {type(e).__name__}"); continue
            prices = {"Home": [], "Away": [], "Draw": []}
            books = set()
            for item in items:
                for b in item.get("bookmakers") or []:
                    for bet in b.get("bets") or []:
                        if bet.get("id") != 1: continue
                        for v in bet.get("values") or []:
                            try: prices[v["value"]].append(float(v["odd"])); books.add(b.get("name"))
                            except (KeyError, ValueError): pass
            books = sorted(books)
            side = prices["Home" if l["side"] == "h" else "Away"]
            if side:
                avg = [sum(v) / len(v) for v in prices.values() if v]
                l.update(odds=round(sum(side) / len(side), 2), best=round(max(side), 2), books=len(books),
                         margin=margin_of(avg) if len(avg) == 3 else None,
                         src="API-Football, average of " + (f"{len(books)} bookmakers" if len(books) != 1 else books[0]))
                matched += 1
    report["football"] = {"calls": calls, "matched": matched, "legs": len(fb)}

def american(x):
    try: x = float(str(x).replace("+", ""))
    except ValueError: return None
    return round(1 + (x / 100 if x > 0 else 100 / -x), 2) if x else None

def price_espn(L, dates, report):
    out = {}
    for sport, path in ESPN_PATH.items():
        want = {str(l.get("id")): l for l in L if l["sport"] == sport}
        if not want: continue
        n = 0
        for d in sorted(dates):
            try: sb = get(f"{ESPN}/{path}/scoreboard?dates={d.replace('-', '')}&limit=400{ESPN_Q.get(sport, '')}")
            except Exception as e:
                report.setdefault("errors", []).append(f"espn {sport} {d}: {type(e).__name__}"); continue
            for ev in sb.get("events") or []:
                l = want.get(str(ev.get("id")))
                if not l or l.get("odds"): continue
                comp = (ev.get("competitions") or [{}])[0]
                o = (comp.get("odds") or [None])[0]
                if not o: continue
                home = next((c["team"]["displayName"] for c in comp.get("competitors", []) if c.get("homeAway") == "home"), "")
                side = "home" if same(home, l["pick"]) else "away"
                ml = (o.get("moneyline") or {}).get(side) or {}
                dec = american((ml.get("close") or ml.get("open") or {}).get("odds") or (o.get(f"{side}TeamOdds") or {}).get("moneyLine"))
                if dec and dec > 1:
                    l.update(odds=dec, margin=margin_of([espn_ml(o, "home"), espn_ml(o, "away")]),
                             src=f"ESPN, {o.get('provider', {}).get('name', 'bookmaker')} moneyline"); n += 1
        out[sport] = {"matched": n, "legs": len(want)}
    report["espn"] = out

def margin_of(decs):
    """A book's margin from every outcome's decimal price (1.05 = 5%), or None."""
    decs = [d for d in decs if d and d > 1]
    return round(sum(1 / d for d in decs), 4) if len(decs) >= 2 else None

def espn_ml(o, side):
    """Decimal price for 'home' or 'away' from an ESPN odds block, or None."""
    ml = (o.get("moneyline") or {}).get(side) or {}
    return american((ml.get("close") or ml.get("open") or {}).get("odds") or (o.get(f"{side}TeamOdds") or {}).get("moneyLine"))

def price_espn_soccer(L, dates, report):
    """Second football source: ESPN soccer scoreboards (DraftKings three-way
    moneyline), for legs API-Football did not price. ESPN's dates= is a US
    Eastern day, so each UK date also asks for the day before. Matched on the
    competition's ESPN slug, kick-off within 90 minutes and both team names."""
    from sources import ESPN_SLUGS
    want = [l for l in L if l["sport"] == "football" and not l.get("odds") and l.get("code") in ESPN_SLUGS]
    if not want:
        report["espn_soccer"] = {"matched": 0, "legs": 0}; return
    calls, matched = 0, 0
    for slug in sorted({s for l in want for s in ESPN_SLUGS[l["code"]]}):
        mine = [l for l in want if slug in ESPN_SLUGS[l["code"]]]
        days = set()
        for l in mine:
            d = datetime.fromisoformat(l["date"])
            days |= {d, d - timedelta(days=1)}
        for d in sorted(days):
            try:
                sb = get(f"{ESPN}/soccer/{slug}/scoreboard?dates={d.strftime('%Y%m%d')}"); calls += 1
            except Exception as e:
                report.setdefault("errors", []).append(f"espn soccer {slug} {d.date()}: {type(e).__name__}"); continue
            for ev in sb.get("events") or []:
                comp = (ev.get("competitions") or [{}])[0]
                o = (comp.get("odds") or [None])[0]
                if not o: continue
                cs = {c.get("homeAway"): c.get("team", {}).get("displayName", "") for c in comp.get("competitors", [])}
                ft = parse(ev.get("date"))
                for l in mine:
                    if l.get("odds"): continue
                    t = parse(l["when"])
                    if t and ft and abs((t - ft).total_seconds()) > 5400: continue
                    if not (same(cs.get("home"), l["home"]) and same(cs.get("away"), l["away"])): continue
                    dec = espn_ml(o, "home" if l["side"] == "h" else "away")
                    if dec and dec > 1:
                        draw = american(((o.get("drawOdds") or {}).get("moneyLine")))
                        l.update(odds=dec, margin=margin_of([espn_ml(o, "home"), espn_ml(o, "away"), draw]) if draw else None,
                                 src=f"ESPN, {o.get('provider', {}).get('name', 'bookmaker')} moneyline"); matched += 1
    report["espn_soccer"] = {"calls": calls, "matched": matched, "legs": len(want)}

# ---------- The Odds API (optional, last) ----------
ODDS_API = "https://api.the-odds-api.com/v4/sports"
ODDS_API_DAY = 15      # credits a UK day: 15 x 31 = 465, inside the free 500
ODDS_API_MONTH = 480   # and never past this in a calendar month (UTC)
ODDS_API_FLOOR = 20    # stop when the API says fewer than this are left
ODDS_API_TTL = 4 * 3600   # a sport's odds are re-read at most every 4 hours
ODDS_RUGBY = {"Premiership": ("premiership",), "URC": ("united rugby", "urc"), "Top 14": ("top 14",),
              "Test match": ("international", "test", "autumn nations", "rugby championship", "six nations")}
ODDS_STOP = {"atp", "wta", "open", "tennis", "the", "de", "di", "cup", "tournament", "international", "championships"}


def _words(s):
    return {w for w in norm(s).split() if len(w) > 2 and w not in ODDS_STOP}


def _odds_get(url):
    """(json, credits left or None)."""
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        left = r.headers.get("x-requests-remaining")
        return json.loads(r.read()), (int(float(left)) if left not in (None, "") else None)


def _odds_keys(l, active):
    """The Odds API sport keys that could price leg l, from the free /sports list."""
    out = []
    for sp in active:
        k, title = sp.get("key", ""), f"{sp.get('title', '')} {sp.get('description', '')}"
        if l["sport"] == "tennis":
            title += " " + k.replace("_", " ")   # the key often names the event when the title is only the tour
            tour = (l.get("tour") or "").lower()
            if tour and k.startswith(f"tennis_{tour}") and _words(l.get("tournament")) & _words(title):
                out.append(k)
        elif l["sport"] == "rugby":
            if k.startswith("rugbyunion") and any(w in title.lower() for w in ODDS_RUGBY.get(l.get("comp"), (norm(l.get("comp") or ""),))):
                out.append(k)
        elif l["sport"] == "nrl":
            if k == "rugbyleague_nrl": out.append(k)
    return out


def price_odds_api(L, dates, report, cache_dir=None, now=None, fetch=None):
    """UK bookmaker match odds from The Odds API for legs nothing else priced.

    Only with ODDS_API_KEY. The /sports list is free; each sport key's odds
    (regions=uk, markets=h2h) cost one credit, so a key is fetched only when an
    unpriced leg needs it, cached on disk for ODDS_API_TTL (.afcache, kept
    between builds), most-needed first, inside a ledger of ODDS_API_DAY credits
    a UK day and ODDS_API_MONTH a month, and never once the API reports fewer
    than ODDS_API_FLOOR left. Prices never feed a model."""
    key = os.environ.get("ODDS_API_KEY")
    want = [l for l in L if not l.get("odds") and l["sport"] in ("tennis", "rugby", "nrl")]
    if not key or not want:
        report["oddsApi"] = "no key" if not key else "no legs"; return
    fetch = fetch or _odds_get
    now = now or datetime.now(timezone.utc)
    if cache_dir is None:
        sys.path.insert(0, HERE)
        import sources as S
        cache_dir = S.AF_CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)
    led_path = os.path.join(cache_dir, "oddsapi-ledger.json")
    try: led = json.load(open(led_path))
    except (OSError, ValueError): led = {}
    day = now.astimezone(ZoneInfo("Europe/London")).date().isoformat(); month = now.strftime("%Y-%m")
    if led.get("month") != month: led = {"month": month, "used": 0, "days": {}, "left": None}
    rep = {"calls": 0, "cached": 0, "matched": 0, "legs": len(want), "skipped": []}

    def cached(name, ttl):
        path = os.path.join(cache_dir, f"oddsapi-{name}.json")
        try:
            if time.time() - os.path.getmtime(path) < ttl: return json.load(open(path))
        except (OSError, ValueError): pass
        return None

    def keep(name, data):
        with open(os.path.join(cache_dir, f"oddsapi-{name}.json"), "w") as f: json.dump(data, f)

    sports = cached("sports", 12 * 3600)
    if sports is None:
        try: sports, _ = fetch(f"{ODDS_API}?apiKey={key}"); keep("sports", sports)
        except Exception as e:
            report["oddsApi"] = dict(rep, error=type(e).__name__); return
    active = [s for s in sports if s.get("active")]
    need = {}
    for l in want:
        for k in _odds_keys(l, active): need.setdefault(k, []).append(l)
    # Why a tennis tournament finds no key (19 Oct: Almaty, European Open, Japan Open): the
    # free /sports list is logged so --probe shows what the API carries and what matched nothing.
    rep["tennisKeys"] = sorted(f"{s.get('key')} | {s.get('title')}" for s in active if str(s.get("key", "")).startswith("tennis"))
    rep["noKey"] = sorted({f"{l.get('tour')} {l.get('tournament')}" for l in want
                           if l["sport"] == "tennis" and not _odds_keys(l, active)})
    for k in sorted(need, key=lambda k: -len(need[k])):
        events = cached(k, ODDS_API_TTL)
        if events is None:
            spent = led["days"].get(day, 0)
            left = led.get("left")
            if spent >= ODDS_API_DAY or led["used"] >= ODDS_API_MONTH or (left is not None and left < ODDS_API_FLOOR):
                rep["skipped"].append(k); continue
            try: events, left = fetch(f"{ODDS_API}/{k}/odds?apiKey={key}&regions=uk&markets=h2h&oddsFormat=decimal")
            except Exception as e:
                report.setdefault("errors", []).append(f"odds api {k}: {type(e).__name__}"); continue
            keep(k, events); rep["calls"] += 1
            led["used"] += 1; led["days"][day] = spent + 1
            if left is not None: led["left"] = left
        else:
            rep["cached"] += 1
        for l in need[k]:
            if l.get("odds"): continue
            names = l.get("players") or [l.get("home"), l.get("away")]
            t = parse(l.get("when"))
            for ev in events:
                h, a = ev.get("home_team", ""), ev.get("away_team", "")
                if not (any(same(h, x) for x in names if x) and any(same(a, x) for x in names if x)): continue
                ct = parse(ev.get("commence_time"))
                if t and ct and abs((t - ct).total_seconds()) > 6 * 3600: continue
                prices, books, margins = [], set(), []
                for b in ev.get("bookmakers") or []:
                    for m in b.get("markets") or []:
                        if m.get("key") != "h2h": continue
                        mg = margin_of([o.get("price") for o in m.get("outcomes") or []])
                        if mg: margins.append(mg)
                        for o in m.get("outcomes") or []:
                            if same(o.get("name", ""), l["pick"]):
                                try: prices.append(float(o["price"])); books.add(b.get("title") or b.get("key"))
                                except (KeyError, ValueError): pass
                if prices:
                    l.update(odds=round(sum(prices) / len(prices), 2), best=round(max(prices), 2), books=len(books),
                             margin=round(sum(margins) / len(margins), 4) if margins else None,
                             src="The Odds API, UK average of " + (f"{len(books)} bookmakers" if len(books) != 1 else next(iter(books))))
                    rep["matched"] += 1
                break
    with open(led_path, "w") as f: json.dump(led, f)
    rep.update(usedToday=led["days"].get(day, 0), usedMonth=led["used"], left=led.get("left"))
    report["oddsApi"] = rep

def price(L, dates):
    report = {}
    price_football(L, dates, report)
    price_espn_soccer(L, dates, report)
    price_espn(L, dates, report)
    price_odds_api(L, dates, report)
    for l in L:
        if not l.get("odds"):
            l.update(odds=round(1 / l["pModel"], 2), est=True, src="estimate: the model's fair price, no bookmaker price found")
        honest(l)
    report["priced"] = sum(1 for l in L if not l.get("est")); report["legs"] = len(L)
    return report

# ---------- honest chances (19 Oct 2026) ----------
# 4-18 Oct: 8 of 48 groups won against 15.9 expected. Legs won 73.1% while the
# tested rates said 79.8% and the bookmakers' prices implied 75.7%, nearer 72%
# without their margin: the market was the better guide. Choosing the five
# legs with the best tested chance for the odds also picked the legs where the
# model and the bookmakers disagreed most, and those won least (10+ points
# above the price: 66.7%). Estimated legs (no bookmaker price) won 68.5% of
# tennis against 83.4% stated. So a leg's chance is now the lower of its tested
# rate and the bookmaker's fair chance, and a leg needs a bookmaker price.
MARGIN = 1.05   # assumed book margin when a source gives only the one side

def honest(l):
    """Set implied, fair and the leg's chance p = min(tested, fair). Prices
    pick and weigh legs here only; they never feed a model."""
    l["implied"] = round(1 / l["odds"], 4)
    l.setdefault("pTested", l["p"])
    if not l.get("est"):
        l["fair"] = round(l["implied"] / max(l.get("margin") or MARGIN, 1.0), 4)
        l["p"] = round(min(l["pTested"], l["fair"]), 4)
    l["edge"] = round(l["p"] * l["odds"] - 1, 4)
    return l

# ---------- groups ----------
def ok_combo(c, lo, hi, name, max_est=0):
    o = math.prod(l["odds"] for l in c)
    if not (lo <= o <= hi): return None
    if len({l["event"] for l in c}) < LEGS_IN.get(name, 5): return None
    if sum(l["odds"] < 1.15 for l in c) > 2 or sum(1 for l in c if l.get("est")) > max_est: return None
    if name != "Banker":
        if not any(l["odds"] < 1.30 for l in c) or not any(1.30 <= l["odds"] < 1.60 for l in c): return None
        if name != "Steady" and not any(l["odds"] >= 1.60 for l in c): return None
    comps = {}
    for l in c: comps[l.get("comp")] = comps.get(l.get("comp"), 0) + 1
    if max(comps.values()) > 2: return None
    return o

def pool(L, used, after):
    c = [l for l in L if l["event"] not in used and not l.get("est") and 1.05 <= l["odds"] <= 2.8 and (parse(l["when"]) or after) >= after]
    # Keep the strongest legs in each price range, so every band can be met
    # without trying every combination of several hundred legs.
    rng = lambda lo, hi, k: sorted([l for l in c if lo <= l["odds"] < hi], key=lambda l: -l["p"])[:k]
    return rng(1.05, 1.30, 12) + rng(1.30, 1.60, 12) + rng(1.60, 2.81, 9)

def best(L, used, after, name, lo, hi):
    # Bookmaker-priced legs only (19 Oct 2026): no estimates, no fallback.
    return _best(L, used, after, name, lo, hi, 0)

def _best(L, used, after, name, lo, hi, max_est):
    top = None
    for c in itertools.combinations(pool(L, used, after), LEGS_IN.get(name, 5)):
        o = ok_combo(c, lo, hi, name, max_est)
        if o is None: continue
        p = math.prod(l["p"] for l in c)
        sports = len({l["sport"] for l in c})
        score = p * (1 + 0.03 * (sports - 1))
        if not top or score > top[0]: top = (score, c, o, p)
    if not top: return None
    _, c, o, p = top
    legs5 = sorted([dict(l) for l in c], key=lambda l: l.get("when") or "9")
    implied = math.prod(l["implied"] for l in legs5)
    return {"name": name, "band": [lo, hi], "odds": round(o, 2), "p": round(p, 4), "implied": round(implied, 4),
            "estimates": sum(1 for l in legs5 if l.get("est")), "legs": legs5}

def build_day(L, after):
    used, groups = set(), []
    for rank in ("main", "alternative"):
        for name, lo, hi in BANDS:
            g = best(L, used, after, name, lo, hi)
            if not g: continue
            g["rank"] = rank; groups.append(g)
            used |= {l["event"] for l in g["legs"]}
    return groups

# ---------- the record ----------
ARCHIVE = os.path.join(HERE, "groupings-archive")

def load(name):
    try: return json.load(open(os.path.join(HERE, name)))
    except Exception: return {}

def results_index():
    """Every graded result, from each sport's full history. The records'
    "days" hold only their last 14 days, so a leg older than that used to
    fall back to Pending on the next regrade (5 Oct 2026 showed 0/5)."""
    rec, trec = load("record.json"), load("tennis-record.json")
    fb = {}
    full = load("record-graded.json").get("graded") or []
    rows = [(g.get("date"), g) for g in full] or \
           [(d.get("date"), g) for d in rec.get("days") or [] for g in d.get("games") or []]
    for date, g in rows:
        if g.get("result"):
            fb[(date, norm(g["home"]), norm(g["away"]))] = g["result"]
            fb.setdefault((None, norm(g["home"]), norm(g["away"])), g["result"])
    tn = {str(g.get("key")): g for g in trec.get("graded") or []} or \
         {str(g.get("key")): g for d in trec.get("days") or [] for g in d.get("games") or []}
    try:
        import sports as SP
        graded, voids = SP.graded_games()
        sp = {str(g.get("id")): g for g in graded}
        sp.update({str(g.get("id")): {**g, "void": True} for g in voids})
    except Exception:
        srec = load("sports-record.json")
        sp = {str(g.get("id")): g for d in srec.get("days") or [] for g in d.get("games") or []}
    return fb, tn, sp

def settle(l, idx):
    fb, tn, sp = idx
    if l["sport"] == "football":
        r = fb.get((l["date"], norm(l["home"]), norm(l["away"]))) or fb.get((None, norm(l["home"]), norm(l["away"])))
        if not r: return "pending", None
        h, a = r; win = "h" if h > a else "a" if a > h else "d"
        return ("won" if win == l["side"] else "lost"), f"{h}-{a}"
    if l["sport"] == "tennis":
        g = tn.get(str(l.get("id")))
        if not g: return "pending", None
        if g.get("void"): return "void", "void"
        return ("won" if norm(g.get("winner")) == norm(l["pick"]) else "lost"), g.get("note") or g.get("winner")
    g = sp.get(str(l.get("id")))
    if g and g.get("void"): return "void", "tie"
    if not g or not g.get("winner"): return "pending", None
    sc = g.get("score")
    return ("won" if norm(g["winner"]) == norm(l["pick"]) else "lost"), ("-".join(map(str, sc)) if isinstance(sc, list) else sc)

def archive(day, generated):
    os.makedirs(ARCHIVE, exist_ok=True)
    path = os.path.join(ARCHIVE, f"{day['date']}.json")
    if os.path.exists(path) or not day["groups"]: return False
    json.dump({"date": day["date"], "published": generated, "groups": day["groups"]}, open(path, "w"), indent=1, ensure_ascii=False)
    return True

def grade():
    idx = results_index(); days = []
    files = sorted(f for f in os.listdir(ARCHIVE) if f.endswith(".json")) if os.path.isdir(ARCHIVE) else []
    for f in files[-60:]:
        a = json.load(open(os.path.join(ARCHIVE, f))); gs = []
        for g in a["groups"]:
            legs = []
            for l in g["legs"]:
                st, res = settle(l, idx)
                legs.append({"pick": l["pick"], "event": l["event"], "sport": l["sport"], "comp": l.get("comp"), "when": l.get("when"),
                             "odds": l["odds"], "est": bool(l.get("est")), "p": l["p"], "status": st, "result": res})
            sts = [l["status"] for l in legs]
            status = "lost" if "lost" in sts else "won" if all(x in ("won", "void") for x in sts) else "pending"
            paid = math.prod(l["odds"] for l in legs if l["status"] != "void") if status == "won" else 0
            gs.append({"name": g["name"], "rank": g.get("rank", "main"), "odds": g["odds"], "p": g["p"], "status": status,
                       "paid": round(paid, 2), "legsWon": sts.count("won"), "legsLost": sts.count("lost"),
                       "legsPending": sts.count("pending"), "legs": legs})
        days.append({"date": a["date"], "published": a.get("published"), "groups": gs})
    days.sort(key=lambda d: d["date"], reverse=True)
    def tally(groups):
        done = [g for g in groups if g["status"] != "pending"]
        legs = [l for g in groups for l in g["legs"] if l["status"] in ("won", "lost")]
        return {"groups": len(groups), "settled": len(done), "won": sum(g["status"] == "won" for g in done),
                "lost": sum(g["status"] == "lost" for g in done), "pending": len(groups) - len(done),
                "legs": len(legs), "legsWon": sum(l["status"] == "won" for l in legs),
                "returned": round(sum(g["paid"] for g in done), 2), "staked": len(done),
                "expected": round(sum(g["p"] for g in done), 2)}
    allg = [g for d in days for g in d["groups"]]
    out = {"graded": iso(datetime.now(timezone.utc)), "overall": tally(allg),
           "byBand": {b[0]: tally([g for g in allg if g["name"] == b[0]]) for b in BANDS},
           "firstChoice": tally([g for g in allg if g["rank"] == "main"]), "days": days}
    json.dump(out, open(os.path.join(HERE, "groupings-record.json"), "w"), indent=1, ensure_ascii=False)
    return out

def write_page(out, record):
    page = dict(out, record=record)
    with open(os.path.join(HERE, "groupings-data.js"), "w") as f:
        f.write("window.__GROUPINGS__=" + json.dumps(page, separators=(",", ":")).replace("</", "<\\/") + ";")

def main():
    if "--grade" in sys.argv:
        rec = grade()
        cur = load("groupings.json")
        if cur: cur.pop("pool", None); write_page(cur, rec)
        print(f"groupings record: {rec['overall']}", file=sys.stderr); return
    probe = "--probe" in sys.argv
    now = datetime.now(timezone.utc)
    # Days are the board's own dates (UK days on the football board).
    today = now.astimezone(ZoneInfo("Europe/London")).date()
    dates = [today.isoformat(), (today + timedelta(days=1)).isoformat()]
    L = legs(set(dates))
    report = price(L, set(dates))
    if probe:
        print(json.dumps(report, indent=1)); return
    days = []
    for d in dates:
        dl = [l for l in L if l["date"] == d]
        days.append({"date": d, "legs": len(dl), "priced": sum(1 for l in dl if not l.get("est")),
                     "groups": build_day(dl, now + timedelta(minutes=20))})
    out = {"generated": iso(now), "bands": BANDS, "rules": {"minN": MIN_N, "minHit": MIN_HIT},
           "sources": report, "days": days}
    # The full priced pool goes in the JSON only (the page does not need it),
    # so the office can regroup later in the day from games still to start.
    full = dict(out, pool={d: [l for l in L if l["date"] == d] for d in dates})
    json.dump(full, open(os.path.join(HERE, "groupings.json"), "w"), separators=(",", ":"))
    if days and days[0]["date"] == today.isoformat(): archive(days[0], out["generated"])
    record = grade()
    write_page(out, record)
    print(f"groupings: {sum(len(d['groups']) for d in days)} groups over {len(days)} days; "
          f"{report['priced']} of {report['legs']} legs priced", file=sys.stderr)

if __name__ == "__main__":
    main()
