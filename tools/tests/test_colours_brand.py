"""Invariants for generated colour tokens and the brand masters.

Run: python3 -m unittest discover -s tools/tests
"""
import json
import sys
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p95 import ROOT, TOKENS, load_context  # noqa: E402
from p95.color import contrast, hex_to_rgb, rgb_to_oklch  # noqa: E402

RAMPS = json.loads((TOKENS / "primitive/color-ramps.json").read_text())["color"]


def ramp(name):
    return [RAMPS[name][str(i)]["$value"]["hex"] for i in range(1, 13)]


class RampTests(unittest.TestCase):
    def test_green_is_palette_verbatim(self):
        with open(ROOT / "brand/source/palette-phosphor95.toml", "rb") as fh:
            pal = tomllib.load(fh)
        used = {pal["core"]["base"], pal["core"]["shadow"], pal["core"]["face"], pal["core"]["face_hover"],
                pal["title"]["inactive_bg"], pal["text"]["fg_faint"], pal["core"]["bevel_light"], pal["text"]["fg_dim"],
                pal["core"]["bevel_hi"], pal["text"]["fg"], pal["status"]["info"], pal["text"]["glow"]}
        self.assertEqual(set(ramp("green")), used)

    def test_every_ramp_monotonic(self):
        for name in ("green", "amber", "white", "red"):
            ls = [rgb_to_oklch(hex_to_rgb(h))[0] for h in ramp(name)]
            self.assertEqual(ls, sorted(ls), name)

    def test_contrast_floors(self):
        for name in ("green", "amber", "white"):
            r = ramp(name)
            face = hex_to_rgb(r[2])
            self.assertGreaterEqual(contrast(hex_to_rgb(r[7]), face), 4.5, f"{name}.8 on {name}.3")
            self.assertGreaterEqual(contrast(hex_to_rgb(r[9]), face), 7.0, f"{name}.10 on {name}.3")

    def test_anchors(self):
        self.assertEqual(ramp("amber")[9], "#ffb000")
        self.assertEqual(ramp("red")[8], "#ff3b3b")


class ThemeTests(unittest.TestCase):
    def test_ansi_sets_distinct(self):
        ansi = json.loads((TOKENS / "primitive/color-ansi.json").read_text())["color"]["ansi"]
        for theme, cols in ansi.items():
            if theme.startswith("$"):
                continue
            hexes = [v["$value"]["hex"] for k, v in cols.items() if not k.startswith("$")]
            self.assertEqual(len(hexes), 16, theme)
            self.assertEqual(len(set(hexes)), 16, f"{theme} repeats a colour")

    def test_same_token_set_in_every_theme(self):
        ctx = load_context()
        paths = {t: set(toks) for t, toks in ctx.themes.items()}
        first = paths[ctx.default_theme]
        for t, p in paths.items():
            self.assertEqual(p, first, f"{t} differs: {sorted(p ^ first)[:5]}")

    def test_amber_warn_distinct_from_text(self):
        t = load_context().themes["amber"]
        self.assertNotEqual(t["status.warn.fg"].value["hex"], t["text.primary"].value["hex"])


class BrandMasterTests(unittest.TestCase):
    def test_master_uses_exactly_avatar_colours(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        avatar = {v["$value"]["hex"] for k, v in RAMPS["avatar"]["green"].items() if not k.startswith("$")}
        for name in ("avatar-phosphor95-48.png", "avatar-phosphor95-16.png"):
            im = Image.open(ROOT / "brand/source" / name).convert("RGBA")
            used = {"#%02x%02x%02x" % c[1][:3] for c in im.getcolors(4096) if c[1][3] >= 128}
            self.assertTrue(used <= avatar, f"{name}: unexpected {used - avatar}")


if __name__ == "__main__":
    unittest.main()
