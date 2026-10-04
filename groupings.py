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
group's chance is the product of its legs' tested rates, shrunk toward the
model's own number when the tested sample is small:

    p_leg = (hit * n + p_model * 30) / (n + 30)

A leg needs a tested rate (n >= 30), a tested rate of at least 65%, and must
be one the board does not flag (football: rated, not a draw pick).

Where the prices come from
--------------------------
  football        API-Football /odds (Match Winner, every bookmaker on the
                  fixture; average and best), matched to our games by date,
                  kick-off within 90 minutes, and both team names
  NFL, MLB, NBA   ESPN scoreboards (DraftKings moneyline), matched by ESPN id
  tennis, rugby   no free source yet: the model's fair price (1 / p), marked
                  as an estimate, and at most two estimates in any group

How a group is chosen
---------------------
Three bands by combined odds: Steady 2.5-4, Balanced 4-7, Stretch 7-14. In
each band the five legs with the highest joint tested chance, subject to:
  - a spread of prices: at least one short leg (under 1.30), at least one
    middle leg (1.30-1.60), and Balanced and Stretch at least one leg 1.60+
  - at most two very short legs (under 1.15), which add risk but little return
  - at most two estimated prices (more only if priced legs cannot fill the
    group at all, and the group shows how many)
  - one leg per game, no more than two from one competition
  - a small preference for mixing sports, and for legs where the tested rate
    beats the bookmaker's implied chance
Then a second, separate group per band ("alternative") from the legs left.
Today and tomorrow, so six groups a day, none sharing a leg.

