# Postponed games dated inside the look-back (23 Nov 2026)

**Case.** The 23 Nov 00:10 UTC build's unplayed warning held two Brazilian
Serie A games dated 21 Nov, CA Mineiro v Corinthians and RB Bragantino v
Vasco, with no result in the ESPN cache through 22 Nov (both sides played on
19 Nov). The same build logged "rescheduled cze.1 / gr.1 / pt.1 / sco.1: 0":
those postponed games (Dundee United v Hearts, Atromitos v AEK, Braga v Gil
Vicente, Estoril v Marítimo, Slovan Liberec v Baník) are not yet listed in
the window, so 0 is the expected count, not a fault.

**Gap.** `build.fill_untimed` treated a row as postponed only once its date
was more than `window` (3) days before the build's start. A row inside the
look-back was matched only to an API-Football listing within 3 days of its
own date. A game postponed from a date inside the look-back to 4+ days later
fitted neither step, so it stayed off the board, the Daily List and the Card
until its first date aged past the look-back (one to three builds' days).

**Change.** A look-back row whose pair API-Football lists nowhere within 3
days of its date takes the rescheduled step: it moves when the pair is
listed exactly once in the window, the source holds no second unplayed row
of the pair, and (split leagues) the date is not past the file's last
fixture. A look-back row listed close by keeps the ordinary step; under
`postponed_only` (the Primeira Liga, the split leagues) it keeps the
league's own date, as before.

**Tests.** `tests/test_untimed.py` `LookBackPostponed` (five cases; two fail
on the old code). No API-Football key here: the first CI build is the live
check. If the two Brazilian games are relisted in the window, `untimed br.1`
counts them and they leave the unplayed warning.

**Not changed.** Any Card rule, model constant, or grading.
