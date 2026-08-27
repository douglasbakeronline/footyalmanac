"""
Ratings and match-outcome engine.

Two stages:
  1. Team strength  -> attack / defence multipliers relative to their own league.
  2. Match model    -> Dixon-Coles adjusted bivariate Poisson -> P(home) / P(draw) / P(away).

Everything here is deterministic and inspectable: no black boxes, every number a
row shows on the dashboard is produced by a function in this file.
"""
from math import exp, factorial

# ---------------------------------------------------------------------------
# League strength coefficients.
#
# Scale: expected goal-scoring quality of an average side in that competition,
# relative to the Premier League (1.00). Used for two things only:
#   - moving a promoted/relegated team's rating into its new division
#   - comparing teams across competitions
#
# THESE ARE HAND-SET PRIORS AND THEY ARE THE WEAKEST PART OF THE MODEL.
# See README "Calibrating league strength" for how to replace them with values
# fitted from European competition results.
# ---------------------------------------------------------------------------
LEAGUES = {
    "en.1": {"iso": "eng", "short": "EPL", "name": "Premier League",   "country": "England",     "tier": 1, "strength": 1.00, "order": 1},
    "en.2": {"iso": "eng", "short": "CHA", "name": "Championship",     "country": "England",     "tier": 2, "strength": 0.78, "order": 2},
    "en.3": {"iso": "eng", "short": "LG1", "name": "League One",       "country": "England",     "tier": 3, "strength": 0.66, "order": 3},
    "en.4": {"iso": "eng", "short": "LG2", "name": "League Two",       "country": "England",     "tier": 4, "strength": 0.58, "order": 4},
    "sco.1": {"iso": "sct", "short": "SPL", "name": "Premiership",      "country": "Scotland",    "tier": 1, "strength": 0.76, "order": 5},
    "es.1": {"iso": "esp", "short": "LAL", "name": "La Liga",          "country": "Spain",       "tier": 1, "strength": 0.99, "order": 6},
    "es.2": {"iso": "esp", "short": "LA2", "name": "LaLiga 2",         "country": "Spain",       "tier": 2, "strength": 0.76, "order": 7},
    "de.1": {"iso": "deu", "short": "BUN", "name": "Bundesliga",       "country": "Germany",     "tier": 1, "strength": 0.97, "order": 8},
    "de.2": {"iso": "deu", "short": "BU2", "name": "2. Bundesliga",    "country": "Germany",     "tier": 2, "strength": 0.76, "order": 9},
    "it.1": {"iso": "ita", "short": "SEA", "name": "Serie A",          "country": "Italy",       "tier": 1, "strength": 0.97, "order": 10},
    "it.2": {"iso": "ita", "short": "SEB", "name": "Serie B",          "country": "Italy",       "tier": 2, "strength": 0.75, "order": 11},
    "fr.1": {"iso": "fra", "short": "FR1", "name": "Ligue 1",          "country": "France",      "tier": 1, "strength": 0.93, "order": 12},
    "fr.2": {"iso": "fra", "short": "FR2", "name": "Ligue 2",          "country": "France",      "tier": 2, "strength": 0.73, "order": 13},
    "nl.1": {"iso": "nld", "short": "ERE", "name": "Eredivisie",       "country": "Netherlands", "tier": 1, "strength": 0.86, "order": 14},
    "pt.1": {"iso": "prt", "short": "PRI", "name": "Primeira Liga",    "country": "Portugal",    "tier": 1, "strength": 0.87, "order": 15},
    "be.1": {"iso": "bel", "short": "BEL", "name": "Pro League",       "country": "Belgium",     "tier": 1, "strength": 0.82, "order": 16},
    "tr.1": {"iso": "tur", "short": "SUP", "name": "Super Lig",        "country": "Turkey",      "tier": 1, "strength": 0.82, "order": 17},
    "at.1": {"iso": "aut", "short": "AUT", "name": "Bundesliga",       "country": "Austria",     "tier": 1, "strength": 0.78, "order": 18},
    "gr.1": {"iso": "grc", "short": "GRE", "name": "Super League",     "country": "Greece",      "tier": 1, "strength": 0.78, "order": 19},
    # Calendar-year season, so it carries its own season strings. It is also the
    # only competition here that is mid-campaign, which makes it the one place
    # you can watch the current-season blend actually doing something.
    "br.1": {"iso": "bra", "short": "BRA", "name": "Serie A",          "country": "Brazil",      "tier": 1, "strength": 0.84, "order": 20,
             "season": "2026", "prev": ["2025", "2024"]},

    # Cup competitions. A cup has no league table of its own, so it has no
    # strength of its own either: every side is rated from its own division and
    # the two are converted into a shared frame (see cup_match). "cup": True is
    # what tells the builder to do that.
    #
    # openfootball has not published 2026/27 cup schedules yet, so these resolve
    # to nothing today and the competitions simply do not appear. They will
    # switch themselves on the first day a schedule lands, with no code change.
    "en.fa":  {"iso": "eng", "short": "FAC", "name": "FA Cup",           "country": "England", "tier": 1, "strength": 0.92, "order": 21, "cup": True},
    "en.lc":  {"iso": "eng", "short": "EFL", "name": "League Cup",       "country": "England", "tier": 1, "strength": 0.90, "order": 22, "cup": True},
    "es.cup": {"iso": "esp", "short": "CDR", "name": "Copa del Rey",     "country": "Spain",   "tier": 1, "strength": 0.92, "order": 23, "cup": True},
    "de.cup": {"iso": "deu", "short": "DFB", "name": "DFB-Pokal",        "country": "Germany", "tier": 1, "strength": 0.91, "order": 24, "cup": True},
    "it.cup": {"iso": "ita", "short": "CIT", "name": "Coppa Italia",     "country": "Italy",   "tier": 1, "strength": 0.91, "order": 25, "cup": True},
    "eu.clq": {"iso": "eur", "short": "UCLQ","name": "Champions League qualifying", "country": "Europe", "tier": 1, "strength": 0.88, "order": 26, "cup": True},
    "eu.cl":  {"iso": "eur", "short": "UCL", "name": "Champions League", "country": "Europe",  "tier": 1, "strength": 1.05, "order": 27, "cup": True},
    "eu.elq": {"iso": "eur", "short": "UELQ","name": "Europa League qualifying",     "country": "Europe", "tier": 1, "strength": 0.82, "order": 28, "cup": True},
    "eu.el":  {"iso": "eur", "short": "UEL", "name": "Europa League",    "country": "Europe",  "tier": 1, "strength": 0.95, "order": 29, "cup": True},
    "eu.ecq": {"iso": "eur", "short": "UECQ","name": "Conference qualifying",        "country": "Europe", "tier": 1, "strength": 0.76, "order": 30, "cup": True},
    "eu.ec":  {"iso": "eur", "short": "UECL","name": "Conference League","country": "Europe",  "tier": 1, "strength": 0.84, "order": 31, "cup": True},
}

