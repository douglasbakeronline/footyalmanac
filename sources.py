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

HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history")


def local_history(code, season):
    """A completed season cached in the repository by backfill.py.

    The competitions openfootball has never carried have no other way to get a
    prior season, and without one every side is unrated and the confidence
    number is a placeholder. Walking the live scoreboard for a whole season is
    three hundred requests, which is fine to do once and unacceptable to do
    every morning, so the result is committed.
    """
    path = os.path.join(HISTORY_DIR, f"{code}-{season}.json")
    if not os.path.exists(path):
        return [], False
    try:
        rows = json.load(open(path))
    except Exception:
        return [], False
    out = [(r["date"], clean_name(r["home"]), clean_name(r["away"]), r["hg"], r["ag"])
           for r in rows if r.get("hg") is not None]
    return (out, True) if out else ([], False)


def fetch_season(code, season, cache_dir=None):
    """Return (matches, ok). matches: list of (date, home, away, hg, ag).

    Order is: the local backfill, then openfootball's football.json, then
    openfootball's plain-text schedule. The local file comes first because a
    competition that has one is a competition openfootball does not carry, and
    going out to the network to be told so is pure latency.
    """
    rows, ok = local_history(code, season)
    if ok:
        return rows, True

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

    # ---- competitions that exist ONLY here ------------------------------
    # openfootball publishes no schedule for any of these, so the slug is the
    # whole source: fixtures, results, and the past season backfill.py walks to
    # produce their ratings.
    #
    # These slugs are unverified. They follow ESPN's published naming, but the
    # environment they were written in cannot reach ESPN, so any of them could
    # be wrong. A wrong slug returns nothing and the competition silently does
    # not appear, which is the safe failure. Run `python3 backfill.py --probe`
    # somewhere with network access to find out which ones answer, and delete
    # the rest.
    "us.1": ["usa.1"], "us.2": ["usa.usl.1"], "mx.1": ["mex.1"],
    "ar.1": ["arg.1"], "br.2": ["bra.2"], "co.1": ["col.1"], "cl.1": ["chi.1"],
    "uy.1": ["uru.1"], "pe.1": ["per.1"], "ec.1": ["ecu.1"],
    "sa.lib": ["conmebol.libertadores"], "sa.sud": ["conmebol.sudamericana"],
    "na.ccc": ["concacaf.champions_cup", "concacaf.champions"],
    "jp.1": ["jpn.1"], "kr.1": ["kor.1"], "cn.1": ["chn.1"], "au.1": ["aus.1"],
    "sa.1": ["ksa.1"], "ae.1": ["uae.1"], "in.1": ["ind.1"],
    "ch.1": ["sui.1"], "ru.1": ["rus.1"], "pt.2": ["por.2"], "nl.2": ["ned.2"],
    "de.3": ["ger.3"], "sco.2": ["sco.2"],

    # The European leagues that used to be ratings-only. They already carry
    # history from openfootball, so a working slug here adds their fixtures
    # without needing a backfill at all.
    "nor.1": ["nor.1"], "swe.1": ["swe.1"], "dnk.1": ["den.1"], "fin.1": ["fin.1"],
    "isl.1": ["isl.1"], "irl.1": ["irl.1"], "cze.1": ["cze.1"], "pol.1": ["pol.1"],
    "ukr.1": ["ukr.1"], "srb.1": ["srb.1"], "hrv.1": ["cro.1"], "rou.1": ["rou.1"],
    "cyp.1": ["cyp.1"], "hun.1": ["hun.1"], "bgr.1": ["bul.1"], "svk.1": ["svk.1"],
    "svn.1": ["slv.1"], "isr.1": ["isr.1"], "bih.1": ["bih.1"], "alb.1": ["alb.1"],
    "arm.1": ["arm.1"], "geo.1": ["geo.1"], "ltu.1": ["ltu.1"], "lva.1": ["lva.1"],
    "est.1": ["est.1"], "mkd.1": ["mkd.1"], "mne.1": ["mne.1"], "aze.1": ["aze.1"],
    "blr.1": ["blr.1"], "mda.1": ["mda.1"], "nir.1": ["nir.1"], "wal.1": ["wal.1"],
    "fro.1": ["fro.1"], "lux.1": ["lux.1"], "mlt.1": ["mlt.1"],
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

