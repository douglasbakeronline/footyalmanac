"""Free price sources (11 Nov 2026).

Douglas, 11 Nov 2026: "Every single game needs odds attached ... Find as many
free sources as you can before we look at increasing costs." Three free feeds,
each switched on by its own secrets and silent without them:

- Betfair Exchange, delayed application key (free with a Betfair account;
  prices 1 to 180 seconds behind live). Every sport Betfair lists, which is
  nearly every football league and tennis match. BETFAIR_APP_KEY,
  BETFAIR_USERNAME, BETFAIR_PASSWORD.
- Matchbook exchange (free with a Matchbook account). MATCHBOOK_USERNAME,
  MATCHBOOK_PASSWORD; prices are read without a session when the API allows.
- SportsGameOdds, free Amateur plan (2,500 games a month, 10 requests a
  minute; NFL, NBA, MLB, NHL, college football and basketball, Champions
  League, MLS). SGO_API_KEY.

Each fills only legs nothing else priced (`odds` empty), after the
bookmaker sources in groupings.price, and labels the price with its source.
An exchange price is the best back price: close to a fair price, with no
bookmaker margin but a commission on winnings (Betfair 2-5%, Matchbook 2%).
SportsGameOdds' William Hill is kept apart (`sgoBooks`) until it is shown to
be the UK book (`SGO_HILL_IS_UK`): its free plan is US-focused and the US
William Hill is now Caesars. Prices never feed a model. Standard library only.
"""
import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "footyalmanac/1.0 (+https://douglasbakeronline.github.io/footyalmanac/)"}

# ---------- shared ----------
def _cache_dir(cache_dir):
    if cache_dir: os.makedirs(cache_dir, exist_ok=True); return cache_dir
    import sources as S
    os.makedirs(S.AF_CACHE_DIR, exist_ok=True)
    return S.AF_CACHE_DIR

def _cached(path, ttl):
    try:
        if time.time() - os.path.getmtime(path) < ttl: return json.load(open(path))
    except (OSError, ValueError): pass
    return None

def _keep(path, data):
    with open(path, "w") as f: json.dump(data, f)

def _http(url, data=None, headers=None, method=None, timeout=40):
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=dict(UA, **(headers or {})), method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"null")

def _names(l):
    return l.get("players") or [l.get("home"), l.get("away")]

def _match(l, a, b, start, G):
    """True when runners / teams a and b (either order) are leg l's two sides
    and the start is within six hours of the leg's."""
    n = _names(l)
    if not all(n) or not a or not b: return False
    t, st = G.parse(l.get("when")), start
    if t and st and abs((t - st).total_seconds()) > 6 * 3600: return False
    return ((G.same_any(a, n[0]) and G.same_any(b, n[1])) or (G.same_any(a, n[1]) and G.same_any(b, n[0])))

def _fill(l, G, odds, other, draw, src, at, book):
    """Set an unpriced leg's price from an exchange or a free feed."""
    l.update(odds=round(odds, 2), best=round(odds, 2), bestBook=book, books=1,
             opp=round(other, 2) if other else None, draw=round(draw, 2) if draw else None,
             margin=G.margin_of([x for x in (odds, other, draw) if x]), pricedAt=at, src=src)

def _window(dates):
    ds = sorted(dates)
    lo = datetime.fromisoformat(ds[0]).replace(tzinfo=timezone.utc) - timedelta(hours=6)
    hi = datetime.fromisoformat(ds[-1]).replace(tzinfo=timezone.utc) + timedelta(hours=30)
    return lo, hi

def _iso(d): return d.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- Betfair Exchange (delayed key) ----------
BF_LOGIN = "https://identitysso.betfair.com/api/login"
BF_RPC = "https://api.betfair.com/exchange/betting/json-rpc/v1"
BF_TYPES = {"football": "1", "tennis": "2", "rugby": "5", "nrl": "1477", "nba": "7522", "ncaab": "7522",
            "wnba": "7522", "nfl": "6423", "cfb": "6423", "nhl": "7524", "mlb": "7511"}
BF_TTL = 30 * 60            # a sport's catalogue and prices, re-read at most every 30 minutes
BF_BOOK_BATCH = 40          # listMarketBook with best offers: weight 5 a market, 200 a call

def _bf_session(key, user, pw, cache_dir, post):
    # Never written to disk: .afcache is an Actions cache on a public repo, and a
    # session token there could be restored by another workflow. One login a build.
    r = post(BF_LOGIN, urllib.parse.urlencode({"username": user, "password": pw}).encode(),
             {"X-Application": key, "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"})
    if not r or r.get("status") != "SUCCESS" or not r.get("token"):
        raise RuntimeError(f"betfair login: {(r or {}).get('error') or 'failed'}")
    return r["token"]

