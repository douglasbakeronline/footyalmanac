"""The model's record on every team (28 Nov 2026, Douglas: "every team in
sports fixtures has an accuracy rating of how the model performed for them in
every fixture they've played").

For each club, side or player: the graded fixtures it played in, how many the
model called right (strict: the picked result happened), how many it expected
to (the sum of its quoted chances), the split by which side it backed, and the
last ten in order. A tally of the scoreboard, never a fit (Rule 1), and no
model reads it. Display only: the page shows it in an open row.

Reads record-graded.json (football), tennis-record.json "graded" and
sports-graded.json; any that fails to load is left out, never guessed. Writes
team-record.js for the page (gitignored, rebuilt on every deploy).

Who is one team (Rule 6: a wrong match is worse than a missed one):

- Football names are compared in `sources._norm` form inside a scope: a
  country's men's game, its women's game, senior internationals, or one
  competition alone (youth leagues, women's and youth internationals).
- Two spellings in one league are one club only when `score._same_club` joins
  them, the archive never shows them apart (`score.distinct_names`) and they
  never play different opponents within `NEAR_DAYS` (Southend / Southend
  United join; Independiente and Independiente Rivadavia do not).
- A name in two leagues of a country is one club (a league under two codes,
  a state and a national league) unless the two play different opponents
  within `NEAR_DAYS` (FC Andorra in LaLiga 2 and Andorra CF in the Tercera).
- A cup tie joins the club's league record only when exactly one club in the
  country carries the name, or exactly one is written that very way; a
  continental tie the same across every country. Otherwise the cup rows
  stand alone.
- A match graded under two league codes is counted once.

Standard library only.
"""
import glob, json, math, os, re, sys
from collections import defaultdict
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
RULE = 1
MIN_READ = 10        # fewer graded fixtures than this: the page gives the count, no verdict
LAST = 10            # the run of recent calls kept, oldest first
NEAR_DAYS = 2        # two spellings playing different opponents this close are two clubs
BOARD_FILES = 3      # football archive days read for the names now on the page
OUT = "team-record.js"

YOUTH = re.compile(r"\bu ?\d\d\b|junior|primavera|youth|reserve|premier league 2", re.I)
WOMEN_CODE = re.compile(r"\.w(\d|\.|$)")
CONTINENTS = {"eur", "sam", "ccf", "fifa"}


