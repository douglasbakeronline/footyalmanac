"""The scale ladder: every way to scale a winner, every sport, tracked.

16 Nov 2026, Douglas: "can we track all of these across all sports please?"
For every graded pick at FLOOR (55%) or better, in every sport, this checks
each scale bet its final score can settle (win and over 2.5, win to nil, win
by 2+, straight sets, games handicaps, each points handicap on the ladder,
and so on) and tallies how often each one landed, by sport, confidence band
and tier (Daily List, reserve, everything else), over the whole record and
over the last RECENT_DAYS days.

A tally, never a fit (Rule 1): nothing here feeds a model, a pick or a
group. Its use is the price each bet needs at its landing rate ("needs"),
which a reader sets against William Hill's price, and the evidence for
which scale bet each sport's Scale tab should use.

What the scores cannot settle is listed as such (`UNSETTLED`): the files hold
final scores only, so half-time bets, team totals against a bookmaker's line,
corners, cards and player bets are not tracked.

Reads record-graded.json, tennis-record.json and sports-graded.json; writes
nothing itself. `scale.py` adds `build()` to scale.json as `ladder`.
Standard library only.
"""
import json
import os
import re
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR = 0.55
RECENT_DAYS = 28
BANDS = ((0.55, 0.65), (0.65, 0.75), (0.75, 0.85), (0.85, 1.01))
TIERS = ("list", "reserve", "else")

# (key, label, bookmaker's name for it). Order is the ladder, safest first.
FOOTBALL = (
    ("dc", "Win or draw", "Double chance"),
    ("win", "Win", "Match result"),
    ("w_o15", "Win and over 1.5 goals", "Result & total goals"),
    ("w_o25", "Win and over 2.5 goals", "Result & total goals"),
    ("w_o35", "Win and over 3.5 goals", "Result & total goals"),
    ("wtn", "Win to nil", "To win to nil"),
    ("by2", "Win by 2+", "Handicap -1.5"),
    ("by3", "Win by 3+", "Handicap -2.5"),
    ("t_o15", "Pick scores 2+", "Team total over 1.5"),
    ("t_o25", "Pick scores 3+", "Team total over 2.5"),
    ("wbtts", "Win and both teams score", "Result & both teams to score"),
)
TENNIS = (
    ("win", "Win", "Match winner"),
    ("fs_win", "Win the first set and the match", "First set & match"),
    ("straight", "Win in straight sets", "Set betting 2-0 / 3-0"),
    ("g35", "Win by 4+ games", "Games handicap -3.5"),
    ("g55", "Win by 6+ games", "Games handicap -5.5"),
    ("g75", "Win by 8+ games", "Games handicap -7.5"),
)
# points handicaps: the sport's ladder of "win by N or more" (handicap -(N-0.5))
MARGINS = {
    "nba": (4, 6, 8, 10, 13, 16),
    "ncaab": (4, 6, 8, 10, 13, 16),
    "wnba": (4, 6, 8, 10, 13),
    "nfl": (3, 4, 7, 8, 10, 14),
    "cfb": (3, 7, 10, 14, 17, 21),
    "rugby": (4, 8, 11, 13, 16, 21),
    "mlb": (2, 3),
}
NAMES = {"football": "Football", "tennis": "Tennis", "nba": "NBA", "ncaab": "College basketball",
         "wnba": "WNBA", "nfl": "NFL", "cfb": "College football", "rugby": "Rugby", "mlb": "Baseball"}
UNSETTLED = {
    "football": ["Win both halves", "Half-time/full-time", "Corners, cards, scorers"],
    "tennis": ["Total games against a line", "Tie-breaks, aces"],
    "nba": ["1st half and quarter bets", "Team totals against a line", "Player bets"],
    "ncaab": ["1st half bets", "Team totals against a line"],
    "nfl": ["1st half bets", "Half-time/full-time", "Player bets"],
    "cfb": ["1st half bets"],
    "rugby": ["Half-time/full-time", "Tries"],
    "mlb": ["First five innings"],
    "wnba": ["Quarter bets"],
}


def margin_bets(sport):
    return tuple([("win", "Win", "Money line")] +
                 [(f"by{n}", f"Win by {n}+", f"Handicap -{n - 0.5:g}") for n in MARGINS[sport]])


def bets_for(sport):
    return FOOTBALL if sport == "football" else TENNIS if sport == "tennis" else margin_bets(sport)


def _load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def tier_of(g):
    return "list" if g.get("list") else "reserve" if g.get("reserve") else "else"


def band_of(c):
    for lo, hi in BANDS:
        if lo <= c < hi:
            return f"{round(lo * 100)}" + ("+" if hi > 1 else f"-{round(hi * 100)}")
    return None


# ------------------------------------------------------------- per sport

def football_landed(mine, theirs):
    """{bet: True/False/None} for a football pick that scored `mine` against
    `theirs`. None is a void (draw no bet on a draw is not offered here, so
    every bet settles)."""
    won, tot = mine > theirs, mine + theirs
    return {"dc": mine >= theirs, "win": won, "w_o15": won and tot >= 2, "w_o25": won and tot >= 3,
            "w_o35": won and tot >= 4, "wtn": won and theirs == 0, "by2": mine - theirs >= 2,
            "by3": mine - theirs >= 3, "t_o15": mine >= 2, "t_o25": mine >= 3, "wbtts": won and theirs > 0}


SET = re.compile(r"\b(\d{1,2})-(\d{1,2})(?:\s*\(\d+(?:-\d+)?\))?")


