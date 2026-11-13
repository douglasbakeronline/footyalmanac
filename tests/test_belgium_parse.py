import unittest
import sources

BE = """= Jupiler Pro League 2026/27
▪ 1. Round
  Fri Aug 7 2026
    20:45  Club Brugge             v KV Kortrijk 3-0
  Sat Aug 8
    18:15  Standard de Liège       v Cercle Brugge
  Sun Aug 9
    20:45  Royale Union Saint-Gilloise v Lommel SK (*)
"""


class BelgiumParse(unittest.TestCase):
    def test_single_space_score_and_annotation(self):
        r = sources.parse_fixture_txt(BE)
        self.assertEqual((r[0]["away"], r[0]["hg"], r[0]["ag"]), ("KV Kortrijk", 3, 0))
        self.assertEqual(r[2]["away"], "Lommel")
        self.assertIsNone(r[2]["hg"])

    def test_espn_spellings(self):
        pairs = {"Racing Genk": "KRC Genk", "Royal Charleroi": "Sporting Charleroi",
                 "Sint-Truidense": "STVV", "Standard Liege": "Standard de Liège",
                 "Union St.-Gilloise": "Royale Union Saint-Gilloise"}
        for e, o in pairs.items():
            self.assertEqual(sources.match_team(e, [o]), o, e)


if __name__ == "__main__":
    unittest.main()