def _load(name):
    try:
        with open(os.path.join(HERE, name)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _leagues():
    try:
        import engine as E
        return E.LEAGUES
    except Exception:
        return {}


def scope_of(code, leagues=None):
    """(kind, scope) of a football competition: which names it may share a
    club with. kind: "dom" (a country's leagues), "cup" (its cups), "cont"
    (continental club ties), "int" (senior internationals), "solo" (its own
    names only)."""
    L = _leagues() if leagues is None else leagues
    m = L.get(code) or {}
    name = str(m.get("name") or "")
    women = bool(m.get("women")) or code == "uwcl" or bool(WOMEN_CODE.search(code)) or "women" in name.lower()
    youth = bool(m.get("u21")) or bool(YOUTH.search(name)) or bool(re.search(r"(^|\.)u\d\d(\.|$)", code))
    if not m:
        return "solo", code
    if m.get("international"):
        return ("solo", code) if (women or youth or code == "asiangames") else ("int", "int")
    if youth:
        return "solo", code
    iso = m.get("iso")
    if not iso or iso in CONTINENTS:
        return "cont", "cont-w" if women else "cont"
    return ("cup" if m.get("cup") else "dom"), iso + ("-w" if women else "")


def _day(s):
    return date.fromisoformat(str(s)[:10])


class Clubs:
    """Resolves (competition code, name as written) to one identity."""

    def __init__(self, fixtures, leagues=None, norm=None, same=None, apart=None):
        """fixtures: (code, date, home, away) for every graded and listed
        football fixture. norm / same / apart default to the build's own
        matcher (sources._norm, score._same_club, score.distinct_names)."""
        self.L = _leagues() if leagues is None else leagues
        if norm is None or same is None:
            import sources as S, score
            norm = norm or S._norm
            same = same or score._same_club
        self.norm, self.same = norm, same
        self.apart = apart or {}
        self._n = {}
        self.parent = {}
        self.joined = []     # ("spelling" | "league", scope, code a, norm a, code b, norm b): every join made
        self._build(fixtures)

    # -- union-find over (scope, code, norm) nodes
    def _find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def _union(self, a, b):
        a, b = self._find(a), self._find(b)
        if a != b:
            self.parent[max(a, b)] = min(a, b)

    def n(self, name):
        if name not in self._n:
            self._n[name] = self.norm(name)
        return self._n[name]

    def _clash(self, fa, fb):
        """Do two fixture lists (date, opponent norm, opponent raw) show two
        clubs: games within NEAR_DAYS against opponents that are not one
        club? Returns (clash, same match seen)."""
        clash = shared = False
        for da, oa, ra in fa:
            for db, ob, rb in fb:
                if abs((da - db).days) > NEAR_DAYS:
                    continue
                if oa == ob or self.same(ra, rb):
                    shared = shared or da == db
                else:
                    clash = True
        return clash, shared

    def _build(self, fixtures):
        played = defaultdict(list)       # (scope, code, norm) -> [(date, opp norm, opp raw)]
        raws = defaultdict(set)          # (scope, code, norm) -> spellings
        for code, d, home, away in fixtures:
            kind, sc = scope_of(code, self.L)
            if kind != "dom":
                continue
            d = _day(d)
            for t, o in ((home, away), (away, home)):
                k = (sc, code, self.n(t))
                played[k].append((d, self.n(o), o))
                raws[k].add(t)
                self._find(k)
        # 1. two spellings inside one league
        by_code = defaultdict(list)
        for k in played:
            by_code[k[:2]].append(k)
        for (sc, code), ks in by_code.items():
            tok = defaultdict(list)
            for k in ks:
                for w in set(k[2].split()):
                    tok[w].append(k)
            seen = set()
            for group in tok.values():
                if len(group) < 2 or len(group) > 12:
                    continue
                for i, a in enumerate(group):
                    for b in group[i + 1:]:
                        if (a, b) in seen or (b, a) in seen:
                            continue
                        seen.add((a, b))
                        if not any(self.same(x, y) for x in raws[a] for y in raws[b]):
                            continue
                        if any(frozenset((x, y)) in self.apart.get(code, ()) for x in raws[a] for y in raws[b]):
                            continue
                        if a[2] in {o for _, o, _ in played[b]} or b[2] in {o for _, o, _ in played[a]}:
                            continue           # they have met: two clubs
                        if self._clash(played[a], played[b])[0]:
                            continue
                        self._union(a, b)
                        self.joined.append(("spelling", sc, code, a[2], code, b[2]))
        # 2. one name in two leagues of a scope
        by_name = defaultdict(list)
        for k in played:
            by_name[(k[0], k[2])].append(k)
        for ks in by_name.values():
            if len(ks) < 2:
                continue
            pairs = [(a, b) + self._clash(played[a], played[b]) for i, a in enumerate(ks) for b in ks[i + 1:]]
            any_clash = any(c for _, _, c, _ in pairs)
            for a, b, clash, shared in pairs:
                if not clash and (shared or not any_clash):
                    self._union(a, b)
                    self.joined.append(("league", a[0], a[1], a[2], b[1], b[2]))
        # the clubs of each scope by every norm they are written under
        self.dom = defaultdict(set)      # (scope, norm) -> {root}
        self.anywhere = defaultdict(set)  # (women?, norm) -> {root}
        self.spelt = defaultdict(set)    # root -> every spelling it is written under
        for k in played:
            r = self._find(k)
            self.dom[(k[0], k[2])].add(r)
            self.anywhere[(k[0].endswith("-w"), k[2])].add(r)
            self.spelt[r] |= raws[k]

    def _one(self, roots, name):
        """The one league club a cup or continental name belongs to, or None:
        the only club carrying the name, else the only one written exactly
        this way (AC Milan beside Serie D's Club Milano)."""
        if len(roots) == 1:
            return next(iter(roots))
        exact = [r for r in roots if name in self.spelt[r]]
        return exact[0] if len(exact) == 1 else None

    def id(self, code, name):
        """The identity a name plays under in this competition."""
        kind, sc = scope_of(code, self.L)
        nm = self.n(name)
        if kind == "dom":
            return self._find((sc, code, nm))
        if kind == "cup":
            roots = self.dom.get((sc, nm)) or ()
            return self._one(roots, name) or (sc, "cup" if not roots else code, nm)
        if kind == "cont":
            return self._one(self.anywhere.get((sc == "cont-w", nm)) or (), name) or (sc, "", nm)
        return (sc, "", nm)


class Tally:
    def __init__(self):
        self.t = {}          # id -> [n, right, quoted, backed, backed won, against, against right, last, from, to]
        self.seen = defaultdict(list)

    def add(self, tid, opp, d, ok, conf, backed):
        """One graded fixture for one side. backed: True the model picked
        this side, False it picked the other, None it called a draw. A second
        copy of the same meeting within a day (a league under two codes) is
        left out."""
        d = _day(d)
        if any(o == opp and abs((d - x).days) <= 1 for o, x in self.seen[tid]):
            return False
        self.seen[tid].append((opp, d))
        r = self.t.setdefault(tid, [0, 0, 0.0, 0, 0, 0, 0, "", str(d), str(d)])
        r[0] += 1; r[1] += bool(ok); r[2] += conf
        if backed is True:
            r[3] += 1; r[4] += bool(ok)
        elif backed is False:
            r[5] += 1; r[6] += bool(ok)
        r[7] = (r[7] + ("1" if ok else "0"))[-LAST:]
        r[9] = str(d)
        return True

    def row(self, tid):
        r = self.t.get(tid)
        return None if not r else [r[0], r[1], round(r[2], 2)] + r[3:]


def football_rows(graded):
    rows = [g for g in graded or [] if g.get("result") and g.get("pick") and g.get("confidence") is not None]
    rows.sort(key=lambda g: (g["date"], g.get("kickoff") or "", g.get("published") or "", g["home"]))
    return rows


def board_fixtures(pred_dir=None, files=BOARD_FILES):
    """(code, date, home, away) for the fixtures on the page now: the newest
    football archive days, so a side with no graded game in this competition
    still finds its record under the page's spelling."""
    out = []
    for path in sorted(glob.glob(os.path.join(pred_dir or os.path.join(HERE, "predictions"), "*.json")))[-files:]:
        try:
            with open(path) as f:
                for r in json.load(f):
                    out.append((r["league"], r["date"], r["home"], r["away"]))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


def build(football=None, tennis=None, sports=None, board=None, clubs=None, now=None):
    """The page's file as a dict. Every argument defaults to the repo's
    record files; tests pass their own."""
    fb = football_rows(_load("record-graded.json").get("graded") if football is None else football)
    board = board_fixtures() if board is None else board
    keys, rows, index = {}, [], {}
    T = Tally()
    count = {}

    def put(key, tid):
        r = T.row(tid)
        if r is None:
            return
        if tid not in index:
            index[tid] = len(rows); rows.append(r)
        keys[key] = index[tid]

    if fb or board:
        if clubs is None:
            import score
            clubs = Clubs([(g["league"], g["date"], g["home"], g["away"]) for g in fb] + list(board),
                          apart=score.distinct_names(fb))
        for g in fb:
            ok = g["pick"] == g["actual"]
            h, a = clubs.id(g["league"], g["home"]), clubs.id(g["league"], g["away"])
            side = {"h": (True, False), "a": (False, True)}.get(g["pick"], (None, None))
            T.add(h, a, g["date"], ok, g["confidence"], side[0])
            T.add(a, h, g["date"], ok, g["confidence"], side[1])
        count["football"] = len(T.t)
        # only the names on the page now: every club's row would be several hundred KB
        for code, _, home, away in board:
            for t in (home, away):
                put(f"f|{code}|{t}", clubs.id(code, t))

    def two_sided(label, games, home, away, when, key):
        before = len(T.t)
        games = [g for g in games if not g.get("void") and g.get("ok") is not None
                 and g.get("confidence") is not None and g.get("pick")]
        games.sort(key=lambda g: (str(g.get(when) or ""), str(g.get(home))))
        for g in games:
            sp = key(g)
            h, a = (sp, g[home]), (sp, g[away])
            T.add(h, a, str(g[when])[:10], g["ok"], g["confidence"], g["pick"] == g[home])
            T.add(a, h, str(g[when])[:10], g["ok"], g["confidence"], g["pick"] == g[away])
        for tid in list(T.t)[before:]:
            put(f"{tid[0]}|{tid[1]}", tid)
        count[label] = len(T.t) - before

    two_sided("tennis", (_load("tennis-record.json").get("graded") or []) if tennis is None else tennis,
              "playerA", "playerB", "date", lambda g: "tennis")
    two_sided("sports", (_load("sports-graded.json").get("graded") or []) if sports is None else sports,
              "home", "away", "when", lambda g: str(g.get("sport")))
    since = min((r[8] for r in rows), default=None)
    return {"generated": (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rule": RULE, "minRead": MIN_READ, "last": LAST, "since": since, "teams": count,
            "cols": ["n", "right", "quoted", "backed", "backedWon", "against", "againstRight", "last", "from", "to"],
            "keys": keys, "rows": rows}


def walk_forward(graded=None, min_prior=6, floor=0.55):
    """Does a team's record say anything about its next game? For every
    graded football pick at `floor`+ whose two sides each had `min_prior`
    graded fixtures before that day, the pick's result by how far the model
    had run above or under its quote on those sides. Advisory: a read of the
    scoreboard, printed by --check, never an input."""
    fb = football_rows(_load("record-graded.json").get("graded") if graded is None else graded)
    import score
    clubs = Clubs([(g["league"], g["date"], g["home"], g["away"]) for g in fb], apart=score.distinct_names(fb))
    hist = defaultdict(lambda: [0, 0, 0.0])
    cells = defaultdict(lambda: [0, 0, 0.0, 0.0])
    day, pend = None, []

    def flush():
        for g, ids in pend:
            for i in ids:
                h = hist[i]; h[0] += 1; h[1] += g["pick"] == g["actual"]; h[2] += g["confidence"]
        pend.clear()

    for g in fb:
        if g["date"] != day:
            flush(); day = g["date"]
        ids = (clubs.id(g["league"], g["home"]), clubs.id(g["league"], g["away"]))
        a, b = hist[ids[0]], hist[ids[1]]
        if min(a[0], b[0]) >= min_prior and g["confidence"] >= floor:
            sur = (a[1] + b[1] - a[2] - b[2]) / (a[0] + b[0])
            band = "10+ under" if sur < -0.10 else "0-10 under" if sur < 0 else "0-10 over" if sur < 0.10 else "10+ over"
            c = cells[band]; ok = g["pick"] == g["actual"]; q = g["confidence"]
            c[0] += 1; c[1] += ok; c[2] += q; c[3] += q * (1 - q)
        pend.append((g, ids))
    out = {}
    for band in ("10+ under", "0-10 under", "0-10 over", "10+ over"):
        n, w, q, v = cells[band]
        if n:
            out[band] = {"n": n, "landed": round(w / n, 4), "quoted": round(q / n, 4),
                         "z": round((w - q) / math.sqrt(v), 2) if v > 0 else None}
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--check" in argv:
        print("picks at 55%+ by the two sides' earlier record against quote (walk-forward, football):")
        for band, c in walk_forward().items():
            print(f"  {band:>10}: {c['n']:4d} picks, landed {c['landed']:.1%} v quoted {c['quoted']:.1%}, z {c['z']:+.2f}")
        return 0
    data = build()
    with open(os.path.join(HERE, OUT), "w") as f:
        f.write("window.__TEAM_RECORD__=" + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";")
    print(f"team record: {data['teams']} teams tallied, {len(data['keys'])} names and {len(data['rows'])} rows written, "
          f"{os.path.getsize(os.path.join(HERE, OUT)) // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
