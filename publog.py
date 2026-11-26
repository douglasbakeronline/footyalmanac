"""The publication log (26 Nov 2026, Douglas: "provide log entries each day
for every group, card, scale and edge picks ever made. We need to hold onto
this data to perfect the platform with each iterative improvement").

Every build, after groupings.py, scale.py and slip.py, this records every
item the page put forward, one file a UK day:

    groupings-archive/published/<day>.json

Items: every group groupings.py built (the Card, the Daily 2x, the List card,
the Model card), every Scale pick and Scale group, the slip, and every Edge
pick on the football board. Each item keeps when it was first and last seen,
how many builds showed it, its first and last snapshot (picks, prices,
chances, status), each change of status or price between builds, and `gone`
when a build that still covered its day no longer showed it (withdrawn or
replaced). Nothing here is graded or fitted: the archives and records stay
the scoreboard (Rule 1). It exists so nothing the page published is ever
lost again: from 28 Oct to 25 Nov five groups were published and never
reached the archive (claude/card-overnight-day-2026-11-26.md), and the only
trace was a count in the build logs.

`--seed` fills the log once from everything already kept: the groupings
archive's locked groups, the Scale and slip archives, the Edge flags in
predictions/ and the
five groups the build logs show were lost (count and kind only, picks where
card-short kept them). Seeded entries carry `source`; a build writes
`source: "build"`. Standard library only.
"""
import glob, gzip, json, os, sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(HERE, "groupings-archive", "published")
CHANGES_MAX = 60      # status / price changes kept per item

# The five groups the build logs show were open at the last build of their
# day and never archived (28 Oct to 25 Nov 2026, the deploy runs' "<day>: n
# holding" lines). The kind is by elimination against what the day archived;
# only 25 Nov's picks were kept (card-short.json). claude/card-overnight-day-2026-11-26.md
LOST = [
    {"day": "2026-11-02", "kind": "model", "name": "Model 3x", "run": "41548052717", "picks": None},
    {"day": "2026-11-04", "kind": "model", "name": "Model 3x", "run": "41925186856", "picks": None},
    {"day": "2026-11-13", "kind": "card", "name": "Card 2x", "run": "43518924506", "picks": None},
    {"day": "2026-11-17", "kind": "list", "name": "List 2x or List long", "run": "44202004853", "picks": None},
    {"day": "2026-11-25", "kind": "card", "name": "Card 2x", "run": "45701015681",
     "picks": ["Golden State Warriors", "Memphis Grizzlies", "Toluca"]},
]


def iso(t): return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path, default=None):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f: return json.load(f)
        with open(path, encoding="utf-8") as f: return json.load(f)
    except (OSError, ValueError):
        return default


def group_kind(name):
    n = str(name or "")
    if n.startswith("Card"): return "card"
    if n.startswith("Daily"): return "daily"
    if n.startswith("List"): return "list"
    if n.startswith("Model"): return "model"
    return "group"


def gid(g):
    return "|".join(sorted(f"{l.get('event')}>{l.get('pick')}" for l in g.get("legs") or []))


LEG_KEYS = ("event", "pick", "sport", "comp", "code", "when", "odds", "best", "bestBook", "firstOdds",
            "pModel", "p", "fair", "opp", "draw", "tested", "status", "est", "tier", "list", "reserve")
GROUP_KEYS = ("name", "window", "seq", "odds", "bestOdds", "bookOdds", "book", "p", "pFair", "implied", "tested",
              "stake", "paper", "short", "span", "status", "locked", "late", "first", "checked", "lockAt", "wide",
              "rule", "wideRule")


def snap_group(g):
    s = {k: g[k] for k in GROUP_KEYS if g.get(k) is not None}
    s["legs"] = [{k: l[k] for k in LEG_KEYS if l.get(k) is not None} for l in g.get("legs") or []]
    return s


def start_of(snap):
    """The item's first start, from any of the shapes logged."""
    ts = [l.get("when") or l.get("start") for l in snap.get("legs") or [] if isinstance(l, dict)]
    ts += [snap.get("start"), snap.get("first") if snap.get("legs") is None else None]
    ts = [t for t in ts if t]
    return min(ts) if ts else None


# ---------------------------------------------------------------- what the build showed

def from_groupings(og):
    """{day: {key: (kind, snap)}} and the days the build covered."""
    out, days = {}, set()
    for d in (og or {}).get("days") or []:
        days.add(d["date"])
        rule = ((og.get("rules") or {}).get("card") or {}).get("rule")
        for g in d.get("groups") or []:
            k = group_kind(g.get("name"))
            s = snap_group(g)
            if k == "card" and rule is not None: s.setdefault("cardRule", rule)
            out.setdefault(d["date"], {})[f"{k}|{g.get('name')}|{g.get('seq') or 1}|{gid(g)}"] = (k, s)
    return out, days


def from_scale(doc):
    out = {}
    for p in doc.get("picks") or []:
        out[f"scale-pick|{p['key']}"] = ("scale-pick", dict(p))
    for g in doc.get("groups") or []:
        out[f"scale-group|{g.get('kind')}|{'+'.join(g.get('legs') or [])}"] = ("scale-group", dict(g))
    return out


