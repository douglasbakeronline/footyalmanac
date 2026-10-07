# Strong tier below expectation: noise, nothing changed (7 Oct 2026)

Office task: record.json shows Strong 78% landed vs 79% expected over 59 games.
Descriptive only; nothing was fitted on the record (Rule 1).

Rebuilt from `score.py`'s own loaders (all 5055 archived picks, results from the
same sources, no verification filter, so 59 Strong games and 45 hits, 76%, vs
79.1% quoted; the record's 46 of 59 uses the verified rows).

- Gap is 1.3 to 3 points. One standard deviation at n=59 is 5.3 points. Noise.
- Celtic's Law: 0 Strong rows (flagged rows are demoted a tier), so no signal.
- Draw risk: P(draw) < 15%: 28 of 34 (82% vs 84% quoted). P(draw) >= 15%: 17 of 25
  (68% vs 73%). Same direction, small, and draw-heavy misses are what the
  bands already price.
- Pick side: home 35/46 (76% vs 78%), away 10/13 (77% vs 82%).
- League: 14 misses, 10 drawn. Most are internationals (UEFA Nations 10/14, AFCON
  qualifying 5/9 vs 81% quoted). AFCON q: P(4+ misses of 9 at 19%) is about 7%,
  one of 15 groups looked at, so expected to turn up. Burundi v Algeria was
  already reviewed in `ranking-review.md`.
- Backtest guard (`tuning-evidence.md`): Strong quoted 78.1 vs landed 79.2, and
  no sign of overconfidence at Strong.

Verdict: no fix tested, because there is no pattern 14 misses can carry to the
gates (250 check fixtures). Re-check when Strong passes ~150 graded games; if AFCON
qualifying or friendlies stay 8+ points under quoted on 30+ games, test a
competition-specific band under `tune.py` gates.
