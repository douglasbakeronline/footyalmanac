"""The slip: the day's accumulator built for return, not confidence (15 Nov 2026).

Douglas, 15 Nov 2026, after a five-fold at 6.6 (one leg short) and an
eleven-fold at 3.0 (two short): "it's becoming really pointless to be having
games that are like 1.10, because you just need so many of them to work ...
make some suggestions of how we can implement a better way of reading and
automating picks from the almanac." Then: "Action that."

The results ledger (ledger.py) says the opposite of the instinct. Priced
picks at 62%+, landed against the price they were available at: 1.00-1.15
land 94.7% against 95.1% implied (-0.4% a leg), 1.15-1.30 -1.8%, 1.30-1.50
-3.3%, 1.50-1.80 -13.8%. Picks where the model sits 5+ points above the
price's implied chance land 49-56% and lose 9-14% a leg. An accumulator
cannot make an edge its legs do not have; it compounds the margin, faster
the longer the price. So the slip:

  - takes every priced pick still to start on a UK day, every sport, at 62%+
  - gives each leg the chance its sport and price band has actually landed
    on the ledger (RATES_MIN_N graded picks, else the pooled band), never
    the model's number alone
  - refuses a leg from a band that returns worse than LEG_RET_MIN, a leg the
    model rates more than ABOVE_MAX over the price's implied chance, and an
    away college pick (sports.WARY_SPORTS, claude/college-side-mark-2026-11-15.md)
  - picks the LEGS[0] to LEGS[1] legs, from different fixtures and at most
    COMP_MAX a competition, whose combined price sits in TARGET and whose
    expected return (the product of tested chance x price) is highest, and
    offers it only when that return is at least the stake (EV_MIN)
  - shows that expected return in pence per pound before anything is placed,
    and says why a day has no slip

Each UK day's slip is archived in slip-archive/<day>.json, replaced until
its first leg starts and frozen from then, graded from the ledger's results
(a void leg is struck from the price), and tallied under the pre-registered
gate: GATE_N settled slips, return positive at the archived price, and
day-resampled p(loss) <= GATE_P, before it is called a method.

    python3 slip.py       # CI, after ledger.py: build today and tomorrow, grade, write slip.json / slip.js

Display and record only: nothing here feeds a model, the Daily List or the
Card. Standard library only. claude/the-slip-2026-11-15.md.
"""
import gzip, itertools, json, os, random, re, sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ARCHIVE = "slip-archive"
LEDGER = "results-ledger.json.gz"
RULE = 1                       # the leg and slip rule; bump on any change
LIVE_FROM = "2026-11-15"
BOOK = "William Hill"
DAYS_AHEAD = 2                 # UK days built: today and tomorrow
GLANCE_DAYS = 14
UK = ZoneInfo("Europe/London")

PRICE_BANDS = ((1.00, 1.15), (1.15, 1.30), (1.30, 1.50), (1.50, 1.80), (1.80, 2.50), (2.50, 99.0))
CONF_MIN = 0.62                # a leg is at least Firm on the model
RATES_MIN_N = 50               # a sport's own band rate needs this many graded picks; else the pooled band
LEG_RET_MIN = -0.02            # a band may cost no more than the bookmaker's margin a leg
ABOVE_MAX = 0.05               # the model no more than this above the price's implied chance
TARGET = (3.0, 6.0)            # the slip's combined price
LEGS = (3, 5)
COMP_MAX = 2                   # legs from one competition
EV_MIN = 1.0                   # a slip is offered only when its expected return covers the stake
CAND_MAX = 30                  # strongest candidates searched (by chance x price)
GATE_N, GATE_P = 100, 0.10     # the pre-registered gate


# 22 Nov 2026 (Douglas: "is there a visual tracker for performance?"): the
# page's tracker draws every settled slip, so slip.json keeps them all (a
# slip a day at most: a year is 365 short rows).
RECENT_KEEP = 400
REPLAY_KEEP = 400

def _load(path, default=None):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f: return json.load(f)
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default


def parse_utc(s):
    if not s: return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else None


def uk_day(dt):
    return dt.astimezone(UK).date().isoformat()


def band_of(price):
    for lo, hi in PRICE_BANDS:
        if lo <= price < hi:
            return f"{lo:.2f}-{hi:.2f}" if hi < 99 else f"{lo:.2f}+"
    return None


def leg_price(row):
    """(price, book) for a ledger row: Hill's where it has one, else the last
    pre-start price, else the first."""
    for src in (row.get("last"), row.get("first")):
        if not src: continue
        if src.get("h"):
            return float(src["h"]), BOOK
        if src.get("o"):
            return float(src["o"]), src.get("bb") or "average"
    return None, None


