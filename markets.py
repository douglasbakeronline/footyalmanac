"""Football markets beyond the match winner: the model's number, the
bookmakers' price and the result, tracked for every fixture (14 Nov 2026).

Douglas, 14 Nov 2026: "For football fixtures I want to start looking at winner
and btts, as well as just btts, goals over 2.5, and any other things you
suggest. Let's go hard on setting this up to track on football." And: "a lot
of time I'm spending reviewing things. I need this to be more automated."

Ten markets, each read from the scoreline grid the match model already
builds (engine's Dixon-Coles grid from the fixture's expected goals), with
the grid's home / draw / away totals rescaled to the published chances so
every market agrees with the row's own 1X2 numbers:

  btts    both teams to score (the published number, engine's own)
  o15     over / under 1.5 goals
  o25     over / under 2.5 goals (the published number)
  o35     over / under 3.5 goals
  wbtts   the pick to win and both teams to score
  wo25    the pick to win and over 2.5 goals
  wtn     the pick to win to nil
  dc      double chance: the pick or the draw
  dnb     draw no bet on the pick (a draw returns the stake)
  tts     the pick's team to score

"The pick" is the likelier of home and away, never the draw. A two-sided
market's selection is its likelier side. One selection a market a fixture.

Prices are API-Football's (`/odds?date=`, every bet in one sweep: the same
number of calls as the match-winner sweep, checked on the live feed on
14 Nov 2026, tools/markets_probe.py on the odds-probe-run branch): the average
over every bookmaker, the best UK book, William Hill's own, and the
bookmakers' fair chance where the whole market is priced. Display and record
only: no price feeds any model, and the Daily List never sees one.

    python3 markets.py            # CI: price and archive, then grade
    python3 markets.py --build    # archive today's and tomorrow's fixtures
    python3 markets.py --score    # write markets-record.json

--build reads the newest predictions/<date>.json (what build.py just
archived: the numbers score.py grades), prices each fixture still to start
in the next MARKET_DAYS UTC days and merges it into
predictions-markets/<date>.json.gz. A fixture's row is replaced until its
kick-off and never after; a later copy with no price keeps the earlier
price for the same selection.

--score grades every archived row against record-graded.json (the result
score.py recorded) into markets-record.json: by market, landed against the
model's number and against the bookmakers' fair chance, the flat return at
the average, best and William Hill price, bands by chance and by the gap
between model and bookmakers, and a gate verdict. Fixtures from before the
markets archive are replayed from the copy of predictions/ that score.py
graded (the same expected goals and chances, no prices), kept apart as
`replay`: calibration only. Unrated sides are left out (their expected goals
are a placeholder).

The gate (pre-registered here, 14 Nov 2026; read on live priced picks only,
never the replay): a rule passes a market when it has GATE_N+ settled priced
picks, they landed above the bookmakers' fair chance, the return at the best
UK price is positive and the day-resampled chance that it is not is
GATE_P or less. Two rules a market: `value` (the model GATE_EDGE or more
above the bookmakers' fair chance) and `all` (every selection). A pass is
printed in bold in the nightly Card review; what it then earns on the page
is a release, not this file's decision. Nothing here is fitted (Rule 1).

Standard library only.
"""
import argparse, glob, gzip, json, math, os, random, sys, time
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "predictions-markets")
RECORD = os.path.join(HERE, "markets-record.json")
RULE = 1                      # the numbers' definition; bump on any change to numbers()
MARKET_DAYS = 2               # UTC dates priced and archived: today and tomorrow
ODDS_TTL = 5 * 3600           # a date's prices are re-read this often (about 4 sweeps a day)
ODDS_FRUGAL_TTL = 24 * 3600   # a push-triggered build (AF_FRUGAL) reuses a day-old copy
ODDS_PARTIAL_TTL = 3600       # a sweep cut short is retried sooner
ODDS_MAX_PAGES = 90           # a date's ceiling: 900 priced fixtures
ODDS_MAX_SECONDS = 180        # a sweep stops here, keeps what it has and resumes on the next build
AF_FLOOR = 2000               # calls left today under which the sweep stands down (the build comes first)
ODDS_VERSION = 2              # 2 (16 Nov 2026): rows carry the extra lines (`x`, EXTRA_BETS)
GATE_N, GATE_P, GATE_EDGE = 150, 0.10, 0.05
BOOK = "William Hill"         # groupings.CARD_BOOK

NAMES = {"btts": "Both teams to score", "o15": "Over / under 1.5 goals", "o25": "Over / under 2.5 goals",
         "o35": "Over / under 3.5 goals", "wbtts": "Win and both teams to score", "wo25": "Win and over 2.5 goals",
         "wtn": "Win to nil", "dc": "Double chance (win or draw)", "dnb": "Draw no bet", "tts": "Pick's team to score"}
