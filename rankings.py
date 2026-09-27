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
FIFA_URL = "https://inside.fifa.com/api/ranking-overview?locale=en&dateId=id{}"
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

def _fifa_release(i):
    try:
        rows = _get(FIFA_URL.format(i)).get("rankings") or []
    except Exception:
        return None
    if not rows:
        return None
    return {"id": i, "date": rows[0]["lastUpdateDate"][:10],
            "teams": {r["rankingItem"]["name"]: [r["rankingItem"]["rank"], r["rankingItem"]["totalPoints"]]
                      for r in rows}}


def load_fifa():
    try:
        return json.load(open(FIFA_FILE))
    except Exception:
        return None


def refresh_fifa(scan=160, log=None):
    """Look for a newer release than the one on file. FIFA publishes roughly
    monthly in season, with ids that step irregularly, so the next ids are
    scanned. Only runs when the file is over three weeks old."""
    cur = load_fifa()
    if cur and (date.today() - date.fromisoformat(cur["date"])).days < 21:
        return cur
    start = (cur["id"] + 1) if cur else 15175
    with cf.ThreadPoolExecutor(8) as ex:
        found = [r for r in ex.map(_fifa_release, range(start, start + scan)) if r]
    if found:
        new = max(found, key=lambda r: r["id"])
        json.dump(new, open(FIFA_FILE, "w"), ensure_ascii=False, separators=(",", ":"))
        if log is not None:
            log.append(f"FIFA ranking: new release {new['date']} (id {new['id']})")
        return new
    if log is not None:
        log.append(f"FIFA ranking: no newer release than {cur['date'] if cur else 'none'}")
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
