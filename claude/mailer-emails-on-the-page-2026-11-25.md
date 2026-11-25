# The emails on the Mailer tab (25 Nov 2026)

Douglas, 25 Nov 2026: the Mailer tab keeps the sign-up form, and under it shows
the emails that went out, a week back, in a horizontal scroll, every pick with
a tick or a cross, a summary of what each email recommended and how it went,
and a chart of how the picks are doing over the same span ("for now just a
week, and when we've got a month's worth we can change it to a month").

## What is built

- **Each sent email is kept.** `mailer.run` writes `mail-archive/<day>.json`
  (`mailer.keep` / `snapshot`) once a daily send goes out: the list as sent
  (time, pick, the model's chance, tested rate, price, ⭐, strongest five), the
  Daily 2x and Card groups with their legs, the Card's reason when there was
  none, the Edge picks. It is never rewritten. The mailer step runs after the
  archive commit, so deploy.yml's "Keep the sent email" step commits it from a
  separate worktree (the checkout's rebuilt dashboard.html is never reset).
- **`mail_page.py`** (after the mailer in deploy.yml) writes `mailbox.js`
  (gitignored): the last `DAYS` (7) UK days with an email, from `MAIL_FROM`
  (23 Nov, the first), today only from 07:00 UK. A kept day reads as **As
  sent**; a day before the archive began (23 to 25 Nov) is **Rebuilt** from
  the records: the list from daylist.json's pinned days in the email's 07:00 to
  07:00 window, college basketball kept only at a recorded price of 1.05+ (the
  email's William Hill rule cannot be read back), the groups from
  groupings-record.json, the settled Edge picks from record.json. Nothing is
  graded here; each result is the record's.
- **The page** (`renderMailbox` in index.html, loads `mailbox.js` when the tab
  opens): one card a day, newest first, scroll-snapped, `min(380px, 86vw)`
  wide, Newer / Older buttons and arrow keys on desktop, swipe on a phone.
  Each card: a summary strip (list landed, the Daily 2x and Card as Won / Lost
  pills, Edge landed), a sentence of what was recommended and how it went, the
  list (first eight, the rest in a fold), the Daily 2x, the Card, the Edge
  picks, every row ✓ / ✗ / • as on How it went. Picks also in a group carry a
  2x, Card or Edge tag. Under the carousel: the list's landed rate by day
  against the model's chance, and each card's running units at the page's
  stakes (Daily 2x one unit, the Card its stake, Edge one unit at the best
  price). `TREND_DAYS` (7) widens the chart to a month when there is one.

## First read (local, 25 Nov)

Three days, all rebuilt: 23 Nov list 10 of 10, Daily 2x won; 24 Nov 13 of 16,
Daily 2x lost, Edge 4 of 5; 25 Nov 2 of 2 settled, Daily 2x lost. No Card
group on any of them (the Card's last was 22 Nov).

## Not changed

The emails themselves, the sign-up form, the records, any card rule.