MARKETS = tuple(NAMES)


# ------------------------------------------------------------------ the numbers

def grid(lh, la, p=None):
    """The Dixon-Coles scoreline grid for these expected goals, summing to 1,
    with its home / draw / away regions rescaled to the published chances p
    ({"h", "d", "a"}) when given: the tempered 1X2 numbers are the ones the
    record has tested, so every market is made to agree with them."""
    import engine as E
    n = E.MAX_GOALS + 1
    ph = [E._pois(i, lh) for i in range(n)]
    pa = [E._pois(i, la) for i in range(n)]
    g = [[ph[x] * pa[y] * E._tau(x, y, lh, la) for y in range(n)] for x in range(n)]
    tot = sum(map(sum, g))
    g = [[c / tot for c in row] for row in g]
    if p:
        raw = {"h": sum(g[x][y] for x in range(n) for y in range(n) if x > y),
               "d": sum(g[x][x] for x in range(n)),
               "a": sum(g[x][y] for x in range(n) for y in range(n) if x < y)}
        ps = sum(p[k] for k in "hda") or 1.0
        w = {k: (p[k] / ps) / raw[k] if raw[k] > 0 else 1.0 for k in "hda"}
        g = [[c * w["h" if x > y else "d" if x == y else "a"] for y, c in enumerate(row)] for x, row in enumerate(g)]
    return g


def _sum(g, test):
    return sum(c for x, row in enumerate(g) for y, c in enumerate(row) if test(x, y))


def numbers(lh, la, p, btts=None, over25=None):
    """{market: {"s": selection, "p": chance}} for one fixture, and the pick's
    side. p is the published {"h", "d", "a"}; btts and over25 the published
    two-way numbers (engine's own, used as they stand when given)."""
    g = grid(lh, la, p)
    side = "h" if p["h"] >= p["a"] else "a"
    win = (lambda x, y: x > y) if side == "h" else (lambda x, y: y > x)
    mine = (lambda x, y: x) if side == "h" else (lambda x, y: y)
    theirs = (lambda x, y: y) if side == "h" else (lambda x, y: x)
    ps = sum(p[k] for k in "hda") or 1.0
    pw, pd = p[side] / ps, p["d"] / ps

    def two(yes, a, b):
        return {"s": a, "p": yes} if yes >= 0.5 else {"s": b, "p": 1 - yes}

    by = btts if btts is not None else _sum(g, lambda x, y: x >= 1 and y >= 1)
    o25 = over25 if over25 is not None else _sum(g, lambda x, y: x + y >= 3)
    out = {"btts": two(by, "yes", "no"),
           "o15": two(_sum(g, lambda x, y: x + y >= 2), "over", "under"),
           "o25": two(o25, "over", "under"),
           "o35": two(_sum(g, lambda x, y: x + y >= 4), "over", "under"),
           "wbtts": {"s": side, "p": _sum(g, lambda x, y: win(x, y) and x >= 1 and y >= 1)},
           "wo25": {"s": side, "p": _sum(g, lambda x, y: win(x, y) and x + y >= 3)},
           "wtn": {"s": side, "p": _sum(g, lambda x, y: win(x, y) and theirs(x, y) == 0)},
           "dc": {"s": side, "p": pw + pd},
           "dnb": {"s": side, "p": pw / (1 - pd) if pd < 1 else 0.0},
           "tts": {"s": side, "p": _sum(g, lambda x, y: mine(x, y) >= 1)}}
    for v in out.values():
        v["p"] = round(min(max(v["p"], 0.0), 1.0), 4)
    return side, out


def settle(market, sel, hg, ag):
    """True (landed), False, or None (void: a draw on draw no bet)."""
    tot = hg + ag
    if market == "btts": return (hg >= 1 and ag >= 1) == (sel == "yes")
    if market in ("o15", "o25", "o35"):
        line = {"o15": 2, "o25": 3, "o35": 4}[market]
        return (tot >= line) == (sel == "over")
    won = hg > ag if sel == "h" else ag > hg
    mine, theirs = (hg, ag) if sel == "h" else (ag, hg)
    if market == "wbtts": return won and hg >= 1 and ag >= 1
    if market == "wo25": return won and tot >= 3
    if market == "wtn": return won and theirs == 0
    if market == "dc": return won or hg == ag
    if market == "dnb": return None if hg == ag else won
    if market == "tts": return mine >= 1
    raise KeyError(market)


