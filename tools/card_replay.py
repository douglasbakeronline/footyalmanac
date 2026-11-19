#!/usr/bin/env python3
"""
The Card replayed on the priced archive, under several leg rules. Advisory:
changes nothing, fits nothing, writes nothing. 29 Oct 2026, Douglas: "I need
this to be the minimum performance of the groups bets over time".

    python3 tools/card_replay.py

Every archived football prediction that carried a bookmaker price before
kick-off (predictions/<date>.json "market", the latest copy per fixture, as
tools/market_check.py joins them) is a candidate leg with the model's number,
the bookmakers' average and best price, and its result. Days follow the
29 Oct 2026 window (07:00 UK to 07:00 next day). For each rule the Card is
built exactly as groupings.build_card builds it today (best_card, card_fault,
mult_combo, the 2x and 3x kinds, three or four picks, no fixture twice) and
graded strictly: a group is won only when every pick won.

Variants compared (29 Oct 2026 afternoon, pre-registered for the 30 Nov
review so no variant is picked because it happened to look good):
  live     the Card exactly as groupings.py builds it today
  under8   the model at least 8 points under the market (live: 5)
  under10  the model at least 10 points under the market
  four3x   Card 3x groups of four picks, 2x unchanged
  wider    wider API-Football leagues admitted, under the market (CARD_CORE_ONLY False)
  uncapped the gap uncapped, as the Card was from 29 to 31 Oct 2026 (10+ under
           lost on the live archive and both football-data seasons; capped 31 Oct)
  short    prices 1.15 to 1.35 only (the one band positive on both seasons)
  rule5    no opposition-price condition (the Card as it ran 31 Oct to 6 Nov 2026)
  opp7     the opposition priced 7+ rather than 9+
  notennis tennis off the Card (CARD_SPORTS_OFF), the tripwire's action
  comp3    three legs from one competition (live: two; 10 Nov 2026)
  fillwide live, and on a day the full rule leaves empty the page's wider-rule
           group (the fallback the page has used since 25 Oct 2026)
  fillopp7 / fillrule5 / fillshort  live, and on an empty day the Card under
           opp7, rule5 or short instead (10 Nov 2026, issue #155)
  modelcard the Model card's rule (the model's own picks at or above the
           bookmakers' chance) on the same legs, staked as the Card (10 Nov 2026)
  tennis75 tennis legs at 75%+, the floor before CARD_RULE 10 (11 Nov 2026)
  tennis80 tennis legs at 80%+ on model and tested rate (live: 85% since 11 Nov)
           (9 Nov 2026: tennis legs are the Card's one consistent leak, 22 of
           40 full-rule legs landed v 71% quoted; registered before the pool
           holds enough real-priced tennis legs to read them)
Each is built with build_card's own pieces (best_card, card_fault, the kinds,
the cap, the stake weights) with one constant patched, so the replay and the
live card cannot drift apart. `--since YYYY-MM-DD` limits the days.

Rule 1 holds: nothing is fitted here, it is the scoreboard read. The archive
has prices from 11 Sep 2026, so this is seven weeks and the intervals are
wide; read the direction, not the decimals. Standard library only.

9 Nov 2026 (issue #154): from POOL_FROM (30 Oct 2026) the legs come from the
archived pool, groupings-archive/pool-<date>.json.gz, the priced legs the
live Card really chose from, every sport, with the first real bookmaker
price (the row itself, or its `priced` block when the leg was first archived
as an estimate), the opposition's price and the result through
groupings.settle (football by names and date; tennis and US sport by id,
or by names when the row predates `id` in POOL_KEYS). Legs with no real
price, or no result yet, are left out. Before POOL_FROM the football-data
archive rows stand. `--no-pool` replays the archive rows throughout, as
before; `--closing` prices each pool leg at its last pre-start price instead;
`--recover` also admits legs archived as estimates before `priced` existed,
at their last price with the typical margin (approximate, see pool_market).
"""
import gzip, json, math, os, random, sys
from collections import defaultdict
from datetime import datetime, timedelta
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "tools"))
import groupings as G, engine as E, sources as S
import market_check as M

random.seed(7)
IDX = {"h": 0, "d": 1, "a": 2}
CORE = {c for c, m in E.LEAGUES.items() if not c.startswith("af.") and not m.get("cup") and not m.get("international")}
POOL_FROM = "2026-10-30"     # the first pool file; archive_pool shipped 30 Oct 2026
POOL_DIR = os.path.join(HERE, "groupings-archive")
PRED_DIR = os.path.join(HERE, "predictions")


def archive_opp_index(pred_dir=PRED_DIR, since=POOL_FROM):
    """(league, date, home, away) -> the football archive's average 1X2
    prices, from rows published before their kick-off (16 Nov 2026). The pool
    kept no opposition price before 6 Nov (`opp` joined the pool's keys then),
    so 382 priced football legs from 30 Oct to 9 Nov could not be read by any
    variant with an opposition condition (rule6 and its family, m7opp5,
    m7opp9): each faulted "no bookmaker price for the opposition". The
    archive's `market` is the same API-Football average, written when the
    build published the row; on the 246 legs that carry both it agrees with
    the pool's own price on the 5.0 and 9.0 lines 91% of the time (median
    difference 0). Later files overwrite earlier ones, so the latest
    pre-start copy stands."""
    out = {}
    if not pred_dir or not os.path.isdir(pred_dir): return out
    for f in sorted(os.listdir(pred_dir)):
        if not f.endswith(".json") or f[:10] < since: continue
        try: rows = json.load(open(os.path.join(pred_dir, f)))
        except (OSError, ValueError): continue
        for x in rows if isinstance(rows, list) else []:
            mk = x.get("market") or {}
            avg = mk.get("avg")
            if not avg or len(avg) != 3 or not x.get("kickoff") or (x.get("published") or "") > x["kickoff"]: continue
            out[(x.get("league"), x.get("date"), x.get("home"), x.get("away"))] = avg
    return out


