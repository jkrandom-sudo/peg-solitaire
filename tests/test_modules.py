"""Tests for settings, score, sound, i18n."""
import io
import json
import tempfile
import unittest
from pathlib import Path

import score as score_mod
import settings as settings_mod
from i18n import t
from sound import Sound


class SettingsTest(unittest.TestCase):
    def test_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as d:
            s = settings_mod.load(Path(d) / "no.json")
            self.assertEqual(s["lang"], "zh")
            self.assertTrue(s["sound"])
            self.assertEqual(s["volume"], 1)
            self.assertEqual(s["variant"], "english")

    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            settings_mod.save({"lang": "en", "sound": False, "volume": 3, "variant": "european"}, p)
            s = settings_mod.load(p)
            self.assertEqual(s["lang"], "en")
            self.assertFalse(s["sound"])
            self.assertEqual(s["volume"], 3)
            self.assertEqual(s["variant"], "european")

    def test_invalid_clamped(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            with open(p, "w") as f:
                json.dump({"lang": "xx", "sound": "no", "volume": 99, "variant": "klingon"}, f)
            s = settings_mod.load(p)
            self.assertEqual(s["lang"], "zh")
            self.assertTrue(s["sound"])
            self.assertEqual(s["volume"], 1)
            self.assertEqual(s["variant"], "english")

    def test_corrupt_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            with open(p, "w") as f:
                f.write("not json")
            self.assertEqual(settings_mod.load(p)["lang"], "zh")

    def test_cycle_lang(self):
        s = {"lang": "zh"}
        settings_mod.cycle_lang(s)
        self.assertEqual(s["lang"], "en")
        settings_mod.cycle_lang(s)
        self.assertEqual(s["lang"], "zh")

    def test_toggle_sound(self):
        s = {"sound": True}
        settings_mod.toggle_sound(s)
        self.assertFalse(s["sound"])

    def test_cycle_volume(self):
        s = {"volume": 3}
        settings_mod.cycle_volume(s)
        self.assertEqual(s["volume"], 0)

    def test_cycle_variant(self):
        s = {"variant": "english"}
        settings_mod.cycle_variant(s)
        self.assertEqual(s["variant"], "european")
        settings_mod.cycle_variant(s)
        self.assertEqual(s["variant"], "english")


class ScoreTest(unittest.TestCase):
    def test_load_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(score_mod.load(Path(d) / "no.json"), [])

    def test_add_top10(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            for i in range(15):
                score_mod.add(f"P{i}", i * 10, "english", 5, path=p)
            scores = score_mod.load(p)
            self.assertEqual(len(scores), 10)
            self.assertEqual(scores[0]["score"], 140)

    def test_compute_score_perfect(self):
        # 1 peg + perfect + english: 1000 - 0 + 200 + 0 = 1200
        self.assertEqual(score_mod.compute_score(1, True, "english"), 1200)

    def test_compute_score_won_not_perfect(self):
        # 1 peg + not perfect + english: 1000
        self.assertEqual(score_mod.compute_score(1, False, "english"), 1000)

    def test_compute_score_european_bonus(self):
        # 1 peg + perfect + european: 1000 + 200 + 50 = 1250
        self.assertEqual(score_mod.compute_score(1, True, "european"), 1250)

    def test_compute_score_stuck(self):
        # 5 pegs left, not perfect: 1000 - 4*30 = 880
        self.assertEqual(score_mod.compute_score(5, False, "english"), 880)

    def test_compute_score_zero_pegs(self):
        self.assertEqual(score_mod.compute_score(0, False, "english"), 0)


class SoundTest(unittest.TestCase):
    def test_disabled_silent(self):
        out = io.StringIO()
        s = Sound(enabled=False, volume=3, output=out)
        s.beep(2)
        self.assertEqual(out.getvalue(), "")

    def test_zero_volume_silent(self):
        out = io.StringIO()
        s = Sound(enabled=True, volume=0, output=out)
        s.beep(2)
        self.assertEqual(out.getvalue(), "")

    def test_emits_bells(self):
        out = io.StringIO()
        s = Sound(enabled=True, volume=2, output=out)
        s.jump()      # 1*2
        s.illegal()   # 2*2
        s.win()       # 3*2
        s.stuck()     # 1*2
        # Total = 14 (1+2+3+1 = 7 calls × volume 2)
        self.assertEqual(out.getvalue().count("\a"), 14)


class I18nTest(unittest.TestCase):
    def test_zh(self):
        self.assertIn("孔明棋", t("zh", "title"))

    def test_en(self):
        self.assertIn("Peg", t("en", "title"))

    def test_format_kwargs(self):
        self.assertEqual(t("en", "pegs_left", n=10), "Pegs left: 10")

    def test_unknown_lang_falls_back(self):
        self.assertIsInstance(t("klingon", "title"), str)

    def test_missing_key_returns_key(self):
        self.assertEqual(t("en", "no_such_key_xyz"), "no_such_key_xyz")


if __name__ == "__main__":
    unittest.main()