Standard library only.
"""
import itertools, json, math, os, re, sys, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
AF_BASE = "https://v3.football.api-sports.io"
ESPN = "https://site.api.espn.com/apis/site/v2/sports"
ESPN_PATH = {"nfl": "football/nfl", "mlb": "baseball/mlb", "nba": "basketball/nba"}
BANDS = [("Steady", 2.5, 4.0), ("Balanced", 4.0, 7.0), ("Stretch", 7.0, 14.0)]
MIN_N, MIN_HIT, SHRINK = 30, 0.65, 30
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
    if not acc or not acc.get("n") or acc.get("hit") is None: return None
    n = acc["n"]
    if n < MIN_N or acc["hit"] < MIN_HIT: return None
    return (acc["hit"] * n + p * SHRINK) / (n + SHRINK)

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
                        "pick": h if side == "h" else a, "comp": g.get("leagueName"), "country": g.get("country"),
                        "when": g.get("kickoff"), "date": day["date"], "pModel": round(p[side], 4), "p": round(pl, 4),
                        "hit": g["accuracy"]["hit"], "n": g["accuracy"]["n"], "list": bool(g.get("list"))})
    td = read_js("tennis-data.js") or {}
    for m in td.get("matches") or []:
        when = f"{m['date']}T{m['time']}:00Z" if m.get("time") else None
        d = m.get("date")
        if d not in dates or "qualif" in (m.get("round") or "").lower(): continue
        pl = leg_p(m.get("confidence") or 0, m.get("accuracy"))
        if pl is None: continue
        out.append({"sport": "tennis", "event": f"{m['playerA']} v {m['playerB']}", "pick": m["pick"],
                    "comp": f"{m.get('tournament')} {m.get('round') or ''}".strip(), "when": when, "date": d, "id": m.get("id"),
                    "pModel": round(m["confidence"], 4), "p": round(pl, 4), "hit": m["accuracy"]["hit"], "n": m["accuracy"]["n"],
                    "list": bool(m.get("list"))})
    sd = read_js("sports-data.js") or {}
    for key, sp in (sd.get("sports") or {}).items():
        if not sp.get("published"): continue
        for g in sp.get("games") or []:
            t = parse(g.get("when"))
            if not t or t.date().isoformat() not in dates: continue
            pl = leg_p(g.get("confidence") or 0, g.get("accuracy"))
            if pl is None: continue
            out.append({"sport": key, "event": f"{g['home']} v {g['away']}", "home": g["home"], "away": g["away"],
                        "pick": g["pick"], "comp": g.get("label") or sp.get("name"), "when": g.get("when"), "date": t.date().isoformat(),
                        "id": g.get("id"), "pModel": round(g["confidence"], 4), "p": round(pl, 4),
                        "hit": g["accuracy"]["hit"], "n": g["accuracy"]["n"], "list": bool(g.get("list"))})
    return out

# ---------- prices ----------
def af(path, key):
    return get(AF_BASE + path, {"x-apisports-key": key})

def price_football(L, dates, report):
    key = os.environ.get("API_FOOTBALL_KEY")
    fb = [l for l in L if l["sport"] == "football"]
    if not key or not fb:
        report["football"] = "no key" if not key else "no legs"; return
    calls, matched = 0, 0
    for d in sorted(dates):
        try:
            fx = af(f"/fixtures?date={d}&timezone=UTC", key); calls += 1
        except Exception as e:
            report.setdefault("errors", []).append(f"fixtures {d}: {type(e).__name__}"); continue
        teams = {f["fixture"]["id"]: (f["teams"]["home"]["name"], f["teams"]["away"]["name"], parse(f["fixture"]["date"]))
                 for f in fx.get("response") or []}
        odds, page, total = {}, 1, 1
        while page <= total and page <= 60:
            try:
                r = af(f"/odds?date={d}&bet=1&page={page}&timezone=UTC", key); calls += 1
            except Exception as e:
                report.setdefault("errors", []).append(f"odds {d} p{page}: {type(e).__name__}"); break
            total = (r.get("paging") or {}).get("total") or 1
            for item in r.get("response") or []:
                prices = {"Home": [], "Away": [], "Draw": []}
                books = set()
                for b in item.get("bookmakers") or []:
                    for bet in b.get("bets") or []:
                        if bet.get("id") != 1: continue
                        for v in bet.get("values") or []:
                            try: prices[v["value"]].append(float(v["odd"])); books.add(b.get("name"))
                            except (KeyError, ValueError): pass
                odds[item["fixture"]["id"]] = (prices, sorted(books))
            page += 1
        for l in fb:
            if l["date"] != d or l.get("odds"): continue
            t = parse(l["when"])
            for fid, (h, a, ft) in teams.items():
                if fid not in odds: continue
                if t and ft and abs((t - ft).total_seconds()) > 5400: continue
                if not (same(h, l["home"]) and same(a, l["away"])): continue
                prices, books = odds[fid]
                side = prices["Home" if l["side"] == "h" else "Away"]
                if side:
                    l.update(odds=round(sum(side) / len(side), 2), best=round(max(side), 2), books=len(books),
                             src="API-Football, average of " + (f"{len(books)} bookmakers" if len(books) != 1 else books[0]))
                    matched += 1
                break
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
            try: sb = get(f"{ESPN}/{path}/scoreboard?dates={d.replace('-', '')}")
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
                    l.update(odds=dec, src=f"ESPN, {o.get('provider', {}).get('name', 'bookmaker')} moneyline"); n += 1
        out[sport] = {"matched": n, "legs": len(want)}
    report["espn"] = out

def price(L, dates):
    report = {}
    price_football(L, dates, report)
    price_espn(L, dates, report)
    for l in L:
        if not l.get("odds"):
            l.update(odds=round(1 / l["pModel"], 2), est=True, src="estimate: the model's fair price, no bookmaker price found")
        l["implied"] = round(1 / l["odds"], 4)
        l["edge"] = round(l["p"] * l["odds"] - 1, 4)
    report["priced"] = sum(1 for l in L if not l.get("est")); report["legs"] = len(L)
    return report

# ---------- groups ----------
def ok_combo(c, lo, hi, name, max_est=2):
    o = math.prod(l["odds"] for l in c)
    if not (lo <= o <= hi): return None
    if len({l["event"] for l in c}) < 5: return None
    if sum(l["odds"] < 1.15 for l in c) > 2 or sum(1 for l in c if l.get("est")) > max_est: return None
    if not any(l["odds"] < 1.30 for l in c) or not any(1.30 <= l["odds"] < 1.60 for l in c): return None
    if name != "Steady" and not any(l["odds"] >= 1.60 for l in c): return None
    comps = {}
    for l in c: comps[l.get("comp")] = comps.get(l.get("comp"), 0) + 1
    if max(comps.values()) > 2: return None
    return o

def pool(L, used, after):
    c = [l for l in L if l["event"] not in used and 1.05 <= l["odds"] <= 2.8 and (parse(l["when"]) or after) >= after]
    # Keep the strongest legs in each price range, so every band can be met
    # without trying every combination of several hundred legs.
    rng = lambda lo, hi, k: sorted([l for l in c if lo <= l["odds"] < hi], key=lambda l: -l["p"])[:k]
    return rng(1.05, 1.30, 12) + rng(1.30, 1.60, 12) + rng(1.60, 2.81, 9)

def best(L, used, after, name, lo, hi):
    # At most two estimated prices; only when the priced legs cannot fill a
    # group at all does it fall back to more, and the group says so.
    return _best(L, used, after, name, lo, hi, 2) or _best(L, used, after, name, lo, hi, 5)

def _best(L, used, after, name, lo, hi, max_est):
    top = None
    for c in itertools.combinations(pool(L, used, after), 5):
        o = ok_combo(c, lo, hi, name, max_est)
        if o is None: continue
        p = math.prod(l["p"] for l in c)
        sports = len({l["sport"] for l in c})
        value = sum(1 for l in c if not l.get("est") and l["edge"] > 0)
        score = p * (1 + 0.03 * (sports - 1)) * (1 + 0.02 * value)
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
    rec, trec, srec = load("record.json"), load("tennis-record.json"), load("sports-record.json")
    fb = {}
    for d in rec.get("days") or []:
        for g in d.get("games") or []:
            if g.get("result"): fb[(d.get("date"), norm(g["home"]), norm(g["away"]))] = g["result"]
            if g.get("result"): fb.setdefault((None, norm(g["home"]), norm(g["away"])), g["result"])
    tn = {str(g.get("key")): g for d in trec.get("days") or [] for g in d.get("games") or []}
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
    out = {"generated": iso(now), "bands": BANDS, "rules": {"minN": MIN_N, "minHit": MIN_HIT, "shrink": SHRINK},
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
