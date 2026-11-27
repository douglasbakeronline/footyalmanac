"""The Mailer tab's emails, with how each pick went (25 Nov 2026, Douglas). mail_page.py.

Douglas, 25 Nov 2026: "the mailers tab has the sign up form ... underneath
... the emails that we send out in a horizontal scroll format ... a tick or a
cross ... 1 week back ... a little summary ... and maybe a data visualization
on how those picks are doing ... for now just a week".

For each of the last DAYS UK days that had a morning email (from MAIL_FROM,
the first one, and today only from 07:00 UK, when it goes), this writes the
email's contents with every pick's result:

- **sent**: `mail-archive/<day>.json`, written by mailer.py the moment the
  Daily List email went out (`mailer.snapshot`): exactly what it held.
- **rebuilt**: days before that archive began (23 to 25 Nov 2026). The list
  from daylist.json's pinned days in the email's 07:00 to 07:00 window
  (college basketball kept only at a recorded price of 1.05+, as the email's
  William Hill rule cannot be read back), the Daily 2x and the Card from
  groupings-record.json, the Edge picks from record.json. Marked "rebuilt" on
  the page: close to what was sent, not the copy itself.

Results are read, never graded here: list picks from daylist.json (each pinned
row's status), groups and their legs from groupings-record.json, Edge picks
from record.json's edge days. The trend is the same window: the Daily List's
landed rate against the model's chance by day, and the running units of the
Daily 2x, the Card (at its stake) and the Edge picks (one unit at the best
price). TREND_DAYS widens it (a month once a month of emails exists).

Writes mailbox.json and mailbox.js (window.__MAILBOX__), gitignored and
rebuilt by every deploy after mailer.py. Standard library only.
"""
import glob, gzip, json, os, sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mailer as M   # noqa: E402

MAIL_FROM = "2026-11-23"   # the first Daily List email (mailer.py, 23 Nov 2026)
DAYS = 7                   # the carousel: today and the six days before (Douglas: "1 week back")
TREND_DAYS = 7             # the chart's span; a month (30) once there are a month of emails
ARCHIVE = "mail-archive"
COLLEGE_MIN = 1.05         # mailer.LIST_PRICE_MIN for a rebuilt day, read off the ledger's price


def _json(path, default=None):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f: return json.load(f)
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default


def key(sport, home, away):
    return M.lb_key(sport, home, away)


def mail_days(today_uk, now_uk_hour):
    """The UK days to show, newest first: up to DAYS, never before MAIL_FROM,
    today only once its email has gone (07:00 UK)."""
    end = date.fromisoformat(today_uk)
    if now_uk_hour < M.SEND_FROM_H: end -= timedelta(days=1)
    out = []
    for i in range(DAYS):
        d = (end - timedelta(days=i)).isoformat()
        if d < MAIL_FROM: break
        out.append(d)
    return out


# ---------------------------------------------------------------- results

def list_results(daylist):
    """sport|home|away -> pinned row (status, result) for every day daylist.json holds."""
    out = {}
    days = [{"list": (daylist or {}).get("list") or []}] + list((daylist or {}).get("past") or [])
    for p in days:
        for it in p.get("list") or []:
            out[key(it.get("sport"), it.get("home"), it.get("away"))] = it
    for it in (daylist or {}).get("early") or []:
        out.setdefault(key(it.get("sport"), it.get("home"), it.get("away")), it)
    return out


def st_of(row):
    s = (row or {}).get("status")
    if s in ("won", "lost", "void"): return s
    if s == "started": return "live"
    return "open"


def group_results(grecord):
    """(date, name, seq) -> graded group from groupings-record.json days."""
    out = {}
    for d in (grecord or {}).get("days") or []:
        for g in d.get("groups") or []:
            out[(d.get("date"), g.get("name"), g.get("seq") or 1)] = g
    return out


def edge_results(record):
    """(date, pick, opp) -> 1/0 from record.json's edge days."""
    out = {}
    for d in ((record or {}).get("edge") or {}).get("days") or []:
        for p in d.get("p") or []:
            out[(d.get("d"), p[0], p[1])] = {"won": p[4], "odds": p[2], "best": p[3]}
    return out


def gst(g):
    s = (g or {}).get("status")
    return s if s in ("won", "lost", "void") else "open"


def leg_st(leg, graded):
    for l in (graded or {}).get("legs") or []:
        if l.get("pick") == leg.get("pick") and (l.get("event") or "") == (leg.get("event") or ""):
            return l.get("status") if l.get("status") in ("won", "lost", "void") else "open"
    return "open"


# ---------------------------------------------------------------- one day

