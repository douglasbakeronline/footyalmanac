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
to keep out legs the market rates lower than the model does. The Daily List is
untouched.

Which probability a leg carries
-------------------------------
Every pick on the site already says how often calls at its level landed in
testing ("86% landed"). A leg's chance is the lowest of that tested rate, the
model's own number and the bookmaker's fair chance (1 / price, less the
book's margin; see honest()):

    p_leg = min(hit, p_model, fair)

What a leg must be (21 Oct 2026, Douglas: groups built to land, nothing risky)
------------------------------------------------------------------------------
  - football or rugby (GROUP_SPORTS), a win pick, priced by a bookmaker
  - tested rate of at least LEG_MIN over at least MIN_N tested games
  - the model's number AND the bookmaker's fair chance both LEG_MIN or more
  - the model no more than MAX_ABOVE_BOOK above the bookmaker: where the model
    rated a leg 5+ points above the market it landed 70% (53 football legs,
    4-21 Oct) against 82% where it sat at or below the market
  - football: nothing the Daily List would exclude for blindness. Celtic's
    Law, unrated, thin history, new competition, unreplayed cup, step 3 and
    under-21 games are all out; only "on the list" or "under the list bar"
    remain (CLEAN_WHY). Flagged 65-70% calls landed 64% live against 70%.

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

How a group is chosen (21 Oct 2026)
-----------------------------------
Two kinds only, built in this order each day:
  Double  two legs, combined chance at least 60%
  Treble  three legs, combined chance at least 50%
In each, the legs with the highest joint chance (a small nudge toward legs on
the Daily List), one leg per game, no more than two from one competition.
Then a second ("alternative") Double and Treble from the legs left, each held
to the same floor. When nothing clears a floor there is no group: sitting a
day out is the rule, not a fault. No game used twice in a day.

Days ahead and the re-check (21 Oct 2026, Douglas)
--------------------------------------------------
Groups are built for today and the next DAYS_AHEAD (3) UK days. Every build
(six a day, deploy.yml) first reads the groups the last build published
(previous(): the local groupings.json or the published copy, the newer) and
re-checks each one against this build's board and prices (recheck()):

  holding      every leg is still a clean pick on the same side, priced, and
               passes safe_leg at today's price; the group still clears its
               floor and odds range. It keeps its place, so a group someone
               has placed does not reshuffle under them, even if a slightly
               stronger one has appeared.
  replacement  it failed. The reasons go in the day's "log" in plain words
               (leg_fault()) and the slot is rebuilt from the legs left.
  new          the slot was empty last build, or this is its first.
  underway     a leg has kicked off; kept as published, never re-priced.

Each leg carries firstOdds, its price when the group was first published, so
the page can show the drift. The record is unchanged: it is still the first
build of each UK day (archive()), whatever was shown in the days before.
Prices for games three days out are thinner (fewer bookmakers have opened
them), so far days fill in as the week goes on.

The five-leg Steady, Balanced and Stretch groups (4-20 Oct) and the 1.5-2.5
Banker (19-20 Oct) are retired. Their rule forced a 1.30-1.60 leg and, above
Steady, a 1.60+ leg into every group; those legs landed 61-70% and 47%, and
the groups landed 11 of 58 (19%). They stay in the record under their names.

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
# 21 Oct 2026, Douglas: groups that land, not groups that pay. Name, legs,
# lowest combined chance, and combined odds range (a sanity range only: legs
# at LEG_MIN or better cannot pay much). Built in this order.
GROUP_KINDS = [("Double", 2, 0.60, 1.10, 3.0), ("Treble", 3, 0.40, 1.20, 3.5)]
# 22 Oct 2026, Douglas: "make all groups return at least double the stake".
# Every group's combined price must be MIN_RETURN or more. Two strict legs
# (75%+ on every read) pay about 1.6 at most, so a strict Double cannot
# reach it; a strict Treble can (three ~78% legs pay about 2.0), so its
# floor drops from 50% to 40%. At 2.00 the bookmakers' own chance is under
# 50% before their margin, so no group can honestly be quoted above that.
MIN_RETURN = 2.0
BANDS = [(n, lo, hi) for n, _, _, lo, hi in GROUP_KINDS]
LEGS_IN = {n: k for n, k, _, _, _ in GROUP_KINDS}
MIN_CHANCE = {n: f for n, _, f, _, _ in GROUP_KINDS}
RISK = {"Double": "Lowest risk", "Treble": "Low risk", "Wider Double": "Higher risk", "Wider Treble": "Higher risk",
        "Wider Fourfold": "Higher risk"}
# Retired kinds, kept so the record still tallies them under their own names.
RETIRED = ["Banker", "Steady", "Balanced", "Stretch"]
LEG_MIN = 0.75          # tested rate, model and bookmaker's fair chance, each
MAX_ABOVE_BOOK = 0.05   # the model may sit at most this far above the market
CLEAN_WHY = (None, "below")   # football: on the Daily List, or off it only for the bar
LIST_NUDGE = 0.02       # per leg on the Daily List: 78% landed v 69% off it, 4-21 Oct
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
MIN_N, MIN_HIT = 30, 0.75   # 0.65 until 21 Oct 2026
# 21 Oct 2026, Douglas: groups for today and the next three UK days, each
# re-checked on every build. Until then today and tomorrow only.
DAYS_AHEAD = 3
# 22 Oct 2026, Douglas: at least three groups every day. When the strict
# Double and Treble cannot make three, "Wider" groups fill the gap from legs
# one step down: tested rate, model and bookmaker all 65%+, the model no more
# than WIDE_ABOVE_BOOK above the market; failing that, Daily List picks with
# no bookmaker price (an estimated price, marked). Labelled "Higher risk",
# graded under their own names, never mixed into the strict record.
# 25 Oct 2026, Douglas: "only show what qualifies". The weekend's losses came
# from forced, weaker picks, so Wider groups no longer fill a day to three:
# a day with no qualifying group shows none. Wider kinds stay defined so the
# record keeps grading the ones already published.
MIN_GROUPS = 0
WIDE_KINDS = [("Wider Double", 2, 0.40, 1.10, 3.5), ("Wider Treble", 3, 0.30, 1.20, 4.5),
              # 22 Oct 2026: at 2.00+ the strongest picks (80%+) are too short to
              # group in threes (three pay ~1.69), so four of them make one: ~2.0,
              # landing ~41%, as often as a Treble of 75% picks.
              ("Wider Fourfold", 4, 0.30, 1.20, 6.0)]
WIDE_MIN = 0.65
WIDE_ABOVE_BOOK = 0.08
WIDE_EST_MIN = 0.75     # an unpriced leg: Daily List, tested rate and model 75%+
WIDE_BANDS = [(n, lo, hi) for n, _, _, lo, hi in WIDE_KINDS]
# 24 Oct 2026, Douglas: "a way of surfacing predictions that have the best
# odds of multiplying a stake ... still some level of confidence". The
# Multipliers: for a target return (3x, 5x), the 2-4 legs with the highest
# combined chance whose combined price reaches it. Evidence, 909 archived
# football picks with a pre-kick-off market price (11 Sep - 24 Oct):
#  - the market's chance beats the model's on log loss (0.979 v 1.013), and
#    where the model sat 5+ points above the market its picks landed at the
#    market's rate, not the model's (47% at +5-10, 42% at +10)
#  - clean legs priced 1.30-1.85 with the model no more than 5 points above
#    the market (n=191) landed 65.4% against 58.5% fair; profit per unit
#    +3.1%, 90% interval -5.9% to +12.6% (no proven edge)
# So a Multiplier leg's chance is the bookmakers' fair chance (1/price less
# the margin), the model is a veto, and a leg is priced 1.30-1.90 (the range
# the evidence covers) with the market giving it 45%+. Shorter legs (1/20) are left out: they add almost
# nothing to the price and still carry the margin. Fewer, longer legs beat
# many short ones for the same return, because each leg adds the margin
# again; the chooser maximises combined chance, so it finds that by itself.
# All sports since the evening of 24 Oct 2026 (Douglas). Only football was tested
# at these prices; the chance quoted is the bookmakers' own, so it holds for any
# sport, but the archive evidence above is football only.
# 24 Oct 2026 evening, Douglas: "at least 2-3 groups per day, at least 3
# teams in each group ... all picks must be likely to come in". So up to
# MULT_PER_DAY Multipliers a day, each three or four picks the bookmakers
# rate 60%+ (MULT_FAIR_MIN), paying MULT_KINDS' lowest price or more. On the
# archive, legs at 60%+ fair in this range landed 76.1% (n=67, fair 64.8%).
# Three such picks pay about 3x and land about one time in four.
# (name, lowest combined price, highest, lowest combined chance)
MULT_KINDS = [("Multiplier", 2.8, 5.0, 0.20)]
MULT_PER_DAY = 3
MULT_LEGS = (3, 4)
MULT_SPORTS = None        # every sport (Douglas, 24 Oct 2026 evening); a set limits it
MULT_ODDS = (1.30, 1.90)   # a leg's own price range: the range the evidence covers
MULT_FAIR_MIN = 0.60       # the bookmakers' fair chance on the pick: likely to come in
MULT_MODEL_MIN = 0.40      # the model must not think the pick unlikely
MULT_ABOVE_BOOK = 0.05     # and must not sit more than this above the market
MULT_POOL = 24
MULT_RULE = 2      # 2: three a day, 3-4 picks, 60%+ each (24 Oct 2026 evening)
RISK.update({n: "Higher return" for n, _, _, _ in MULT_KINDS})
MIN_CHANCE.update({n: f for n, _, _, f in MULT_KINDS})
MULT_RANGE = {n: (lo, hi) for n, lo, hi, _ in MULT_KINDS}
# Admission to the leg pool: a tested band with MIN_N games behind it. The
# strict and Wider gates (safe_leg, wide_leg) still require their own tested
# rate (pTested, which is min(tested rate, model)), so lowering this changes
# nothing for them; it lets the Multipliers see mid-priced picks.
ADMIT_MIN = 0.0
LEGS_IN.update({n: k for n, k, _, _, _ in WIDE_KINDS})
MIN_CHANCE.update({n: f for n, _, f, _, _ in WIDE_KINDS})
RANGE = {n: (lo, hi) for n, lo, hi in BANDS + WIDE_BANDS}
# Where the last build's groups are read from, so this build can re-check
# them. The CI workspace starts clean, so the published copy is the one that
# exists there; a local run also has its own groupings.json. The newer wins.
PUBLISHED = "https://douglasbakeronline.github.io/footyalmanac/groupings.json"
LOG_KEEP = 12           # replacement notes kept per day
UA ={"User-Agent": "Mozilla/5.0 (footyalmanac groupings)"}

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

def leg_p(p, acc, min_hit=None):
    """A leg's chance: its band's tested rate, never above the model's own
    number. Until 19 Oct 2026 it was the tested rate pulled toward the
    model's number, which is the side that runs high at the top end (a 90%
    pick with a 77% tested rate was quoted 83%); legs landed 73.1% against
    79.8% quoted, 5-18 Oct."""
    if not acc or not acc.get("n") or acc.get("hit") is None: return None
    if acc["n"] < MIN_N or acc["hit"] < (MIN_HIT if min_hit is None else min_hit): return None
    return min(acc["hit"], p)

# ---------- the board ----------
def tennis_placeholder(when):
    """ESPN's stand-in time for a match with no order of play yet: exactly
    midnight in New York."""
    t = parse(when)
    if not t: return False
    ny = t.astimezone(ZoneInfo("America/New_York"))
    return ny.hour == 0 and ny.minute == 0

def tennis_starts(days=21):
    """Each tournament's usual first start (UTC "HH:MM"): the earliest real
    time it has used over the last `days` days in history-tennis/, ignoring
    ESPN's placeholders. Tournaments with no timed match are left out."""
    out = {}
    cut = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    for tour in ("atp", "wta"):
        try:
            rows = json.load(open(os.path.join(HERE, "history-tennis", f"{tour}.json"))).get("matches") or []
        except (OSError, ValueError):
            continue
        times = {}
        for m in rows:
            if m.get("date", "") < cut or not m.get("time") or not m.get("tournament"): continue
            if tennis_placeholder(f"{m['date']}T{m['time']}:00Z"): continue
            times.setdefault(m["tournament"], []).append(m["time"])
        for k, v in times.items():
            out[k] = min(v)
    return out

def legs(dates):
    out = []
    data = json.load(open(os.path.join(HERE, "data.json"))) if os.path.exists(os.path.join(HERE, "data.json")) else {}
    for day in data.get("days") or []:
        if day["date"] not in dates: continue
        for g in day.get("games", []):
            p = g.get("p") or {}
            if not p or g.get("unrated"): continue
            # 21 Oct 2026: nothing the Daily List keeps out for blindness
            if g.get("celtic") or g.get("why") not in CLEAN_WHY: continue
            side = max(p, key=p.get)
            if side == "d": continue
            pl = leg_p(p[side], g.get("accuracy"), ADMIT_MIN)
            # 24 Oct 2026: mid-priced picks join the pool for the Multipliers
            # only (multOnly); they are priced from the bulk day prices and
            # never cost a per-fixture call (price_football, price_espn_soccer).
            if pl is None or p[side] < MULT_MODEL_MIN: continue
            h, a = g["home"]["name"], g["away"]["name"]
            out.append({"sport": "football", "event": f"{h} v {a}", "home": h, "away": a, "side": side,
                        "pick": h if side == "h" else a, "code": g.get("league"), "comp": g.get("leagueName"), "country": g.get("country"),
                        "when": g.get("kickoff"), "date": day["date"], "pModel": round(p[side], 4), "p": round(pl, 4),
                        "hit": g["accuracy"].get("cumHit", g["accuracy"]["hit"]), "n": g["accuracy"].get("cumN", g["accuracy"]["n"]), "list": bool(g.get("list")),
                        "pDraw": round(p.get("d", 0), 4), "multOnly": pl < WIDE_MIN})
    # 24 Oct 2026, Douglas: "Multipliers should be across all sports". Every
    # published sport's picks now enter the pool; those outside GROUP_SPORTS,
    # or under the Wider tested rate, are multOnly: the Multipliers can use
    # them, the groups built to land cannot (safe_leg, wide_leg).
    td = read_js("tennis-data.js") or {}
    starts = tennis_starts()
    for m in td.get("matches") or []:
        when = f"{m['date']}T{m['time']}:00Z" if m.get("time") else None
        # 25 Oct 2026: before the order of play is out ESPN dates a match at
        # midnight US Eastern (04:00 or 05:00 UTC), which put Vienna and Basel
        # in the Overnight window. Such a match takes its tournament's usual
        # first start from history-tennis/ instead (timeEst), or no time.
        time_est = False
        if when and tennis_placeholder(when):
            first = starts.get(m.get("tournament"))
            when, time_est = (f"{m['date']}T{first}:00Z" if first else None), True
        d = m.get("date")
        if d not in dates or "qualif" in (m.get("round") or "").lower(): continue
        pl = leg_p(m.get("confidence") or 0, m.get("accuracy"), ADMIT_MIN)
        if pl is None or (m.get("confidence") or 0) < MULT_MODEL_MIN: continue
        out.append({"sport": "tennis", "event": f"{m['playerA']} v {m['playerB']}", "pick": m["pick"], "tour": m.get("tour"), "tournament": m.get("tournament"),
                    "players": [m.get("playerA"), m.get("playerB")],
                    "comp": f"{m.get('tournament')} {m.get('round') or ''}".strip(), "when": when, "timeEst": time_est, "date": d, "id": m.get("id"),
                    "pModel": round(m["confidence"], 4), "p": round(pl, 4), "hit": m["accuracy"].get("cumHit", m["accuracy"]["hit"]), "n": m["accuracy"].get("cumN", m["accuracy"]["n"]),
                    "list": bool(m.get("list")), "multOnly": "tennis" not in GROUP_SPORTS or pl < WIDE_MIN,
                    # 25 Oct 2026, Douglas: tennis back on the Card. It stays off the
                    # Daily List (build_tennis.LIST_ON) until its live record holds;
                    # on the Card a tennis pick still needs a bookmaker price, the
                    # bookmakers at 60%+ and the model within 5 points of them.
                    "listOff": False, "tennisListOff": bool((td.get("list") or {}).get("off"))})
    sd = read_js("sports-data.js") or {}
    for key, sp in (sd.get("sports") or {}).items():
        if not sp.get("published"): continue
        for g in sp.get("games") or []:
            t = parse(g.get("when"))
            if not t or t.date().isoformat() not in dates: continue
            pl = leg_p(g.get("confidence") or 0, g.get("accuracy"), ADMIT_MIN)
            if pl is None or (g.get("confidence") or 0) < MULT_MODEL_MIN: continue
            out.append({"sport": key, "event": f"{g['home']} v {g['away']}", "home": g["home"], "away": g["away"],
                        "pick": g["pick"], "comp": g.get("label") or sp.get("name"), "when": g.get("when"), "date": t.date().isoformat(),
                        "id": g.get("id"), "pModel": round(g["confidence"], 4), "p": round(pl, 4),
                        "hit": g["accuracy"].get("cumHit", g["accuracy"]["hit"]), "n": g["accuracy"].get("cumN", g["accuracy"]["n"]), "list": bool(g.get("list")),
                        "multOnly": key not in GROUP_SPORTS or pl < WIDE_MIN, "listOff": bool(sp.get("listOff"))})
    return out

# ---------- prices ----------
def af(path, key):
    return get(AF_BASE + path, {"x-apisports-key": key})

ODDS_TTL = 90 * 60     # a fixture's prices are re-read at most every 90 minutes


def _odds_for(fid, key, cache_dir):
    """Match Winner prices for one fixture, cached on disk for ODDS_TTL.
    Returns (response items, calls made).

    25 Oct 2026 (review bug 8): this used to call API-Football directly, past
    sources._af_get's spent marker, so once the day's allowance was gone every
    fixture cost a call and its empty answer was cached 90 minutes as "no
    prices". Now the call goes through _af_get (paced, retried, stops for the
    run once the allowance is spent) and only a genuine answer is cached:
    _af_get keeps a path in its own cache only on a 200 with no errors, so a
    quota refusal, a bad reply or a network failure is never written to disk."""
    path = os.path.join(cache_dir, f"odds-{fid}.json")
    try:
        if time.time() - os.path.getmtime(path) < ODDS_TTL:
            with open(path) as f:
                return json.load(f), 0
    except (OSError, ValueError):
        pass
    sys.path.insert(0, HERE)
    import sources as S
    q = f"/odds?fixture={fid}&bet=1"
    before = S.AF_USAGE["calls"]
    items = S._af_get(q) or []
    calls = S.AF_USAGE["calls"] - before
    if q in S._AF_CACHE:       # a real answer, empty or not
        os.makedirs(cache_dir, exist_ok=True)
        with open(path, "w") as f:
            json.dump(items, f)
    return items, calls


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
    # 22 Oct 2026: the build now reads every API-Football price by date
    # (odds.af_odds_day, cached); a leg found there costs no call. The
    # one-fixture call stays as the fallback for anything it missed.
    import odds as O
    try:
        bulk = O.af_prices({_date.fromisoformat(d) for d in dates})
    except Exception as e:
        bulk = {}
        report.setdefault("errors", []).append(f"bulk odds: {type(e).__name__}")
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
            row = bulk.get(str(fid))
            if row:
                i = 0 if l["side"] == "h" else 2
                l.update(odds=round(row["avg"][i], 2), best=round(row["max"][i], 2), books=row["books"],
                         bestBook=(row.get("maxBook") or [None, None, None])[i],
                         margin=margin_of(row["avg"]),
                         src="API-Football, average of " + (f"{row['books']} bookmakers" if row["books"] != 1 else "1 bookmaker"))
                matched += 1; continue
            if l.get("multOnly"): continue    # bulk prices only, no call of its own
            try:
                items, n = _odds_for(fid, key, S.AF_CACHE_DIR); calls += n
            except Exception as e:
                report.setdefault("errors", []).append(f"odds {fid}: {type(e).__name__}"); continue
            prices = {"Home": [], "Away": [], "Draw": []}
            books = set(); top = {}    # best price per side among UK-licensed books (odds.UK_BOOKS)
            for item in items:
                for b in item.get("bookmakers") or []:
                    uk = O.uk_book(b.get("name"))
                    for bet in b.get("bets") or []:
                        if bet.get("id") != 1: continue
                        for v in bet.get("values") or []:
                            try:
                                o = float(v["odd"]); prices[v["value"]].append(o); books.add(b.get("name"))
                                if uk and o > top.get(v["value"], (0, None))[0]: top[v["value"]] = (o, b.get("name"))
                            except (KeyError, ValueError): pass
            books = sorted(books)
            side = prices["Home" if l["side"] == "h" else "Away"]
            if side:
                avg = [sum(v) / len(v) for v in prices.values() if v]
                mean = sum(side) / len(side)
                uk_top = top.get("Home" if l["side"] == "h" else "Away", (0, None))
                l.update(odds=round(mean, 2), best=round(uk_top[0] if uk_top[1] else mean, 2), books=len(books),
                         bestBook=uk_top[1],
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
    want = [l for l in L if l["sport"] == "football" and not l.get("odds") and l.get("code") in ESPN_SLUGS
            and not l.get("multOnly")]
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
    # 21 Oct 2026: five URC and Top 14 legs (81-91%) went unpriced because no
    # key's title named their competition. When none does, try every active
    # union key: the event is still matched on both team names and kick-off,
    # so a wrong key prices nothing, and credits stay inside the day's cap.
    if l["sport"] == "rugby" and not out:
        out = [sp["key"] for sp in active if str(sp.get("key", "")).startswith("rugbyunion")]
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
    rep["rugbyKeys"] = sorted(f"{s.get('key')} | {s.get('title')}" for s in active if str(s.get("key", "")).startswith("rugby"))
    rep["noKey"] = sorted({f"{l.get('tour')} {l.get('tournament')}" for l in want
                           if l["sport"] == "tennis" and not _odds_keys(l, active)} |
                          {f"rugby {l.get('comp')}" for l in want if l["sport"] == "rugby" and not _odds_keys(l, active)})
    # Keys the groups built to land need come first; Multiplier-only legs
    # (multOnly, 24 Oct 2026) ride on the same keys and spend what is left.
    for k in sorted(need, key=lambda k: (-sum(1 for l in need[k] if not l.get("multOnly")), -len(need[k]))):
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
                prices, books, margins, top = [], set(), [], (0, None)
                for b in ev.get("bookmakers") or []:
                    for m in b.get("markets") or []:
                        if m.get("key") != "h2h": continue
                        mg = margin_of([o.get("price") for o in m.get("outcomes") or []])
                        if mg: margins.append(mg)
                        for o in m.get("outcomes") or []:
                            if same(o.get("name", ""), l["pick"]):
                                try:
                                    pr = float(o["price"]); prices.append(pr); books.add(b.get("title") or b.get("key"))
                                    if pr > top[0]: top = (pr, b.get("title") or b.get("key"))
                                except (KeyError, ValueError): pass
                if prices:
                    l.update(odds=round(sum(prices) / len(prices), 2), best=round(max(prices), 2), books=len(books), bestBook=top[1],
                             margin=round(sum(margins) / len(margins), 4) if margins else None,
                             src="The Odds API, UK average of " + (f"{len(books)} bookmakers" if len(books) != 1 else next(iter(books))))
                    rep["matched"] += 1
                break
    with open(led_path, "w") as f: json.dump(led, f)
    rep.update(usedToday=led["days"].get(day, 0), usedMonth=led["used"], left=led.get("left"))
    report["oddsApi"] = rep


# ---------- API-Sports, other sports (25 Oct 2026) ----------
# The API-Football account carries a free plan on each of API-Sports' other
# products (tools/odds_probe.py, 25 Oct 2026: rugby, basketball, hockey,
# baseball, american-football all answer, "Free", 100 calls a day each).
# Odds come per game (/odds?game=), not by date, so each build reads the
# day's games once per sport and date (cached), then prices only the legs
# that still need one, inside AS_DAY calls a UK day per product.
AS_HOST = {"rugby": "v1.rugby.api-sports.io", "nba": "v1.basketball.api-sports.io",
           "wnba": "v1.basketball.api-sports.io", "ncaab": "v1.basketball.api-sports.io",
           "nhl": "v1.hockey.api-sports.io", "mlb": "v1.baseball.api-sports.io",
           "nfl": "v1.american-football.api-sports.io", "cfb": "v1.american-football.api-sports.io"}
AS_DAY = 85            # of the free 100 a day per product, leaving room for a probe
AS_GAMES_TTL = 4 * 3600
AS_ODDS_TTL = 90 * 60
AS_GAP = 6.5           # seconds between calls to one product (free plan: 10 a minute)
AS_AHEAD = 1           # the free plan only serves yesterday to tomorrow
AS_BETS = ("Home/Away", "Match Winner", "3Way Result", "Moneyline", "Winner")


def _as_side(item, pick_home):
    """(average price for the pick, best price, best book, books, margin) from
    one /odds item, using the first match-winner bet found per bookmaker. The
    best price is among UK-licensed books only (odds.UK_BOOKS; API-Sports
    shares API-Football's bookmaker list); none pricing it leaves best at the
    average and the book None."""
    import odds as O
    side, books, margins, top = [], set(), [], (0.0, None)
    for bk in item.get("bookmakers") or []:
        bets = {b.get("name"): b for b in bk.get("bets") or []}
        bet = next((bets[n] for n in AS_BETS if n in bets), None)
        if not bet: continue
        vals = {}
        for v in bet.get("values") or []:
            try: vals[str(v.get("value"))] = float(v.get("odd"))
            except (TypeError, ValueError): pass
        o = vals.get("Home" if pick_home else "Away")
        if not o or o <= 1: continue
        side.append(o); books.add(bk.get("name"))
        if O.uk_book(bk.get("name")) and o > top[0]: top = (o, bk.get("name"))
        mg = margin_of(list(vals.values()))
        if mg: margins.append(mg)
    if not side: return None
    mean = sum(side) / len(side)
    return (round(mean, 2), round(top[0] if top[1] else mean, 2), top[1], len(books),
            round(sum(margins) / len(margins), 4) if margins else None)


def price_api_sports(L, dates, report, cache_dir=None, now=None, fetch=None):
    key = os.environ.get("API_FOOTBALL_KEY")
    want = [l for l in L if not l.get("odds") and l["sport"] in AS_HOST and l.get("home") and l.get("away")]
    if not key or not want:
        report["apiSports"] = "no key" if not key else "no legs"; return
    stub = fetch is not None
    fetch = fetch or (lambda url: get(url, {"x-apisports-key": key}))
    now = now or datetime.now(timezone.utc)
    if cache_dir is None:
        sys.path.insert(0, HERE)
        import sources as S
        cache_dir = S.AF_CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)
    day = now.astimezone(ZoneInfo("Europe/London")).date().isoformat()
    led_path = os.path.join(cache_dir, "apisports-ledger.json")
    try: led = json.load(open(led_path))
    except (OSError, ValueError): led = {}
    if led.get("day") != day: led = {"day": day, "used": {}}
    rep = {"legs": len(want), "matched": 0, "calls": 0, "cached": 0, "skipped": 0}

    def cached(name, ttl):
        path = os.path.join(cache_dir, f"apisports2-{name}.json")
        try:
            if time.time() - os.path.getmtime(path) < ttl: return json.load(open(path))
        except (OSError, ValueError): pass
        return None

    last = {}
    def call(host, path, name, ttl):
        c = cached(name, ttl)
        if c is not None: rep["cached"] += 1; return c
        if led["used"].get(host, 0) >= AS_DAY: rep["skipped"] += 1; return None
        # The free plan allows 10 calls a minute per product: pace them.
        wait = AS_GAP - (time.time() - last.get(host, 0))
        if wait > 0 and not stub: time.sleep(wait)
        try: d = fetch(f"https://{host}{path}")
        except Exception as e:
            report.setdefault("errors", []).append(f"api-sports {host}{path}: {type(e).__name__}"); return None
        last[host] = time.time()
        led["used"][host] = led["used"].get(host, 0) + 1; rep["calls"] += 1
        items = d.get("response") or [] if isinstance(d, dict) else []
        errs = d.get("errors") if isinstance(d, dict) else None
        if errs:
            # 25 Oct 2026: a rate-limit reply was cached as "no games" for four
            # hours, so nothing matched. Errors are logged, never cached.
            rep.setdefault("errors", []).append(f"{host.split('.')[1]} {path.split('?')[0]}: {list(errs)[:2] if isinstance(errs, dict) else errs}")
            return items or None
        with open(os.path.join(cache_dir, f"apisports2-{name}.json"), "w") as f: json.dump(items, f)
        return items

    horizon = (now.date() + timedelta(days=AS_AHEAD)).isoformat()
    want = [l for l in want if (l.get("date") or "") <= horizon]
    rep["legs"] = len(want)
    for l in sorted(want, key=lambda l: l.get("when") or "9"):
        host = AS_HOST[l["sport"]]
        t = parse(l.get("when"))
        days = sorted(d for d in {(t or now).date().isoformat(), l["date"]} if d <= horizon)
        game = None
        for dd in days:
            games = call(host, f"/games?date={dd}", f"{host.split('.')[1]}-games-{dd}", AS_GAMES_TTL) or []
            for g in games:
                tm = g.get("teams") or {}
                h, a = (tm.get("home") or {}).get("name", ""), (tm.get("away") or {}).get("name", "")
                gt = parse(g.get("date")) if isinstance(g.get("date"), str) else None
                if gt is None and g.get("timestamp"):
                    gt = datetime.fromtimestamp(g["timestamp"], timezone.utc)
                if t and gt and abs((t - gt).total_seconds()) > 3 * 3600: continue
                if same(h, l["home"]) and same(a, l["away"]):
                    game = g; break
            if game: break
        if not game: continue
        gid_ = game.get("id")
        items = call(host, f"/odds?game={gid_}", f"{host.split('.')[1]}-odds-{gid_}", AS_ODDS_TTL) or []
        r = _as_side(items[0], same(l["pick"], l["home"])) if items else None
        if not r: continue
        avg, best, book, n, mg = r
        l.update(odds=avg, best=best, bestBook=book, books=n, margin=mg,
                 src="API-Sports, average of " + (f"{n} bookmakers" if n != 1 else (book or "1 bookmaker")))
        rep["matched"] += 1
    with open(led_path, "w") as f: json.dump(led, f)
    rep["used"] = led["used"]
    report["apiSports"] = rep


# ---------- PinnWire: Pinnacle prices (25 Oct 2026) ----------
# Pinnacle's own prices for 13 sports (tennis and rugby among them), through
# PinnWire's free key (100 calls a day, no card; the shared demo key is used
# up by others each day, tools/odds_probe.py). Only with PINNWIRE_KEY. One
# call per build at most (sport_id=all, prematch, cached PW_TTL), so six
# builds use six calls. Pinnacle runs a thin margin, so its price is close to
# a fair one; it prices legs nothing else did, never football (API-Football
# covers that).
PW_URL = "https://pinnwire.com/kit/v1/markets?sport_id=all&event_type=prematch"
PW_TTL = 60 * 60


def same_any(a, b):
    """same(), and also names in either order ("Sinner, Jannik" / "Jannik Sinner")."""
    if same(a, b): return True
    ta, tb = sorted(norm(a).split()), sorted(norm(b).split())
    return bool(ta) and ta == tb

def price_pinnwire(L, dates, report, cache_dir=None, fetch=None):
    key = os.environ.get("PINNWIRE_KEY")
    want = [l for l in L if not l.get("odds") and l["sport"] != "football"]
    if not key or not want:
        report["pinnwire"] = "no key" if not key else "no legs"; return
    if cache_dir is None:
        sys.path.insert(0, HERE)
        import sources as S
        cache_dir = S.AF_CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, "pinnwire-prematch.json")
    events, calls = None, 0
    try:
        if time.time() - os.path.getmtime(path) < PW_TTL: events = json.load(open(path))
    except (OSError, ValueError): pass
    if events is None:
        try:
            d = (fetch or (lambda u: get(u, {"x-api-key": key})))(PW_URL); calls = 1
            events = d.get("events") or [] if isinstance(d, dict) else []
            with open(path, "w") as f: json.dump(events, f)
        except Exception as e:
            report["pinnwire"] = {"error": type(e).__name__}; return
    matched = 0
    for l in want:
        names = l.get("players") or [l.get("home"), l.get("away")]
        if not all(names): continue
        t = parse(l.get("when"))
        for ev in events:
            st = parse(ev.get("starts") or ev.get("start_ts"))
            if t and st and abs((t - st).total_seconds()) > 6 * 3600: continue
            h, a = ev.get("home", ""), ev.get("away", "")
            if not (same_any(h, names[0]) and same_any(a, names[1])) and not (same_any(h, names[1]) and same_any(a, names[0])): continue
            ml = ((ev.get("periods") or {}).get("num_0") or {}).get("money_line") or {}
            side = "home" if same_any(l["pick"], h) else "away" if same_any(l["pick"], a) else None
            o = ml.get(side) if side else None
            if not o or o <= 1: break
            l.update(odds=round(float(o), 2), best=round(float(o), 2), bestBook="Pinnacle", books=1,
                     margin=margin_of([ml.get("home"), ml.get("away"), ml.get("draw")]),
                     src="Pinnacle (PinnWire)")
            matched += 1; break
    report["pinnwire"] = {"calls": calls, "events": len(events), "legs": len(want), "matched": matched}

