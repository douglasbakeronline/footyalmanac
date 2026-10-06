"""Live-settled football results persist between builds (score.py, 6 Oct 2026)."""
import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score as SC

class Settled(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "current", "settled-results.json")
            SC.save_settled({("afcon.q", "2026-09-29", "Burundi", "Algeria"): (2, 2)}, p)
            self.assertEqual(SC.load_settled(p), {("afcon.q", "2026-09-29", "Burundi", "Algeria"): (2, 2)})
            self.assertNotIn("rows", json.load(open(p)))      # invisible to replay.py's freeze

    def test_missing_file_is_empty(self):
        self.assertEqual(SC.load_settled("/nonexistent/x.json"), {})

if __name__ == "__main__":
    unittest.main()
