"""The Sports Almanac emails, sent with Resend (23 Nov 2026, Douglas).

Two emails, both built from the files the build has already written, never
from the page's HTML and never regraded:

- **The Daily List** at 07:00 UK every morning, about today's UK day: the
  Daily List (one list, strongest first; not the reserve) with the page's own
  display rules, the Daily 2x, the Card (or the page's reason there is none),
  the Edge picks and, for subscribers who ticked Scale, the day's Scale bets
  from the Daily List tier and the Scale groups.
- **The Weekly Record** on Saturday at 07:00 UK (the sign-up form's "sunday"
  column), the seven UK days Saturday to Friday just ended: the Daily List
  landed v quoted by sport, the strongest wins and the misses, each card's
  week in the ledger's headline pattern, and the list at William Hill's prices.

Sources (read, never written): daylist.json (daylist.py), groupings-data.js
(groupings.py: listBooks, prices, contexts, each day's groups and cardShort),
data.json (build.py: the football board's Edge flags), scale.json (scale.py),
slip.json (slip.py), results-ledger.json.gz (ledger.py), groupings-record.json,
record.json (edge), sports-data.js (sport names).

Sending: the subscriber list and a once-a-day claim come from two Supabase
functions (almanac_mail_list, almanac_mail_claim) that need MAILER_SECRET;
the emails go one per recipient through Resend's batch endpoint, at most 100
a call and two calls a second, each with a one-click List-Unsubscribe header
and its own manage and unsubscribe links. Silent and exit 0 without
RESEND_API_KEY or MAILER_SECRET, like notify.py. Never prints an address.

  python3 mailer.py                      # CI: send what is due now (07:00-11:59 UK)
  python3 mailer.py --preview DIR        # write daily/weekly .html and .txt, no network
  python3 mailer.py --preview DIR --day 2026-11-21
  python3 mailer.py --to you@example.com --kind weekly   # one test copy, no claim

Standard library only. claude/mailer-2026-11-23.md.
"""
import argparse, gzip, html, json, os, re, sys, time, urllib.error, urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
UK = ZoneInfo("Europe/London")

SITE = "https://sportsalmanac.bet/"
SUPABASE_URL = "https://nangcsyicqfvfawyvkus.supabase.co"
SUPABASE_KEY = "sb_publishable_aNDvbiKjeNgZx9iIg75tZw_vQDmP28F"   # the page's publishable key (index.html)
RESEND_BATCH = "https://api.resend.com/emails/batch"
SENDER = "Sports Almanac <list@sportsalmanac.bet>"
HEADER_IMG = os.environ.get("MAILER_HEADER_IMG") or SITE + "email-header.png"   # the site's cover header (deploy.yml publishes it); tests may point elsewhere
UNSUB_URL = SUPABASE_URL + "/functions/v1/almanac-unsubscribe?t={t}"
MANAGE_URL = SITE + "#mailer?manage={t}"
TEST_TOKEN = "00000000-0000-0000-0000-000000000000"   # previews and test copies: links that change nothing
MANAGE_MARK, UNSUB_MARK = "%%MANAGE_URL%%", "%%UNSUB_URL%%"
TOKEN_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

SEND_FROM_H, SEND_TO_H = 7, 12      # 07:00 to 11:59 UK; a missed morning is skipped, never sent late
WEEKLY_DOW = 5                      # Saturday
BATCH_MAX = 100                     # Resend's batch limit
RATE_GAP_S = 0.5                    # Resend: two requests a second
RETRIES = 2                         # a 429, a 5xx or a lost connection, twice more with backoff

# The page's display rules (index.html), kept equal by hand: see each comment.
GROUP_A_MIN = 0.85                  # GROUP_A_MIN
LIST_PRICE_MIN = {"ncaab": 1.05}    # listPriceMin: the best price on file, any source (27 Nov 2026)
WIN_FB_MAX = 1.40                   # WIN_FB_MAX
BOOK_GAP = 0.10                     # BOOK_GAP
TIER_MIN, TIER_BANKER, TIER_CAUTION, TIER_WAIT_H = 0.70, 12, 6, 18   # collegeTier
WARY_SPORTS = {"ncaab", "cfb"}      # sideWary
BOOK = "William Hill"

SPORT_NAMES = {"football": "Football", "tennis": "Tennis", "nfl": "NFL", "nba": "NBA", "wnba": "WNBA",
               "mlb": "Baseball", "ncaab": "College basketball", "cfb": "College football",
               "rugby": "Rugby", "nhl": "Ice hockey"}

# Look: the site's cover (index.html :root)
PAPER, SURFACE, INK, INK2, MUTE, RULE = "#f0e8d6", "#fbf6ea", "#1a1511", "#4b4038", "#6e6355", "#c6b89e"
RED, YELLOW, YELLOW_SOFT, GREEN, GREEN_SOFT = "#c8102e", "#f4d21c", "#fbf0bf", "#1c6b3a", "#dcebdf"
# The site's three faces (index.html --f-display, --f-ui, --f-num), loaded where the mail app allows web
# fonts (Apple Mail, iOS) and falling back to the nearest system face elsewhere (Gmail, Outlook).
F_DISPLAY = "Anton, Impact, 'Arial Narrow Bold', 'Arial Narrow', sans-serif"
F_UI = "'Barlow Semi Condensed', 'Arial Narrow', 'Helvetica Neue', Helvetica, Arial, sans-serif"
F_NUM = "'IBM Plex Mono', Menlo, Consolas, 'Courier New', monospace"
F_HEAD, F_BODY, F_MONO = F_DISPLAY, F_UI, F_NUM
F_SERIF = "Georgia, 'Times New Roman', serif"
FONTS_LINK = "https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Semi+Condensed:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap"


# ---------------------------------------------------------------- reading

def _json(path, default=None):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f: return json.load(f)
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default


def _js(path, default=None):
    """A `window.__X__ = {...};` file as data."""
    try:
        with open(path, encoding="utf-8") as f: s = f.read()
        s = s[s.index("=") + 1:].strip().rstrip(";").strip()
        return json.loads(s)
    except Exception:
        return default


def load(root=HERE):
    """Every file the emails read, as data. A missing file is None, never an error."""
    p = lambda n: os.path.join(root, n)
    return {"daylist": _json(p("daylist.json")) or _js(p("daylist.js")),
            "groupings": _js(p("groupings-data.js")) or _json(p("groupings.json")),
            "data": _json(p("data.json")) or _js(p("data.js")),
            "scale": _json(p("scale.json")) or _js(p("scale.js")),
            "slip": _json(p("slip.json")) or _js(p("slip.js")),
            "sports": _js(p("sports-data.js")),
            "ledger": _json(p("results-ledger.json.gz")),
            "grecord": _json(p("groupings-record.json")),
            "record": _json(p("record.json"))}


# ---------------------------------------------------------------- small helpers

E = lambda s: html.escape(str(s if s is not None else ""), quote=True)
pct = lambda x: f"{round((x or 0) * 100)}%"


def lb_key(sport, home, away):
    return f"{sport}|{str(home or '').lower()}|{str(away or '').lower()}"


def name_of(x):
    return x.get("name") if isinstance(x, dict) else x


def parse_utc(s):
    if not s: return None
    s = str(s).replace("Z", "+00:00")
    if re.match(r".*T\d\d:\d\d\+", s): s = s.replace("+", ":00+", 1)
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def uk_time(s):
    d = parse_utc(s)
    return d.astimezone(UK).strftime("%H:%M") if d else ""


def long_day(day):
    d = date.fromisoformat(day)
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B %Y')}"


def short_day(day):
    d = date.fromisoformat(day)
    return f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"


def sport_name(src, k):
    sp = ((src.get("sports") or {}).get("sports") or {}).get(k) or {}
    return sp.get("name") or SPORT_NAMES.get(k) or k


def signed(x, dp=2):
    return ("+" if x >= 0 else "−") + f"{abs(x):.{dp}f}"


def signed_pc(net, staked):
    if not staked: return ""
    v = round(net / staked * 100)
    return ("+" if net >= 0 else "−") + f"{abs(v)}%"


# ---------------------------------------------------------------- the page's row rules

def tennis_game(m):
    """tennisAsGame, the fields the rules read."""
    when = f"{m.get('date')}T{m['time']}:00Z" if m.get("time") and not m.get("timeTbc") else f"{m.get('date')}T12:00:00Z"
    return {"sport": "tennis", "home": m.get("playerA"), "away": m.get("playerB"), "pick": m.get("pick"),
            "confidence": m.get("confidence"), "list": m.get("list"), "when": when, "neutral": False}


def item_game(it):
    """itemGame: the full row behind a pinned list item, in the page's shape, and its sport."""
    f, sport = it.get("full"), it.get("sport")
    if not f:
        g = dict(it)
        if sport == "football":
            g["home"], g["away"] = {"name": it.get("home")}, {"name": it.get("away")}
        return g, sport
    if sport == "tennis": return tennis_game(f), sport
    return f, sport


