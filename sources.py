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
from datetime import datetime, date, timedelta

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
    "en.5":  ["england/master/{s}/5-nationalleague.txt"],
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

    # Cup schedules. openfootball's naming for these has never been consistent,
    # so each competition lists every path it has used. None resolve for
    # 2026/27 yet; the first one that does switches the competition on.
    "en.fa":  ["england/master/{s}/cup.txt", "england/master/{s}/facup.txt",
               "england/master/{s}/5-facup.txt", "europe/master/england/{s}_engfacup.txt"],
    "en.lc":  ["england/master/{s}/leaguecup.txt", "england/master/{s}/6-leaguecup.txt",
               "europe/master/england/{s}_engleaguecup.txt"],
    "es.cup": ["espana/master/{s}/cup.txt", "europe/master/spain/{s}_escup.txt"],
    "de.cup": ["deutschland/master/{s}/cup.txt", "europe/master/germany/{s}_decup.txt"],
    "it.cup": ["italy/master/{s}/cup.txt", "europe/master/italy/{s}_itcup.txt"],
    # UEFA competitions live in their own repo, with the qualifying rounds in
    # separate files from the main draw. Qualifiers run through August, so they
    # are listed first: they are the ties actually being played right now.
    "eu.clq": ["champions-league/master/{s}/clq.txt"],
    "eu.cl":  ["champions-league/master/{s}/cl.txt"],
    "eu.elq": ["champions-league/master/{s}/elq.txt"],
    "eu.el":  ["champions-league/master/{s}/el.txt"],
    "eu.ecq": ["champions-league/master/{s}/confq.txt"],
    "eu.ec":  ["champions-league/master/{s}/conf.txt"],

    # rating-source leagues (history only)
    "nor.1": ["europe/master/norway/{s}_no1.txt"],
    "cze.1": ["europe/master/czech-republic/{s}_cz1.txt"],
    "pol.1": ["europe/master/poland/{s}_pl1.txt"],
    "dnk.1": ["europe/master/denmark/{s}_dk1.txt"],
    "swe.1": ["europe/master/sweden/{s}_se1.txt"],
    "ukr.1": ["europe/master/ukraine/{s}_ua1.txt"],
    "srb.1": ["europe/master/serbia/{s}_rs1.txt"],
    "hrv.1": ["europe/master/croatia/{s}_hr1.txt"],
    "rou.1": ["europe/master/romania/{s}_ro1.txt"],
    "cyp.1": ["europe/master/cyprus/{s}_cy1.txt"],
    "hun.1": ["europe/master/hungary/{s}_hu1.txt"],
    "bgr.1": ["europe/master/bulgaria/{s}_bg1.txt"],
    "svk.1": ["europe/master/slovakia/{s}_sk1.txt"],
    "svn.1": ["europe/master/slovenia/{s}_si1.txt"],
    "isr.1": ["europe/master/israel/{s}_il1.txt"],
    "fin.1": ["europe/master/finland/{s}_fi1.txt"],
    "irl.1": ["europe/master/ireland/{s}_ie1.txt"],
    "isl.1": ["europe/master/iceland/{s}_is1.txt"],
    "bih.1": ["europe/master/bosnia-herzegovina/{s}_ba1.txt"],
    "alb.1": ["europe/master/albania/{s}_al1.txt"],
    "arm.1": ["europe/master/armenia/{s}_am1.txt"],
    "geo.1": ["europe/master/georgia/{s}_ge1.txt"],
    "ltu.1": ["europe/master/lithuania/{s}_lt1.txt"],
    "lva.1": ["europe/master/latvia/{s}_lv1.txt"],
    "est.1": ["europe/master/estonia/{s}_ee1.txt"],
    "mkd.1": ["europe/master/north-macedonia/{s}_mk1.txt"],
    "mne.1": ["europe/master/montenegro/{s}_me1.txt"],
    "aze.1": ["europe/master/azerbaijan/{s}_az1.txt"],
    "blr.1": ["europe/master/belarus/{s}_by1.txt"],
    "mda.1": ["europe/master/moldova/{s}_md1.txt"],
    "nir.1": ["europe/master/northern-ireland/{s}_nir1.txt"],
    "wal.1": ["europe/master/wales/{s}_wal1.txt"],
    "fro.1": ["europe/master/faroe-islands/{s}_fo1.txt"],
    "lux.1": ["europe/master/luxembourg/{s}_lu1.txt"],
    "mlt.1": ["europe/master/malta/{s}_mt1.txt"],
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
    """Return (matches, ok). matches: list of (date, home, away, hg, ag).

    Tries football.json first, then falls back to parsing results out of the
    plain-text schedule. The smaller European leagues exist only as text, and
    those files carry completed scores alongside future fixtures, so the same
    parser serves both purposes.
    """
    url = f"{RAW}/football.json/master/{season}/{code}.json"
    try:
        doc = json.loads(_get(url, cache_dir))
    except Exception:
        rows, ok = fetch_fixtures(code, season, cache_dir)
        played = [(r["date"], r["home"], r["away"], r["hg"], r["ag"])
                  for r in rows if r["hg"] is not None] if ok else []
        return (played, True) if played else ([], False)
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
            try:
                cur_date = date(y or 1900, mon, day)
            except ValueError:
                # A malformed date line should skip that line, not abort the
                # whole competition. openfootball has occasional typos.
                continue
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
        # season=None means the competition is a rating source only: pull its
        # history so its clubs can be priced in Europe, but never its fixtures.
        if season is not None:
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


