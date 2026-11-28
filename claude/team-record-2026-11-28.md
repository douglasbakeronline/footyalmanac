# The model's record on every team (28 Nov 2026)

Douglas, 28 Nov 2026, with a screenshot of another site's per-team "accuracy
record" (accuracy, correct tips, tips evaluated, last ten as dots): "Can we
develop this feature? Where every team in sports fixtures has an accuracy
rating of how the model performed for them in every fixture they've played?"

## What was built

`teamrecord.py`, run by deploy.yml after the ledger step on every build, writes
`team-record.js` (gitignored, 345 KB raw, 94 KB gzipped, loaded after the first
paint with scale.js and racing.js). For every club, side and player:

| Column | Meaning |
|---|---|
| `n` | graded fixtures it played in |
| `right` | of those, the model's call landed (strict: the picked result happened) |
| `quoted` | what the model expected to get right: the sum of its quoted chances |
| `backed`, `backedWon` | fixtures where this side was the pick, and how many it won |
| `against`, `againstRight` | fixtures where the other side was the pick, and how many of those calls landed |
| `last` | the last ten calls, oldest first, 1 right and 0 wrong |
| `from`, `to` | its first and latest graded fixture |

A draw call counts in `n` and `right` and in neither split. Sources: the three
graded files (`record-graded.json`, `tennis-record.json` "graded",
`sports-graded.json`), nothing regraded. At 28 Nov: 4,528 football identities,
613 tennis players, 650 sides in the other sports. Football rows are written
only for the names in the newest three archive days (the board and the days
just played); the other sports and tennis are written whole.

On the page (`teamRecBlock`, `teamRecCard` in `index.html`): an open row, every
sport, shows a block under the team sheets, "The model's record on each side",
one card a side with four tiles in the scoreline's idiom: Called right (green
at or above what the model expected, red under, grey with "too few to read"
under `MIN_READ` 10 fixtures), Model expected, When backed, Last 10 as dots.
Nothing on the closed row. A side with nothing graded says so; a page built
without the file shows no block.

## Who is one team

The hard part, and Rule 6 applies: a wrong join is worse than a missed one.

- Names are compared in `sources._norm` form inside a scope: a country's men's
  game, its women's game (`en.w1`, `es.w1`, `fr.w1`: 33 women's sides on the
  record share a name with a men's club, Arsenal and Real Madrid among them),
  senior internationals, or one competition alone (youth leagues, women's and
  youth internationals).
- Two spellings in one league join only when `score._same_club` matches them
  both ways, `score.distinct_names` does not show them apart, they have never
  met, and they never play different opponents within `NEAR_DAYS` (2). On the
  record that joins 14 pairs, all checked by hand (Southend / Southend United
  and four more National League sides, Ried, Konyaspor, Alanyaspor, Amed,
  Çorum, Aris, Asteras Tripolis, Iraklis, Volos) and refuses Independiente /
  Independiente Rivadavia, Guinea / Equatorial Guinea, CSKA Sofia / CSKA 1948,
  Naft / Naft Maysan.
- One name in two leagues of a country is one club (the Süper Lig as `tr.1`
  and `af.203`, the Pro League as `be.1` and `af.144`) unless the two play
  different opponents within two days: FC Andorra (LaLiga 2) and Andorra CF
  (Tercera) stay apart, as do the Serie D namesakes of Milan and Palermo.
- A cup tie joins the league record only when exactly one club in the country
  carries the name, or exactly one is written that very way (AC Milan beside
  Serie D's Club Milano); a continental tie the same across every country
  (Bayern's 14: ten Bundesliga, one Pokal, three Champions League, under two
  spellings). Otherwise the cup rows stand alone.
- `Clubs.joined` lists every join for review.

## A finding on the scoreboard

Ten graded football rows are a second copy of a match under another
competition code: `tr.1` and `af.203` on 9 to 11 Oct (6), `be.1` and `af.144`
on 20 and 21 Nov (2), `es.cup` on 27 Oct (2). `score.drop_duplicates` joins
copies within one league code only. The team record counts each once
(`Tally.add`); `record-graded.json` still counts them twice (10 of 15,593).
Not fixed here: it is a grading change with its own guards.

## Does a team's record say anything about its next game?

Tested before shipping, because a number beside a pick invites that reading.
`python3 teamrecord.py --check`: walk-forward on the football record, every
pick at 55%+ whose two sides each had six graded fixtures before that day, by
how far the model had run above or under its quote on those two sides.

| The two sides' earlier record v quote | Picks | Landed | Quoted | z |
|---|---|---|---|---|
| 10+ points under | 111 | 62.2% | 61.7% | +0.11 |
| 0 to 10 under | 160 | 68.1% | 63.2% | +1.31 |
| 0 to 10 over | 241 | 68.5% | 63.8% | +1.52 |
| 10+ over | 257 | 71.2% | 65.1% | +2.08 |

A lean in the expected direction and no more: 769 picks over 100 days, the top
and bottom bands about one standard error apart, and it is a read of the
scoreboard, which nothing may be fitted on (Rule 1). So the block is display
only and says so on the page. What would make it more: the same signal on the
replay (`predictability.py` on 2025-26, never the record), then the gates.
Until then no chip on the closed row, no filter and no card rule reads it.

## Not done

- No page listing every team (a search or a league table of records).
- Pinned and played rows, How it went and the emails do not show it.
- No "last 90 days" window: the record starts on 20 Aug 2026, so all of it is
  shown; a window earns its place once there is a season behind it.
- Horse racing has no sides.

## Roll back

`git revert` the merge. `team-record.js` is rebuilt, never committed.
