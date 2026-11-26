# The European blind spot, and why domestic cups stay off (26 Nov 2026)

Douglas, 26 Nov, after Ajax v Thun (87%) sat off a thin Thursday list:
"We need to remove the blind spot. There must be a way of predicting European
cup fixtures from different leagues. Cup fixtures need to be on the daily list
if they pass the bar."

## How cup ties reach the list today

- **European ties** (eu.cl, eu.el, eu.ec) list at the league bar (80%) like any
  league game. They carry Celtic's Law only when one side's league is outside
  the European strength fit, `europe.json` (`build.py` `fitted_pair`). Inside
  the fit they are priced on fitted league strengths: five have listed this
  autumn.
- **Domestic cups** (API-Football, `S.AF_CUPS`) list only when the cup replay
  passes the list's own rule: calls at the bar landing 80%+ in testing, 30+
  calls in each window (`cup_gate`, `CUP_LIST`). That is already "on the list
  if they pass the bar"; they have not passed.

## Domestic cups: the evidence says no

`tools/cup_calibration.py` on the replay's 2,496 priced ties (1 Jan to 25 Nov,
fit before 1 July, check after): the raw model's 80%+ cup calls landed 76% of
46 on the check half (quoted 86.8%), its 70%+ calls 66.5% of 155 (quoted
78%). With the live cup calibration almost no tie reaches 80%; at T 1.4, 12
check calls did, 10 landed. No cup clears 30 calls at 80% in a window, so
none can pass, and removing the flag would put picks on the list that land
under their number (Rule 9, Rule 10). The cup replay keeps running every day
and lists them by itself the day they pass. A cup recalibration (T 1.4) is
better on the fit half but fails p(worse) on the check (0.33): not shipped.

## European ties: the fit was missing leagues

`eurotest.py --skips` (new) names every tie the fit could not price, run in CI
by `.github/workflows/eurotest.yml` (the sandbox cannot reach the domestic
sources). On the CI run of 26 Nov:

- **Switzerland** matched in full but was not in `europe.json`: the file was
  last fitted on 11 Sep, when the Swiss clubs did not match. Every Swiss tie
  (Ajax v Thun) carried the flag for that alone.
- **Monaco** (10 ties a season) had no league: its country tag was not mapped
  to Ligue 1. Mapped (`MON`, `MCO` -> fr.1).
- Still outside: Israel (no Israeli club matched, 18-24 ties a season), a few
  clubs in Finland, Ukraine, Hungary, Romania, Poland and Georgia, and
  countries with no league on file (Kazakhstan, Kosovo, Andorra, Gibraltar,
  San Marino, Liechtenstein, 84 ties a season). Each is a matching or source
  job, listed by `--skips`.

## The refit

`python3 eurotest.py --fit`, run in CI by hand (the workflow's `write` input),
fit 2024-25 (797 ties), check 2025-26 (471 ties): log loss -0.0281 against the
shipped frame (sd 0.0093, p(worse) 0.001), 53.7% correct; 70%+ calls landed
80% of 30 (quoted 76.5%). The gates (Rule 3: 250+ check, p(worse) <= 0.30,
gain >= 0.0005) pass. 47 leagues, Switzerland added. `europe.json` is the file
the tool wrote, committed by hand at Douglas's instruction (Rule 5: a
structural file moves only when a human commits it).

On the live record the sample is small: 12 European picks at 70%+ unflagged,
9 landed (75% v 81.8% quoted). Watch the European rows in "How it went".
