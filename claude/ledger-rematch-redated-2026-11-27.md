# The results ledger: rematches and re-dated rows (27 Nov 2026)

Found while reading the 25 Nov Card 2x the archive lost (Warriors, Grizzlies,
Toluca): the ledger's ungraded report listed 193 picks to chase, most of them
Premier League, La Liga, Süper Lig and Brazilian games that had been graded.
Two faults in `ledger.py`, both in how copies of one pairing become rows.

## 1. A re-dated fixture left its old row behind

A row's key carries its start date. When a fixture's latest copy moved (a
round's nominal date, then the day it was played: Liverpool v Manchester
United archived for Saturday 21 Nov 15:00, played Sunday 22 Nov 16:30), the
build wrote the new key and the merge kept the old one, pending, for good
("merged and never trimmed"). 199 football rows on 26 Nov.

Now `merge` drops an old **pending** row whose key the build no longer writes
when the build has a row of the same pairing within `MOVE_DAYS` (10) of it.
A row with a result is never dropped; a row whose sources are gone (no new
row of the pair) is kept, as before.

## 2. Two meetings of a pair within 10 days were one fixture

Copies of a pairing within `MOVE_DAYS` were clustered as one fixture moved,
whatever the competition. A cup tie and a league game a week apart, a
two-game friendly series, a league that meets twice (Andorra), a play-off
(Peru) became one row: the later meeting decided the key and read the
results of every date in the cluster, earliest first. So:

- Inter Club d'Escaldes v Casa de Portugal (29 Nov) and Sport Huancayo v
  Universitario (28 Nov) were settled before kick-off with the first
  meeting's result, and the first meeting was counted again under its own
  key: a double count and a future game graded.
- Tahiti v Cook Islands (17 Nov) was graded 4-0 won from the 14 Nov game; it
  was 3-3.
- 15 first meetings (cup ties beside league games, mostly) were left pending
  and never counted.

Now `predictions(played=)` splits a cluster when a copy was published after
a graded copy of the pair kicked off, on a start `REMATCH_DAYS` (2) or more
later: that copy is the next meeting. Under two days it stays one fixture
(Atletico Hidalgo v Racing de Veracruz 2, a 16:00 copy and an 00:00 copy of
one game). And `merge` never keeps a result for a start still to come.

## The read on the 26 Nov files (rebuilt locally, nothing fetched)

| | before | after |
|---|---|---|
| rows | 20,292 | 20,112 |
| won / lost | 9,536 / 7,875 | 9,548 / 7,880 |
| pending | 2,822 | 2,625 |
| ungraded, to chase | 193 | 86 |
| Daily List settled | 806 (88.21% v 86.86%) | 808 (88.12% v 86.84%) |

22 rows changed result: 19 first meetings gained their own result, 2 future
games lost a borrowed one, Tahiti's 17 Nov flipped from won to lost. No pair
has two settled rows with one score inside 10 days after the change.

## What it touches

The ledger feeds `slip.py`'s band rates, the mailer's weekly record and the
nightly reviews' ledger reads; the changes are a dozen settled rows in
17,400, so no rate moves by more than a tenth of a point. `score.py`, the
record, the Card and every grade on the page are unchanged: this is the
ledger's own grouping of the archive (Rule 1: nothing graded or fitted from
it).