def _bf_rpc(post, key, token, method, params):
    r = post(BF_RPC, [{"jsonrpc": "2.0", "method": f"SportsAPING/v1.0/{method}", "params": params, "id": 1}],
             {"X-Application": key, "X-Authentication": token, "Content-Type": "application/json", "Accept": "application/json"})
    r = r[0] if isinstance(r, list) and r else r or {}
    if r.get("error"): raise RuntimeError(f"betfair {method}: {json.dumps(r['error'])[:200]}")
    return r.get("result") or []

def price_betfair(L, dates, report, cache_dir=None, post=None, now=None):
    import groupings as G
    key, user, pw = (os.environ.get(k) for k in ("BETFAIR_APP_KEY", "BETFAIR_USERNAME", "BETFAIR_PASSWORD"))
    want = [l for l in L if not l.get("odds") and l["sport"] in BF_TYPES]
    if not (key and user and pw) or not want:
        report["betfair"] = "no key" if not (key and user and pw) else "no legs"; return
    cache_dir = _cache_dir(cache_dir)
    post = post or (lambda u, d, h: _http(u, d, h, "POST"))
    rep = {"calls": 0, "legs": len(want), "matched": 0, "markets": 0}
    try:
        token = _bf_session(key, user, pw, cache_dir, post); rep["calls"] += 1
    except Exception as e:
        report["betfair"] = dict(rep, error=str(e)[:200]); return
    lo, hi = _window(dates)
    by_type = {}
    for l in want: by_type.setdefault(BF_TYPES[l["sport"]], []).append(l)
    for et, legs in by_type.items():
        path = os.path.join(cache_dir, f"betfair-{et}.json")
        data = _cached(path, BF_TTL)
        if data is None:
            try:
                cat = _bf_rpc(post, key, token, "listMarketCatalogue", {
                    "filter": {"eventTypeIds": [et], "marketTypeCodes": ["MATCH_ODDS"],
                               "marketStartTime": {"from": _iso(lo), "to": _iso(hi)}},
                    "maxResults": 1000, "sort": "FIRST_TO_START",
                    "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"]}); rep["calls"] += 1
                # prices only for the markets a wanted leg could match (by start
                # time and a name), so a 1,000-market football day costs a few calls
                need = [m for m in cat if any(_bf_names_hit(m, l, G) for l in legs)]
                books = {}
                for i in range(0, len(need), BF_BOOK_BATCH):
                    ids = [m["marketId"] for m in need[i:i + BF_BOOK_BATCH]]
                    for b in _bf_rpc(post, key, token, "listMarketBook", {"marketIds": ids,
                                     "priceProjection": {"priceData": ["EX_BEST_OFFERS"]}}):
                        books[b["marketId"]] = {str(r["selectionId"]): ((r.get("ex") or {}).get("availableToBack") or [{}])[0].get("price")
                                                for r in b.get("runners") or [] if r.get("status", "ACTIVE") == "ACTIVE"}
                    rep["calls"] += 1
                data = {"cat": need, "books": books, "at": _iso(datetime.now(timezone.utc))}
                _keep(path, data)
            except Exception as e:
                report.setdefault("errors", []).append(f"betfair {et}: {str(e)[:120]}"); continue
        rep["markets"] += len(data["cat"])
        for l in legs:
            if l.get("odds"): continue
            for m in data["cat"]:
                runners = [r for r in m.get("runners") or [] if r.get("runnerName") != "The Draw"]
                if len(runners) != 2: continue
                a, b = runners[0]["runnerName"], runners[1]["runnerName"]
                if not _match(l, a, b, G.parse(m.get("marketStartTime")), G): continue
                px = data["books"].get(m["marketId"]) or {}
                pick = next((r for r in runners if G.same_any(r["runnerName"], l["pick"])), None)
                if not pick or not px.get(str(pick["selectionId"])): break
                other = next(r for r in runners if r is not pick)
                draw = next((r for r in m.get("runners") or [] if r.get("runnerName") == "The Draw"), None)
                _fill(l, G, px[str(pick["selectionId"])], px.get(str(other["selectionId"])),
                      px.get(str(draw["selectionId"])) if draw else None,
                      "Betfair Exchange, best back price (delayed)", data.get("at"), "Betfair Exchange")
                l["exchange"] = "betfair"
                rep["matched"] += 1; break
    report["betfair"] = rep

def _bf_names_hit(m, l, G):
    t, st = G.parse(l.get("when")), G.parse(m.get("marketStartTime"))
    if t and st and abs((t - st).total_seconds()) > 6 * 3600: return False
    names = [r.get("runnerName", "") for r in m.get("runners") or []]
    return any(G.same_any(n, l["pick"]) for n in names)