def tier_game(it):
    """itemTier's merge: the slim pinned copy over its full row, line and venue from the full row."""
    f = it.get("full") or {}
    return {**f, **it, "line": f.get("line"), "neutral": f.get("neutral")}


def college_tier(g, now):
    if not g or g.get("sport") != "ncaab" or not ((g.get("confidence") or 0) >= TIER_MIN): return None
    home = g.get("pick") == name_of(g.get("home"))
    sp = (g.get("line") or {}).get("spread")
    try: by = None if sp is None else (-float(sp) if home else float(sp))
    except (TypeError, ValueError): by = None
    if not home and not g.get("neutral"): return "leave"
    if by is not None and by < TIER_CAUTION: return "leave"
    if g.get("neutral") or (by is not None and by < TIER_BANKER): return "caution"
    if by is not None: return "banker"
    t = parse_utc(g.get("when") or g.get("start"))
    if t and (t - now).total_seconds() > TIER_WAIT_H * 3600: return None
    return "solid"


def tennis_wary(g):
    return g.get("sport") == "tennis" and (g.get("confidence") or 0) < 0.80


def side_wary(g):
    if g.get("sport") not in WARY_SPORTS or not ((g.get("confidence") or 0) >= 0.70): return False
    if g.get("neutral"): return True
    return bool(g.get("pick") and g.get("home") and g.get("pick") != name_of(g.get("home")))


def trail_wary(g):
    if g.get("sport") != "ncaab" or not ((g.get("confidence") or 0) >= 0.70) or not g.get("when"): return False
    if str(g["when"])[5:7] not in ("11", "12"): return False
    rec = g.get("recordH") if g.get("pick") == g.get("home") else g.get("recordA") if g.get("pick") == g.get("away") else None
    if not rec: return False
    w, l = rec.get("w") or 0, rec.get("l") or 0
    return w + l >= 3 and l > w


def pick_side(g, sport):
    if sport == "football":
        p = g.get("p") or {}
        if not p: return None
        mp = [p.get("h") or 0, p.get("d") or 0, p.get("a") or 0]
        i = mp.index(max(mp))
        return "h" if i == 0 else "a" if i == 2 else None
    pick = g.get("pick")
    return "h" if pick == name_of(g.get("home")) else "a" if pick == name_of(g.get("away")) else None


def ml_fair(line, side):
    def imp(ml):
        try: ml = float(ml)
        except (TypeError, ValueError): return None
        if not ml: return None
        return -ml / (-ml + 100) if ml < 0 else 100 / (ml + 100)
    if not line: return None
    h, a = imp(line.get("mlH")), imp(line.get("mlA"))
    if h is None or a is None or h + a <= 0: return None
    return (h if side == "h" else a) / (h + a)


def book_gap(g, sport, G):
    conf = g.get("confidence")
    if not conf: return False
    side = pick_side(g, sport)
    if not side: return False
    home, away = name_of(g.get("home")), name_of(g.get("away"))
    pick = home if side == "h" else away
    q = ((G or {}).get("prices") or {}).get(lb_key(sport, home, away))
    fair = None
    if q and q.get("f") is not None and (not q.get("p") or q.get("p") == pick): fair = float(q["f"])
    elif (g.get("market") or {}).get("p"):
        fair = (g["market"]["p"][0 if side == "h" else 2]) or None
    if fair is None: fair = ml_fair(g.get("line"), side)
    return fair is not None and conf - fair >= BOOK_GAP


def pick_price(g, sport, side, G):
    """pickPrice: Hill's, else the average, else football's best on file."""
    home, away = name_of(g.get("home")), name_of(g.get("away"))
    pick = home if side == "h" else away
    k = lb_key(sport, home, away)
    q = ((G or {}).get("prices") or {}).get(k)
    if q and (q.get("h") or q.get("o")) and (not q.get("p") or q.get("p") == pick): return float(q.get("h") or q.get("o"))
    m = ((G or {}).get("listBooks") or {}).get(k)
    if m and m.get("h"): return float(m["h"])
    b = (g.get("market") or {}).get("best")
    if b and b[0 if side == "h" else 2]: return float(b[0 if side == "h" else 2])
    return None


def likely_winner(g, sport, G, now):
    """likelyWinner: the ⭐ on a Daily List pick that passes every check the record backs."""
    if not g or not g.get("list"): return False
    side = pick_side(g, sport)
    if not side: return False
    if sport == "football":
        if g.get("celtic") or g.get("unrated"): return False
        px = pick_price(g, sport, side, G)
        if px and px >= WIN_FB_MAX: return False
    if tennis_wary(g) or side_wary(g) or trail_wary(g): return False
    if book_gap(g, sport, G): return False
    if college_tier(g, now) in ("caution", "leave"): return False
    c = ((G or {}).get("contexts") or {}).get(lb_key(sport, name_of(g.get("home")), name_of(g.get("away"))))
    return not (c and c.get("verdict") == "against")


def list_price(it, G):
    """The row's price chip: William Hill's, else the bookmakers' average (labelled)."""
    k = lb_key(it["sport"], it.get("home"), it.get("away"))
    m = ((G or {}).get("listBooks") or {}).get(k) or {}
    q = ((G or {}).get("prices") or {}).get(k) or {}
    if m.get("h"): return {"label": "Hill", "price": float(m["h"])}
    if q.get("h"): return {"label": "Hill", "price": float(q["h"])}
    if q.get("o"): return {"label": "Exch" if q.get("x") else "Avg", "price": float(q["o"]), "not_hill": bool(m.get("b"))}
    if m.get("b"): return {"label": "Not at Hill", "price": None}
    return None


def strength(it):
    a = it.get("accuracy") or {}
    return (it.get("confidence") or 0, a.get("cumHit") or a.get("hit") or 0)


def tested(it):
    a = it.get("accuracy") or {}
    return a.get("cumHit") or a.get("hit")


def window(day):
    """07:00 UK on `day` to 07:00 UK the next day, in UTC (24 Nov 2026, Douglas:
    "Some of the games on the mailer already played ... can it be a 07.00-07.00
    24 hour period"): the email goes at 07:00, so a game before then has started."""
    d = date.fromisoformat(day)
    lo = datetime(d.year, d.month, d.day, 7, tzinfo=UK)
    n = d + timedelta(days=1)
    hi = datetime(n.year, n.month, n.day, 7, tzinfo=UK)
    return lo.astimezone(timezone.utc), hi.astimezone(timezone.utc)


def in_window(it, lo, hi, key="start"):
    """A pick starting inside the window; an untimed one stays with its own day."""
    t = parse_utc(it.get(key))
    if it.get("timed") is False or t is None:
        return True
    return lo <= t < hi


def list_items(src, day, now):
    """The Daily List as the page shows it for the day: list picks only (never the
    reserve), college basketball only at 1.05+ from any price on file, Leave out tier off, strongest
    first. Returns (items, left_off)."""
    DL, G = src.get("daylist") or {}, src.get("groupings") or {}
    if DL.get("date") == day:
        # 07:00 to 07:00: today's from 07:00 and the next UK day's overnight games
        lo, hi = window(day)
        raw = [it for it in DL.get("list") or [] if in_window(it, lo, hi)] + \
              [it for it in DL.get("early") or [] if it.get("timed") is not False and in_window(it, lo, hi)]
    else: raw = next((p.get("list") or [] for p in DL.get("past") or [] if p.get("date") == day), [])
    items, off = [], 0
    for it in raw:
        if not it.get("list"): continue
        floor = LIST_PRICE_MIN.get(it.get("sport"), 0)
        px = None
        if floor:
            # the slim pinned copy names the pick; its full row may carry the market
            g, sport = {**(it.get("full") or {}), **it}, it.get("sport")
            side = pick_side(g, sport)
            px = pick_price(g, sport, side, G) if side else None
        if (floor and not ((px or 0) >= floor)) or college_tier(tier_game(it), now) == "leave":
            off += 1; continue
        items.append(it)
    items.sort(key=strength, reverse=True)
    out = []
    for it in items:
        g, sport = item_game(it)
        out.append({**it, "star": likely_winner(g, sport, G, now), "px": list_price(it, G)})
    return out, off


# 27 Nov 2026: a price under 1.05 is marked Short in the email as on the page. The
# confidence bands the email carried that morning went with the page's that
# afternoon (Douglas: "I don't like the percentage banding"): one list again.
SHORT_PRICE = 1.05                  # SHORT_PRICE: lands as quoted, pays too little to matter in a slip


def is_short(it):
    px = (it.get("px") or {}).get("price")
    return bool(px and px < SHORT_PRICE and it.get("status") in (None, "upcoming"))


