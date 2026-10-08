#!/usr/bin/env python3
"""
NFL, MLB, NBA and rugby: one pipeline, one model, tested before it is shown.

    python3 sports.py --history              walk ESPN results into history-sports/ (first run is long)
    python3 sports.py --tune                 fit and test the model per sport, write sports.json
    python3 sports.py --build                price the next few days, write sports-data.js, archive
    python3 sports.py --score                grade the archive, write sports-record.js
    python3 sports.py --daily                --history (top-up only), --build, --score: what CI runs

Separate from football and tennis, which never import it.

The model
---------
Elo, per sport, keyed by ESPN's team id, so there is no name matching to go
wrong. A home side gets HFA points (none at a neutral venue). The update is
scaled by margin of victory where that helps (FiveThirtyEight's form), and a
team returning from an off-season (no game for OFFSEASON_DAYS) is pulled
REGRESS of the way back to 1500, because rosters change.

Every constant is fitted per sport on the season before last (FIT window) and
judged on the most recent one (CHECK window), which it never saw, with the
same paired bootstrap and gates as tune.py. Before any of that, the model has
to beat simply backing the home side, or the sport is not published.

A sport only puts games on the Daily List if its backtest earns it: calls at
its list threshold must have landed 78%+ in both windows, with at least 30
check-window calls. Otherwise the tab shows the sport and the list says why it
is absent. Rugby club, international and Super Rugby teams rate in separate
pools because they almost never meet.

Standard library only.
"""
import argparse, concurrent.futures as cf, json, math, os, random, sys, time, urllib.request
from datetime import date, datetime, timedelta, timezone
from bands import band_rate

HERE = os.path.dirname(os.path.abspath(__file__))
HIST_DIR = os.path.join(HERE, "history-sports")
PRED_DIR = os.path.join(HERE, "predictions-sports")
PARAMS = os.path.join(HERE, "sports.json")
DATA_JS = os.path.join(HERE, "sports-data.js")
RECORD = os.path.join(HERE, "sports-record.json")
RECORD_JS = os.path.join(HERE, "sports-record.js")

ESPN_HOSTS = ["https://site.api.espn.com", "https://site.web.api.espn.com"]
ESPN_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.espn.com/",
    "Origin": "https://www.espn.com",
}

HIST_START = date(2023, 7, 1)
FIT = (date(2024, 7, 1), date(2025, 7, 1))     # the season before last
CHECK = (date(2025, 7, 1), None)                # the most recent, up to today
OFFSEASON_DAYS = 90
MIN_GAMES = 8          # a team needs this many rated games before its number counts
WINDOW_DAYS = 7          # always reaches the coming weekend, when most rugby is played
RESCAN = 3

# Gates, as tune.py.
MIN_HOLDOUT, MAX_P_WORSE, MIN_GAIN = 250, 0.30, 0.0005
# The Daily List takes a sport's games from the lowest confidence at which its
# calls landed LIST_MIN_HIT or better in every test window holding at least
# LIST_MIN_N such calls (and at least one window must). Shared with football
# and tennis: every pick on the list landed four in five or better in testing
# (raised from three in four on 29 Sep 2026, Douglas's call).
LIST_THRESHOLDS = (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85)
LIST_MIN_HIT, LIST_MIN_N = 0.80, 30
RESERVE_MIN = 0.62   # the list's reserve floor, Firm, as football and tennis


def list_threshold(windows):
    for t in LIST_THRESHOLDS:
        ok, big = True, 0
        for w in windows:
            b = next((x for x in w if abs(x["from"] - t) < 1e-9), None)
            if b is None:
                ok = False
                break
            if b["n"] >= LIST_MIN_N:
                big += 1
                ok = ok and b["hit"] >= LIST_MIN_HIT
        if ok and big:
            return t
    return None
DEFAULTS = {"k": 20, "hfa": 50, "regress": 0.33, "mov": 1}
GRID = {"k": (8, 12, 16, 20, 25, 32, 40), "hfa": (0, 25, 50, 75, 100),
        "regress": (0.0, 0.25, 0.5), "mov": (0, 1)}