def price(L, dates):
    report = {}
    price_football(L, dates, report)
    price_espn_soccer(L, dates, report)
    price_espn(L, dates, report)
    price_api_sports(L, dates, report)
    price_pinnwire(L, dates, report)
    price_odds_api(L, dates, report)
    for l in L:
        if not l.get("odds"):
            # 22 Oct 2026: with a typical bookmaker margin (MARGIN), so a group
            # shown at 2.00+ should still pay that much when placed.
            l.update(odds=round(1 / (l["pModel"] * MARGIN), 2), est=True,
                     src="estimate: the model's price less a typical bookmaker margin, no bookmaker price found")
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
def safe_leg(l):
    """Whether a priced leg may go in a group (21 Oct 2026): a bookmaker price,
    the model and the market both at LEG_MIN or more, and the model no more
    than MAX_ABOVE_BOOK above the market. Where they disagree the market has
    been the better guide (see the module notes)."""
    if l.get("multOnly") or l.get("est") or l.get("fair") is None: return False
    if l["pModel"] < LEG_MIN or l["fair"] < LEG_MIN or l.get("pTested", l["p"]) < LEG_MIN: return False
    return l["pModel"] - l["fair"] <= MAX_ABOVE_BOOK

def wide_leg(l):
    """A leg for the Wider groups (22 Oct 2026): priced, with tested rate,
    model and bookmaker all WIDE_MIN+ and the model at most WIDE_ABOVE_BOOK
    over the market; or unpriced, on the Daily List, tested and model
    WIDE_EST_MIN+. Both compete on their chance (best_wide)."""
    if l.get("multOnly"): return False
    if l.get("est") or l.get("fair") is None:
        return bool(l.get("list") and l.get("pTested", l["p"]) >= WIDE_EST_MIN and l["pModel"] >= WIDE_EST_MIN)
    if min(l["pModel"], l["fair"], l.get("pTested", l["p"])) < WIDE_MIN: return False
    return l["pModel"] - l["fair"] <= WIDE_ABOVE_BOOK