def slim_group(g, graded):
    return {"name": g.get("name"), "seq": g.get("seq") or 1, "odds": g.get("odds"), "hill": g.get("hill"),
            "stake": g.get("stake") or 1, "p": g.get("p"), "short": bool(g.get("short")),
            "st": gst(graded), "paid": (graded or {}).get("paid"),
            "legs": [{**l, "st": leg_st(l, graded)} for l in g.get("legs") or []]}


def from_sent(snap, LR, GR, ER):
    day = snap["day"]
    lst = []
    for it in snap.get("list") or []:
        r = LR.get(key(it.get("sport"), it.get("home"), it.get("away")))
        lst.append({**it, "st": st_of(r), "score": ((r or {}).get("result") or {}).get("score")})
    daily = snap.get("daily")
    daily = slim_group(daily, GR.get((day, "Daily 2x", daily.get("seq") or 1))) if daily else None
    cards = [slim_group(g, GR.get((day, g.get("name"), g.get("seq") or 1))) for g in snap.get("cards") or []]
    edge = []
    for e in snap.get("edge") or []:
        k = M.parse_utc(e.get("kickoff"))
        dates = [k.date().isoformat()] if k else []
        r = next((ER[(d, e["pick"], e["opp"])] for d in dates + [day] if (d, e["pick"], e["opp"]) in ER), None)
        edge.append({**e, "st": ("won" if r["won"] else "lost") if r else "open"})
    return {"day": day, "source": "sent", "sentAt": snap.get("sentAt"), "subject": snap.get("subject"),
            "list": lst, "daily": daily, "cards": cards, "cardShort": snap.get("cardShort"), "edge": edge}


def ledger_price(ledger_rows, sport, home, away):
    for r in ledger_rows.get(key(sport, home, away)) or []:
        for k in ("last", "first"):
            o = (r.get(k) or {}).get("o")
            if o: return float(o)
    return None


def rebuilt(day, daylist, grecord, record, ledger_rows, ER):
    """A day before mail-archive/ began, rebuilt from the committed records."""
    lo, hi = M.window(day)
    nxt = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    pool = []
    for p in [{"date": (daylist or {}).get("date"), "list": (daylist or {}).get("list") or []}] + list((daylist or {}).get("past") or []):
        if p.get("date") in (day, nxt):
            for it in p.get("list") or []:
                if it.get("list") is False: continue
                t = M.parse_utc(it.get("start"))
                if t is None:
                    if p.get("date") == day: pool.append(it)
                elif lo <= t < hi: pool.append(it)
    lst = []
    for it in pool:
        if it.get("sport") == "ncaab":
            px = ledger_price(ledger_rows, it.get("sport"), it.get("home"), it.get("away"))
            if not (px and px >= COLLEGE_MIN): continue
        lst.append(it)
    lst.sort(key=lambda it: it.get("confidence") or 0, reverse=True)
    nA = min(5, sum(1 for it in lst if (it.get("confidence") or 0) >= M.GROUP_A_MIN))
    out = [{"sport": it.get("sport"), "home": it.get("home"), "away": it.get("away"), "pick": it.get("pick"),
            "comp": it.get("comp"), "start": it.get("start"), "timed": it.get("timed", True),
            "conf": it.get("confidence"), "A": i < nA, "st": st_of(it), "score": (it.get("result") or {}).get("score")}
           for i, it in enumerate(lst)]
    gday = next((d for d in (grecord or {}).get("days") or [] if d.get("date") == day), {}) or {}

    def g_of(g):
        return {"name": g.get("name"), "seq": g.get("seq") or 1, "odds": g.get("odds"), "hill": None,
                "stake": g.get("stake") or 1, "p": g.get("p"), "short": False, "st": gst(g), "paid": g.get("paid"),
                "legs": [{"pick": l.get("pick"), "event": l.get("event"), "sport": l.get("sport"), "comp": l.get("comp"),
                          "when": l.get("when"), "odds": l.get("odds"), "p": l.get("p"),
                          "st": l.get("status") if l.get("status") in ("won", "lost", "void") else "open"}
                         for l in g.get("legs") or []]}
    groups = gday.get("groups") or []
    daily = next((g_of(g) for g in groups if g.get("name") == "Daily 2x"), None)
    cards = [g_of(g) for g in groups if str(g.get("name") or "").startswith("Card") and not g.get("wide")]
    edge = []
    for d in ((record or {}).get("edge") or {}).get("days") or []:
        if d.get("d") == day:
            edge += [{"pick": p[0], "opp": p[1], "odds": p[2], "best": p[3], "st": "won" if p[4] else "lost"} for p in d.get("p") or []]
    return {"day": day, "source": "rebuilt", "subject": None, "list": out, "daily": daily, "cards": cards,
            "cardShort": None if cards else "No Card group that day.", "edge": edge}


