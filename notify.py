#!/usr/bin/env python3
"""
Push a note to Douglas's phone when the build makes a new Card group, and
once a UK day a morning briefing of the Daily List (10 Nov 2026, below).
29 Oct 2026, Douglas: "no time lock, but I get a push notification once a
betting group is created".

    python3 notify.py            after groupings.py, in deploy.yml

Reads groupings.json (this build's output). Every Card group whose status is
"new" or "replacement" and whose `first` stamp is this build's (so a group
first shown on an earlier build is not sent again) gets one message. Sends
through ntfy (https://ntfy.sh): a free push service with iOS and Android
apps; the topic name is the only secret, so it is read from NTFY_TOPIC and
never printed. Nothing is sent when the variable is unset, so a fork or a
local run is silent. Standard library only.

Message: "Card 2x · Fri 30 Oct · 2.18 (2.26 best)" then one line a pick
with its kick-off, price at the card's bookmaker (or best), and the group's
first kick-off, which is when it freezes.
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
UK = ZoneInfo("Europe/London")
NTFY = os.environ.get("NTFY_URL", "https://ntfy.sh")


def when(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UK)
    except Exception:
        return None


def message(g, date):
    book = g.get("book") or "William Hill"
    d = when(date + "T12:00:00Z")
    # ASCII only in the title: it travels as an HTTP header, which drops non-Latin bytes
    title = f"{g['name']}, {d.strftime('%a %d %b') if d else date}, {g['odds']:.2f}" + (
        f" ({g['bookOdds']:.2f} at {book})" if g.get("bookOdds") else f" ({g['bestOdds']:.2f} best)" if g.get("bestOdds") else "")
    lines = []
    for l in g["legs"]:
        t = when(l.get("when") or "")
        px = (l.get("bookOdds") or {}).get(book)
        price = f"{px:.2f} {book}" if px else f"{(l.get('best') or l['odds']):.2f} {l.get('bestBook') or 'avg'}"
        lines.append(f"{t.strftime('%a %H:%M') if t else '--:--'}  {l['pick']}  {price}")
    first = min((when(l.get("when") or "") for l in g["legs"] if when(l.get("when") or "")), default=None)
    units = g.get("stake") or 1
    lines.append(f"{units} unit{'s' if units != 1 else ''} · open until {first.strftime('%a %H:%M') if first else 'first kick-off'}"
                 + (f" · {len(g['bench'])} substitute{'s' if len(g['bench']) != 1 else ''}" if g.get("bench") else ""))
    if g.get("status") == "replacement":
        # 29 Oct 2026: a replacement is flagged in the title and tagged apart,
        # so a group placed from the earlier push is noticed
        title = "REPLACEMENT: " + title
        lines.append("Replaces a group that failed its re-check. If you placed the earlier version, your bet stands; the record grades this one.")
    return title, "\n".join(lines)


def send(topic, title, body, tags="soccer", priority="high", click=None):
    headers = {"Title": title, "Tags": tags, "Priority": priority}
    if click: headers["Click"] = click
    req = urllib.request.Request(f"{NTFY}/{topic}", data=body.encode("utf-8"), method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


# ---------- the morning briefing (10 Nov 2026) ----------
# Douglas: "develop more". One push a UK day, from the first build at or after
# BRIEF_HOUR UK: the day's Daily List count, Group A, the model treble (the
# week-ahead panel's rule), the Edge picks and the Card, with a link to the
# site. The day already briefed is kept in groupings-archive/briefed.json,
# which the build commits with the rest of the archive, so a late or repeated
# build never sends it twice. Display only, like everything here.
SITE = "https://douglasbakeronline.github.io/footyalmanac/"
BRIEF_HOUR = 5
BRIEF_FILE = os.path.join(HERE, "groupings-archive", "briefed.json")
GROUP_A_MIN = 0.85     # daylist.GROUP_A_MIN


def _hm(s):
    t = when(s or "")
    return t.strftime("%H:%M") if t else "--:--"


def briefing(og, data, now):
    """(title, body) for the UK day of `now`, or None when it has no list pick."""
    day = now.astimezone(UK).date().isoformat()
    # the pool is filed by board date (UTC for the US sports); a list pick
    # belongs to the UK day it starts on, as on the Daily List
    def uk_day(l, filed):
        t = when(l.get("when") or "")
        return t.date().isoformat() if t else filed
    legs = [l for d, ls in (og.get("pool") or {}).items() for l in ls if l.get("list") and uk_day(l, d) == day]
    seen, picks = set(), []
    for l in sorted(legs, key=lambda l: -(l.get("pModel") or 0)):
        k = (l.get("event"), l.get("pick"))
        if k in seen: continue
        seen.add(k); picks.append(l)
    if not picks: return None
    d = now.astimezone(UK)
    title = f"Daily List, {d.strftime('%a %d %b')}: {len(picks)} pick{'s' if len(picks) != 1 else ''}"
    lines = []
    a = [l for l in picks if (l.get("pModel") or 0) >= GROUP_A_MIN][:5]
    if a:
        lines.append("Group A: " + "; ".join(f"{l['pick']} {round(l['pModel'] * 100)}% {_hm(l.get('when'))}" for l in a))
    open_ = [l for l in picks if (when(l.get("when") or "") or now) > now][:3]
    if len(open_) >= 2:
        ch = 1.0
        for l in open_: ch *= l.get("pModel") or 0
        lines.append(f"Model {'treble' if len(open_) == 3 else 'double'} {round(ch * 100)}%: " + ", ".join(l["pick"] for l in open_))
    edge = [g for dd in (data.get("days") or []) if dd.get("date") == day for g in dd.get("games") or [] if g.get("edge")]
    if edge:
        lines.append(f"Edge: {len(edge)} football pick{'s' if len(edge) != 1 else ''} (" + ", ".join(
            (g["home"]["name"] if g["edge"].get("side") == "h" else g["away"]["name"]) + f" {g['edge']['odds']:.2f}" for g in edge[:3]) + ")")
    card = [g for dd in og.get("days") or [] if dd.get("date") == day for g in dd.get("groups") or []
            if str(g.get("name", "")).startswith("Card") and not g.get("wide") and g.get("status") != "underway"]
    lines.append(f"Card: {len(card)} group{'s' if len(card) != 1 else ''} open" if card
                 else "Card: nothing qualifies yet; prices are read again on every build")
    return title, "\n".join(lines)


def brief_due(now, path=BRIEF_FILE):
    if now.astimezone(UK).hour < BRIEF_HOUR: return False
    try:
        with open(path) as f: last = json.load(f).get("date")
    except (OSError, ValueError):
        last = None
    return last != now.astimezone(UK).date().isoformat()


def mark_briefed(now, path=BRIEF_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"date": now.astimezone(UK).date().isoformat(), "at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}, f)


def main():
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        print("notify: NTFY_TOPIC not set, nothing sent"); return 0
    try:
        with open(os.path.join(HERE, "groupings.json")) as f: og = json.load(f)
    except (OSError, ValueError) as e:
        print(f"notify: no groupings.json ({e})"); return 0
    stamp = og.get("generated")
    sent = 0
    for day in og.get("days") or []:
        for g in day.get("groups") or []:
            if not str(g.get("name", "")).startswith("Card"): continue
            if g.get("status") not in ("new", "replacement") or g.get("first") != stamp: continue
            title, body = message(g, day["date"])
            try:
                send(topic, title, body, "warning" if g.get("status") == "replacement" else "soccer"); sent += 1
            except Exception as e:
                print(f"notify: send failed ({type(e).__name__})")
    print(f"notify: {sent} sent")
    now = datetime.now(timezone.utc)
    if brief_due(now):
        try:
            with open(os.path.join(HERE, "data.json")) as f: data = json.load(f)
        except (OSError, ValueError):
            data = {}
        b = briefing(og, data, now)
        if b:
            try:
                send(topic, b[0], b[1], "sunrise", "default", SITE); mark_briefed(now)
                print("notify: morning briefing sent")
            except Exception as e:
                print(f"notify: briefing failed ({type(e).__name__})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
