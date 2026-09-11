#!/usr/bin/env python3
"""
Guard the club-name matcher.

    python3 nametest.py

Why this exists
---------------
Two sources, two spellings for the same club. openfootball says "FC Bayern
München", the live scoreboard says "Bayern Munich". Nothing in the build
notices when those fail to meet: the club simply comes back with no season
played, the blend falls all the way to last year, the fixture gets priced as
though this season had not started, and the page says nothing at all. That bug
sat on the board for weeks and every European tie was wrong.

So the failure has to be loud. This checks three things:

  1. Live-source spellings resolve to the club openfootball actually has, and
     resolve with matches played rather than an empty record.
  2. No club in the rated pool resolves to a *different* club. A missed match
     leaves a visible gap; a wrong one prices a fixture with someone else's
     rating and looks perfectly normal.
  3. Clubs that only a founding year separates stay apart.

Exit code is non-zero on any failure, so deploy.yml can refuse to publish.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E
import sources as S
import build as B

# Spellings the live source uses, and the competition whose current table the
# club should be found in. Add to this whenever a "not rated" row turns out to
# be a name mismatch rather than a genuinely missing season.
LIVE_NAMES = [
    ("Bayern Munich", "de.1"), ("Bayer Leverkusen", "de.1"),
    ("Borussia Dortmund", "de.1"), ("RB Leipzig", "de.1"),
    ("Eintracht Frankfurt", "de.1"), ("1. FC Cologne", "de.1"),
    ("Werder Bremen", "de.1"), ("Union Berlin", "de.1"),
    ("Hoffenheim", "de.1"), ("Mainz", "de.1"),
    ("Real Madrid", "es.1"), ("Barcelona", "es.1"),
    ("Atletico Madrid", "es.1"), ("Athletic Club", "es.1"),
    ("Real Betis", "es.1"), ("Real Sociedad", "es.1"),
    ("Celta Vigo", "es.1"), ("Rayo Vallecano", "es.1"), ("Villarreal", "es.1"),
    ("Manchester City", "en.1"), ("Arsenal", "en.1"),
    ("Tottenham Hotspur", "en.1"), ("Newcastle United", "en.1"),
    ("Nottingham Forest", "en.1"),
    ("Inter Milan", "it.1"), ("AC Milan", "it.1"), ("Juventus", "it.1"),
    ("Napoli", "it.1"), ("Atalanta", "it.1"), ("AS Roma", "it.1"),
    ("Lazio", "it.1"),
    ("Paris Saint-Germain", "fr.1"), ("Marseille", "fr.1"),
    ("Monaco", "fr.1"), ("Lille", "fr.1"),
    ("Ajax", "nl.1"), ("PSV Eindhoven", "nl.1"), ("Feyenoord", "nl.1"),
    ("Sporting CP", "pt.1"), ("Benfica", "pt.1"), ("FC Porto", "pt.1"),
    ("Braga", "pt.1"),
]

# European fixtures arrive in the live source's spelling and are rated through
# the club's domestic league, so they have to resolve against the rated pool,
# not a current table. Each of these was a European tie priced off two
# placeholder ratings until an alias went in. (spelling, club it must reach)
EUROPE_NAMES = [
    ("Club Brugge", "Club Brugge KV"), ("Olympiacos", "Olympiakos Piraeus"),
    ("Benfica", "Sport Lisboa e Benfica"), ("SL Benfica", "Sport Lisboa e Benfica"),
    ("Red Bull Salzburg", "RB Salzburg"), ("Qarabag", "Qarabağ FK"),
    ("Pafos", "Paphos"), ("AZ Alkmaar", "AZ"), ("Bodo/Glimt", "FK Bodø/Glimt"),
]

# Pairs that must never collapse into each other. Two clubs, one city, and the
# founding year is the only thing between them.
DISTINCT = [("CSKA Sofia", "CSKA 1948 Sofia")]


def load():
    spec = {c: (None if E.LEAGUES[c].get("ratingsOnly") else E.LEAGUES[c].get("season", B.SEASON),
                [] if E.LEAGUES[c].get("cup") else E.LEAGUES[c].get("prev", B.PREV))
            for c in E.LEAGUES}
    history, fixtures, _ = S.fetch_all_seasons(spec)
    cur = {}
    for code, rows in fixtures.items():
        played = [(r["date"], r["home"], r["away"], r["hg"], r["ag"])
                  for r in rows if r["hg"] is not None]
        cur[code] = E.build_table(played)
    return set(B.team_pool(history, fixtures)), cur


def main():
    pool, cur = load()
    fails = []

    # 1. live spellings find a club, with a real record behind it
    checked = 0
    for name, code in LIVE_NAMES:
        table = cur.get(code) or {}
        if not table:
            continue                      # league out of season or unfetched
        checked += 1
        hit = name if name in table else S.match_team(name, set(table))
        if not hit:
            fails.append(f"{name!r} ({code}) matched nothing in the current table")
            continue
        if not table[hit]["P"]:
            fails.append(f"{name!r} -> {hit!r} ({code}) has no matches played")
    print(f"live spellings: {checked} checked against a live table")

    # 1b. European spellings reach the right club in the rated pool
    eu = 0
    for name, want in EUROPE_NAMES:
        if want not in pool:
            continue                      # that league's prior is not on file
        eu += 1
        got = S.match_team(name, pool)
        if got != want:
            fails.append(f"{name!r} should resolve to {want!r}, got {got!r}")
    print(f"european spellings: {eu} checked against the rated pool")

    # 2. nothing resolves to a different club
    wrong = [(t, g) for t in pool if (g := S.match_team(t, pool)) != t]
    for a, b in wrong:
        fails.append(f"{a!r} resolves to {b!r} — a wrong match prices the "
                     f"fixture with another club's rating")
    print(f"rated pool: {len(pool)} clubs, {len(wrong)} resolving elsewhere")

    # 3. year-separated clubs stay apart
    for a, b in DISTINCT:
        if a in pool and b in pool:
            if S.match_team(a, pool) != a or S.match_team(b, pool) != b:
                fails.append(f"{a!r} and {b!r} are no longer distinct")
    print(f"distinct pairs: {len(DISTINCT)} checked")

    if fails:
        print(f"\n{len(fails)} failure(s):", file=sys.stderr)
        for f in fails:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("\nall clear")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
