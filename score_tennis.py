#!/usr/bin/env python3
"""
Grade every archived tennis prediction against who actually won.

    python3 score_tennis.py              grade, write tennis-record.json and tennis-record.js

The tennis twin of score.py, and kept apart from it: football never reads
anything this writes.

What counts
-----------
A prediction is graded only if it was published before the match started.
build_tennis.py stamps every archived price with its publish time; a match
whose scheduled start is earlier than that is skipped, not graded, because a
number published mid-match proves nothing. A match with no start time is
held to the start of its day.

Walkovers and cancellations are void: no ball was struck, so there is nothing
to be right or wrong about. A retirement is graded (the result stands) and
marked "ret." on the board.

Results come from the same ESPN tennis scoreboard build_tennis.py prices off.
A new prediction is matched to its result by ESPN's match id. Older ones,
archived before the id was kept, are matched on the two players (rating-pool
names, via build_tennis.match_player) within two days of the scheduled date,
and only when exactly one match fits. A wrong result is worse than none.

Graded matches are kept in tennis-record.json and never re-fetched, so a day
ESPN is unreachable costs nothing but that day's new grades.

Standard library only.
"""
import json, math, os, sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_tennis as B

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = os.path.join(HERE, "tennis-record.json")
RECORD_JS = os.path.join(HERE, "tennis-record.js")
REVIEW_DAYS = 14
LOOKBACK_DAYS = 21     # how far back an ungraded prediction is still chased
EPS = 1e-12


def kickoff(m):
    return f"{m['date']}T{m.get('time') or '00:00'}:00Z"


def load_predictions():
    """{key: prediction}, the latest price published before the match began."""
    best = {}
    skipped = 0
    for name in sorted(os.listdir(B.PRED_DIR)) if os.path.isdir(B.PRED_DIR) else []:
        if not name.endswith(".json"):
            continue
        try:
            rows = json.load(open(os.path.join(B.PRED_DIR, name)))
        except Exception as e:
            print(f"  skipping {name}: {e}", file=sys.stderr)
            continue
        for m in rows:
            if not m.get("published") or m["published"] >= kickoff(m):
                skipped += 1
                continue
            k = B.pred_key(m)
            if k not in best or m["published"] > best[k]["published"]:
                best[k] = m
    return best, skipped


def fetch_results(days, ratings):
    """Every finished singles match ESPN returns for these dates, keyed by
    match id and by (tour, frozenset of rating-pool names)."""
    by_id, by_pair = {}, defaultdict(list)
    for tour in ("atp", "wta"):
        by_full, by_initial = B.build_index(ratings[tour]["ratings"])
        seen = set()
        for day in sorted(days):
            errs = []
            for slug in B.TOUR_SLUGS[tour]:
                for ev in B._get_day(slug, day, 25, errs):
                    for r in B._matches_from_event(ev, tour):
                        if r["state"] != "post" or (r["id"], r["date"]) in seen:
                            continue
                        seen.add((r["id"], r["date"]))
                        a = B.match_player(r["p0"], by_full, by_initial)
                        b = B.match_player(r["p1"], by_full, by_initial)
                        r["pool"] = {r["p0"]: a, r["p1"]: b}
                        if r["id"]:
                            by_id[r["id"]] = r
                        if a and b:
                            by_pair[(tour.upper(), frozenset((a, b)))].append(r)
            if errs and len(errs) >= len(B.ESPN_HOSTS):
                print(f"  espn {errs[0]}", file=sys.stderr)
    return by_id, by_pair


def find_result(m, by_id, by_pair):
    if m.get("id") and m["id"] in by_id:
        return by_id[m["id"]]
    d0 = date.fromisoformat(m["date"])
    cands = [r for r in by_pair.get((m["tour"], frozenset((m["playerA"], m["playerB"]))), [])
             if abs((date.fromisoformat(r["date"]) - d0).days) <= 2]
    return cands[0] if len(cands) == 1 else None


def outcome(m, r):
    """(status, winner as a rating-pool name). status: graded, void or None."""
    note = (r.get("note") or "").lower()
    if r.get("statusName") == "STATUS_CANCELED" or "w/o" in note or "walkover" in note:
        return "void", None
    if not r.get("winner"):
        return None, None
    return "graded", r["pool"].get(r["winner"]) or r["winner"]


def summarise(rows):
    if not rows:
        return None
    n = len(rows)
    hit = sum(r["ok"] for r in rows)
    ll = -sum(math.log(max(r["confidence"] if r["ok"] else 1 - r["confidence"], EPS))
              for r in rows) / n
    return {"n": n, "correct": hit, "accuracy": round(hit / n, 4),
            "expected": round(sum(r["confidence"] for r in rows) / n, 4),
            "logLoss": round(ll, 4)}