# ---------- Matchbook exchange ----------
MB_BASE = "https://api.matchbook.com"
MB_TTL = 30 * 60
MB_SPORT_NAMES = {"football": "soccer", "tennis": "tennis", "rugby": "rugby union", "nrl": "rugby league",
                  "nba": "basketball", "ncaab": "basketball", "wnba": "basketball", "nfl": "american football",
                  "cfb": "american football", "nhl": "ice hockey", "mlb": "baseball"}

def price_matchbook(L, dates, report, cache_dir=None, http=None):
    import groupings as G
    user, pw = os.environ.get("MATCHBOOK_USERNAME"), os.environ.get("MATCHBOOK_PASSWORD")
    want = [l for l in L if not l.get("odds") and l["sport"] in MB_SPORT_NAMES]
    if not (user and pw) or not want:
        report["matchbook"] = "no key" if not (user and pw) else "no legs"; return
    cache_dir = _cache_dir(cache_dir)
    http = http or _http
    rep = {"calls": 0, "legs": len(want), "matched": 0}
    hdr = {"Accept": "application/json", "Content-Type": "application/json"}
    try:
        # in memory only, as Betfair's (never in the public repo's Actions cache)
        r = http(f"{MB_BASE}/bpapi/rest/security/session", {"username": user, "password": pw}, hdr, "POST"); rep["calls"] += 1
        if (r or {}).get("session-token"): hdr["session-token"] = r["session-token"]
        sports = _cached(os.path.join(cache_dir, "matchbook-sports.json"), 24 * 3600)
        if sports is None:
            sports = (http(f"{MB_BASE}/edge/rest/lookups/sports?per-page=200", None, hdr) or {}).get("sports") or []; rep["calls"] += 1
            _keep(os.path.join(cache_dir, "matchbook-sports.json"), sports)
    except Exception as e:
        report["matchbook"] = dict(rep, error=str(e)[:200]); return
    ids = {str(sp.get("name", "")).lower(): sp.get("id") for sp in sports}
    lo, hi = _window(dates)
    by_sport = {}
    for l in want:
        sid = ids.get(MB_SPORT_NAMES[l["sport"]])
        if sid: by_sport.setdefault(sid, []).append(l)
    for sid, legs in by_sport.items():
        path = os.path.join(cache_dir, f"matchbook-{sid}.json")
        events = _cached(path, MB_TTL)
        if events is None:
            try:
                q = urllib.parse.urlencode({"sport-ids": sid, "after": int(lo.timestamp()), "before": int(hi.timestamp()),
                                            "include-prices": "true", "price-depth": 1, "odds-type": "DECIMAL",
                                            "exchange-type": "back-lay", "per-page": 500})
                events = (http(f"{MB_BASE}/edge/rest/events?{q}", None, hdr) or {}).get("events") or []; rep["calls"] += 1
                _keep(path, events)
            except Exception as e:
                report.setdefault("errors", []).append(f"matchbook {sid}: {str(e)[:120]}"); continue
        for l in legs:
            if l.get("odds"): continue
            for ev in events:
                mk = next((m for m in ev.get("markets") or [] if m.get("market-type") in ("one_x_two", "money_line")), None)
                if not mk: continue
                runners = [r for r in mk.get("runners") or [] if str(r.get("name", "")).lower() != "draw"]
                if len(runners) != 2: continue
                a, b = runners[0].get("name"), runners[1].get("name")
                if not _match(l, a, b, G.parse(ev.get("start")), G): continue
                back = lambda r: next((p.get("odds") for p in r.get("prices") or [] if p.get("side") == "back"), None)
                pick = next((r for r in runners if G.same_any(r.get("name", ""), l["pick"])), None)
                if not pick or not back(pick): break
                other = next(r for r in runners if r is not pick)
                draw = next((r for r in mk.get("runners") or [] if str(r.get("name", "")).lower() == "draw"), None)
                _fill(l, G, float(back(pick)), back(other), back(draw) if draw else None,
                      "Matchbook exchange, best back price", G.read_at(path), "Matchbook")
                l["exchange"] = "matchbook"
                rep["matched"] += 1; break
    report["matchbook"] = rep


# ---------- SportsGameOdds, free Amateur plan ----------
SGO_BASE = "https://api.sportsgameodds.com/v2/events"
SGO_LEAGUES = {"nba": "NBA", "ncaab": "NCAAB", "nfl": "NFL", "cfb": "NCAAF", "nhl": "NHL", "mlb": "MLB"}
SGO_MONTH = 2400       # of the free 2,500 games ("objects") a month
SGO_TTL = 6 * 3600
SGO_HILL_IS_UK = False # True once its William Hill is shown to match the UK book's prices

