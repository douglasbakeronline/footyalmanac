# The Championship's API-Football spellings (20 Nov 2026)

## What the 11:05 UTC build showed (run 44724616939)

The first CI read after #441 (`claude/retime-championship-seriea-2026-11-20.md`):

- `untimed it.1: 13 fixture(s)`, `untimed en.1: 13`, `es.1: 19`, `tr.1: 16`, `br.1: 18`: Serie A under
  `AF_RETIME` works, Bologna v Udinese left the "football kickoff:" line.
- No `untimed en.2` line. In its place: `::warning::en.2: API-Football kick-offs not used, club names
  unmatched: QPR; Sheffield Utd`. All or nothing on names (Rule 6), so no Championship row was retimed and
  "football kickoff: 2026-11-21 Championship (England): Sheffield United v Watford board 12:30 UTC,
  API-Football 15:00" was still there, the leg unpriced.
- The other 22 Championship clubs matched as API-Football spells them.

## The change

`sources.ALIASES` adds `"sheffield utd": "sheffield united"` and `"qpr": "queens park rangers"` (beside the
existing `"sheff utd"`). Both are exact aliases to one club; Sheffield Wednesday and Queen's Park are
unaffected. `tests/test_untimed.py`: both names match the Championship pool, and Sheffield United v Watford's
12:30 takes API-Football's 15:00 under `fill_untimed(retime="eng")`.

## Also read on that build

- "football Card unpriced: 2": OL Lyonnes v Strasbourg (D1 Arkema, 74%) is no longer under `noFixture`, so
  the #439 spelling matches; it is unpriced because no source prices it. Vancouver Whitecaps v Real Salt Lake
  (MLS, 64%) the same. Nothing to fix.
- `noFixture 1`: NWSL Washington Spirit v Kansas City Current, not Card-reachable.

## Not changed

Any Card constant, the 90-minute guard, the matcher's rules, the model. No local build could fetch (sandbox).

## What the next session should read

The next CI build's "untimed en.2: N fixture(s)" line with no warning, and Sheffield United v Watford gone
from "football kickoff:".
