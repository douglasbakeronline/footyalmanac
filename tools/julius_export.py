#!/usr/bin/env python3
"""Export every graded prediction for outside review (Julius AI, 8 Oct 2026).

    python3 tools/julius_export.py                 writes julius/julius.ai.review.<today>/ and its .zip
    python3 tools/julius_export.py --date 2026-10-08

Reads only what the site's own graders wrote, so nothing is regraded here:
  football      record-graded.json (score.py, every graded fixture)
  tennis        tennis-record.json "graded" (score_tennis.py)
  other sports  sports.graded_games() over predictions-sports/ and history-sports/

Run it after the daily build has committed record-graded.json: a local
score.py run lacks the paid API-Football results and grades about half the
football that CI does. Standard library only.
"""
import argparse, csv, glob, json, os, sys, zipfile
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine as E
import sports as SP

COLUMNS = [
    "date", "start_utc", "published_utc", "sport", "competition", "home", "away",
    "pick", "pick_side", "confidence", "confidence_pct", "tier", "tested_rate",
    "group", "on_daily_list", "on_reserve", "result", "mark", "correct", "top_pick_correct", "quoted_chance",
    "winner", "final_score", "predicted_score", "draw_read", "verification", "flags", "note",
]
MARK = {"won": "✓", "lost": "✗", "void": "–"}
GROUPS = {"list": "Daily List", "reserve": "Reserve", "board": "Board"}


def _group(r):
    return "list" if r.get("list") else ("reserve" if r.get("reserve") else "board")


def _rate(acc):
    if not isinstance(acc, dict):
        return ""
    v = acc.get("cumHit") or acc.get("hit")
    return round(v, 4) if v else ""


def _row(**kw):
    out = {c: kw.get(c, "") for c in COLUMNS}
    res = out["result"]
    out["mark"] = MARK.get(res, "")
    out["correct"] = {"won": 1, "lost": 0}.get(res, "")
    if out["top_pick_correct"] == "":
        out["top_pick_correct"] = out["correct"]
    if out["quoted_chance"] == "" and out["confidence"] != "" and res in ("won", "lost"):
        out["quoted_chance"] = round(out["confidence"], 4)
    g = out["group"]
    out["on_daily_list"] = int(g == "list")
    out["on_reserve"] = int(g == "reserve")
    out["group"] = GROUPS[g]
    c = out["confidence"]
    if c != "":
        out["confidence"] = round(c, 4)
        out["confidence_pct"] = round(c * 100, 1)
    return out


def football():
    path = os.path.join(ROOT, "record-graded.json")
    if not os.path.exists(path):
        sys.exit("record-graded.json is missing: it is written by score.py in the daily build")
    with open(path) as f:
        doc = json.load(f)
    out = []
    side = {"h": "home", "d": "draw", "a": "away"}
    for r in doc["graded"]:
        name = lambda k: r["home"] if k == "h" else r["away"] if k == "a" else "Draw"
        flags = [f for f, on in (("celtic", r.get("celtic")), ("unrated", r.get("unrated"))) if on]
        ps = r.get("score") or [-1, -1]
        out.append(_row(
            date=r["date"], start_utc=r.get("kickoff") or "", published_utc=r.get("published") or "",
            sport="Football", competition=E.LEAGUES.get(r["league"], {}).get("name", r["league"]),
            home=r["home"], away=r["away"], pick=name(r["pick"]), pick_side=side[r["pick"]],
            confidence=r["confidence"], tier=r.get("tier", ""), tested_rate=_rate(r.get("accuracy")),
            group=_group(r), result="won" if r["ok"] else "lost", winner=name(r["actual"]),
            final_score=f"{r['result'][0]}-{r['result'][1]}",
            predicted_score=f"{ps[0]}-{ps[1]}" if ps[0] >= 0 else "",
            draw_read=int(bool(r.get("drawRead"))), verification=r.get("verified", ""),
            top_pick_correct=int(r["pick"] == r["actual"]),
            quoted_chance=r.get("expected", round(r["confidence"], 4)),
            flags=" ".join(flags)))
    return out, doc.get("generated")


