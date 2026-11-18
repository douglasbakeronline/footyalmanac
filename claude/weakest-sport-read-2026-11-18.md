# The weakest of the other sports, read 18 Nov 2026 (Theo)

Task: find the sport or tour furthest below its expected hit rate with enough games, test one fix.

## Read (sports-graded.json, 1,536 picks; tennis-record.json liveBands)

Landed v quoted, all picks:
- NFL 104: 61.5% v 65.0% (z about -0.7). 60-70% band 32 picks, 53% v 65%, z -1.4.
- College football 358: 67.3% v 70.0%. 70%+ bands 182 picks, about 75.8% v 80%, z about -1.4 (already off the list, `sports.LIST_OFF`).
- Baseball 54: 50% v 55.9% (small; the 55-60% band landed 67.6%).
- NBA 205 69% v 65%, college basketball 710 80% v 77%, rugby 90 72% v 69%: at or above quote.
- Tennis: ATP 63.2% v 63.5% (551), WTA 64.2% v 64.3% (916). Worst live band WTA 60-65% (57.4% v 62.5%, z -1.3 on 162) and 70-75% (67.5% v 72.4%, z -1.0 on 83); neighbours sit above quote.

## Result

No sport or tour is under quote by two standard errors on 50+ picks, so there is nothing to fix and no test to run. Any change would be fitted to noise and break Rule 1 (the record is the scoreboard). No code or model changed.

## Watch

NFL mid band (60-70%) and college football 70%+ if either reaches z -2 on 50+ picks. The college sides already have the Away / Neutral mark and Behind .500 mark (`claude/college-side-mark-2026-11-15.md`).
