"""College basketball: does the rating carry too much of last season into the new one?

Asked on 16 Nov 2026 after UMBC v Iona: the board had UMBC at 81% on a rating
built from last season's team, and UMBC brought back no starters. The note
`claude/daily-list-losses-2026-11-14.md` left two tests owed: a faster K early
in the season and a heavier summer regression. This runs both, and both
together, on the walk-forward replay `sports.py --tune` uses:

  fit 2024-25, check 2025-26 to the archive start (`sports.FIT`, `sports.CHECK`);
  every variant gets its own season-phase calibration fitted on the fit season
  only (`sports.fit_phase_calibration`), as live does;
  compared with live (k 32, hfa 100, regress 0.25, mov 1) on the same check
  games, paired and bootstrapped; Rule 3 gates (250+ games, p(worse) <= 0.30,
  gain >= 0.0005) and the 65%+ honesty guard (gap may not widen > 1 point).

It also prints, for live, the early-season picks of a side whose results this
season trail its rating (the UMBC shape), landed v quoted, as a second look.

Advisory only: writes nothing. Run: python3 tools/ncaab_carry_eval.py
"""
import math
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sports  # noqa: E402

LIVE = {"k": 32, "hfa": 100, "regress": 0.25, "mov": 1}


class EarlyElo(sports.Elo):
    """Live Elo, plus K x `mult` for a team's first `n` games after a summer
    break. The count resets when the summer regression is applied."""

    def __init__(self, p, mult=1.0, n=0):
        super().__init__(p)
        self.mult, self.n = mult, n
        self.season = {}   # (pool, team) -> games since the last break

    def get(self, pool, team, when):
        key = (pool, team)
        e = self.r.get(key)
        broke = e is None or (datetime.fromisoformat(when[:10])
                              - datetime.fromisoformat(e[1][:10])).days > sports.OFFSEASON_DAYS
        if broke:
            self.season[key] = 0
        return super().get(pool, team, when)

    def update(self, g):
        ph, eh, ea = self.predict(g)
        kh = self.season.get((g["pool"], g["h"]), 99)
        ka = self.season.get((g["pool"], g["a"]), 99)
        early = self.mult if min(kh, ka) < self.n else 1.0
        s = 1.0 if g["hs"] > g["as"] else (0.0 if g["hs"] < g["as"] else 0.5)
        m = 1.0
        if self.p["mov"] and g["hs"] != g["as"]:
            margin = abs(g["hs"] - g["as"])
            diff = (eh[0] - ea[0]) if s == 1.0 else (ea[0] - eh[0])
            m = math.log(margin + 1) * 2.2 / (max(diff, -400) * 0.001 + 2.2)
        delta = self.p["k"] * early * m * (s - ph)
        eh[0] += delta
        ea[0] -= delta
        for e in (eh, ea):
            e[1] = g["when"]
            e[2] += 1
        for t in ((g["pool"], g["h"]), (g["pool"], g["a"])):
            self.season[t] = self.season.get(t, 0) + 1
        return ph


def run(games, p, mult=1.0, n=0):
    elo = EarlyElo(p, mult, n)
    out = []
    for g in games:
        eh = elo.r.get((g["pool"], g["h"]))
        ea = elo.r.get((g["pool"], g["a"]))
        warm = bool(eh and ea and eh[2] >= sports.MIN_GAMES and ea[2] >= sports.MIN_GAMES)
        out.append((g, elo.update(g), warm))
    return out


def keyed(preds, cal):
    """Check-window log loss by game id, and rows for the bands."""
    ll, rows = {}, []
    for g, ph, warm in preds:
        if not warm or not sports.in_window(g, sports.CHECK):
            continue
        ph = sports.calibrate(ph, cal, g["when"])
        y = 1 if g["hs"] > g["as"] else (0 if g["hs"] < g["as"] else None)
        conf = max(ph, 1 - ph)
        rows.append((conf, y is not None and (y == 1) == (ph >= 0.5), g))
        if y is not None:
            ll[g.get("id") or (g["when"], g["h"], g["a"])] = -math.log(max(ph if y else 1 - ph, 1e-12))
    return ll, rows


def top_gap(rows):
    g = [r for r in rows if r[0] >= 0.65]
    return abs(sum(r[0] for r in g) / len(g) - sum(r[1] for r in g) / len(g)) if g else 0.0


def early_rate(rows):
    g = [r for r in rows if r[0] >= 0.70 and int(r[2]["when"][5:7]) in (11, 12)]
    return len(g), (sum(r[1] for r in g) / len(g) if g else 0), (sum(r[0] for r in g) / len(g) if g else 0)


