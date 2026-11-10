#!/usr/bin/env python3
"""
Push a note to Douglas's phone when the build makes a new Card group, and
four briefings a UK day at his betting times (10 Nov 2026, below).
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
from datetime import datetime, timedelta, timezone
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


# ---------- the briefings (10 Nov 2026) ----------
# Douglas: "I'm most likely to want to place a bet in the morning around 8am,
# around lunchtime, early evening and before I go to bed." One push in each of
# four slots a UK day, from the first build at or after the slot's hour (the
# 07:40, 12:00, 17:00 and 22:15 builds): what is still to start, the
# strongest list picks, the model treble, Edge picks and open Card groups,
# and from lunch on, how the day's list has gone so far. Only the latest due
# slot is sent, so a late build never sends a stale one; slots sent are kept
# in groupings-archive/briefed.json, which the build already commits, so a
# repeated build never sends twice. Display only, like everything here.
SITE = "https://douglasbakeronline.github.io/footyalmanac/"
SLOTS = [("morning", 7), ("lunch", 11), ("evening", 16), ("night", 21)]
BRIEF_FILE = os.path.join(HERE, "groupings-archive", "briefed.json")
GROUP_A_MIN = 0.85     # daylist.GROUP_A_MIN
NIGHT_UNTIL = 8        # the bedtime push covers picks starting before 08:00 UK tomorrow


def _hm(s):
    t = when(s or "")
    return t.strftime("%H:%M") if t else "--:--"


def _uk_day(l, filed):
    t = when(l.get("when") or "")
    return t.date().isoformat() if t else filed


def _list_picks(og, day):
    """The day's list picks, each once, strongest first. The pool is filed by
    board date (UTC for the US sports); a pick belongs to the UK day it starts
    on, as on the Daily List."""
    seen, out = set(), []
    legs = [l for d, ls in (og.get("pool") or {}).items() for l in ls if l.get("list") and _uk_day(l, d) == day]
    for l in sorted(legs, key=lambda l: -(l.get("pModel") or 0)):
        k = (l.get("event"), l.get("pick"))
        if k not in seen: seen.add(k); out.append(l)
    return out


def _tally(picks, idx):
    won = lost = 0
    if idx is None: return None
    try:
        import groupings as G
    except Exception:
        return None
    for l in picks:
        try: st, _ = G.settle(l, idx)
        except Exception: continue
        won += st == "won"; lost += st == "lost"
    return won, lost


def due_slot(now, path=BRIEF_FILE):
    """The latest slot whose hour has passed today and has not been sent."""
    uk = now.astimezone(UK)
    due = [name for name, h in SLOTS if uk.hour >= h]
    if not due: return None
    try:
        with open(path) as f: st = json.load(f)
    except (OSError, ValueError):
        st = {}
    sent = (st.get("slots") or []) if st.get("date") == uk.date().isoformat() else []
    return None if due[-1] in sent else due[-1]


def mark_sent(now, slot, path=BRIEF_FILE):
    uk = now.astimezone(UK); day = uk.date().isoformat()
    try:
        with open(path) as f: st = json.load(f)
    except (OSError, ValueError):
        st = {}
    slots = (st.get("slots") or []) if st.get("date") == day else []
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"date": day, "slots": slots + [slot], "at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}, f)


def briefing(og, data, now, slot="morning", idx=None):
    """(title, body) for one slot, or None when there is nothing to back."""
    uk = now.astimezone(UK); day = uk.date().isoformat()
    today = _list_picks(og, day)
    picks = list(today)
    if slot == "night":
        # bedtime: tonight's late games and the overnight US slate
        tomorrow = (uk + timedelta(days=1)).date().isoformat()
        cut = datetime.fromisoformat(f"{tomorrow}T{NIGHT_UNTIL:02d}:00").replace(tzinfo=UK)
        picks += [l for l in _list_picks(og, tomorrow) if (when(l.get("when") or "") or cut) < cut]
        picks.sort(key=lambda l: -(l.get("pModel") or 0))
    open_ = [l for l in picks if (when(l.get("when") or "") or now) > now]
    edge = [g for dd in (data.get("days") or []) for g in dd.get("games") or []
            if g.get("edge") and (when(g.get("kickoff") or "") or now) > now and _uk_day({"when": g.get("kickoff")}, dd.get("date")) == day]
    card = [g for dd in og.get("days") or [] if dd.get("date") == day for g in dd.get("groups") or []
            if str(g.get("name", "")).startswith("Card") and not g.get("wide") and g.get("status") != "underway"]
    if not open_ and not card and not edge: return None
    d = uk.strftime('%a %d %b')
    n = len(open_)
    title = {"morning": f"Daily List, {d}: {len(today)} pick{'s' if len(today) != 1 else ''}",
             "lunch": f"Lunchtime, {d}: {n} list pick{'s' if n != 1 else ''} to start",
             "evening": f"This evening, {d}: {n} list pick{'s' if n != 1 else ''} to start",
             "night": f"Tonight and overnight: {n} list pick{'s' if n != 1 else ''} before {NIGHT_UNTIL}am"}[slot]
    lines = []
    if slot != "morning":
        t = _tally(today, idx)
        if t and sum(t): lines.append(f"Today so far: {t[0]} won, {t[1]} lost")
    a = [l for l in open_ if (l.get("pModel") or 0) >= GROUP_A_MIN][:5] or open_[:3]
    if a:
        lines.append(("Strongest to come: " if slot != "morning" else "Group A: ")
                     + "; ".join(f"{l['pick']} {round(l['pModel'] * 100)}% {_hm(l.get('when'))}" for l in a))
    m = open_[:3]
    if len(m) >= 2:
        ch = 1.0
        for l in m: ch *= l.get("pModel") or 0
        lines.append(f"Model {'treble' if len(m) == 3 else 'double'} {round(ch * 100)}%: " + ", ".join(l["pick"] for l in m))
    if edge:
        lines.append(f"Edge: {len(edge)} football pick{'s' if len(edge) != 1 else ''} (" + ", ".join(
            (g["home"]["name"] if g["edge"].get("side") == "h" else g["away"]["name"]) + f" {g['edge']['odds']:.2f}" for g in edge[:3]) + ")")
    if card:
        hill = [g.get("bookOdds") for g in card if g.get("bookOdds")]
        lines.append(f"Card: {len(card)} group{'s' if len(card) != 1 else ''} open" + (f", Hill {', '.join(f'{x:.2f}' for x in hill)}" if hill else ""))
    elif slot == "morning":
        lines.append("Card: nothing qualifies yet; prices are read again on every build")
    return title, "\n".join(lines)


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
    slot = due_slot(now)
    if slot:
        try:
            with open(os.path.join(HERE, "data.json")) as f: data = json.load(f)
        except (OSError, ValueError):
            data = {}
        try:
            import groupings as G
            idx = G.results_index()
        except Exception:
            idx = None
        b = briefing(og, data, now, slot, idx)
        if b:
            try:
                send(topic, b[0], b[1], {"morning": "sunrise", "lunch": "sandwich", "evening": "city_sunset", "night": "crescent_moon"}[slot],
                     "default", SITE)
                print(f"notify: {slot} briefing sent")
            except Exception as e:
                print(f"notify: {slot} briefing failed ({type(e).__name__})")
                return 0
        # sent, or nothing to back: either way this slot is done for the day
        mark_sent(now, slot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