# ---------------------------------------------------------------------------
# Live fallback: ESPN's public scoreboard
#
# openfootball is volunteer-maintained and its European coverage lags badly:
# as of this build the champions-league repo stops at 2025/26, so no UEFA
# fixture exists there for the current season even though the ties are being
# played. ESPN publishes a public scoreboard endpoint that needs no key and
# covers every competition below.
#
# This runs only when openfootball has nothing for a competition, so the public
# domain source stays primary and ESPN is the gap-filler.
#
# NOTE: this could not be exercised in the environment it was written in, which
# could only reach github.com. It is written to fail closed — any error, any
# unexpected shape, and it returns nothing and the competition simply does not
# appear, exactly as it does today.
# ---------------------------------------------------------------------------

# Two hosts serving the same payload. site.api is the usual one; site.web.api
# is what espn.com itself calls and sometimes answers when the other refuses.
ESPN_HOSTS = ["https://site.api.espn.com", "https://site.web.api.espn.com"]
ESPN_PATH = "/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={d}&limit=400"

# Requests are made one date at a time. A range ("20260827-20260831") is
# accepted by some competitions and silently ignored by others, which is how a
# whole week of fixtures went missing without a single error being raised.
# Single dates are the form ESPN's own site uses and the only one that behaves
# consistently across every slug.

ESPN_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.espn.com/soccer/scoreboard",
    "Origin": "https://www.espn.com",
}

# Several slugs per competition, tried in order. ESPN splits qualifying rounds
# onto their own slug, and does not always open a new season on the main slug
# until the league phase starts, so the qualifying slug is the one carrying
# August ties.
ESPN_SLUGS = {
    "en.1": ["eng.1"], "en.2": ["eng.2"], "en.3": ["eng.3"], "en.4": ["eng.4"],
    "en.5": ["eng.5"],
    "en.fa": ["eng.fa"], "en.lc": ["eng.league_cup"],
    "es.1": ["esp.1"], "es.2": ["esp.2"], "es.cup": ["esp.copa_del_rey"],
    "de.1": ["ger.1"], "de.2": ["ger.2"], "de.cup": ["ger.dfb_pokal"],
    "it.1": ["ita.1"], "it.2": ["ita.2"], "it.cup": ["ita.coppa_italia"],
    "fr.1": ["fra.1"], "fr.2": ["fra.2"],
    "nl.1": ["ned.1"], "pt.1": ["por.1"], "be.1": ["bel.1"], "tr.1": ["tur.1"],
    "at.1": ["aut.1"], "gr.1": ["gre.1"], "sco.1": ["sco.1"], "br.1": ["bra.1"],
    # One slug each. Letting the main competition fall back to the qualifying
    # slug meant the same tie was fetched twice under two codes and rendered as
    # a duplicate row.
    "eu.cl":  ["uefa.champions"],
    "eu.clq": ["uefa.champions_qual"],
    "eu.el":  ["uefa.europa"],
    "eu.elq": ["uefa.europa_qual"],
    "eu.ec":  ["uefa.europa.conf"],
    "eu.ecq": ["uefa.europa.conf_qual"],
}


def _espn_day(slug, day, timeout, errs):
    """One competition, one date. Returns a list of raw event dicts."""
    d = day.strftime("%Y%m%d")
    last = None
    for host in ESPN_HOSTS:
        url = host + ESPN_PATH.format(slug=slug, d=d)
        try:
            req = urllib.request.Request(url, headers=ESPN_HEADERS)
            return json.loads(urllib.request.urlopen(req, timeout=timeout).read()).get("events") or []
        except Exception as e:
            last = f"{type(e).__name__} {e}"
    if last:
        errs.append(f"{slug} {d}: {last}")
    return []


def _row(ev):
    """One ESPN event -> the same row shape parse_fixture_txt produces."""
    comp = (ev.get("competitions") or [{}])[0]
    sides = comp.get("competitors") or []
    home = next((c for c in sides if c.get("homeAway") == "home"), None)
    away = next((c for c in sides if c.get("homeAway") == "away"), None)
    if not home or not away:
        return None
    iso = comp.get("date") or ev.get("date") or ""
    if len(iso) < 10:
        return None
    done = bool(((comp.get("status") or {}).get("type") or {}).get("completed"))
    hg = ag = None
    if done:
        try:
            hg, ag = int(home.get("score")), int(away.get("score"))
        except (TypeError, ValueError):
            hg = ag = None
    return {
        "date": iso[:10],
        "time": iso[11:16] if len(iso) >= 16 else None,
        "round": (ev.get("season") or {}).get("slug"),
        "home": clean_name((home.get("team") or {}).get("displayName") or ""),
        "away": clean_name((away.get("team") or {}).get("displayName") or ""),
        "hg": hg, "ag": ag,
    }


