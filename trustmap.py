"""Where to trust the model (10 Nov 2026): every graded pick, every sport,
by family and confidence band, landed against quoted.

A read of the scoreboard, never a fit (Rule 1): the grid only counts what
was published before the start and graded since. The page shows it in How it
went so a reader can see which sports and confidence levels have earned
trust and which have not. Strict win test: a football pick lands only if the
picked result happened (a draw read as a draw).

Reads record-graded.json (football), tennis-record.json "graded" and
sports.graded_games(); any that fails to load is left out, never guessed.
Standard library only.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [(0.55, 0.65), (0.65, 0.75), (0.75, 0.85), (0.85, 0.95), (0.95, 1.0001)]
MIN_SHOW = 10          # a cell with fewer graded picks is shown faint, not read
Z = 1.645              # 90%: the page calls a cell above or under quote past this


def _load(name):
    try:
        with open(os.path.join(HERE, name)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _family_football(code):
    """Core leagues (engine.LEAGUES, not af.*), the wider API-Football
    leagues, and cups with internationals: the three families the site already
    treats apart (bands, list bar, the Card)."""
    code = str(code or "")
    if code.startswith("af."): return "football-wider"
    try:
        import engine as E
        m = E.LEAGUES.get(code) or {}
    except Exception:
        m = {}
    if m.get("cup") or m.get("international") or not m: return "football-cups"
    return "football"


def rows():
    """(family, confidence, landed) for every graded pick at 55%+."""
    out = []
    for g in _load("record-graded.json").get("graded") or []:
        c = g.get("confidence")
        if c is None or c < BANDS[0][0] or not g.get("result") or not g.get("pick"): continue
        out.append((_family_football(g.get("league")), c, g.get("pick") == g.get("actual")))
    for g in _load("tennis-record.json").get("graded") or []:
        c = g.get("confidence")
        if c is None or c < BANDS[0][0] or g.get("void") or g.get("ok") is None: continue
        out.append((f"tennis-{str(g.get('tour') or '').lower()}", c, bool(g.get("ok"))))
    try:
        import sports
        graded, _ = sports.graded_games()
    except Exception:
        graded = []
    for g in graded:
        c = g.get("confidence")
        if c is None or c < BANDS[0][0] or g.get("ok") is None: continue
        out.append((str(g.get("sport")), c, bool(g.get("ok"))))
    return out


def grid(rs=None):
    rs = rows() if rs is None else rs
    cells = {}
    for fam, c, ok in rs:
        b = next((i for i, (lo, hi) in enumerate(BANDS) if lo <= c < hi), None)
        if b is None: continue
        for key in ((fam, b), (fam, "all")):
            t = cells.setdefault(key, [0, 0, 0.0, 0.0])
            t[0] += 1; t[1] += ok; t[2] += c; t[3] += c * (1 - c)
    fams = {}
    for (fam, b), (n, won, q, v) in cells.items():
        z = round((won - q) / math.sqrt(v), 2) if v > 0 else None
        fams.setdefault(fam, {})[str(b)] = {"n": n, "won": won, "quoted": round(q / n, 4), "z": z}
    order = sorted(fams, key=lambda f: -fams[f]["all"]["n"])
    return {"bands": [[lo, min(hi, 1.0)] for lo, hi in BANDS], "minShow": MIN_SHOW, "z": Z,
            "families": [{"key": f, **{"cells": fams[f]}} for f in order]}


if __name__ == "__main__":
    g = grid()
    for f in g["families"]:
        a = f["cells"]["all"]
        print(f"{f['key']:16} {a['n']:6} landed {a['won'] / a['n']:.1%} v {a['quoted']:.1%}  z {a['z']}")