# A feed: an ESPN scoreboard path, the months it plays in, which weekdays to
# walk for history (rugby is almost all Friday to Sunday; asking for every day
# of a club season across six competitions would be thousands of empty calls),
# and the season types to skip (1 is preseason in the US leagues, but rugby
# labels its whole season type 1).
ALL_DAYS = (0, 1, 2, 3, 4, 5, 6)
WEEKEND = (4, 5, 6)
SPORTS = {
    "nfl": {"name": "NFL", "feeds": [
        {"path": "football/nfl", "label": "NFL", "pool": "nfl", "months": (9, 10, 11, 12, 1, 2),
         "days": ALL_DAYS, "skip": (1, 4)}]},
    "mlb": {"name": "Baseball", "feeds": [
        {"path": "baseball/mlb", "label": "MLB", "pool": "mlb", "months": (3, 4, 5, 6, 7, 8, 9, 10, 11),
         "days": ALL_DAYS, "skip": (1,)}]},
    "nba": {"name": "Basketball", "feeds": [
        {"path": "basketball/nba", "label": "NBA", "pool": "nba", "months": (10, 11, 12, 1, 2, 3, 4, 5, 6),
         "days": ALL_DAYS, "skip": (1,)}]},
    "rugby": {"name": "Rugby", "feeds": [
        {"path": "rugby/267979", "label": "Premiership", "pool": "club", "months": (9, 10, 11, 12, 1, 2, 3, 4, 5, 6), "days": WEEKEND, "skip": ()},
        {"path": "rugby/270557", "label": "URC", "pool": "club", "months": (9, 10, 11, 12, 1, 2, 3, 4, 5, 6), "days": WEEKEND, "skip": ()},
        {"path": "rugby/270559", "label": "Top 14", "pool": "club", "months": (8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6), "days": WEEKEND, "skip": ()},
        {"path": "rugby/271937", "label": "Champions Cup", "pool": "club", "months": (12, 1, 4, 5), "days": WEEKEND, "skip": ()},
        {"path": "rugby/272073", "label": "Challenge Cup", "pool": "club", "months": (12, 1, 4, 5), "days": WEEKEND, "skip": ()},
        {"path": "rugby/180659", "label": "Six Nations", "pool": "intl", "months": (2, 3), "days": WEEKEND, "skip": ()},
        {"path": "rugby/244293", "label": "Rugby Championship", "pool": "intl", "months": (7, 8, 9, 10), "days": WEEKEND, "skip": ()},
        {"path": "rugby/289234", "label": "Test match", "pool": "intl", "months": (6, 7, 8, 10, 11), "days": WEEKEND, "skip": ()},
        {"path": "rugby/164205", "label": "World Cup", "pool": "intl", "months": (9, 10), "days": ALL_DAYS, "skip": ()},
        {"path": "rugby/242041", "label": "Super Rugby", "pool": "sr", "months": (2, 3, 4, 5, 6), "days": WEEKEND, "skip": ()},
    ]},
    # Added 6 Oct 2026 from ESPN's free feeds. Each is tuned and gated like the
    # others: on the board once it beats backing the home side, on the Daily
    # List only once its backtest earns it.
    "nhl": {"name": "Ice hockey", "feeds": [
        {"path": "hockey/nhl", "label": "NHL", "pool": "nhl", "months": (10, 11, 12, 1, 2, 3, 4, 5, 6),
         "days": ALL_DAYS, "skip": (1,)}]},
    "cfb": {"name": "College football", "feeds": [
        {"path": "football/college-football", "label": "NCAA FBS", "pool": "cfb", "months": (8, 9, 10, 11, 12, 1),
         "days": ALL_DAYS, "skip": (1,)}]},
    "ncaab": {"name": "College basketball", "feeds": [
        # groups=50 is all of Division I; without it ESPN returns only a few featured games
        {"path": "basketball/mens-college-basketball", "label": "NCAA", "pool": "ncaab", "q": "&groups=50",
         "months": (11, 12, 1, 2, 3, 4), "days": ALL_DAYS, "skip": (1,)}]},
    # Their own sports, not feeds of the NBA and union rugby: those share one
    # set of fitted constants per sport, and adding games would move them.
    "wnba": {"name": "WNBA", "feeds": [
        {"path": "basketball/wnba", "label": "WNBA", "pool": "wnba", "months": (5, 6, 7, 8, 9, 10),
         "days": ALL_DAYS, "skip": (1,)}]},
    "nrl": {"name": "Rugby league", "feeds": [
        {"path": "rugby-league/3", "label": "NRL", "pool": "nrl", "months": (3, 4, 5, 6, 7, 8, 9, 10),
         "days": ALL_DAYS, "skip": ()}]},
}

