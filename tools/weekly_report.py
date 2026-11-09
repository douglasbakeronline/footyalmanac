#!/usr/bin/env python3
"""
The week's report for Douglas (9 Nov 2026: "I want a weekly report sent on
Sunday morning 8am"). Reads the record files only, fits nothing, changes
nothing. Writes weekly-report.json and weekly-report.md.

    python3 tools/weekly_report.py --out DIR [--to YYYY-MM-DD] [--extra FILE]

The period is the seven days ending on --to (default: yesterday, UK date),
so a Sunday 08:00 run reports Sunday to Saturday with every game graded.
"Shipped" runs to the report date itself, so the releases that landed since
the period ended are not lost. --extra FILE is a JSON object merged into the
report by the session that runs it (health lines, decisions waiting, the
scoreboard's open questions), since gh and the Actions API are not the
record's business. Standard library only.

Sections: the Card this week and to date (full-rule groups by first start,
one unit a group as groupings-record.json stakes them, won against expected,
return at the average and best price, legs by sport landed v quoted, Card 3x
count, empty days); the Daily List by sport (list picks landed v quoted,
reserve apart); what shipped (RELEASES.md headings dated in the window);
the week's record files' generated stamps.
"""
import json, math, os, re, sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CARD_FROM = "2026-10-25"   # the Card's first day


def load(name, default=None):
    try:
        with open(os.path.join(HERE, name), encoding="utf-8") as f: return json.load(f)
    except (OSError, ValueError):
        return default if default is not None else {}


def uk_today():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/London")).date()
    except Exception:
        return datetime.now(timezone.utc).date()


def pct(x, d=0):
    return f"{x * 100:.{d}f}%" if x is not None else "n/a"


def ret(x):
    """A return multiple as a signed percentage: 1.14 -> +14%."""
    return f"{(x - 1) * 100:+.0f}%" if x is not None else "n/a"


def card_section(rec, lo, hi):
    """Full-rule Card groups whose day falls in [lo, hi]; the record's own
    day is the Card day (07:00 UK to 07:00)."""
    groups, legs_by_sport, days_with, three = [], defaultdict(lambda: [0, 0, 0.0]), set(), 0
    all_days = set()
    for d in rec.get("days") or []:
        if not (lo <= d["date"] <= hi): continue
        all_days.add(d["date"])
        for g in d.get("groups") or []:
            if not str(g.get("name", "")).startswith("Card") or g.get("wide") or g.get("status") not in ("won", "lost"): continue
            groups.append(g); days_with.add(d["date"])
            if g["name"] == "Card 3x": three += 1
            for l in g.get("legs") or []:
                s = legs_by_sport[l.get("sport") or "?"]
                s[0] += 1; s[1] += l.get("status") == "won"; s[2] += l.get("p") or 0
    n = len(groups); won = sum(g["status"] == "won" for g in groups)
    exp = sum(g.get("p") or 0 for g in groups)
    ret = sum(g.get("paid") or g["odds"] for g in groups if g["status"] == "won")
    best = sum(g.get("paidBest") or g.get("bestOdds") or g["odds"] for g in groups if g["status"] == "won")
    var = sum((g.get("p") or 0) * (1 - (g.get("p") or 0)) for g in groups)
    out = {"from": lo, "to": hi, "groups": n, "won": won, "lost": n - won, "expected": round(exp, 2),
           "z": round((won - exp) / math.sqrt(var), 2) if var else None,
           "units": n, "returned": round(ret, 2), "returnedBest": round(best, 2),
           "return": round(ret / n, 3) if n else None, "returnBest": round(best / n, 3) if n else None,
           "card3x": three, "daysWithCard": len(days_with), "daysInRecord": len(all_days),
           "legsBySport": {s: {"legs": v[0], "landed": v[1], "quoted": round(v[2] / v[0], 3) if v[0] else None}
                           for s, v in sorted(legs_by_sport.items(), key=lambda kv: -kv[1][0])},
           "groupList": [{"date": g.get("lockAt", "")[:10], "name": g["name"], "odds": g["odds"], "p": g.get("p"), "status": g["status"],
                          "legs": [f"{l.get('pick')} ({l.get('sport')}, {l.get('odds')})" for l in g.get("legs") or []]} for g in groups]}
    return out


def list_section(lo, hi):
    """Daily List picks landed v quoted by sport, reserve apart, from the
    three records' day lists."""
    out = {}
    fb = load("record.json")
    def tally(rows, conf, ok):
        n = len(rows); w = sum(ok(r) for r in rows); q = sum(conf(r) for r in rows)
        return {"n": n, "landed": w, "rate": round(w / n, 3) if n else None, "quoted": round(q / n, 3) if n else None}
    rows = [g for d in fb.get("days") or [] if lo <= d["date"] <= hi for g in d.get("games") or [] if g.get("result") is not None]
    out["football"] = {"list": tally([g for g in rows if g.get("list")], lambda g: g["confidence"], lambda g: bool(g.get("won"))),
                       "reserve": tally([g for g in rows if g.get("reserve")], lambda g: g["confidence"], lambda g: bool(g.get("won")))}
    tn = load("tennis-record.json")
    rows = [g for d in tn.get("days") or [] if lo <= d["date"] <= hi for g in d.get("games") or [] if g.get("winner") and not g.get("void")]
    out["tennis"] = {"list": tally([g for g in rows if g.get("list")], lambda g: g["confidence"], lambda g: bool(g.get("ok"))),
                     "reserve": tally([g for g in rows if g.get("reserve")], lambda g: g["confidence"], lambda g: bool(g.get("ok")))}
    sp = load("sports-record.json")
    by = defaultdict(list)
    for d in sp.get("days") or []:
        if not (lo <= d["date"] <= hi): continue
        for g in d.get("games") or []:
            if g.get("winner"): by[g.get("sport") or "?"].append(g)
    for s, rows in sorted(by.items()):
        out[s] = {"list": tally([g for g in rows if g.get("list")], lambda g: g["confidence"], lambda g: bool(g.get("ok"))),
                  "reserve": tally([g for g in rows if g.get("reserve")], lambda g: g["confidence"], lambda g: bool(g.get("ok")))}
    return out