# ---------------------------------------------------------------------- rates

def band_rates(rows):
    """Landed v implied by (sport, price band) and pooled by band, on graded
    priced picks at CONF_MIN+: n, landed, rate, implied, return at the price.
    A tally of the ledger, never a fit (Rule 1)."""
    t = {}
    for r in rows:
        if r.get("result") not in ("won", "lost") or (r.get("conf") or 0) < CONF_MIN: continue
        p, _ = leg_price(r)
        if not p: continue
        b = band_of(p)
        if not b: continue
        for k in ((r["sport"], b), ("all", b)):
            x = t.setdefault(k, [0, 0, 0.0, 0.0])
            x[0] += 1; x[1] += r["result"] == "won"; x[2] += 1 / p; x[3] += p * (r["result"] == "won")
    out = {}
    for (sport, b), (n, w, imp, ret) in t.items():
        out.setdefault(sport, {})[b] = {"n": n, "landed": w, "rate": round(w / n, 4),
                                        "implied": round(imp / n, 4), "ret": round(ret / n - 1, 4)}
    return out


def leg_chance(sport, band, rates):
    """(chance, return, basis) for a leg: its sport's own band when it holds
    RATES_MIN_N picks, else the pooled band, else None."""
    own = (rates.get(sport) or {}).get(band)
    if own and own["n"] >= RATES_MIN_N:
        return own["rate"], own["ret"], f"{sport} at {band}: {own['landed']} of {own['n']}"
    pooled = (rates.get("all") or {}).get(band)
    if pooled and pooled["n"] >= RATES_MIN_N:
        return pooled["rate"], pooled["ret"], f"all sports at {band}: {pooled['landed']} of {pooled['n']}"
    return None, None, None


# ----------------------------------------------------------------- candidates

def comp_name(r):
    """A football row's league name (the ledger carries the code)."""
    if r.get("sport") != "football":
        return r.get("comp")
    try:
        import scale
        return scale.league_name(r.get("comp"))
    except Exception:
        return r.get("comp")


def candidates(day, rows, rates, now):
    """The day's admissible legs and the reasons the rest were left out."""
    try:
        import sports as SP
        wary_sports = SP.WARY_SPORTS
    except Exception:
        wary_sports = {"ncaab", "cfb"}
    legs, off = [], {}
    for r in rows:
        start = parse_utc(r.get("start"))
        if not start or uk_day(start) != day or start <= now or r.get("result"): continue
        conf = r.get("conf") or 0
        if conf < CONF_MIN: continue
        p, book = leg_price(r)
        if not p:
            off["no price"] = off.get("no price", 0) + 1; continue
        band = band_of(p)
        ch, ret, basis = leg_chance(r["sport"], band, rates)
        why = None
        if ch is None: why = "band untested"
        elif ret < LEG_RET_MIN: why = "band loses"
        elif conf - 1 / p > ABOVE_MAX: why = "model above the price"
        elif r["sport"] in wary_sports and r.get("side") == "a": why = "away college pick"
        if why:
            off[why] = off.get(why, 0) + 1; continue
        legs.append({"key": r["key"], "sport": r["sport"], "comp": comp_name(r), "home": r["home"], "away": r["away"],
                     "pick": r["pick"], "side": r.get("side"), "start": r["start"], "conf": conf,
                     "list": bool(r.get("list")), "reserve": bool(r.get("reserve")),
                     "price": p, "book": book, "band": band, "chance": ch, "bandRet": ret, "basis": basis,
                     "fixture": f"{r['sport']}|{r['home']}|{r['away']}"})
    legs.sort(key=lambda l: (-(l["chance"] * l["price"]), -l["chance"], l["start"]))
    return legs, off


def best_slip(legs):
    """The LEGS-sized set with the highest expected return whose price is in
    TARGET, from different fixtures, at most COMP_MAX a competition; or
    (None, why)."""
    cand = legs[:CAND_MAX]
    best, reason = None, "few" if len(cand) < LEGS[0] else None
    under = over = False
    for k in range(LEGS[0], LEGS[1] + 1):
        if len(cand) < k: break
        for combo in itertools.combinations(cand, k):
            if len({l["fixture"] for l in combo}) < k: continue
            comps = {}
            for l in combo: comps[l["comp"]] = comps.get(l["comp"], 0) + 1
            if max(comps.values()) > COMP_MAX: continue
            price = 1.0; ev = 1.0; ch = 1.0
            for l in combo:
                price *= l["price"]; ev *= l["chance"] * l["price"]; ch *= l["chance"]
            if price < TARGET[0]: under = True; continue
            if price > TARGET[1]: over = True; continue
            if best is None or ev > best["ev"] or (ev == best["ev"] and ch > best["chance"]):
                best = {"legs": list(combo), "price": round(price, 2), "chance": round(ch, 4), "ev": round(ev, 4)}
    if best and best["ev"] >= EV_MIN:
        return best, None
    if best:
        return None, "value"
    if reason is None:
        reason = "short" if under and not over else "long" if over and not under else "spread" if (under or over) else "few"
    return None, reason