TIERS = [(0.70, "Strong"), (0.62, "Firm"), (0.55, "Lean"), (0.0, "No read")]


def tier_of(p):
    for m, name in TIERS:
        if p >= m:
            return name


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------

def _day(path, d, errs, q=""):
    for host in ESPN_HOSTS:
        url = f"{host}/apis/site/v2/sports/{path}/scoreboard?dates={d:%Y%m%d}&limit=400{q}"
        try:
            req = urllib.request.Request(url, headers=ESPN_HEADERS)
            return json.loads(urllib.request.urlopen(req, timeout=25).read()).get("events") or []
        except Exception as e:
            errs.append(f"{path} {d}: {type(e).__name__} {e}")
    return None


# A completed flag does not mean the game was played to a result: these carry a
# partial or placeholder score and must never be graded or fed to the Elo.
NOT_PLAYED = ("STATUS_CANCELED", "STATUS_POSTPONED", "STATUS_ABANDONED",
              "STATUS_SUSPENDED", "STATUS_FORFEIT")


def _game(ev, feed):
    """One ESPN event -> a game dict, or None for anything unusable."""
    if (ev.get("season") or {}).get("type") in feed["skip"]:
        return None
    comp = (ev.get("competitions") or [{}])[0]
    sides = comp.get("competitors") or []
    home = next((c for c in sides if c.get("homeAway") == "home"), None)
    away = next((c for c in sides if c.get("homeAway") == "away"), None)
    if not home or not away:
        return None
    ht, at = home.get("team") or {}, away.get("team") or {}
    if not ht.get("id") or not at.get("id"):
        return None
    st = (comp.get("status") or {}).get("type") or {}
    final = bool(st.get("completed")) and st.get("name") not in NOT_PLAYED
    hs = as_ = None
    if final:
        try:
            hs, as_ = int(float(home.get("score"))), int(float(away.get("score")))
        except (TypeError, ValueError):
            final = False
    return {"id": ev.get("id"), "when": comp.get("date") or ev.get("date"),
            "feed": feed["path"], "label": feed["label"], "pool": feed["pool"],
            "h": ht["id"], "hn": ht.get("displayName") or ht.get("name"),
            "a": at["id"], "an": at.get("displayName") or at.get("name"),
            "neutral": bool(comp.get("neutralSite")), "state": st.get("state"),
            "final": final, "hs": hs, "as": as_}


def _hist_path(feed):
    return os.path.join(HIST_DIR, feed["path"].replace("/", "_") + ".json")


def load_history(feed):
    try:
        doc = json.load(open(_hist_path(feed)))
    except Exception:
        return {}, None
    return {g["id"]: g for g in doc["games"]}, (date.fromisoformat(doc["through"]) if doc.get("through") else None)


def walk_history(feed, until=None, sleep=0.08, log=None):
    """Completed games from HIST_START (or the last walk, less RESCAN days)."""
    games, through = load_history(feed)
    until = until or (date.today() - timedelta(days=1))
    d = max(HIST_START, through - timedelta(days=RESCAN)) if through else HIST_START
    asked = 0
    while d <= until:
        if d.month in feed["months"] and d.weekday() in feed["days"]:
            errs = []
            evs = _day(feed["path"], d, errs, feed.get("q", ""))
            asked += 1
            if evs is None:
                if log is not None:
                    log.append(errs[0])
            else:
                for ev in evs:
                    g = _game(ev, feed)
                    if g and g["final"]:
                        games[g["id"]] = g
            time.sleep(sleep)
        d += timedelta(days=1)
    os.makedirs(HIST_DIR, exist_ok=True)
    tmp = _hist_path(feed) + ".tmp"
    json.dump({"through": until.isoformat(),
               "games": sorted(games.values(), key=lambda g: g["when"])},
              open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, _hist_path(feed))
    return len(games), asked


def all_feeds():
    for sport, cfg in SPORTS.items():
        for f in cfg["feeds"]:
            yield sport, f


def _same_game(g):
    # ESPN sometimes carries one match under two event ids (Racing 92 v
    # Perpignan, 3 Oct 2026). Counted twice it would move both ratings twice.
    # Keyed to the minute, not the day: a baseball doubleheader is the same
    # two teams twice on one date, at different times, and both games count.
    return (g["pool"], g["h"], g["a"], g["when"][:16])


