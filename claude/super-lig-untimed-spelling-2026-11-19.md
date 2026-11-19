# The Süper Lig's kick-offs: one spelling (19 Nov 2026)

## What the first CI build with the untimed fill showed

`build.fill_untimed` (#425, #417) shipped this afternoon. The 16:28 UTC build
(run 44565906389) logged:

- `untimed br.1: 11 fixture(s) took API-Football's date and time`
- `untimed es.1: 15 fixture(s) took API-Football's date and time`
- `##[warning]tr.1: API-Football kick-offs not used, club names unmatched: Erzurumspor FK`

So La Liga and Brazil's Serie A now carry real days and starts (Athletic v
Espanyol moved from the round's nominal 22 Nov to 20 Nov 20:00 UTC; Real
Madrid v Celta to 21 Nov 20:00), and the Süper Lig did not: all nine tr.1 rows
in `predictions/2026-11-19.json` still have no kick-off. The fill is all or
nothing on names (Rule 6), and one club, API-Football's "Erzurumspor FK"
(the board's "BB Erzurumspor"), matched nothing. `_norm` keeps the "fk", so
containment never reaches "bb erzurumspor"; the ESPN alias "erzurum bb" did
not cover it.

## Why it matters for the Card

A football leg with no start time is refused by the Card (#416), and two
Süper Lig games were "moved" on the same build's pricing line
(`football moved: Super Lig: Galatasaray v Samsunspor on 2026-11-22,
API-Football 2026-11-21; Kocaelispor v Fenerbahçe ...`): the board's nominal
date is a day off, so neither is priced. Both are the kind of strong home or
away favourite the Card's rule reaches. With the spelling, the fill moves the
round to its real days and times, and those legs are priced and timed.

## The change

`sources.ALIASES["erzurumspor fk"] = "bb erzurumspor"`, with the pair added
to `tests/test_lagging_results.py`. No other tr.1 name was reported unmatched,
and no two names mapped to one club.

## Checked and left alone

The stale nominal-date copies the earlier builds archived (e.g. Athletic v
Espanyol on 22 Nov, published 16:07, beside the timed 20 Nov copy) do not
double-grade: across the whole archive, 772 pairs sit on two dates within 10
days; only 5 have both copies graded, all friendlies played twice. The other
copy is never matched to a result (`score.py` keys on the date), and the
ledger and `pool_rows` already keep one row a moved fixture.

## What the next CI build should print

`untimed tr.1: 9 fixture(s) took API-Football's date and time`, no tr.1
warning, and no Süper Lig games under "football moved:". If another spelling
shows, add it the same way.