def fetch_espn(code, start, end, timeout=25, log=None):
    """Fixtures for one competition across a date range, queried day by day.

    Returns the same row shape as parse_fixture_txt so callers cannot tell the
    difference. Failures are reported through `log` rather than swallowed: a
    blocked request and an empty competition are different problems and must
    not look identical.
    """
    slugs = ESPN_SLUGS.get(code)
    if not slugs:
        return [], False
    days = []
    d = start
    while d <= end:
        days.append(d)
        d += timedelta(days=1)

    for slug in slugs:
        rows, errs, seen = [], [], set()
        for day in days:
            for ev in _espn_day(slug, day, timeout, errs):
                r = _row(ev)
                if not r:
                    continue
                key = (r["date"], r["home"], r["away"])
                if key not in seen:
                    seen.add(key)
                    rows.append(r)
        inwin = [r for r in rows if start.isoformat() <= r["date"] <= end.isoformat()]
        if log is not None:
            note = f"  ERROR {errs[0]}" if errs else ""
            log.append(f"{code}/{slug}: {len(rows)} returned, {len(inwin)} in window{note}")
        if inwin:
            return inwin, True
    return [], False


# --- reconciling ESPN's club names with openfootball's ---------------------

def _norm(n):
    n = clean_name(n).lower()
    for a, b in (("&", "and"), ("-", " "), (".", ""), ("'", ""), ("ø", "o"), ("ë", "e"),
                 ("ł", "l"), ("ż", "z"), ("ą", "a"), ("ę", "e"), ("š", "s"), ("ž", "z"),
                 ("č", "c"), ("ș", "s"), ("ț", "t"), ("ă", "a"), ("â", "a"), ("î", "i"),
                 ("å", "a"), ("æ", "ae"), ("ğ", "g"), ("ı", "i"), ("ş", "s"),
                 ("é", "e"), ("ü", "u"), ("ö", "o"), ("ä", "a"), ("á", "a"),
                 ("í", "i"), ("ó", "o"), ("ú", "u"), ("ç", "c"), ("ñ", "n")):
        n = n.replace(a, b)
    drop = {"fc", "cf", "afc", "sc", "ac", "as", "ss", "us", "cd", "ud", "rc",
            "sd", "ca", "sv", "tsg", "vfl", "vfb", "bv", "sk", "nk", "hnk",
            "the", "club", "de", "futbol", "calcio"}
    return " ".join(w for w in n.split() if w not in drop).strip()


# ESPN abbreviates; openfootball spells out. Normalisation cannot bridge
# "Man City" to "Manchester City" or "Spurs" to "Tottenham Hotspur", so the
# common cases are listed explicitly. Extend this as mismatches show up on the
# site as "not rated" rows.
ALIASES = {
    "man city": "manchester city", "man utd": "manchester united",
    "man united": "manchester united", "spurs": "tottenham hotspur",
    "wolves": "wolverhampton wanderers", "nottm forest": "nottingham forest",
    "brighton": "brighton and hove albion", "leicester": "leicester city",
    "newcastle": "newcastle united", "west ham": "west ham united",
    "leeds": "leeds united", "west brom": "west bromwich albion",
    "sheff utd": "sheffield united", "sheff wed": "sheffield wednesday",
    "bayern munich": "bayern munchen", "borussia mgladbach": "borussia monchengladbach",
    "monchengladbach": "borussia monchengladbach", "dortmund": "borussia dortmund",
    "leverkusen": "bayer leverkusen", "eintracht frankfurt": "eintracht frankfurt",
    "inter milan": "internazionale milano", "inter": "internazionale milano",
    "ac milan": "milan", "roma": "roma", "atletico madrid": "atletico madrid",
    "atleti": "atletico madrid", "athletic club": "athletic club",
    "real sociedad": "real sociedad", "psg": "paris saint germain",
    "paris sg": "paris saint germain", "marseille": "olympique marseille",
    "lyon": "olympique lyonnais", "psv eindhoven": "psv",
    "ajax": "ajax", "sporting cp": "sporting", "sporting lisbon": "sporting",
    "porto": "porto", "benfica": "benfica",
}


def match_team(name, pool):
    """Map an ESPN club name onto a rated team, or None.

    Deliberately conservative: an exact normalised match, then a containment
    match, and nothing cleverer. A wrong match would silently price a fixture
    with another club's rating, which is far worse than leaving it unrated —
    an unrated fixture says so on the page, a mismatched one lies quietly.
    """
    if name in pool:
        return name
    target = _norm(name)
    target = ALIASES.get(target, target)
    if not target:
        return None
    norm = {}
    for t in pool:
        norm.setdefault(_norm(t), t)
        alias = ALIASES.get(_norm(t))
        if alias:
            norm.setdefault(alias, t)
    if target in norm:
        return norm[target]
    hits = [v for k, v in norm.items()
            if (target in k or k in target) and min(len(k), len(target)) >= 4]
    return hits[0] if len(hits) == 1 else None