def history_for(sport):
    games = {}
    for f in SPORTS[sport]["feeds"]:
        for g in load_history(f)[0].values():
            games.setdefault(_same_game(g), g)
    return sorted(games.values(), key=lambda g: g["when"])


# ---------------------------------------------------------------------------
# model
# ---------------------------------------------------------------------------

def p_home(eh, ea, hfa, neutral):
    return 1.0 / (1.0 + 10 ** (-((eh - ea) + (0 if neutral else hfa)) / 400.0))


class Elo:
    def __init__(self, p):
        self.p = p
        self.r = {}       # (pool, team id) -> [elo, last date, games]

    def get(self, pool, team, when):
        k = (pool, team)
        e = self.r.get(k)
        if e is None:
            e = self.r[k] = [1500.0, when, 0]
        elif (datetime.fromisoformat(when[:10]) - datetime.fromisoformat(e[1][:10])).days > OFFSEASON_DAYS:
            e[0] = 1500 + (e[0] - 1500) * (1 - self.p["regress"])
            e[1] = when   # regress once per break: predict() is called again for later games
        return e

    def predict(self, g):
        eh = self.get(g["pool"], g["h"], g["when"])
        ea = self.get(g["pool"], g["a"], g["when"])
        return p_home(eh[0], ea[0], self.p["hfa"], g["neutral"]), eh, ea

    def update(self, g):
        ph, eh, ea = self.predict(g)
        s = 1.0 if g["hs"] > g["as"] else (0.0 if g["hs"] < g["as"] else 0.5)
        m = 1.0
        if self.p["mov"] and g["hs"] != g["as"]:
            margin = abs(g["hs"] - g["as"])
            diff = (eh[0] - ea[0]) if s == 1.0 else (ea[0] - eh[0])
            m = math.log(margin + 1) * 2.2 / (max(diff, -400) * 0.001 + 2.2)
        delta = self.p["k"] * m * (s - ph)
        eh[0] += delta
        ea[0] -= delta
        for e in (eh, ea):
            e[1] = g["when"]
            e[2] += 1
        return ph


def replay(games, p):
    """Walk every game in order. Returns (elo, [(game, p_home, warm)])."""
    elo = Elo(p)
    out = []
    for g in games:
        eh = elo.r.get((g["pool"], g["h"]))
        ea = elo.r.get((g["pool"], g["a"]))
        warm = bool(eh and ea and eh[2] >= MIN_GAMES and ea[2] >= MIN_GAMES)
        ph = elo.update(g)
        out.append((g, ph, warm))
    return elo, out


def in_window(g, win):
    d = date.fromisoformat(g["when"][:10])
    return win[0] <= d and (win[1] is None or d < win[1])


def _logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def calibrate(p, cal):
    """Raw Elo probability -> calibrated. cal = {"a", "b"}: logistic in the
    log-odds, two parameters, as football's temperature line. None = as is."""
    if not cal:
        return p
    z = cal["a"] + cal["b"] * _logit(p)
    return 1 / (1 + math.exp(-max(min(z, 30), -30)))


def fit_calibration(preds, win):
    """Newton's method for (a, b) on home-win, warm decided games in a window."""
    xs = [(_logit(ph), 1 if g["hs"] > g["as"] else 0) for g, ph, warm in preds
          if warm and in_window(g, win) and g["hs"] != g["as"]]
    a, b = 0.0, 1.0
    for _ in range(30):
        ga = gb = haa = hab = hbb = 0.0
        for x, y in xs:
            p = 1 / (1 + math.exp(-max(min(a + b * x, 30), -30)))
            e, v = p - y, p * (1 - p)
            ga += e; gb += e * x
            haa += v; hab += v * x; hbb += v * x * x
        det = haa * hbb - hab * hab
        if not det:
            break
        da, db = (hbb * ga - hab * gb) / det, (haa * gb - hab * ga) / det
        a, b = a - da, b - db
        if abs(da) + abs(db) < 1e-9:
            break
    return {"a": round(a, 4), "b": round(b, 4)}


