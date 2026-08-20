"""
Data sources.

Primary source is openfootball (github.com/openfootball) which is public domain,
needs no key, and has no rate limit worth worrying about. Two shapes are used:

  football.json/<season>/<code>.json    completed seasons, with scores
  <country>/<season>/<n>-<league>.txt   current-season fixture lists

A live source (football-data.org or API-Football) should be layered on top for
same-day results and kick-off changes; see README. The parsers below normalise
everything into one shape so a second source only needs its own reader.
"""
import json, os, re, urllib.request, concurrent.futures
from datetime import datetime, date

RAW = "https://raw.githubusercontent.com/openfootball"
MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

# code -> list of candidate paths for the current-season fixture list, tried in
# order. openfootball is volunteer-maintained and its layout is not uniform:
# England/Spain/Italy/Germany each have their own repo with a <season>/ folder,
# while France, the Netherlands and Portugal live inside a shared `europe` repo
# under a <season>_<code>.txt naming scheme. Hence a candidate list per league
# rather than one rule.
FIXTURE_FILES = {
    "en.1":  ["england/master/{s}/1-premierleague.txt"],
    "en.2":  ["england/master/{s}/2-championship.txt"],
    "en.3":  ["england/master/{s}/3-league1.txt"],
    "en.4":  ["england/master/{s}/4-league2.txt"],
    "es.1":  ["espana/master/{s}/1-liga.txt"],
    "es.2":  ["espana/master/{s}/2-liga2.txt"],
    "de.1":  ["deutschland/master/{s}/1-bundesliga.txt"],
    "de.2":  ["deutschland/master/{s}/2-bundesliga2.txt"],
    "it.1":  ["italy/master/{s}/1-seriea.txt"],
    "it.2":  ["italy/master/{s}/2-serieb.txt"],
    "fr.1":  ["europe/master/france/{s}_fr1.txt", "france/master/{s}/1-ligue1.txt"],
    "fr.2":  ["europe/master/france/{s}_fr2.txt"],
    "nl.1":  ["europe/master/netherlands/{s}_nl1.txt"],
    "pt.1":  ["europe/master/portugal/{s}_pt1.txt"],
    "be.1":  ["belgium/master/{s}/be1.txt", "europe/master/belgium/{s}_be1.txt"],
    "sco.1": ["europe/master/scotland/{s}_sco1.txt", "scotland/master/{s}/1-premiership.txt"],
    "at.1":  ["europe/master/austria/{s}_at1.txt", "austria/master/{s}/1-bundesliga.txt"],
    "gr.1":  ["europe/master/greece/{s}_gr1.txt"],
    "tr.1":  ["europe/master/turkey/{s}_tr1.txt"],
    "br.1":  ["south-america/master/brazil/{s}_br1.txt"],
}

# Status markers the schedules append to a side: [postponed], [awarded], etc.
ANNOTATION = re.compile(r"\s*\[[^\]]*\]\s*$")

SUFFIXES = re.compile(
    r"\s+(FC|AFC|CF|SC|AC|BSC|VfL|VfB|TSG|SV|FSV|SpVgg|BV|SK|CD|UD|RCD|RC|SD|"
    r"US|SS|ASD|AS|OGC|RC|CA|NK|HNK|GNK)$", re.I)


def _get(url, cache_dir=None, timeout=30):
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        p = os.path.join(cache_dir, re.sub(r"[^a-zA-Z0-9._-]", "_", url)[-120:])
        if os.path.exists(p):
            return open(p, "rb").read()
    data = urllib.request.urlopen(url, timeout=timeout).read()
    if cache_dir:
        open(p, "wb").write(data)
    return data


def clean_name(n):
    """Trim status markers and club-type suffixes so 'Arsenal FC' and 'Arsenal' are one team.
    Applied consistently to both sources, so any residual mismatch shows up as
    a team with zero matches rather than a silently wrong rating."""
    n = ANNOTATION.sub("", n.strip()).strip()
    prev = None
    while prev != n:
        prev = n
        n = SUFFIXES.sub("", n).strip()
    return n


# --- completed seasons ------------------------------------------------------

def fetch_season(code, season, cache_dir=None):
    """Return (matches, ok). matches: list of (date, home, away, hg, ag)."""
    url = f"{RAW}/football.json/master/{season}/{code}.json"
    try:
        doc = json.loads(_get(url, cache_dir))
    except Exception:
        return [], False
    out = []
    for m in doc.get("matches", []):
        ft = _full_time(m)
        if ft is None:
            continue
        out.append((m.get("date", ""), clean_name(m["team1"]),
                    clean_name(m["team2"]), ft[0], ft[1]))
    return out, True


def _full_time(m):
    """openfootball has used three shapes for the score over the years:
    {"score": {"ft": [h, a]}}, {"score": [h, a]}, and {"score1": h, "score2": a}.
    Accept all three rather than silently dropping a season's worth of results."""
    sc = m.get("score")
    if isinstance(sc, dict):
        ft = sc.get("ft")
        if isinstance(ft, (list, tuple)) and len(ft) == 2:
            return int(ft[0]), int(ft[1])
    if isinstance(sc, (list, tuple)) and len(sc) == 2:
        return int(sc[0]), int(sc[1])
    if m.get("score1") is not None and m.get("score2") is not None:
        return int(m["score1"]), int(m["score2"])
    return None


# --- current season fixture lists ------------------------------------------

