"""Today's Daily List, pinned for the whole UK day.

The live data files (data.json, tennis-data.js, sports-data.js) only carry
games that have not started, so a day that began with six picks used to read
"0 picks" by the evening, on the site and in the office (5 Oct 2026: six
tennis picks gone by 18:00). This writes the day's list as it stood before
each game started, with how each one went so far.

Membership uses the same rule the record grades by: for each game, the latest
archived price published before its start (predictions*/<build date>.json,
merged, never rewritten after the start). A game that has not started yet can
still change on a later build, exactly as on the live list. Once it starts it
is frozen.

Results come from the three record files written earlier in the same build
(record.json, tennis-record.json, sports-record.json). Nothing here is fitted,
priced or graded anew: it is a read of the archive and the record.

Writes daylist.json and daylist.js (window.__DAY_LIST__). Standard library.
"""
import glob, json, os, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
UK = ZoneInfo("Europe/London")
LOOKBACK = 8          # build-date archive files to read: a game can be priced days ahead


def parse_utc(s):
    if not s: return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else None


def uk_day(dt): return dt.astimezone(UK).date().isoformat()


def _load(path, default=None):
    try:
        with open(path) as f: return json.load(f)
    except Exception:
        return default


def _football_tier(conf, celtic, unrated):
    if unrated: return "No read"
    tiers = [(0.70, "Strong"), (0.62, "Firm"), (0.55, "Lean"), (0.0, "No read")]
    i = next(i for i, (m, _) in enumerate(tiers) if conf >= m)
    if celtic and i < len(tiers) - 1: i += 1
    return tiers[i][1]


def _leagues():
    try:
        sys.path.insert(0, HERE)
        import engine as E
        return E.LEAGUES
    except Exception:
        return {}


def football_item(g, leagues):
    ko = parse_utc(g.get("kickoff"))
    if ko:
        start = ko
    else:
        try: start = datetime.fromisoformat(g["date"] + "T00:00:00+00:00")
        except Exception: return None
    p = g.get("p") or {}
    side = max(p, key=p.get) if p else "h"
    lg = leagues.get(g.get("league")) or {}
    return {"sport": "football", "key": f"f|{g['league']}|{g['date']}|{g['home']}|{g['away']}",
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "timed": bool(ko), "date": g["date"],
            "league": g.get("league"),
            "comp": f"{lg.get('country', '')} {lg.get('name', g.get('league') or '')}".strip(),
            "home": g["home"], "away": g["away"], "side": side,
            "pick": {"h": g["home"], "a": g["away"], "d": "Draw"}[side],
            "confidence": g.get("confidence"), "p": p,
            "tier": _football_tier(g.get("confidence") or 0, g.get("celtic"), g.get("unrated")),
            "accuracy": g.get("accuracy"), "list": bool(g.get("list")), "reserve": bool(g.get("reserve")),
            "why": g.get("why"), "published": g.get("published")}


def tennis_item(m):
    if not m.get("date"): return None
    t = m.get("time")
    start = parse_utc(f"{m['date']}T{t}:00Z") if t else parse_utc(f"{m['date']}T00:00:00Z")
    if not start: return None
    pa = (m.get("p") or {}).get("a")
    return {"sport": "tennis", "key": f"t|{m.get('id') or ''}|{m['date']}|{m['playerA']}|{m['playerB']}",
            "id": m.get("id"), "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "timed": bool(t), "date": m["date"],
            "comp": f"{m.get('tour', '')} · {m.get('tournament') or ''}{' · ' + m['round'] if m.get('round') else ''}",
            "chip": m.get("tour"), "home": m["playerA"], "away": m["playerB"],
            "side": "h" if m.get("pick") == m["playerA"] else "a", "pick": m.get("pick"),
            "pHome": pa, "confidence": m.get("confidence"), "tier": m.get("tier"), "accuracy": m.get("accuracy"),
            "list": bool(m.get("list")), "reserve": bool(m.get("reserve")), "published": m.get("published")}


