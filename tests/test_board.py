"""Tests for board.py."""
import unittest

from board import (
    Board, IllegalMove, SIZE, apply_move, english_mask, european_mask,
    initial_grid, is_perfect, is_stuck, is_won, legal_moves, peg_count,
)


class MasksTest(unittest.TestCase):
    def test_english_has_33_holes(self):
        m = english_mask()
        count = sum(1 for row in m for v in row if v)
        self.assertEqual(count, 33)

    def test_english_corners_excluded(self):
        m = english_mask()
        self.assertFalse(m[0][0])
        self.assertFalse(m[0][1])
        self.assertFalse(m[1][0])
        self.assertFalse(m[6][6])

    def test_european_has_37_holes(self):
        m = european_mask()
        count = sum(1 for row in m for v in row if v)
        self.assertEqual(count, 37)

    def test_european_extra_corners(self):
        m = european_mask()
        for (r, c) in [(1, 1), (1, 5), (5, 1), (5, 5)]:
            self.assertTrue(m[r][c])


class InitialGridTest(unittest.TestCase):
    def test_centre_is_empty(self):
        g = initial_grid("english")
        self.assertEqual(g[3][3], False)

    def test_other_holes_have_pegs(self):
        g = initial_grid("english")
        self.assertTrue(g[3][0])
        self.assertTrue(g[0][3])
        self.assertTrue(g[6][3])

    def test_outside_is_none(self):
        g = initial_grid("english")
        self.assertIsNone(g[0][0])
        self.assertIsNone(g[6][6])

    def test_starting_peg_count(self):
        self.assertEqual(peg_count(initial_grid("english")), 32)
        self.assertEqual(peg_count(initial_grid("european")), 36)

    def test_invalid_variant(self):
        with self.assertRaises(ValueError):
            initial_grid("klingon")


class LegalMovesTest(unittest.TestCase):
    def test_initial_legal_moves_english(self):
        g = initial_grid("english")
        moves = legal_moves(g)
        # The four pegs adjacent to the centre can each jump into the centre.
        # Plus their mirror images? No — only those 4 jumps are possible at start.
        self.assertEqual(len(moves), 4)
        # All must land at (3,3) — let's just check each is among the four
        expected = {((1, 3), "d"), ((5, 3), "u"), ((3, 1), "r"), ((3, 5), "l")}
        self.assertEqual(set(moves), expected)


class ApplyMoveTest(unittest.TestCase):
    def test_first_move(self):
        g = initial_grid("english")
        new = apply_move(g, (1, 3), "d")
        self.assertFalse(new[1][3])  # source empty
        self.assertFalse(new[2][3])  # jumped peg removed
        self.assertTrue(new[3][3])   # landing has peg
        self.assertEqual(peg_count(new), 31)

    def test_no_peg_at_source(self):
        g = initial_grid("english")
        with self.assertRaises(IllegalMove):
            apply_move(g, (3, 3), "d")  # centre is empty

    def test_no_peg_to_jump(self):
        g = initial_grid("english")
        # (0,3) → 'd': mid (1,3) has peg, target (2,3) has peg → not empty
        with self.assertRaises(IllegalMove):
            apply_move(g, (0, 3), "d")

    def test_unknown_direction(self):
        g = initial_grid("english")
        with self.assertRaises(IllegalMove):
            apply_move(g, (1, 3), "x")

    def test_jump_off_board(self):
        g = initial_grid("english")
        with self.assertRaises(IllegalMove):
            apply_move(g, (3, 0), "l")  # off board


class WinAndStuckTest(unittest.TestCase):
    def test_won_iff_one_peg(self):
        g = [[None] * SIZE for _ in range(SIZE)]
        # Single peg in centre
        g[3][3] = True
        # Make it a valid hole grid: also mark some holes as empty
        g[2][3] = False
        self.assertTrue(is_won(g))
        self.assertTrue(is_perfect(g))

    def test_won_not_perfect(self):
        g = [[None] * SIZE for _ in range(SIZE)]
        g[3][3] = False
        g[0][3] = True
        self.assertTrue(is_won(g))
        self.assertFalse(is_perfect(g))

    def test_initial_not_stuck(self):
        self.assertFalse(is_stuck(initial_grid("english")))

    def test_no_pegs_is_stuck(self):
        g = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                if english_mask()[r][c]:
                    g[r][c] = False
        self.assertTrue(is_stuck(g))


class BoardTest(unittest.TestCase):
    def test_init(self):
        b = Board()
        self.assertEqual(b.peg_count(), 32)
        self.assertFalse(b.is_won())
        self.assertFalse(b.is_stuck())

    def test_play_advances(self):
        b = Board()
        b.play((1, 3), "d")
        self.assertEqual(b.peg_count(), 31)
        self.assertEqual(len(b.history), 1)

    def test_undo_restores(self):
        b = Board()
        before = [row[:] for row in b.grid]
        b.play((1, 3), "d")
        self.assertNotEqual(b.grid, before)
        self.assertTrue(b.undo())
        self.assertEqual(b.grid, before)
        self.assertEqual(b.peg_count(), 32)

    def test_undo_empty(self):
        b = Board()
        self.assertFalse(b.undo())

    def test_reset(self):
        b = Board()
        b.play((1, 3), "d")
        b.reset()
        self.assertEqual(b.peg_count(), 32)
        self.assertEqual(b.history, [])

    def test_european_variant(self):
        b = Board(variant="european")
        self.assertEqual(b.peg_count(), 36)

    def test_invalid_variant(self):
        with self.assertRaises(ValueError):
            Board(variant="klingon")

    def test_render_text(self):
        b = Board()
        text = b.render_text()
        self.assertIn("●", text)
        self.assertIn("·", text)

    def test_game_over_when_won(self):
        b = Board()
        b.grid = [[None] * SIZE for _ in range(SIZE)]
        b.grid[3][3] = True
        self.assertTrue(b.is_won())
        self.assertTrue(b.is_game_over())


if __name__ == "__main__":
    unittest.main()
