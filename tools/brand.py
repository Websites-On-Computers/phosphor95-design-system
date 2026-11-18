#!/usr/bin/env python3
"""Generate the Phosphor95 logo set -> brand/logo/   (needs Pillow; the token build doesn't)

    python3 tools/brand.py

Inputs:
  brand/source/avatar-phosphor95-48.png   the lock-screen avatar (master, 6 colours)
  brand/source/avatar-phosphor95-16.png   the same drawing hand-pixelled at 16px (favicons)
  assets/fonts/PxPlus_IBM_VGA_8x16.ttf    wordmark face (pixel-exact at 16px multiples)
  tokens (via tools/p95)                  per-theme colours; the avatar recolours through
                                          operator.* tokens, everything else through semantics

Rules enforced here: integer scaling only (nearest neighbour), no antialiasing anywhere.
Outputs are committed so designers and other repos can grab them without running anything.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p95 import ROOT, load_context  # noqa: E402
from p95.color import dtcg_to_rgba, rgb_to_hex  # noqa: E402

SRC = ROOT / "brand/source"
OUT = ROOT / "brand/logo"
FONT = ROOT / "assets/fonts/PxPlus_IBM_VGA_8x16.ttf"
ROLES = ["hair", "shade-1", "shade-2", "mid", "skin", "light"]
WORD = "PHOSPHOR95"
TAGLINE = "DESIGN SYSTEM"


# ----------------------------------------------------------------- helpers
def hexof(toks, path) -> str:
    return rgb_to_hex(dtcg_to_rgba(toks[path].value)[:3])


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_master(path: Path, green_map: dict[str, str]) -> list[list[str | None]]:
    """Master PNG -> grid of operator role names (None = transparent)."""
    im = Image.open(path).convert("RGBA")
    inv = {rgb(h): role for role, h in green_map.items()}
    grid = []
    for y in range(im.height):
        row = []
        for x in range(im.width):
            r, g, b, a = im.getpixel((x, y))
            if a < 128:
                row.append(None)
                continue
            if (r, g, b) not in inv:
                raise SystemExit(f"{path.name}: pixel ({x},{y}) #{r:02x}{g:02x}{b:02x} is not an operator colour; "
                                 "update AVATAR in tools/gen_ramps.py if the master changed")
            row.append(inv[(r, g, b)])
        grid.append(row)
    return grid


def paint(grid, colours: dict[str, str]) -> Image.Image:
    h, w = len(grid), len(grid[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, row in enumerate(grid):
        for x, role in enumerate(row):
            if role:
                im.putpixel((x, y), (*rgb(colours[role]), 255))
    return im


def up(im: Image.Image, k: int) -> Image.Image:
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def text_bitmap(text: str) -> list[list[int]]:
    """PxPlus 8x16 at its native 16px, 1-bit; plus a trailing block cursor cell."""
    f = ImageFont.truetype(str(FONT), 16)
    w = 8 * len(text)
    im = Image.new("1", (w, 16), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.text((0, 0), text, font=f, fill=1)
    return [[im.getpixel((x, y)) for x in range(w)] for y in range(16)]


def with_cursor(bits, gap=1):
    """Append a full-cell block cursor (8x16) after `gap` blank columns... cursor sits in its own cell."""
    out = []
    for y, row in enumerate(bits):
        cursor = [1] * 7 + [0] if 1 <= y <= 14 else [0] * 8
        out.append(row + cursor)
    return out


def bits_image(bits, colour: str) -> Image.Image:
    h, w = len(bits), len(bits[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    c = (*rgb(colour), 255)
    for y in range(h):
        for x in range(w):
            if bits[y][x]:
                im.putpixel((x, y), c)
    return im


def bevel_frame(w: int, h: int, t: dict[str, str], sunken=True) -> Image.Image:
    """Win95 2px bevel around a base-filled well."""
    im = Image.new("RGBA", (w, h), (*rgb(t["base"]), 255))
    d = ImageDraw.Draw(im)
    tl_out, tl_in, br_out, br_in = (("shadow", "dark", "hi", "light") if sunken else ("light", "hi", "dark", "shadow"))
    for i, (tl, br) in enumerate(((tl_out, br_out), (tl_in, br_in))):
        d.line([(i, h - 1 - i), (i, i), (w - 1 - i, i)], fill=rgb(t[tl]))
        d.line([(i + 1, h - 1 - i), (w - 1 - i, h - 1 - i), (w - 1 - i, i + 1)], fill=rgb(t[br]))
    return im


# --------------------------------------------------------------- SVG output
def runs(grid_or_bits, key):
    """Yield (x, y, length, key) horizontal runs of equal non-empty cells."""
    for y, row in enumerate(grid_or_bits):
        x = 0
        while x < len(row):
            k = key(row[x])
            if k is None:
                x += 1
                continue
            s = x
            while x < len(row) and key(row[x]) == k:
                x += 1
            yield s, y, x - s, k


def svg(w, h, groups: list[tuple[str, list[tuple[int, int, int]]]], title: str, bg: str | None = None, extra: str = "") -> str:
    """groups: [(fill, [(x, y, len)])]. fill may be a CSS var() with fallback."""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
             f'shape-rendering="crispEdges" role="img" aria-label="{title}"><title>{title}</title>']
    if bg:
        parts.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')
    parts.append(extra)
    for fill, rs in groups:
        d = "".join(f"M{x} {y}h{n}v1h-{n}z" for x, y, n in rs)
        parts.append(f'<path fill="{fill}" d="{d}"/>')
    parts.append("</svg>\n")
    return "".join(parts)


def var(name, fallback):
    return f"var(--p95-{name}, {fallback})"


# --------------------------------------------------------------- terminal art
def ansi_halfblocks(img: Image.Image) -> str:
    """Truecolor half-block art: each character = 2 vertical pixels (▀ fg=top, bg=bottom)."""
    img = img.convert("RGBA")
    img = img.crop(img.getbbox())  # drop transparent margins
    px = img.load()
    lines = []
    for y in range(0, img.height, 2):
        cells = []  # (char, fg, bg) with None = terminal default
        for x in range(img.width):
            top = px[x, y]
            bot = px[x, y + 1] if y + 1 < img.height else (0, 0, 0, 0)
            t = top[:3] if top[3] >= 128 else None
            b = bot[:3] if bot[3] >= 128 else None
            if t and b:
                cells.append(("▀", t, b))
            elif t:
                cells.append(("▀", t, None))
            elif b:
                cells.append(("▄", b, None))
            else:
                cells.append((" ", None, None))
        while cells and cells[-1][0] == " ":
            cells.pop()
        out, cur_fg, cur_bg = [], "unset", "unset"
        for ch, fg, bg in cells:
            if ch != " " and fg != cur_fg:
                out.append(f"\x1b[38;2;{fg[0]};{fg[1]};{fg[2]}m")
                cur_fg = fg
            if bg != cur_bg:
                out.append("\x1b[49m" if bg is None else f"\x1b[48;2;{bg[0]};{bg[1]};{bg[2]}m")
                cur_bg = bg
            out.append(ch)
        lines.append("".join(out) + "\x1b[0m")
    return "\n".join(lines) + "\n"


def mono_halfblocks(bits) -> str:
    out = []
    for y in range(0, len(bits), 2):
        top, bot = bits[y], bits[y + 1] if y + 1 < len(bits) else [0] * len(bits[0])
        out.append("".join({(1, 1): "█", (1, 0): "▀", (0, 1): "▄", (0, 0): " "}[(t, b)] for t, b in zip(top, bot)).rstrip())
    return "\n".join(out) + "\n"


ASCII_SHADE = {None: " ", "hair": ":", "shade-1": "-", "shade-2": "=", "mid": "+", "skin": "#", "light": "@"}


def ascii_art(grid) -> str:
    """Pure-ASCII Operator, 2 pixels per character horizontally squashed to 1 (terminal cells are 1:2)."""
    lines = []
    for y in range(0, len(grid), 2):
        row = grid[y]
        lines.append("".join(ASCII_SHADE[row[x]] for x in range(len(row))).rstrip())
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    indent = min(len(l) - len(l.lstrip()) for l in lines if l)
    return "\n".join(l[indent:] for l in lines) + "\n"


# --------------------------------------------------------------------- main
def main():
    ctx = load_context()
    green = {r: hexof(ctx.themes["green"], f"color.avatar.green.{r}") for r in ROLES}
    master48 = load_master(SRC / "avatar-phosphor95-48.png", green)
    master16 = load_master(SRC / "avatar-phosphor95-16.png", green)
    word = with_cursor(text_bitmap(WORD))
    tag = text_bitmap(TAGLINE)
    OUT.mkdir(parents=True, exist_ok=True)
    written = []

    def save(im, name):
        im.save(OUT / name)
        written.append(name)

    def write(text, name):
        (OUT / name).write_text(text, encoding="utf-8")
        written.append(name)

    sheet_rows = []
    for theme, toks in ctx.themes.items():
        op = {r: hexof(toks, f"operator.{r}") for r in ROLES}
        t = {k: hexof(toks, p) for k, p in {
            "base": "surface.base", "face": "surface.face", "text": "text.primary", "hot": "text.hot",
            "secondary": "text.secondary", "hi": "bevel.hi", "light": "bevel.light", "shadow": "bevel.shadow",
            "dark": "bevel.dark"}.items()}

        # Operator, bare (transparent background)
        a48 = paint(master48, op)
        save(a48, f"operator-{theme}.png")
        for k in (2, 4, 8):
            save(up(a48, k), f"operator-{theme}@{k}x.png")

        # Mark: avatar in a sunken 2px-bevel well, 64x64 (8px cell grid)
        mark = bevel_frame(64, 64, t)
        mark.alpha_composite(a48, (8, 8))
        save(mark, f"mark-{theme}.png")
        for k in (2, 4):
            save(up(mark, k), f"mark-{theme}@{k}x.png")

        # Wordmark: PxPlus 8x16, 1-bit, block cursor
        wm = bits_image(word, t["text"])
        for k in (1, 2, 3, 4):
            save(up(wm, k), f"wordmark-{theme}{'' if k == 1 else f'@{k}x'}.png")

        # Horizontal lockup: mark | wordmark @2x over tagline @1x, 64px tall, on face
        W = 64 + 16 + len(word[0]) * 2
        lock = Image.new("RGBA", (W + 16, 80), (*rgb(t["face"]), 255))
        lock.alpha_composite(mark, (8, 8))
        lock.alpha_composite(up(wm, 2), (88, 12))
        lock.alpha_composite(bits_image(tag, t["secondary"]), (88, 52))
        save(lock, f"lockup-{theme}.png")
        save(up(lock, 2), f"lockup-{theme}@2x.png")

        # Static SVGs per theme
        groups = [(op[r], [(x, y, n) for x, y, n, k in runs(master48, lambda v: v) if k == r]) for r in ROLES]
        write(svg(48, 48, groups, "Phosphor95 Operator"), f"operator-{theme}.svg")
        sheet_rows.append((theme, t, lock, a48))

        # Terminal art per theme
        write(ansi_halfblocks(a48), f"operator-{theme}.ansi")

    # Themeable SVGs: colours read --p95-* custom properties, falling back to green
    g = ctx.themes["green"]
    groups = [(var(f"operator-{r}", green[r]), [(x, y, n) for x, y, n, k in runs(master48, lambda v: v) if k == r]) for r in ROLES]
    write(svg(48, 48, groups, "Phosphor95 Operator"), "operator.svg")
    wrs = [(x, y, n) for x, y, n, _ in runs(word, lambda v: 1 if v else None)]
    write(svg(len(word[0]), 16, [(var("text-primary", hexof(g, "text.primary")), wrs)], "PHOSPHOR95"), "wordmark.svg")
    # mark.svg: bevel well + operator, themeable
    bev = (
        f'<rect width="64" height="64" fill="{var("surface-base", hexof(g, "surface.base"))}"/>'
        f'<path fill="{var("bevel-shadow", hexof(g, "bevel.shadow"))}" d="M0 0h64v1H1v63H0z"/>'
        f'<path fill="{var("bevel-dark", hexof(g, "bevel.dark"))}" d="M1 1h62v1H2v62H1z"/>'
        f'<path fill="{var("bevel-hi", hexof(g, "bevel.hi"))}" d="M64 0v64H0v-1h63V0z"/>'
        f'<path fill="{var("bevel-light", hexof(g, "bevel.light"))}" d="M63 1v62H1v-1h61V1z"/>'
    )
    shifted = [(f, [(x + 8, y + 8, n) for x, y, n in rs]) for f, rs in groups]
    write(svg(64, 64, shifted, "Phosphor95", extra=bev), "mark.svg")

    # Favicons / app icons (green): 16px sprite for small sizes, 48px master for large
    a16 = paint(master16, green)
    ab = rgb(hexof(g, "surface.base"))
    save(a16, "favicon-16.png")
    save(up(a16, 2), "favicon-32.png")
    ico = Image.new("RGBA", (48, 48), (*ab, 255))
    ico.alpha_composite(paint(master48, green))
    ico.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)],
             append_images=[up(a16, 1), up(a16, 2)])
    written.append("favicon.ico")
    for size in (180, 192, 512):
        k = (size - 32) // 48
        icon = Image.new("RGBA", (size, size), (*ab, 255))
        av = up(paint(master48, green), k)
        icon.alpha_composite(av, ((size - av.width) // 2, (size - av.height) // 2))
        save(icon, f"icon-{size}.png")

    # Terminal: mono wordmark + ASCII operator
    write(mono_halfblocks(word), "wordmark.txt")
    write(ascii_art(master48), "operator.txt")
    write(ansi_halfblocks(paint(master16, green)), "operator-small.ansi")

    # Contact sheet (verification preview, not a deliverable)
    pad = 16
    rowh = max(r[2].height for r in sheet_rows) * 2
    sw = max(r[2].width for r in sheet_rows) * 2 + 48 * 4 + pad * 3
    sheet = Image.new("RGBA", (sw, len(sheet_rows) * (rowh + pad) + pad), (0, 0, 0, 255))
    for i, (theme, t, lock, a48) in enumerate(sheet_rows):
        y = pad + i * (rowh + pad)
        sheet.alpha_composite(up(lock, 2), (pad, y))
        well = Image.new("RGBA", (192, 192), (*rgb(t["base"]), 255))
        well.alpha_composite(up(a48, 4))
        sheet.alpha_composite(well, (pad * 2 + lock.width * 2, y))
    save(sheet, "_sheet.png")
    print(f"  [ OK ] brand  {len(written)} files -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
