#!/usr/bin/env python3
"""Render ANSI terminal output to a PNG, as a Phosphor95 terminal would show it (needs Pillow).

    cargo run --example gallery -- --snapshot --theme amber | python3 tools/ansi2png.py - out.png --theme amber

The 16-colour palette, default fg/bg come from the theme's generated Ghostty scheme. Font: PxPlus
IBM VGA 9x16 (the Phosphor-95 terminal face), with DejaVu Sans Mono for glyphs it lacks (braille).
Supports SGR 0/1/2/4/7, 30-37/90-97/39, 40-47/100-107/49, 38;5;n, 48;5;n, 38;2;r;g;b, 48;2;r;g;b.
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CW, CH = 9, 16


def scheme(theme):
    s = {}
    for line in (ROOT / f"packages/tui/terminal-themes/ghostty/phosphor95-{theme}").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = (x.strip() for x in line.split("=", 1))
            if k == "palette":
                i, c = v.split("=")
                s[int(i)] = c
            else:
                s[k] = v
    return s


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def x256(i, pal):
    if i < 16:
        return rgb(pal[i])
    if i >= 232:
        v = 8 + 10 * (i - 232)
        return (v, v, v)
    i -= 16
    lv = [0, 95, 135, 175, 215, 255]
    return (lv[i // 36], lv[(i // 6) % 6], lv[i % 6])


def main(argv):
    src, out = argv[0], argv[1]
    theme = argv[argv.index("--theme") + 1] if "--theme" in argv else "green"
    text = sys.stdin.read() if src == "-" else Path(src).read_text()
    sc = scheme(theme)
    dfg, dbg = rgb(sc["foreground"]), rgb(sc["background"])
    lines = text.rstrip("\n").split("\n")
    cols = max(len(re.sub(r"\x1b\[[0-9;]*m", "", l)) for l in lines)
    img = Image.new("RGB", (cols * CW, len(lines) * CH), dbg)
    d = ImageDraw.Draw(img)
    px = ImageFont.truetype(str(ROOT / "assets/fonts/PxPlus_IBM_VGA_9x16.ttf"), 16)
    try:
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
    except OSError:  # macOS has no DejaVu; Menlo is close enough for the fallback glyphs
        fb = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
    cmap = set()
    try:
        from PIL import features  # noqa: F401
    except Exception:
        pass

    def has(ch):
        try:
            return px.getmask(ch).getbbox() is not None or ch == " "
        except Exception:
            return False

    for y, line in enumerate(lines):
        fg, bg, bold, dim, rev = None, None, False, False, False
        x = 0
        for tok in re.findall(r"\x1b\[[0-9;]*m|.", line):
            if tok.startswith("\x1b["):
                codes = [int(c) for c in tok[2:-1].split(";") if c != ""] or [0]
                i = 0
                while i < len(codes):
                    c = codes[i]
                    if c == 0: fg, bg, bold, dim, rev = None, None, False, False, False
                    elif c == 1: bold = True
                    elif c == 2: dim = True
                    elif c == 7: rev = True
                    elif 30 <= c <= 37: fg = rgb(sc[c - 30])
                    elif 90 <= c <= 97: fg = rgb(sc[c - 90 + 8])
                    elif c == 39: fg = None
                    elif 40 <= c <= 47: bg = rgb(sc[c - 40])
                    elif 100 <= c <= 107: bg = rgb(sc[c - 100 + 8])
                    elif c == 49: bg = None
                    elif c in (38, 48) and codes[i + 1] == 5:
                        col = x256(codes[i + 2], sc); i += 2
                        if c == 38: fg = col
                        else: bg = col
                    elif c in (38, 48) and codes[i + 1] == 2:
                        col = tuple(codes[i + 2:i + 5]); i += 4
                        if c == 38: fg = col
                        else: bg = col
                    i += 1
                continue
            f, b = fg or dfg, bg or dbg
            if rev: f, b = b, f
            if dim: f = tuple((a + c) // 2 for a, c in zip(f, b))
            d.rectangle([x * CW, y * CH, x * CW + CW - 1, y * CH + CH - 1], fill=b)
            if tok != " ":
                if tok in "▀▄█":
                    top = tok in "▀█"; bot = tok in "▄█"
                    if top: d.rectangle([x * CW, y * CH, x * CW + CW - 1, y * CH + CH // 2 - 1], fill=f)
                    if bot: d.rectangle([x * CW, y * CH + CH // 2, x * CW + CW - 1, y * CH + CH - 1], fill=f)
                elif has(tok):
                    d.text((x * CW, y * CH), tok, font=px, fill=f)
                else:
                    d.text((x * CW, y * CH + 1), tok, font=fb, fill=f)
            x += 1
    img.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