def shipped_section(lo, hi):
    """RELEASES.md headings dated in [lo, hi]: '## 2026-11-09 Title' or
    '## release-2026-11-09-2 (...)' forms, with the first 'What changed' line."""
    try:
        text = open(os.path.join(HERE, "RELEASES.md"), encoding="utf-8").read()
    except OSError:
        return []
    out = []
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M):
        head, body = m.group(1).strip(), m.group(2)
        dm = re.search(r"(20\d\d-\d\d-\d\d)", head)
        if not dm or not (lo <= dm.group(1) <= hi): continue
        wm = re.search(r"\*\*What changed[.:]?\*\*[.:]?\s*(.+?)(?:\n\n|\n\*\*|\Z)", body, re.S)
        what = re.sub(r"\s+", " ", wm.group(1)).strip() if wm else ""
        title = re.sub(r"^release-20\d\d-\d\d-\d\d(-\d)?\s*\(pending tag\):\s*|\s*\((?:tag )?pending(?: tag)?\)\s*$|^20\d\d-\d\d-\d\d\s+", "", head).strip()
        title = re.sub(r"^\((?:tag )?pending(?: tag)?\):\s*", "", title)
        out.append({"date": dm.group(1), "title": title[:1].upper() + title[1:], "what": what[:400]})
    return sorted(out, key=lambda x: x["date"], reverse=True)   # newest first, whichever heading style


def build(to=None, extra=None):
    today = uk_today()
    to_d = date.fromisoformat(to) if to else today - timedelta(days=1)
    lo, hi = (to_d - timedelta(days=6)).isoformat(), to_d.isoformat()
    rec = load("groupings-record.json")
    report = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "reportDate": today.isoformat(),
              "period": {"from": lo, "to": hi},
              "card": {"week": card_section(rec, lo, hi), "toDate": card_section(rec, CARD_FROM, hi), "recordBlock": rec.get("card"),
                       "graded": rec.get("graded")},
              "list": list_section(lo, hi),
              "shipped": shipped_section(lo, today.isoformat()),
              "stamps": {"record.json": load("record.json").get("generated"), "tennis-record.json": load("tennis-record.json").get("generated"),
                         "sports-record.json": load("sports-record.json").get("generated"), "groupings-record.json": rec.get("graded")}}
    if extra: report.update(extra)
    return report


def markdown(r):
    p = r["period"]; w = r["card"]["week"]; t = r["card"]["toDate"]
    L = [f"# Sports Almanac, week {p['from']} to {p['to']}", ""]
    L += ["## The Card", ""]
    if w["groups"]:
        L.append(f"{w['groups']} groups settled, {w['won']} won against {w['expected']} expected (z {w['z']}), "
                 f"{w['returned']} back on {w['units']} units ({ret(w['return'])}; at best prices {ret(w['returnBest'])}). "
                 f"Card 3x built: {w['card3x']}. Days with a Card: {w['daysWithCard']} of {w['daysInRecord']}.")
        L.append("")
        L.append("| sport | legs | landed | quoted |"); L.append("|---|---|---|---|")
        for s, v in w["legsBySport"].items():
            L.append(f"| {s} | {v['legs']} | {v['landed']} ({pct(v['landed'] / v['legs'])}) | {pct(v['quoted'])} |")
        L.append("")
        for g in w["groupList"]:
            L.append(f"- {g['date']} {g['name']} at {g['odds']}: {g['status']}. " + "; ".join(g["legs"]))
    else:
        L.append("No Card group settled this week.")
    L += ["", f"Since {t['from']}: {t['groups']} groups, {t['won']} won against {t['expected']} expected (z {t['z']}), "
              f"return {ret(t['return'])} at the average price, {ret(t['returnBest'])} at best.", ""]
    L += ["## The Daily List", "", "| sport | list picks | landed | quoted | reserve |", "|---|---|---|---|---|"]
    for s, v in r["list"].items():
        li, re_ = v["list"], v["reserve"]
        L.append(f"| {s} | {li['n']} | {li['landed']} ({pct(li['rate'])}) | {pct(li['quoted'])} | {re_['landed']}/{re_['n']} ({pct(re_['rate'])}) |")
    L += ["", "## Shipped", ""]
    for s in r["shipped"]:
        L.append(f"- {s['date']} {s['title']}" + (f": {s['what']}" if s["what"] else ""))
    if not r["shipped"]: L.append("Nothing released.")
    for key, title in (("health", "Health"), ("decisions", "Decisions waiting on Douglas"), ("next", "Next week")):
        if r.get(key):
            L += ["", f"## {title}", ""] + [f"- {x}" for x in r[key]]
    return "\n".join(L) + "\n"


def main():
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else HERE
    to = sys.argv[sys.argv.index("--to") + 1] if "--to" in sys.argv else None
    extra = json.load(open(sys.argv[sys.argv.index("--extra") + 1])) if "--extra" in sys.argv else None
    r = build(to, extra)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "weekly-report.json"), "w", encoding="utf-8") as f: json.dump(r, f, indent=1, ensure_ascii=False)
    md = markdown(r)
    with open(os.path.join(out, "weekly-report.md"), "w", encoding="utf-8") as f: f.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