# Home advantage, expressed as multipliers on expected goals.
# Ratio HOME_MULT/AWAY_MULT ~ 1.33 reproduces the long-run English top-flight
# split of roughly 45% home / 26% draw / 29% away. Lower divisions run slightly
# higher (smaller crowds, worse pitches, but less travel-adjusted squad depth).
HOME_MULT = {1: 1.155, 2: 1.170, 3: 1.180, 4: 1.185}
AWAY_MULT = {1: 0.870, 2: 0.862, 3: 0.855, 4: 0.850}

SHRINK_FULL_SEASON = 6.0   # pseudo-matches pulling a full season's rating toward league average
SHRINK_ON_TRANSFER = 10.0  # extra pull applied when a team changes division
BLEND_K = 12.0             # current-season matches needed before new data outweighs the prior
FORM_MAX = 0.05            # hard cap on how much last-5 form may move expected goals
RHO = -0.06                # Dixon-Coles low-score correlation term
MAX_GOALS = 10

# Temperature. Raw Poisson output from season-aggregate ratings is measurably
# over-confident: in backtesting, matches priced at 90% came in around 77%.
# The ratings do not know about injuries, rotation, red cards or a keeper having
# the game of his life, so the true distribution is flatter than the model's.
# T > 1 flattens every probability toward the 1/3 line. Fitted on 2025-26; see
# backtest.py --tune. Re-fit whenever the league strength table changes.
TEMPERATURE = 1.15