def is_wide(name): return str(name).startswith("Wider")

def ok_combo(c, lo, hi, name, max_est=0):
    o = math.prod(l["odds"] for l in c)
    if not (max(lo, MIN_RETURN) <= o <= hi): return None
    if len({l["event"] for l in c}) < LEGS_IN.get(name, 5): return None
    if sum(1 for l in c if l.get("est")) > max_est: return None
    comps = {}
    for l in c: comps[l.get("comp")] = comps.get(l.get("comp"), 0) + 1
    if max(comps.values()) > 2: return None
    return o

def pool(L, used, after, max_est=0, wide=False):
    ok = wide_leg if wide else safe_leg
    c = [l for l in L if l["event"] not in used and (max_est or ok(l)) and l["odds"] >= 1.01
         and (parse(l["when"]) or after) >= after]
    # The strongest twenty are plenty for two or three legs.
    return sorted(c, key=lambda l: -l["p"])[:20]

def best(L, used, after, name, lo, hi):
    # Bookmaker-priced, safe legs only: no estimates, no fallback.
    return _best(L, used, after, name, lo, hi, 0)

# Rule version of the Wider groups. A published Wider group from an older
# rule is rebuilt, not held, the first build after the rule changes.
WIDE_RULE = 4      # 3: every group pays MIN_RETURN or more; 4: Fourfolds (22 Oct 2026)

