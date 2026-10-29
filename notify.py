#!/usr/bin/env python3
"""
Push a note to Douglas's phone when the build makes a new Card group.
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
    title = f"{g['name']} · {d.strftime('%a %d %b') if d else date} · {g['odds']:.2f}" + (
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
    if g.get("status") == "replacement": lines.append("Replaces a group that failed its re-check.")
    return title, "\n".join(lines)


def send(topic, title, body, tags="ticket"):
    req = urllib.request.Request(f"{NTFY}/{topic}", data=body.encode("utf-8"), method="POST",
                                 headers={"Title": title, "Tags": tags, "Priority": "high"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


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
                send(topic, title, body); sent += 1
            except Exception as e:
                print(f"notify: send failed ({type(e).__name__})")
    print(f"notify: {sent} sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