def summary(d):
    t = lambda xs: {"won": sum(x["st"] == "won" for x in xs), "lost": sum(x["st"] == "lost" for x in xs),
                    "open": sum(x["st"] not in ("won", "lost", "void") for x in xs), "n": len(xs)}
    return {"list": t(d["list"]), "edge": t(d["edge"]),
            "daily": d["daily"]["st"] if d.get("daily") else None,
            "cards": [g["st"] for g in d.get("cards") or []]}


# ---------------------------------------------------------------- the trend

def units(g):
    """(staked, returned) for a settled group at the page's stakes; None while open."""
    if not g or g["st"] not in ("won", "lost", "void"): return None
    stake = g.get("stake") or 1
    if g["st"] == "void": return (0.0, 0.0)
    return (float(stake), float(stake) * float(g.get("paid") or 0) if g["st"] == "won" else 0.0)


def trend(days):
    """Oldest first, over the last TREND_DAYS of `days`."""
    xs = sorted(days, key=lambda d: d["day"])[-TREND_DAYS:]
    out = {"days": [d["day"] for d in xs], "list": [], "daily": [], "card": [], "edge": []}
    for d in xs:
        s = [x for x in d["list"] if x["st"] in ("won", "lost")]
        out["list"].append({"day": d["day"], "won": sum(x["st"] == "won" for x in s), "n": len(s),
                            "quoted": round(sum(x.get("conf") or 0 for x in s) / len(s), 4) if s else None,
                            "open": sum(x["st"] not in ("won", "lost", "void") for x in d["list"])})
        u = units(d.get("daily"))
        out["daily"].append({"day": d["day"], "staked": u[0] if u else 0, "net": round(u[1] - u[0], 2) if u else 0,
                             "st": d["daily"]["st"] if d.get("daily") else None})
        cs = [units(g) for g in d.get("cards") or []]
        cs = [c for c in cs if c]
        out["card"].append({"day": d["day"], "staked": sum(c[0] for c in cs), "net": round(sum(c[1] - c[0] for c in cs), 2),
                            "st": ",".join(g["st"] for g in d.get("cards") or []) or None})
        es = [e for e in d["edge"] if e["st"] in ("won", "lost")]
        out["edge"].append({"day": d["day"], "staked": len(es),
                            "net": round(sum((float(e.get("best") or e.get("odds") or 0) - 1) if e["st"] == "won" else -1 for e in es), 2),
                            "st": f"{sum(e['st'] == 'won' for e in es)}/{len(es)}" if es else None})
    return out


# ---------------------------------------------------------------- build

def build(root=HERE, now=None):
    now = now or datetime.now(timezone.utc)
    now_uk = now.astimezone(M.UK)
    p = lambda n: os.path.join(root, n)
    daylist = _json(p("daylist.json")) or M._js(p("daylist.js")) or {}
    grecord, record = _json(p("groupings-record.json")) or {}, _json(p("record.json")) or {}
    L = _json(p("results-ledger.json.gz")) or {}
    ledger_rows = {}
    for r in L.get("rows") or []:
        if r.get("start", "") >= MAIL_FROM: ledger_rows.setdefault(key(r.get("sport"), r.get("home"), r.get("away")), []).append(r)
    LR, GR, ER = list_results(daylist), group_results(grecord), edge_results(record)
    days = []
    for d in mail_days(now_uk.date().isoformat(), now_uk.hour):
        snap = _json(p(os.path.join(ARCHIVE, f"{d}.json")))
        x = from_sent(snap, LR, GR, ER) if snap and snap.get("day") == d else rebuilt(d, daylist, grecord, record, ledger_rows, ER)
        x["summary"] = summary(x)
        days.append(x)
    return {"generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "from": MAIL_FROM, "span": DAYS, "trendDays": TREND_DAYS,
            "days": days, "trend": trend(days)}


def write(out, root=HERE):
    with open(os.path.join(root, "mailbox.json"), "w", encoding="utf-8") as f: json.dump(out, f, separators=(",", ":"))
    with open(os.path.join(root, "mailbox.js"), "w", encoding="utf-8") as f:
        f.write("window.__MAILBOX__ = " + json.dumps(out, separators=(",", ":")) + ";\n")


def main():
    out = build()
    write(out)
    for d in out["days"]:
        s = d["summary"]
        print(f"mailbox {d['day']} ({d['source']}): list {s['list']['won']} won, {s['list']['lost']} lost, {s['list']['open']} open; "
              f"Daily 2x {s['daily'] or 'none'}; Card {', '.join(s['cards']) or 'none'}; Edge {s['edge']['won']}/{s['edge']['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