def best_wide(L, used, after, name, lo, hi):
    """A Wider group from the strongest legs, priced or not (22 Oct 2026,
    rule 2, Douglas: "why are you not using stronger picks from the daily
    list"). Rule 1 took bookmaker-priced legs first, so 71% priced legs went
    in ahead of 80%+ unpriced Daily List picks; list picks have won 84.8% of
    79, clean 65-75% picks 70.9% of 220. An unpriced leg's chance is its
    tested rate, capped by the model; its price is an estimate, marked."""
    g = _best(L, used, after, name, lo, hi, LEGS_IN[name], wide=True)
    if g: g["rule"] = WIDE_RULE
    return g

def is_mult(name): return str(name).startswith("Multiplier")

def mult_fault(l):
    """Why a leg cannot go in a Multiplier, in plain words, or None
    (24 Oct 2026). See MULT_KINDS for the evidence."""
    if MULT_SPORTS and l.get("sport") not in MULT_SPORTS: return f"{l['pick']}: not a Multiplier sport"
    # 25 Oct 2026: a sport kept off the Daily List for its live record (college
    # football, tennis) is kept out of the Multipliers too. North Carolina, a
    # college football leg, lost Douglas a five-fold on 24 Oct.
    if l.get("listOff"): return f"{l['pick']}: its sport is off the Daily List on its live record"
    if l.get("est") or l.get("fair") is None: return f"{l['pick']}: no bookmaker price"
    if not MULT_ODDS[0] <= l["odds"] <= MULT_ODDS[1]:
        return f"{l['pick']}: price {l['odds']:.2f}, outside {MULT_ODDS[0]:.2f} to {MULT_ODDS[1]:.2f}"
    if l["fair"] < MULT_FAIR_MIN:
        return f"{l['pick']}: the bookmakers now give {pct(l['fair'])}, under {pct(MULT_FAIR_MIN)}"
    if l["pModel"] < MULT_MODEL_MIN:
        return f"{l['pick']}: the model now gives {pct(l['pModel'])}, under {pct(MULT_MODEL_MIN)}"
    if l["pModel"] - l["fair"] > MULT_ABOVE_BOOK:
        return (f"{l['pick']}: the model ({pct(l['pModel'])}) now sits {round((l['pModel'] - l['fair']) * 100)} "
                f"points above the bookmakers ({pct(l['fair'])})")
    return None

def mult_leg(l): return mult_fault(l) is None

def as_mult(l):
    """A leg as a Multiplier carries it: its chance is the bookmakers' fair
    chance, which has been the better guide at these prices."""
    return dict(l, p=l["fair"], basis="bookmakers")

def mult_combo(c, lo, hi):
    """Combined price if the legs make a valid Multiplier, else None."""
    o = math.prod(l["odds"] for l in c)
    if not lo <= o <= hi: return None
    if len({l["event"] for l in c}) < len(c): return None
    comps = {}
    for l in c: comps[l.get("comp")] = comps.get(l.get("comp"), 0) + 1
    if max(comps.values()) > 2: return None
    return o

def best_mult(L, used, after, name):
    """The 2-4 legs with the highest combined chance (bookmakers' fair) whose
    combined price reaches the kind's target, or None."""
    lo, hi = MULT_RANGE[name]
    cands = [as_mult(l) for l in L if l["event"] not in used and mult_leg(l)
             and (parse(l["when"]) or after) >= after]
    # Keep the legs that give up the least chance per unit of price: chance
    # lost is -log(fair), price gained is log(odds); their ratio is about
    # 1 + log(margin) / log(odds), so lower-margin and longer legs come first.
    # Sorting by chance alone kept only the shortest legs, which cannot reach
    # 3x in four (found on 24 Oct's board: 128 legs passed, no group).
    cands = sorted(cands, key=lambda l: (-math.log(l["p"]) / math.log(l["odds"]), -l["p"]))[:MULT_POOL]
    top = None
    for k in MULT_LEGS:
        for c in itertools.combinations(cands, k):
            o = mult_combo(c, lo, hi)
            if o is None: continue
            p = math.prod(l["p"] for l in c)
            if p < MIN_CHANCE[name]: continue
            if not top or p > top[0] or (p == top[0] and o > top[2]): top = (p, c, o)
    if not top: return None
    p, c, o = top
    legs_ = sorted([dict(l) for l in c], key=lambda l: l.get("when") or "9")
    return {"name": name, "risk": RISK.get(name), "band": [lo, hi], "minChance": MIN_CHANCE[name],
            "odds": round(o, 2), "p": round(p, 4), "implied": round(math.prod(l["implied"] for l in legs_), 4),
            "estimates": 0, "basis": "bookmakers", "rule": MULT_RULE, "legs": legs_}

def recheck_mult(g, L):
    """recheck() for a Multiplier: every leg still a clean pick on the same
    side, still passing mult_leg at today's price, and the group still at or
    above its target and floor."""
    by = {(l["event"], l["pick"]): l for l in L}
    legs_, why = [], []
    if g.get("rule") != MULT_RULE:
        return None, ["rebuilt under the current Multiplier rule"]
    for old in g["legs"]:
        cur = by.get((old["event"], old["pick"]))
        if cur is None:
            why.append(f"{old['pick']}: no longer a clean pick for this day (moved, postponed, flagged or the model's side changed)")
            continue
        fault = mult_fault(cur)
        if fault: why.append(fault); continue
        legs_.append(dict(as_mult(cur), firstOdds=old.get("firstOdds", old.get("odds"))))
    if why: return None, why
    name = g["name"]
    lo, hi = MULT_RANGE[name]
    o = mult_combo(legs_, lo, hi)
    p = math.prod(l["p"] for l in legs_)
    if o is None:
        return None, [f"combined price {math.prod(l['odds'] for l in legs_):.2f}, outside {lo:.2f} to {hi:.2f}"]
    if p < MIN_CHANCE[name]:
        return None, [f"combined chance now {pct(p)}, under the {pct(MIN_CHANCE[name])} floor"]
    legs_.sort(key=lambda l: l.get("when") or "9")
    return {**{k: v for k, v in g.items() if k not in ("legs", "odds", "p", "implied", "status", "checked")},
            "odds": round(o, 2), "p": round(p, 4), "implied": round(math.prod(l["implied"] for l in legs_), 4),
            "estimates": 0, "legs": legs_, "status": "holding", "first": g.get("first") or g.get("checked")}, []

def _best(L, used, after, name, lo, hi, max_est, wide=False, priced_only=False):
    top = None
    cands = pool(L, used, after, 0, wide=wide)
    if priced_only: cands = [l for l in cands if not l.get("est")]
    for c in itertools.combinations(cands, LEGS_IN.get(name, 5)):
        o = ok_combo(c, lo, hi, name, max_est)
        if o is None: continue
        p = math.prod(l["p"] for l in c)
        if p < MIN_CHANCE.get(name, 0): continue
        score = p * (1 + LIST_NUDGE * sum(1 for l in c if l.get("list")))
        if not top or score > top[0]: top = (score, c, o, p)
    if not top: return None
    _, c, o, p = top
    legs_ = sorted([dict(l) for l in c], key=lambda l: l.get("when") or "9")
    implied = math.prod(l["implied"] for l in legs_)
    return {"name": name, "risk": RISK.get(name), "band": [lo, hi], "minChance": MIN_CHANCE.get(name),
            "odds": round(o, 2), "p": round(p, 4), "implied": round(implied, 4),
            "estimates": sum(1 for l in legs_ if l.get("est")), "legs": legs_}

