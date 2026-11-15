#!/usr/bin/env python3
"""
World rankings as a model input: FIFA for international football, ATP for
men's tennis. WTA rankings are shown but not used (they did not pass).

    python3 rankings.py            refresh fifa-rankings.json and print the top of each

Tested 28 Sep 2026, fit on 2025, judged on 2026, paired bootstrap, tune.py
gates, the honesty guard (quoted vs landed at 65%+ may not widen):

  FIFA points gap, international win picks, on top of the international
  ratings (refitted quarterly in the test so the ranking had no freshness
  advantage): -0.0361 log loss, p(worse) 0.00; top 20% of calls 80.9% ->
  84.3% landed. The largest single gain any signal has shown on this site.
  ATP ranking gap (log ratio, ranks capped at 151 because the live feed
  lists the top 150), on top of Elo: -0.0037, p(worse) 0.03.
  WTA ranking gap, same form: -0.0004, p(worse) 0.30. Failed the gain gate.

Both adjust only the probability of the pick landing, the quantity the test
measured: p' = sigmoid(w0 + w1 * logit(p) + w2 * gap [+ w3]). A fixture
where either side has no ranking (non-FIFA members such as Martinique, a
player outside the ATP top 150 whose rival is also outside it) keeps its
unadjusted number.

Sources: FIFA's own ranking API (inside.fifa.com, by release id; history in
the repo as fifa-rankings.json, refreshed when a new release appears), and
ESPN's tennis rankings (top 150 by athlete id). Standard library only.
"""
import concurrent.futures as cf, json, math, os, re, sys, urllib.request
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FIFA_FILE = os.path.join(HERE, "fifa-rankings.json")
# 15 Nov 2026: no release after id 15175 (20 Jul) was found from August to
# November, with every fetch answering (no failure logged), while FIFA kept
# publishing (an October 2026 release is on inside.fifa.com). The site moved
# to /fifa-rankings/world-ranking/ and its API's URLs now carry
# rankingType=football (seen on a public id15136 URL); the ids after 15175
# look to be answered only with it. Each URL is tried with it first and
# without it second, so the old form still works if it ever answers again.
FIFA_URL = "https://inside.fifa.com/api/ranking-overview?locale=en&rankingType=football&dateId=id{}"
FIFA_URLS = (FIFA_URL, "https://inside.fifa.com/api/ranking-overview?locale=en&dateId=id{}")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "application/json"}

# The fitted adjustments (see the module docstring for the evidence).
FIFA_W = [0.3868, 0.8101, 0.2634, -0.5658]   # intercept, logit(p), points gap / 100, both ranked
ATP_W = [-0.1207, 0.8557, 0.1985]            # intercept, logit(p), log(rank opp / rank fav)
ATP_CAP = 151

# The site's (martj42 / ESPN) spelling -> FIFA's.
FIFA_NAMES = {
    "United States": "USA", "South Korea": "Korea Republic", "North Korea": "DPR Korea",
    "Iran": "IR Iran", "China": "China PR", "Ivory Coast": "Côte d'Ivoire",
    "Czech Republic": "Czechia", "Turkey": "Türkiye", "Cape Verde": "Cabo Verde",
    "DR Congo": "Congo DR", "Kyrgyzstan": "Kyrgyz Republic", "Brunei": "Brunei Darussalam",
    "Taiwan": "Chinese Taipei", "Saint Kitts and Nevis": "St Kitts and Nevis",
    "Saint Lucia": "St Lucia", "Saint Vincent and the Grenadines": "St Vincent and the Grenadines",
    "Hong Kong": "Hong Kong, China", "Gambia": "The Gambia",
    "United States Virgin Islands": "US Virgin Islands",
}


def _sig(z):
    return 1 / (1 + math.exp(-max(min(z, 30), -30)))


def _logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _get(url, timeout=20):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                             timeout=timeout).read())


# ---------------------------------------------------------------------------
# FIFA
# ---------------------------------------------------------------------------

FIFA_SEED = 15175          # the release on file when the scan was first written (20 Jul 2026)
FIFA_LATEST_URL = "https://inside.fifa.com/api/ranking-overview?locale=en"   # dateless: the current release
FIFA_LATEST_URLS = (FIFA_LATEST_URL + "&rankingType=football", FIFA_LATEST_URL)
FIFA_STALE_DAYS = 45
# A release must hold at least this share of the teams on file to replace it:
# the men's ranking holds about 211 sides, so a futsal, beach or women's list
# answered under the same id scheme is refused rather than written.
FIFA_MIN_SHARE = 0.8