# ------------------------------------------------------------------- the prices
#
# API-Football bet ids, names and value labels as its live feed gave them on
# 14 Nov 2026 (probe/markets-probe.json on the odds-probe-report branch).
# (bet id, value label) -> (market, outcome). An outcome is the selection it
# prices ("yes", "over", "h") or another member of the same market, kept so
# the bookmakers' margin can be taken out.
def _labels():
    m = {(8, "Yes"): ("btts", "yes"), (8, "No"): ("btts", "no"),
         (2, "Home"): ("dnb", "h"), (2, "Away"): ("dnb", "a"),
         (12, "Home/Draw"): ("dc", "h"), (12, "Draw/Away"): ("dc", "a"), (12, "Home/Away"): ("dc", "x"),
         # win to nil: one bet for both sides at Bet365 and William Hill, a yes / no bet a side elsewhere
         (36, "Home"): ("wtn", "h"), (36, "Away"): ("wtn", "a"),
         (29, "Yes"): ("wtn", "h"), (29, "No"): ("wtn", "h/no"), (30, "Yes"): ("wtn", "a"), (30, "No"): ("wtn", "a/no"),
         # the team to score: William Hill lists it as its own bet, the others as the team total over 0.5
         (43, "Yes"): ("tts", "h"), (43, "No"): ("tts", "h/no"), (44, "Yes"): ("tts", "a"), (44, "No"): ("tts", "a/no"),
         (16, "Over 0.5"): ("tts", "h"), (16, "Under 0.5"): ("tts", "h/no"),
         (17, "Over 0.5"): ("tts", "a"), (17, "Under 0.5"): ("tts", "a/no")}
    for key, line in (("o15", "1.5"), ("o25", "2.5"), ("o35", "3.5")):
        m[(5, f"Over {line}")] = (key, "over"); m[(5, f"Under {line}")] = (key, "under")
    for res, s in (("Home", "h"), ("Draw", "d"), ("Away", "a")):
        m[(24, f"{res}/Yes")] = ("wbtts", s if s != "d" else "d/yes"); m[(24, f"{res}/No")] = ("wbtts", f"{s}/no")
        m[(25, f"{res}/Over 2.5")] = ("wo25", s if s != "d" else "d/over"); m[(25, f"{res}/Under 2.5")] = ("wo25", f"{s}/under")
    return m


LABELS = _labels()
BETS = {b for b, _ in LABELS}
# The outcomes that make up a whole market, and what their true chances sum
# to: 1 for a partition, 2 for double chance (each result is in two of its
# three outcomes). The team to score and win to nil are a yes / no a side
# (_whole); where a book prices only the yes, there is no fair chance.
WHOLE = {"btts": (("yes", "no"), 1), "o15": (("over", "under"), 1), "o25": (("over", "under"), 1),
         "o35": (("over", "under"), 1), "dnb": (("h", "a"), 1), "dc": (("h", "a", "x"), 2),
         "wbtts": (("h", "h/no", "d/yes", "d/no", "a", "a/no"), 1),
         "wo25": (("h", "h/under", "d/over", "d/under", "a", "a/under"), 1)}


# 16 Nov 2026 (Douglas: "make sure we get to the level where everything is
# captured"): the sweep already returns every bet of every book; these are kept
# as well, by API-Football's bet name, so the scale bets the record can settle
# (handicaps, halves, team totals) have the bookmakers' lines beside them. Only
# the average over books and William Hill's price, and only for fixtures this
# site predicts (the archive rows), so the files stay small. Nothing reads them yet.
EXTRA_BETS = ("Asian Handicap", "Handicap Result", "HT/FT Double", "First Half Winner", "Second Half Winner",
              "Goals Over/Under First Half", "Total - Home", "Total - Away", "Home Team Score a Goal",
              "Away Team Score a Goal", "Win Both Halves", "Home win both halves", "Away win both halves",
              "To Win Either Half", "Clean Sheet - Home", "Clean Sheet - Away")
EXTRA_MAX = 120                 # values kept a fixture at most, a guard on file size


def _whole(market, sel):
    if market in ("tts", "wtn"):
        return (sel, f"{sel}/no"), 1
    return WHOLE.get(market, (None, None))