def tier_table(rows):
    out = []
    for lo, name in B.TIERS:
        g = [r for r in rows if r["tier"] == name]
        if g:
            out.append({"name": name, "min": lo, **summarise(g)})
    return out


def main():
    ratings = json.load(open(os.path.join(HERE, "tennis.json")))
    preds, late = load_predictions()
    try:
        old = json.load(open(RECORD)).get("graded", [])
    except Exception:
        old = []
    graded = {g["key"]: g for g in old}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff = (date.today() - timedelta(days=LOOKBACK_DAYS)).isoformat()
    pending = {k: m for k, m in preds.items()
               if k not in graded and kickoff(m) < now and m["date"] >= cutoff}

    if pending:
        days = set()
        for m in pending.values():
            d = date.fromisoformat(m["date"])
            days.update({d - timedelta(days=1), d, min(d + timedelta(days=1), date.today())})
        by_id, by_pair = fetch_results(days, ratings)
        new = void = 0
        for k, m in pending.items():
            r = find_result(m, by_id, by_pair)
            if not r:
                continue
            status, winner = outcome(m, r)
            rid = r.get("id") or f"{m['tour']}|{r['date']}|{r['p0']}|{r['p1']}"
            if status == "void":
                graded[k] = {"key": k, "result": rid, "published": m["published"],
                             "void": True, "date": m["date"], "tour": m["tour"],
                             "playerA": m["playerA"], "playerB": m["playerB"],
                             "note": r.get("note")}
                void += 1
            elif status == "graded":
                conf = m["confidence"]
                graded[k] = {
                    "key": k, "result": rid, "void": False, "date": m["date"], "tour": m["tour"],
                    "tournament": m.get("tournament"), "round": m.get("round"),
                    "playerA": m["playerA"], "playerB": m["playerB"],
                    "pick": m["pick"], "confidence": conf, "tier": B.tier_of(conf),
                    "list": bool(m.get("list")),
                    "winner": winner, "ok": winner == m["pick"],
                    "retired": "ret" in (r.get("note") or "").lower(),
                    "note": r.get("note"), "published": m["published"],
                }
                new += 1
        print(f"  {new} newly graded, {void} void, "
              f"{len(pending) - new - void} still waiting on a result", file=sys.stderr)

    # A rescheduled match was priced under each date it was listed for, so two
    # archived predictions can resolve to one result. The match is graded
    # once, on the latest price published before it started.
    latest = {}
    for g in graded.values():
        rid = g.get("result") or g["key"]
        if rid not in latest or g.get("published", "") > latest[rid].get("published", ""):
            latest[rid] = g
    graded = {g["key"]: g for g in latest.values()}
    rows = [g for g in graded.values() if not g["void"]]
    by_date = defaultdict(list)
    for r in rows:
        by_date[r["date"]].append(r)
    days = [{"date": d, **summarise(by_date[d]), "tiers": tier_table(by_date[d]),
             "games": sorted(by_date[d], key=lambda r: -r["confidence"])}
            for d in sorted(by_date, reverse=True)[:REVIEW_DAYS]]

    bands = []
    for lo, hi in [(0.5, 0.55), (0.55, 0.62), (0.62, 0.70), (0.70, 1.01)]:
        g = [r for r in rows if lo <= r["confidence"] < hi]
        if g:
            bands.append({"from": lo, "to": min(hi, 1.0), **summarise(g)})

    payload = {
        "generated": now,
        "archived": len(preds), "publishedLate": late,
        "overall": summarise(rows),
        "byTour": {t: summarise([r for r in rows if r["tour"] == t]) for t in ("ATP", "WTA")},
        "tiers": tier_table(rows),
        # the Daily List's tennis picks on their own, from the day it launched
        "list": summarise([r for r in rows if r.get("list")]),
        "bands": bands,
        "void": sum(1 for g in graded.values() if g["void"]),
        "days": days,
        "graded": list(graded.values()),
    }
    json.dump(payload, open(RECORD, "w"), separators=(",", ":"))
    # The page reads a script, not the JSON: dashboard.html opens off disk,
    # where fetch() is blocked. Same reason build.py writes data.js.
    view = {k: v for k, v in payload.items() if k != "graded"}
    with open(RECORD_JS, "w") as f:
        f.write("window.__TENNIS_RECORD__=" + json.dumps(view, separators=(",", ":")) + ";")

    o = payload["overall"]
    if o:
        print(f"tennis: graded {o['n']} matches, {o['accuracy']:.1%} picked the winner "
              f"(quoted {o['expected']:.1%}), {payload['void']} void, "
              f"{late} archived prices published after the start were not graded",
              file=sys.stderr)
    else:
        print("tennis: nothing graded yet", file=sys.stderr)


if __name__ == "__main__":
    main()