def card_short_text(s):
    """cardShortText, without the page's re-check sentence (an email is not rebuilt)."""
    if not s: return "No Card group today: too few picks clear the rule so far. A blank day is the rule working."
    n, kind = s.get("picks") or 0, s.get("kind") or "group"
    band = s.get("band") or [2, 3]
    lo, hi = f"{float(band[0]):.2f}", f"{float(band[1] or 0):.2f}"
    why, best = s.get("why"), s.get("best")
    tail = " A blank day is the rule working."
    if why == "long": return f"No Card group today: {n} picks clear the rule, but every set of them pays more than a {kind} can (the cheapest {float(best):.2f}, over its {hi} top).{tail}"
    if why == "short": return f"No Card group today: {n} picks clear the rule, but together they pay at most {float(best):.2f}, under the {kind}'s {lo}.{tail}"
    if why == "spread":
        c = s.get("comps") or 0
        return f"No Card group today: {n} picks clear the rule, but from {c} competition{'' if c == 1 else 's'}, and a group takes at most two from one.{tail}"
    if why == "chance": return f"No Card group today: {n} picks clear the rule, but no set paying {lo} to {hi} has the Sports Almanac model's combined chance high enough.{tail}"
    picks = "one pick clears" if n == 1 else f"{'no' if n == 0 else n} picks clear"
    return f"No Card group today: {picks} the rule so far, and a group needs {s.get('need') or 3}.{tail}"


def g_day(src, day):
    return next((d for d in (src.get("groupings") or {}).get("days") or [] if d.get("date") == day), None)


def edge_picks(src, day):
    D = src.get("data") or {}
    lo, hi = window(day)
    nxt = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    games = [g for d in D.get("days") or [] if d.get("date") in (day, nxt) for g in d.get("games") or []
             if (d.get("date") == day and (not g.get("kickoff") or in_window(g, lo, hi, "kickoff")))
             or (d.get("date") == nxt and g.get("kickoff") and in_window(g, lo, hi, "kickoff"))]
    out = []
    for g in games:
        e = g.get("edge")
        if not e: continue
        who, vs = (g["home"], g["away"]) if e.get("side") == "h" else (g["away"], g["home"])
        out.append({"pick": name_of(who), "opp": name_of(vs), "comp": g.get("leagueName") or g.get("short") or g.get("league"),
                    "country": g.get("country"), "kickoff": g.get("kickoff"), **e})
    return sorted(out, key=lambda x: x.get("kickoff") or "")


def scale_day(src, day):
    S = src.get("scale") or {}
    d = next((x for x in S.get("days") or [] if x.get("date") == day), None)
    if not d: return [], []
    picks = [p for p in d.get("picks") or [] if p.get("tier") == "list"]
    by = {p.get("key"): p for p in d.get("picks") or []}
    groups = [{**g, "legPicks": [by[k] for k in g.get("legs") or [] if k in by]} for g in d.get("groups") or []]
    return picks, groups


# ---------------------------------------------------------------- HTML pieces

def _p(text, size=14, color=INK2, extra=""):
    return f'<p style="margin:0 0 10px 0;font-family:{F_BODY};font-size:{size}px;line-height:1.5;color:{color};{extra}">{text}</p>'


def section(title, sub, inner):
    """A red day band and its body, as the site's .day-head: Anton 17px white with an ink offset, the count in mono yellow."""
    sub_h = (f'<td align="right" valign="middle" style="padding:6px 12px 5px 8px;font-family:{F_NUM};font-size:12px;font-weight:600;'
             f'color:{YELLOW}">{E(sub)}</td>') if sub else ""
    return (f'<tr><td style="padding:0">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{RED};border:1px solid {INK};border-top:0">'
            f'<tr><td valign="middle" style="padding:6px 12px 5px 12px;font-family:{F_DISPLAY};font-size:17px;line-height:1.3;letter-spacing:.04em;'
            f'text-transform:uppercase;color:#ffffff;text-shadow:1.5px 1.5px 0 {INK}">{E(title)}</td>{sub_h}</tr></table>'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td style="background:{SURFACE};border:1px solid {RULE};border-top:0;padding:2px 12px 10px 12px">{inner}</td></tr>'
            f'</table></td></tr>')


def label_bar(title, sub):
    """A group label, as the site's .lgrp: small caps in the UI face, the title in ink, the count in mono."""
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0">'
            f'<tr><td style="padding:12px 0 4px 0;font-family:{F_UI};font-size:11px;font-weight:700;letter-spacing:.08em;'
            f'text-transform:uppercase;color:{MUTE};border-bottom:1px solid {INK}"><b style="color:{INK}">{E(title)}</b>'
            f'<span style="font-family:{F_NUM};font-size:11px;font-weight:600;letter-spacing:0;text-transform:none;color:{MUTE}">&nbsp;&nbsp;{E(sub)}</span></td></tr></table>')


def row(left_top, left_bottom, main, meta, right_big, right_small, tint=None):
    """One pick: time and sport on the left, the pick and its line in the middle, the number on the right."""
    bg = f"background:{tint};" if tint else ""
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-bottom:1px solid {RULE};{bg}">'
            f'<tr><td width="58" valign="top" style="padding:10px 6px 10px 0;font-family:{F_MONO};font-size:13px;color:{INK}">{left_top}'
            f'<div style="font-family:{F_BODY};font-size:10px;letter-spacing:.5px;text-transform:uppercase;color:{MUTE};padding-top:2px">{left_bottom}</div></td>'
            f'<td valign="top" style="padding:10px 8px 10px 0;font-family:{F_BODY};font-size:15px;line-height:1.35;color:{INK}">{main}'
            f'<div style="font-size:12px;line-height:1.45;color:{MUTE};padding-top:2px">{meta}</div></td>'
            f'<td width="74" valign="top" align="right" style="padding:10px 0 10px 0;font-family:{F_HEAD};font-size:18px;color:{INK};white-space:nowrap">{right_big}'
            f'<div style="font-family:{F_MONO};font-size:12px;color:{INK2};padding-top:2px;white-space:nowrap">{right_small}</div></td></tr></table>')


def price_html(px):
    if not px: return '<span style="color:#9a8f80">no price</span>'
    if px.get("price") is None: return E(px["label"])
    return f'{E(px["label"])} <b>{px["price"]:.2f}</b>'


def price_text(px):
    if not px: return "no price yet"
    if px.get("price") is None: return px["label"]
    return f'{px["label"]} {px["price"]:.2f}'


def status_word(it):
    st, r = it.get("status"), it.get("result") or {}
    if st == "won": return "Won" + (f" {r['score']}" if r.get("score") else "")
    if st == "lost": return "Lost" + (f" {r['score']}" if r.get("score") else "")
    if st == "void": return "Void"
    if st == "started": return "Under way"
    return ""


def list_row(src, it):
    opp = it["away"] if it.get("side") == "h" else it["home"]
    star = ' <span style="font-size:11px;line-height:1;vertical-align:1px" title="Likely winner">⭐</span>' if it.get("star") else ""
    t = tested(it)
    meta = [E(it.get("comp") or "")]
    meta.append(f"tested {pct(t)}" if t else "no tested rate yet")
    st = status_word(it)
    if st: meta.append(f'<b style="color:{GREEN if it.get("status") == "won" else RED if it.get("status") == "lost" else INK2}">{E(st)}</b>')
    when = uk_time(it.get("start")) if it.get("timed", True) else "TBC"
    return row(E(when), E(sport_name(src, it.get("sport"))),
               f'<b>{E(it.get("pick"))}</b>{star} <span style="color:{MUTE}">v {E(opp)}</span>',
               " · ".join(meta), pct(it.get("confidence")),
               price_html(it.get("px")) + (f'<br><span style="color:{RED};font-size:10px;font-weight:bold;letter-spacing:.04em">SHORT</span>' if is_short(it) else ""))


def leg_row(src, l, tint=None):
    bo = l.get("bookOdds") or {}
    hill = bo.get(BOOK)
    if hill: price = f"Hill <b>{hill:.2f}</b>"
    elif l.get("est"): price = f"est. <b>{float(l['odds']):.2f}</b>"
    else: price = f"Avg <b>{float(l['odds']):.2f}</b>" + ("<br>not at Hill" if bo else "")
    meta = [E(l.get("event") or ""), E(l.get("comp") or sport_name(src, l.get("sport")))]
    return row(E(uk_time(l.get("when"))), E(sport_name(src, l.get("sport"))), f'<b>{E(l.get("pick"))}</b>',
               " · ".join(meta), pct(l.get("p")), price, tint)


def group_head(name, line, odds_line):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:10px 0 0 0;border-bottom:2px solid {INK}">'
            f'<tr><td style="padding:4px 0;font-family:{F_HEAD};font-size:16px;color:{INK}">{E(name)}'
            f'<div style="font-family:{F_BODY};font-size:12px;color:{MUTE};font-weight:normal">{line}</div></td>'
            f'<td align="right" valign="bottom" style="padding:4px 0;font-family:{F_BODY};font-size:13px;color:{INK}">{odds_line}</td></tr></table>')