def sport_item(g):
    start = parse_utc(g.get("when"))
    if not start: return None
    return {"sport": g.get("sport"), "key": f"s|{g.get('id') or ''}|{g.get('home')}|{g.get('away')}",
            "id": g.get("id"), "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "timed": True,
            "date": start.date().isoformat(), "comp": g.get("label") or g.get("sport"), "chip": g.get("label"),
            "home": g.get("home"), "away": g.get("away"),
            "side": "h" if g.get("pick") == g.get("home") else "a", "pick": g.get("pick"),
            "pHome": g.get("pHome"), "confidence": g.get("confidence"), "tier": g.get("tier"),
            "accuracy": g.get("accuracy"), "list": bool(g.get("list")), "reserve": bool(g.get("reserve")),
            "published": g.get("published")}


def pinned(day, archives, now):
    """The day's list and reserve: per game, the latest price published before its start.

    archives: iterable of (kind, entry). Prices with no `published` are legacy
    and cannot be shown to predate the start, so they are skipped, as score.py
    and score_tennis.py skip them.
    """
    leagues = _leagues() if any(k == "football" for k, _ in archives) else {}
    best = {}
    for kind, g in archives:
        try:
            it = {"football": lambda: football_item(g, leagues), "tennis": lambda: tennis_item(g),
                  "sport": lambda: sport_item(g)}[kind]()
        except Exception:
            it = None
        if not it: continue
        start, pub = parse_utc(it["start"]), parse_utc(it.get("published"))
        if uk_day(start) != day or not pub or pub >= start: continue
        prev = best.get(it["key"])
        if prev is None or pub > parse_utc(prev["published"]):
            best[it["key"]] = it
    out = [it for it in best.values() if it["list"] or it["reserve"]]
    for it in out:
        it["started"] = parse_utc(it["start"]) <= now
    return out


def attach_results(items, record, trec, srec):
    fb = {}
    for d in (record or {}).get("days") or []:
        for g in d.get("games") or []:
            fb[(d["date"], g.get("league"), g.get("home"), g.get("away"))] = g
    tn, tn2 = {}, {}
    for g in (trec or {}).get("graded") or []:
        if g.get("key"): tn[str(g["key"])] = g
        tn2[(g.get("date"), g.get("playerA"), g.get("playerB"))] = g
    sp, sp2 = {}, {}
    for d in (srec or {}).get("days") or []:
        for g in d.get("games") or []:
            if g.get("id"): sp[str(g["id"])] = g
            sp2[(g.get("home"), g.get("away"), (g.get("when") or "")[:10])] = g
    for it in items:
        res = None
        if it["sport"] == "football":
            g = fb.get((it["date"], it.get("league"), it["home"], it["away"]))
            if g and g.get("result"):
                res = {"ok": bool(g.get("ok")), "void": False, "score": f"{g['result'][0]}-{g['result'][1]}"}
        elif it["sport"] == "tennis":
            g = tn.get(str(it.get("id"))) or tn2.get((it["date"], it["home"], it["away"]))
            if g:
                res = {"ok": None if g.get("void") else bool(g.get("ok")), "void": bool(g.get("void")),
                       "winner": g.get("winner"), "note": g.get("note")}
        else:
            g = sp.get(str(it.get("id"))) or sp2.get((it["home"], it["away"], it["start"][:10]))
            if g and g.get("ok") is not None:
                sc = g.get("score")
                res = {"ok": bool(g.get("ok")), "void": bool(g.get("void")),
                       "score": f"{sc[0]}-{sc[1]}" if isinstance(sc, list) and len(sc) == 2 else None,
                       "winner": g.get("winner")}
        it["result"] = res
        it["status"] = ("void" if res["void"] else "won" if res["ok"] else "lost") if res else \
                       ("started" if it["started"] else "upcoming")
    return items


SITE = "https://douglasbakeronline.github.io/footyalmanac/"


