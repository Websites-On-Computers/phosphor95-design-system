"""Colour math: DTCG colour objects, hex, WCAG contrast.

DTCG 2025.10 colour values are objects:
    {"colorSpace": "srgb", "components": [r, g, b], "alpha": 1, "hex": "#rrggbb"}
with components in 0..1. We author only sRGB. `hex` is optional per the spec, but
we always write it because it makes the JSON readable.
"""
from __future__ import annotations

import re

_HEX = re.compile(r"^#([0-9a-fA-F]{6})$")


class ColorError(ValueError):
    pass


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    m = _HEX.match(h)
    if not m:
        raise ColorError(f"not a #rrggbb hex colour: {h!r}")
    v = m.group(1)
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def rgb_to_hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb[:3])


def hex_to_dtcg(h: str, alpha: float = 1.0) -> dict:
    r, g, b = hex_to_rgb(h)
    obj = {
        "colorSpace": "srgb",
        "components": [round(r / 255, 4), round(g / 255, 4), round(b / 255, 4)],
        "alpha": alpha,
        "hex": h.lower(),
    }
    return obj


def dtcg_to_rgba(value: dict) -> tuple[int, int, int, float]:
    """Validate a DTCG colour object and return (r, g, b, alpha) with 8-bit channels.

    If `hex` is present it must agree with `components`, so a hand-edited file can't
    drift silently. Disagreement within one 8-bit step is allowed for rounding.
    """
    if not isinstance(value, dict):
        raise ColorError(f"colour $value must be an object, got {type(value).__name__}")
    if value.get("colorSpace") != "srgb":
        raise ColorError(f"only colorSpace 'srgb' is supported, got {value.get('colorSpace')!r}")
    comps = value.get("components")
    if not (isinstance(comps, list) and len(comps) == 3 and all(isinstance(c, (int, float)) for c in comps)):
        raise ColorError("components must be a list of 3 numbers")
    if any(c < 0 or c > 1 for c in comps):
        raise ColorError(f"components must be within 0..1, got {comps}")
    alpha = value.get("alpha", 1)
    if not isinstance(alpha, (int, float)) or not 0 <= alpha <= 1:
        raise ColorError(f"alpha must be a number within 0..1, got {alpha!r}")
    rgb = tuple(round(c * 255) for c in comps)
    if "hex" in value:
        hrgb = hex_to_rgb(value["hex"])
        if any(abs(a - b) > 1 for a, b in zip(rgb, hrgb)):
            raise ColorError(f"hex {value['hex']} disagrees with components {comps}")
        rgb = hrgb
    return rgb[0], rgb[1], rgb[2], float(alpha)


def to_css(value: dict) -> str:
    r, g, b, a = dtcg_to_rgba(value)
    if a >= 1:
        return rgb_to_hex((r, g, b))
    return f"rgb({r} {g} {b} / {a:g})"


def relative_luminance(rgb) -> float:
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg_rgb, bg_rgb) -> float:
    """WCAG 2.x contrast ratio, 1..21."""
    a, b = relative_luminance(fg_rgb), relative_luminance(bg_rgb)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


# ------------------------------------------------------------------ OKLab / OKLCH
# Björn Ottosson's OKLab (2020). Used to derive ramps with matching perceived lightness.
import math


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def rgb_to_oklch(rgb) -> tuple[float, float, float]:
    r, g, b = (_lin(c / 255) for c in rgb[:3])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def _oklch_to_linear(L: float, C: float, h: float) -> tuple[float, float, float]:
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def oklch_to_hex(L: float, C: float, h: float) -> str:
    """OKLCH -> #rrggbb, reducing chroma (keeping L and h) until it fits in sRGB."""
    def fits(c):
        return all(-1e-6 <= x <= 1 + 1e-6 for x in _oklch_to_linear(L, c, h))

    if not fits(C):
        lo, hi = 0.0, C
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if fits(mid) else (lo, mid)
        C = lo
    return rgb_to_hex(tuple(_gam(min(1, max(0, x))) * 255 for x in _oklch_to_linear(L, C, h)))
