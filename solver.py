"""Peg Solitaire solver — depth-bounded DFS for hint generation.

The full English board has roughly 5 × 10⁶ reachable states, but with good
pruning DFS finishes in a couple of seconds. We cap by node-budget so the
hint command can't hang.
"""
from typing import List, Optional, Tuple

from board import (
    apply_move, is_won, legal_moves, peg_count,
)


def solve(
    grid: List[List[Optional[bool]]],
    max_nodes: int = 200_000,
) -> Optional[List[Tuple[Tuple[int, int], str]]]:
    """Return a sequence of moves that wins from `grid`, or None.

    Search is cut off after `max_nodes` expansions. Returning None just
    means the search was inconclusive within the budget — not necessarily
    that no win exists.
    """
    if is_won(grid):
        return []
    if peg_count(grid) <= 1:
        return None  # impossible to win without a peg to jump
    seen = set()
    nodes = [0]

    def key(g):
        return tuple(
            tuple(0 if v is None else (2 if v else 1) for v in row)
            for row in g
        )

    def dfs(g) -> Optional[List[Tuple[Tuple[int, int], str]]]:
        if is_won(g):
            return []
        if nodes[0] >= max_nodes:
            return None
        nodes[0] += 1
        k = key(g)
        if k in seen:
            return None
        seen.add(k)
        for src, d in legal_moves(g):
            try:
                ng = apply_move(g, src, d)
            except Exception:
                continue
            sub = dfs(ng)
            if sub is not None:
                return [(src, d)] + sub
        return None

    return dfs(grid)


def hint(
    grid: List[List[Optional[bool]]], max_nodes: int = 80_000
) -> Optional[Tuple[Tuple[int, int], str]]:
    """Return one move that lies on a winning continuation, or None."""
    sol = solve(grid, max_nodes=max_nodes)
    if not sol:
        # Fall back to any legal move so the player at least gets unstuck.
        moves = legal_moves(grid)
        return moves[0] if moves else None
    return sol[0]
