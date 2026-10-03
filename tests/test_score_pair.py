"""Regression tests for the evaluation scorer (evaluation/score_pair.py) and
the harness's snapshot check (evaluation/predict.py). Standard library, no network.
Insufficient evidence must never read as a pass."""
import json, os, random, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "evaluation"))
import score_pair as S
import predict as P


def fixtures(n, split, rng, sharp=0.0, seed_y=None):
    """n fixtures whose outcome is drawn from a 'true' distribution; sharp>0 moves the candidate toward it."""
    out = {}
    for i in range(n):
        t = [rng.uniform(0.2, 0.6), rng.uniform(0.2, 0.3)]
        t.append(max(0.05, 1 - sum(t))); s = sum(t); t = [x / s for x in t]
        y = rng.choices([0, 1, 2], weights=t)[0]
        out[f"{split}|x|2026-01-{i:05d}|H{i}|A{i}"] = {"split": split, "y": y, "true": t}
    return out


def as_rows(fx, sharp):
    rows = {}
    for k, v in fx.items():
        flat = [1 / 3] * 3
        p = [(1 - sharp) * f + sharp * t for f, t in zip(flat, v["true"])]
        rows[k] = {"key": k, "split": v["split"], "y": v["y"], "p": p}
    return rows


class Scorer(unittest.TestCase):
    def setUp(self):
        rng = random.Random(1)
        self.fx = {**fixtures(400, "fit", rng), **fixtures(600, "check", rng)}

    def test_better_candidate_passes(self):
        ev = S.compare(as_rows(self.fx, 0.2), as_rows(self.fx, 0.9))
        self.assertEqual(ev["verdict"], "pass", ev["reasons"])

    def test_worse_candidate_fails(self):
        ev = S.compare(as_rows(self.fx, 0.9), as_rows(self.fx, 0.0))
        self.assertEqual(ev["verdict"], "fail")

    def test_identical_is_na(self):
        r = as_rows(self.fx, 0.5)
        self.assertEqual(S.compare(r, json.loads(json.dumps(r)))["verdict"], "n/a")

    def test_tiny_gain_is_insufficient(self):
        ev = S.compare(as_rows(self.fx, 0.500), as_rows(self.fx, 0.501))
        self.assertEqual(ev["verdict"], "insufficient")

    def test_too_few_check_fixtures_is_insufficient(self):
        fx = {k: v for i, (k, v) in enumerate(self.fx.items()) if v["split"] == "fit" or i % 4 == 0}
        ev = S.compare(as_rows(fx, 0.2), as_rows(fx, 0.9))
        self.assertEqual(ev["verdict"], "insufficient")
        self.assertTrue(any("check fixtures" in r for r in ev["reasons"]))

    def test_different_keys_hold(self):
        b, c = as_rows(self.fx, 0.2), as_rows(self.fx, 0.9)
        c.pop(next(iter(c)))
        ev = S.compare(b, c)
        self.assertEqual(ev["verdict"], "insufficient")
        self.assertIn("fixture keys differ", ev["reasons"][0])

    def test_different_outcomes_hold(self):
        b, c = as_rows(self.fx, 0.2), as_rows(self.fx, 0.9)
        k = next(iter(c)); c[k] = dict(c[k], y=(c[k]["y"] + 1) % 3)
        self.assertEqual(S.compare(b, c)["verdict"], "insufficient")

    def test_bootstrap_is_reproducible(self):
        b, c = as_rows(self.fx, 0.3), as_rows(self.fx, 0.6)
        self.assertEqual(S.compare(b, c)["splits"]["check"]["paired"], S.compare(b, c)["splits"]["check"]["paired"])

    def test_metrics(self):
        m = S.metrics([{"p": [1.0, 0.0, 0.0], "y": 0}, {"p": [0.5, 0.25, 0.25], "y": 1}])
        self.assertAlmostEqual(m["accuracy"], 0.5)
        self.assertAlmostEqual(m["brier"], (0 + (0.25 + 0.5625 + 0.0625)) / 2)


class Snapshot(unittest.TestCase):
    def test_tampered_snapshot_is_refused(self):
        body = {"data": {"x|2025-26": [["2025-08-01", "A", "B", 1, 0]]}, "current": {}}
        body["sha256"] = P.digest({"data": body["data"], "current": body["current"]})
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.json")
            json.dump(body, open(p, "w"))
            self.assertEqual(P.verify(p)[1], body["sha256"])
            body["data"]["x|2025-26"][0][3] = 5
            json.dump(body, open(p, "w"))
            with self.assertRaises(SystemExit):
                P.verify(p)


if __name__ == "__main__":
    unittest.main()