# Both-teams-to-score and over-2.5 need heavy correction, and it is worth being
# blunt about why. Fitted on 2025/26, the raw grid claimed 64%+ for fixtures
# where both sides actually scored only 57.8% of the time. Shrinking 60% of the
# way back toward the league base rate was optimal:
#
#     k     log loss
#     0.0   0.6901     (ignore the model, always quote the base rate)
#     0.4   0.6880     <- fitted
#     1.0   0.6930     (trust the raw grid)
#
# The gap between using the model and ignoring it entirely is 0.002. That is
# almost nothing. Goals-based markets are far less predictable from season
# aggregates than the match result is, and the UI says so rather than dressing
# a coin flip up as a read.
BTTS_SHRINK = 0.4
BTTS_BASE = 0.539     # share of fixtures where both sides scored, 2025/26


def _shrink(p, base=BTTS_BASE, k=BTTS_SHRINK):
    """Pull a two-way probability back toward the observed base rate."""
    return min(max(base + k * (p - base), 0.02), 0.98)


# ---------------------------------------------------------------------------
# Stage 1: season tables and strength ratings
# ---------------------------------------------------------------------------

def blank_row(team):
    return {"team": team, "P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0,
            "Pts": 0, "results": []}


def build_table(matches):
    """matches: list of (date, home, away, hg, ag). Returns dict team -> row."""
    tbl = {}
    for date, h, a, hg, ag in matches:
        for t in (h, a):
            tbl.setdefault(t, blank_row(t))
        rh, ra = tbl[h], tbl[a]
        rh["P"] += 1; ra["P"] += 1
        rh["GF"] += hg; rh["GA"] += ag
        ra["GF"] += ag; ra["GA"] += hg
        if hg > ag:
            rh["W"] += 1; ra["L"] += 1; rh["Pts"] += 3
            rh["results"].append((date, "W", 3)); ra["results"].append((date, "L", 0))
        elif hg < ag:
            ra["W"] += 1; rh["L"] += 1; ra["Pts"] += 3
            ra["results"].append((date, "W", 3)); rh["results"].append((date, "L", 0))
        else:
            rh["D"] += 1; ra["D"] += 1; rh["Pts"] += 1; ra["Pts"] += 1
            rh["results"].append((date, "D", 1)); ra["results"].append((date, "D", 1))
    for r in tbl.values():
        r["GD"] = r["GF"] - r["GA"]
        r["PPG"] = round(r["Pts"] / r["P"], 3) if r["P"] else 0.0
        r["results"].sort()
    return tbl


def league_goal_rate(table):
    """Average goals scored per team per match in this competition."""
    gf = sum(r["GF"] for r in table.values())
    p = sum(r["P"] for r in table.values())
    if not p or not gf:
        return 1.35   # a goalless opening weekend must not collapse the model
    return gf / p


def strength_from_table(table, k=None):
    """Attack / defence multipliers relative to this competition's average.

    att > 1 means the side scores more than a league-average team.
    def < 1 means it concedes less. Both are shrunk toward 1.0 so that a
    team with few matches is not treated as though its record were settled.
    """
    k = SHRINK_FULL_SEASON if k is None else k
    mu = league_goal_rate(table)
    out = {}
    for t, r in table.items():
        p = r["P"]
        if p == 0:
            out[t] = {"att": 1.0, "def": 1.0}
            continue
        att_raw = (r["GF"] / p) / mu
        def_raw = (r["GA"] / p) / mu
        w = p / (p + k)
        out[t] = {"att": w * att_raw + (1 - w) * 1.0,
                  "def": w * def_raw + (1 - w) * 1.0}
    return out


def transfer_rating(rating, from_code, to_code, k=None):
    """Move a rating between divisions.

    A side's absolute quality is (rating relative to its league) x (league
    strength). Re-express that against the new league's average, then shrink
    hard toward 1.0 because promoted and relegated sides are the least
    predictable teams on any given weekend.
    """
    if from_code == to_code:
        return dict(rating)
    k = SHRINK_ON_TRANSFER if k is None else k
    s_from = LEAGUES[from_code]["strength"]
    s_to = LEAGUES[to_code]["strength"]
    att = rating["att"] * (s_from / s_to)
    dfn = rating["def"] * (s_to / s_from)
    w = 38 / (38 + k)
    return {"att": w * att + (1 - w) * 1.0,
            "def": w * dfn + (1 - w) * 1.0}


def blend(prior, current, played, k=None):
    """Weight this season's evidence against last season's rating.

    played=0 -> pure prior. played=12 -> 50/50. played=30 -> 71% current season.

    K=12 was fitted, not guessed, and it is higher than intuition suggests: in
    backtesting, last season's table beat the current season's until roughly a
    dozen matches had been played. Six games of new results is a small sample
    and the model is better off distrusting it.
    """
    if current is None or played == 0:
        return dict(prior)
    k = BLEND_K if k is None else k
    w = played / (played + k)
    return {"att": w * current["att"] + (1 - w) * prior["att"],
            "def": w * current["def"] + (1 - w) * prior["def"]}