def parse_odds(items):
    """{fixture id: {market: {outcome: {"o": average, "n": books, "b": best UK
    price, "bb": its book, "h": William Hill}}}} from /odds response items.
    The average is over every bookmaker; best is among UK-licensed books
    (odds.UK_BOOKS), None when none priced it."""
    import odds as O
    out = {}
    for item in items or []:
        fid = (item.get("fixture") or {}).get("id")
        if not fid: continue
        acc, extra = {}, {}
        for b in item.get("bookmakers") or []:
            name = b.get("name")
            uk = O.uk_book(name)
            seen = set()
            for bet in b.get("bets") or []:
                if bet.get("name") in EXTRA_BETS:
                    hill = uk and O.uk_name(name) == BOOK
                    for v in bet.get("values") or []:
                        try: o = float(v.get("odd"))
                        except (TypeError, ValueError): continue
                        if o <= 1.0: continue
                        e = extra.setdefault(bet["name"], {}).setdefault(str(v.get("value")).strip(), [[], None])
                        e[0].append(o)
                        if hill: e[1] = round(o, 2)
                if bet.get("id") not in BETS: continue
                for v in bet.get("values") or []:
                    hit = LABELS.get((bet.get("id"), str(v.get("value")).strip()))
                    if not hit or hit in seen: continue     # one price a book an outcome
                    try: o = float(v.get("odd"))
                    except (TypeError, ValueError): continue
                    if o <= 1.0: continue
                    seen.add(hit)
                    a = acc.setdefault(hit[0], {}).setdefault(hit[1], {"all": [], "b": None, "bb": None, "h": None})
                    a["all"].append(o)
                    if uk and (a["b"] is None or o > a["b"]): a["b"], a["bb"] = round(o, 2), O.uk_name(name)
                    if uk and O.uk_name(name) == BOOK: a["h"] = round(o, 2)
        row = {}
        for mk, outs in acc.items():
            row[mk] = {oc: {k: v for k, v in (("o", round(sum(a["all"]) / len(a["all"]), 3)), ("n", len(a["all"])),
                                              ("b", a["b"]), ("bb", a["bb"]), ("h", a["h"])) if v is not None}
                       for oc, a in outs.items()}
        if extra:
            x, n = {}, 0
            for bn, vals in extra.items():
                for val, (os_, h) in vals.items():
                    if n >= EXTRA_MAX: break
                    x.setdefault(bn, {})[val] = [round(sum(os_) / len(os_), 3), h] if h else [round(sum(os_) / len(os_), 3)]
                    n += 1
            row["x"] = x
        if row: out[str(fid)] = row
    return out


def price_of(row, market, sel):
    """The selection's price block from one fixture's parsed odds, with `f`,
    the bookmakers' fair chance, when the whole market is priced. None when
    the selection itself has no price."""
    outs = (row or {}).get(market) or {}
    mine = outs.get(sel)
    if not mine: return None
    blk = dict(mine)
    members, total = _whole(market, sel)
    if members and all(m in outs for m in members):
        imp = sum(1.0 / outs[m]["o"] for m in members)
        if imp > 0:
            blk["f"] = round((1.0 / mine["o"]) * total / imp, 4)
    return blk


def _odds_path(d):
    import sources as S
    return os.path.join(S.AF_CACHE_DIR, f"markets-odds-{d.isoformat()}.json.gz")