def from_slip(doc):
    s = (doc or {}).get("slip")
    if not s: return {}
    return {"slip|" + "+".join(l.get("key", "") for l in s.get("legs") or []): ("slip", dict(s, rule=doc.get("rule")))}


EDGE_KEYS = ("league", "date", "home", "away", "kickoff", "p", "confidence", "list", "reserve", "edge", "market")


def from_edge_rows(rows):
    out = {}
    for r in rows or []:
        if not isinstance(r, dict) or not r.get("edge"): continue
        snap = {k: r[k] for k in EDGE_KEYS if r.get(k) is not None}
        snap["start"] = r.get("kickoff") or r.get("when")
        out.setdefault(r.get("date"), {})[f"edge|{r.get('league')}|{r.get('home')}|{r.get('away')}"] = ("edge", snap)
    return out


def from_data(data):
    """Edge picks on this build's football board (data.json)."""
    out, days = {}, set()
    for d in (data or {}).get("days") or []:
        days.add(d.get("date"))
        rows = [dict(g, date=d.get("date"), league=g.get("league") or g.get("code")) for g in d.get("games") or []]
        for day, items in from_edge_rows(rows).items(): out.setdefault(day, {}).update(items)
    return out, days


# ---------------------------------------------------------------- the merge

WATCH = ("status", "locked", "odds", "bookOdds", "price", "chance", "conf")


def changed(a, b):
    return {k: [a.get(k), b.get(k)] for k in WATCH if a.get(k) != b.get(k)}


def merge(doc, seen, covered, at, source="build"):
    """Fold one build's items for one day into the day's log. `covered` is
    the set of kinds this build read for the day: an item of a covered kind
    not seen is marked gone (withdrawn or replaced), never deleted."""
    items = doc.setdefault("items", {})
    for key, (kind, snap) in seen.items():
        e = items.get(key)
        if e is None:
            items[key] = {"kind": kind, "source": source, "firstSeen": at, "lastSeen": at, "builds": 1,
                          "start": start_of(snap), "first": snap, "last": snap, "changes": []}
            continue
        diff = changed(e.get("last") or {}, snap)
        if e.get("gone"):
            e["changes"].append({"at": at, "back": True}); e.pop("gone", None)
        if diff:
            e["changes"].append({"at": at, **diff}); e["changes"] = e["changes"][-CHANGES_MAX:]
        e.update(lastSeen=at, builds=e.get("builds", 0) + 1, last=snap, start=start_of(snap) or e.get("start"))
    for key, e in items.items():
        if key not in seen and e["kind"] in covered and not e.get("gone") and e.get("source") == "build":
            e["gone"] = at
    return doc


def day_path(day): return os.path.join(LOG_DIR, f"{day}.json")


def load_day(day):
    return _load(day_path(day)) or {"day": day, "items": {}}


def save_day(doc):
    os.makedirs(LOG_DIR, exist_ok=True)
    p = day_path(doc["day"])
    doc["items"] = dict(sorted(doc["items"].items(), key=lambda kv: (kv[1].get("kind", ""), kv[1].get("start") or "", kv[0])))
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(doc, f, separators=(",", ":"), ensure_ascii=False)
        f.write("\n")
    os.replace(p + ".tmp", p)


def record_build(now=None, here=HERE):
    """Log what this build showed. Returns {day: items seen}."""
    now = now or datetime.now(timezone.utc); at = iso(now)
    per_day, covered = {}, {}
    og = _load(os.path.join(here, "groupings.json"))
    if og:
        items, days = from_groupings(og)
        for d in days: covered.setdefault(d, set()).update({"card", "daily", "list", "model", "group"})
        for d, it in items.items(): per_day.setdefault(d, {}).update(it)
    data = _load(os.path.join(here, "data.json"))
    if data:
        items, days = from_data(data)
        for d in days: covered.setdefault(d, set()).add("edge")
        for d, it in items.items(): per_day.setdefault(d, {}).update(it)
    from zoneinfo import ZoneInfo
    today = now.astimezone(ZoneInfo("Europe/London")).date()
    for k in range(-1, 4):
        day = (today + timedelta(days=k)).isoformat()
        sc = _load(os.path.join(here, "scale-archive", f"{day}.json"))
        if sc:
            covered.setdefault(day, set()).update({"scale-pick", "scale-group"})
            per_day.setdefault(day, {}).update(from_scale(sc))
        sl = _load(os.path.join(here, "slip-archive", f"{day}.json"))
        if sl:
            covered.setdefault(day, set()).add("slip")
            per_day.setdefault(day, {}).update(from_slip(sl))
    for day in sorted(set(per_day) | set(covered)):
        if not day: continue
        doc = load_day(day)
        merge(doc, per_day.get(day, {}), covered.get(day, set()), at)
        doc["updated"] = at
        save_day(doc)
    return {d: len(v) for d, v in per_day.items()}


# ---------------------------------------------------------------- the seed

