# Damping the FIFA ranking's big lifts: tested, rejected (12 Nov 2026)

Douglas, after the Wary internationals on 12 Nov (Egypt, Belarus, Nigeria,
Ivory Coast, Slovakia, Guinea, Cameroon): "can you make the accuracy
better?"

## The problem

`rankings.adjust_fifa` re-scores a ranked international's pick with the FIFA
points gap. Overall it helps (`claude/world-rankings.md`; on 2022-24 -0.0099
pick log loss, p(worse) 0.012), but when it lifts a pick 20+ points it
overshoots: 44 such picks in Oct 2022-Oct 2024 quoted 73.0%, landed 65.9%.

## What was tested (`tools/fifa_lift_damping.py`)

Eleven variants, pre-registered: shrink every lift to 60/70/80/90%; cap the
lift at 8/10/15/20 points; keep the first 10 points and shrink the rest to
30/50/70%. Fit on Oct 2022-Sep 2023 (786 ranked win picks), check on Oct
2023-Oct 2024 (1,247), pick log loss against the live adjustment, paired
bootstrap (ranktest.py's data and quarterly-refitted ratings).

| Best on the fit half | Fit | Check |
|---|---|---|
| cap at 15 points | -0.0004 (p 0.36) | +0.0000 (p(worse) 0.53) |

No variant beats live on the fit half by the gain bar (0.0005); the ones that
help on the check half (shrink to 80-90%, -0.0009 to -0.0012) are worse or
level on the fit half. The big-lift band is real but small (29 picks in the
check half), and damping it costs as much in the 15-20 point band (which
landed above quote, 75.6% v 71.6%) as it saves. Rejected under the gates.

## What stays

The Wary mark on a pick the ranking carried is the right treatment: it tells
the bettor the two readings disagree. Its real chance sits between the
model's own number and the adjusted one.

## Not tried

Refitting `FIFA_W` with a saturating gap term on 2022-26 together: needs the
2024-26 FIFA releases joined into the harness (Dato-Futbol's archive ends Sep
2024).
