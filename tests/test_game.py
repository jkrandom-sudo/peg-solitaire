"""Tests for game.py."""
import io
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import game
import score as score_mod
import settings as settings_mod
from sound import Sound


class StackedInput:
    def __init__(self, lines):
        self.lines = list(lines)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.lines:
            raise EOFError()
        return self.lines.pop(0)


class ParseMoveTest(unittest.TestCase):
    def test_space_form(self):
        self.assertEqual(game.parse_move("3 1 r"), ((3, 1), "r"))
        self.assertEqual(game.parse_move("1 3 d"), ((1, 3), "d"))

    def test_compact_form(self):
        self.assertEqual(game.parse_move("31r"), ((3, 1), "r"))

    def test_rc_form(self):
        self.assertEqual(game.parse_move("r3c1 r"), ((3, 1), "r"))

    def test_comma_form(self):
        self.assertEqual(game.parse_move("3,1,r"), ((3, 1), "r"))

    def test_paren_form(self):
        self.assertEqual(game.parse_move("(3,1) r"), ((3, 1), "r"))

    def test_case_insensitive(self):
        self.assertEqual(game.parse_move("3 1 R"), ((3, 1), "r"))

    def test_invalid_no_direction(self):
        self.assertIsNone(game.parse_move("3 1"))

    def test_invalid_garbage(self):
        self.assertIsNone(game.parse_move("hello"))
        self.assertIsNone(game.parse_move(""))

    def test_invalid_out_of_bounds(self):
        self.assertIsNone(game.parse_move("9 9 r"))

    def test_invalid_unknown_dir(self):
        self.assertIsNone(game.parse_move("3 1 x"))


class FormatMoveTest(unittest.TestCase):
    def test_format(self):
        self.assertIn("3", game.format_move((3, 1), "r", "en"))
        self.assertIn("right", game.format_move((3, 1), "r", "en"))


class PlayRoundTest(unittest.TestCase):
    def _settings(self, **kw):
        s = {"lang": "en", "sound": False, "volume": 0, "variant": "english"}
        s.update(kw)
        return s

    def test_quit(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        result = game.play_round(s, sound, StackedInput(["q"]), out, rng=random.Random(0))
        self.assertIsNone(result)

    def test_eof_raises(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        with self.assertRaises(game.QuitGame):
            game.play_round(s, sound, StackedInput([]), out, rng=random.Random(0))

    def test_bad_format(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["xyz", "q"]), out, rng=random.Random(0))
        self.assertIn("Bad format", out.getvalue())

    def test_undo_empty_message(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["u", "q"]), out, rng=random.Random(0))
        self.assertIn("Nothing to undo", out.getvalue())

    def test_reset_command(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["1 3 d", "r", "q"]), out, rng=random.Random(0))
        self.assertIn("Reset", out.getvalue())

    def test_legal_move_advances(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["1 3 d", "q"]), out, rng=random.Random(0))
        self.assertIn("31", out.getvalue())  # peg count display

    def test_illegal_move_message(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["0 0 r", "q"]), out, rng=random.Random(0))
        self.assertIn("Illegal", out.getvalue())

    def test_hint_command(self):
        out = io.StringIO()
        s = self._settings()
        sound = Sound(enabled=False, output=out)
        game.play_round(s, sound, StackedInput(["h", "q"]), out, rng=random.Random(0))
        self.assertIn("Hint", out.getvalue())


class MainMenuTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self._patches = [
            patch.object(settings_mod, "DEFAULT_PATH", tmp / "s.json"),
            patch.object(score_mod, "DEFAULT_PATH", tmp / "scores.json"),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self._tmp.cleanup()

    def test_quit(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["q"]), out, rng=random.Random(0))
        self.assertTrue("Bye" in out.getvalue() or "再见" in out.getvalue())

    def test_eof_exits(self):
        out = io.StringIO()
        game.main_menu(StackedInput([]), out, rng=random.Random(0))
        self.assertTrue("Bye" in out.getvalue() or "再见" in out.getvalue())

    def test_unknown(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["zzz", "q"]), out, rng=random.Random(0))
        self.assertTrue("Unknown" in out.getvalue() or "未知" in out.getvalue())

    def test_help_flow(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["h", "", "q"]), out, rng=random.Random(0))
        self.assertTrue("Help" in out.getvalue() or "帮助" in out.getvalue())

    def test_scores_empty(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["l", "", "q"]), out, rng=random.Random(0))
        self.assertTrue("No scores" in out.getvalue() or "暂无" in out.getvalue())

    def test_settings_back(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "b", "q"]), out, rng=random.Random(0))
        self.assertTrue(settings_mod.DEFAULT_PATH.exists())

    def test_settings_cycle_lang(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "1", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["lang"], "en")

    def test_settings_toggle_sound(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "2", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertFalse(s["sound"])

    def test_settings_cycle_volume(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "3", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["volume"], 2)

    def test_settings_cycle_variant(self):
        out = io.StringIO()
        game.main_menu(StackedInput(["s", "4", "b", "q"]), out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["variant"], "european")

    def test_play_then_save_score(self):
        settings_mod.save({"lang": "en", "sound": False, "volume": 0, "variant": "english"})
        out = io.StringIO()
        fake = {"result": "perfect", "score": 1200, "variant": "english", "pegs": 1, "perfect": True}
        with patch.object(game, "play_round", return_value=fake):
            game.main_menu(StackedInput(["p", "Alice", "q"]), out, rng=random.Random(0))
        scores = score_mod.load()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["name"], "Alice")
        self.assertEqual(scores[0]["score"], 1200)

    def test_play_skip_save(self):
        settings_mod.save({"lang": "en", "sound": False, "volume": 0, "variant": "english"})
        out = io.StringIO()
        fake = {"result": "perfect", "score": 1200, "variant": "english", "pegs": 1, "perfect": True}
        with patch.object(game, "play_round", return_value=fake):
            game.main_menu(StackedInput(["p", "", "q"]), out, rng=random.Random(0))
        self.assertEqual(score_mod.load(), [])

    def test_play_quit_round_no_save(self):
        settings_mod.save({"lang": "en", "sound": False, "volume": 0, "variant": "english"})
        out = io.StringIO()
        with patch.object(game, "play_round", return_value=None):
            game.main_menu(StackedInput(["p", "q"]), out, rng=random.Random(0))
        self.assertEqual(score_mod.load(), [])


if __name__ == "__main__":
    unittest.main()