def group_odds(g):
    hill = g.get("bookOdds")
    if hill: return f'<b style="font-family:{F_HEAD};font-size:18px">{float(hill):.2f}</b> at {E(g.get("book") or BOOK)}', f"{float(hill):.2f} at {g.get('book') or BOOK}"
    return f'<b style="font-family:{F_HEAD};font-size:18px">{float(g["odds"]):.2f}</b> average', f"{float(g['odds']):.2f} average"


def wrap(title, day_line, preheader, body_rows, foot):
    return f"""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light">
<link href="{FONTS_LINK}" rel="stylesheet">
<title>{E(title)}</title></head>
<body style="margin:0;padding:0;background:{PAPER}">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:{PAPER}">{E(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{PAPER}">
<tr><td align="center" style="padding:16px 10px 28px 10px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%">
<tr><td style="padding:0;background:{INK};line-height:0;font-size:0"><img src="{HEADER_IMG}" width="600" alt="The Sports Almanac · Complete sports statistics · 2026" style="display:block;width:100%;max-width:600px;height:auto;border:0;outline:none;text-decoration:none;background:{INK};color:#ffffff;font-family:{F_HEAD};font-size:24px;line-height:1.2"></td></tr>
<tr><td style="padding:0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{YELLOW};border:1px solid {INK};border-top:0"><tr>
<td style="padding:12px 12px;font-family:{F_UI};font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:{INK}">{E(title)}</td>
<td align="right" style="padding:12px 12px;font-family:{F_UI};font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:{INK};white-space:nowrap">{E(day_line)}</td></tr></table></td></tr>
{''.join(body_rows)}
{foot}
</table></td></tr></table></body></html>"""


def footer_html(links):
    a = lambda href, txt: f'<a href="{E(href)}" style="color:{INK};font-weight:bold">{E(txt)}</a>'
    lk = " · ".join(a(h, t) for t, h in links)
    return (f'<tr><td style="background:{SURFACE};border:1px solid {RULE};border-top:0;padding:16px 14px;font-family:{F_BODY};font-size:13px;line-height:1.6;color:{INK2}">'
            f'<p style="margin:0 0 10px 0">{lk}</p>'
            f'<p style="margin:0 0 10px 0">Every pick is the Sports Almanac model\'s own read, published before the start and graded in public on the site, losses included. Past results do not guarantee future ones.</p>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 10px 0"><tr>'
            f'<td valign="top" style="background:{RED};color:#ffffff;font-family:{F_HEAD};font-size:15px;padding:6px 8px">18+</td>'
            f'<td style="padding:0 0 0 10px;font-family:{F_BODY};font-size:12px;line-height:1.5;color:{INK2}">Every pick can lose. Set a limit before you bet and never chase a loss. Free, confidential help: GamCare 0808 8020 133 · '
            f'<a href="https://www.begambleaware.org" style="color:{INK}">BeGambleAware.org</a></td></tr></table>'
            f'<p style="margin:0;font-size:12px;color:{MUTE}">You get this because you signed up at sportsalmanac.bet. '
            f'<a href="{MANAGE_MARK}" style="color:{INK}">Manage your emails</a> · <a href="{UNSUB_MARK}" style="color:{INK}">Unsubscribe</a></p></td></tr>')


def footer_text(links):
    return ("\n".join(f"{t}: {h}" for t, h in links) +
            "\n\nEvery pick is the Sports Almanac model's own read, published before the start and graded in public on the site, losses included. "
            "Past results do not guarantee future ones.\n\n18+. Every pick can lose. Free, confidential help: GamCare 0808 8020 133, "
            f"https://www.begambleaware.org\n\nManage your emails: {MANAGE_MARK}\nUnsubscribe: {UNSUB_MARK}\n")


# ---------------------------------------------------------------- the welcome series (design, 23 Nov 2026)
#
# Three emails for a new subscriber: confirm (at sign-up, double opt-in), welcome
# (once confirmed) and how to read the Daily List (two days later). Built here so
# they share the shell; nothing sends them yet. CONFIRM_MARK is the row's token.

CONFIRM_MARK = "%%CONFIRM_URL%%"
CONFIRM_URL = SITE + "#mailer?confirm={t}"


def button(href, label):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 14px 0"><tr>'
            f'<td style="background:{RED};border:1px solid {INK}">'
            f'<a href="{href}" style="display:inline-block;padding:13px 22px;font-family:{F_HEAD};font-size:15px;letter-spacing:1px;'
            f'text-transform:uppercase;color:#ffffff;text-decoration:none">{E(label)}</a></td></tr></table>')


def key_row(term, text):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-bottom:1px solid {RULE}">'
            f'<tr><td width="112" valign="top" style="padding:10px 10px 10px 0;font-family:{F_HEAD};font-size:13px;color:{INK}">{term}</td>'
            f'<td valign="top" style="padding:10px 0;font-family:{F_BODY};font-size:14px;line-height:1.5;color:{INK2}">{text}</td></tr></table>')


def welcome_emails():
    """[(name, {subject, html, text})] for the three welcome emails."""
    links = [("Today's Daily List", SITE), ("How it went", SITE + "#results")]
    out = []

    body = [section("One tap to start", None,
                    _p("Thanks for signing up at sportsalmanac.bet. Confirm this address and your first Daily List arrives at 07:00 tomorrow.", 15, INK, "padding-top:8px") +
                    button(CONFIRM_MARK, "Confirm my email") +
                    _p("If you didn't sign up, ignore this email. Nothing more will be sent to you.", 13, MUTE))]
    out.append(("welcome-1-confirm", {
        "subject": "Confirm your Sports Almanac emails", "kind": "confirm",
        "html": wrap("Confirm your email", "One step left", "One tap and the Daily List starts tomorrow at 07:00.", body, footer_html(links)),
        "text": f"Confirm your Sports Almanac emails\n\nConfirm this address and your first Daily List arrives at 07:00 tomorrow:\n{CONFIRM_MARK}\n\nIf you didn't sign up, ignore this email.\n\n" + footer_text(links)}))

    get = (key_row("Daily List", "Every morning at 07:00 UK: the day's strongest picks across every sport, with the price at William Hill where there is one.") +
           key_row("Weekly Record", "Saturdays at 07:00 UK: how last week's picks landed against what was quoted, wins and misses both.") +
           key_row("Scale", "Only if you ticked it: the day's Scale bets, a pick to win plus a second condition, inside the Daily List email."))
    how = (_p("Every number comes from the Sports Almanac model alone. No bookmaker's price goes into a pick; prices are shown only so you can see what you'd get.", 14, INK2, "padding-top:8px") +
           _p("Every pick is published before the start and graded in public on the site, losses included. Nothing is taken down after the result.", 14, INK2) +
           button(SITE, "See today's list"))
    body = [section("What you'll get", None, get), section("How the picks are made", None, how)]
    out.append(("welcome-2-welcome", {
        "subject": "You're in: the Daily List starts tomorrow", "kind": "welcome",
        "html": wrap("Welcome", "You're confirmed", "What arrives, when, and how the picks are made.", body, footer_html(links)),
        "text": "You're in. The Daily List arrives every morning at 07:00 UK; the Weekly Record on Saturdays.\n\n"
                "Every number comes from the Sports Almanac model alone, published before the start and graded in public, losses included.\n\n" + footer_text(links)}))

    groups = (label_bar("One list", "strongest first") +
              _p("Every pick that cleared the Daily List's bar, the Sports Almanac model's strongest first, each with how often calls at its level landed in testing.", 14, INK2, "padding-top:8px") +
              label_bar("Short", "a price under 1.05") +
              _p("A short pick lands as often as quoted but pays so little it adds almost nothing to a slip.", 14, INK2, "padding-top:8px"))
    row_key = (key_row("90%", "The Sports Almanac model's chance the pick wins.") +
               key_row("tested 84%", "How often picks at this level landed in testing, on games the Sports Almanac model was never tuned on. A pick only reaches the list when that figure is 80% or better.") +
               key_row("Hill 1.25", "William Hill's price, for reference. Avg means the average across UK books where Hill has none.") +
               key_row("⭐", "Likely winner: a list pick that also clears a short set of extra checks, such as no bookmakers' warning against it.") +
               key_row("Won / Lost", "Picks already played show their result, so nothing is hidden."))
    body = [section("The list", "how it is ordered", groups),
            section("Reading a row", "the example numbers are for illustration", row_key)]
    out.append(("welcome-3-guide", {
        "subject": "How to read the Daily List", "kind": "guide",
        "html": wrap("How to read it", "Two-minute guide", "The order, the tested rate and the star, explained.", body, footer_html(links)),
        "text": "How to read the Daily List\n\nOne list, the model's strongest pick first, each with how often calls at its level landed in testing.\n"
                "Short: a price under 1.05, which lands as quoted but adds little to a slip.\n\n" + footer_text(links)}))
    return out


