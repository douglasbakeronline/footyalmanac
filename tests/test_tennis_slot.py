"""A tennis price is graded only on a match its two players played (19 Oct
2026). ESPN reuses a match id when a draw slot changes hands; on 12 Oct
"Pohankova v Jovic" was played by Bondar and booked as a Jovic loss."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_tennis as ST

M = {"playerA": "Mia Pohankova", "playerB": "Iva Jovic"}


class Slot(unittest.TestCase):

    def test_a_slot_played_by_someone_else_is_void(self):
        r = {"p0": "Mia Pohankova", "p1": "Anna Bondar", "winner": "Mia Pohankova", "note": "",
             "pool": {"Mia Pohankova": "Mia Pohankova", "Anna Bondar": "Anna Bondar"}}
        self.assertEqual(ST.outcome(M, r), ("void", None))

    def test_the_priced_players_grade_as_before(self):
        r = {"p0": "Iva Jovic", "p1": "Mia Pohankova", "winner": "Iva Jovic", "note": "",
             "pool": {"Iva Jovic": "Iva Jovic", "Mia Pohankova": None}}      # one unnamed by the pool
        self.assertEqual(ST.outcome(M, r), ("graded", "Iva Jovic"))

    def test_stored_grades_are_checked_against_their_result_line(self):
        bad = {**M, "note": "Mia Pohankova (SVK) bt Anna Bondar (HUN) 6-1 6-3"}
        good = {**M, "note": "Mia Pohankova (SVK) bt Iva Jovic (USA) 6-1 6-3"}
        self.assertFalse(ST.named_in_note(bad))
        self.assertTrue(ST.named_in_note(good))


if __name__ == "__main__":
    unittest.main()