def build_day(L, after, prev=None, now=None, log=None, min_groups=0):
    """The day's groups. With prev (the groups an earlier build published for
    this date), each is re-checked first: one still passing every rule keeps
    its place, so a group someone has already placed does not reshuffle under
    them; one that fails is dropped, the reasons go in log, and its slot is
    rebuilt from the legs left. A group with a leg already started is kept as
    published, marked underway, and its games are not reused."""
    used, groups = set(), []
    now = now or after
    stamp = iso(now)
    kept, wide_kept, mult_kept = {}, [], []
    for g in prev or []:
        if g.get("name") not in LEGS_IN and not is_mult(g.get("name")): continue
        if underway(g, now):
            u = dict(g, status="underway"); groups.append(u)
            used |= {l["event"] for l in g["legs"]}; continue
        if is_mult(g["name"]):
            if g["name"] not in MULT_RANGE: continue      # a retired Multiplier kind
            ng, why = recheck_mult(g, L)
            if ng is None:
                if log is not None:
                    log.append({"at": stamp, "name": g["name"], "rank": g.get("rank", "main"), "odds": g.get("odds"),
                                "picks": [l["pick"] for l in g["legs"]], "why": why})
                continue
            if len(mult_kept) >= MULT_PER_DAY: continue
            mult_kept.append(ng); used |= {l["event"] for l in ng["legs"]}; continue
        ng, why = recheck(g, L)
        if ng is None:
            if log is not None:
                log.append({"at": stamp, "name": g["name"], "rank": g.get("rank", "main"),
                            "odds": g.get("odds"), "picks": [l["pick"] for l in g["legs"]], "why": why})
            continue
        if is_wide(g["name"]):
            if g.get("rule") != WIDE_RULE:
                if log is not None:
                    log.append({"at": stamp, "name": g["name"], "rank": g.get("rank", "fill"), "odds": g.get("odds"),
                                "picks": [l["pick"] for l in g["legs"]],
                                "why": ["rebuilt under the new rule: strongest Daily List picks first, priced or not"]})
                continue
            wide_kept.append(ng); used |= {l["event"] for l in ng["legs"]}; continue
        if (g.get("rank", "main"), g["name"]) in kept: continue
        kept[(g.get("rank", "main"), g["name"])] = ng
        used |= {l["event"] for l in ng["legs"]}
    replaced = {(e["rank"], e["name"]) for e in (log or []) if e["at"] == stamp}
    for rank in ("main", "alternative"):
        for name, lo, hi in BANDS:
            g = kept.get((rank, name))
            if g is None:
                g = best(L, used, after, name, lo, hi)
                if not g: continue
                g.update(rank=rank, first=stamp, status="replacement" if (rank, name) in replaced else "new")
                for l in g["legs"]: l.setdefault("firstOdds", l["odds"])
                used |= {l["event"] for l in g["legs"]}
            g["checked"] = stamp
            groups.append(g)
    # Wider groups (22 Oct 2026): only while the day has fewer than
    # min_groups that can still be placed. A Wider group that still holds is
    # kept even when a strict one has since appeared, as strict ones are.
    live_n = lambda: sum(1 for g in groups if g.get("status") != "underway")
    for g in wide_kept:
        g["checked"] = stamp; groups.append(g)
    wide_replaced = sum(1 for e in (log or []) if e["at"] == stamp and is_wide(e["name"]))
    while live_n() < min_groups:
        # A Double first, as it needs the fewest legs and lands most often;
        # a Treble only when no Double can be made from what is left.
        # The most likely group of either kind (22 Oct 2026: at 2.00 or more
        # a Treble of three ~80% picks lands about as often as a Double of
        # two ~70% picks, so neither kind goes first by rule).
        cands = [x for x in (best_wide(L, used, after, n, lo, hi) for n, lo, hi in WIDE_BANDS) if x]
        if not cands: break
        g = max(cands, key=lambda x: x["p"])
        g.update(rank="fill", first=stamp, status="replacement" if wide_replaced > 0 else "new")
        wide_replaced -= 1
        for l in g["legs"]: l.setdefault("firstOdds", l["odds"])
        g["checked"] = stamp
        used |= {l["event"] for l in g["legs"]}
        groups.append(g)
    # Multipliers (24 Oct 2026): after the groups built to land, from the
    # picks those left, so they never take a leg the safer groups need. They
    # do not count toward min_groups: they are a different kind of bet.
    name = MULT_KINDS[0][0]
    mults = list(mult_kept)
    mult_replaced = sum(1 for e in (log or []) if e["at"] == stamp and is_mult(e["name"]))
    while len(mults) < MULT_PER_DAY:
        g = best_mult(L, used, after, name)
        if not g: break
        g.update(first=stamp, status="replacement" if mult_replaced > 0 else "new")
        mult_replaced -= 1
        for l in g["legs"]: l.setdefault("firstOdds", l["odds"])
        used |= {l["event"] for l in g["legs"]}
        mults.append(g)
    # Strongest first; the rank says first, second or third choice.
    mults.sort(key=lambda g: -g["p"])
    for g, rank in zip(mults, ("main", "alternative", "third")):
        g["rank"] = rank; g["checked"] = stamp
        groups.append(g)
    # A first choice that failed with nothing to replace it leaves the second
    # choice as the best of its kind, so it is shown as the first.
    for name, _, _ in BANDS:
        live = [g for g in groups if g["name"] == name and g.get("status") != "underway"]
        if live and not any(g["rank"] == "main" for g in live):
            live[0]["rank"] = "main"
    # 25 Oct 2026: every group also carries its combined price at the best
    # price on offer for each pick (bestOdds); the headline stays the average.
    for g in groups:
        if g.get("status") != "underway":
            g["bestOdds"] = round(math.prod(max(l.get("best") or l["odds"], l["odds"]) for l in g["legs"]), 2)
    # Underway groups last: they can no longer be placed.
    return sorted(groups, key=lambda g: g.get("status") == "underway")


# ---------- the Card (25 Oct 2026) ----------
# Douglas, after the weekend of 24-25 Oct: "make bets the day before or
# morning and leave it", "groups play over the same sort of hours", "only one
# fixture per group", "at least 2.0 or 3.0+ returns on all groups", "all
# sports considered". The Card replaces the Double / Treble / Wider /
# Multiplier groups as what the site puts forward (those kinds stay in the
# record under their names). For each UK day, three windows by kick-off:
#   Overnight 00:00-09:00 (US evening sport, Asia, Oceania)
#   Daytime   09:00-17:00 (Asia late, Europe lunch and afternoon)
#   Evening   17:00-24:00 (Europe evening, US afternoon)
# and in each window two groups: Card 2x (pays 2.0 or more) and Card 3x (3.0
# or more), each of CARD_LEGS picks from different fixtures, no fixture in
# two groups the same day. Every pick is priced by a bookmaker, rated 60%+ by
# them (CARD_FAIR_MIN), the model no more than 5 points above them, clean,
# from a sport on the Daily List; its chance is the bookmakers' own.
#
# Locking. A group can be rebuilt while prices settle, until its window's
# lock: 21:00 UK the evening before for Overnight, 07:00 UK on the day for
# Daytime and Evening. From then it never changes, whatever happens to a
# price or a leg: it is the bet to place and leave. A window that had no
# group by its lock may still get one later from games not yet started,
# marked late. Only locked groups are archived and graded.
CARD_WINDOWS = [("Overnight", 0, 9), ("Daytime", 9, 17), ("Evening", 17, 24)]
CARD_KINDS = [("Card 2x", 2.0, 3.0, 0.30), ("Card 3x", 3.0, 4.6, 0.18)]
CARD_LEGS = (3, 4)
CARD_ODDS = (1.15, 1.90)
CARD_FAIR_MIN = 0.60
CARD_POOL = 24
CARD_RULE = 1
UK = ZoneInfo("Europe/London")
RISK.update({"Card 2x": "Pays 2x+", "Card 3x": "Pays 3x+"})
MIN_CHANCE.update({n: f for n, _, _, f in CARD_KINDS})
CARD_RANGE = {n: (lo, hi) for n, lo, hi, _ in CARD_KINDS}

def is_card(name): return str(name).startswith("Card")

def uk_slot(l):
    """(UK date, window name) of a leg's kick-off, or None without a time."""
    t = parse(l.get("when"))
    if not t: return None
    u = t.astimezone(UK)
    w = next(n for n, a, b in CARD_WINDOWS if a <= u.hour < b)
    return u.date().isoformat(), w

def lock_time(date, window):
    """When a window's groups freeze, as a UTC datetime."""
    d = datetime.fromisoformat(date).date()
    if window == "Overnight":
        loc = datetime(d.year, d.month, d.day, 21, 0, tzinfo=UK) - timedelta(days=1)
    else:
        loc = datetime(d.year, d.month, d.day, 7, 0, tzinfo=UK)
    return loc.astimezone(timezone.utc)

def window_end(date, window):
    d = datetime.fromisoformat(date).date()
    end = dict((n, b) for n, _, b in CARD_WINDOWS)[window]
    base = datetime(d.year, d.month, d.day, tzinfo=UK) + timedelta(hours=end)
    return base.astimezone(timezone.utc)

# 25 Oct 2026, Douglas: "There is no daytime and evening bets. There needs to
# be some even if they update on later rebuilds." When the full rule fills
# neither kind in a window, the window takes the best group under the wider
# rule: picks priced 1.08 to 2.10 at the bookmakers' 55%+, three to five of
# them (short favourites need a fifth to reach 2x). The model still may
# not sit more than 5 points above the market (the weekend's losing pattern).
# Wider groups are labelled, rebuilt on every build until the lock, replaced
# by a full-rule group as soon as one can be made, and graded apart
# (cardWide) so the full rule's record stays clean.
CARD_WIDE_ODDS = (1.08, 2.10)
CARD_WIDE_LEGS = (3, 4, 5)
CARD_WIDE_FAIR_MIN = 0.55

def card_fault(l, wide=False):
    """Why a leg cannot go on the Card, in plain words, or None."""
    lo_hi, fair_min = (CARD_WIDE_ODDS, CARD_WIDE_FAIR_MIN) if wide else (CARD_ODDS, CARD_FAIR_MIN)
    if l.get("listOff"): return f"{l['pick']}: its sport is off the Daily List on its live record"
    if l.get("est") or l.get("fair") is None: return f"{l['pick']}: no bookmaker price"
    if not lo_hi[0] <= l["odds"] <= lo_hi[1]:
        return f"{l['pick']}: price {l['odds']:.2f}, outside {lo_hi[0]:.2f} to {lo_hi[1]:.2f}"
    if l["fair"] < fair_min:
        return f"{l['pick']}: the bookmakers give {pct(l['fair'])}, under {pct(fair_min)}"
    if l["pModel"] < MULT_MODEL_MIN:
        return f"{l['pick']}: the model gives {pct(l['pModel'])}, under {pct(MULT_MODEL_MIN)}"
    if l["pModel"] - l["fair"] > MULT_ABOVE_BOOK:
        return (f"{l['pick']}: the model ({pct(l['pModel'])}) sits {round((l['pModel'] - l['fair']) * 100)} "
                f"points above the bookmakers ({pct(l['fair'])})")
    return None