def previous_full(day, fetch=True):
    """{key: full} from the daylist the site last published for this day.

    A football row's detail (team sheets, form, links) comes from data.json,
    and data.json drops a game once it has started. Every build before the
    start carries the full object forward here, so a started pick keeps the
    same click-through as an upcoming one (6 Oct 2026)."""
    if not fetch: return {}
    import urllib.request
    try:
        with urllib.request.urlopen(SITE + "daylist.json", timeout=30) as r: d = json.load(r)
    except Exception:
        return {}
    if d.get("date") != day: return {}
    return {it["key"]: it["full"] for it in (d.get("list") or []) + (d.get("reserve") or []) if it.get("full")}


def attach_full(items, archives, data, prev):
    """Each item's full object, in the shape the page's own rows take:
    football the data.json game, tennis the tennis-data.js match, other sports
    the sports-data.js game. Archived entries already are that shape for tennis
    and the other sports; football needs data.json or the carried copy."""
    fb = {}
    for day in (data or {}).get("days") or []:
        for g in day.get("games") or []:
            try: fb[f"f|{g['league']}|{g['date']}|{g['home']['name']}|{g['away']['name']}"] = g
            except Exception: pass
    raw = {}
    for kind, g in archives:
        if kind == "tennis": raw[f"t|{g.get('id') or ''}|{g.get('date')}|{g.get('playerA')}|{g.get('playerB')}"] = g
        elif kind == "sport": raw[f"s|{g.get('id') or ''}|{g.get('home')}|{g.get('away')}"] = g
    for it in items:
        full = fb.get(it["key"]) if it["sport"] == "football" else raw.get(it["key"])
        if full is not None and it["sport"] != "football":
            full = {k: v for k, v in full.items() if k != "published"}
        it["full"] = full or prev.get(it["key"])


def read_archives(day, here=HERE):
    d0 = datetime.fromisoformat(day).date()
    names = {(d0 - timedelta(days=i)).isoformat() for i in range(LOOKBACK)}
    out = []
    for kind, folder in (("football", "predictions"), ("tennis", "predictions-tennis"), ("sport", "predictions-sports")):
        for path in sorted(glob.glob(os.path.join(here, folder, "*.json"))):
            if os.path.basename(path)[:-5] not in names: continue
            for g in _load(path, []) or []:
                out.append((kind, g))
    return out


def _load_js(path):
    try:
        t = open(path).read()
        return json.loads(t[t.index("{"):t.rindex("}") + 1])
    except Exception:
        return None


STALE_H = 12      # a feed not rebuilt for this long is a gap, not a quiet day


def coverage(day, archives, here=HERE, now=None):
    """What the day's list was chosen from (7 Oct 2026, Douglas: every day the
    list must be drawn from the whole day's data, all leagues, cups and
    friendlies, every sport). Every game priced for the UK day, per sport:
    how many, in how many competitions, how many on the list and reserve, and,
    for football, why each of the rest is off it (build.list_reason). Gaps are
    data the board did not get: a feed not rebuilt, API-Football days not
    fetched or its allowance gone."""
    now = now or datetime.now(timezone.utc)
    leagues = _leagues()
    sp_doc = _load_js(os.path.join(here, "sports-data.js")) or {}
    sp_cfg = sp_doc.get("sports") or {}
    seen = {}
    for kind, g in archives:
        try:
            it = {"football": lambda: football_item(g, leagues), "tennis": lambda: tennis_item(g),
                  "sport": lambda: sport_item(g)}[kind]()
        except Exception:
            it = None
        if not it or uk_day(parse_utc(it["start"])) != day: continue
        prev = seen.get(it["key"])
        pub, ppub = parse_utc(it.get("published")), parse_utc((prev or {}).get("published"))
        if prev is None or (pub and (not ppub or pub > ppub)):
            seen[it["key"]] = it
    out = {}
    for it in seen.values():
        k = it["sport"]
        c = out.setdefault(k, {"games": 0, "comps": set(), "list": 0, "reserve": 0, "why": {}})
        c["games"] += 1
        c["comps"].add(it.get("league") or (it.get("comp") or "").split(" · ")[1 if k == "tennis" else 0])
        c["list"] += it["list"]; c["reserve"] += it["reserve"] and not it["list"]
        if not it["list"]:
            if k == "football":
                why = it.get("why") or "older"
            elif k == "tennis":
                why = "below" if (it.get("confidence") or 0) < 0.80 else "rule"
            else:
                bar = (sp_cfg.get(k) or {}).get("listMin")
                why = "boardOnly" if bar is None else "below" if (it.get("confidence") or 0) < bar else "rule"
            c["why"][why] = c["why"].get(why, 0) + 1
    for c in out.values():
        c["comps"] = len(c["comps"])
    gaps = []
    data = _load(os.path.join(here, "data.json"), {}) or {}
    for label, doc in (("football", data), ("tennis", _load_js(os.path.join(here, "tennis-data.js"))),
                       ("other sports", sp_doc)):
        gen = parse_utc(((doc or {}).get("generated") or "") + ("" if (doc or {}).get("generated", "").endswith("Z") else "Z")) \
            if doc and doc.get("generated") else None
        if not gen:
            gaps.append(f"{label}: no board file")
        elif (now - gen).total_seconds() > STALE_H * 3600:
            gaps.append(f"{label}: board last rebuilt {gen.strftime('%d %b %H:%M')} UTC")
    af = (data.get("health") or {}).get("apiFootball") or {}
    miss = [d for d in af.get("daysMissing") or [] if d >= (datetime.fromisoformat(day).date() - timedelta(days=1)).isoformat()]
    if miss:
        gaps.append(f"football: API-Football fixtures not fetched for {', '.join(miss[:4])}"
                    + (f" and {len(miss) - 4} more days" if len(miss) > 4 else ""))
    elif af.get("spent") and not af.get("calls"):
        gaps.append("football: API-Football allowance used up; the board used the last copy it had")
    return {"sports": out, "gaps": gaps}


