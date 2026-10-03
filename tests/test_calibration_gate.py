"""Regression tests for the calibration gate's baseline (3 Oct 2026).

    python3 -m unittest discover -s tests -v

A candidate calibration curve must beat the calibration the site is using
now (engine.CALIBRATION, from calibration.json), on the same fixtures, not
the flat engine.TEMPERATURE that the curve replaced. The flat constant is
the baseline only when no calibration is configured. Synthetic fixtures with
a known true curve; no network, no record.json.
"""
import contextlib, io, math, os, random, sys, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import engine as E
import tune as T

TRUE = {"a": 1.05, "b": -0.8}          # how the synthetic outcomes really behave
CANDIDATE = {"a": 1.05, "b": -0.4}     # better than flat 1.15, worse than TRUE


def _draw(rng, p, cal):
    t = T.curve_T(max(p), cal)
    q = [x ** (1.0 / t) for x in p]
    s = sum(q)
    r = rng.random() * s
    return 0 if r < q[0] else (1 if r < q[0] + q[1] else 2)


def synthetic_raws(n=4000, seed=7, cal=TRUE):
    """(home, draw, away, outcome) rows whose outcomes follow `cal`."""
    rng, out = random.Random(seed), []
    for _ in range(n):
        h = rng.uniform(0.25, 0.8)
        d = rng.uniform(0.15, min(0.35, 0.95 - h))
        p = (h, d, 1 - h - d)
        out.append(p + (_draw(rng, p, cal),))
    return out


def synthetic_rows(n, seed, cal=TRUE):
    """(lh, la, outcome) rows, the shape tune.lambdas returns."""
    rng, out = random.Random(seed), []
    for _ in range(n):
        lh, la = rng.uniform(0.6, 2.6), rng.uniform(0.4, 2.0)
        p = T.outcome(lh, la, E.RHO)
        out.append((lh, la, _draw(rng, p, cal)))
    return out


class LiveBaseline(unittest.TestCase):

    def test_configured_curve_is_the_baseline(self):
        with mock.patch.object(E, "CALIBRATION", dict(TRUE)):
            b = T.live_baseline()
        self.assertEqual((b["kind"], b["a"], b["b"]), ("curve", TRUE["a"], TRUE["b"]))
        self.assertEqual(b["source"], "calibration.json")

    def test_missing_calibration_falls_back_to_flat_temperature(self):
        raws = synthetic_raws(600)
        with mock.patch.object(E, "CALIBRATION", None):
            b = T.live_baseline()
            check, _ = T.gate(raws, CANDIDATE, b)
        self.assertEqual(b, {"kind": "flat", "T": E.TEMPERATURE,
                             "source": "engine.TEMPERATURE (no calibration.json)"})
        flat = T.mean(T.score_raw(raws, T=E.TEMPERATURE)[0])
        self.assertEqual(check["shipped"], round(flat, 4))

    def test_baseline_scores_exactly_what_engine_temper_publishes(self):
        raws = synthetic_raws(300)
        for cal in (dict(TRUE), None):
            with mock.patch.object(E, "CALIBRATION", cal):
                per, _, _ = T.score_under(raws, T.live_baseline())
                for (h, d, a, y), got in zip(raws, per):
                    self.assertAlmostEqual(got, -math.log(E.temper(h, d, a)[y]), places=12)