# ---------------------------------------------------------------- the Daily List email

def daily_email(day, src=None, with_scale=False, now=None):
    """The morning email for UK day `day` (YYYY-MM-DD): {subject, html, text, count}."""
    src = src if src is not None else load()
    now = now or datetime.now(timezone.utc)
    G = src.get("groupings") or {}
    items, off = list_items(src, day, now)
    rows, text = [], []
    dl = long_day(day)
    text.append(f"THE SPORTS ALMANAC · THE DAILY LIST · {dl}\n")

    # 1. The Daily List
    if items:
        inner = []
        text.append(f"THE DAILY LIST · {len(items)} pick{'' if len(items) == 1 else 's'} clear the bar")
        text.append("")
        for it in items:
            inner.append(list_row(src, it))
            opp = it["away"] if it.get("side") == "h" else it["home"]
            t = tested(it)
            st = status_word(it)
            text.append(f"  {uk_time(it.get('start')) if it.get('timed', True) else 'TBC'}  {it.get('pick')}{' *' if it.get('star') else ''} v {opp}"
                        f" · {sport_name(src, it.get('sport'))} · {it.get('comp') or ''} · {pct(it.get('confidence'))}"
                        f"{f' · tested {pct(t)}' if t else ''} · {price_text(it.get('px'))}{' (short)' if is_short(it) else ''}{f' · {st}' if st else ''}")
        nailed = next((it for it in items if it.get("star")), None)
        if any(it.get("star") for it in items):
            inner.append(_p(f"⭐ marks a likely winner: a list pick that passes every check the record backs (football under {WIN_FB_MAX:.2f}, "
                            "no college away, neutral or behind .500 pick, no tennis under 80%, no Bookies mark, no context check against).", 12, MUTE, "padding-top:10px"))
            text.append(f"\n* likely winner. Most nailed on: {nailed['pick']} ({pct(nailed['confidence'])}).")
        if off:
            text.append(f"\n{off} college basketball pick{'' if off == 1 else 's'} left off: no price at 1.05 or better on file, or tiered Leave out.")
            inner.append(_p(f"{off} college basketball pick{'' if off == 1 else 's'} left off: no price at 1.05 or better on file, or tiered Leave out. On the college basketball tab.", 12, MUTE))
        inner.append(_p("Strongest first. The percentage is the Sports Almanac model's chance; tested is how often calls at that level landed on games never tuned on. "
                        f"Prices are William Hill's where read (Avg: the bookmakers' average), shown only: the list never sees a price. Short: under {SHORT_PRICE:.2f}, it pays too little to add much to a slip.", 12, MUTE))
        rows.append(section("The Daily List", f"{len(items)} pick{'' if len(items) == 1 else 's'} clear the bar", "".join(inner)))
    else:
        msg = "Nothing clears the Daily List's bar today, in any sport, so nothing is served. No padding: a blank list is the rule working."
        rows.append(section("The Daily List", "none today", _p(msg, 14, INK2, "padding-top:10px")))
        text.append("THE DAILY LIST\n  " + msg)

    gd = g_day(src, day) or {}
    groups = gd.get("groups") or []

    # 2. The Daily 2x
    d2 = next((g for g in groups if g.get("name") == "Daily 2x"), None)
    if d2:
        oh, ot = group_odds(d2)
        n = len(d2.get("legs") or [])
        line = f"{n} picks, the Sports Almanac model's strongest at 1.10+" + (" · <b>short of 2x today</b>" if d2.get("short") else " · on trial")
        inner = [group_head("Today's 2x", line, oh)] + [leg_row(src, l) for l in d2.get("legs") or []]
        if d2.get("short"): inner.append(_p("Nothing more qualified today, so this slip pays under 2x.", 12, MUTE, "padding-top:8px"))
        inner.append(_p(f"All {n} land: Sports Almanac model {pct(d2.get('p'))}. One unit; graded on its own line.", 12, MUTE, "padding-top:8px"))
        rows.append(section("The Daily 2x", "one slip a day", "".join(inner)))
        text.append(f"\nTHE DAILY 2X · {ot}{' · short of 2x today' if d2.get('short') else ''}")
        text += [f"  {uk_time(l.get('when'))}  {l.get('pick')} ({l.get('event')}) · {pct(l.get('p'))} · "
                 f"{'Hill %.2f' % l['bookOdds'][BOOK] if (l.get('bookOdds') or {}).get(BOOK) else 'avg %.2f' % float(l['odds'])}" for l in d2.get("legs") or []]
    else:
        msg = "No 2x yet today: no priced pick at 1.10+ has come in. It is rebuilt on every build; the Bets tab has the latest."
        rows.append(section("The Daily 2x", "one slip a day", _p(msg, 14, INK2, "padding-top:10px")))
        text.append("\nTHE DAILY 2X\n  " + msg)

    # 3. The Card
    cards = [g for g in groups if str(g.get("name", "")).startswith("Card") and not g.get("wide")]
    if cards:
        inner = []
        text.append("\nTHE CARD")
        for g in cards:
            oh, ot = group_odds(g)
            stake = g.get("stake") or 1
            n = len(g.get("legs") or [])
            inner.append(group_head(g["name"] + (" (second)" if (g.get("seq") or 1) > 1 else ""),
                                    f"{n} picks · {stake} unit{'' if stake == 1 else 's'} · open until its first start", oh))
            inner += [leg_row(src, l) for l in g.get("legs") or []]
            text.append(f"  {g['name']} · {ot} · {stake} unit{'' if stake == 1 else 's'}")
            text += [f"    {uk_time(l.get('when'))}  {l.get('pick')} ({l.get('event')}) · {pct(l.get('p'))}"
                     f"{' · Hill %.2f' % l['bookOdds'][BOOK] if (l.get('bookOdds') or {}).get(BOOK) else ' · not at Hill'}" for l in g.get("legs") or []]
        inner.append(_p("Place once, before the first start; a group can still change until then, so check the Bets tab before placing. No cash out, no topping up.", 12, MUTE, "padding-top:8px"))
        rows.append(section("The Card", "the Sports Almanac model's own picks, staked", "".join(inner)))
    else:
        msg = card_short_text(gd.get("cardShort"))
        rows.append(section("The Card", "the Sports Almanac model's own picks, staked", _p(E(msg), 14, INK2, "padding-top:10px")))
        text.append("\nTHE CARD\n  " + msg)

    # 4. Edge picks
    edges = edge_picks(src, day)
    if edges:
        inner = []
        text.append("\nEDGE PICKS")
        for e in edges:
            inner.append(row(E(uk_time(e.get("kickoff"))), "Football", f'<b style="color:{GREEN}">{E(e["pick"])}</b> <span style="color:{MUTE}">v {E(e["opp"])}</span>',
                             f'{E(e.get("comp") or "")} · bookmakers {pct(e.get("fair"))}, Sports Almanac model {pct(e.get("model"))}, {E(e["opp"])} priced {float(e.get("opp") or 0):.2f}',
                             f'{float(e["odds"]):.2f}', f'best {float(e.get("best") or e["odds"]):.2f}', GREEN_SOFT))
            text.append(f"  {uk_time(e.get('kickoff'))}  {e['pick']} v {e['opp']} · {e.get('comp') or ''} · {float(e['odds']):.2f} (best {float(e.get('best') or e['odds']):.2f})")
        inner.append(_p("Football favourites at 1.15 to 1.90 whose opponent is priced 5.0 or more. Take the best price: at the average the edge is thin.", 12, MUTE, "padding-top:8px"))
        rows.append(section("Edge picks", f"{len(edges)} today", "".join(inner)))
    else:
        msg = "No Edge picks today yet. They are rare by design (about five a week, mostly at weekends)."
        rows.append(section("Edge picks", "none today", _p(msg, 14, INK2, "padding-top:10px")))
        text.append("\nEDGE PICKS\n  " + msg)

    # 5. Scale, only for subscribers who chose it
    if with_scale:
        picks, sgroups = scale_day(src, day)
        S = src.get("scale") or {}
        inner, txt = [], ["\nSCALE (beta)"]
        for p in picks:
            bet = p.get("bet") or ((S.get("sports") or {}).get(p.get("sport")) or {}).get("bet") or ""
            if p.get("price"): pr, prt = f'{E(p.get("book") or BOOK)} <b>{p["price"]:.2f}</b>', f"{p.get('book') or BOOK} {p['price']:.2f}"
            elif p.get("est"): pr, prt = f'≈ <b>{p["est"]:.2f}</b> estimate', f"≈ {p['est']:.2f} estimate"
            else: pr, prt = "no price", "no price"
            opp = p["away"] if p.get("side") == "h" else p["home"]
            inner.append(row(E(uk_time(p.get("start"))), E(sport_name(src, p.get("sport"))),
                             f'<b>{E(p.get("pick"))}</b> <span style="color:{MUTE}">{E(bet.lower())}</span>',
                             f'v {E(opp)} · winner {pct(p.get("conf"))}', pct(p.get("chance")), pr))
            txt.append(f"  {uk_time(p.get('start'))}  {p.get('pick')} {bet.lower()} v {opp} · {pct(p.get('chance'))} · {prt}")
        if not picks:
            inner.append(_p("No Scale bets from today's Daily List.", 14, INK2, "padding-top:10px")); txt.append("  No Scale bets from today's Daily List.")
        for g in sgroups:
            if g.get("price"): gp, gpt = f'{E(S.get("book") or BOOK)} <b>{g["price"]:.2f}</b>', f"{g['price']:.2f}"
            elif g.get("est"): gp, gpt = f'≈ <b>{g["est"]:.2f}</b> estimate', f"≈ {g['est']:.2f} estimate"
            else: gp, gpt = "no price", "no price"
            names = ", ".join(E(f"{x.get('pick')} {str(x.get('bet') or '').lower()}") for x in g["legPicks"])
            inner.append(group_head(g.get("name") or "Scale group", f"{len(g.get('legs') or [])} legs · all land {pct(g.get('chance'))}", gp))
            inner.append(_p(names, 13, INK2, "padding-top:6px"))
            txt.append(f"  {g.get('name')} · {gpt} · all land {pct(g.get('chance'))}: " + ", ".join(f"{x.get('pick')} {str(x.get('bet') or '').lower()}" for x in g["legPicks"]))
        inner.append(_p("The Daily List's winners with a second condition, for bigger odds. ≈ marks an estimate where no feed prices the bet: its chance less a typical margin, not a price a bookmaker offered.", 12, MUTE, "padding-top:8px"))
        rows.append(section("Scale", "beta · the list's picks, bigger odds", "".join(inner)))
        text += txt

    links = [("Today's Daily List", SITE + "#list"), ("Bets", SITE + "#today"), ("Scale", SITE + "#scale"), ("Every card's record", SITE + "#results?board=cards")]
    n = len(items)
    subject = f"The Daily List, {short_day(day)}: " + (f"{n} pick{'' if n == 1 else 's'}" if n else "nothing clears the bar")
    pre = (f"{n} picks clear the bar today" + (f", led by {items[0]['pick']} at {pct(items[0]['confidence'])}." if n else ".")) if n else "Nothing clears the bar today."
    body = wrap("The Daily List", dl, pre, rows, footer_html(links))
    return {"subject": subject, "html": body, "text": "\n".join(text) + "\n\n" + footer_text(links), "count": n, "kind": "daily"}


