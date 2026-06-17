"""Peg solitaire — main menu and round loop."""
import random
import sys
from typing import Optional, Tuple

import score as score_mod
import settings as settings_mod
import solver as solver_mod
from board import Board, DIRECTIONS, IllegalMove, in_bounds
from i18n import t
from sound import Sound


class QuitGame(Exception):
    pass


def parse_move(text: str) -> Optional[Tuple[Tuple[int, int], str]]:
    """Parse a move command. Returns ((r, c), direction) or None.

    Accepted forms:
      '3 1 r'         space-separated
      '31r'           compact 3-char
      'r3c1 r'        rNcN form
      '3,1,r'         comma-separated
      '(3,1) r'       parenthesised
    """
    if not text:
        return None
    s = text.strip().lower()
    if not s:
        return None
    # Direction is the last non-whitespace character; must be u/d/l/r.
    if s[-1] not in DIRECTIONS:
        return None
    direction = s[-1]
    rest = s[:-1].strip()
    # Normalise: drop labels and structural punctuation.
    for ch in ",()rc":
        rest = rest.replace(ch, " ")
    digit_tokens = rest.split()
    if not digit_tokens or not all(tok.isdigit() for tok in digit_tokens):
        return None
    if len(digit_tokens) == 2:
        r, c = int(digit_tokens[0]), int(digit_tokens[1])
    elif len(digit_tokens) == 1 and len(digit_tokens[0]) == 2:
        r, c = int(digit_tokens[0][0]), int(digit_tokens[0][1])
    else:
        return None
    if not in_bounds(r, c):
        return None
    return ((r, c), direction)


def format_move(src: Tuple[int, int], direction: str, lang: str) -> str:
    return f"({src[0]},{src[1]}) {t(lang, f'dir_{direction}')}"


def play_round(s: dict, sound: Sound, input_func, output, rng=None) -> Optional[dict]:
    if rng is None:
        rng = random.Random()
    lang = s.get("lang", "zh")
    variant = s.get("variant", "english")
    board = Board(variant=variant)

    def write(msg=""):
        output.write(msg + "\n")

    while True:
        write(board.render_text())
        write(t(lang, "pegs_left", n=board.peg_count()))

        if board.is_won():
            if board.is_perfect():
                write(t(lang, "perfect"))
                result = "perfect"
            else:
                write(t(lang, "won"))
                result = "won"
            sound.win()
            score = score_mod.compute_score(1, board.is_perfect(), variant)
            write(t(lang, "score_label", score=score))
            return {
                "result": result,
                "score": score,
                "variant": variant,
                "pegs": 1,
                "perfect": board.is_perfect(),
            }
        if board.is_stuck():
            write(t(lang, "stuck", n=board.peg_count()))
            sound.stuck()
            score = score_mod.compute_score(board.peg_count(), False, variant)
            write(t(lang, "score_label", score=score))
            return {
                "result": "stuck",
                "score": score,
                "variant": variant,
                "pegs": board.peg_count(),
                "perfect": False,
            }

        try:
            line = input_func(t(lang, "input_move"))
        except EOFError:
            raise QuitGame()
        cmd = line.strip().lower()
        if cmd == "q":
            return None
        if cmd == "u":
            if not board.undo():
                write(t(lang, "nothing_undo"))
            continue
        if cmd == "r":
            board.reset()
            write(t(lang, "reset_done"))
            continue
        if cmd == "h":
            mv = solver_mod.hint(board.grid)
            if mv is None:
                write(t(lang, "no_hint"))
            else:
                src, d = mv
                write(t(lang, "hint_label", move=format_move(src, d, lang)))
            continue
        parsed = parse_move(cmd)
        if parsed is None:
            write(t(lang, "bad_format"))
            continue
        src, direction = parsed
        try:
            board.play(src, direction)
        except IllegalMove:
            write(t(lang, "illegal"))
            sound.illegal()
            continue
        sound.jump()


def show_help(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    output.write("\n=== " + t(lang, "help_title") + " ===\n")
    output.write(t(lang, "help_body") + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def show_scores(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    scores = score_mod.load()
    output.write("\n=== " + t(lang, "scores_title") + " ===\n")
    if not scores:
        output.write(t(lang, "scores_empty") + "\n")
    else:
        for i, e in enumerate(scores, 1):
            v = e.get("variant", "english")
            output.write(t(
                lang, "scores_row",
                rank=i, name=e.get("name", "")[:12],
                score=e.get("score", 0),
                variant=t(lang, f"variant_{v}"),
                pegs=e.get("pegs", 0),
            ) + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def settings_menu(s: dict, input_func, output) -> dict:
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "settings_title") + " ===\n")
        output.write(t(lang, "settings_lang", value=t(lang, f"lang_{lang}")) + "\n")
        output.write(t(lang, "settings_sound",
                       value=t(lang, "on" if s.get("sound") else "off")) + "\n")
        output.write(t(lang, "settings_volume", value=s.get("volume", 1)) + "\n")
        output.write(t(lang, "settings_variant",
                       value=t(lang, f"variant_{s.get('variant', 'english')}")) + "\n")
        output.write(t(lang, "settings_back") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            break
        if choice == "1":
            settings_mod.cycle_lang(s)
        elif choice == "2":
            settings_mod.toggle_sound(s)
        elif choice == "3":
            settings_mod.cycle_volume(s)
        elif choice == "4":
            settings_mod.cycle_variant(s)
        elif choice == "b":
            break
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")
    settings_mod.save(s)
    return s


def main_menu(input_func=None, output=None, rng=None) -> None:
    if input_func is None:
        input_func = input
    if output is None:
        output = sys.stdout
    if rng is None:
        rng = random.Random()
    s = settings_mod.load()
    settings_mod.save(s)
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "title") + " ===\n")
        output.write(t(lang, "menu_play") + "\n")
        output.write(t(lang, "menu_help") + "\n")
        output.write(t(lang, "menu_scores") + "\n")
        output.write(t(lang, "menu_settings") + "\n")
        output.write(t(lang, "menu_quit") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "q":
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "p":
            sound = Sound(enabled=bool(s.get("sound", True)),
                          volume=int(s.get("volume", 1)),
                          output=output)
            try:
                result = play_round(s, sound, input_func, output, rng=rng)
            except QuitGame:
                output.write(t(lang, "bye") + "\n")
                return
            if result is None:
                continue
            try:
                name = input_func(t(lang, "name_prompt")).strip()
            except EOFError:
                name = ""
            if name:
                score_mod.add(name, result["score"], result["variant"], result["pegs"])
        elif choice == "h":
            show_help(s, input_func, output)
        elif choice == "l":
            show_scores(s, input_func, output)
        elif choice == "s":
            settings_menu(s, input_func, output)
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
