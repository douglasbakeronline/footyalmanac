# The Daily List at William Hill (10 Nov 2026)

Douglas, 10 Nov 2026, 03:07, looking at 7 Nov (36 of 36 landed): "I search
for a lot of those games and they are not on William Hill." He places with
William Hill (`CARD_BOOK`). The Daily List takes no bookmaker input by his
standing decision, so the site had no way to say which list picks he could
actually back, and the list's record mixed picks he could place with picks
no UK book offers. This adds that, display and tally only.

## What the archive showed first (read only)

Pool archive, list picks 1 to 13 Nov (`groupings-archive/pool-*.json.gz`):

| sport | list picks | any UK book | William Hill |
|---|---|---|---|
| college basketball | 172 | 0 | 0 |
| football | 29 | 4 | 3 |
| tennis | 10 | 1 | 1 |
| NBA | 9 | 0 | 0 |
| NFL | 4 | 0 | 0 |
| rugby | 4 | 0 | 0 |

College basketball is most of the list on a busy night and the site had read
no UK price for any of it. ESPN's DraftKings line, its only source, carries no
UK book and skips the big mismatches altogether: nearly every college pick
was archived as the model's estimate. Every UK-books pass before today asked
only for legs that could reach a card (`books_wanted`: price 1.08-2.10, sports
on the Card), so a 1.02 list favourite was never looked up.

## What shipped

- **The list pass** (`groupings.price_odds_api(list_books=True)`, run last in
  `price`): every Daily List pick without UK books, in a sport The Odds API's
  UK region carries (`LIST_BOOK_SPORTS`: tennis, rugby, NRL and the US sports
  via `LIST_BOOK_KEYS`, `basketball_ncaab` among them), gets every UK book's
  price (`bookOdds`) and `ukChecked` once a UK slate was read for it. One
  credit prices a whole sport's slate. The pass spends only while the day's
  ledger is under `LIST_BOOK_DAY` (9 of `ODDS_API_DAY` 15) and re-reads a slate
  at most every `LIST_BOOK_TTL` (8 hours), so the Card's own passes keep their
  credits. The leg's own price, estimate flag and fair chance are untouched.
  Football list picks keep API-Football's bulk UK books (`af_prices`), as
  before; no football key is bought from The Odds API (one credit a league).
- **The pool archive** keeps `ukChecked` on a first write and `lastBooks` /
  `lastChecked` from later builds before the start (the first write never
  changes), so the record knows what a pick could be backed at.
- **The page**: each list pick carries a chip under its tested rate: `Hill
  1.04` (William Hill's price), `Not at Hill` (UK books price it, Hill does
  not; the tooltip names the best UK price), `No UK price` (a UK slate was
  read and did not list the game, or the name did not match), nothing when no
  UK slate was read. `groupings.list_books_page` writes the marks
  (`groupings-data.js` `listBooks`), from this build's legs and today's and
  yesterday's archive for started picks.
- **The filter**: "Show: Every pick / At William Hill" under the order toggle
  on the Daily List, remembered on the device. "At William Hill" shows only
  picks Hill priced, with a count of those left out per day.
- **The record**: `groupings-record.json` `listAtBook` (`list_at_book`):
  settled list picks from `LIST_BOOK_FROM` (10 Nov) split three ways (priced at
  Hill / UK books but not Hill / no UK price read), landed, quoted and, at
  Hill, the return on one unit at Hill's price; by sport; and a mark per pick
  for the last 21 days. "How it went", Daily List: an "At William Hill" tile
  beside the list's own tallies, and the chip on each list row of each day.
- **The nightly Card review** prints the same three-line table
  (`card_review_post.list_book_section`).

Tests: `tests/test_list_books.py` (Hill / not Hill / not found, one credit a
slate, off-list picks skipped, the list cap, the three-way record, tennis
keyed on the event, `lastBooks` on a later build with the first write kept,
the review table). Suite 696 OK; `nametest.py` clear. Page checked at 400
and 1280 wide on the live sports and tennis files with sample marks.

## What it cannot do yet

- It starts empty. The first real marks arrive with the first deploy build
  that has `ODDS_API_KEY` and credits left under the list cap; the record
  counts from 10 Nov. Past days before that show no chip.
- "No UK price" can be a name mismatch rather than absence: The Odds API
  spells US college teams much as ESPN does, but not always. A pick whose
  game Hill does price but whose name failed to match reads "No UK price",
  never "Not at Hill"; check one or two by hand in the first week, and add
  any spelling that misses to the matcher.
- Football list picks in leagues API-Football has no prices for show nothing
  (25 of 29 in the sample above). The Odds API could price them at one credit
  a league; not done, since the list's football is spread over many leagues.
- The Odds API's free 500 a month is shared with the Card. If the month runs
  short the list pass is what stops first, by design.

## 11 Nov 2026: the tally settled one pick in forty

The 11 Nov review (#235) showed 1 settled list pick since 10 Nov. US-sport
pool rows for 10 to 12 Nov were first written on 8 Nov, before `id` joined
`POOL_KEYS`, and `archive_pool` never adds to a first write, so `settle`
(US sport by id) left them pending. `list_at_book` now settles through
`groupings.settle_pool` (names and date within a day, moved from
`tools/card_replay.py`, which the replay already used), and `archive_pool`
copies a later build's `id` into a row that lacks one. At 11 Nov: 35 settled
(5 at Hill, all won, +2.0% at Hill's price; 15 not at Hill; 15 unchecked).
Far too few to read anything into.

## Not changed

The Daily List's admission, order and record; the model; the Card and every
`CARD_*` constant; `CARD_RULE`; any existing record line.