def build(now=None, here=HERE, fetch=True):
    now = now or datetime.now(timezone.utc)
    day = uk_day(now)
    archives = read_archives(day, here)
    items = pinned(day, archives, now)
    attach_full(items, archives, _load(os.path.join(here, "data.json"), {}), previous_full(day, fetch))
    attach_results(items, _load(os.path.join(here, "record.json"), {}),
                   _load(os.path.join(here, "tennis-record.json"), {}),
                   _load(os.path.join(here, "sports-record.json"), {}))
    strength = lambda it: (-((it.get("accuracy") or {}).get("cumHit") or (it.get("accuracy") or {}).get("hit") or 0), -(it.get("confidence") or 0))
    items.sort(key=strength)
    for it in items: it.pop("published", None)
    lst, res = [i for i in items if i["list"]], [i for i in items if i["reserve"]]
    count = lambda xs, s: sum(1 for i in xs if i["status"] == s)
    summary = {k: {"n": len(xs), "won": count(xs, "won"), "lost": count(xs, "lost"), "void": count(xs, "void"),
                   "started": count(xs, "started"), "upcoming": count(xs, "upcoming")}
               for k, xs in (("list", lst), ("reserve", res))}
    return {"date": day, "generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "summary": summary,
            "coverage": coverage(day, archives, here, now), "list": lst, "reserve": res}


def main():
    d = build()
    with open(os.path.join(HERE, "daylist.json"), "w") as f:
        json.dump(d, f, separators=(",", ":"))
    with open(os.path.join(HERE, "daylist.js"), "w") as f:
        f.write("window.__DAY_LIST__=" + json.dumps(d, separators=(",", ":")) + ";")
    s = d["summary"]
    print(f"day list {d['date']}: {s['list']['n']} list ({s['list']['won']} won, {s['list']['lost']} lost), "
          f"{s['reserve']['n']} reserve ({s['reserve']['won']} won, {s['reserve']['lost']} lost)")
    cv = d["coverage"]
    print("coverage: " + "; ".join(f"{k} {c['games']} games in {c['comps']} competitions, {c['list']} on the list"
                                   for k, c in sorted(cv["sports"].items())))
    for gap in cv["gaps"]:
        # a warning on the run page, so a thin day is seen, not just quiet
        print(f"::warning::coverage gap: {gap}")


if __name__ == "__main__":
    main()
