# Tennis ratings gap: four months of results missing (8 October 2026)

Triggered by Daily List pick 13 on 8 Oct: Muchova 77.4% against Bartunkova
in the China Open quarterfinal. Bartunkova won. Douglas asked whether recent
form is missing from the model across sports.

## What was wrong

Not form as a feature: results. `tennis.json` is fitted on the Sackmann
archive (`tune_tennis.py`), which stops at tournaments starting 1 June (ATP)
and 2 June (WTA) 2026. The 8 Oct refit did not move that: the archive has not
been updated since. `build_tennis.py` then added only the last six days of
ESPN results before pricing. Everything between (the grass season,
Wimbledon, the North American swing, the US Open, most of the Asian swing)
never reached a rating, on either tour, for anyone.

Bartunkova had about 30 matches in that gap: Birmingham final, Wimbledon and
US Open third rounds, Montreal third round, Monterrey semi. The model saw
only her China Open wins.

| Muchova v Bartunkova, 8 Oct | P(Muchova) |
|---|---|
| June snapshot alone | 79.9% |
| As published (snapshot + 6 days) | 77.4% |
| Snapshot + every result since the archive | 73.6% |

With the results, Muchova is still the favourite but under the 75% tennis
list bar: a reserve pick, not a list pick.

The other sports do not have this gap: `history-sports/` is walked to
yesterday by every build, and football's current season is refreshed daily.

## The fix

`history-tennis/<tour>.json` keeps every completed ESPN singles result, topped
up each build (`HIST_RESCAN` 3 days re-read) and committed by `deploy.yml`
like `history-sports/`. A build starts from the `tennis.json` snapshot and
applies, in date order, every result after the archive ends:

- `tennis.json` carries the archive boundary per tour (`archive.through`,
  the last tournament start, and the pairs who met in tournaments that began
  in the 14 days before it). `tune_tennis.py --fit` writes it;
  `tune_tennis.py --boundary` added it to the current file without refitting.
- Results dated before `through` are the archive's. Up to `through` + 14 days
  a pair that met in the archive's last tournaments is the same match and is
  skipped. Walkovers are skipped, as the archive skips them.
- A failed ESPN day never marks the history walked, so it is fetched again.
- Each build starts from the snapshot, so nothing is applied twice.
- An older `tennis.json` without the boundary falls back to the six-day
  window, with a warning in the log.

First walk (8 Oct, by hand): 3,091 ATP and 4,305 WTA results from 16 May;
1,470 ATP and 2,563 WTA applied (the rest have a player with no rating, or
were in the archive). A repeat build gives identical prices. Tests:
`tests/test_tennis_history.py`.

## Evidence

`tools/tennis_gap_eval.py`: every match since the archive ends, priced from
results on earlier days only, both players rated. A = as built until today
(snapshot + 6 days). B = snapshot + every result since. Paired bootstrap.

| | n | A log loss | B log loss | B − A | p(worse) |
|---|---|---|---|---|---|
| WTA all | 2,563 | 0.6005 | 0.5962 | −0.0042 | 0.023 |
| WTA Jun-Jul | 1,236 | | | −0.0052 | 0.007 |
| WTA Aug-Oct | 1,327 | | | −0.0033 | 0.157 |
| ATP all | 1,470 | 0.6291 | 0.6256 | −0.0035 | 0.095 |
| ATP Jun-Jul | 727 | | | +0.0041 | 0.987 |
| ATP Aug-Oct | 743 | | | −0.0109 | 0.016 |

75%+ main-draw calls: WTA 351 at 87.2% (A) v 326 at 88.3% (B); ATP 145 at
82.1% v 142 at 81.7%.

Read honestly: better overall on both tours, clearly so for WTA and for ATP
since August. ATP is worse in June-July: ESPN carries no surface, so grass
results go in as hard-court results (the build has always done this for its
six days; now it does it for the whole grass season). A tournament-name
surface lookup was tried: a wash overall (better ATP, worse WTA), not
shipped. It needs revisiting before next June.

This is not a new model. `tune_tennis.py` tested a continuous Elo walk over
every result; the six-day window was a production shortcut that was never
tested and silently dropped data. B is the tested design.

## Form, tested and rejected

Two hot-form signals, chosen before looking, each on top of B:

- **More responsive Elo after the archive (K × 1.5):** worse on both tours
  (WTA +0.0011, ATP +0.0021 log loss; worse on every period but WTA Jun-Jul).
- **Wins already in this tournament** (logit + β × win difference), β fitted
  on June-August, checked on September-October: β fits to 0 on both tours.

Elo already is a form model: every result moves the rating, more for a
surprise. Beating Sabalenka moved Bartunkova a long way. What was missing was
the results, not a form term. Football form was re-tested 29 Sep with the
same answer (`claude/tuning-evidence.md`).

## Today's board (8 Oct 09:07 build v fixed)

Tennis list 8 -> 6 (same matches): Andreeva v Alexandrova 76.3% -> 66.9%,
De Minaur 76.9% -> 71.7%, both now reserve. Bergs moves up to reserve;
Humbert, Blockx, Khachanov, Cerundolo, Tsitsipas, Bai and Andreescu drop out
of reserve; Berrettini v Nakashima flips (58.5% -> Nakashima 56.6%).

## Open

- Surface for ESPN results: needed before the 2027 grass and clay seasons.
- The Sackmann archive has not updated since June. If it stays stalled, the
  history carries the ratings indefinitely; a refit adds nothing until it
  moves.
- Tennis list bands (`ACCURACY_BANDS`) come from the archive walk, which is
  the continuous design, so they describe B better than A.
