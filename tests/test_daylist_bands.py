"""daylist.band_records: each page band's record from the results ledger's summary."""
import gzip, json, os, tempfile, unittest
import daylist


class BandRecords(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        summ = {
            "ncaab|list|90-95": {"n": 10, "won": 9, "quoted": 0.92, "priced": 10, "ret": -0.02},
            "ncaab|list|95+": {"n": 10, "won": 10, "quoted": 0.97, "priced": 0},
            "ncaab|reserve|80-85": {"n": 20, "won": 16, "quoted": 0.82, "priced": 10, "ret": 0.10},
            "ncaab|list|80-85": {"n": 20, "won": 18, "quoted": 0.83, "priced": 10, "ret": -0.10},
            "ncaab|board|80-85": {"n": 5, "won": 1, "quoted": 0.81},
        }
        with gzip.open(os.path.join(self.dir, "results-ledger.json.gz"), "wt") as f:
            json.dump({"summary": summ, "rows": []}, f)

    def test_ninety_joins_two_ledger_bands(self):
        b = daylist.band_records(self.dir)["pick"]["ncaab"]["90"]
        self.assertEqual((b["n"], b["won"]), (20, 19))
        self.assertAlmostEqual(b["quoted"], 0.945)
        self.assertAlmostEqual(b["ret"], -0.02)   # weighted by priced picks only

    def test_list_and_reserve_merge_board_only_in_every(self):
        r = daylist.band_records(self.dir)
        self.assertEqual(r["pick"]["ncaab"]["80"]["n"], 40)
        self.assertAlmostEqual(r["pick"]["ncaab"]["80"]["ret"], 0.0)
        self.assertEqual(r["every"]["ncaab"]["80"]["n"], 45)

    def test_missing_ledger_is_empty(self):
        self.assertEqual(daylist.band_records(tempfile.mkdtemp()), {})


if __name__ == "__main__":
    unittest.main()
