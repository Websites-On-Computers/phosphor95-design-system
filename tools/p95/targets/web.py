"""dist/web/: the @phosphor95/web package.

    p95.css           everything, in cascade layers:
                      p95.reset, p95.tokens, p95.base, p95.components, p95.utilities, p95.effects
    p95-tokens.css    tokens + derived recipes only (bring your own components)
    fonts/            PxPlus, VT323, W95FA + licenses
    js/               vanilla Web Components (ES modules), js/index.js registers all
    brand/            logo SVGs, favicons, Operator PNGs
    icons/            curated Chicago95-recoloured icon subset

Pixel glyphs (checkmark, radio, arrows, title-bar controls) are drawn here from ASCII
pixel maps:
  * as CSS masks (`--p95-mask-*`), coloured with tokens at use site (recolour with themes)
  * as per-theme coloured images (`--p95-img-*`), for places a mask can't reach
    (a select's background layer, scrollbar buttons)
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from urllib.parse import quote

from .. import ROOT
from .. import color as colour
from . import css as css_target

SRC = ROOT / "packages/web/src"
LAYERS = ["reset", "tokens", "base", "components", "utilities", "effects"]
CSS_FILES = {  # layer -> source files (in order)
    "reset": ["reset.css"],
    "tokens": ["fonts.css", "@tokens", "masks.css", "recipes.css"],
    "base": ["base.css"],
    "components": ["components.css"],
    "utilities": ["utilities.css"],
    "effects": ["effects.css"],
}

# '#' = pixel on. Every glyph is drawn at 1x on the pixel grid.
PIXELS = {
    "check": [
        "......#.",
        ".....##.",
        "#...###.",
        "##.###..",
        "#####...",
        ".###....",
        "..#.....",
        "........",
    ],
    "radio-ring": [
        "....########....",
        "..############..",
        ".##############.",
        ".##############.",
        "################",
        "################",
        "################",
        "################",
        "################",
        "################",
        "################",
        "################",
        ".##############.",
        ".##############.",
        "..############..",
        "....########....",
    ],
    "radio-well": [
        "................",
        "....########....",
        "..############..",
        "..############..",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        ".##############.",
        "..############..",
        "..############..",
        "....########....",
        "................",
    ],
    "radio-dot": [
        "................", "................", "................", "................",
        "................", "......####......", ".....######.....", ".....######.....",
        ".....######.....", ".....######.....", "......####......", "................",
        "................", "................", "................", "................",
    ],
    "arrow-down": ["#######", ".#####.", "..###..", "...#..."],
    "arrow-up": ["...#...", "..###..", ".#####.", "#######"],
    "arrow-right": ["#...", "##..", "###.", "####", "###.", "##..", "#..."],
    "arrow-left": ["...#", "..##", ".###", "####", ".###", "..##", "...#"],
    "close": [
        "##....##",
        ".##..##.",
        "..####..",
        "...##...",
        "..####..",
        ".##..##.",
        "##....##",
    ],
    "minimize": ["........", "........", "........", "........", "........", "######..", "######.."],
    "maximize": [
        "#########",
        "#########",
        "#.......#",
        "#.......#",
        "#.......#",
        "#.......#",
        "#.......#",
        "#########",
    ],
    "restore": [
        "..######",
        "..######",
        "..#....#",
        "######.#",
        "######.#",
        "#....###",
        "#....#..",
        "######..",
    ],
}

# Per-theme coloured images: name -> (pixel map, token whose colour fills it)
IMAGES = {
    "arrow-down": ("arrow-down", "text.primary"),
    "arrow-down-disabled": ("arrow-down", "text.disabled"),
    "arrow-up": ("arrow-up", "text.primary"),
    "arrow-left": ("arrow-left", "text.primary"),
    "arrow-right": ("arrow-right", "text.primary"),
}

ICONS = {  # published name -> Phosphor95 icon-theme path (relative to the theme root)
    "folder": "places/{s}/folder.png", "folder-open": "status/{s}/folder-open.png",
    "file": "mimes/{s}/text-x-generic.png", "terminal": "apps/{s}/utilities-terminal.png",
    "computer": "devices/{s}/computer.png", "network": "places/{s}/network-workgroup.png",
    "trash": "places/{s}/user-trash.png", "search": "actions/{s}/system-search.png",
    "settings": "categories/{s}/preferences-system.png", "info": "status/{s}/dialog-information.png",
    "warning": "status/{s}/dialog-warning.png", "error": "status/{s}/dialog-error.png",
    "help": "apps/{s}/help-browser.png", "clock": "apps/{s}/preferences-system-time.png",
    "audio": "devices/{s}/audio-speakers.png", "microphone": "devices/{s}/audio-input-microphone.png",
    "drive": "devices/{s}/drive-harddisk.png", "printer": "devices/{s}/printer.png",
    "mail": "apps/{s}/internet-mail.png", "globe": "apps/{s}/internet-web-browser.png",
    "lock": "status/{s}/changes-prevent.png", "user": "status/{s}/avatar-default.png",
}
ICON_THEME = Path.home() / ".local/share/icons/Phosphor95"


def _svg(rows: list[str], fill: str = "#000") -> str:
    h, w = len(rows), len(rows[0])
    d = []
    for y, row in enumerate(rows):
        x = 0
        while x < w:
            if row[x] == "#":
                s = x
                while x < w and row[x] == "#":
                    x += 1
                d.append(f"M{s} {y}h{x - s}v1h-{x - s}z")
            else:
                x += 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'shape-rendering="crispEdges"><path fill="{fill}" d="{"".join(d)}"/></svg>')


def _url(svg: str) -> str:
    return 'url("data:image/svg+xml,' + quote(svg, safe=" =:/,;'") + '")'


def masks_css(ctx) -> str:
    lines = ["/* Generated by tools/p95/targets/web.py: pixel glyphs. Masks take colour at use site. */", ":root {"]
    for name, rows in PIXELS.items():
        lines.append(f"  --p95-mask-{name}: {_url(_svg(rows))};")
    lines.append("}")
    for theme, toks in ctx.themes.items():
        sel = ":root, [data-theme=\"%s\"]" % theme if theme == ctx.default_theme else f'[data-theme="{theme}"]'
        lines.append(f"{sel} {{")
        for name, (glyph, token) in IMAGES.items():
            hexv = colour.rgb_to_hex(colour.dtcg_to_rgba(toks[token].value)[:3])
            lines.append(f"  --p95-img-{name}: {_url(_svg(PIXELS[glyph], hexv))};")
        lines.append("}")
    return "\n".join(lines) + "\n"


def _tokens_css(ctx, tmp: Path) -> str:
    css_target.build(ctx, tmp)
    return (tmp / "tokens.css").read_text(encoding="utf-8")


def build(ctx, out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    tokens = _tokens_css(ctx, out / "_tmp")
    shutil.rmtree(out / "_tmp")
    masks = masks_css(ctx)

    def source(name: str) -> str:
        if name == "@tokens":
            return tokens
        if name == "masks.css":
            return masks
        return (SRC / "css" / name).read_text(encoding="utf-8")

    header = ("/* @phosphor95/web. Generated by tools/build.py; do not edit (sources: packages/web/src/css). */\n"
              f"@layer {', '.join('p95.' + l for l in LAYERS)};\n")
    bundle = [header]
    for layer in LAYERS:
        body = "\n".join(source(f) for f in CSS_FILES[layer])
        # @font-face must not sit inside @layer for older engines; it is layer-agnostic anyway.
        if layer == "tokens":
            fonts = source("fonts.css")
            body = body.replace(fonts, "")
            bundle.append(fonts)
        bundle.append(f"@layer p95.{layer} {{\n{body}\n}}\n")
    (out / "p95.css").write_text("\n".join(bundle), encoding="utf-8")
    (out / "p95-tokens.css").write_text(
        header + source("fonts.css") + "@layer p95.tokens {\n" + tokens + masks + source("recipes.css") + "}\n",
        encoding="utf-8")
    written += [out / "p95.css", out / "p95-tokens.css"]

    # fonts
    fdir = out / "fonts"
    shutil.copytree(ROOT / "assets/fonts", fdir)
    written.append(fdir)

    # js
    jdir = out / "js"
    shutil.copytree(SRC / "js", jdir)
    op_svg = (ROOT / "brand/logo/operator.svg").read_text(encoding="utf-8").strip()
    (jdir / "operator-svg.js").write_text(
        "// Generated from brand/logo/operator.svg by tools/build.py.\n"
        f"export default {json.dumps(op_svg)};\n", encoding="utf-8")
    wm_svg = (ROOT / "brand/logo/wordmark.svg").read_text(encoding="utf-8").strip()
    (jdir / "wordmark-svg.js").write_text(
        "// Generated from brand/logo/wordmark.svg by tools/build.py.\n"
        f"export default {json.dumps(wm_svg)};\n", encoding="utf-8")
    written.append(jdir)

    # brand
    bdir = out / "brand"
    bdir.mkdir()
    for f in ["mark.svg", "operator.svg", "wordmark.svg", "favicon.ico", "favicon-16.png", "favicon-32.png",
              "icon-180.png", "icon-192.png", "icon-512.png"] + [
              f"{k}-{t}{s}.png" for k in ("operator", "mark") for t in ctx.themes for s in ("", "@2x")]:
        src = ROOT / "brand/logo" / f
        if src.exists():
            shutil.copy2(src, bdir / f)
    written.append(bdir)

    # icons (only if the icon theme is installed; the package ships whatever was copied last)
    idir = ROOT / "assets/icons"
    if ICON_THEME.exists():
        for name, rel in ICONS.items():
            for size in (16, 32):
                src = ICON_THEME / rel.format(s=size)
                if src.exists():
                    (idir / str(size)).mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src.resolve(), idir / str(size) / f"{name}.png")
    if (idir / "16").exists():
        shutil.copytree(idir, out / "icons", ignore=shutil.ignore_patterns("README.md"))
        written.append(out / "icons")

    pkg = json.loads((ROOT / "packages/web/package.json").read_text(encoding="utf-8"))
    (out / "package.json").write_text(json.dumps(pkg, indent=2) + "\n", encoding="utf-8")
    written.append(out / "package.json")
    return written