def tennis_rates():
    """{(archive key, published): tested rate} from predictions-tennis/."""
    rates = {}
    for path in glob.glob(os.path.join(ROOT, "predictions-tennis", "*.json")):
        with open(path) as f:
            for m in json.load(f):
                key = m.get("id") or f"{m['tour']}|{m['date']}|{m['playerA']}|{m['playerB']}"
                rates[(key, m.get("published"))] = _rate(m.get("accuracy"))
    return rates


def tennis():
    with open(os.path.join(ROOT, "tennis-record.json")) as f:
        doc = json.load(f)
    rates = tennis_rates()
    out = []
    for g in doc.get("graded", []):
        comp = " · ".join(x for x in (g.get("tour"), g.get("tournament"), g.get("round")) if x)
        common = dict(date=g["date"], published_utc=g.get("published") or "", sport="Tennis",
                      competition=comp, home=g["playerA"], away=g["playerB"], note=g.get("note") or "",
                      verification="published before the start")
        if g.get("void"):
            out.append(_row(**common, group="board", result="void"))
            continue
        out.append(_row(**common, pick=g["pick"], pick_side="A" if g["pick"] == g["playerA"] else "B",
                        confidence=g["confidence"], tier=g.get("tier", ""), group=_group(g),
                        tested_rate=rates.get((g["key"], g.get("published")), ""),
                        result="won" if g["ok"] else "lost", winner=g.get("winner") or "",
                        flags="retired" if g.get("retired") else ""))
    return out, doc.get("generated")


def other_sports():
    graded, voids = SP.graded_games()
    out = []
    for r, void in [(r, False) for r in graded] + [(r, True) for r in voids]:
        sc = r.get("score") or ["", ""]
        out.append(_row(
            date=r["when"][:10], start_utc=r["when"], published_utc=r.get("published") or "",
            sport=SP.SPORTS.get(r["sport"], {}).get("name", r["sport"]), competition=r.get("label", ""),
            home=r["home"], away=r["away"], pick=r["pick"],
            pick_side="home" if r["pick"] == r["home"] else "away",
            confidence=r["confidence"], tier=r.get("tier", ""), tested_rate=_rate(r.get("accuracy")),
            group=_group(r), result="void" if void else ("won" if r["ok"] else "lost"),
            winner="" if void else r.get("winner", ""), final_score=f"{sc[0]}-{sc[1]}",
            verification="published before the start", note="tie: void" if void else ""))
    return out


def tally(rows):
    won = sum(1 for r in rows if r["result"] == "won")
    lost = sum(1 for r in rows if r["result"] == "lost")
    void = sum(1 for r in rows if r["result"] == "void")
    graded = [r for r in rows if r["result"] in ("won", "lost")]
    quoted = sum(r["quoted_chance"] for r in graded) / len(graded) if graded else None
    hit = won / (won + lost) if won + lost else None
    return {"picks": len(rows), "won": won, "lost": lost, "void": void,
            "hit_rate": round(hit, 4) if hit is not None else "",
            "mean_quoted": round(quoted, 4) if quoted is not None else "",
            "hit_minus_quoted": round(hit - quoted, 4) if hit is not None and quoted is not None else ""}


def write_csv(path, rows, columns):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


