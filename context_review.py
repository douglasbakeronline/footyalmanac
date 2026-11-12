"""The context check on the Card's picks (11 Nov 2026).

Douglas, 11 Nov 2026: "the groups pick fixtures on statistical insight. But
with added human contextual review it does much better. I need the groups to
have the same contextual reading" and "I want this contextual review now.
But also just a better understanding of the numbers... goals and points and
other things."

Before a Card group is built, every pick that passes the Card's rule (the
model's own pick, groupings.model_fault) is read by Claude with live web
search: team news (injuries, suspensions, rotation before a bigger game),
the manager, what the game means to each side, travel and the season's
numbers (table position, points, goals for and against, home or away form,
the last five). Each pick gets a verdict with a one-line reason and its
sources:

  clear    nothing found that argues against the pick
  caution  something worth knowing that does not clearly lower its chance
  against  a concrete, sourced reason the pick is less likely than the
           model's number (a key absence, a rested side, nothing to play for)

An "against" pick is kept off the Card (groupings.card_fault, CARD_CONTEXT)
and a substitute takes its place. Every verdict is archived with the pool
(`ctx`) and on the Card's legs, so the record can show whether "against"
picks really landed less often than the model said. It cannot be replayed
on past seasons: the news of those days is not available.

Prices never feed the model; the review sees the price only to know which
side is the favourite. Silent without ANTHROPIC_API_KEY. One review a pick a
day, a second within REFRESH_H hours of the start (line-ups and late news),
at most MAX_REVIEWS calls a build. Verdicts are kept in
groupings-archive/context-<date>.json (committed with the archive).
"""
import json, os, re, sys, urllib.error, urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "groupings-archive")
API = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("CONTEXT_MODEL", "claude-sonnet-5-5")
# 12 Nov 2026 (Douglas: Daily List picks at 75%+ too, football first, then the
# most useful sports, inside the Max plan's monthly API credit, about $100):
# Sonnet where the news is richest and the judgement matters most, Haiku
# (about a third of the cost) for the rest; at most DAILY_READS a UK day,
# read in PRIORITY order (Card picks first, then by sport, then the strongest).
CHEAP_MODEL = os.environ.get("CONTEXT_CHEAP_MODEL", "claude-haiku-5-5")
RICH_SPORTS = {"football", "nba"}
PRIORITY = ("football", "nba", "tennis", "ncaab", "rugby", "nrl", "nfl", "mlb", "nhl", "wnba", "cfb")
DAILY_READS = int(os.environ.get("CONTEXT_DAILY_READS", "25"))
LEDGER = "context-ledger.json"
MAX_REVIEWS = 16        # calls a build
MAX_SEARCHES = 5        # web searches a pick
REFRESH_H = 3           # a second read this close to the start (line-ups)
LEAD_H = 30             # only picks starting within this many hours are read
VERDICTS = ("clear", "caution", "against")
SPORTS = {"football": "football (soccer)", "nba": "NBA basketball", "tennis": "tennis", "rugby": "rugby union",
          "nrl": "rugby league", "mlb": "baseball", "nhl": "ice hockey", "wnba": "WNBA basketball"}


def key_of(l):
    return f"{l.get('event')}|{l.get('pick')}"


def path_of(date):
    return os.path.join(ARCHIVE, f"context-{date}.json")


def load(date):
    try:
        with open(path_of(date)) as f: return json.load(f)
    except Exception:
        return {}


def save(date, data):
    os.makedirs(ARCHIVE, exist_ok=True)
    with open(path_of(date), "w") as f: json.dump(data, f, indent=1, sort_keys=True)


def parse_when(s):
    try: return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception: return None


def prompt(l):
    sport = SPORTS.get(l.get("sport"), l.get("sport"))
    other = l.get("away") if l.get("pick") == l.get("home") else l.get("home")
    when = l.get("when") or l.get("date")
    price = f"{l['odds']:.2f}" if l.get("odds") and not l.get("est") else "not priced"
    return f"""You are checking one pick for a sports prediction site before it goes into a small accumulator.

Fixture: {l.get('event')} ({sport}, {l.get('comp') or ''}), starting {when} UTC.
The pick: {l.get('pick')} to win. Opponent: {other or 'see fixture'}.
The site's statistical model gives the pick {round((l.get('pModel') or 0) * 100)}%. Bookmaker price for the pick: {price}.

Search the web now for current information and read it as an experienced, sceptical bettor would:
1. Team news for both sides: injuries, suspensions, illness, players rested or likely rotated (a bigger game in the next few days, a dead rubber, cup priorities), confirmed line-ups if published. For tennis: fitness, retirements, schedule, surface.
2. Context: manager or coach changes, what the result means to each side (title, promotion, relegation, nothing to play for), travel, weather, off-field turmoil.
3. The numbers this season: league position and points, goals (or points) scored and conceded, home or away record as relevant, the last five results of each side, recent head-to-head.

Then decide:
- "against": only for a concrete, sourced reason that makes the pick clearly less likely than {round((l.get('pModel') or 0) * 100)}% (a key player out, a heavily rotated side, a side with nothing to play for against one fighting for its season, a form collapse the numbers show). General doubt is not enough.
- "caution": something worth knowing that does not clearly lower the chance.
- "clear": nothing found that argues against the pick.
If you cannot find information about this fixture, answer "caution" and say so. Never invent facts: every claim must come from a page you found.

Answer with ONLY this JSON, no other text:
{{"verdict": "clear" | "caution" | "against", "reason": "one sentence, the deciding fact and its source", "numbers": "one or two sentences: position, points, goals for and against, last five, for both sides", "news": "one sentence: the team news that matters, or 'nothing significant'", "sources": [{{"title": "...", "url": "https://..."}}]}}"""