def best_card(L, used, after, name, wide=False):
    """The CARD_LEGS picks with the highest combined chance (bookmakers'
    fair) whose combined price falls in the kind's range, or None."""
    lo, hi = CARD_RANGE[name]
    cands = [as_mult(l) for l in L if l["event"] not in used and card_fault(l, wide) is None
             and (parse(l["when"]) or after) >= after]
    cands = sorted(cands, key=lambda l: (-math.log(l["p"]) / math.log(l["odds"]), -l["p"]))[:CARD_POOL]
    top = None
    for k in (CARD_WIDE_LEGS if wide else CARD_LEGS):
        for c in itertools.combinations(cands, k):
            o = mult_combo(c, lo, hi)
            if o is None: continue
            p = math.prod(l["p"] for l in c)
            if p < MIN_CHANCE[name]: continue
            if not top or p > top[0] or (p == top[0] and o > top[2]): top = (p, c, o)
    if not top: return None
    p, c, o = top
    legs_ = sorted([dict(l) for l in c], key=lambda l: l.get("when") or "9")
    return {"name": name, "risk": "Wider rule" if wide else RISK.get(name), "band": [lo, hi], "minChance": MIN_CHANCE[name],
            "odds": round(o, 2), "p": round(p, 4), "implied": round(math.prod(l["implied"] for l in legs_), 4),
            "estimates": 0, "basis": "bookmakers", "rule": CARD_RULE, "wide": wide, "legs": legs_,
            "bestOdds": round(math.prod(max(l.get("best") or l["odds"], l["odds"]) for l in legs_), 2)}

def recheck_card(g, L):
    """An unlocked Card group against this build: every leg still on the
    board on the same side and passing card_fault, the group in range and
    above its floor. (group at today's prices, []) or (None, reasons)."""
    if g.get("rule") != CARD_RULE: return None, ["rebuilt under the current Card rule"]
    by = {(l["event"], l["pick"]): l for l in L}
    legs_, why = [], []
    for old in g["legs"]:
        cur = by.get((old["event"], old["pick"]))
        if cur is None:
            why.append(f"{old['pick']}: no longer on the board for this day (moved, postponed, flagged or the model's side changed)"); continue
        if cur.get("est") and not old.get("est") and old.get("odds"):
            # 25 Oct 2026 (review bug 8): a price source that failed this build
            # is not a reason to drop an unlocked Card group. The last confirmed
            # price stands, flagged stale, until a build can read one again; the
            # model's side of the check still runs on this build's number.
            cur = stale_price(cur, old)
        f = card_fault(cur, bool(g.get("wide")))
        if f: why.append(f); continue
        legs_.append(dict(as_mult(cur), firstOdds=old.get("firstOdds", old.get("odds"))))
    if why: return None, why
    lo, hi = CARD_RANGE[g["name"]]
    o = mult_combo(legs_, lo, hi); p = math.prod(l["p"] for l in legs_)
    if o is None: return None, [f"combined price {math.prod(l['odds'] for l in legs_):.2f}, outside {lo:.2f} to {hi:.2f}"]
    if p < MIN_CHANCE[g["name"]]: return None, [f"combined chance now {pct(p)}, under the {pct(MIN_CHANCE[g['name']])} floor"]
    legs_.sort(key=lambda l: l.get("when") or "9")
    return {**{k: v for k, v in g.items() if k not in ("legs", "odds", "p", "implied", "status", "checked", "bestOdds")},
            "odds": round(o, 2), "p": round(p, 4), "implied": round(math.prod(l["implied"] for l in legs_), 4),
            "bestOdds": round(math.prod(max(l.get("best") or l["odds"], l["odds"]) for l in legs_), 2),
            "legs": legs_, "status": "holding"}, []

def card_slot(g):
    """A Card group's slot: (window, kind). One group per slot per day."""
    return (g.get("window"), g.get("name"))

def archived_card(date):
    """The locked Card groups in groupings-archive/<date>.json, one per slot
    (the first archived wins). 25 Oct 2026 (review bug 9): a locked group used
    to survive only through the published groupings.json; if Pages lagged, the
    next build made a fresh late group and the archive held two for one slot.
    The archive is now the source of truth for locked slots."""
    try:
        with open(os.path.join(ARCHIVE, f"{date}.json")) as f: a = json.load(f)
    except (OSError, ValueError):
        return []
    out, seen = [], set()
    for g in a.get("groups") or []:
        if not is_card(g.get("name")) or not g.get("locked") or not g.get("window"): continue
        if card_slot(g) in seen: continue
        seen.add(card_slot(g)); out.append(g)
    return out

def build_card(L, date, now, prev=None, log=None, archived=None):
    """The Card for one UK date: up to two groups in each window. L holds the
    day's legs (any board date); each is placed by its UK kick-off. A slot
    locked in the day's archive (archived, read from disk when None) is reused
    as it was archived, never rebuilt or duplicated; the last build's published
    groups (prev) fill the rest."""
    stamp = iso(now); after = now + timedelta(minutes=20)
    by_win = {w: [] for w, _, _ in CARD_WINDOWS}
    for l in L:
        s = uk_slot(l)
        if s and s[0] == date: by_win[s[1]].append(l)
    groups, used, filled = [], set(), set()
    if archived is None: archived = archived_card(date)
    for g in list(archived) + list(prev or []):
        if not is_card(g.get("name")) or g.get("window") not in by_win: continue
        slot = card_slot(g)
        if slot in filled: continue
        lock = lock_time(date, g["window"])
        if g.get("locked") or now >= lock:
            g = dict(g, locked=True, lockAt=iso(lock))
            g["status"] = "underway" if underway(g, now) else ("late" if g.get("late") else "locked")
            groups.append(g); used |= {l["event"] for l in g["legs"]}; filled.add(slot); continue
        if g.get("wide"): continue    # rebuilt below: a full-rule group takes its place when one can be made
        ng, why = recheck_card(g, by_win[g["window"]])
        if ng is None:
            if log is not None:
                log.append({"at": stamp, "name": g["name"], "rank": g["window"], "odds": g.get("odds"),
                            "picks": [l["pick"] for l in g["legs"]], "why": why})
            continue
        ng["checked"] = stamp; groups.append(ng); used |= {l["event"] for l in ng["legs"]}; filled.add(slot)
    replaced = {e["rank"] + "|" + e["name"] for e in (log or []) if e["at"] == stamp}
    for w, _, _ in CARD_WINDOWS:
        if now >= window_end(date, w): continue
        lock = lock_time(date, w)
        for name, _, _, _ in CARD_KINDS:
            if (w, name) in filled: continue
            g = best_card(by_win[w], used, after, name)
            if not g: continue
            late = now >= lock
            g.update(window=w, rank=w, first=stamp, checked=stamp, lockAt=iso(lock), locked=late, late=late,
                     status="late" if late else ("replacement" if f"{w}|{name}" in replaced else "new"))
            for l in g["legs"]: l.setdefault("firstOdds", l["odds"])
            used |= {l["event"] for l in g["legs"]}; filled.add((w, name)); groups.append(g)
    # The wider rule, only for a window the full rule left empty.
    for w, _, _ in CARD_WINDOWS:
        if now >= window_end(date, w) or any(f[0] == w for f in filled): continue
        lock = lock_time(date, w)
        for name, _, _, _ in CARD_KINDS:
            g = best_card(by_win[w], used, after, name, wide=True)
            if not g: continue
            late = now >= lock
            g.update(window=w, rank=w, first=stamp, checked=stamp, lockAt=iso(lock), locked=late, late=late,
                     status="late" if late else "new")
            for l in g["legs"]: l.setdefault("firstOdds", l["odds"])
            used |= {l["event"] for l in g["legs"]}; filled.add((w, name)); groups.append(g)
    order = {w: i for i, (w, _, _) in enumerate(CARD_WINDOWS)}
    return sorted(groups, key=lambda g: (order.get(g.get("window"), 9), g["name"]))

def card_windows(date):
    return [{"name": w, "from": a, "to": b, "lockAt": iso(lock_time(date, w))} for w, a, b in CARD_WINDOWS]

def archive_locked(day, generated):
    """Add each locked group to the day's archive file once. A group already
    there is never changed (update_closing adds closing prices only)."""
    locked = [g for g in day["groups"] if g.get("locked")]
    if not locked: return 0
    os.makedirs(ARCHIVE, exist_ok=True)
    path = os.path.join(ARCHIVE, f"{day['date']}.json")
    try:
        with open(path) as f: a = json.load(f)
    except (OSError, ValueError):
        a = {"date": day["date"], "published": generated, "groups": []}
    have = {gid(g) for g in a.get("groups") or []}
    # 25 Oct 2026 (review bug 9): one group per (window, kind) slot a day. A
    # slot already archived is never given a second group, whatever its picks.
    slots = {card_slot(g) for g in a.get("groups") or [] if is_card(g.get("name")) and g.get("window")}
    n = 0
    for g in locked:
        if gid(g) in have: continue
        if is_card(g.get("name")) and g.get("window") and card_slot(g) in slots: continue
        g = dict(g, archivedAt=generated)
        if g.get("late"):
            # A late group is built after its lock, so its published price is
            # already a post-lock price: it is the price at lock (bug 10).
            g["legs"] = [dict(l, lockPrice=l.get("lockPrice") or {"odds": l["odds"], "best": l.get("best") or l["odds"],
                                                                   "book": l.get("bestBook"), "at": generated})
                         if not l.get("est") else dict(l) for l in g["legs"]]
        a.setdefault("groups", []).append(g); have.add(gid(g)); slots.add(card_slot(g)); n += 1
    if n:
        with open(path, "w") as f: json.dump(a, f, indent=1, ensure_ascii=False)
    return n

# ---------- the re-check (21 Oct 2026) ----------
def gid(g):
    """A group's identity: its picks, whatever their prices."""
    return "|".join(sorted(f"{l['event']}>{l['pick']}" for l in g["legs"]))

def underway(g, now):
    return any((parse(l.get("when")) or now) <= now for l in g["legs"] if l.get("when"))

def leg_fault(l, wide=False):
    """Why a priced leg is no longer safe to group, in plain words, or None."""
    if wide:
        if wide_leg(l): return None
        if l.get("est") or l.get("fair") is None:
            return f"{l['pick']}: no bookmaker price and not a Daily List pick at {pct(WIDE_EST_MIN)}+"
        low = min(("model", l["pModel"]), ("bookmakers", l["fair"]), ("tested rate", l.get("pTested", l["p"])), key=lambda x: x[1])
        if low[1] < WIDE_MIN: return f"{l['pick']}: {low[0]} now {pct(low[1])}, under {pct(WIDE_MIN)}"
        return (f"{l['pick']}: the model ({pct(l['pModel'])}) now sits {round((l['pModel'] - l['fair']) * 100)} "
                f"points above the bookmakers ({pct(l['fair'])})")
    if l.get("est") or l.get("fair") is None:
        return f"{l['pick']}: no bookmaker price this build"
    if l["pModel"] < LEG_MIN:
        return f"{l['pick']}: the model now gives {pct(l['pModel'])}, under {pct(LEG_MIN)}"
    if l["fair"] < LEG_MIN:
        return f"{l['pick']}: price {l['odds']:.2f}, the bookmakers now give {pct(l['fair'])}, under {pct(LEG_MIN)}"
    if l.get("pTested", l["p"]) < LEG_MIN:
        return f"{l['pick']}: tested rate now {pct(l['pTested'])}, under {pct(LEG_MIN)}"
    if l["pModel"] - l["fair"] > MAX_ABOVE_BOOK:
        return (f"{l['pick']}: the model ({pct(l['pModel'])}) now sits {round((l['pModel'] - l['fair']) * 100)} "
                f"points above the bookmakers ({pct(l['fair'])})")
    return None