README = """# Sports Almanac: graded predictions for review ({day})

Every prediction the site published and has since graded, across every
sport, exported on {day} by `tools/julius_export.py` from the site's own
grading files. Nothing is regraded or filtered beyond what the site grades.
Site: https://douglasbakeronline.github.io/footyalmanac/

## Files

| File | What |
|---|---|
| `all_picks.csv` | every graded pick, all sports, one row each ({n_all} rows) |
| `daily_list.csv` | picks flagged for the Daily List ({n_list}) |
| `reserve.csv` | picks flagged for the reserve ({n_res}) |
| `by_sport/<sport>.csv` | the same rows split by sport |
| `summary.csv` | picks, won, lost, void, hit rate and mean `quoted_chance` by group and sport |
| `by_day.csv` | the same tallies per day, group and sport |
| `calibration_bands.csv` | hit rate against mean `quoted_chance`, in 5-point bands of `confidence`, by sport |

## Columns (`all_picks.csv` and the files split from it)

| Column | Meaning |
|---|---|
| `date` | the event's date as archived (football: fixture date; others: UTC date of the start) |
| `start_utc` | scheduled start, UTC, where recorded (blank for tennis and older football rows) |
| `published_utc` | when the graded price was published, UTC (blank for football rows archived before 2 Oct 2026) |
| `sport`, `competition` | sport, and league / tournament and round |
| `home`, `away` | the two sides (tennis: player A, player B) |
| `pick`, `pick_side` | the side the model favoured (football can be Draw, rarely) |
| `confidence`, `confidence_pct` | the model's probability for its pick, at publication (0-1 and %) |
| `tier` | Strong 70%+, Firm 62%+, Lean 55%+, No read below (football demotes Celtic's Law rows one tier) |
| `tested_rate` | how often calls at this level landed in out-of-sample testing, as shown on the site (tennis and the other sports; football's archive does not record it) |
| `group` | Daily List, Reserve or Board (graded but on neither list) |
| `on_daily_list`, `on_reserve` | 1/0 flags for the same |
| `result` | won, lost or void |
| `mark` | ✓ won, ✗ lost, – void, as on the site's "How it went" pages |
| `correct` | 1 won, 0 lost, blank void (the site's rule; football counts draw readings) |
| `top_pick_correct` | 1 if the top pick itself landed (football: draw readings count 0 here) |
| `quoted_chance` | the model's own chance of `correct`: the pick's probability, plus the draw chance for football rows whose predicted scoreline is a draw. Compare hit rates with this, not `confidence` |
| `winner`, `final_score` | who won (football: team or Draw) and the score |
| `predicted_score` | football only: the model's likeliest scoreline |
| `draw_read` | football only: 1 if counted right because the predicted scoreline was a draw and the game was drawn |
| `verification` | football: `verified` (published before a known kick-off), `verified-by-date`, `legacy-unverified` (archived before publish times were recorded, 2 Oct 2026); others: only prices published before the start are graded |
| `flags` | football `celtic` (a fixture the model is structurally blind to), `unrated`; tennis `retired` |
| `note` | tennis result line, or why a pick is void |

## How grading works

- Only a price published before the start is graded; a later price proves nothing and is left out.
  Where a game was priced several times, the latest pre-start price is graded.
- Football is home / draw / away. A pick is right if the top pick landed, or if the predicted
  scoreline was a draw and the game was drawn (`draw_read`; the site's rule since 6 Oct 2026).
  The top-pick-only hit rate is `correct` with `draw_read` rows counted as misses.
- Tennis: walkovers and abandoned matches are void. The other sports: a tie is void.
- The **Daily List** is picks whose level landed at least the bar in testing (80% for most
  football and sports; 75% for tennis from 8 Oct and the wider API-Football leagues), with
  blind spots, draws and tennis qualifying left out. The **Reserve** is clean picks under the bar,
  Firm (62%) or better. Each group is graded on its own; the reserve never counts in the list.
- Groups are the flags set when the price was published. Until 8 Oct 2026 the site's front page
  showed at most 20 picks a day, so on a busy day some list-flagged picks were graded but not shown.

## Things to know before reading the numbers

- Football rows before 2 Oct 2026 carry no publish time (`legacy-unverified`); they were archived
  by the daily build before kick-off, but that cannot be proved from the file.
- Tennis ratings missed results between 2 June and 8 Oct 2026 (fixed 8 Oct); tennis prices
  before then were made on stale ratings.
- The Daily List bar and the reserve began on 27-30 Sep 2026, and the tennis bar moved from 80%
  to 75% on 8 Oct; early days are thin.
- No bookmaker prices are in any model or in this export.

Source files as of: football {f_gen}, tennis {t_gen}.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--out", default=os.path.join(ROOT, "julius"))
    args = ap.parse_args()

    fb, f_gen = football()
    tn, t_gen = tennis()
    rows = fb + tn + other_sports()
    rows.sort(key=lambda r: (r["date"], r["sport"], -(r["confidence"] or 0) if r["confidence"] != "" else 0))

    name = f"julius.ai.review.{args.date}"
    base = os.path.join(args.out, name)
    write_csv(os.path.join(base, "all_picks.csv"), rows, COLUMNS)
    lst = [r for r in rows if r["group"] == "Daily List"]
    res = [r for r in rows if r["group"] == "Reserve"]
    write_csv(os.path.join(base, "daily_list.csv"), lst, COLUMNS)
    write_csv(os.path.join(base, "reserve.csv"), res, COLUMNS)
    by_sport = defaultdict(list)
    for r in rows:
        by_sport[r["sport"]].append(r)
    for sport, rs in by_sport.items():
        write_csv(os.path.join(base, "by_sport", f"{slug(sport)}.csv"), rs, COLUMNS)

    tcols = ["picks", "won", "lost", "void", "hit_rate", "mean_quoted", "hit_minus_quoted"]
    summary = []
    for grp in ("All", "Daily List", "Reserve", "Board"):
        gr = rows if grp == "All" else [r for r in rows if r["group"] == grp]
        for sport in ["All sports"] + sorted(by_sport):
            sr = gr if sport == "All sports" else [r for r in gr if r["sport"] == sport]
            if sr:
                summary.append({"group": grp, "sport": sport, **tally(sr)})
    write_csv(os.path.join(base, "summary.csv"), summary, ["group", "sport"] + tcols)

    days = defaultdict(list)
    for r in rows:
        days[(r["date"], r["group"], r["sport"])].append(r)
    by_day = [{"date": d, "group": g, "sport": s, **tally(rs)} for (d, g, s), rs in sorted(days.items())]
    write_csv(os.path.join(base, "by_day.csv"), by_day, ["date", "group", "sport"] + tcols)

    bands = []
    for sport in ["All sports"] + sorted(by_sport):
        sr = [r for r in rows if r["result"] in ("won", "lost") and (sport == "All sports" or r["sport"] == sport)]
        for lo in range(30, 100, 5):
            b = [r for r in sr if lo <= r["confidence_pct"] < lo + 5]
            if b:
                t = tally(b)
                bands.append({"sport": sport, "band": f"{lo}-{lo + 5}%", "picks": t["won"] + t["lost"],
                              "hit_rate": t["hit_rate"], "mean_quoted": t["mean_quoted"],
                              "hit_minus_quoted": t["hit_minus_quoted"]})
    write_csv(os.path.join(base, "calibration_bands.csv"), bands,
              ["sport", "band", "picks", "hit_rate", "mean_quoted", "hit_minus_quoted"])

    with open(os.path.join(base, "README.md"), "w", encoding="utf-8") as f:
        f.write(README.format(day=args.date, n_all=len(rows), n_list=len(lst), n_res=len(res),
                              f_gen=f_gen, t_gen=t_gen))

    zpath = base + ".zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(base):
            for fn in sorted(files):
                full = os.path.join(dirpath, fn)
                z.write(full, os.path.join(name, os.path.relpath(full, base)))

    a = tally(rows)
    print(f"{name}: {len(rows)} graded picks ({a['won']} won, {a['lost']} lost, {a['void']} void); "
          f"Daily List {len(lst)}, reserve {len(res)}; sports: "
          + ", ".join(f"{s} {len(v)}" for s, v in sorted(by_sport.items())), file=sys.stderr)


if __name__ == "__main__":
    main()