# The web search server tool's version string; CONTEXT_TOOL overrides it. A
# refused version is tried with the next, and the API's own words are logged.
TOOLS = tuple(t for t in (os.environ.get("CONTEXT_TOOL"), "web_search_20250305") if t)


def model_for(l):
    return MODEL if l.get("cxCard") or l.get("sport") in RICH_SPORTS else CHEAP_MODEL


def priority(l):
    """Card picks first, then football, NBA, tennis, college basketball, the
    rest, the strongest first within each, then the earliest start."""
    sp = l.get("sport")
    return (0 if l.get("cxCard") else 1, PRIORITY.index(sp) if sp in PRIORITY else len(PRIORITY),
            -(l.get("pModel") or 0), l.get("when") or "9")


def ledger_load():
    try:
        with open(os.path.join(ARCHIVE, LEDGER)) as f: return json.load(f)
    except Exception:
        return {}


def ledger_save(led):
    os.makedirs(ARCHIVE, exist_ok=True)
    keep = dict(sorted(led.items())[-14:])
    with open(os.path.join(ARCHIVE, LEDGER), "w") as f: json.dump(keep, f, indent=1, sort_keys=True)


def call(l, key, post=None):
    last = None
    for tool in TOOLS:
        body = {"model": model_for(l), "max_tokens": 1500,
                "tools": [{"type": tool, "name": "web_search", "max_uses": MAX_SEARCHES}],
                "messages": [{"role": "user", "content": prompt(l)}]}
        if post: return post(body)
        req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST",
                                     headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            last = RuntimeError(f"HTTP {e.code} with {tool}: {msg}")
            if e.code != 400: break
    raise last


def parse(reply):
    """The verdict from a Messages API reply, or None if it cannot be read."""
    text = "".join(b.get("text", "") for b in (reply or {}).get("content") or [] if b.get("type") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    if not m: return None
    try: v = json.loads(m.group(0))
    except Exception: return None
    verdict = str(v.get("verdict", "")).strip().lower()
    if verdict not in VERDICTS: return None
    src = [{"title": str(s.get("title", ""))[:120], "url": str(s.get("url", ""))} for s in (v.get("sources") or [])
           if isinstance(s, dict) and str(s.get("url", "")).startswith("http")][:4]
    if verdict == "against" and not src: verdict = "caution"     # an unsourced "against" never vetoes
    return {"verdict": verdict, "reason": str(v.get("reason", ""))[:300], "numbers": str(v.get("numbers", ""))[:400],
            "news": str(v.get("news", ""))[:300], "sources": src}


def due(old, l, now):
    """Whether a pick needs a (fresh) read this build."""
    start = parse_when(l.get("when"))
    if start and start <= now: return False
    if start and start - now > timedelta(hours=LEAD_H): return False
    if not old: return True
    at = parse_when(old.get("at"))
    if start and at and start - at > timedelta(hours=REFRESH_H) and start - now <= timedelta(hours=REFRESH_H): return True
    return False


def review(legs, now, report=None, post=None, key=None):
    """Read every pick in legs that is due, attach l['context'] to each leg
    that has a verdict, and keep the verdicts by UK date. Returns the count
    of calls made."""
    report = report if report is not None else {}
    key = key or os.environ.get("ANTHROPIC_API_KEY")
    by_date, calls = {}, 0
    led = ledger_load(); today = now.astimezone(timezone.utc).date().isoformat()
    left = max(0, DAILY_READS - led.get(today, 0))
    for l in sorted(legs, key=priority):
        d = l.get("ukDate") or l.get("date")
        store = by_date.setdefault(d, load(d))
        old = store.get(key_of(l))
        if (key or post) and calls < min(MAX_REVIEWS, left) and due(old, l, now):
            try:
                v = parse(call(l, key, post)); calls += 1
                if v:
                    v["at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ"); v["model"] = model_for(l)
                    v["reads"] = (old or {}).get("reads", 0) + 1
                    store[key_of(l)] = old = v
                else:
                    report.setdefault("errors", []).append(f"context: unreadable reply for {l.get('pick')}")
            except Exception as e:
                report.setdefault("errors", []).append(f"context: {type(e).__name__}: {str(e)[:300]}")
        if old: l["context"] = old
    for d, store in by_date.items():
        if store: save(d, store)
    if calls:
        led[today] = led.get(today, 0) + calls; ledger_save(led)
    report["context"] = {"calls": calls, "read": sum(1 for l in legs if l.get("context")),
                         "against": sum(1 for l in legs if (l.get("context") or {}).get("verdict") == "against"),
                         "today": led.get(today, 0), "dailyCap": DAILY_READS, "on": bool(key or post)}
    return calls


if __name__ == "__main__":
    # by hand: python3 context_review.py "<event>" "<pick>" [when]
    l = {"event": sys.argv[1], "pick": sys.argv[2], "when": sys.argv[3] if len(sys.argv) > 3 else None,
         "sport": "football", "pModel": 0.65}
    print(json.dumps(parse(call(l, os.environ["ANTHROPIC_API_KEY"])), indent=1))