def archive_opp(row, aidx):
    """The opposition's and the draw's average price for a football pool row
    from the archive index, or None."""
    if row.get("sport") != "football" or not aidx: return None
    avg = aidx.get((row.get("code"), (row.get("when") or "")[:10], row.get("home"), row.get("away")))
    side = row.get("side") or ("h" if row.get("pick") == row.get("home") else "a")
    if not avg or side not in ("h", "a"): return None
    o = avg[2 - IDX[side]]
    return (round(o, 2), round(avg[1], 2) if avg[1] else None) if o else None


def pool_market(row, closing=False, recover=False):
    """The bookmaker numbers a pool row can be replayed on, or None: the row's
    own when it was priced at first write, else its `priced` block (the first
    real price, 9 Nov 2026). With closing=True the last pre-start price.
    recover=True also takes a leg archived as an estimate before `priced`
    existed (30 Oct to 9 Nov 2026) at its last pre-start price with the
    typical margin (groupings.MARGIN), as the live pipeline prices a one-sided
    source: approximate, and a closing price, so labelled `recovered`."""
    if not row.get("est") and row.get("fair") is not None:
        mk = {k: row.get(k) for k in G.PRICED_KEYS if row.get(k) is not None}
    elif row.get("priced") and row["priced"].get("fair") is not None:
        mk = dict(row["priced"])
    elif recover and row.get("lastOdds"):
        mk = {"odds": row["lastOdds"], "best": row.get("lastBest") or row["lastOdds"], "margin": G.MARGIN,
              "fair": round(1 / row["lastOdds"] / G.MARGIN, 4), "opp": row.get("lastOpp"),
              "src": "recovered: last pre-start price, typical margin", "recovered": True}
    else:
        return None
    if closing and row.get("lastOdds"):
        mk.update(odds=row["lastOdds"], best=row.get("lastBest") or row["lastOdds"])
        if row.get("lastFair") is not None: mk["fair"] = row["lastFair"]
        if row.get("lastOpp"): mk["opp"] = row["lastOpp"]
    return mk


# moved into groupings on 11 Nov 2026 (list_at_book needs the same fallback);
# kept as names here for tools/price_timing.py and the tests
name_indexes = G.name_indexes
near = G._near
settle_pool = G.settle_pool


def pool_legs(since=None, until=None, closing=False, pool_dir=POOL_DIR, idx=None, recover=False, pred_dir=None):
    """Pool rows -> settled legs in groupings' shape, by Card day, with a
    tally of what was left out and why (and, with recover, how many legs
    were taken at their last price). A football leg with no opposition price
    takes the football archive's (archive_opp, 16 Nov 2026); pred_dir defaults
    to predictions/ only for the live pool, so a test's pool reads no disk."""
    idx = idx or G.results_index(); names = name_indexes(idx)
    if pred_dir is None and pool_dir == POOL_DIR: pred_dir = PRED_DIR
    aidx = archive_opp_index(pred_dir) if pred_dir else {}
    by, skipped, recovered, oppfill = defaultdict(list), defaultdict(int), 0, 0
    # 13 Nov 2026: one row a fixture (G.pool_rows): a fixture moved to another
    # day was counted twice, once on the day it was not played
    for d, row in G.pool_rows(pool_dir):
        if d < POOL_FROM or (since and d < since) or (until and d > until): continue
        mk = pool_market(row, closing, recover)
        if mk is None:
            skipped["estimate only"] += 1; continue
        if mk.get("recovered"): recovered += 1
        if not mk.get("opp"):
            ao = archive_opp(row, aidx)
            if ao:
                mk = dict(mk, opp=ao[0], oppFrom="archive")
                if ao[1] and not mk.get("draw"): mk["draw"] = ao[1]
        l = dict(row, **mk, est=False)
        # 14 Nov 2026: an order of play published before the start clears the estimate
        l["timeEst"] = G.pool_time_est(row)
        if l.get("sport") == "football" and not l.get("side"):
            l["side"] = "h" if l["pick"] == l.get("home") else "a"
        st, res = settle_pool(l, idx, names)
        if st not in ("won", "lost"):
            skipped[st] += 1; continue
        l["won"] = st == "won"; l["result"] = res
        if l.get("oppFrom") == "archive": oppfill += 1
        l["core"] = G.core_league(l.get("code")) if l.get("sport") == "football" else False
        l.setdefault("hit", l.get("pTested") or l.get("p"))
        # the bookmakers' chance is the archived one (honest() would refit it
        # from the first margin, wrong at the closing price); p as honest() sets it
        l["implied"] = round(1 / l["odds"], 4); l.setdefault("pTested", l["p"])
        l["p"] = round(min(l["pTested"], l["fair"]), 4); l["edge"] = round(l["p"] * l["odds"] - 1, 4)
        slot = G.uk_slot(l)
        if slot: by[slot[0]].append(l)
        else: skipped["no time"] += 1
    skipped = dict(skipped)
    if recovered: skipped["recovered, counted at the last price"] = recovered
    if oppfill: skipped["opposition price from the football archive (kept)"] = oppfill
    return by, skipped


