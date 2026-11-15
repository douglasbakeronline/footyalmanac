# ATP below quote: surface not retested, nothing to ship (15 November 2026)

HQ planner task of 15 Nov (ATP 171 of 290 landed, 59% v 64% quoted, z -2.0, 28 days). Third issue of
the surface idea (13 Oct, 27 Oct, 9 Nov). Checked first, as the task asks:

- The tournament-to-surface map was tested and rejected on both tours
  (`claude/tennis-surface-test-2026-10-13.md`: ATP +0.0031 log loss worse, p(worse) 0.95, n=1,523;
  ATP grass events +0.0142, p 0.996; only ATP clay improved, -0.0099, p(worse) 0.13 on 187 games,
  under the 250 gate).
- No free automatable surface source (`claude/tennis-surface-source-2026-10-27.md`,
  `claude/tennis-surface-recheck-2026-11-09.md`: Sackmann 2026 files 404, tennis-data.co.uk 403,
  ESPN carries no surface field).
- The live window is 18 Oct to 15 Nov: Asian swing, indoor hard Europe and the tour finals. Every
  event is hard court, which is what every result is already rated as, so a surface map changes no
  price or rating in the period the gap sits in. Surface cannot be the cause of this shortfall.

No new test was run: nothing new exists to test, and the live record is not a fit target (Rule 1).
z -2.0 on one sport-and-tour cell picked after looking is also within what 20+ cells produce.
Tennis stays off the Daily List per `build_tennis.LIST_ON` rules and the Card at 85%+.

Planner: stop issuing the surface task until a surface column CI can fetch exists (revisit March
2027, before the clay swing). A different idea worth a task: ATP landing by round and by rating-gap
band on history, not surface.
