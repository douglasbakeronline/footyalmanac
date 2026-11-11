# Card tennis legs: 8 of 15 since 29 Oct, 23 of 41 in all (11 Nov 2026)

HQ planner (11 Nov) flags tennis legs on the Card: 8 of 15 landed (53%) against
11.5 expected (76% quoted), z -2.1. Result: **nothing to ship**. The same
question was closed on 30 Oct and 6 Nov (`tennis-legs-gap-2026-10-30.md`,
`tennis-legs-gap-2026-11-06.md`); the new fact is the count.

## Where it stands (locate only, Rule 1)

`groupings-record.json` `cardLegsBySport` at 11 Nov, full rule: tennis 23 of 41
(56%) v 71% quoted, 29.1 expected, z -2.13, `tripwire` false. The tripwire needs
50 legs; 9 more are to come (about one a day since rule 6, and fewer since the
model rule, so mid to late November). NBA 26 of 34 (z +0.72), football 22 of 30
(z +0.71) land above quote, so the Card's sport mix is not the problem.

## Why no rule

- The 15 legs since 29 Oct have a standard error of about 11 points; any cut
  (competition, price, home or away, opposition price) leaves cells of 3 to 8
  legs. Choosing one would be fitting on the scoreboard.
- No tennis price history exists, so a price, gap or opposition rule cannot be
  replayed on past seasons paired and bootstrapped (Rule 3 gates unreachable).
  The pool holds 56 settled priced tennis legs since 30 Oct, too few and the
  same period.
- The model-only floor (75%, `CARD_SPORT_MIN`) is already live and the
  Daily List's tennis bar was raised for ATP on its own-band evidence
  (`tennis-list-own-band-2026-11-06.md`).
- The sport-off rule (two standard errors under on 50+ legs) has not been met:
  41 legs. Taking tennis off now would break the delegated tripwire.

## Do next

The next session after tennis reaches 50 full-rule legs reads `cardLegsBySport`
and, if z is -2.0 or lower, adds `"tennis"` to `CARD_SPORTS_OFF` (CARD_RULE
bump, note, release) without asking. If z has recovered, leave it. Split by
tour and by price band only at that count, and only to locate, not to fit.

## Not changed

`CARD_SPORTS_OFF`, `CARD_SPORT_MIN`, `CARD_RULE`, any code or record file.