def legs_of(rows):
    """Archive rows -> legs in groupings' shape, by Card day."""
    by = defaultdict(list)
    for i, x in enumerate(rows):
        p = x.get("p") or {}
        if not p or x.get("celtic") or x.get("unrated") or x.get("why") not in G.CLEAN_WHY: continue
        side = max(p, key=p.get)
        if side == "d": continue
        mk = x["market"]; j = IDX[side]
        avg, best = mk["avg"][j], (mk.get("best") or mk["avg"])[j]
        margin = sum(1 / o for o in mk["avg"] if o)
        l = {"sport": "football", "event": f"{x['home']} v {x['away']}", "pick": x["home"] if side == "h" else x["away"],
             "comp": x["league"], "code": x["league"], "when": x.get("kickoff") or f"{x['date']}T12:00:00Z", "date": x["date"], "odds": round(avg, 2),
             "best": round(best, 2), "margin": round(margin, 4), "est": False, "pModel": round(p[side], 4), "p": round(p[side], 4),
             "hit": 0.8, "n": 100, "won": x["actual"] == side, "core": x["league"] in CORE,
             # 9 Nov 2026: the opposition's and the draw's average price, so the
             # live rule (CARD_OPP_MIN, 6 Nov) replays on the archive
             "opp": round(mk["avg"][2 - j], 2) if mk["avg"][2 - j] else None, "draw": round(mk["avg"][1], 2) if mk["avg"][1] else None}
        G.honest(l)
        slot = G.uk_slot(l)
        if slot: by[slot[0]].append(l)
    return by


# 11 Nov 2026: payout bands for the payout variants (name, lowest combined
# price, highest, lowest combined chance, picks a group). The floor chance
# is the band's fair chance less a margin's worth, as the 2x's 0.30 is.
PAYOUT_BANDS = {
    "Card 1.5x": (1.45, 1.99, 0.40, (2, 3)),
    "Card 2.5x": (2.40, 2.99, 0.24, (3, 4, 5)),
    "Card 3x": (3.00, 4.60, 0.18, (3, 4, 5)),
}
PAYOUTS = {
    "pay15": ["Card 1.5x"],
    "pay25": ["Card 2.5x"],
    "pay3": ["Card 3x"],
    "ladder": ["Card 3x", "Card 2.5x", "Card 2x", "Card 1.5x"],
}


def payout_patch(kinds):
    """Constants for a Card built from the given payout bands (in order)."""
    band = dict(PAYOUT_BANDS, **{"Card 2x": (2.0, 3.0, 0.30, G.CARD_LEGS)})
    ck = [(n, band[n][0], band[n][1], band[n][2]) for n in kinds]
    legs = tuple(sorted({k for n in kinds for k in band[n][3]}))
    p = {"CARD_KINDS": ck, "CARD_BUILD": tuple(kinds), "CARD_LEGS": legs, "_LEGS": {n: tuple(band[n][3]) for n in kinds},
         "CARD_RANGE": dict(G.CARD_RANGE, **{n: (lo, hi) for n, lo, hi, _ in ck}),
         "MIN_CHANCE": dict(G.MIN_CHANCE, **{n: f for n, _, _, f in ck}),
         "CARD_STAKE": dict(G.CARD_STAKE, **{n: 2 for n in kinds})}
    if len(kinds) > 1: p["_PER_KIND"] = 1     # the ladder: one group a band a day
    return p


