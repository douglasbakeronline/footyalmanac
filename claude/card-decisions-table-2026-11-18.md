# The Card review's pre-registered decisions table (18 Nov 2026)

## Why

Eleven Card decisions are pre-registered across ten notes, each with its own
trigger and its own actor: some the next build session takes without asking
(the tennis tripwire, the context veto), some are Douglas's (rule 13 v rule 12,
the opposition floor his rule 13 dropped), some wait for the 30 Nov review.
The nightly review printed some of them in different sections and most not at
all, so a session had to read every note to know what was due. With the
30 Nov review twelve days off, one table now says, every night, where each
stands.

## What

`tools/card_review_post.decisions_section(rec, rep, hist)`, printed straight
after the live Card's 14 days. One row a decision: the trigger (copied from the
note behind it), where it stands tonight, the status (waiting, **due**,
**fired**) and who acts. A closing line in bold counts what is due or fired.

| decision | trigger | note |
|---|---|---|
| Tennis off the Card (any sport whose tripwire fires) | 50+ legs at the floor, z -2 or under | `card-tripwire-at-floor-2026-11-14.md` |
| The Card's floor line | 50+ settled groups, z -2 or under (`CARD_FLOOR_Z`, `CARD_FLOOR_N`) | `groupings.py` |
| Rule 13 v rule 12 | 30 Nov or 50 settled rule 13 groups | `card-rule13-model-only-2026-11-17.md` |
| Tennis floor back to 75% | 30 tennis Card legs under rule 10+, `tennis75` ahead at p(worse) 0.30 or under | `tennis-floor-85-2026-11-11.md` |
| Core leagues only again | 30 Nov, `m7core` ahead at p(worse) 0.30 or under | `card-wider-leagues-2026-11-11.md` |
| Opposition floor `m7opp5` / `m7opp9` | pool and both football-data seasons, 100+ legs | `card-m7opp-2026-11-15.md` |
| Context veto off | 30 settled "against" picks at or above the model | `context-check-2026-11-11.md` |
| The Daily 2x's rule | 50 settled slips, z -2 or under | `daily-2x-2026-11-17.md` |
| The List 2x as a method / the List long dropped | 30 settled each | `list-card-2026-11-17.md` |

One change of actor: `card-m7opp-2026-11-15.md` let a session set the
opposition floor live without asking if `m7opp5` or `m7opp9` passed the gate.
Rule 13 (17 Nov) removed that floor at Douglas's explicit call, so a pass now
goes to him, not straight to the page. The row says so.

## Tonight's read (pool replay run in the sandbox from the committed archives)

Nothing due or fired. The Card: 13 of 42 won v 14.33 expected, z -0.44,
-19.8% at the page's stakes. Rule 13: 0 of 2 settled v 0.67 expected;
`rule12` behind live on the pool (-0.89 a day, p(worse) 0.853, 39 legs).
No tennis leg at the 85% floor has reached the Card since rule 10, so neither
the tripwire nor `tennis75` (+0.07 a day, p(worse) 0.463) can be read yet.
`m7core` -0.76 a day (p 0.876). `m7opp5` -0.11 a day on the pool, ahead in one
football-data season of two. No context "against" pick has settled (the check
is paused to 1 Dec). Daily 2x 0 of 1; the List 2x and List long have built
nothing: across 16 to 19 Nov no non-college list pick carried a real price of
1.15+ (the international break's list was 1.01 to 1.14 where priced), so that
is the rule doing what it says, not a fault.

## Not changed

Every `CARD_*` constant, the page, the record. The table reads and prints;
it decides nothing. Tests: `tests/test_review_decisions.py`.