def _american(s):
    try: x = float(str(s).replace("+", ""))
    except (TypeError, ValueError): return None
    return round(1 + (x / 100 if x > 0 else 100 / -x), 3) if x else None

def price_sgo(L, dates, report, cache_dir=None, fetch=None, now=None):
    import groupings as G
    key = os.environ.get("SGO_API_KEY")
    want = [l for l in L if not l.get("odds") and l["sport"] in SGO_LEAGUES]
    if not key or not want:
        report["sgo"] = "no key" if not key else "no legs"; return
    cache_dir = _cache_dir(cache_dir)
    fetch = fetch or (lambda u: _http(u))
    now = now or datetime.now(timezone.utc)
    led_path = os.path.join(cache_dir, "sgo-ledger.json")
    led = _cached(led_path, 40 * 86400) or {}
    if led.get("month") != now.strftime("%Y-%m"): led = {"month": now.strftime("%Y-%m"), "objects": 0}
    import calendar
    days_left = calendar.monthrange(now.year, now.month)[1] - now.day + 1
    rep = {"calls": 0, "objects": 0, "legs": len(want), "matched": 0}
    lo, hi = _window(dates)
    by_league = {}
    for l in want: by_league.setdefault(SGO_LEAGUES[l["sport"]], []).append(l)
    # leagues with the most Daily List games first; each spends from an even daily share
    for lg in sorted(by_league, key=lambda k: -sum(1 for l in by_league[k] if l.get("list"))):
        path = os.path.join(cache_dir, f"sgo-{lg}.json")
        events = _cached(path, SGO_TTL)
        if events is None:
            share = (SGO_MONTH - led["objects"]) / days_left
            if led["objects"] >= SGO_MONTH or rep["objects"] >= share:
                report.setdefault("sgoSkipped", []).append(lg); continue
            try:
                q = urllib.parse.urlencode({"leagueID": lg, "oddsAvailable": "true", "startsAfter": _iso(max(lo, now)),
                                            "startsBefore": _iso(hi), "limit": 100, "apiKey": key})
                d = fetch(f"{SGO_BASE}?{q}") or {}
                events = d.get("data") or []; rep["calls"] += 1
                rep["objects"] += len(events); led["objects"] += len(events)
                _keep(path, events)
            except Exception as e:
                report.setdefault("errors", []).append(f"sgo {lg}: {str(e)[:120]}"); continue
        for l in by_league[lg]:
            if l.get("odds"): continue
            for ev in events:
                th, ta = (ev.get("teams") or {}).get("home") or {}, (ev.get("teams") or {}).get("away") or {}
                hn = (th.get("names") or {}).get("long") or (th.get("names") or {}).get("medium")
                an = (ta.get("names") or {}).get("long") or (ta.get("names") or {}).get("medium")
                if not _match(l, hn, an, G.parse((ev.get("status") or {}).get("startsAt")), G): continue
                side = "home" if G.same_any(l["pick"], hn) else "away" if G.same_any(l["pick"], an) else None
                if not side: break
                odds = ev.get("odds") or {}
                mine = odds.get(f"points-{side}-game-ml-{side}") or odds.get(f"points-{side}-reg-ml-{side}") or {}
                opp_side = "away" if side == "home" else "home"
                theirs = odds.get(f"points-{opp_side}-game-ml-{opp_side}") or odds.get(f"points-{opp_side}-reg-ml-{opp_side}") or {}
                books = {b: _american(v.get("odds")) for b, v in (mine.get("byBookmaker") or {}).items() if v.get("available", True)}
                books = {b: o for b, o in books.items() if o and o > 1}
                if not books: break
                others = [o for o in (_american(v.get("odds")) for v in (theirs.get("byBookmaker") or {}).values()) if o and o > 1]
                avg = sum(books.values()) / len(books)
                top = max(books.items(), key=lambda kv: kv[1])
                _fill(l, G, avg, sum(others) / len(others) if others else None, None,
                      f"SportsGameOdds, average of {len(books)} bookmaker{'s' if len(books) != 1 else ''}", G.read_at(path), top[0])
                l.update(best=round(top[1], 2), books=len(books), sgoBooks={b: round(o, 2) for b, o in books.items()})
                if SGO_HILL_IS_UK and books.get("williamhill"):
                    l.setdefault("bookOdds", {})[G.CARD_BOOK] = round(books["williamhill"], 2)
                rep["matched"] += 1; break
    _keep(led_path, led)
    rep["monthObjects"] = led["objects"]
    report["sgo"] = rep