# ---------------------------------------------------------------- the email as sent, kept

MAIL_ARCHIVE = os.path.join(HERE, "mail-archive")   # mail_page.py reads it for the Mailer tab (25 Nov 2026)


def _leg(l):
    hill = (l.get("bookOdds") or {}).get(BOOK)
    return {"pick": l.get("pick"), "event": l.get("event"), "sport": l.get("sport"), "comp": l.get("comp"),
            "when": l.get("when"), "p": l.get("p"), "odds": l.get("odds"), "hill": hill, "est": bool(l.get("est"))}


def _group(g):
    return {"name": g.get("name"), "seq": g.get("seq") or 1, "odds": g.get("odds"), "hill": g.get("bookOdds"),
            "stake": g.get("stake") or 1, "p": g.get("p"), "short": bool(g.get("short")),
            "legs": [_leg(l) for l in g.get("legs") or []]}


def snapshot(day, src, now=None, mail=None):
    """What the morning email for `day` held, as data (25 Nov 2026, Douglas: the Mailer tab shows each
    email with a tick or a cross): the same reads as daily_email, the plain variant (no Scale)."""
    now = now or datetime.now(timezone.utc)
    items, _ = list_items(src, day, now)
    nA = min(5, sum(1 for it in items if (it.get("confidence") or 0) >= GROUP_A_MIN))
    gd = g_day(src, day) or {}
    groups = gd.get("groups") or []
    d2 = next((g for g in groups if g.get("name") == "Daily 2x"), None)
    cards = [g for g in groups if str(g.get("name", "")).startswith("Card") and not g.get("wide")]
    return {"day": day, "sentAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "subject": (mail or {}).get("subject"),
            "list": [{"sport": it.get("sport"), "home": it.get("home"), "away": it.get("away"), "pick": it.get("pick"),
                      "comp": it.get("comp"), "start": it.get("start"), "timed": it.get("timed", True),
                      "conf": it.get("confidence"), "tested": tested(it), "px": it.get("px"), "star": bool(it.get("star")),
                      "A": i < nA} for i, it in enumerate(items)],
            "daily": _group(d2) if d2 else None,
            "cards": [_group(g) for g in cards],
            "cardShort": None if cards else card_short_text(gd.get("cardShort")),
            "edge": [{"pick": e["pick"], "opp": e["opp"], "comp": e.get("comp"), "kickoff": e.get("kickoff"),
                      "odds": e.get("odds"), "best": e.get("best")} for e in edge_picks(src, day)]}


def keep(day, src, now=None, mail=None, folder=None):
    """Write mail-archive/<day>.json once, the first time the day's email goes; never rewritten."""
    folder = folder or globals()["MAIL_ARCHIVE"]
    path = os.path.join(folder, f"{day}.json")
    if os.path.exists(path): return path
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot(day, src, now, mail), f, ensure_ascii=False, indent=1)
    return path


# ---------------------------------------------------------------- the Weekly Record email

def week_of(day):
    """The seven UK days Saturday to Friday that ended before `day`."""
    d = date.fromisoformat(day)
    end = d - timedelta(days=((d.weekday() - 4) % 7) or 7)   # the last Friday before d
    start = end - timedelta(days=6)
    return start.isoformat(), end.isoformat()


def week_list(src, a, b):
    rows = [r for r in (src.get("ledger") or {}).get("rows") or []
            if r.get("list") and a <= (r.get("date") or "") <= b and not r.get("movedTo") and not r.get("duplicate")]
    done = [r for r in rows if r.get("result") in ("won", "lost")]
    by = {}
    for r in done:
        t = by.setdefault(r.get("sport"), {"n": 0, "won": 0, "q": 0.0})
        t["n"] += 1; t["won"] += r["result"] == "won"; t["q"] += r.get("conf") or 0
    tot = {"n": len(done), "won": sum(r["result"] == "won" for r in done), "q": sum(r.get("conf") or 0 for r in done),
           "pending": sum(1 for r in rows if r.get("result") is None), "void": sum(1 for r in rows if r.get("result") == "void")}
    wins = sorted([r for r in done if r["result"] == "won"], key=lambda r: -(r.get("conf") or 0))[:5]
    misses = sorted([r for r in done if r["result"] == "lost"], key=lambda r: -(r.get("conf") or 0))
    return tot, by, wins, misses


def _groups_week(src, a, b, match):
    won = settled = pending = 0; exp = staked = ret = 0.0
    for d in (src.get("grecord") or {}).get("days") or []:
        if not a <= d.get("date", "") <= b: continue
        for g in d.get("groups") or []:
            if not match(g): continue
            if g.get("status") == "pending": pending += 1; continue
            if g.get("status") not in ("won", "lost"): continue
            u = g.get("stake") or 1
            settled += 1; won += g["status"] == "won"; exp += g.get("p") or 0
            staked += u; ret += u * (g.get("paid") or 0)
    return {"won": won, "settled": settled, "exp": exp, "pending": pending, "net": ret - staked, "staked": staked}


def head_line(h, per="the page's stakes", unit="units"):
    """The ledger's headline: "<won> of <settled> won v <expected> expected · <return> at its stakes"."""
    if not h["settled"]:
        return "Nothing settled this week." + (f" {h['pending']} to settle." if h.get("pending") else "")
    s = f"{h['won']} of {h['settled']} won"
    if h.get("exp") is not None: s += f" v {h['exp']:.1f} expected"
    if h.get("ret"): s += f" · {h['ret']}"
    elif h.get("staked"): s += f" · {signed_pc(h['net'], h['staked'])} at {per} ({signed(h['net'])} {unit} on {round(h['staked'], 2):g})"
    if h.get("pending"): s += f" · {h['pending']} to settle"
    return s