def losses(preds, win, cal=None):
    """Per-game binary log loss on home-win, and pick hits, for warm games
    in a window. Draws are excluded from the loss and count as misses."""
    ll, rows = [], []
    for g, ph, warm in preds:
        if not warm or not in_window(g, win):
            continue
        ph = calibrate(ph, cal)
        y = 1 if g["hs"] > g["as"] else (0 if g["hs"] < g["as"] else None)
        conf = max(ph, 1 - ph)
        pick_home = ph >= 0.5
        hit = y is not None and (y == 1) == pick_home
        rows.append((conf, hit, g))
        if y is not None:
            ll.append(-math.log(max(ph if y else 1 - ph, 1e-12)))
    return ll, rows


def paired(a, b, reps=1500, seed=17):
    rng = random.Random(seed)
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    means = [sum(diff[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    mu = sum(diff) / n
    sd = math.sqrt(sum((m - mu) ** 2 for m in means) / len(means))
    return mu, sd, sum(1 for m in means if m > 0) / len(means)


def bands(rows):
    out = []
    for t in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85):
        g = [r for r in rows if r[0] >= t]
        if g:
            out.append({"from": t, "n": len(g), "hit": round(sum(r[1] for r in g) / len(g), 4),
                        "quoted": round(sum(r[0] for r in g) / len(g), 4)})
    return out


def tune_sport(sport, verbose=True):
    games = [g for g in history_for(sport) if g["final"]]
    if not games:
        return None
    say = print if verbose else (lambda *a, **k: None)
    say(f"\n{SPORTS[sport]['name']}: {len(games)} games on file")

    def score(p, win):
        return losses(replay(games, p)[1], win)

    best = None
    for k in GRID["k"]:
        for hfa in GRID["hfa"]:
            for reg in GRID["regress"]:
                for mov in GRID["mov"]:
                    p = {"k": k, "hfa": hfa, "regress": reg, "mov": mov}
                    ll, _ = score(p, FIT)
                    if ll and (best is None or sum(ll) / len(ll) < best[0]):
                        best = (sum(ll) / len(ll), p)
    fitted = best[1]
    ll_fit_c, rows_fit = score(fitted, FIT)
    ll_new, rows_chk = score(fitted, CHECK)
    ll_def, _ = score(DEFAULTS, CHECK)
    n = len(ll_new)

    # 1. does the model beat backing the home side at the fit window's home rate?
    fit_y = [1 if g["hs"] > g["as"] else 0 for (_, _, g) in rows_fit if g["hs"] != g["as"]]
    hr = sum(fit_y) / max(len(fit_y), 1)
    chk_y = [1 if g["hs"] > g["as"] else 0 for (_, _, g) in rows_chk if g["hs"] != g["as"]]
    base = [-math.log(hr if y else 1 - hr) for y in chk_y]
    m_b, sd_b, pw_b = paired(ll_new, base) if n else (0, 0, 1)
    beats_home = n >= MIN_HOLDOUT and pw_b <= MAX_P_WORSE and -m_b >= MIN_GAIN

    # 2. is the fitted set worth shipping over the defaults?
    m_d, sd_d, pw_d = paired(ll_new, ll_def) if n else (0, 0, 1)
    use_fitted = n >= MIN_HOLDOUT and pw_d <= MAX_P_WORSE and -m_d >= MIN_GAIN
    params = fitted if use_fitted else DEFAULTS
    if not use_fitted:
        _, rows_fit = score(params, FIT)
        ll_new, rows_chk = score(params, CHECK)

    # 3. calibration: does a two-parameter curve, fitted on the fit window,
    # make the quoted numbers truer on the check window? Same gates.
    preds = replay(games, params)[1]
    cal = fit_calibration(preds, FIT)
    ll_cal, rows_chk_cal = losses(preds, CHECK, cal)
    m_c, sd_c, pw_c = paired(ll_cal, ll_new) if n else (0, 0, 1)

    # Honesty guard: a better log loss overall is not enough if the strongest
    # calls end up quoted above what they land (rugby, Sep 2026: 85% quoted,
    # 81% landed). The quoted-minus-landed gap at 65%+ may not widen by more
    # than a point.
    def top_gap(rows):
        g = [r for r in rows if r[0] >= 0.65]
        return abs(sum(r[0] for r in g) / len(g) - sum(r[1] for r in g) / len(g)) if g else 0.0
    gap_raw, gap_cal = top_gap(rows_chk), top_gap(rows_chk_cal)
    use_cal = (n >= MIN_HOLDOUT and pw_c <= MAX_P_WORSE and -m_c >= MIN_GAIN
               and gap_cal <= gap_raw + 0.01)
    if use_cal:
        ll_new, rows_chk = ll_cal, rows_chk_cal
        rows_fit = losses(preds, FIT, cal)[1]
    say(f"  calibration a={cal['a']} b={cal['b']}: {m_c:+.4f}, p(worse) {pw_c:.2f}, "
        f"65%+ gap {gap_raw:.3f} -> {gap_cal:.3f} -> {'applied' if use_cal else 'not applied'}")

    b_fit, b_chk = bands(rows_fit), bands(rows_chk)
    list_min = list_threshold([b_fit, b_chk])

    acc = sum(r[1] for r in rows_chk) / max(len(rows_chk), 1)
    say(f"  fitted {fitted} (fit window log loss {best[0]:.4f})")
    say(f"  check window: {n} games, log loss {sum(ll_new)/max(n,1):.4f}, picked the winner {acc:.1%}")
    say(f"  vs backing home ({hr:.1%}): {m_b:+.4f}, p(worse) {pw_b:.2f} -> {'PASS' if beats_home else 'FAIL'}")
    say(f"  fitted vs defaults: {m_d:+.4f}, p(worse) {pw_d:.2f} -> {'fitted' if use_fitted else 'defaults'} shipped")
    for b in b_chk:
        say(f"    {b['from']:.0%}+  n={b['n']:4}  landed {b['hit']:.1%}  quoted {b['quoted']:.1%}")
    say(f"  Daily List threshold: {f'{list_min:.0%}' if list_min else 'none, backtest does not earn a place'}")
    return {"params": params, "fittedParams": fitted, "usedFitted": use_fitted,
            "games": len(games), "check": {"n": n, "logLoss": round(sum(ll_new) / max(n, 1), 4),
                                           "accuracy": round(acc, 4), "homeRate": round(hr, 4),
                                           "vsHome": round(m_b, 4), "pWorseVsHome": round(pw_b, 3)},
            "publish": beats_home, "listMin": list_min,
            "cal": cal if use_cal else None, "calTested": {"a": cal["a"], "b": cal["b"],
                                                           "delta": round(m_c, 4), "pWorse": round(pw_c, 3),
                                                           "topGapRaw": round(gap_raw, 4), "topGapCal": round(gap_cal, 4)},
            "bandsFit": b_fit, "bandsCheck": b_chk,
            "windows": {"fit": [FIT[0].isoformat(), FIT[1].isoformat()],
                        "check": [CHECK[0].isoformat(), None]}}


# ---------------------------------------------------------------------------
# build, archive, score
# ---------------------------------------------------------------------------

def load_params():
    try:
        return json.load(open(PARAMS))
    except Exception:
        return {}


def upcoming(sport, start, days):
    out, errs = [], []
    for f in SPORTS[sport]["feeds"]:
        seen = set()
        for i in range(days):
            d = start + timedelta(days=i)
            if d.month not in f["months"]:
                continue
            for ev in _day(f["path"], d, errs, f.get("q", "")) or []:
                g = _game(ev, f)
                if g and g["state"] == "pre" and g["id"] not in seen and _same_game(g) not in seen:
                    seen.update((g["id"], _same_game(g)))
                    out.append(g)
    return out


def accuracy_for(conf, bands_chk):
    """How calls at this level did on games the model never saw: its own
    band, not every call above it (bands.band_rate, 6 Oct 2026)."""
    return band_rate(conf, bands_chk)


def _result(g, team):
    mine, theirs = (g["hs"], g["as"]) if g["h"] == team else (g["as"], g["hs"])
    return "W" if mine > theirs else ("L" if mine < theirs else "D"), mine, theirs


def form(games, team, n=5):
    """The last n results, newest first."""
    out = []
    for g in reversed(games[-n:]):
        r, mine, theirs = _result(g, team)
        home = g["h"] == team
        out.append({"r": r, "score": f"{mine}-{theirs}", "opp": g["an"] if home else g["hn"],
                    "home": home, "date": g["when"][:10]})
    return out


def record(games, team):
    """Won-lost(-drawn) since the team's last off-season break."""
    cur = []
    for g in games:
        if cur and (datetime.fromisoformat(g["when"][:10])
                    - datetime.fromisoformat(cur[-1]["when"][:10])).days > OFFSEASON_DAYS:
            cur = []
        cur.append(g)
    w = sum(1 for g in cur if _result(g, team)[0] == "W")
    l = sum(1 for g in cur if _result(g, team)[0] == "L")
    d = len(cur) - w - l
    return {"w": w, "l": l, "d": d}


def head_to_head(games, team, opp, n=3):
    out = []
    for g in reversed(games):
        if opp in (g["h"], g["a"]):
            out.append({"date": g["when"][:10], "home": g["hn"], "away": g["an"],
                        "score": f"{g['hs']}-{g['as']}"})
            if len(out) == n:
                break
    return out


def build(start=None):
    P = load_params()
    start = start or date.today()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {"generated": now, "from": start.isoformat(), "sports": {}}
    archive = []
    for sport, cfg in SPORTS.items():
        sp = P.get(sport)
        entry = {"name": cfg["name"], "published": bool(sp and sp.get("publish")),
                 "listMin": sp.get("listMin") if sp else None,
                 "check": sp.get("check") if sp else None,
                 "bands": sp.get("bandsCheck") if sp else None, "games": []}
        payload["sports"][sport] = entry
        if not entry["published"]:
            continue
        played = [g for g in history_for(sport) if g["final"]]
        elo, _ = replay(played, sp["params"])
        by_team = {}
        for g in played:
            by_team.setdefault((g["pool"], g["h"]), []).append(g)
            by_team.setdefault((g["pool"], g["a"]), []).append(g)
        for g in upcoming(sport, start, WINDOW_DAYS):
            eh = elo.r.get((g["pool"], g["h"]))
            ea = elo.r.get((g["pool"], g["a"]))
            if not eh or not ea or eh[2] < MIN_GAMES or ea[2] < MIN_GAMES:
                continue   # a team without enough history is not priced, as football
            raw, eh, ea = elo.predict(g)
            ph = calibrate(raw, sp.get("cal"))
            conf = max(ph, 1 - ph)
            row = {"id": g["id"], "sport": sport, "label": g["label"], "when": g["when"],
                   "home": g["hn"], "away": g["an"], "neutral": g["neutral"],
                   "pHome": round(ph, 4), "pick": g["hn"] if ph >= 0.5 else g["an"],
                   "confidence": round(conf, 4), "tier": tier_of(conf),
                   "eloH": round(eh[0]), "eloA": round(ea[0]), "gamesH": eh[2], "gamesA": ea[2],
                   "hfa": 0 if g["neutral"] else sp["params"]["hfa"],
                   "accuracy": accuracy_for(conf, sp.get("bandsCheck")),
                   "formH": form(by_team.get((g["pool"], g["h"]), []), g["h"]),
                   "formA": form(by_team.get((g["pool"], g["a"]), []), g["a"]),
                   "recordH": record(by_team.get((g["pool"], g["h"]), []), g["h"]),
                   "recordA": record(by_team.get((g["pool"], g["a"]), []), g["a"]),
                   "h2h": head_to_head(by_team.get((g["pool"], g["h"]), []), g["h"], g["a"]),
                   "list": bool(entry["listMin"] and conf >= entry["listMin"]),
                   # the list's reserve: a sport with a list place, below its
                   # bar, Firm or better (build.RESERVE_MIN)
                   "reserve": bool(entry["listMin"] and RESERVE_MIN <= conf < entry["listMin"])}
            entry["games"].append(row)
            archive.append({**row, "published": now})
        entry["games"].sort(key=lambda r: r["when"])

    with open(DATA_JS, "w") as f:
        f.write("window.__SPORTS_DATA__=" + json.dumps(payload, separators=(",", ":")) + ";")
    if archive:
        os.makedirs(PRED_DIR, exist_ok=True)
        path = os.path.join(PRED_DIR, f"{now[:10]}.json")
        try:
            old = {r["id"]: r for r in json.load(open(path))}
        except Exception:
            old = {}
        for r in archive:
            old[r["id"]] = r
        json.dump(list(old.values()), open(path, "w"), separators=(",", ":"))
    n = sum(len(e["games"]) for e in payload["sports"].values())
    print(f"sports: {n} games priced, " + ", ".join(
        f"{e['name']} {len(e['games'])}{'' if e['published'] else ' (not published)'}"
        for e in payload["sports"].values()), file=sys.stderr)


def settle(r, g):
    """The graded row for archived pick r against final game g, or None for a tie.

    A tie is void: the pick is a two-way call (pHome) and neither side can be
    right. Counting it a miss understated accuracy (2 of 52 graded on 5 Oct 2026)."""
    if g["hs"] == g["as"]:
        return None
    winner = g["hn"] if g["hs"] > g["as"] else g["an"]
    return {**r, "score": [g["hs"], g["as"]], "winner": winner, "ok": winner == r["pick"]}


def graded_games():
    """Archived picks graded against results already walked into
    history-sports/: (graded rows, void picks). Only the latest price
    published before the game started counts."""
    results = {}
    for _, f in all_feeds():
        results.update(load_history(f)[0])
    best = {}
    if os.path.isdir(PRED_DIR):
        for name in sorted(os.listdir(PRED_DIR)):
            for r in json.load(open(os.path.join(PRED_DIR, name))):
                if r["published"][:16] >= r["when"][:16]:
                    continue   # published after the start: proves nothing
                if r["id"] not in best or r["published"] > best[r["id"]]["published"]:
                    best[r["id"]] = r
    graded, void = [], []
    for gid, r in best.items():
        g = results.get(gid)
        if not g or not g["final"]:
            continue
        row = settle(r, g)
        if row is None:
            void.append({**r, "score": [g["hs"], g["as"]]})
            continue
        graded.append(row)
    return graded, void


def score():
    """Grade archived picks, write sports-record.js."""
    graded, voids = graded_games()
    void = len(voids)

    def summ(rows):
        if not rows:
            return None
        return {"n": len(rows), "correct": sum(x["ok"] for x in rows),
                "accuracy": round(sum(x["ok"] for x in rows) / len(rows), 4),
                "expected": round(sum(x["confidence"] for x in rows) / len(rows), 4)}

    by_date = {}
    for r in graded:
        by_date.setdefault(r["when"][:10], []).append(r)
    out = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "void": void,
           "overall": summ(graded),
           "bySport": {s: summ([r for r in graded if r["sport"] == s]) for s in SPORTS},
           "list": summ([r for r in graded if r["list"]]),
           "reserve": summ([r for r in graded if r.get("reserve")]),
           "reserveTiers": {t: summ([r for r in graded if r.get("reserve") and r["tier"] == t])
                            for t in ("Strong", "Firm")},
           "days": [{"date": d, **summ(by_date[d]),
                     "games": sorted(by_date[d], key=lambda r: -r["confidence"])}
                    for d in sorted(by_date, reverse=True)[:14]]}
    json.dump(out, open(RECORD, "w"), separators=(",", ":"))
    with open(RECORD_JS, "w") as f:
        f.write("window.__SPORTS_RECORD__=" + json.dumps(out, separators=(",", ":")) + ";")
    o = out["overall"]
    print(f"sports: {o['n'] if o else 0} graded, {void} tied (void)", file=sys.stderr)


def history(workers=6):
    log = []

    def one(item):
        sport, f = item
        n, asked = walk_history(f, log=log)
        return f"{sport}/{f['label']}: {n} games on file ({asked} days asked)"

    with cf.ThreadPoolExecutor(workers) as ex:
        for line in ex.map(one, list(all_feeds())):
            print("  " + line, file=sys.stderr)
    for line in log[:8]:
        print(f"    espn {line}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", action="store_true")
    ap.add_argument("--tune", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--daily", action="store_true")
    ap.add_argument("--only", help="comma-separated sports")
    args = ap.parse_args()
    if args.only:
        keep = set(args.only.split(","))
        for s in list(SPORTS):
            if s not in keep:
                SPORTS.pop(s)
    if args.history or args.daily:
        history()
    if args.tune:
        P = load_params()
        for s in SPORTS:
            v = tune_sport(s)
            if v:
                P[s] = v
        P["generated"] = date.today().isoformat()
        json.dump(P, open(PARAMS, "w"), indent=1)
    if args.build or args.daily:
        build()
    if args.score or args.daily:
        score()
    if not any((args.history, args.tune, args.build, args.score, args.daily)):
        ap.error("nothing to do")


if __name__ == "__main__":
    main()
