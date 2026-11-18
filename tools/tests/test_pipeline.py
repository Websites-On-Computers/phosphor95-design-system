"""Run: python3 -m unittest discover -s tools/tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p95 import Context, load_context, run_checks  # noqa: E402
from p95 import color as c  # noqa: E402
from p95.dtcg import TokenError, deep_merge, flatten, resolve  # noqa: E402
from p95.targets.css import var_name  # noqa: E402


def col(h):
    return {"$value": c.hex_to_dtcg(h)}


def tokens(tree):
    return resolve(flatten(tree, {}))


class ColourTests(unittest.TestCase):
    def test_contrast_extremes(self):
        self.assertAlmostEqual(c.contrast((0, 0, 0), (255, 255, 255)), 21.0, places=3)
        self.assertAlmostEqual(c.contrast((51, 255, 102), (51, 255, 102)), 1.0)

    def test_known_palette_pair(self):
        # fg on base, measured during planning: 14.92
        self.assertAlmostEqual(c.contrast(c.hex_to_rgb("#33ff66"), c.hex_to_rgb("#020a04")), 14.92, places=2)

    def test_round_trip(self):
        self.assertEqual(c.dtcg_to_rgba(c.hex_to_dtcg("#0a2412"))[:3], (10, 36, 18))

    def test_hex_component_drift_rejected(self):
        v = c.hex_to_dtcg("#33ff66")
        v["hex"] = "#000000"
        with self.assertRaises(c.ColorError):
            c.dtcg_to_rgba(v)

    def test_alpha_css(self):
        self.assertEqual(c.to_css(c.hex_to_dtcg("#33ff66", 0.5)), "rgb(51 255 102 / 0.5)")


class DtcgTests(unittest.TestCase):
    def test_type_inherited_and_alias_resolved(self):
        t = tokens({"color": {"$type": "color", "a": col("#33ff66"), "b": {"$value": "{color.a}"}}})
        self.assertEqual(t["color.b"].value["hex"], "#33ff66")
        self.assertEqual(t["color.b"].alias_of, "color.a")

    def test_alias_chain(self):
        t = tokens({"x": {"$type": "color", "a": col("#ff3b3b"), "b": {"$value": "{x.a}"}, "c": {"$value": "{x.b}"}}})
        self.assertEqual(t["x.c"].value["hex"], "#ff3b3b")

    def test_cycle_detected(self):
        with self.assertRaisesRegex(TokenError, "cycle"):
            tokens({"x": {"$type": "color", "a": {"$value": "{x.b}"}, "b": {"$value": "{x.a}"}}})

    def test_dangling_alias(self):
        with self.assertRaisesRegex(TokenError, "points to no token"):
            tokens({"x": {"$type": "color", "a": {"$value": "{x.nope}"}}})

    def test_missing_type(self):
        with self.assertRaisesRegex(TokenError, "no \\$type"):
            tokens({"x": {"a": {"$value": 1}}})

    def test_type_mismatch_alias(self):
        tree = {"n": {"$type": "number", "a": {"$value": 2}}, "x": {"$type": "color", "b": {"$value": "{n.a}"}}}
        with self.assertRaises(TokenError):
            tokens(tree)

    def test_bad_dimension_unit(self):
        with self.assertRaisesRegex(TokenError, "unit"):
            tokens({"s": {"$type": "dimension", "a": {"$value": {"value": 4, "unit": "em"}}}})

    def test_invalid_name(self):
        with self.assertRaisesRegex(TokenError, "invalid"):
            tokens({"x": {"$type": "number", "a{b}": {"$value": 1}}})

    def test_composite_alias_members(self):
        t = tokens({
            "c": {"$type": "color", "fg": col("#33ff66")},
            "w": {"$type": "dimension", "one": {"$value": {"value": 1, "unit": "px"}}},
            "b": {"$type": "border", "focus": {"$value": {"color": "{c.fg}", "width": "{w.one}", "style": "dashed"}}},
        })
        self.assertEqual(t["b.focus"].value["color"]["hex"], "#33ff66")

    def test_layer_override_replaces_token(self):
        base, src = {}, {}
        deep_merge(base, {"t": {"$type": "color", "a": col("#000000")}}, "base.json", src)
        deep_merge(base, {"t": {"a": col("#ffffff")}}, "theme.json", src)
        t = resolve(flatten(base, src))
        self.assertEqual(t["t.a"].value["hex"], "#ffffff")
        self.assertEqual(t["t.a"].source, "theme.json")


class GateTests(unittest.TestCase):
    def test_gate_fails_bad_pair(self):
        t = tokens({"k": {"$type": "color", "fg": col("#0f5a24"), "bg": col("#0a2412")}})
        ctx = Context(themes={"t": t}, default_theme="t", manifest={})
        fails = run_checks(ctx, [{"fg": "k.fg", "bg": "k.bg", "min": 4.5}])
        self.assertEqual(len(fails), 1)
        self.assertIn("1.97", fails[0])

    def test_gate_unknown_token(self):
        t = tokens({"k": {"$type": "color", "fg": col("#33ff66")}})
        ctx = Context(themes={"t": t}, default_theme="t", manifest={})
        self.assertTrue(run_checks(ctx, [{"fg": "k.fg", "bg": "k.missing", "min": 3}]))

    def test_repo_tokens_pass(self):
        self.assertEqual(run_checks(load_context()), [])


class CssTests(unittest.TestCase):
    def test_theme_block_redeclares_semantic_aliases(self):
        import tempfile
        from p95.targets.css import build as css_build
        with tempfile.TemporaryDirectory() as d:
            css = css_build(load_context(), Path(d))[0].read_text()
        amber = css.split('[data-theme="amber"]', 1)[1].split("}", 1)[0]
        self.assertIn("--p95-text-primary: var(--p95-color-phosphor-10);", amber)
        self.assertIn("--p95-color-phosphor-10: var(--p95-color-amber-10);", amber)

    def test_var_name(self):
        self.assertEqual(var_name("color.source.text.fg-dim"), "--p95-color-source-text-fg-dim")
        self.assertEqual(var_name("title.activeBg"), "--p95-title-active-bg")


if __name__ == "__main__":
    unittest.main()
