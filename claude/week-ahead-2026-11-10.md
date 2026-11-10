# The week ahead, on top of Bets (10 Nov 2026)

Douglas, 09:07: "I need a 7 day forecast looking ahead. A section to sit on
top of the bets tab ... clear insight into what days will have what bets. A
nice infographic. I believe every day there will be at least 1 bet to make.
Bend all rules but keep the accuracy. Same sport is ok, we don't need to
align to the bookies. We just need to rely on the model and its accurate
performance."

## What shipped

`index.html`, `weekAhead` / `weekDays` / `weekRecord`, above the Card:

- Seven day cards: pick count, a sport bar scaled to the busiest day, the
  strongest model bet and its chance. Phone: a swipeable strip.
- For the chosen day, the **Model treble** (top three list picks still to
  start, by the list's own order: confidence) and **Model double** (top two),
  the product of the model's numbers as the chance, William Hill chips and a
  combined Hill price when every leg has one. A single on a one-pick day.
- The same rule's record from the graded list (`listReviewDays`, published
  before the start), loaded with the records when Bets opens.

Nothing is padded: a day with no list pick says so. Display only: not
staked, pushed or archived as a group. The Card and its rules are unchanged;
it is still the one rule with evidence of beating the price.

## What was said to Douglas, and why

The model is accurate: list picks land as quoted (How it went, "Is the list
honest?"), and on the graded list the top-two double and top-three treble
land at or a little above their quote. Accuracy is not return. List picks
are priced around 1.10 with a 5% margin, so a treble of them pays about 1.3
and carries the margin three times; on ten days of real prices list
accumulators returned -32% at three legs (`claude/list-accas-2026-11-10.md`).
The panel says so in one line and shows the Hill price where there is one.

## Open

- The model groups are not archived as groups; their record is derived from
  the graded list each time. If they are to be bet regularly, archive them at
  first start (as the Card is) so the record cannot drift with the list's
  ordering.
- Football legs are in the panel on the live site (the test page had no
  football data file).