VARIANTS = {
    "live": {},
    "under8": {"CARD_UNDER_MARKET": 0.08},
    "under10": {"CARD_UNDER_MARKET": 0.10},
    "four3x": {"CARD_LEGS_3X": (4,)},
    "wider": {"CARD_CORE_ONLY": False},
    "uncapped": {"CARD_UNDER_MAX": 0},     # rule 4, before the 31 Oct 2026 cap
    "short": {"CARD_ODDS": (1.15, 1.35)},
    # 6 Nov 2026: live is rule 6 (opposition priced 9+). "rule5" is the Card
    # as it ran from 31 Oct to 6 Nov, for the 30 Nov comparison; legs archived
    # before 6 Nov carry no opposition price, so "live" is empty on those days.
    "rule5": {"CARD_OPP_MIN": {}},
    "opp7": {"CARD_OPP_MIN": {"football": 7.0}},
    # 9 Nov 2026, pre-registered for the tennis tripwire and the 30 Nov review
    "notennis": {"CARD_SPORTS_OFF": set(G.CARD_SPORTS_OFF) | {"tennis"}},
    "tennis80": {"CARD_SPORT_MIN": dict(G.CARD_SPORT_MIN, tennis=0.80)},
    # 11 Nov 2026: live tennis floor raised to 85% (CARD_RULE 10); the old 75%
    "tennis75": {"CARD_SPORT_MIN": dict(G.CARD_SPORT_MIN, tennis=0.75)},
    # 9 Nov 2026 (claude/card-staking-2026-11-09.md), pre-registered for the
    # 30 Nov review: the same groups at one unit each. Live stakes two on a 2x;
    # the live 2x has landed under quote and the 3x over, the football-data
    # seasons the other way round. Same groups, so read `return` (per unit
    # staked); the units-a-day pairing also carries the smaller turnover.
    "flatstake": {"CARD_STAKE": {"Card 2x": 1, "Card 3x": 1}},
    # 10 Nov 2026 (claude/card-funnel-2026-11-10.md), pre-registered for the
    # 30 Nov review: three legs from one competition rather than two. On 9 Nov
    # five NBA legs cleared the full rule and no group was built.
    "comp3": {"COMP_MAX": 3},
    # 10 Nov 2026 (issue #155, claude/card-fillers-2026-11-10.md), pre-
    # registered for the 30 Nov review: the empty-day fillers. Each is the live
    # Card, and only on a day the full rule leaves empty, groups built under
    # the filler (marked `fill`). Paired against live they measure the
    # filler's own return; "fillwide" is the page's fallback today (the
    # wider rule, 1.08-2.10 at 55%+, graded apart as cardWide).
    "fillwide": {"_FILL": "wide"},
    "fillopp7": {"_FILL": "opp7"},
    "fillrule5": {"_FILL": "rule5"},
    "fillshort": {"_FILL": "short"},
    # 10 Nov 2026, pre-registered for the 30 Nov review: the Model card (the
    # model's own picks, rated 60%+ and at or above the bookmakers' chance,
    # groups chosen on the model's chance, groupings.MODEL_KINDS), built on
    # the same legs as the Card and staked like it, so the review compares
    # the two on hundreds of legs rather than the paper record's 14 groups.
    "modelcard": {"_KINDS": "model"},
    # 11 Nov 2026: the Card became the model's own picks (CARD_RULE 7, Douglas:
    # "The model rules"). The rule 6 Card it replaced is kept here, so the 30 Nov
    # review still pairs the two on the same legs.
    "rule6": {},     # RULE6 below: the rule 6 Card, base of the family
    # 19 Nov 2026 (RULES below): the rules before rule 6, on the rule 6 base
    "rule1": {"CARD_CORE_ONLY": False, "CARD_UNDER_MAX": 0, "CARD_OPP_MIN": {}},
    "rule4": {"CARD_UNDER_MAX": 0, "CARD_OPP_MIN": {}},
    # 11 Nov 2026 (Douglas: "Just do better on the groups"): the rule 7 Card's
    # group shape and edge, each one change from live, run on the pool and on
    # five football-data seasons (card_legs_history.py cardM7*).
    "m7edge3": {"CARD_MODEL_EDGE": 0.03},        # the model 3+ points above the bookmakers
    "m7edge6": {"CARD_MODEL_EDGE": 0.06},        # 6+ points above
    "m7legs3": {"CARD_LEGS": (3,)},              # three picks a group, never four or five
    "m7short": {"CARD_ODDS": (1.15, 1.50)},      # picks priced 1.15 to 1.50 only
    "m7only2x": {"CARD_KINDS": [k for k in G.CARD_KINDS if k[0] == "Card 2x"]},   # no 3x (live from CARD_RULE 8)
    "with3x": {"CARD_BUILD": ("Card 2x", "Card 3x")},   # 11 Nov 2026: the rule 7 Card with its 3x, as before CARD_RULE 8
    "m7notennis": {"CARD_SPORTS_OFF": set(G.CARD_SPORTS_OFF) | {"tennis"}},
    # 11 Nov 2026 (claude/card-funnel-rule7-2026-11-11.md): the funnel under
    # rule 8 has the value demand the one condition that costs groups (4 to 8
    # on 6-14 Nov). Pre-registered before any result: the model up to 5 points
    # under the bookmakers' chance. Volume is not return; gated like the rest.
    "m7under5": {"CARD_MODEL_EDGE": -0.05},
    # 11 Nov 2026 evening (claude/card-m7wide-2026-11-11.md), pre-registered
    # before any result: the rule 8 Card with the wider API-Football leagues
    # admitted (CARD_CORE_ONLY False, card_league: no cups, no new leagues).
    # The funnel has "league" the largest single fault on football (224 of
    # 439 pool legs from 6 Nov). Pool only: football-data carries no wider
    # league. Volume is not return; gated like the rest.
    "m7wide": {"CARD_CORE_ONLY": False},   # live from 11 Nov 2026 (CARD_RULE 11)
    "m7core": {"CARD_CORE_ONLY": True},    # core leagues only, the rule to CARD_RULE 10
    # 12 Nov 2026 (claude/card-m7legs2-2026-11-12.md), pre-registered before
    # any result: the rule 11 Card 2x may also be two picks. On 11 Nov five NBA
    # picks cleared the full rule at 1.53-1.64 and no group was built: three
    # of them pay 3.6x+, over the 2x band (2.0-3.0), and a group needed three.
    # Two picks at 1.40-1.73 sit in the band. Volume is not return; gated.
    "m7legs2": {"CARD_LEGS": (2, 3, 4, 5)},
    # 11 Nov 2026, Douglas: "Preferably 3x or more. Then 2.5x. Then 2x. Then
    # 1.5x ... I need the groups to win every time. But ultimately this has to
    # be a profitable business." Pre-registered before any result: the rule 8
    # Card with its 2x swapped for one payout band each (the model's own picks,
    # its most likely combination in the band, up to three a day, two units a
    # group like the 2x), and the ladder in his order, one group a band.
    **{v: payout_patch(kinds) for v, kinds in PAYOUTS.items()},
    # 12 Nov 2026 (groupings.CARD_SPAN, claude/card-span-2026-11-12.md): a day
    # the full rule leaves empty borrows the next day's legs (one group, at
    # least one of the day's own picks); the next day never reuses them. Live
    # since 12 Nov, but until 17 Nov the replay's "live" built without it and
    # this ran as span2; now every live-machinery variant spans while
    # CARD_SPAN is on (`spans`), and nospan replays the rollback
    # (claude/card-replay-live-span-2026-11-17.md).
    "nospan": {"_SPAN": False},
    "span2": {"_SPAN": True},    # 19 Nov 2026: two-day groups, live from 12 to 19 Nov, off under CARD_RULE 14
    # 15 Nov 2026 (claude/card-m7opp-2026-11-15.md), pre-registered before any
    # result: the rule 11 Card with rule 6's opposition condition on its
    # football picks (groupings.CARD_MODEL_OPP_MIN). 9+ is rule 6's floor, the
    # one condition that held in all five football-data seasons; 5.0 (4/1) is
    # the Edge flag's floor since 11 Nov. Gated like the rest.
    "m7opp9": {"CARD_MODEL_OPP_MIN": {"football": 9.0}},
    "m7opp5": {"CARD_MODEL_OPP_MIN": {"football": 5.0}},
    # 16 Nov 2026: CARD_RULE 12 set m7opp5 live (Douglas's call, before its
    # pool gate), so m7opp5 now equals live; rule 11, with no opposition
    # condition, is replayed as m7noopp (claude/card-opp5-list2x-2026-11-16.md)
    "m7noopp": {"CARD_MODEL_OPP_MIN": {}},
    # 17 Nov 2026: CARD_RULE 13 dropped both bookmaker conditions (the value
    # demand and the opposition floor), so m7noopp is live less the value
    # demand and m7opp5 is live less neither. The rule 12 Card is replayed
    # as rule12 for the 30 Nov review (claude/card-rule13-model-only-2026-11-17.md).
    "rule12": {"CARD_MODEL_EDGE": 0.0, "CARD_MODEL_OPP_MIN": {"football": 5.0}, "CARD_BUILD": ("Card 2x",), "CARD_CORE_ONLY": False,
               "CARD_SPORT_MIN": {"tennis": 0.85}, "_SPAN": True},   # pinned 19 Nov 2026
    # 19 Nov 2026 (RULES below): the model's-picks rules before rule 11, each
    # as it ran (the value demand on, no two-day groups before 12 Nov)
    "rule7": {"CARD_MODEL_EDGE": 0.0, "CARD_MODEL_OPP_MIN": {}, "CARD_BUILD": ("Card 2x", "Card 3x"), "CARD_CORE_ONLY": True,
              "CARD_SPORT_MIN": dict(G.CARD_SPORT_MIN, tennis=0.75), "_SPAN": False},
    "rule8": {"CARD_MODEL_EDGE": 0.0, "CARD_MODEL_OPP_MIN": {}, "CARD_BUILD": ("Card 2x",), "CARD_CORE_ONLY": True,
              "CARD_SPORT_MIN": dict(G.CARD_SPORT_MIN, tennis=0.75), "_SPAN": False},
    "rule10": {"CARD_MODEL_EDGE": 0.0, "CARD_MODEL_OPP_MIN": {}, "CARD_BUILD": ("Card 2x",), "CARD_CORE_ONLY": True,
               "CARD_SPORT_MIN": {"tennis": 0.85}, "_SPAN": False},
    # 19 Nov 2026 (CARD_RULE 14 set rule 8's constants live): rules 11 to 13
    # pinned in full, as live no longer carries their wider leagues, 85%
    # tennis floor or two-day groups
    "rule11": {"CARD_MODEL_EDGE": 0.0, "CARD_MODEL_OPP_MIN": {}, "CARD_BUILD": ("Card 2x",), "CARD_CORE_ONLY": False,
               "CARD_SPORT_MIN": {"tennis": 0.85}, "_SPAN": True},
    "rule13": {"CARD_MODEL_EDGE": None, "CARD_MODEL_OPP_MIN": {}, "CARD_BUILD": ("Card 2x",), "CARD_CORE_ONLY": False,
               "CARD_SPORT_MIN": {"tennis": 0.85}, "_SPAN": True},
    "m7value": {"CARD_MODEL_EDGE": 0.0},   # the value demand alone (rule 11)
    # 18 Nov 2026 (claude/card-m7cap160-2026-11-18.md): on the results ledger,
    # 60%+ picks priced 1.60 to 1.90 at their first price landed 47% against
    # the model's 64% (95 legs, football, NBA and tennis; football alone 76
    # legs, 50% v 64%, z -2.45), the legs rule 13 admits once the value
    # demand is off. Pre-registered before any group replay: the Card's price
    # range capped at 1.60. m7short (1.50) is the existing tighter cap.
    "m7cap160": {"CARD_ODDS": (1.15, 1.60)},
}