WHY = {"few": "fewer than three legs clear the leg rule today",
       "value": "the best slip the legs allow returns less than the stake on its tested chances",
       "short": "every slip the legs allow pays under the target band: the admissible picks are too short-priced",
       "long": "every slip the legs allow pays over the target band",
       "spread": "no set of legs lands inside the target band"}


# -------------------------------------------------------------------- archive

def merge_day(old, slip, why, legs_n, off, now, stamp, day):
    """A day's archive: the slip is replaced until its first leg starts and
    frozen from then; the leg count and the left-off reasons are this
    build's."""
    old = old or {}
    cur = old.get("slip")
    if cur and (parse_utc(cur["first"]) or now) <= now:
        return dict(old, date=day, rule=old.get("rule", RULE), candidates=legs_n, off=off, built=stamp)
    out = {"date": day, "rule": RULE, "candidates": legs_n, "off": off, "built": stamp, "why": why, "slip": None}
    if slip:
        out["slip"] = {"legs": [{k: v for k, v in l.items() if k != "fixture"} for l in slip["legs"]],
                       "price": slip["price"], "chance": slip["chance"], "ev": slip["ev"],
                       "first": min(l["start"] for l in slip["legs"]), "published": stamp}
        out["why"] = None
    return out


def grade(slip, results):
    """The slip's state from the ledger's results: lost once a leg lost, won
    when every standing leg won, void when none stood, pending otherwise;
    `ret` on a unit stake with void legs struck from the price."""
    states = [results.get(l["key"]) for l in slip["legs"]]
    if "lost" in states:
        return {"state": "lost", "ret": 0.0}
    if any(s is None for s in states):
        return {"state": "pending"}
    stood = [l for l, s in zip(slip["legs"], states) if s == "won"]
    if not stood:
        return {"state": "void", "ret": 1.0}
    ret = 1.0
    for l in stood: ret *= l["price"]
    return {"state": "won", "ret": round(ret, 4)}


def gate(settled, reps=2000, seed=11):
    """The pre-registered read: n, return, and day-resampled p(loss)."""
    n = len(settled)
    if not n:
        return {"n": 0, "pass": False}
    by_day = {}
    for s in settled: by_day.setdefault(s["date"], []).append(s["ret"] - 1)
    days = list(by_day.values())
    rng = random.Random(seed)
    ret = sum(s["ret"] for s in settled) / n - 1
    losses = 0
    for _ in range(reps):
        tot = cnt = 0
        for _ in range(len(days)):
            d = days[rng.randrange(len(days))]
            tot += sum(d); cnt += len(d)
        losses += (tot / cnt) <= 0
    p = losses / reps
    return {"n": n, "ret": round(ret, 4), "pLoss": round(p, 3),
            "pass": n >= GATE_N and ret > 0 and p <= GATE_P, "need": {"n": GATE_N, "pLoss": GATE_P}}


# --------------------------------------------------------------------- replay

def replay(rows, upto, since=None):
    """The rule walked forward over the ledger's past days: each day's slip
    is built from the day's priced picks with the band rates read from the
    picks settled before that day, then graded. A check of the selection
    rule on data it has not seen, not a fit; the rates it needs are thin at
    the start, so early days build nothing."""
    results = {r["key"]: r["result"] for r in rows if r.get("result")}
    days = sorted({uk_day(parse_utc(r["start"])) for r in rows if parse_utc(r.get("start"))})
    out = []
    for day in days:
        if day >= upto or (since and day < since): continue
        day_start = datetime.fromisoformat(day + "T00:00:00").replace(tzinfo=UK).astimezone(timezone.utc)
        past = [r for r in rows if (parse_utc(r.get("start")) or day_start) < day_start]
        rates = band_rates(past)
        legs, off = candidates(day, [dict(r, result=None) for r in rows], rates, day_start - timedelta(seconds=1))
        slip, why = best_slip(legs)
        if not slip:
            out.append({"date": day, "why": why, "candidates": len(legs)}); continue
        g = grade({"legs": slip["legs"]}, results)
        out.append({"date": day, "price": slip["price"], "chance": slip["chance"], "ev": slip["ev"], "candidates": len(legs),
                    "legs": [f"{l['pick']} {l['price']:.2f}" for l in slip["legs"]], **g})
    settled = [{"date": d["date"], "ret": d["ret"], "state": d["state"]} for d in out if d.get("state") in ("won", "lost", "void")]
    return {"days": out, "settled": len(settled), "won": sum(s["state"] == "won" for s in settled),
            "built": sum(1 for d in out if d.get("price")), "gate": gate(settled)}