def pct(x): return f"{round(x * 100)}%"

def stale_price(cur, old):
    """This build's leg (unpriced) carrying the last confirmed price from the
    published leg, flagged stale, with fair and p recomputed on it."""
    cur = dict(cur, **{k: old[k] for k in ("odds", "best", "bestBook", "books", "margin", "src") if k in old}, est=False, stale=True)
    cur.pop("fair", None); cur["p"] = cur.get("pTested", cur["p"])
    return honest(cur)

def recheck(g, L):
    """Re-test a published group against this build's legs and prices.
    Returns (the group at today's prices, []) if every rule still holds, else
    (None, reasons). A leg missing from this build's pool has left the board as
    a clean pick: moved, postponed, flagged, or the model has changed its side."""
    by = {(l["event"], l["pick"]): l for l in L}
    legs_, why = [], []
    for old in g["legs"]:
        cur = by.get((old["event"], old["pick"]))
        if cur is None:
            why.append(f"{old['pick']}: no longer a clean pick for this day (moved, postponed, flagged or the model's side changed)")
            continue
        if cur.get("est") and not old.get("est") and old.get("odds"):
            # A price source that failed this build is not a reason to drop a
            # group: the last confirmed price stands, flagged, until a build
            # can read one again. The model's side of the check still runs.
            cur = stale_price(cur, old)
        fault = leg_fault(cur, wide=is_wide(g["name"]))
        if fault: why.append(fault); continue
        nl = dict(cur, firstOdds=old.get("firstOdds", old.get("odds")))
        legs_.append(nl)
    if why: return None, why
    name = g["name"]
    lo, hi = RANGE[name]
    o = ok_combo(legs_, lo, hi, name, LEGS_IN[name] if is_wide(name) else 0)
    p = math.prod(l["p"] for l in legs_)
    if o is None:
        return None, [f"combined price {math.prod(l['odds'] for l in legs_):.2f}, outside {lo:.2f} to {hi:.2f}"]
    if p < MIN_CHANCE[name]:
        return None, [f"combined chance now {pct(p)}, under the {pct(MIN_CHANCE[name])} floor"]
    legs_.sort(key=lambda l: l.get("when") or "9")
    return {**{k: v for k, v in g.items() if k not in ("legs", "odds", "p", "implied", "status", "checked")},
            "odds": round(o, 2), "p": round(p, 4), "implied": round(math.prod(l["implied"] for l in legs_), 4),
            "estimates": sum(1 for l in legs_ if l.get("est")), "legs": legs_, "status": "holding",
            "first": g.get("first") or g.get("checked")}, []

def previous():
    """The groups the last build published: {date: day}. Local file or the
    published copy, whichever is newer; {} when neither can be read, in which
    case every group this build is new."""
    best_ = {}
    cands = [load("groupings.json")]
    try: cands.append(get(PUBLISHED, timeout=20))
    except Exception: pass
    for c in cands:
        if c and c.get("generated", "") > best_.get("generated", ""): best_ = c
    out = {}
    for d in best_.get("days") or []:
        for g in d.get("groups") or []:
            g.setdefault("first", best_.get("generated"))   # groups from before 21 Oct carry no date
        out[d["date"]] = d
    return out

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

VOID_AFTER = 72 * 3600   # a football leg with no result this long after kick-off is void (25 Oct 2026)

def dead_fixtures(dates):
    """{(date, norm home, norm away)} of football fixtures API-Football marks
    postponed, cancelled, abandoned, awarded or suspended (sources.AF_DEAD) on
    these UTC dates, read from the cached day files only: grading never
    spends a call. Empty when the cache has no copy."""
    import gzip
    sys.path.insert(0, HERE)
    import sources as S
    out = set()
    for d in dates:
        path = os.path.join(S.AF_CACHE_DIR, f"day-{d}.json.gz")
        try:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                rows = json.load(fh).get("rows") or []
        except (OSError, ValueError):
            continue
        for c in rows:
            f = S._expand(c)
            if (f["fixture"].get("status") or {}).get("short") in S.AF_DEAD:
                when = f["fixture"].get("date") or ""
                h, a = f["teams"]["home"]["name"], f["teams"]["away"]["name"]
                out.add((when[:10], norm(h), norm(a)))
                out.add((d, norm(h), norm(a)))
    return out

def settle(l, idx, dead=None):
    fb, tn, sp = idx
    if l["sport"] == "football":
        r = fb.get((l["date"], norm(l["home"]), norm(l["away"]))) or fb.get((None, norm(l["home"]), norm(l["away"])))
        if not r:
            # 25 Oct 2026: a fixture the source marks postponed, cancelled or
            # abandoned is void, as a bookmaker settles it, and drops out of
            # the price. Until then it sat pending for ever (5 legs on 25 Oct).
            if dead and (l["date"], norm(l["home"]), norm(l["away"])) in dead: return "void", "postponed"
            return "pending", None
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

AVOID_GAP = 0.08      # the model this far above the market: the pattern that lost most
AVOID_MIN = 0.55      # only picks someone might back (Lean or better)

def avoid_list(dl, limit=12):
    """Picks to avoid for one day (25 Oct 2026). Two kinds, both from the
    weekend's losses and the archive:
      gap      the model sits AVOID_GAP+ above the bookmakers' fair chance.
               On 909 archived picks, 5-10 points above landed 47%, 10+ 42%,
               at the market's rate, not the model's (Oita Trinita, 63% v 50%,
               lost a five-fold on 25 Oct).
      off      a strong-looking pick from a sport kept off the Daily List on its
               live record (college football, tennis).
    Most suspect first."""
    out = []
    for l in dl:
        if l.get("est") or l.get("fair") is None or l["pModel"] < AVOID_MIN: continue
        gap = l["pModel"] - l["fair"]
        if gap >= AVOID_GAP:
            # 70%+ picks: the archive has only 5 with this gap (all won), so
            # they are marked caution, not avoid; under 70% it is 31 picks
            # quoted 61% that landed 35%.
            out.append({"pick": l["pick"], "event": l["event"], "sport": l["sport"], "comp": l.get("comp"), "when": l.get("when"),
                        "odds": l["odds"], "model": l["pModel"], "fair": l["fair"], "kind": "gap",
                        "level": "caution" if l["pModel"] >= 0.70 else "avoid", "score": gap})
        elif l.get("listOff") and l["pModel"] >= 0.70:
            out.append({"pick": l["pick"], "event": l["event"], "sport": l["sport"], "comp": l.get("comp"), "when": l.get("when"),
                        "odds": l["odds"], "model": l["pModel"], "fair": l["fair"], "kind": "off", "level": "avoid", "score": 0.05})
    return sorted(out, key=lambda x: (x["level"] != "avoid", -x["score"]))[:limit]

def check_pool(L):
    """Every priced pick, compact, for the page's slip checker (25 Oct 2026):
    paste a slip, see each pick's model and bookmaker chance and any flag."""
    return [{"s": l["sport"], "e": l["event"], "k": l["pick"], "d": l["date"], "o": l["odds"],
             "f": l.get("fair"), "m": l["pModel"], "x": 1 if l.get("listOff") else 0}
            for l in L if not l.get("est") and l.get("fair") is not None]

def update_closing(L, now, dates):
    """Closing prices for the record (25 Oct 2026, Douglas: "I need the model
    to beat the bookies' odds"). On every build, each archived leg that has not
    started takes this build's price for the same pick as lastOdds / lastBest.
    The last build before kick-off leaves the nearest thing to a closing price.
    A pick whose price shortens after we published it beat the closing line,
    the standard early sign of an edge; one that drifts did not. Only lastOdds,
    lastBest and lastAt are added: what was published is never changed."""
    by = {(l["event"], l["pick"]): l for l in L if not l.get("est") and l.get("odds")}
    for d in dates:
        path = os.path.join(ARCHIVE, f"{d}.json")
        if not os.path.exists(path): continue
        with open(path) as f: a = json.load(f)
        changed = False
        for g in a.get("groups") or []:
            lock = parse(g.get("lockAt")) if is_card(g.get("name")) else None
            for l in g.get("legs") or []:
                t = parse(l.get("when"))
                if t and t <= now: continue
                cur = by.get((l["event"], l["pick"]))
                if not cur: continue
                l.update(lastOdds=cur["odds"], lastBest=cur.get("best") or cur["odds"], lastAt=iso(now))
                # 25 Oct 2026 (review bug 10): the price at lock. A group is
                # priced by the last build before its lock, which can be hours
                # earlier, so the first build after the lock that still finds a
                # price records it once (lockPrice: average, best UK price and
                # its book), and the record grades returnedLock on it. A leg no
                # post-lock build has priced keeps lockPrice null.
                if lock and now >= lock and not l.get("lockPrice"):
                    l["lockPrice"] = {"odds": cur["odds"], "best": cur.get("best") or cur["odds"],
                                      "book": cur.get("bestBook"), "at": iso(now)}
                changed = True
        if changed:
            with open(path, "w") as f: json.dump(a, f, indent=1, ensure_ascii=False)

def archive(day, generated):
    os.makedirs(ARCHIVE, exist_ok=True)
    path = os.path.join(ARCHIVE, f"{day['date']}.json")
    if os.path.exists(path) or not day["groups"]: return False
    json.dump({"date": day["date"], "published": generated, "groups": day["groups"]}, open(path, "w"), indent=1, ensure_ascii=False)
    return True