def week_cards(src, a, b):
    out = []
    is_card = lambda g: str(g.get("name", "")).startswith("Card") and not g.get("wide") and not g.get("late")
    out.append(("The Card", head_line(_groups_week(src, a, b, is_card), "the page's stakes")))
    out.append(("Daily 2x", head_line(_groups_week(src, a, b, lambda g: g.get("name") == "Daily 2x"), "one unit a slip")))
    out.append(("List card", head_line(_groups_week(src, a, b, lambda g: g.get("name") in ("List 2x", "List long")), "one unit a group")))
    # the slip: the live slips settled this week (slip.json record.recent)
    rec = [x for x in (((src.get("slip") or {}).get("record") or {}).get("recent") or []) if a <= x.get("date", "") <= b]
    real = [x for x in rec if x.get("state") in ("won", "lost")]
    net = sum((x.get("ret") or 0) - 1 for x in real)
    h = {"won": sum(x["state"] == "won" for x in real), "settled": len(real), "exp": sum(x.get("chance") or 0 for x in real), "pending": 0,
         "net": net, "staked": len(real), "ret": f"{signed_pc(net, len(real))} at one unit a slip ({signed(net)} units)" if real else None}
    out.append(("The slip", head_line(h)))
    # Edge picks: record.json edge days, one unit a pick at the best and the average price
    ps = [p for d in ((src.get("record") or {}).get("edge") or {}).get("days") or [] if a <= d.get("d", "") <= b for p in d.get("p") or []]
    nb = sum((p[3] - 1) if p[4] else -1 for p in ps); na = sum((p[2] - 1) if p[4] else -1 for p in ps)
    h = {"won": sum(1 for p in ps if p[4]), "settled": len(ps), "exp": None, "pending": 0,
         "ret": f"{signed_pc(nb, len(ps))} at the best price, one unit a pick ({signed(nb)} units); {signed_pc(na, len(ps))} at the average" if ps else None}
    out.append(("Edge picks", head_line(h)))
    # Scale groups: a price where every leg had one, else the estimate (≈)
    won = settled = 0; exp = net = 0.0; est = False
    for d in (src.get("scale") or {}).get("days") or []:
        if not a <= d.get("date", "") <= b: continue
        for g in d.get("groups") or []:
            if g.get("state") not in ("won", "lost"): continue
            pay = g.get("ret") if g.get("ret") is not None else g.get("estRet")
            if g.get("ret") is None and g.get("estRet") is not None: est = True
            settled += 1; won += g["state"] == "won"; exp += g.get("chance") or 0
            net += (pay - 1) if pay is not None else 0
    h = {"won": won, "settled": settled, "exp": exp, "pending": 0,
         "ret": f"{'≈ ' if est else ''}{signed_pc(net, settled)} at one unit a group ({signed(net)} units{', some at estimated prices' if est else ''})" if settled else None}
    out.append(("Scale groups", head_line(h)))
    return out