# ---------------------------------------------------------------------- build

def build(now=None, here=HERE):
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    ledger = _load(os.path.join(here, LEDGER), {}) or {}
    rows = ledger.get("rows") or []
    rates = band_rates(rows)
    results = {r["key"]: r["result"] for r in rows if r.get("result")}
    adir = os.path.join(here, ARCHIVE)
    os.makedirs(adir, exist_ok=True)
    today = date.fromisoformat(uk_day(now))
    for k in range(0, DAYS_AHEAD):
        day = (today + timedelta(days=k)).isoformat()
        path = os.path.join(adir, f"{day}.json")
        legs, off = candidates(day, rows, rates, now)
        slip, why = best_slip(legs)
        merged = merge_day(_load(path, {}) or {}, slip, why, len(legs), off, now, stamp, day)
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(merged, f, separators=(",", ":"), ensure_ascii=False)
        os.replace(path + ".tmp", path)

    files = sorted(fn for fn in os.listdir(adir) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", fn))
    days_out, settled, recent = [], [], []
    for fn in files:
        d = _load(os.path.join(adir, fn), {}) or {}
        day = fn[:-5]
        if d.get("slip"):
            g = grade(d["slip"], results)
            d["slip"].update(g)
            d["slip"]["legStates"] = {l["key"]: results.get(l["key"]) for l in d["slip"]["legs"]}
            if g["state"] in ("won", "lost", "void"):
                settled.append({"date": day, "ret": g["ret"], "state": g["state"]})
                recent.append({"date": day, "state": g["state"], "price": d["slip"]["price"], "ev": d["slip"]["ev"],
                               "chance": d["slip"].get("chance"),
                               "ret": g["ret"], "legs": [f"{l['pick']} {l['price']:.2f}" for l in d["slip"]["legs"]]})
        if day >= (today - timedelta(days=GLANCE_DAYS)).isoformat():
            days_out.append(d)
    rp = replay(rows, LIVE_FROM)
    out = {"generated": stamp, "rule": RULE, "book": BOOK, "today": today.isoformat(), "from": LIVE_FROM,
           "replay": {k: v for k, v in rp.items() if k != "days"},
           # 22 Nov 2026: every replayed slip, for the tracker's line (was the last 20)
           "replayDays": [d for d in rp["days"] if d.get("price")][-REPLAY_KEEP:],
           "rule_text": {"confMin": CONF_MIN, "legRetMin": LEG_RET_MIN, "aboveMax": ABOVE_MAX, "target": TARGET,
                         "legs": LEGS, "compMax": COMP_MAX, "ratesMinN": RATES_MIN_N, "evMin": EV_MIN},
           "days": days_out, "rates": rates,
           "record": {"gate": gate(settled), "won": sum(s["state"] == "won" for s in settled),
                      "lost": sum(s["state"] == "lost" for s in settled), "recent": recent[-RECENT_KEEP:][::-1]}}
    with open(os.path.join(here, "slip.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    with open(os.path.join(here, "slip.js"), "w", encoding="utf-8") as f:
        f.write("window.__SLIP__=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/") + ";")
    return out


def main():
    out = build()
    for d in out["days"]:
        if d["date"] < out["today"]: continue
        s = d.get("slip")
        if s:
            print(f"slip {d['date']}: {len(s['legs'])} legs at {s['price']:.2f}, tested chance {s['chance']:.0%}, "
                  f"expected return {100 * s['ev']:.0f}p in the pound, {s.get('state', 'open')}; "
                  + ", ".join(f"{l['pick']} {l['price']:.2f}" for l in s["legs"]))
        else:
            print(f"slip {d['date']}: none ({WHY.get(d.get('why'), d.get('why'))}); {d.get('candidates', 0)} legs clear, "
                  f"left out {d.get('off')}")
    rp = out["replay"]
    print(f"slip replay before {LIVE_FROM}: {rp['built']} days built, {rp['won']} of {rp['settled']} won"
          + (f", return {100 * rp['gate']['ret']:+.1f}%, p(loss) {rp['gate']['pLoss']}" if rp["settled"] else ""))
    g = out["record"]["gate"]
    print(f"slip record: {out['record']['won']} won, {out['record']['lost']} lost"
          + (f", return {100 * g['ret']:+.1f}%, p(loss) {g['pLoss']}, gate {'passed' if g['pass'] else 'not yet'}" if g.get("n") else ""))


if __name__ == "__main__":
    main()