_DATE = re.compile(r"^\s{2,6}(?:\w{3}\s+)?(\w{3})\s+(\d{1,2})(?:\s+(\d{4}))?\s*$")
_ROUND = re.compile(r"^\s*[▪•]\s*(.+?)\s*$")
# One space is enough before the separator: these files pad the home column to a
# fixed width, so the longest club name in a division ("Brighton & Hove Albion
# FC") gets a single space and a \s{2,} rule drops all nineteen of its fixtures.
_MATCH = re.compile(
    r"^\s{2,8}(?:(\d{1,2}:\d{2})\s+)?(.+?)\s+(?:v|vs)\s+(.+?)\s*$")
_PLAYED = re.compile(
    r"^\s{2,8}(?:(\d{1,2}:\d{2})\s+)?(.+?)\s{2,}(\d+)-(\d+).*?\s{2,}(.+?)\s*$")
# openfootball uses two result layouts. Most repos put the score between the
# sides ("Liverpool  4-2 (1-0)  Bournemouth"); the South American repo appends
# it after the away side ("CA Mineiro  v SE Palmeiras  2-2 (1-1)"). Without this
# the score is silently absorbed into the away team's name and every played
# match is read as a future fixture.
_TRAILING = re.compile(r"^(.+?)\s{2,}(\d+)\s*-\s*(\d+)(?:\s*\(\s*\d+\s*-\s*\d+\s*\))?\s*$")


def parse_fixture_txt(text):
    """Parse an openfootball .txt schedule.

    Handles the two quirks of the format: the date line is only printed when it
    changes, and the kick-off time is only printed when it changes within a day.
    """
    rows, cur_date, cur_time, cur_round, year = [], None, None, None, None
    for line in text.splitlines():
        if not line.strip() or line.startswith(("=", "#")):
            continue
        mr = _ROUND.match(line)
        if mr and not re.search(r"\d{1,2}:\d{2}", line):
            cur_round = mr.group(1)
            continue
        md = _DATE.match(line)
        if md and md.group(1) in MONTHS:
            if md.group(3):
                year = int(md.group(3))
            mon, day = MONTHS[md.group(1)], int(md.group(2))
            # season rolls over the new year: Aug-Dec then Jan-May
            y = year
            if cur_date and mon < cur_date.month and year:
                y = year + 1
                year = y
            cur_date = date(y or 1900, mon, day)
            cur_time = None
            continue
        mp = _PLAYED.match(line)
        if mp and cur_date:
            if mp.group(1):
                cur_time = mp.group(1)
            rows.append({"date": cur_date.isoformat(), "time": cur_time,
                         "round": cur_round, "home": clean_name(mp.group(2)),
                         "away": clean_name(mp.group(5)),
                         "hg": int(mp.group(3)), "ag": int(mp.group(4))})
            continue
        mm = _MATCH.match(line)
        if mm and cur_date and " v " in line.replace(" vs ", " v "):
            if mm.group(1):
                cur_time = mm.group(1)
            away, hg, ag = mm.group(3), None, None
            mt = _TRAILING.match(away)
            if mt:
                away, hg, ag = mt.group(1), int(mt.group(2)), int(mt.group(3))
            rows.append({"date": cur_date.isoformat(), "time": cur_time,
                         "round": cur_round, "home": clean_name(mm.group(2)),
                         "away": clean_name(away), "hg": hg, "ag": ag})
    return rows


def fetch_fixtures(code, season, cache_dir=None):
    for path in FIXTURE_FILES.get(code, []):
        try:
            txt = _get(f"{RAW}/{path.format(s=season)}", cache_dir).decode("utf-8", "replace")
        except Exception:
            continue
        rows = parse_fixture_txt(txt)
        if rows:
            return rows, True
    return [], False


def fetch_all_seasons(plan, cache_dir=None, workers=10):
    """plan: {code: (current_season, [prev_seasons])}. Leagues run on different
    calendars, so each one carries its own season strings."""
    jobs = []
    for c, (season, prevs) in plan.items():
        for s in prevs:
            jobs.append(("hist", c, s))
        jobs.append(("fix", c, season))

    def run(j):
        kind, c, s = j
        if kind == "hist":
            m, ok = fetch_season(c, s, cache_dir)
            return ("hist", c, s, m, ok)
        m, ok = fetch_fixtures(c, s, cache_dir)
        return ("fix", c, s, m, ok)

    history, fixtures, missing = {}, {}, []
    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        for kind, c, s, m, ok in ex.map(run, jobs):
            if not ok or not m:
                missing.append(f"{c} {s} ({kind})")
                continue
            if kind == "hist":
                history.setdefault(c, {})[s] = m
            else:
                fixtures[c] = m
    return history, fixtures, missing


def fetch_all(codes, season, prev_seasons, cache_dir=None, workers=10):
    """Pull everything in parallel. Returns (history, fixtures, missing)."""
    jobs = []
    for c in codes:
        for s in prev_seasons:
            jobs.append(("hist", c, s))
        jobs.append(("fix", c, season))

    def run(j):
        kind, c, s = j
        if kind == "hist":
            m, ok = fetch_season(c, s, cache_dir)
            return ("hist", c, s, m, ok)
        m, ok = fetch_fixtures(c, s, cache_dir)
        return ("fix", c, s, m, ok)

    history, fixtures, missing = {}, {}, []
    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        for kind, c, s, m, ok in ex.map(run, jobs):
            if not ok or not m:
                missing.append(f"{c} {s} ({kind})")
                continue
            if kind == "hist":
                history.setdefault(c, {})[s] = m
            else:
                fixtures[c] = m
    return history, fixtures, missing