def form_points(row, n=5):
    """Points from the last n matches THIS SEASON. None if too few played."""
    res = row["results"] if row else []
    if len(res) == 0:
        return None
    last = res[-n:]
    return {"pts": sum(x[2] for x in last),
            "max": 3 * len(last),
            "seq": "".join(x[1] for x in last)}


def form_factor(fp):
    """Small, capped nudge from recent form.

    Form is mostly already inside the season ratings. What it adds is the part
    the season total misses: injuries, a new manager, a squad that has stopped
    trying. Hence a nudge, not a driver.
    """
    if not fp or fp["max"] < 6:
        return 1.0
    ppg = fp["pts"] / (fp["max"] / 3)
    dev = (ppg - 1.35) / 1.65          # -0.82 .. +1.00 across the plausible range
    return 1.0 + max(-1.0, min(1.0, dev)) * FORM_MAX


# ---------------------------------------------------------------------------
# Stage 2: match model
# ---------------------------------------------------------------------------

def _pois(k, lam):
    return exp(-lam) * lam ** k / factorial(k)


def _tau(x, y, lh, la, rho=RHO):
    """Dixon-Coles correction. Low-scoring results are not independent:
    0-0 and 1-1 happen more often than a plain Poisson expects, 1-0 and 0-1
    slightly less. Without this the model systematically under-prices draws."""
    if x == 0 and y == 0:
        return 1 - lh * la * rho
    if x == 0 and y == 1:
        return 1 + lh * rho
    if x == 1 and y == 0:
        return 1 + la * rho
    if x == 1 and y == 1:
        return 1 - rho
    return 1.0


def temper(h, d, a, T=None):
    """Flatten probabilities toward equal thirds by temperature T, then
    renormalise. T=1 leaves them untouched."""
    T = TEMPERATURE if T is None else T
    if T == 1.0:
        return h, d, a
    p = [max(x, 1e-12) ** (1.0 / T) for x in (h, d, a)]
    s = sum(p)
    return p[0] / s, p[1] / s, p[2] / s


def match_probabilities(att_h, def_h, att_a, def_a, mu, tier=1,
                        form_h=1.0, form_a=1.0, adj_h=1.0, adj_a=1.0):
    """Return probabilities, expected goals and the likeliest scoreline."""
    hm = HOME_MULT.get(tier, 1.16)
    am = AWAY_MULT.get(tier, 0.87)
    lh = max(0.15, att_h * def_a * mu * hm * form_h * adj_h)
    la = max(0.15, att_a * def_h * mu * am * form_a * adj_a)

    ph = [_pois(i, lh) for i in range(MAX_GOALS + 1)]
    pa = [_pois(i, la) for i in range(MAX_GOALS + 1)]

    home = draw = away = 0.0
    btts = over25 = 0.0
    total = 0.0
    best, best_p = (0, 0), -1.0
    for x in range(MAX_GOALS + 1):
        for y in range(MAX_GOALS + 1):
            p = ph[x] * pa[y] * _tau(x, y, lh, la)
            total += p
            if p > best_p:
                best_p, best = p, (x, y)
            if x > y:
                home += p
            elif x == y:
                draw += p
            else:
                away += p
            # Both teams to score, and over 2.5 goals, fall out of the same
            # grid for free: they are just different cells summed.
            if x >= 1 and y >= 1:
                btts += p
            if x + y >= 3:
                over25 += p

    home, draw, away = home / total, draw / total, away / total
    home, draw, away = temper(home, draw, away)
    # Two-way markets get their own, milder temperature: the over-confidence
    # measured on the 1X2 grid does not transfer directly to a binary question.
    btts = _shrink(btts / total)
    over25 = _shrink(over25 / total, base=0.52)
    return {
        "home": home, "draw": draw, "away": away,
        "btts": btts, "over25": over25,
        "xg_home": lh, "xg_away": la,
        "likely_score": best,
        "confidence": max(home, draw, away),
    }