# 11 Nov 2026 (claude/card-replay-rule6-family-2026-11-11.md): the variants
# above "rule6" were pre-registered as one change to the rule 6 Card. Under
# rule 7/8 the live Card reads none of CARD_UNDER_MARKET, CARD_UNDER_MAX,
# CARD_OPP_MIN or CARD_CORE_ONLY and builds no 3x, so patched onto live they
# rebuilt live exactly ("identical to live" in the 11 Nov review) and the
# fillers built nothing. Each now runs on the rule 6 Card with its one change,
# as registered, and is paired against both live and rule6.
# 12 Nov 2026: the rule 6 Card ran with tennis at 75% (29 Oct to 11 Nov); the
# live floor went to 85% with CARD_RULE 10, and RULE6 had inherited it, so
# rule6, notennis and tennis80 replayed identically (no tennis leg reaches 85%
# on the pool). Pinned to the floor rule 6 ran with, like CARD_CORE_ONLY.
RULE6 = {"CARD_MODEL_RULE": False, "CARD_RULE": 6, "CARD_BUILD": ("Card 2x", "Card 3x"), "CARD_CORE_ONLY": True,
         "CARD_SPORT_MIN": dict(G.CARD_SPORT_MIN, tennis=0.75)}
RULE6_FAMILY = {"rule6", "under8", "under10", "four3x", "wider", "uncapped", "short", "rule5", "opp7", "notennis", "tennis80",
                "rule1", "rule4"}