def trailing_check(games, p=LIVE, mult=1.0, n=0):
    """Live replay: November-December picks at 70%+ whose picked side has
    played 3+ games this season and lost more than it won. Landed v quoted."""
    elo = EarlyElo(p, mult, n)
    pre = run(games, p, mult, n)
    cal = sports.fit_phase_calibration(pre, sports.FIT, sports.PHASE_MONTHS["ncaab"])
    rec = {}   # (pool, team) -> [w, l, last date]
    hit = {"trail": [0, 0, 0.0], "other": [0, 0, 0.0]}
    for g in games:
        eh = elo.r.get((g["pool"], g["h"]))
        ea = elo.r.get((g["pool"], g["a"]))
        warm = bool(eh and ea and eh[2] >= sports.MIN_GAMES and ea[2] >= sports.MIN_GAMES)
        for t in (g["h"], g["a"]):
            r = rec.get((g["pool"], t))
            if r is None or (datetime.fromisoformat(g["when"][:10])
                             - datetime.fromisoformat(r[2][:10])).days > sports.OFFSEASON_DAYS:
                rec[(g["pool"], t)] = [0, 0, g["when"]]
        ph = elo.update(g)
        if warm and int(g["when"][5:7]) in (11, 12) and g["hs"] != g["as"]:
            p = sports.calibrate(ph, cal, g["when"])
            conf, home = max(p, 1 - p), p >= 0.5
            if conf >= 0.70:
                pick = g["h"] if home else g["a"]
                w, l, _ = rec[(g["pool"], pick)]
                key = "trail" if (w + l >= 3 and l > w) else "other"
                won = (g["hs"] > g["as"]) == home
                hit[key][0] += 1
                hit[key][1] += won
                hit[key][2] += conf
        hw = 1 if g["hs"] > g["as"] else 0
        for t, won in ((g["h"], hw), (g["a"], 1 - hw)):
            r = rec[(g["pool"], t)]
            r[0 if won else 1] += 1
            r[2] = g["when"]
    return hit


def main():
    games = [g for g in sports.history_for("ncaab") if g["final"]]
    print(f"College basketball: {len(games)} games on file; fit {sports.FIT}, check {sports.CHECK}")

    variants = [("live", LIVE, 1.0, 0)]
    for reg in (0.35, 0.5):
        variants.append((f"regress {reg}", {**LIVE, "regress": reg}, 1.0, 0))
    for mult in (1.5, 2.0):
        for n in (6, 10):
            variants.append((f"early K x{mult} for {n} games", LIVE, mult, n))
    for reg in (0.35, 0.5):
        variants.append((f"regress {reg} + early K x1.5 for 6", {**LIVE, "regress": reg}, 1.5, 6))

    base = None
    print(f"\n{'variant':36} {'games':>6} {'logloss':>8} {'gain':>8} {'p(worse)':>8} {'gap65':>6}  early 70%+ landed/quoted  verdict")
    for name, p, mult, n in variants:
        preds = run(games, p, mult, n)
        cal = sports.fit_phase_calibration(preds, sports.FIT, sports.PHASE_MONTHS["ncaab"])
        ll, rows = keyed(preds, cal)
        en, eh, eq = early_rate(rows)
        if base is None:
            base = (ll, top_gap(rows))
            print(f"{name:36} {len(ll):6} {sum(ll.values())/len(ll):8.4f} {'':>8} {'':>8} {base[1]:6.3f}  {en:4} {eh:.1%} / {eq:.1%}")
            continue
        keys = [k for k in ll if k in base[0]]
        a = [ll[k] for k in keys]
        b = [base[0][k] for k in keys]
        mu, sd, pw = sports.paired(a, b)
        gap = top_gap(rows)
        ok = (len(keys) >= sports.MIN_HOLDOUT and pw <= sports.MAX_P_WORSE
              and -mu >= sports.MIN_GAIN and gap <= base[1] + 0.01)
        print(f"{name:36} {len(keys):6} {sum(a)/len(a):8.4f} {-mu:+8.4f} {pw:8.2f} {gap:6.3f}  {en:4} {eh:.1%} / {eq:.1%}  {'PASS' if ok else 'fail'}")

    for title, args in (("Live", ()), ("Early K x1.5 for 6 games", (LIVE, 1.5, 6))):
      print(f"\n{title}, November-December picks at 70%+ (calibrated), all seasons on file:")
      for k, (n, w, q) in trailing_check(games, *args).items():
        label = "picked side behind .500 this season (3+ games)" if k == "trail" else "every other pick"
        if n:
            se = math.sqrt((q / n) * (1 - q / n) / n)
            print(f"  {label:48} {n:5}  landed {w/n:.1%}  quoted {q/n:.1%}  z {((w - q) / n) / se:+.1f}")


if __name__ == "__main__":
    main()
