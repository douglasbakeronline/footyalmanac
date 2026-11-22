# A played match dated on its round's day inside the build window (22 Nov 2026)

**Found.** The 02:11 UTC build of 22 Nov named one football `noFixture` leg:
La Liga, Athletic Club v RCD Espanyol de Barcelona, dated 22 Nov. The match
was played on Friday 20 Nov (0-1, in the committed ESPN cache). The same build
logged `lag es.1: ... 5 with no fixture to fill` and `lag tr.1: ... 4`.

**Cause.** openfootball dates La Liga and the Süper Lig by round (the Sunday,
22 Nov) with no kick-off. `build.fill_lagging` filled a result only into a row
dated *before* the build window, so a Friday or Saturday result whose row sat
on the round's Sunday (the build day) found nothing to fill. Then
`fill_untimed` (API-Football asked from the day before the window) moved the
four Saturday rows to 21 Nov, out of the window, still unplayed; Friday's
Athletic v Espanyol had no API-Football fixture from 21 Nov on, so it stayed
on the 22 Nov board as unplayed, untimed, and was asked a price.
Effects for a day or two until the round date passed: nine results missing
from the ratings (and from `tune.load`'s check season, which uses the same
rule), and one played match on the board.

**Fix.** A result dated before the window now also fills its pair's unplayed
row dated up to `build.AHEAD_DAYS` (3) days into the window, and that row takes
the date it was played. Rows dated before the window are still chosen first;
a result after the cut is still ignored; names stay all or nothing.

**Read on the committed cache and the live openfootball files (22 Nov):**

| league | filled before | filled now | unplaced before | unplaced now |
|---|---|---|---|---|
| es.1 | 50 | 55 | 5 | 0 |
| tr.1 | 63 | 67 | 4 | 0 |
| br.1, pt.1 | 74, 35 | unchanged | 1, 1 | 1, 1 (another cause, not chased) |
| en.1, it.1, de.1, fr.1 | | unchanged | 0 | 0 |

The nine: Athletic Club 0-1 Espanyol (20 Nov); Rayo 0-1 Valencia, Real Madrid
2-1 Celta, Alavés 3-1 Deportivo, Sevilla 1-1 Betis, Gençlerbirliği 1-0
Gaziantep, Galatasaray 2-1 Samsunspor, Amed 0-2 Rizespor, Kocaelispor 2-2
Fenerbahçe (21 Nov).

**For the Card.** La Liga and the Süper Lig are core leagues, so the Card can
take their weekend games. A Sunday pick now carries its own Friday and
Saturday results, and the board no longer asks a price for a match already
played.

**What to check.** On the next CI build, `lag es.1` and `lag tr.1` with no
"no fixture to fill" on a weekend, and no played La Liga match under
`football noFixture:`.

Files: `build.py` (`fill_lagging`, `AHEAD_DAYS`), `tests/test_lagging_results.py`.