# 19 Nov 2026 (Douglas: "I would have hoped that the idea for the card rule
# has been tracked the entire time since it was incepted ... which rule has
# performed the best over the entire timeline"): every CARD_RULE the page has
# run, as a variant built on the whole pool, so each rule is read on the same
# days rather than only on the days it was live. The live dates are from
# groupings.CARD_RULE's history. Rule 9 (the context veto) cannot be rebuilt
# on days it did not read, so it is not a variant; rules 2 and 3 changed only
# the windows and the page, not the picks. Rule 13 is `live`.
RULES = [
    # number, variant, live from, live to, one line
    (1, "rule1", "2026-10-25", "2026-10-28", "bookmakers' favourites the model rates 5+ under them, any league, 2x and 3x"),
    (4, "rule4", "2026-10-29", "2026-10-30", "core leagues only"),
    (5, "rule5", "2026-10-31", "2026-11-05", "the gap capped at 10 under"),
    (6, "rule6", "2026-11-06", "2026-11-10", "the opposition priced 9+"),
    (7, "rule7", "2026-11-11", "2026-11-11", "the model's own picks at or above the bookmakers, 2x and 3x, core leagues, tennis 75%+"),
    (8, "rule8", "2026-11-11", "2026-11-11", "the 2x alone"),
    (10, "rule10", "2026-11-11", "2026-11-11", "tennis at 85%+"),
    (11, "rule11", "2026-11-11", "2026-11-15", "the wider leagues in (two-day groups from 12 Nov)"),
    (12, "rule12", "2026-11-16", "2026-11-16", "football opposition priced 5.0+"),
    (13, "rule13", "2026-11-17", "2026-11-18", "the model alone: no bookmaker condition, wider leagues, two-day groups"),
    (14, "live", "2026-11-19", None, "rule 8's constants again: the model at or above the bookmakers, core leagues, tennis 75%+, 2x alone"),
]


def patch_of(variant):
    """The constants a variant sets: a rule 6 family variant on top of RULE6."""
    return dict(RULE6, **VARIANTS[variant]) if variant in RULE6_FAMILY else VARIANTS[variant]


def build_wide(day_legs, date):
    """The page's fallback for an empty day (groupings.build_card's wider-rule
    block): one group of each kind under the wider rule, seq 1."""
    after = G.lock_time(date, "Day"); groups, used = [], set()
    for name, _, _, _ in G.built_kinds():
        g = G.best_card(day_legs, used, after, name, wide=True)
        if not g: continue
        used |= {l["event"] for l in g["legs"]}
        g["won"] = all(l["won"] for l in g["legs"]); g["stake"] = G.CARD_STAKE.get(name, 1); g["seq"] = 1
        groups.append(g)
    return groups


def spans(variant):
    """17 Nov 2026: whether a variant is built with two-day groups. Every
    variant on the live machinery spans while groupings.CARD_SPAN is live
    (it is part of the live Card since 12 Nov), unless it sets `_SPAN`
    itself (nospan). The rule 6 family is pinned to how rule 6 ran (no
    two-day groups then) and the paper Model card never had them."""
    patch = patch_of(variant)
    if "_SPAN" in patch: return bool(patch["_SPAN"])
    if variant in RULE6_FAMILY or patch.get("_KINDS") == "model": return False
    return bool(G.CARD_SPAN)


def _patched(patch):
    """Set a variant's constants on groupings; returns the saved values."""
    saved = {k: getattr(G, k) for k in patch if hasattr(G, k) and not k.startswith("_")}
    for k, v in patch.items():
        if k != "CARD_LEGS_3X" and not k.startswith("_"): setattr(G, k, v)
    return saved


def build_span(by, dates, variant="live"):
    """12 Nov 2026: a variant's Card, and each day it leaves empty takes one
    group from its own legs and the next day's (at least one of its own), the
    way groupings.build_card does under CARD_SPAN, under the variant's own
    constants. Days in order; legs a two-day group holds are not used again
    the next day. A filler variant (`_FILL`) spans on live's rule first and
    fills only a day still empty, as the page would with both on."""
    from datetime import date as _date, timedelta as _td
    patch = patch_of(variant)
    fill = patch.get("_FILL")
    base = "live" if fill else variant
    rule = {} if fill else patch
    out, held = {}, set()
    for d in dates:
        own = [l for l in by[d] if l["event"] not in held]
        gs = build(own, d, base)
        if not gs:
            nd = (_date.fromisoformat(d) + _td(days=1)).isoformat()
            mine = {o["event"] for o in own}
            saved = _patched(rule)
            try:
                after = G.lock_time(d, "Day")
                for name, _, _, _ in G.built_kinds():
                    g = G.best_card(own + [l for l in by.get(nd, []) if l["event"] not in held], set(), after, name,
                                    need=lambda l: l["event"] in mine)
                    if not g or not any(l["event"] in mine for l in g["legs"]): continue
                    g["won"] = all(l["won"] for l in g["legs"]); g["stake"] = G.CARD_STAKE.get(name, 1); g["seq"] = 1; g["span"] = True
                    held |= {l["event"] for l in g["legs"]}; gs = [g]; break
            finally:
                for k, v in saved.items(): setattr(G, k, v)
        if not gs and fill:
            gs = build_wide(own, d) if fill == "wide" else build(own, d, fill)
            for g in gs: g["fill"] = True
        out[d] = gs
    return out


