# Tennis below its expected hit rate, second look (12 October 2026)

Alert: 59.5% picked winners against 61.7% quoted over 526 graded matches
(313 of 526). Follow-up to `claude/tennis-hit-rate.md` (5 Oct). Descriptive
only: nothing here is fitted on `tennis-record.json` (rule 1).

## What the record shows

z = (hits - sum of quoted p) / sqrt(sum p(1-p)), on the favourite's quoted p.

| Cut | n | Landed | Quoted | z |
|---|---|---|---|---|
| All | 526 | 59.5% | 61.7% | -1.07 |
| ATP | 225 | 63.1% | 62.3% | +0.25 |
| WTA | 301 | 56.8% | 61.3% | -1.63 |
| ATP main draw | 173 | 63.6% | 63.8% | -0.06 |
| ATP qualifying | 52 | 61.5% | 57.4% | +0.61 |
| WTA main draw | 229 | 55.5% | 60.9% | -1.7 |
| WTA qualifying | 72 | 61.1% | 62.4% | |

Surface is not stored (ESPN carries none; every archived price is Hard), so
surface below is assigned by tournament name for the autumn events: WTA hard
main draw 59.8% v 62.7% quoted (n=174, z -0.81); WTA clay main draw (Samsun,
Tolentino, Porto, Lisbon) 41.8% v 55.4% (n=55, z -2.04); ATP is all hard and
on target. By band, WTA 70-80% calls landed 59.1% of 44 against 73.4% quoted;
the Daily List itself landed 25 of 30 (83.3% v 83.3%).

## Reading

The overall gap is 1 standard error: noise. It is a WTA gap, and inside WTA
the one pocket that stands out is clay events priced with hard-court
ratings. That is a mechanism that fits (the 8 Oct note found the same
no-surface problem hurting ATP on grass), but it is one of seven cells picked
after looking, so z -2.0 is not evidence by itself.

## Test attempted: surface weighting

Not run. The honest test needs the Sackmann archive (`tune_tennis.py
--cache`, `tools/tennis_gap_eval.py`) and that host is unreachable from this
sandbox. The ESPN history has no surface, so assigning one by tournament and
scoring it on the same results would be tuning on the scoreboard's period.
The 8 Oct tournament-name surface lookup was already a wash overall (better
ATP, worse WTA). `surfaceWeight` 0.3 stays.

## Next step, for a session that can reach the archive

Run `tools/tennis_gap_eval.py` with a third arm: a tournament-name surface
(clay/grass/hard) for WTA results since June, scoring only WTA clay events,
paired bootstrap, gates from `CLAUDE.md` rule 3. Needs a surface source
before June 2027 regardless (open item in `CLAUDE.md`). Re-check this alert
after ~150 more WTA clay main-draw picks; autumn clay is a small slice of
the year.

No model number, code, record or archive changed.