def _fifa_release(i, errors=None):
    """One release by id, or None, trying each of FIFA_URLS in turn. The
    first exception, if any, is appended to `errors` as (id, "Type: message")
    so the caller can log it."""
    rows = []
    for url in FIFA_URLS:
        try:
            rows = _get(url.format(i)).get("rankings") or []
        except Exception as e:
            if errors is not None:
                errors.append((i, f"{type(e).__name__}: {e}"))
            continue
        if rows:
            break
    return _parse_release(i, rows)


def _parse_release(i, rows):
    """A release from FIFA's "rankings" rows, or None."""
    if not rows:
        return None
    return {"id": i, "date": rows[0]["lastUpdateDate"][:10],
            "teams": {r["rankingItem"]["name"]: [r["rankingItem"]["rank"], r["rankingItem"]["totalPoints"]]
                      for r in rows}}


def _same_list(cur, new, top=20, share=0.8):
    """True when `new` reads as the same ranking as `cur`: at least `share`
    of cur's top `top` sides sit in new's top `top` + 10. Month to month the
    men's top 20 barely moves; the women's list shares about half of it."""
    if not cur or not cur.get("teams"):
        return True
    head = [t for t, v in sorted(cur["teams"].items(), key=lambda kv: kv[1][0])[:top]]
    near = {t for t, v in new["teams"].items() if v[0] <= top + 10}
    return sum(t in near for t in head) >= share * len(head)