# English exonyms against the local spellings openfootball uses. This is a whole
# class of failure rather than a handful of clubs: the live source says Prague,
# Cologne, Milan, Warsaw, Belgrade, the schedules say Praha, Köln, Milano,
# Warszawa, Beograd, and no amount of normalising letters bridges the two.
# Applied to the city token, so it fixes every club in that city at once rather
# than one alias per club.
CITIES = {
    "prague": "praha", "cologne": "koln", "munich": "munchen",
    "milan": "milano", "turin": "torino", "florence": "firenze",
    "genoa": "genova", "naples": "napoli", "rome": "roma",
    "seville": "sevilla", "lisbon": "lisboa", "warsaw": "warszawa",
    "moscow": "moskva", "athens": "athina", "copenhagen": "kobenhavn",
    "gothenburg": "goteborg", "vienna": "wien", "belgrade": "beograd",
    "bucharest": "bucuresti", "zurich": "zurich", "brussels": "brussel",
    "antwerp": "antwerpen", "the hague": "den haag", "hague": "den haag",
    "salonika": "thessaloniki", "nicosia": "lefkosia", "kiev": "kyiv",
    "bruges": "brugge", "ghent": "gent", "eindhoven": "eindhoven",
}


def _base(n):
    """Letters and generic words only. Deliberately stops before the city map
    and the alias table, because both of those have to be applied in a
    particular order and doing it inside here got them the wrong way round."""
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


def _nonum(norm):
    """The same name with bare numbers taken out.

    A number in a club name is nearly always a founding year, and only one of
    the two sources tends to carry it: openfootball says "Bayer 04 Leverkusen"
    where the live source says "Bayer Leverkusen", and containment cannot see
    through a token wedged into the middle of the name.

    Nearly always, though, is not always — CSKA Sofia and CSKA 1948 Sofia are
    two different clubs in the same city, and the year is the only thing
    telling them apart. So this is a last resort in match_team rather than part
    of the comparable form, and it still has to come back with exactly one
    candidate before anything is matched.
    """
    words = [w for w in norm.split() if not w.isdigit()]
    return " ".join(words) if words else norm


def _norm(n):
    """The comparable form of a club name.

    Aliases resolve first and the city map second. The other way round,
    "Inter Milan" becomes "inter milano" before the alias table gets a look at
    it, the alias for "inter milan" never fires, and the name goes on to be
    matched against whatever else is in Milan.
    """
    b = _base(n)
    b = ALIASES.get(b, b)
    return " ".join(CITIES.get(w, w) for w in b.split())


# A candidate whose whole name reduces to a city and nothing else cannot
# identify a club: every side in that city contains it. Matching "Inter Milan"
# against a candidate that has reduced to "milano" returned AC Milan, which is
# the exact failure the conservative matching here exists to prevent, and it
# would have priced the fixture with another club's rating and said nothing.
def _bare_place(norm):
    toks = set(norm.split())
    return bool(toks) and toks <= set(CITIES.values())


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
    "ajax": "ajax", "porto": "porto", "benfica": "benfica",
    # Sporting has to name the city. Mapping it to a bare "sporting" made it
    # ambiguous between Lisbon and Braga, the matcher correctly refused to
    # guess, and every Sporting tie in Europe rendered as a club with no
    # rating on file.
    "sporting cp": "sporting clube portugal",
    "sporting lisbon": "sporting clube portugal",
    "sporting braga": "sporting clube braga",
    "braga": "sporting clube braga",
}


def match_team(name, pool):
    """Map a live-source club name onto a rated team, or None.

    Deliberately conservative: an exact normalised match, then a containment
    match with two guards, and nothing cleverer. A wrong match would silently
    price a fixture with another club's rating, which is far worse than leaving
    it unrated — an unrated fixture says so on the page, a mismatched one lies
    quietly.
    """
    if name in pool:
        return name
    target = _norm(name)
    if not target:
        return None

    norm = {}
    for t in pool:
        norm.setdefault(_norm(t), t)
    if target in norm:
        return norm[target]

    hits = [(k, v) for k, v in norm.items()
            if (target in k or k in target) and min(len(k), len(target)) >= 4
            # guard one: a candidate that is only a city name identifies nobody
            and not _bare_place(k)]
    # guard two: more than one candidate means the name is ambiguous, and a
    # guess here is a silently wrong rating rather than a visible gap
    if len(hits) == 1:
        return hits[0][1]
    if hits:
        return None

    # Last resort: try again with founding years taken out of both sides. Both
    # guards still apply, so a name that only a year separates from another
    # club comes back unmatched rather than wrong.
    bare = _nonum(target)
    hits = [(k, v) for k, v in ((_nonum(k), v) for k, v in norm.items())
            if (bare in k or k in bare) and min(len(k), len(bare)) >= 4
            and not _bare_place(k)]
    hits = {v for _, v in hits}
    return next(iter(hits)) if len(hits) == 1 else None
