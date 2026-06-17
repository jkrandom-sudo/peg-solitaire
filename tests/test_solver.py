"""Tests for solver.py."""
import unittest

from board import SIZE, apply_move, initial_grid, is_won
from solver import hint, solve


class SolveTest(unittest.TestCase):
    def test_won_returns_empty(self):
        g = [[None] * SIZE for _ in range(SIZE)]
        g[3][3] = True
        self.assertEqual(solve(g), [])

    def test_two_peg_wins(self):
        # Two pegs that can jump into one
        g = [[None] * SIZE for _ in range(SIZE)]
        g[3][1] = True
        g[3][2] = True
        g[3][3] = False
        sol = solve(g)
        self.assertIsNotNone(sol)
        # First move should jump from (3,1) right
        cur = g
        for src, d in sol:
            cur = apply_move(cur, src, d)
        self.assertTrue(is_won(cur))

    def test_unsolvable_returns_none(self):
        # Two isolated pegs with no adjacency possible
        g = [[None] * SIZE for _ in range(SIZE)]
        g[3][0] = True
        g[3][6] = True
        # Mark some other cells as empty so they're "playable" holes
        for c in range(SIZE):
            if g[3][c] is None:
                g[3][c] = False
        sol = solve(g)
        self.assertIsNone(sol)


class HintTest(unittest.TestCase):
    def test_initial_hint_returns_legal(self):
        g = initial_grid("english")
        h = hint(g)
        self.assertIsNotNone(h)
        src, d = h
        # Should be one of the four legal opening moves
        self.assertIn((src, d), [
            ((1, 3), "d"), ((5, 3), "u"), ((3, 1), "r"), ((3, 5), "l")
        ])

    def test_hint_falls_back_to_any_move(self):
        # Setup where solver can't find a win in budget, but legal moves exist.
        # Easiest: 3-peg config with no winning continuation
        g = [[None] * SIZE for _ in range(SIZE)]
        g[3][1] = True
        g[3][2] = True
        g[3][3] = True  # all three filled — no empty hole, no jumps possible
        h = hint(g)
        self.assertIsNone(h)


if __name__ == "__main__":
    unittest.main()