def _release_ids(obj):
    """Every release id ("id15175", or a dateId / id field holding one)
    anywhere in a decoded FIFA response. The overview's exact shape is not
    pinned, so the id is taken wherever it appears."""
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("dateId", "id") and isinstance(v, (str, int)):
                m = re.fullmatch(r"(?:id)?(\d{4,6})", str(v))
                if m:
                    out.add(int(m.group(1)))
            out |= _release_ids(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= _release_ids(v)
    elif isinstance(obj, str):
        m = re.fullmatch(r"id(\d{4,6})", obj)
        if m:
            out.add(int(m.group(1)))
    return out


def _fifa_latest(errors=None, notes=None):
    """(latest release id, release) from FIFA's dateless overview. The id is
    the largest one it names, or None. Since at least 15 Nov 2026 the
    overview names no id and answers with the current release's "rankings"
    rows alone, so those rows are parsed as a release too (its id is None:
    the caller keeps the file's id as the scan's start). When an overview
    names no id, its keys and its rows' date go to `notes`."""
    ids, rel = set(), None
    for url in FIFA_LATEST_URLS:
        try:
            doc = _get(url)
        except Exception as e:
            if errors is not None:
                errors.append(("latest", f"{type(e).__name__}: {e}"))
            continue
        found = _release_ids(doc)
        rows = doc.get("rankings") if isinstance(doc, dict) else None
        try:
            r = _parse_release(None, rows) if isinstance(rows, list) else None
        except (KeyError, TypeError, IndexError):
            r = None
        if r and (rel is None or r["date"] > rel["date"]):
            rel = r
        if not found and notes is not None:
            keys = sorted(doc)[:12] if isinstance(doc, dict) else type(doc).__name__
            what = f"{len(r['teams'])} teams dated {r['date']}" if r else "no parsable rows"
            notes.append(f"FIFA ranking: overview {url.split('?', 1)[1]} named no release id "
                         f"(keys: {keys}; {what})")
        ids |= found
    return (max(ids) if ids else None), rel


def _fifa_latest_id(errors=None, notes=None):
    """The latest release id FIFA's dateless overview names, or None."""
    return _fifa_latest(errors, notes)[0]


def load_fifa():
    try:
        return json.load(open(FIFA_FILE))
    except Exception:
        return None


def fifa_age_days(cur):
    return (date.today() - date.fromisoformat(cur["date"])).days if cur else None


def _stale_warning(cur, log):
    if log is None or not cur:
        return
    age = fifa_age_days(cur)
    if age > FIFA_STALE_DAYS:
        log.append(f"WARNING: FIFA ranking on file is {age} days old ({cur['date']}, id {cur['id']}); "
                   f"internationals are being scored on a stale ranking")


def refresh_fifa(scan=160, log=None):
    """Look for a newer release than the one on file. FIFA's dateless overview
    names the current release id; that id is fetched first, then the ids after
    max(seed, file id) are scanned because ids step irregularly. Only runs when
    the file is over three weeks old. The first fetch failure is logged with
    its type and message, and a file over FIFA_STALE_DAYS old raises a line
    starting WARNING: in the build log whether or not the scan finds anything."""
    cur = load_fifa()
    if cur and fifa_age_days(cur) < 21:
        return cur
    start = max(FIFA_SEED, cur["id"] if cur else 0) + 1
    errors, notes = [], []
    latest, overview = _fifa_latest(errors, notes)
    ids = list(range(start, start + scan))
    if latest and latest >= start:
        ids = [latest] + [i for i in ids if i != latest]
    with cf.ThreadPoolExecutor(8) as ex:
        found = [r for r in ex.map(lambda i: _fifa_release(i, errors), ids) if r]
    need = FIFA_MIN_SHARE * len(cur["teams"]) if cur and cur.get("teams") else 0
    short = [r for r in found if len(r["teams"]) < need]
    found = [r for r in found if len(r["teams"]) >= need]
    other = [r for r in found if not _same_list(cur, r)]
    found = [r for r in found if _same_list(cur, r)]
    if other and log is not None:
        log.append("FIFA ranking: refused " + ", ".join(f"id {r['id']}" for r in other[:5])
                   + ": its top 30 does not hold the file's top 20 (another ranking)")
    if not found and overview and (not cur or overview["date"] > cur["date"]):
        if len(overview["teams"]) < need or not _same_list(cur, overview):
            if log is not None:
                log.append(f"FIFA ranking: refused the overview's release ({len(overview['teams'])} teams, "
                           f"{overview['date']}): not the men's ranking on file")
        else:
            # No id to scan from: keep the file's (or the seed), so the next
            # scan starts where it did and the overview is read again.
            overview["id"] = max(FIFA_SEED, cur["id"] if cur else 0)
            overview["from"] = "overview"
            found = [overview]
    if short and log is not None:
        log.append("FIFA ranking: refused " + ", ".join(f"id {r['id']} ({len(r['teams'])} teams)" for r in short[:5])
                   + f", under {FIFA_MIN_SHARE:.0%} of the {len(cur['teams'])} on file")
    if found:
        new = max(found, key=lambda r: r["id"])
        json.dump(new, open(FIFA_FILE, "w"), ensure_ascii=False, separators=(",", ":"))
        if log is not None:
            log.append(f"FIFA ranking: new release {new['date']} (id {new['id']}"
                       + (", from the dateless overview" if new.get("from") else "") + ")")
        _stale_warning(new, log)
        return new
    if log is not None:
        log.append(f"FIFA ranking: no newer release than {cur['date'] if cur else 'none'} "
                   f"(scanned ids {ids[0]}-{ids[-1]}, latest per overview: {latest})")
        log.extend(notes)
        if errors:
            which, msg = errors[0]
            log.append(f"FIFA ranking: first fetch failure (id {which}) {msg}")
    _stale_warning(cur, log)
    return cur


def fifa_team(fifa, name):
    """[rank, points] or None."""
    if not fifa:
        return None
    t = fifa["teams"]
    return t.get(FIFA_NAMES.get(name, name)) or t.get(name)


def adjust_fifa(conf, fav, opp):
    """Probability the international win pick lands, given both FIFA entries."""
    if not fav or not opp:
        return conf
    return _sig(FIFA_W[0] + FIFA_W[1] * _logit(conf) + FIFA_W[2] * (fav[1] - opp[1]) / 100 + FIFA_W[3])


# ---------------------------------------------------------------------------
# tennis
# ---------------------------------------------------------------------------

def tennis_ranks(tour):
    """{ESPN athlete id: rank} for the current top 150, or {} on any failure."""
    try:
        idx = _get(f"https://sports.core.api.espn.com/v2/sports/tennis/leagues/{tour}/rankings")
        ref = idx["items"][0]["$ref"].replace("http://", "https://")
        doc = _get(ref)
    except Exception:
        return {}
    out = {}
    for r in doc.get("ranks") or []:
        m = re.search(r"/athletes/(\d+)", (r.get("athlete") or {}).get("$ref", ""))
        if m and r.get("current"):
            out[m.group(1)] = int(r["current"])
    return out


def adjust_atp(conf, rank_fav, rank_opp):
    """Probability the ATP pick lands. Unranked in the live top 150 counts as
    151 on both sides, exactly as in the test; two unranked players carry no
    ranking information and keep the Elo number."""
    if not rank_fav and not rank_opp:
        return conf
    rf, ro = min(rank_fav or ATP_CAP, ATP_CAP), min(rank_opp or ATP_CAP, ATP_CAP)
    return _sig(ATP_W[0] + ATP_W[1] * _logit(conf) + ATP_W[2] * math.log(ro / rf))


if __name__ == "__main__":
    log = []
    f = refresh_fifa(log=log)
    print("\n".join(log))
    if f:
        top = sorted(f["teams"].items(), key=lambda kv: kv[1][0])[:5]
        print(f"FIFA {f['date']}: " + ", ".join(f"{r[0]}. {n}" for n, r in top))
    for t in ("atp", "wta"):
        r = tennis_ranks(t)
        print(f"{t.upper()}: {len(r)} ranked players")