def weekly_email(day, src=None):
    """The Saturday email: the seven UK days Saturday to Friday before `day`."""
    src = src if src is not None else load()
    a, b = week_of(day)
    tot, by, wins, misses = week_list(src, a, b)
    span = f"{short_day(a)} to {short_day(b)}"
    rows, text = [], [f"THE SPORTS ALMANAC · THE WEEKLY RECORD · {span}\n"]

    # 1. The Daily List
    inner = []
    if tot["n"]:
        head = f"{tot['won']} of {tot['n']} landed ({pct(tot['won'] / tot['n'])}) against {pct(tot['q'] / tot['n'])} quoted"
        inner.append(f'<p style="margin:10px 0 8px 0;font-family:{F_HEAD};font-size:20px;line-height:1.25;color:{INK}">{E(head)}</p>')
        extra = [f"{tot['void']} void" if tot["void"] else "", f"{tot['pending']} still to settle" if tot["pending"] else ""]
        if any(extra): inner.append(_p(", ".join(x for x in extra if x) + ".", 12, MUTE))
        cells = "".join(
            f'<tr><td style="padding:6px 0;border-bottom:1px solid {RULE};font-family:{F_BODY};font-size:14px;color:{INK}">{E(sport_name(src, k))}</td>'
            f'<td align="right" style="padding:6px 0;border-bottom:1px solid {RULE};font-family:{F_MONO};font-size:13px;color:{INK}">{t["won"]} of {t["n"]}</td>'
            f'<td align="right" style="padding:6px 0;border-bottom:1px solid {RULE};font-family:{F_MONO};font-size:13px;color:{INK}">{pct(t["won"] / t["n"])}</td>'
            f'<td align="right" style="padding:6px 0;border-bottom:1px solid {RULE};font-family:{F_MONO};font-size:13px;color:{MUTE}">{pct(t["q"] / t["n"])}</td></tr>'
            for k, t in sorted(by.items(), key=lambda kv: -kv[1]["n"]))
        th = f'font-family:{F_BODY};font-size:11px;letter-spacing:.5px;text-transform:uppercase;color:{MUTE};padding:4px 0;border-bottom:2px solid {INK}'
        inner.append(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="{th}">Sport</td><td align="right" style="{th}">Landed</td><td align="right" style="{th}">Rate</td><td align="right" style="{th}">Quoted</td></tr>{cells}</table>')
        text.append("THE DAILY LIST\n  " + head)
        text += [f"  {sport_name(src, k)}: {t['won']} of {t['n']} ({pct(t['won'] / t['n'])}) v {pct(t['q'] / t['n'])} quoted" for k, t in sorted(by.items(), key=lambda kv: -kv[1]["n"])]

        def pick_line(r):
            opp = r["away"] if r.get("side") == "h" else r["home"]
            return f"{r.get('pick')} v {opp}", f"{sport_name(src, r.get('sport'))} · {short_day(r['date'])} · {pct(r.get('conf'))}" + (f" · {r['score']}" if r.get("score") else "")
        if wins:
            inner.append(label_bar("Strongest wins", f"the {len(wins)} the Sports Almanac model was surest of"))
            for r in wins:
                m, meta = pick_line(r)
                inner.append(_p(f'<b style="color:{GREEN}">✓</b> <b style="color:{INK}">{E(m)}</b><br><span style="font-size:12px;color:{MUTE}">{E(meta)}</span>', 14, INK, "margin:6px 0"))
            text.append("\n  Strongest wins:"); text += [f"    + {' · '.join(pick_line(r))}" for r in wins]
        inner.append(label_bar("The misses", f"{len(misses)} lost, every one named" if misses else "none this week"))
        for r in misses:
            m, meta = pick_line(r)
            inner.append(_p(f'<b style="color:{RED}">✗</b> <b style="color:{INK}">{E(m)}</b><br><span style="font-size:12px;color:{MUTE}">{E(meta)}</span>', 14, INK, "margin:6px 0"))
        text.append("\n  The misses:" + ("" if misses else " none")); text += [f"    x {' · '.join(pick_line(r))}" for r in misses]
    else:
        inner.append(_p("No Daily List pick settled this week.", 14, INK2, "padding-top:10px")); text.append("THE DAILY LIST\n  No Daily List pick settled this week.")
    rows.append(section("The Daily List", "landed against quoted", "".join(inner)))

    # 2. Each card's week
    lines = week_cards(src, a, b)
    inner = "".join(
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-bottom:1px solid {RULE}"><tr>'
        f'<td width="120" valign="top" style="padding:9px 8px 9px 0;font-family:{F_HEAD};font-size:13px;color:{INK}">{E(n)}</td>'
        f'<td valign="top" style="padding:9px 0;font-family:{F_BODY};font-size:14px;line-height:1.45;color:{INK2}">{E(l)}</td></tr></table>' for n, l in lines)
    inner += _p("Expected is each group's chance added up. A group wins only when every pick does. Each card's full ledger is on the site.", 12, MUTE, "padding-top:8px")
    rows.append(section("Every card's week", "won against expected", inner))
    text.append("\nEVERY CARD'S WEEK"); text += [f"  {n}: {l}" for n, l in lines]

    # 3. At real prices
    lab = (src.get("grecord") or {}).get("listAtBook") or {}
    ab = lab.get("atBook") or {}
    if ab.get("n"):
        frm = short_day(lab["from"]) if lab.get("from") else "the start"
        line = (f"Since {frm}, {ab['n']} settled list picks were priced at {lab.get('book') or BOOK} before the start: "
                f"{ab.get('won')} landed ({pct(ab.get('rate'))}) against {pct(ab.get('quoted'))} quoted, "
                f"{signed_pc(ab.get('ret') or 0, 1)} at {lab.get('book') or BOOK}'s price, one unit a pick.")
    else:
        line = "No list pick has a William Hill price on the record yet."
    rows.append(section("At real prices", "the list at William Hill", _p(E(line), 14, INK2, "padding-top:10px") +
                        _p("A high hit rate is not a profit: short prices land often and pay little.", 12, MUTE)))
    text.append("\nAT REAL PRICES\n  " + line)

    links = [("Every card's record", SITE + "#results?board=cards"), ("Today's Daily List", SITE + "#list"), ("Bets", SITE + "#today"), ("Scale", SITE + "#scale")]
    subject = f"The Weekly Record, {span}: " + (f"list {tot['won']} of {tot['n']}" if tot["n"] else "the week's cards")
    pre = f"The Daily List {tot['won']} of {tot['n']} landed, and every card's week." if tot["n"] else "Every card's week."
    body = wrap("The Weekly Record", span, pre, rows, footer_html(links))
    return {"subject": subject, "html": body, "text": "\n".join(text) + "\n\n" + footer_text(links), "count": tot["n"], "kind": "weekly"}


# ---------------------------------------------------------------- schedule

def due(now_uk):
    """The kinds due at this UK time: the daily from 07:00 to 11:59 every day, the
    weekly in the same window on Saturdays. Outside it nothing is sent."""
    if not SEND_FROM_H <= now_uk.hour < SEND_TO_H: return []
    return ["daily"] + (["weekly"] if now_uk.weekday() == WEEKLY_DOW else [])


# ---------------------------------------------------------------- sending

def personalise(body, token):
    return body.replace(MANAGE_MARK, MANAGE_URL.format(t=token)).replace(UNSUB_MARK, UNSUB_URL.format(t=token))


def message(to, token, mail):
    """One email for one recipient: their own links and one-click unsubscribe."""
    return {"from": SENDER, "to": [to], "subject": mail["subject"],
            "html": personalise(mail["html"], token), "text": personalise(mail["text"], token),
            "headers": {"List-Unsubscribe": f"<{UNSUB_URL.format(t=token)}>",
                        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"},
            # which email this is, so Resend's click and delivery events can be counted by kind (almanac.email_kpis)
            "tags": [{"name": "kind", "value": re.sub(r"[^A-Za-z0-9_-]", "_", mail.get("kind") or "email")}]}


def batches(xs, n=BATCH_MAX):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def _http(url, body, headers, timeout=30):
    """POST JSON. Returns (status, parsed body or None); status 0 for a lost connection."""
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "sports-almanac-mailer", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            try: return r.status, json.loads(raw or b"null")
            except ValueError: return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, None


def _rpc(name, body, post=_http):
    return post(f"{SUPABASE_URL}/rest/v1/rpc/{name}", body, {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})


def mail_list(secret, kind, post=_http):
    st, body = _rpc("almanac_mail_list", {"p_secret": secret, "p_kind": kind}, post)
    if not 200 <= st < 300 or not isinstance(body, list): raise RuntimeError(f"almanac_mail_list answered {st}")
    return [r for r in body if isinstance(r, dict) and r.get("email") and TOKEN_RE.match(str(r.get("manage_token") or ""))]


def mail_claim(secret, kind, day, post=_http):
    st, body = _rpc("almanac_mail_claim", {"p_secret": secret, "p_kind": kind, "p_day": day}, post)
    if not 200 <= st < 300: raise RuntimeError(f"almanac_mail_claim answered {st}")
    if isinstance(body, list): body = body[0] if body else False
    if isinstance(body, dict): body = next(iter(body.values()), False)
    return body is True


def send_batch(key, msgs, idem, post=_http, sleep=time.sleep):
    """One Resend batch call. A 429, a 5xx or a lost connection is tried twice more,
    with the same idempotency key, so a retry after a lost reply never sends twice;
    any 2xx ends it. Returns the HTTP status of the last try."""
    st = 0
    for attempt in range(RETRIES + 1):
        st, _ = post(RESEND_BATCH, msgs, {"Authorization": f"Bearer {key}", "Idempotency-Key": idem})
        if 200 <= st < 300: return st
        if not (st == 0 or st == 429 or st >= 500) or attempt == RETRIES: return st
        sleep(2 * (attempt + 1))
    return st


def send(key, kind, day, recipients, mails, post=_http, sleep=time.sleep, log=print):
    """Send `mails` (one per variant) to every recipient, one email each, in batches."""
    msgs = []
    for r in recipients:
        mail = mails["scale"] if kind == "daily" and r.get("scale") else mails["plain"]
        msgs.append(message(r["email"], r["manage_token"], mail))
    sent = failed = 0
    for i, chunk in enumerate(batches(msgs)):
        if i: sleep(RATE_GAP_S)
        st = send_batch(key, chunk, f"almanac-{kind}-{day}-{i}", post, sleep)
        if 200 <= st < 300: sent += len(chunk)
        else:
            failed += len(chunk); log(f"mailer: {kind} batch {i + 1} failed (HTTP {st})")
    log(f"mailer: {kind} {day}: {sent} sent, {failed} failed, {len(recipients)} on the list")
    return sent, failed


def build(kind, day, src, now=None):
    """Both variants of a kind's email: {"plain", "scale"} (the weekly has one)."""
    if kind == "daily":
        return {"plain": daily_email(day, src, False, now), "scale": daily_email(day, src, True, now)}
    w = weekly_email(day, src)
    return {"plain": w, "scale": w}


def stale(kind, day, src):
    """Why today's files cannot make today's email, or None."""
    if kind != "daily": return None if (src.get("ledger") and src.get("grecord")) else "the record files are missing"
    dl = src.get("daylist") or {}
    if dl.get("date") != day: return f"daylist.json is for {dl.get('date') or 'no day'}, not {day}"
    if not src.get("groupings"): return "groupings-data.js is missing"
    return None


def run(now=None, env=None, post=_http, sleep=time.sleep, log=print, src=None):
    env = os.environ if env is None else env
    key, secret = env.get("RESEND_API_KEY"), env.get("MAILER_SECRET")
    if not key or not secret:
        log("mailer: not configured (RESEND_API_KEY or MAILER_SECRET missing); nothing sent")
        return 0
    now = now or datetime.now(timezone.utc)
    now_uk = now.astimezone(UK)
    day = now_uk.date().isoformat()
    kinds = due(now_uk)
    if not kinds:
        log(f"mailer: {now_uk:%H:%M} UK is outside the 07:00-11:59 send window; nothing sent (a missed morning is skipped)")
        return 0
    src = src if src is not None else load()
    for kind in kinds:
        why = stale(kind, day, src)
        if why: log(f"mailer: {kind} skipped: {why}"); continue
        try:
            mails = build(kind, day, src, now)
            recipients = mail_list(secret, kind, post)
            if not recipients: log(f"mailer: {kind} {day}: nobody on the list"); continue
            if not mail_claim(secret, kind, day, post):
                log(f"mailer: {kind} {day} already claimed by another build; nothing sent"); continue
            sent, _ = send(key, kind, day, recipients, mails, post, sleep, log)
            if kind == "daily" and sent:
                log(f"mailer: kept {os.path.relpath(keep(day, src, now, mails['plain']), HERE)}")
        except Exception as e:   # one kind failing never stops the other, never fails the build
            log(f"mailer: {kind} failed: {type(e).__name__}: {str(e)[:120]}")
    return 0


def preview(out, day, src=None, now=None):
    src = src if src is not None else load()
    os.makedirs(out, exist_ok=True)
    d = daily_email(day, src, True, now)
    w = weekly_email(day, src)
    for name, m in (("daily", d), ("weekly", w)):
        for ext in ("html", "txt"):
            with open(os.path.join(out, f"{name}.{ext}"), "w", encoding="utf-8") as f:
                f.write(personalise(m["html" if ext == "html" else "text"], TEST_TOKEN))
    for name, m in welcome_emails():
        with open(os.path.join(out, f"{name}.html"), "w", encoding="utf-8") as f:
            f.write(personalise(m["html"], TEST_TOKEN).replace(CONFIRM_MARK, CONFIRM_URL.format(t=TEST_TOKEN)))
    print(f"mailer: preview written to {out} (daily: {d['count']} list picks; weekly: {w['count']} settled list picks)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--preview", metavar="DIR", help="write daily/weekly .html and .txt from the local files, no network")
    ap.add_argument("--day", help="the UK day, YYYY-MM-DD (default today)")
    ap.add_argument("--kind", choices=["daily", "weekly", "welcome", "all"], default="daily", help="with --to: which email(s)")
    ap.add_argument("--to", metavar="EMAIL", help="send one test copy (needs RESEND_API_KEY), no claim")
    a = ap.parse_args(argv)
    day = a.day or datetime.now(UK).date().isoformat()
    if a.preview: return preview(a.preview, day)
    if a.to:
        key = os.environ.get("RESEND_API_KEY")
        if not key: print("mailer: not configured (RESEND_API_KEY missing); nothing sent"); return 0
        src = load()
        mails = []
        if a.kind in ("daily", "all"): mails.append(("daily", daily_email(day, src, True)))
        if a.kind in ("weekly", "all"): mails.append(("weekly", weekly_email(day, src)))
        if a.kind in ("welcome", "all"):
            mails += [(n, {**m, "html": m["html"].replace(CONFIRM_MARK, CONFIRM_URL.format(t=TEST_TOKEN)),
                           "text": m["text"].replace(CONFIRM_MARK, CONFIRM_URL.format(t=TEST_TOKEN))})
                      for n, m in welcome_emails()]
        for n, m in mails:
            m = {**m, "subject": "[Test] " + m["subject"]}
            st = send_batch(key, [message(a.to, TEST_TOKEN, m)], f"almanac-test-{n}-{day}-{int(time.time())}")
            print(f"mailer: test {n} copy {'sent' if 200 <= st < 300 else f'failed (HTTP {st})'}")
            time.sleep(RATE_GAP_S)
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
