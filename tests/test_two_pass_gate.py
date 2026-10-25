"""The two-consecutive-passes rule for the weekly auto-apply (25 Oct 2026, bug 20).

    python3 -m unittest tests.test_two_pass_gate -v

tune.py --fit and tools/model_ideas.py --fit-home each need the same
candidate to pass the three gates (>= 250 check fixtures, p(worse) <= 0.30,
gain >= 0.0005) on two weekly runs in a row before anything is written. The
pending candidate and its run live in tuning-pending.json. Pure logic, no
network, no record.json.
"""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import tune as T

CURVE = {"kind": "curve", "a": 1.12, "b": -0.35}
OTHER = {"kind": "curve", "a": 1.10, "b": -0.40}


class TwoPass(unittest.TestCase):
    def test_threshold_is_two(self):
        self.assertEqual(T.PASSES_TO_APPLY, 2)
        self.assertEqual(T.MAX_P_WORSE, 0.30)   # the gate itself is unchanged

    def test_first_pass_holds_second_applies(self):
        apply, st = T.consecutive_passes("calibration", CURVE, True, {}, "2026-10-26")
        self.assertFalse(apply)
        self.assertEqual(st["calibration"]["passes"], 1)
        self.assertEqual(st["calibration"]["candidate"], CURVE)
        apply, st = T.consecutive_passes("calibration", CURVE, True, st, "2026-11-02")
        self.assertTrue(apply)
        self.assertNotIn("calibration", st)   # applied: the run starts again

    def test_fail_between_passes_resets(self):
        _, st = T.consecutive_passes("calibration", CURVE, True, {}, "2026-10-26")
        apply, st = T.consecutive_passes("calibration", CURVE, False, st, "2026-11-02")
        self.assertFalse(apply); self.assertNotIn("calibration", st)
        apply, st = T.consecutive_passes("calibration", CURVE, True, st, "2026-11-09")
        self.assertFalse(apply); self.assertEqual(st["calibration"]["passes"], 1)

    def test_different_candidate_starts_over(self):
        _, st = T.consecutive_passes("calibration", CURVE, True, {}, "2026-10-26")
        apply, st = T.consecutive_passes("calibration", OTHER, True, st, "2026-11-02")
        self.assertFalse(apply)
        self.assertEqual(st["calibration"], {"candidate": OTHER, "passes": 1, "since": "2026-11-02", "last": "2026-11-02"})

    def test_candidate_compared_by_value_not_identity(self):
        _, st = T.consecutive_passes("home", {"k": 0.5}, True, {}, "2026-10-26")
        st = json.loads(json.dumps(st))   # as it comes back from the committed file
        apply, _ = T.consecutive_passes("home", {"k": 0.5}, True, st, "2026-11-02")
        self.assertTrue(apply)

    def test_keys_are_independent(self):
        _, st = T.consecutive_passes("calibration", CURVE, True, {}, "2026-10-26")
        apply, st = T.consecutive_passes("home", {"k": 0.25}, True, st, "2026-10-26")
        self.assertFalse(apply)
        self.assertEqual(set(st), {"calibration", "home"})
        apply, st = T.consecutive_passes("home", {"k": 0.25}, False, st, "2026-11-02")
        self.assertEqual(set(st), {"calibration"})   # a home fail leaves calibration's run alone

    def test_since_kept_across_the_run(self):
        T_SAVE = T.PASSES_TO_APPLY
        try:
            T.PASSES_TO_APPLY = 3
            _, st = T.consecutive_passes("calibration", CURVE, True, {}, "2026-10-26")
            _, st = T.consecutive_passes("calibration", CURVE, True, st, "2026-11-02")
            self.assertEqual((st["calibration"]["since"], st["calibration"]["last"], st["calibration"]["passes"]),
                             ("2026-10-26", "2026-11-02", 2))
        finally:
            T.PASSES_TO_APPLY = T_SAVE

    def test_pending_file_round_trip_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "tuning-pending.json")
            self.assertEqual(T.load_pending(path), {})
            _, st = T.consecutive_passes("calibration", CURVE, True, {}, "2026-10-26")
            T.save_pending(st, path)
            self.assertEqual(T.load_pending(path), st)
            with open(path, "w") as f: f.write("not json")
            self.assertEqual(T.load_pending(path), {})   # a corrupt file is a clean slate, never a crash


if __name__ == "__main__":
    unittest.main()
