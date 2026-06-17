"""Peg Solitaire (孔明棋 / Hi-Q) board.

Two board variants are supported:
  english  — 33-hole cross (3×3 arms on a 7×7 grid)
  european — 37-hole cross (the English board with four extra corner cells)

Cell states:
  None  → outside the playable region
  False → empty hole
  True  → peg

A move is a jump: a peg jumps over an adjacent peg into an empty hole
straight up/down/left/right. The jumped-over peg is removed.

The classic English challenge: start with all holes filled except the
centre, finish with exactly one peg remaining (ideally in the centre).
"""
from typing import List, Optional, Tuple


SIZE = 7
DIRECTIONS = {
    "u": (-1, 0),
    "d": (1, 0),
    "l": (0, -1),
    "r": (0, 1),
}


class IllegalMove(Exception):
    pass


def english_mask() -> List[List[bool]]:
    """Return a 7×7 mask: True where a hole exists."""
    mask = [[False] * SIZE for _ in range(SIZE)]
    for r in range(SIZE):
        for c in range(SIZE):
            in_vertical_arm = 2 <= c <= 4
            in_horizontal_arm = 2 <= r <= 4
            if in_vertical_arm or in_horizontal_arm:
                mask[r][c] = True
    return mask


def european_mask() -> List[List[bool]]:
    """Same as English plus four extra corner cells (37 holes)."""
    mask = english_mask()
    # Four diagonally-adjacent cells to the corners of the central 3×3
    for (r, c) in [(1, 1), (1, 5), (5, 1), (5, 5)]:
        mask[r][c] = True
    return mask


VARIANTS = {
    "english": english_mask,
    "european": european_mask,
}


def initial_grid(variant: str = "english") -> List[List[Optional[bool]]]:
    """All holes filled with pegs except the centre."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    mask = VARIANTS[variant]()
    grid: List[List[Optional[bool]]] = [[None] * SIZE for _ in range(SIZE)]
    for r in range(SIZE):
        for c in range(SIZE):
            if mask[r][c]:
                grid[r][c] = True
    cr = SIZE // 2
    grid[cr][cr] = False
    return grid


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < SIZE and 0 <= c < SIZE


def is_hole(grid: List[List[Optional[bool]]], r: int, c: int) -> bool:
    return in_bounds(r, c) and grid[r][c] is not None


def has_peg(grid: List[List[Optional[bool]]], r: int, c: int) -> bool:
    return is_hole(grid, r, c) and grid[r][c] is True


def is_empty(grid: List[List[Optional[bool]]], r: int, c: int) -> bool:
    return is_hole(grid, r, c) and grid[r][c] is False


def legal_moves(grid: List[List[Optional[bool]]]) -> List[Tuple[Tuple[int, int], str]]:
    """Return all legal (src, direction) pairs."""
    out = []
    for r in range(SIZE):
        for c in range(SIZE):
            if not has_peg(grid, r, c):
                continue
            for d, (dr, dc) in DIRECTIONS.items():
                mr, mc = r + dr, c + dc
                tr, tc = r + 2 * dr, c + 2 * dc
                if has_peg(grid, mr, mc) and is_empty(grid, tr, tc):
                    out.append(((r, c), d))
    return out


def apply_move(
    grid: List[List[Optional[bool]]], src: Tuple[int, int], direction: str
) -> List[List[Optional[bool]]]:
    """Return a new grid with the given jump applied. Raises IllegalMove."""
    if direction not in DIRECTIONS:
        raise IllegalMove(f"unknown direction: {direction}")
    r, c = src
    if not has_peg(grid, r, c):
        raise IllegalMove("no peg at source")
    dr, dc = DIRECTIONS[direction]
    mr, mc = r + dr, c + dc
    tr, tc = r + 2 * dr, c + 2 * dc
    if not has_peg(grid, mr, mc):
        raise IllegalMove("no peg to jump over")
    if not is_empty(grid, tr, tc):
        raise IllegalMove("landing hole is not empty")
    new = [row[:] for row in grid]
    new[r][c] = False
    new[mr][mc] = False
    new[tr][tc] = True
    return new


def peg_count(grid: List[List[Optional[bool]]]) -> int:
    return sum(1 for row in grid for v in row if v is True)


def is_won(grid: List[List[Optional[bool]]]) -> bool:
    """Game is won when exactly one peg remains."""
    return peg_count(grid) == 1


def is_perfect(grid: List[List[Optional[bool]]]) -> bool:
    """Perfect win: one peg remains, in the centre."""
    cr = SIZE // 2
    return is_won(grid) and grid[cr][cr] is True


def is_stuck(grid: List[List[Optional[bool]]]) -> bool:
    """No legal moves (and not yet down to 1 peg → loss)."""
    return not legal_moves(grid)


class Board:
    def __init__(self, variant: str = "english"):
        if variant not in VARIANTS:
            raise ValueError(f"unknown variant: {variant}")
        self.variant = variant
        self.grid: List[List[Optional[bool]]] = initial_grid(variant)
        self.history: List[Tuple[Tuple[int, int], str]] = []

    def reset(self) -> None:
        self.grid = initial_grid(self.variant)
        self.history = []

    def play(self, src: Tuple[int, int], direction: str) -> None:
        new = apply_move(self.grid, src, direction)
        self.grid = new
        self.history.append((src, direction))

    def undo(self) -> bool:
        if not self.history:
            return False
        src, d = self.history.pop()
        # Reverse the jump: peg is now at landing; we move it back to src,
        # restore the jumped peg.
        r, c = src
        dr, dc = DIRECTIONS[d]
        mr, mc = r + dr, c + dc
        tr, tc = r + 2 * dr, c + 2 * dc
        # State after jump: src/mid empty, target has peg.
        if not has_peg(self.grid, tr, tc):
            # Inconsistent — restore history and bail.
            self.history.append((src, d))
            return False
        new = [row[:] for row in self.grid]
        new[tr][tc] = False
        new[mr][mc] = True
        new[r][c] = True
        self.grid = new
        return True

    def legal_moves(self):
        return legal_moves(self.grid)

    def peg_count(self) -> int:
        return peg_count(self.grid)

    def is_won(self) -> bool:
        return is_won(self.grid)

    def is_perfect(self) -> bool:
        return is_perfect(self.grid)

    def is_stuck(self) -> bool:
        return is_stuck(self.grid)

    def is_game_over(self) -> bool:
        return self.is_won() or self.is_stuck()

    def render_text(self) -> str:
        lines = ["    " + "  ".join(str(c) for c in range(SIZE))]
        for r in range(SIZE):
            cells = []
            for c in range(SIZE):
                v = self.grid[r][c]
                if v is None:
                    cells.append(" ")
                elif v:
                    cells.append("●")
                else:
                    cells.append("·")
            lines.append(f"{r}   " + "  ".join(cells))
        return "\n".join(lines)