def grade(now=None):
    now = now or datetime.now(timezone.utc)
    idx = results_index(); days = []
    files = sorted(f for f in os.listdir(ARCHIVE) if f.endswith(".json")) if os.path.isdir(ARCHIVE) else []
    files = files[-60:]
    try:
        dead = dead_fixtures({f[:-5] for f in files} | {l["date"] for f in files for g in json.load(open(os.path.join(ARCHIVE, f)))["groups"]
                                                     for l in g["legs"] if l.get("sport") == "football" and l.get("date")})
    except Exception:
        dead = set()
    for f in files:
        a = json.load(open(os.path.join(ARCHIVE, f))); gs = []
        for g in a["groups"]:
            legs = []
            for l in g["legs"]:
                st, res = settle(l, idx, dead)
                lp = l.get("lockPrice") or {}
                legs.append({"pick": l["pick"], "event": l["event"], "sport": l["sport"], "comp": l.get("comp"), "when": l.get("when"),
                             "odds": l["odds"], "best": max(l.get("best") or l["odds"], l["odds"]), "lastOdds": l.get("lastOdds"),
                             "lockOdds": lp.get("odds"), "lockBest": lp.get("best"), "lockBook": lp.get("book"),
                             "est": bool(l.get("est")), "p": l["p"], "status": st, "result": res})
            # 25 Oct 2026: a football leg still without a result VOID_AFTER
            # after kick-off, while every other leg has settled, was postponed
            # or abandoned without the source saying so. It is void and drops
            # out of the price, as a bookmaker settles it, so the group pays on
            # its remaining legs instead of sitting pending for ever.
            for l in legs:
                t = parse(l.get("when"))
                if l["status"] != "pending" or l["sport"] != "football" or not t: continue
                others = [x for x in legs if x is not l]
                if (now - t).total_seconds() >= VOID_AFTER and all(x["status"] != "pending" for x in others):
                    l["status"], l["result"] = "void", "no result"
            sts = [l["status"] for l in legs]
            status = "lost" if "lost" in sts else "won" if all(x in ("won", "void") for x in sts) else "pending"
            live = [l for l in legs if l["status"] != "void"]
            paid = math.prod(l["odds"] for l in live) if status == "won" else 0
            paid_best = math.prod(l["best"] for l in live) if status == "won" else 0
            # 25 Oct 2026 (bug 10): the return at the price at lock, only when
            # every paying leg has one; a group without is left out of that tally.
            at_lock = all(l["lockOdds"] for l in live) if live else False
            paid_lock = (math.prod(l["lockOdds"] for l in live) if status == "won" else 0) if at_lock else None
            # 25 Oct 2026 (review bug 1): wide, late, locked and lockAt were
            # dropped here, so wider-rule and post-lock groups were tallied as
            # the full Card. They travel with the graded row and are tallied apart.
            gs.append({"name": g["name"], "rank": g.get("rank", "main"), "window": g.get("window"), "odds": g["odds"], "p": g["p"], "status": status,
                       "wide": bool(g.get("wide")), "late": bool(g.get("late")), "locked": bool(g.get("locked")), "lockAt": g.get("lockAt"),
                       "paid": round(paid, 2), "paidBest": round(paid_best, 2),
                       "paidLock": round(paid_lock, 2) if paid_lock is not None else None,
                       "legsWon": sts.count("won"), "legsLost": sts.count("lost"),
                       "legsPending": sts.count("pending"), "legs": legs})
        days.append({"date": a["date"], "published": a.get("published"), "groups": gs})
    days.sort(key=lambda d: d["date"], reverse=True)
    def tally(groups):
        done = [g for g in groups if g["status"] != "pending"]
        legs = [l for g in groups for l in g["legs"] if l["status"] in ("won", "lost")]
        # closing line: each leg once (a leg can sit in more than one group)
        seen, clv = set(), []
        for g in groups:
            for l in g["legs"]:
                k = (l["event"], l["pick"])
                if k in seen or not l.get("lastOdds") or l.get("est"): continue
                seen.add(k); clv.append(l["odds"] / l["lastOdds"] - 1)
        return {"groups": len(groups), "settled": len(done), "won": sum(g["status"] == "won" for g in done),
                "lost": sum(g["status"] == "lost" for g in done), "pending": len(groups) - len(done),
                "legs": len(legs), "legsWon": sum(l["status"] == "won" for l in legs),
                "returned": round(sum(g["paid"] for g in done), 2), "staked": len(done),
                "returnedBest": round(sum(g.get("paidBest", g["paid"]) for g in done), 2),
                # 25 Oct 2026 (bug 10): at the price at lock, over the settled
                # groups that have one (stakedLock), so it reads against its own stake.
                "returnedLock": round(sum(g["paidLock"] for g in done if g.get("paidLock") is not None), 2),
                "stakedLock": sum(1 for g in done if g.get("paidLock") is not None),
                "expected": round(sum(g["p"] for g in done), 2),
                # 25 Oct 2026: published price v the last price before kick-off.
                # Positive = the price shortened after we published (beat the close).
                "clv": {"n": len(clv), "shortened": sum(1 for x in clv if x > 0.005),
                        "drifted": sum(1 for x in clv if x < -0.005),
                        "mean": round(sum(clv) / len(clv), 4) if clv else None}}
    allg = [g for d in days for g in d["groups"]]
    out = {"graded": iso(datetime.now(timezone.utc)), "overall": tally(allg),
           "byBand": {n: tally([g for g in allg if g["name"] == n])
                      for n in [c[0] for c in CARD_KINDS] + [b[0] for b in BANDS + WIDE_BANDS] + [m[0] for m in MULT_KINDS] + RETIRED
                      if n in [c[0] for c in CARD_KINDS] or any(g["name"] == n for g in allg)},
           # 25 Oct 2026: the Card is what the site puts forward; the older kinds
           # are no longer built and stay in the record under their names.
           "current": [c[0] for c in CARD_KINDS],
           "retired": RETIRED + [b[0] for b in BANDS + WIDE_BANDS] + [m[0] for m in MULT_KINDS],
           # 22 Oct 2026: the record headline is the groups the tab builds now,
           # strict and Wider apart; the retired kinds keep their own lines.
           "strict": tally([g for g in allg if g["name"] in LEGS_IN and not is_wide(g["name"])]),
           "wider": tally([g for g in allg if is_wide(g["name"])]),
           "multiplier": tally([g for g in allg if is_mult(g["name"])]),
           # The Card record is the full rule, locked on time. Wider-rule groups
           # (cardWide) and groups added after a window's lock (cardLate, any
           # rule) are tallied on their own lines and never count toward it.
           "card": tally([g for g in allg if is_card(g["name"]) and not g.get("wide") and not g.get("late")]),
           "cardWide": tally([g for g in allg if is_card(g["name"]) and g.get("wide") and not g.get("late")]),
           "cardLate": tally([g for g in allg if is_card(g["name"]) and g.get("late")]),
           "cardByWindow": {w: tally([g for g in allg if is_card(g["name"]) and not g.get("wide") and not g.get("late") and g.get("window") == w]) for w, _, _ in CARD_WINDOWS},
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
        if cur:
            pool = cur.pop("pool", None) or {}
            write_page(dict(cur, check=check_pool([l for v in pool.values() for l in v])), rec)
        print(f"groupings record: {rec['overall']}", file=sys.stderr); return
    probe = "--probe" in sys.argv
    now = datetime.now(timezone.utc)
    # Days are the board's own dates (UK days on the football board).
    today = now.astimezone(ZoneInfo("Europe/London")).date()
    dates = [(today + timedelta(days=i)).isoformat() for i in range(DAYS_AHEAD + 1)]
    L = legs(set(dates))
    report = price(L, set(dates))
    if probe:
        print(json.dumps(report, indent=1)); return
    prev = previous()
    days = []
    for d in dates:
        dl = [l for l in L if l["date"] == d]
        pd = prev.get(d) or {}
        log = list(pd.get("log") or [])
        # 25 Oct 2026: the Card replaces the older kinds as what is put forward.
        # Legs are placed by UK kick-off, so a day takes legs from every board date.
        groups = build_card(L, d, now, prev=pd.get("groups"), log=log)
        live = [g for g in groups if g.get("status") != "underway"]
        core = [l for l in dl if not l.get("multOnly")]   # the counts the page has always shown
        days.append({"date": d, "legs": len(core), "priced": sum(1 for l in core if not l.get("est")),
                     "safe": sum(1 for l in core if safe_leg(l)), "multLegs": sum(1 for l in dl if mult_leg(l)),
                     "groups": groups,
                     "checked": iso(now), "log": log[-LOG_KEEP:],
                     "windows": card_windows(d),
                     "cardLegs": sum(1 for l in L if uk_slot(l) and uk_slot(l)[0] == d and card_fault(l) is None),
                     "review": {s: sum(1 for g in groups if g.get("status") == s)
                                for s in ("new", "holding", "replacement", "underway", "locked", "late")},
                     "previously": len(pd.get("groups") or []) if pd else None,
                     "avoid": avoid_list(dl),
                     "dropped": sum(1 for e in log if e["at"] == iso(now))})
        report.setdefault("review", {})[d] = days[-1]["review"]
    out = {"generated": iso(now), "bands": BANDS,
           "kinds": [{"name": n, "legs": k, "minChance": f, "risk": RISK.get(n)} for n, k, f, _, _ in GROUP_KINDS + WIDE_KINDS]
                    + [{"name": n, "legs": list(MULT_LEGS), "minChance": f, "risk": RISK.get(n), "target": lo}
                       for n, lo, _, f in MULT_KINDS]
                    + [{"name": n, "legs": list(CARD_LEGS), "minChance": f, "risk": RISK.get(n), "target": lo}
                       for n, lo, _, f in CARD_KINDS],
           "rules": {"minReturn": MIN_RETURN, "minN": MIN_N, "minHit": MIN_HIT, "legMin": LEG_MIN, "maxAboveBook": MAX_ABOVE_BOOK,
                     "minGroups": MIN_GROUPS, "wideMin": WIDE_MIN, "wideAboveBook": WIDE_ABOVE_BOOK,
                     "wideEstMin": WIDE_EST_MIN,
                     "mult": {"odds": list(MULT_ODDS), "fairMin": MULT_FAIR_MIN, "modelMin": MULT_MODEL_MIN,
                              "aboveBook": MULT_ABOVE_BOOK, "legs": list(MULT_LEGS), "perDay": MULT_PER_DAY},
                     "card": {"odds": list(CARD_ODDS), "fairMin": CARD_FAIR_MIN, "modelMin": MULT_MODEL_MIN,
                              "wideOdds": list(CARD_WIDE_ODDS), "wideFairMin": CARD_WIDE_FAIR_MIN, "wideLegs": list(CARD_WIDE_LEGS),
                              "aboveBook": MULT_ABOVE_BOOK, "legs": list(CARD_LEGS),
                              "windows": [list(w) for w in CARD_WINDOWS]}},
           "sources": report, "days": days}
    # The full priced pool goes in the JSON only (the page does not need it),
    # so the office can regroup later in the day from games still to start.
    full = dict(out, pool={d: [l for l in L if l["date"] == d] for d in dates})
    json.dump(full, open(os.path.join(HERE, "groupings.json"), "w"), separators=(",", ":"))
    # 25 Oct 2026: the record is the locked Card, archived as each window locks.
    for d in days: archive_locked(d, out["generated"])
    update_closing(L, now, [(today + timedelta(days=i)).isoformat() for i in (-1, 0, 1)])
    record = grade()
    write_page(dict(out, check=check_pool(L)), record)
    print(f"groupings: {sum(len(d['groups']) for d in days)} groups over {len(days)} days; "
          f"{report['priced']} of {report['legs']} legs priced", file=sys.stderr)
    for d in days:
        r = d["review"]
        print(f"  {d['date']}: {r['holding']} holding, {r['replacement']} replaced, {r['new']} new, "
              f"{r['underway']} underway" + "".join(f"\n    dropped {e['name']} ({e['rank']}): {'; '.join(e['why'])}"
                                                   for e in d["log"] if e["at"] == d["checked"]), file=sys.stderr)

if __name__ == "__main__":
    main()