def odds_day(d, log=None, now=None):
    """Every tracked market's prices on one UTC date, {fixture id: row}.
    Cached in .afcache; a failed or refused sweep keeps the last copy. Stands
    down when the day's API-Football allowance is under AF_FLOOR."""
    import sources as S
    now = now or time.time()
    path, stale, start = _odds_path(d), None, 1
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            doc = json.load(fh)
        stale = doc.get("rows") or {}
        ttl = ODDS_PARTIAL_TTL if doc.get("partial") else ODDS_TTL
        if os.environ.get("AF_FRUGAL"): ttl = max(ttl, ODDS_FRUGAL_TTL)
        if doc.get("v") == ODDS_VERSION and now - doc.get("fetched", 0) < ttl:
            return stale
        # a sweep cut short picks up at the page it stopped on, while its
        # first pages are still fresh; otherwise every sweep starts again
        if doc.get("v") == ODDS_VERSION and doc.get("partial") and doc.get("resume") \
                and now - doc.get("began", 0) < ODDS_TTL:
            start = int(doc["resume"])
    except (OSError, ValueError):
        pass
    if not os.environ.get("API_FOOTBALL_KEY"):
        return stale or {}
    rows, page, total, calls, partial, t0 = {}, start, start, 0, False, time.time()
    began = doc.get("began", now) if start > 1 else now
    while page <= min(total, ODDS_MAX_PAGES):
        q = f"/odds?date={d.isoformat()}&page={page}"
        items = S._af_get(q); calls += 1
        # every bet of every bookmaker is megabytes a page: parsed, then let go
        S._AF_CACHE.pop(q, None)
        if not items:
            partial = page > start
            break
        rows.update(parse_odds(items))
        total = int((S.AF_PAGING.get(q) or {}).get("total") or page)
        left = S.AF_USAGE.get("left")
        if left is not None and left < AF_FLOOR:
            partial = page < total; page += 1
            if log is not None: log.append(f"markets odds {d}: stood down at {left} calls left today")
            break
        if time.time() - t0 > ODDS_MAX_SECONDS:
            partial = page < total; page += 1
            break
        page += 1
    if not rows:
        if log is not None:
            log.append(f"markets odds {d}: nothing returned ({calls} calls), " + ("kept the last copy" if stale else "no copy on file"))
        return stale or {}
    if (partial or start > 1) and stale:
        rows = {**stale, **rows}
    os.makedirs(S.AF_CACHE_DIR, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump({"fetched": now, "began": began, "v": ODDS_VERSION, "partial": partial,
                   "resume": page if partial else None, "rows": rows}, fh, separators=(",", ":"))
    if log is not None:
        log.append(f"markets odds {d}: {len(rows)} fixtures priced, {calls} calls" + (" (partial)" if partial else ""))
    return rows


# ------------------------------------------------------------------- the archive

def parse_utc(s):
    if not s: return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else None


def _load(path, default=None):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f: return json.load(f)
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default


def key_of(r): return (r["league"], r["date"], r["home"], r["away"])


def row_for(g, prices=None, published=None):
    """The archive row for one predictions/ entry g, or None when it cannot
    be priced by the model (no expected goals, an unrated side)."""
    if not g.get("xg") or not g.get("p") or g.get("unrated"): return None
    side, nums = numbers(g["xg"][0], g["xg"][1], g["p"], g.get("btts"), g.get("over25"))
    for mk, v in nums.items():
        blk = price_of(prices, mk, v["s"])
        if blk: v.update(blk)
    row = {"league": g["league"], "date": g["date"], "home": g["home"], "away": g["away"],
           "kickoff": g.get("kickoff"), "published": published, "side": side, "v": RULE,
           "celtic": bool(g.get("celtic")), "m": nums}
    if (prices or {}).get("x"):
        row["x"] = prices["x"]          # the extra lines (EXTRA_BETS): {bet: {value: [average, Hill]}}
    return row


PRICE_KEYS = ("o", "n", "b", "bb", "h", "f")


def merge_rows(old, new, now):
    """The day's archive after this build: a fixture's row is replaced until
    its kick-off and kept as it stood from then on; a first row for a fixture
    already started is refused; a new row with no price for a market keeps
    the earlier price when the selection is the same."""
    out = {key_of(r): r for r in old or []}
    for r in new:
        ko = parse_utc(r.get("kickoff"))
        k = key_of(r)
        prev = out.get(k)
        pko = parse_utc((prev or {}).get("kickoff")) or ko
        if (ko and ko <= now) or (pko and pko <= now):
            continue
        if not ko and r["date"] <= now.date().isoformat():
            continue        # no kick-off time on its own day: cannot be shown to predate the start
        if prev:
            if "x" not in r and "x" in prev:
                r["x"] = prev["x"]      # a later build with no extra lines keeps the earlier ones
            for mk, v in r["m"].items():
                pv = (prev.get("m") or {}).get(mk) or {}
                if "o" not in v and "o" in pv and pv.get("s") == v["s"]:
                    v.update({x: pv[x] for x in PRICE_KEYS if x in pv})
        out[k] = r
    return sorted(out.values(), key=lambda r: (r.get("kickoff") or r["date"], r["league"], r["home"]))


def build(now=None, here=HERE, fetch=True, log=None):
    """Price and archive the fixtures still to start in the next MARKET_DAYS
    UTC days. Returns (rows written, priced, file)."""
    now = now or datetime.now(timezone.utc)
    log = log if log is not None else []
    files = sorted(glob.glob(os.path.join(here, "predictions", "*.json")))
    if not files:
        return 0, 0, None
    src = files[-1]
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    last = (now.date() + timedelta(days=MARKET_DAYS - 1)).isoformat()
    games = []
    for g in _load(src, []) or []:
        ko = parse_utc(g.get("kickoff"))
        if ko and not (now < ko and ko.date().isoformat() <= last): continue
        if not ko and not (now.date().isoformat() < g.get("date", "") <= last): continue
        games.append(g)
    by_fid = {}
    if fetch and games and os.environ.get("API_FOOTBALL_KEY"):
        try:
            import odds as O
            days = sorted({now.date() + timedelta(days=i) for i in range(MARKET_DAYS)})
            prices = {}
            for d in days:
                prices.update(odds_day(d, log=log))
            idx = O.af_fixture_index({d + timedelta(days=o) for d in days for o in (-1, 0, 1)})
            hit = O.match_af([(i, parse_utc(g.get("kickoff")), g["date"], g["home"], g["away"]) for i, g in enumerate(games)], idx)
            by_fid = {i: prices.get(fid) for i, fid in hit.items()}
            log.append(f"markets: {len(hit)} of {len(games)} fixtures matched to API-Football, "
                       f"{sum(1 for v in by_fid.values() if v)} with a market price")
        except Exception as e:
            log.append(f"markets prices failed: {type(e).__name__}: {e}")
    rows = [r for r in (row_for(g, by_fid.get(i), stamp) for i, g in enumerate(games)) if r]
    os.makedirs(os.path.join(here, "predictions-markets"), exist_ok=True)
    path = os.path.join(here, "predictions-markets", os.path.basename(src) + ".gz")
    merged = merge_rows((_load(path, []) or []), rows, now)
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(merged, f, separators=(",", ":"), ensure_ascii=False)
    os.replace(tmp, path)
    priced = sum(1 for r in rows if any("o" in v for v in r["m"].values()))
    return len(rows), priced, path


# -------------------------------------------------------------------- the record

def results(here=HERE):
    """{(league, home, away): [(date, graded row)]} from record-graded.json."""
    out = {}
    for g in (_load(os.path.join(here, "record-graded.json"), {}) or {}).get("graded") or []:
        if g.get("result"):
            out.setdefault((g["league"], g["home"], g["away"]), []).append((g["date"], g))
    return out


def _result_for(r, res, days=3):
    cands = res.get((r["league"], r["home"], r["away"])) or []
    d0 = date.fromisoformat(r["date"])
    best = None
    for d, g in cands:
        off = (date.fromisoformat(d) - d0).days
        # 15 Nov 2026: a result two or more days before the fixture's own date is an
        # earlier meeting of the same sides, not this game (New Zealand v India,
        # 12 and 15 Nov: the second was graded 5-0 before it kicked off). A moved
        # fixture's newest archived copy carries its new date (live_rows).
        if off < -1: continue
        gap = abs(off)
        if gap <= days and (best is None or gap < best[0]): best = (gap, g)
    return best[1] if best else None


def live_rows(here=HERE):
    """The newest archived copy of each fixture published before its start."""
    best = {}
    for path in sorted(glob.glob(os.path.join(here, "predictions-markets", "*.json.gz"))):
        for r in _load(path, []) or []:
            pub, ko = parse_utc(r.get("published")), parse_utc(r.get("kickoff"))
            if not pub: continue
            if ko and pub >= ko: continue
            if not ko and r.get("published", "")[:10] >= r["date"]: continue
            k = (r["league"], r["home"], r["away"], r["date"])
            if k not in best or r["published"] > best[k]["published"]: best[k] = r
    # a fixture moved to another day: the newest copy of the pairing within 10 days is the fixture
    by_pair = {}
    for k, r in best.items():
        by_pair.setdefault(k[:3], []).append(r)
    out = []
    for rows in by_pair.values():
        rows.sort(key=lambda r: r["date"])
        cluster = [rows[0]]
        for r in rows[1:]:
            if (date.fromisoformat(r["date"]) - date.fromisoformat(cluster[-1]["date"])).days <= 10:
                cluster.append(r)
            else:
                out.append(max(cluster, key=lambda x: x["published"])); cluster = [r]
        out.append(max(cluster, key=lambda x: x["published"]))
    return out


def replay_rows(res, skip, here=HERE):
    """Fixtures graded before the markets archive, from the copy of
    predictions/ score.py graded (matched on its publish time): the same
    expected goals and chances, no prices."""
    want = {}
    for (lg, h, a), cands in res.items():
        for d, g in cands:
            if g.get("published") and (lg, h, a, d) not in skip:
                want[(lg, d, h, a, g["published"])] = g
    out = []
    for path in sorted(glob.glob(os.path.join(here, "predictions", "*.json"))):
        for g in _load(path, []) or []:
            k = (g.get("league"), g.get("date"), g.get("home"), g.get("away"), g.get("published"))
            if k not in want: continue
            del want[k]
            r = row_for(g, None, g.get("published"))
            if r: out.append(r)
    return out


def _tally():
    return {"n": 0, "landed": 0, "void": 0, "quoted": 0.0, "var": 0.0,
            "priced": 0, "ret": 0.0, "retBest": 0.0, "hill": 0, "retHill": 0.0,
            "fairN": 0, "fair": 0.0, "fairLanded": 0}


def _add(t, v, ok):
    if ok is None:
        t["void"] += 1
    else:
        t["n"] += 1; t["landed"] += ok; t["quoted"] += v["p"]; t["var"] += v["p"] * (1 - v["p"])
    if "o" in v:
        back = lambda o: 1.0 if ok is None else (o if ok else 0.0)
        t["priced"] += 1; t["ret"] += back(v["o"]); t["retBest"] += back(v.get("b") or v["o"])
        if v.get("h"):
            t["hill"] += 1; t["retHill"] += back(v["h"])
        if "f" in v and ok is not None:
            t["fairN"] += 1; t["fair"] += v["f"]; t["fairLanded"] += ok


def _done(t):
    out = {"n": t["n"], "landed": t["landed"]}
    if t["void"]: out["void"] = t["void"]
    if t["n"]:
        out["rate"] = round(t["landed"] / t["n"], 4); out["quoted"] = round(t["quoted"] / t["n"], 4)
        if t["var"] > 0: out["z"] = round((t["landed"] - t["quoted"]) / math.sqrt(t["var"]), 2)
    if t["priced"]:
        out["priced"] = t["priced"]; out["ret"] = round(t["ret"] / t["priced"] - 1, 4)
        out["retBest"] = round(t["retBest"] / t["priced"] - 1, 4)
    if t["hill"]:
        out["atHill"] = t["hill"]; out["retHill"] = round(t["retHill"] / t["hill"] - 1, 4)
    if t["fairN"]:
        out["fairN"] = t["fairN"]; out["fair"] = round(t["fair"] / t["fairN"], 4)
        out["fairRate"] = round(t["fairLanded"] / t["fairN"], 4)
    return out


BANDS = (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01)
GAPS = ((-1.0, -0.10, "10+ under"), (-0.10, -0.05, "5-10 under"), (-0.05, 0.0, "0-5 under"),
        (0.0, 0.05, "0-5 over"), (0.05, 0.10, "5-10 over"), (0.10, 1.0, "10+ over"))


def gate(picks, seed=11, reps=2000):
    """The verdict on one rule's settled priced picks: [(day, landed or None,
    price block)]. See the module note."""
    priced = [(d, ok, v) for d, ok, v in picks if "o" in v]
    out = {"n": len(priced), "need": GATE_N}
    if not priced:
        out["verdict"] = "wait"; return out
    back = lambda ok, v: (1.0 if ok is None else ((v.get("b") or v["o"]) if ok else 0.0)) - 1.0
    pnl = [back(ok, v) for _, ok, v in priced]
    out["retBest"] = round(sum(pnl) / len(pnl), 4)
    fair = [(ok, v["f"]) for _, ok, v in priced if "f" in v and ok is not None]
    if fair:
        out["landed"] = round(sum(ok for ok, _ in fair) / len(fair), 4)
        out["fair"] = round(sum(f for _, f in fair) / len(fair), 4)
    by_day = {}
    for (d, _, _), x in zip(priced, pnl):
        by_day.setdefault(d, []).append(x)
    days = list(by_day.values())
    rng = random.Random(seed)
    bad = 0
    for _ in range(reps):
        s = n = 0
        for _ in days:
            xs = days[rng.randrange(len(days))]
            s += sum(xs); n += len(xs)
        bad += (s / n) <= 0
    out["pLoss"] = round(bad / reps, 3)
    # 23 Nov 2026: where the verdict comes from, said beside it and never
    # read by it (the gate stays as pre-registered): match days, the share
    # on the busiest three, each selection, and William Hill's own price.
    sizes = sorted((len(xs) for xs in days), reverse=True)
    out["days"] = len(days)
    out["top3"] = round(sum(sizes[:3]) / len(priced), 3)
    sel = {}
    for (_, ok, v), x in zip(priced, pnl):
        t = sel.setdefault(str(v.get("s")), {"n": 0, "landed": 0, "pnl": 0.0})
        t["n"] += 1; t["landed"] += bool(ok); t["pnl"] += x
    out["bySel"] = {k: {"n": t["n"], "landed": t["landed"], "retBest": round(t["pnl"] / t["n"], 4)}
                    for k, t in sorted(sel.items(), key=lambda kv: -kv[1]["n"])}
    hill = [(1.0 if ok is None else (v["h"] if ok else 0.0)) - 1.0 for _, ok, v in priced if v.get("h")]
    out["hill"] = {"n": len(hill), "ret": round(sum(hill) / len(hill), 4) if hill else None}
    if len(priced) < GATE_N:
        out["verdict"] = "wait"
    else:
        ok = out["retBest"] > 0 and out["pLoss"] <= GATE_P and fair and out["landed"] > out["fair"]
        out["verdict"] = "pass" if ok else "fail"
    return out


def record(here=HERE, now=None):
    now = now or datetime.now(timezone.utc)
    res = results(here)
    live = live_rows(here)
    graded_live, pending = [], 0
    for r in live:
        g = _result_for(r, res)
        if g: graded_live.append((r, g))
        elif (parse_utc(r.get("kickoff")) or now) < now: pending += 1
    skip = {(r["league"], r["home"], r["away"], g["date"]) for r, g in graded_live}
    graded_replay = [(r, g) for r in replay_rows(res, skip, here) for g in [_result_for(r, res, days=0)] if g]
    out = {"generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "rule": RULE, "book": BOOK,
           "gate": {"n": GATE_N, "pLoss": GATE_P, "edge": GATE_EDGE},
           "tests": 2 * len(MARKETS),   # rules read against the gate (value and all, each market)
           "live": {"fixtures": len(graded_live), "pending": pending,
                    "from": min((r["date"] for r, _ in graded_live), default=None),
                    "to": max((r["date"] for r, _ in graded_live), default=None)},
           "replay": {"fixtures": len(graded_replay),
                      "from": min((r["date"] for r, _ in graded_replay), default=None),
                      "to": max((r["date"] for r, _ in graded_replay), default=None)},
           "markets": {}}
    for mk in MARKETS:
        t_live, t_rep, t_all = _tally(), _tally(), _tally()
        bands = [_tally() for _ in BANDS[:-1]]
        gaps = [_tally() for _ in GAPS]
        rule_all, rule_value = [], []
        for src, rows in (("live", graded_live), ("replay", graded_replay)):
            for r, g in rows:
                v = (r.get("m") or {}).get(mk)
                if not v: continue
                ok = settle(mk, v["s"], g["result"][0], g["result"][1])
                _add(t_live if src == "live" else t_rep, v, ok)
                _add(t_all, v, ok)
                i = next(i for i in range(len(BANDS) - 1) if BANDS[i] <= v["p"] < BANDS[i + 1])
                _add(bands[i], v, ok)
                if src == "live" and "o" in v:
                    rule_all.append((r["date"], ok, v))
                    if "f" in v:
                        gap = v["p"] - v["f"]
                        _add(gaps[next((i for i, (lo, hi, _) in enumerate(GAPS) if lo <= gap < hi), len(GAPS) - 1)], v, ok)
                        if gap >= GATE_EDGE: rule_value.append((r["date"], ok, v))
        out["markets"][mk] = {
            "name": NAMES[mk], "live": _done(t_live), "replay": _done(t_rep), "all": _done(t_all),
            "bands": [{"from": BANDS[i], "to": min(BANDS[i + 1], 1.0), **_done(b)} for i, b in enumerate(bands) if b["n"] or b["void"]],
            "gaps": [{"gap": lab, **_done(t)} for (_, _, lab), t in zip(GAPS, gaps) if t["priced"]],
            "gate": {"value": gate(rule_value), "all": gate(rule_all)}}
    return out


def write_record(here=HERE, now=None):
    rec = record(here, now)
    with open(os.path.join(here, "markets-record.json"), "w") as f:
        json.dump(rec, f, separators=(",", ":"))
    return rec


def report(rec):
    lv, rp = rec["live"], rec["replay"]
    print(f"markets: {lv['fixtures']} live fixtures graded ({lv['pending']} awaiting a result), "
          f"{rp['fixtures']} replayed from the archive")
    print(f"  {'market':30} {'n':>6} {'landed':>7} {'model':>6} {'z':>6} {'priced':>6} {'best':>7} {'value rule':>18}")
    for mk, m in rec["markets"].items():
        a, l, gv = m["all"], m["live"], m["gate"]["value"]
        if not a.get("n"): continue
        verdict = gv["verdict"] if gv["verdict"] != "wait" else f"wait {gv['n']}/{gv['need']}"
        print(f"  {m['name']:30} {a['n']:6d} {a['rate']:7.1%} {a['quoted']:6.1%} {a.get('z', 0):+6.1f} "
              f"{l.get('priced', 0):6d} {('%+.1f%%' % (l['retBest'] * 100)) if 'retBest' in l else '-':>7} {verdict:>18}")
        if gv["verdict"] == "pass":
            print(f"::notice::markets: {m['name']} passed the value gate ({gv['n']} picks, {gv['retBest']:+.1%} at the best price, p(loss) {gv['pLoss']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()
    both = not (a.build or a.score)
    if a.build or both:
        log = []
        n, priced, path = build(fetch=not a.no_fetch, log=log)
        for line in log: print(f"  {line}")
        print(f"markets: {n} fixtures archived to {os.path.relpath(path, HERE) if path else 'nothing'}, {priced} with a price")
    if a.score or both:
        report(write_record())


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()
