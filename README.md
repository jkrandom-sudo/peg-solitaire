# 孔明棋 / Peg Solitaire (Hi-Q)

A pure-Python (stdlib only) console implementation of the classic
single-player **peg solitaire** puzzle (also known as Hi-Q, Solo Noble,
孔明棋 / 独立钻石棋). Jump pegs over each other to remove them until only
one remains. Bilingual UI (中文 / English), two board variants (English
33-hole / European 37-hole), depth-bounded DFS solver for hints, undo,
persistent settings, top-10 leaderboard, and minimal terminal-bell SFX.

> Goal: end with a single peg remaining — ideally in the centre hole.

## Rules

- The board is a **cross-shaped** grid of holes (33 in the English
  variant, 37 in the European variant). Initially every hole has a peg
  except the **centre**, which is empty.
- A move is a **jump**: pick any peg with an orthogonally adjacent peg
  next to it, and an empty hole **two steps in the same direction**. The
  peg jumps into the empty hole, and the jumped-over peg is removed.
- Diagonal jumps are not allowed. Only one peg moves per turn.
- The game **ends** when there are no more legal jumps. You **win** if
  exactly one peg remains; a **perfect** win has that final peg in the
  centre hole.

## Features

- Two board variants — English (33 holes) and European (37 holes)
- Depth-bounded DFS solver for **hint** (returns a move that lies on a
  winning continuation when one is found within the node budget,
  otherwise falls back to any legal move)
- Bilingual: 中文 / English (toggle in Settings → 1)
- Persistent settings → `~/.pegsolitaire_settings.json`
- Persistent top-10 leaderboard → `~/.pegsolitaire_scores.json`
- Sound on/off + 4-level volume (terminal bell `\a`)
- Undo / reset / hint / quit commands
- Pure Python 3 stdlib — no third-party packages

## Quickstart

```bash
git clone https://github.com/jkrandom-sudo/peg-solitaire.git
cd peg-solitaire
python3 game.py
```

## In-game commands

At your turn prompt, give a source square plus a direction:

| Input              | Effect                                              |
|--------------------|-----------------------------------------------------|
| `3 1 r`            | Jump the peg at row 3, col 1 to the right           |
| `31r`              | Compact form (row, col, direction)                  |
| `r3c1 r`           | Verbose `rNcN` form                                 |
| `3,1,r`            | Comma-separated                                     |
| `(3,1) r`          | Parenthesised                                       |
| `u`                | Undo the last jump                                  |
| `h`                | Hint — show a recommended jump                      |
| `r`                | Reset the board                                     |
| `q`                | Abandon round, return to menu                       |

Directions are `u` (up), `d` (down), `l` (left), `r` (right). Coordinates
are `row col` with `row, col ∈ [0, 6]` on the 7×7 underlying grid.

```
       Cols 2–4 form the vertical arm.
       Rows 2–4 form the horizontal arm.

         0  1  2  3  4  5  6
       +--------------------+
   0   |       ●  ●  ●      |    English board (33 holes):
   1   |       ●  ●  ●      |    centre = (3, 3)
   2   | ●  ●  ●  ●  ●  ●  ●|
   3   | ●  ●  ●  ·  ●  ●  ●|    · = empty centre at start
   4   | ●  ●  ●  ●  ●  ●  ●|
   5   |       ●  ●  ●      |
   6   |       ●  ●  ●      |
       +--------------------+
```

The European variant adds the four cells `(1,1)`, `(1,5)`, `(5,1)`, `(5,5)`.

## Scoring

```
score = 1000 − (pegs_left − 1) × 30 + perfect_bonus + variant_bonus
   where perfect_bonus = 200 (last peg in centre) or 0
         variant_bonus =   0 (English) or 50 (European)
```

So a perfect English win scores **1200**; ending stuck with 5 pegs
remaining scores **880**.

## Project layout

```
peg-solitaire/
├── game.py            # menu + round loop + parse_move
├── board.py           # Board class, masks, jump rules, render
├── solver.py          # DFS lookahead + hint()
├── i18n.py            # zh / en strings + t() helper
├── settings.py        # JSON settings persistence
├── score.py           # JSON leaderboard persistence
├── sound.py           # terminal-bell SFX
├── tests/
│   ├── test_board.py
│   ├── test_solver.py
│   ├── test_modules.py
│   ├── test_game.py
│   └── run_tests.py
└── README.md
```

## Running tests

```bash
python3 tests/run_tests.py
```

88 tests cover mask construction (33-hole / 37-hole counts), initial
grid setup, legal-move enumeration, jump validation including
out-of-board and missing-peg cases, undo correctness, win/perfect/stuck
detection, the DFS solver on small boards, hint fallback behaviour,
settings/score persistence, sound output, i18n fallbacks, and the menu /
round loop flow via a scripted-input helper.

## License

MIT
