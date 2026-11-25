# Graded football results against a second source (25 Nov 2026)

Issue #472 asks for every graded result to be checked against an independent
source. The runners cannot reach a new free source from a cloud session, but
the build already reads one: `periods.py` matches each graded football fixture
of the last 180 days to API-Football's cached day file (`odds.match_af`, both
names and the kick-off) for its half-time score. Until today a fixture whose
API-Football full time differed from the graded result was counted ("N
refused (full time disagreed)") and filed in `periods/missed.json`, never
looked at again. Each of those is either a wrong grade or a wrong match, and
nobody could see which.

## What it does now

- `periods/disagree.json`, keyed `league|date|home|away`: `graded`, `af` (the
  two scores), `fid`, `afHome` / `afAway`, `sim` (odds.name_sim of each name,
  so a loose pair reads as a likely wrong match).
- Kept while the record grades the fixture as it did; a regrade drops it and
  the fixture is tried again (an agreeing full time then keeps the half time).
- The build log names up to five ("periods: API-Football scores these graded
  results another way: ...").
- `tools/card_integrity.py` `result-disagrees`: a settled football leg of a
  staked slip (`staked`: the Card, the Daily 2x, the List card) from
  `DISAGREE_FROM` (25 Nov) whose fixture is in the file with both names at
  `DISAGREE_SIM` (0.8) or closer. An integrity finding opens the nightly
  office-backlog issue, so the threshold keeps loose pairs out.

## What it does not do

- Regrade anything. API-Football's `fulltime` excludes extra time and
  penalties, and a wrong match is possible at 0.5 similarity, so the file is
  for a person (or a session) to read, not a source of grades.
- Cover tennis or the US sports and rugby: their results come from ESPN only
  and no second source is on the runners. That part of #472 stays open.
- Look back: disagreements counted before today are in `missed.json` and are
  not retried. The first CI build's "periods:" lines are the first read.