def seed(here=HERE):
    """Fill the log from everything already kept (once; re-running adds
    nothing new: seeded items merge on their keys)."""
    n = {}
    def put(day, items, at, source):
        if not day or not items: return
        doc = load_day(day)
        for key, (kind, snap) in items.items():
            if key in doc["items"]: continue
            doc["items"][key] = {"kind": kind, "source": source, "firstSeen": snap.get("first") if isinstance(snap.get("first"), str) else at,
                                 "lastSeen": at, "builds": None, "start": start_of(snap), "first": snap, "last": snap, "changes": []}
            n[source] = n.get(source, 0) + 1
        save_day(doc)
    arch = os.path.join(here, "groupings-archive")
    for f in sorted(glob.glob(os.path.join(arch, "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))):
        a = _load(f) or {}
        day = a.get("date") or os.path.basename(f)[:10]
        items = {}
        for g in a.get("groups") or []:
            k = group_kind(g.get("name"))
            items[f"{k}|{g.get('name')}|{g.get('seq') or 1}|{gid(g)}"] = (k, snap_group(g))
        put(day, items, a.get("published") or day, "archive")
    for f in sorted(glob.glob(os.path.join(here, "scale-archive", "*.json"))):
        doc = _load(f) or {}
        put(doc.get("date") or os.path.basename(f)[:10], from_scale(doc), os.path.basename(f)[:10], "scale-archive")
    for f in sorted(glob.glob(os.path.join(here, "slip-archive", "*.json"))):
        doc = _load(f) or {}
        put(doc.get("date") or os.path.basename(f)[:10], from_slip(doc), doc.get("built") or os.path.basename(f)[:10], "slip-archive")
    for f in sorted(glob.glob(os.path.join(here, "predictions", "*.json"))):
        rows = _load(f)
        if not isinstance(rows, list): continue
        for day, items in from_edge_rows(rows).items():
            put(day, items, os.path.basename(f)[:10], "predictions")
    for x in LOST:
        doc = load_day(x["day"])
        key = f"lost|{x['name']}|{x['run']}"
        if key not in doc["items"]:
            doc["items"][key] = {"kind": x["kind"], "source": "build-log", "lost": True, "run": x["run"], "name": x["name"],
                                 "picks": x["picks"], "note": "open at the last build of its day, never archived; kind by elimination"
                                 if not x["picks"] else "open at the last build of its day, never archived; picks from card-short.json"}
            save_day(doc); n["build-log"] = n.get("build-log", 0) + 1
    return n


def unarchived(now=None, days=3, here=HERE):
    """Groups a build put on the page, not withdrawn, whose first pick
    started 2+ hours ago, and that are not in groupings-archive/<day>.json:
    the failure behind the five lost groups. Read by tools/card_integrity.py
    (`group-unarchived`)."""
    now = now or datetime.now(timezone.utc)
    out = []
    for k in range(-days, 1):
        day = (now.date() + timedelta(days=k)).isoformat()
        doc = _load(day_path(day))
        if not doc: continue
        arch = _load(os.path.join(here, "groupings-archive", f"{day}.json")) or {}
        have = {gid(g) for g in arch.get("groups") or []}
        for key, e in doc.get("items", {}).items():
            if e.get("source") != "build" or e.get("gone") or e.get("kind") not in ("card", "daily", "list", "model", "group"):
                continue
            st = e.get("start")
            try: t = datetime.fromisoformat(str(st).replace("Z", "+00:00"))
            except ValueError: continue
            if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
            if now - t < timedelta(hours=2) or gid(e.get("last") or {}) in have: continue
            out.append({"check": "group-unarchived", "date": day, "group": (e.get("last") or {}).get("name"),
                        "picks": [l.get("pick") for l in (e.get("last") or {}).get("legs") or []], "start": st})
    return out


def report(day):
    """One line an item, for reading a day by hand."""
    doc = _load(day_path(day))
    if not doc: return f"{day}: nothing logged"
    lines = [f"{day}: {len(doc['items'])} item(s)"]
    for key, e in doc["items"].items():
        last = e.get("last") or {}
        name = last.get("name") or e.get("name") or e["kind"]
        picks = [l.get("pick") for l in last.get("legs") or [] if isinstance(l, dict)] or e.get("picks") or [last.get("pick") or last.get("home")]
        price = last.get("odds") or last.get("price")
        state = "LOST" if e.get("lost") else ("withdrawn " + e["gone"] if e.get("gone") else (last.get("status") or ""))
        lines.append(f"  {e['kind']:<11} {str(name)[:22]:<22} {', '.join(str(p) for p in picks if p)[:70]:<70} "
                     f"{price if price is not None else '':<6} {state} [{e.get('source')}]")
    return "\n".join(lines)


def main():
    if "--day" in sys.argv:
        print(report(sys.argv[sys.argv.index("--day") + 1])); return 0
    if "--seed" in sys.argv:
        n = seed()
        print("publog seed: " + ", ".join(f"{k} {v}" for k, v in sorted(n.items())))
        return 0
    seen = record_build()
    print("publog: " + (", ".join(f"{d} {n}" for d, n in sorted(seen.items())) or "nothing on the page"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