def tennis_sets(row):
    """The sets of a graded tennis row as (pick's games, opponent's games),
    or None (a void, a retirement, no score). The note reads "winner bt
    loser 6-4 3-6 6-2", the winner's games first."""
    if not row or row.get("void") or row.get("retired"):
        return None
    note = str(row.get("note") or "")
    tail = note.split(" bt ", 1)[1] if " bt " in note else note
    sets = [(int(a), int(b)) for a, b in SET.findall(tail)]
    won = sum(1 for a, b in sets if a > b)
    if len(sets) < 2 or won < 2:
        return None
    return sets if row.get("ok") else [(b, a) for a, b in sets]


def tennis_landed(sets):
    mine = sum(1 for a, b in sets if a > b)
    theirs = len(sets) - mine
    won = mine > theirs
    gd = sum(a for a, b in sets) - sum(b for a, b in sets)
    return {"win": won, "fs_win": won and sets[0][0] > sets[0][1], "straight": won and theirs == 0,
            "g35": gd >= 4, "g55": gd >= 6, "g75": gd >= 8}


def margin_landed(sport, m):
    out = {"win": m > 0}
    for n in MARGINS[sport]:
        out[f"by{n}"] = m >= n
    return out


# ------------------------------------------------------------- the rows

def rows(fgraded, trec, sgraded):
    """(sport, date, confidence, tier, {bet: landed}) for every graded pick at FLOOR+."""
    for g in (fgraded or {}).get("graded") or []:
        c = g.get("confidence") or 0
        if c < FLOOR or g.get("unrated") or g.get("pick") not in ("h", "a") or not g.get("result"):
            continue
        hg, ag = g["result"]
        mine, theirs = (hg, ag) if g["pick"] == "h" else (ag, hg)
        yield "football", g.get("date") or "", c, tier_of(g), football_landed(mine, theirs)
    for g in (trec or {}).get("graded") or []:
        c = g.get("confidence") or 0
        if c < FLOOR:
            continue
        sets = tennis_sets(g)
        if sets is None:
            continue
        yield "tennis", g.get("date") or "", c, tier_of(g), tennis_landed(sets)
    for g in (sgraded or {}).get("graded") or []:
        sp, c = g.get("sport"), g.get("confidence") or 0
        if sp not in MARGINS or c < FLOOR or g.get("void") or not g.get("score"):
            continue
        h, a = g["score"]
        m = (h - a) if g.get("pick") == g.get("home") else (a - h)
        yield sp, str(g.get("when") or "")[:10], c, tier_of(g), margin_landed(sp, m)


def _cell():
    return {"n": 0, "landed": 0}


def _done(t):
    out = {"n": t["n"], "landed": t["landed"]}
    if t["n"]:
        out["rate"] = round(t["landed"] / t["n"], 4)
        if t["landed"]:
            out["needs"] = round(t["n"] / t["landed"], 2)
    return out


def build(here=HERE, today=None):
    """The ladder: for each sport, each bet's tally overall, by confidence
    band, by tier and over the last RECENT_DAYS days."""
    today = today or date.today()
    since = (today - timedelta(days=RECENT_DAYS)).isoformat()
    f = _load(os.path.join(here, "record-graded.json"), {})
    t = _load(os.path.join(here, "tennis-record.json"), {})
    s = _load(os.path.join(here, "sports-graded.json"), {})
    acc = {}
    for sport, day, c, tier, landed in rows(f, t, s):
        sp = acc.setdefault(sport, {"all": {}, "band": {}, "tier": {}, "recent": {}, "picks": 0})
        sp["picks"] += 1
        b = band_of(c)
        for bet, ok in landed.items():
            if ok is None:
                continue
            for cell in (sp["all"].setdefault(bet, _cell()),
                         sp["band"].setdefault(b, {}).setdefault(bet, _cell()),
                         sp["tier"].setdefault(tier, {}).setdefault(bet, _cell())) + \
                        ((sp["recent"].setdefault(bet, _cell()),) if day >= since else ()):
                cell["n"] += 1
                cell["landed"] += bool(ok)
    out = {"floor": FLOOR, "recentDays": RECENT_DAYS, "bands": [band_of(lo) for lo, _ in BANDS],
           "tiers": list(TIERS), "sports": {}}
    order = ("football", "tennis", "nba", "nfl", "rugby", "ncaab", "cfb", "mlb", "wnba")
    for sport in sorted(acc, key=lambda x: order.index(x) if x in order else 99):
        sp = acc[sport]
        out["sports"][sport] = {
            "name": NAMES.get(sport, sport), "picks": sp["picks"],
            "bets": [{"key": k, "label": lab, "book": bk} for k, lab, bk in bets_for(sport)],
            "all": {k: _done(v) for k, v in sp["all"].items()},
            "recent": {k: _done(v) for k, v in sp["recent"].items()},
            "band": {b: {k: _done(v) for k, v in d.items()} for b, d in sp["band"].items()},
            "tier": {tr: {k: _done(v) for k, v in d.items()} for tr, d in sp["tier"].items()},
            "unsettled": UNSETTLED.get(sport, []),
        }
    return out


if __name__ == "__main__":
    L = build()
    for sp, d in L["sports"].items():
        print(f"{d['name']} ({d['picks']} picks)")
        for b in d["bets"]:
            a, hi = d["all"].get(b["key"], {}), d["band"].get("85+", {}).get(b["key"], {})
            lst = d["tier"].get("list", {}).get(b["key"], {})
            print(f"  {b['label']:<34} all {a.get('rate', 0):.0%} of {a.get('n', 0):<5}"
                  f" 85%+ {hi.get('rate', 0):.0%} of {hi.get('n', 0):<4} list {lst.get('rate', 0):.0%} of {lst.get('n', 0)}")