def build(day_legs, date, variant):
    """One day's Card under a variant, with the live machinery."""
    patch = patch_of(variant)
    if patch.get("_KINDS") == "model":
        after = G.lock_time(date, "Day"); groups, used = [], set()
        for (name, _, _, _), card in zip(G.MODEL_KINDS, G.CARD_KINDS):
            g = G.best_card(day_legs, used, after, name)
            if not g: continue
            used |= {l["event"] for l in g["legs"]}
            # grade and stake as the Card kind it mirrors; its chance is the model's
            g["won"] = all(l["won"] for l in g["legs"]); g["stake"] = G.CARD_STAKE.get(card[0], 1); g["seq"] = 1
            g["name"] = card[0]; g["model"] = True
            groups.append(g)
        return groups
    if "_FILL" in patch:
        groups = build(day_legs, date, "live")
        if groups: return groups
        fill = patch["_FILL"]
        groups = build_wide(day_legs, date) if fill == "wide" else build(day_legs, date, fill)
        for g in groups: g["fill"] = True
        return groups
    saved = {k: getattr(G, k) for k in patch if hasattr(G, k)}
    legs_3x = patch.get("CARD_LEGS_3X")
    legs_of_kind = patch.get("_LEGS") or {}
    for k, v in patch.items():
        if k != "CARD_LEGS_3X" and not k.startswith("_"): setattr(G, k, v)
    try:
        after = G.lock_time(date, "Day"); groups, used = [], set()
        for seq in ((1,) if patch.get("_PER_KIND") else (1, 2, 3)):
            for name, _, _, _ in G.built_kinds():
                if len(groups) >= G.CARD_MAX_GROUPS: break
                if name in legs_of_kind:
                    old_legs = G.CARD_LEGS; G.CARD_LEGS = legs_of_kind[name]
                    try: g = G.best_card(day_legs, used, after, name)
                    finally: G.CARD_LEGS = old_legs
                elif legs_3x and name == "Card 3x":
                    old_legs = G.CARD_LEGS; G.CARD_LEGS = legs_3x
                    try: g = G.best_card(day_legs, used, after, name)
                    finally: G.CARD_LEGS = old_legs
                else:
                    g = G.best_card(day_legs, used, after, name)
                if not g: continue
                used |= {l["event"] for l in g["legs"]}
                g["won"] = all(l["won"] for l in g["legs"]); g["stake"] = G.CARD_STAKE.get(name, 1); g["seq"] = seq
                groups.append(g)
        return groups
    finally:
        for k, v in saved.items(): setattr(G, k, v)


def summarise(days, label):
    gs = [g for d in days.values() for g in d]
    if not gs:
        print(f"{label:<8} no groups"); return
    n, w = len(gs), sum(g["won"] for g in gs)
    exp = sum(g["p"] for g in gs)
    st = sum(g["stake"] for g in gs); ret = sum(g["stake"] * g["odds"] for g in gs if g["won"])
    best = sum(g["stake"] * g["bestOdds"] for g in gs if g["won"])
    legs = [l for g in gs for l in g["legs"]]
    lw = sum(l["won"] for l in legs); lq = sum(l["fair"] for l in legs)
    keys = list(days); vals = []
    for _ in range(4000):
        pick = [days[random.choice(keys)] for _ in keys]
        s_ = sum(g["stake"] for d in pick for g in d); r_ = sum(g["stake"] * g["odds"] for d in pick for g in d if g["won"])
        vals.append(r_ / s_ - 1 if s_ else 0)
    vals.sort()
    print(f"{label:<8} days {len(days):>2}  groups {n:>3}  won {w:>3} ({w/n*100:4.0f}%)  expected {exp/n*100:4.0f}%  "
          f"units {st:>3}  return {(ret/st-1)*100:+5.0f}% (90% {vals[200]*100:+.0f} to {vals[3799]*100:+.0f})  best {(best/st-1)*100:+5.0f}%  "
          f"legs {lw}/{len(legs)} landed {lw/len(legs)*100:4.1f}% v quoted {lq/len(legs)*100:4.1f}%")
    for name in dict.fromkeys(g["name"] for g in gs):
        k = [g for g in gs if g["name"] == name]
        if k:
            kw = sum(g["won"] for g in k); ks = sum(g["stake"] for g in k); kr = sum(g["stake"] * g["odds"] for g in k if g["won"])
            print(f"         {name}: {kw}/{len(k)} won, expected {sum(g['p'] for g in k)/len(k)*100:.0f}%, return {(kr/ks-1)*100:+.0f}%")
    return gs