class Gate(unittest.TestCase):

    raws = synthetic_raws(1500)

    def test_beating_flat_but_losing_to_the_live_curve_fails(self):
        flat = {"kind": "flat", "T": E.TEMPERATURE}
        _, vs_flat = T.gate(self.raws, CANDIDATE, flat)
        self.assertTrue(all(vs_flat.values()), "precondition: candidate beats flat 1.15")
        with mock.patch.object(E, "CALIBRATION", dict(TRUE)):
            check, gates = T.gate(self.raws, CANDIDATE, T.live_baseline())
        self.assertGreater(check["delta"], 0)
        self.assertFalse(gates["worthIt"])
        self.assertFalse(gates["notWorse"])
        self.assertFalse(all(gates.values()))

    def test_identical_candidate_fails_minimum_gain(self):
        with mock.patch.object(E, "CALIBRATION", dict(TRUE)):
            check, gates = T.gate(self.raws, dict(TRUE), T.live_baseline())
        self.assertEqual(check["delta"], 0)
        self.assertEqual(check["shipped"], check["fitted"])
        self.assertTrue(gates["enoughData"])
        self.assertTrue(gates["notWorse"])
        self.assertFalse(gates["worthIt"])

    def test_candidate_and_baseline_score_the_same_fixtures(self):
        with mock.patch.object(E, "CALIBRATION", dict(TRUE)):
            check, _ = T.gate(self.raws[:400], CANDIDATE, T.live_baseline())
        self.assertEqual(check["n"], 400)
        self.assertFalse(T.gate(self.raws[:249], CANDIDATE, T.live_baseline())[1]["enoughData"])


class FitCalibration(unittest.TestCase):
    """fit_calibration end to end on synthetic seasons (lambdas patched)."""

    ROWS = {"fit": synthetic_rows(500, 1), "check": synthetic_rows(400, 2)}

    def run_fit(self, cal):
        rows = self.ROWS
        with mock.patch.object(T, "lambdas", lambda data, split, *a, **k: rows[split]), \
             mock.patch.object(T, "exclusions", lambda data, split: []), \
             mock.patch.object(E, "CALIBRATION", cal):
            return T.fit_calibration({}, verbose=False)

    def test_refit_identical_to_the_live_curve_does_not_ship(self):
        first, v0 = self.run_fit(None)
        self.assertEqual(v0["baseline"]["kind"], "flat")
        self.assertTrue(v0["pass"], "precondition: a fitted curve beats flat 1.15 here")
        again, v1 = self.run_fit(dict(first))
        self.assertEqual(again, first)
        self.assertEqual((v1["baseline"]["a"], v1["baseline"]["b"]), (first["a"], first["b"]))
        self.assertFalse(v1["gates"]["worthIt"])
        self.assertFalse(v1["pass"])

    def test_verdict_names_baseline_candidate_counts_and_exclusions(self):
        _, v = self.run_fit(dict(TRUE))
        self.assertEqual(v["baseline"]["describe"], "T = 1.05 + -0.8 x (confidence - 0.45)")
        self.assertEqual(v["candidate"]["kind"], "curve")
        self.assertEqual((v["fitSeason"]["n"], v["checkSeason"]["n"]), (500, 400))
        self.assertEqual(v["excluded"], {"fit": [], "check": []})


class SweepReport(unittest.TestCase):

    def test_sweep_baseline_is_the_live_configuration(self):
        rows = synthetic_rows(400, 3)
        out, paired = io.StringIO(), T.paired
        # the sweep's bootstrap is tested above; fewer resamples keep this quick
        with mock.patch.object(T, "paired", lambda a, b: paired(a, b, reps=100)), \
             mock.patch.object(T, "lambdas", lambda data, split, *a, **k: rows), \
             mock.patch.object(T, "exclusions", lambda data, split: []), \
             mock.patch.object(E, "CALIBRATION", dict(TRUE)), \
             contextlib.redirect_stdout(out):
            T.report({})
        text = out.getvalue()
        self.assertIn("baseline = the live configuration: T = 1.05 + -0.8 x "
                      "(confidence - 0.45) [calibration.json]", text)
        self.assertIn("flat TEMPERATURE (no curve)", text)
        live = T.mean(T.score_under(T.raw_probs(rows), T.as_curve(TRUE))[0])
        self.assertIn(f"log loss {live:.4f}", text)
        # the flat constant the curve replaced is a row to compare, not the baseline
        flat_115 = [l for l in text.splitlines()
                    if l.strip().startswith("flat TEMPERATURE") and f" {E.TEMPERATURE} " in l]
        self.assertEqual(len(flat_115), 1)


if __name__ == "__main__":
    unittest.main()