# ---------------------------------------------------------------------------
# Absences
#
# There is no free, open, machine-readable injury feed. Every source is either
# behind a paid API or on a site whose terms forbid scraping. So absences are
# entered by hand in absences.json and converted here, which at least means you
# name the players rather than guessing at a multiplier.
#
# The magnitudes below are deliberately modest. Published work on this puts even
# an outstanding player at something like a fifth to a third of a goal per game,
# because squads are deep and a replacement is rarely worthless. If a single
# injury moves a fixture by twenty points you have overstated it.
# ---------------------------------------------------------------------------

# how much of a player's effect lands on attack vs defence
ROLE_SPLIT = {
    "forward":    (1.00, 0.00),
    "attack":     (1.00, 0.00),
    "midfield":   (0.55, 0.45),
    "defence":    (0.10, 0.90),
    "defender":   (0.10, 0.90),
    "goalkeeper": (0.00, 1.00),
}

# full-strength effect on expected goals, before the role split
IMPORTANCE = {"star": 0.115, "key": 0.065, "squad": 0.022}

ABSENCE_ATT_FLOOR = 0.80   # a team without eleven stars is still a football team
ABSENCE_DEF_CEIL = 1.20


def absence_factors(players):
    """players: list of {"name", "role", "importance"} -> (att_mult, def_mult).

    Effects compound multiplicatively rather than adding, so the fifth absentee
    matters less than the first. That is closer to reality than a linear tally,
    where a long injury list quickly produces a nonsense rating.
    """
    att, dfn = 1.0, 1.0
    for p in players or []:
        w = IMPORTANCE.get(str(p.get("importance", "key")).lower(), IMPORTANCE["key"])
        a_share, d_share = ROLE_SPLIT.get(str(p.get("role", "midfield")).lower(),
                                          ROLE_SPLIT["midfield"])
        att *= (1.0 - w * a_share)
        dfn *= (1.0 + w * d_share)
    return max(ABSENCE_ATT_FLOOR, att), min(ABSENCE_DEF_CEIL, dfn)


# ---------------------------------------------------------------------------
# Cup ties
#
# League fixtures are easy: both sides are rated against the same average, so
# the ratings are directly comparable. A cup tie is not. Barnsley against
# Arsenal, or Bodo/Glimt against Real Madrid, pits ratings measured against two
# different yardsticks, and comparing them raw is meaningless.
#
# The fix is to convert both sides into one shared frame before pricing. The
# frame sits at the midpoint of the two competitions, which keeps the
# conversion symmetric: neither side is treated as the home standard.
#
# The honest caveat is that this leans entirely on the league strength
# coefficients, which are hand-set. In a league fixture they cancel out and do
# not matter. In a cup tie they are the whole answer, so a cup price is doing
# more guessing than a league price and is flagged accordingly.
# ---------------------------------------------------------------------------

def transfer_by_strength(rating, s_from, s_to, k=SHRINK_ON_TRANSFER, played=38):
    """Same idea as transfer_rating, but between raw strength values rather
    than named competitions, so it works for a one-off cup frame."""
    if s_from == s_to:
        return dict(rating)
    att = rating["att"] * (s_from / s_to)
    dfn = rating["def"] * (s_to / s_from)
    w = played / (played + k)
    return {"att": w * att + (1 - w) * 1.0,
            "def": w * dfn + (1 - w) * 1.0}


def cup_frame(s_home, s_away):
    """The shared yardstick for a tie between two competitions."""
    return (s_home + s_away) / 2.0


def cup_match(rating_h, s_h, rating_a, s_a, mu, tier=1, neutral=False,
              form_h=1.0, form_a=1.0):
    """Price a tie between sides rated in different competitions.

    neutral=True removes home advantage, for finals and one-off venues.
    """
    frame = cup_frame(s_h, s_a)
    rh = transfer_by_strength(rating_h, s_h, frame)
    ra = transfer_by_strength(rating_a, s_a, frame)
    if neutral:
        saved_h = HOME_MULT.get(tier, 1.16)
        saved_a = AWAY_MULT.get(tier, 0.87)
        mid = (saved_h + saved_a) / 2.0
        HOME_MULT[tier], AWAY_MULT[tier] = mid, mid
        try:
            return match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"],
                                       mu, tier=tier, form_h=form_h, form_a=form_a)
        finally:
            HOME_MULT[tier], AWAY_MULT[tier] = saved_h, saved_a
    return match_probabilities(rh["att"], rh["def"], ra["att"], ra["def"],
                               mu, tier=tier, form_h=form_h, form_a=form_a)