def main():
    since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else None
    use_pool, closing, recover = "--no-pool" not in sys.argv, "--closing" in sys.argv, "--recover" in sys.argv
    rows = M.rows()
    by = legs_of(rows)
    if use_pool:
        # 9 Nov 2026: the pool is the source from POOL_FROM; archive rows before
        by = defaultdict(list, {d: ls for d, ls in by.items() if d < POOL_FROM})
        pool, skipped = pool_legs(since=since, closing=closing, recover=recover)
        for d, ls in pool.items(): by[d].extend(ls)
        sports = defaultdict(int)
        for d, ls in pool.items():
            for l in ls: sports[l["sport"]] += 1
        print(f"pool from {POOL_FROM}: {sum(sports.values())} settled priced legs over {len(pool)} days "
              f"({', '.join(f'{k} {v}' for k, v in sorted(sports.items(), key=lambda x: -x[1]))}); left out: "
              f"{', '.join(f'{k} {v}' for k, v in sorted(skipped.items()))}{'; closing prices' if closing else ''}")
    dates = [d for d in sorted(by) if (not since or d >= since) and by[d]]
    if not dates:
        print("no legs"); return {}
    print(f"{len(rows)} priced archive rows, {sum(len(by[d]) for d in dates)} clean win-pick legs over {len(dates)} days, {dates[0]} to {dates[-1]}")
    out, report = {}, {"days": len(dates), "from": dates[0], "to": dates[-1], "variants": {},
                       "source": {"pool": use_pool, "poolFrom": POOL_FROM if use_pool else None, "closing": closing, "recover": recover,
                                  "poolLegs": dict(sports) if use_pool else None, "poolLeftOut": skipped if use_pool else None}}
    for v in VARIANTS:
        if spans(v): days = build_span(by, dates, v)
        else: days = {d: build(by[d], d, v) for d in dates}
        days = {d: g for d, g in days.items() if g}
        out[v] = days
        summarise(days, v)
        gs = [g for d in days.values() for g in d]
        st = sum(g["stake"] for g in gs); rt = sum(g["stake"] * g["odds"] for g in gs if g["won"])
        report["variants"][v] = {"days": len(days), "groups": len(gs), "won": sum(g["won"] for g in gs),
                                 "expected": round(sum(g["p"] for g in gs), 2), "units": st,
                                 "return": round(rt / st, 3) if st else None, "emptyDays": len(dates) - len(days),
                                 # 10 Nov 2026: the legs, for the decision gate (100+ legs, CLAUDE.md)
                                 "legs": sum(len(g["legs"]) for g in gs), "legsWon": sum(l["won"] for g in gs for l in g["legs"])}
        if v == "live":
            # 18 Nov 2026: the live rule's own groups, for tools/staking.py's
            # bankroll (it had read the football-data `card` key, rule 5/6
            # football only, a Card the page no longer builds)
            report["variants"][v]["groupList"] = [
                {"date": g.get("date") or d, "name": g["name"], "p": round(g["p"], 4), "odds": round(g["odds"], 3),
                 "stake": g["stake"], "won": bool(g["won"]), "legs": len(g["legs"])}
                for d, gl in sorted(days.items()) for g in gl]
        fg = [g for g in gs if g.get("fill")]
        if "_FILL" in VARIANTS[v]:
            # 10 Nov 2026 (#155): the filler's own groups, on the days live left empty
            fs = sum(g["stake"] for g in fg); fr = sum(g["stake"] * g["odds"] for g in fg if g["won"])
            report["variants"][v]["fill"] = {"days": len({g.get("date") or d for d, gl in days.items() for g in gl if g.get("fill")}),
                                             "groups": len(fg), "won": sum(g["won"] for g in fg), "expected": round(sum(g["p"] for g in fg), 2),
                                             "units": fs, "return": round(fr / fs, 3) if fs else None,
                                             "legs": sum(len(g["legs"]) for g in fg), "legsWon": sum(l["won"] for g in fg for l in g["legs"])}
            f = report["variants"][v]["fill"]
            if fg: print(f"         filler alone: {f['days']} days, {f['groups']} groups, {f['won']} won (expected {f['expected']}), "
                         f"units {fs}, return {(f['return'] - 1) * 100:+.0f}%, legs {f['legsWon']}/{f['legs']}")
            else: print("         filler alone: no groups on the empty days")
    pairs = [(v, "live") for v in VARIANTS if v != "live"] + [(v, "rule6") for v in sorted(RULE6_FAMILY - {"rule6"})]
    for v, base in pairs:
        a, b = out[base], out[v]
        alld = sorted(set(a) | set(b)); diffs = []
        for d in alld:
            ra = sum(g["stake"] * g["odds"] for g in a.get(d, []) if g["won"]) - sum(g["stake"] for g in a.get(d, []))
            rb = sum(g["stake"] * g["odds"] for g in b.get(d, []) if g["won"]) - sum(g["stake"] for g in b.get(d, []))
            diffs.append(rb - ra)
        if not diffs: continue
        keys = ("vsLivePerDay", "pWorse") if base == "live" else ("vsRule6PerDay", "pWorseVsRule6")
        if v in RULE6_FAMILY: report["variants"][v]["base"] = "rule6"
        if not any(diffs):
            print(f"paired {v} - {base} on {len(alld)} days: identical to {base}")
            report["variants"][v].update({keys[0]: 0.0, keys[1]: None}); continue
        bs = sorted(sum(random.choice(diffs) for _ in diffs) / len(diffs) for _ in range(4000))
        print(f"paired {v} - {base} on {len(alld)} days: {sum(diffs)/len(diffs):+.2f} units a day, "
              f"90% {bs[200]:+.2f} to {bs[3799]:+.2f}, p(worse) {sum(x < 0 for x in bs)/len(bs):.2f}")
        report["variants"][v].update({keys[0]: round(sum(diffs) / len(diffs), 3), keys[1]: round(sum(x < 0 for x in bs) / len(bs), 3)})
    report["rules"] = rules_table(report["variants"])
    print("\nEvery Card rule on the whole archive (the same days for each; RULES):")
    for r in report["rules"]:
        print(f"  rule {r['rule']:>2} ({r['from']} to {r['to'] or 'now'}): {r['groups']} groups, won {r['won']} (expected {r['expected']}), "
              f"return {(r['return'] - 1) * 100:+.0f}%, {r['legs']} legs" + (f", v live {r['vsLivePerDay']:+.2f} a day, p(worse) {r['pWorse']}" if r.get("pWorse") is not None else "")
              + f"  {r['what']}" if r["groups"] else f"  rule {r['rule']:>2}: no groups  {r['what']}")
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as f: json.dump(report, f, indent=1)
    return report


def rules_table(variants):
    """19 Nov 2026: every CARD_RULE (RULES) read from the replay's variants,
    in order, with its live dates; the one table that answers which rule did
    best on the same days."""
    rows = []
    for n, v, a, b, what in RULES:
        r = variants.get(v) or {}
        rows.append({"rule": n, "variant": v, "from": a, "to": b, "what": what,
                     "groups": r.get("groups", 0), "won": r.get("won", 0), "expected": r.get("expected", 0),
                     "return": r.get("return") or 0, "legs": r.get("legs", 0), "emptyDays": r.get("emptyDays"),
                     "vsLivePerDay": r.get("vsLivePerDay"), "pWorse": r.get("pWorse")})
    return rows


if __name__ == "__main__":
    main()
