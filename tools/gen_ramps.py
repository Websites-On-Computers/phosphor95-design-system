#!/usr/bin/env python3
"""Generate the 12-step colour ramps and per-theme ANSI-16 sets
-> tokens/primitive/color-ramps.json, tokens/primitive/color-ansi.json

    python3 tools/gen_ramps.py

Green is the Phosphor-95 palette verbatim: its 12 colours, sorted by lightness, are the
12 steps. Every other ramp copies green's OKLCH lightness curve step by step, in its own
hue, with chroma scaled to the ramp's anchor. So step N plays the same role, at roughly
the same contrast, in every theme. Anchors pin existing colours exactly (e.g. amber.10 is
the theme's warn #ffb000), and tools/build.py's contrast gate checks the results.

Re-run after editing GREEN or RAMPS. The output is committed; tokens/ stays the source of truth.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p95 import ROOT, TOKENS  # noqa: E402
from p95.color import contrast, hex_to_dtcg, hex_to_rgb, oklch_to_hex, rgb_to_oklch  # noqa: E402

# step -> (hex, job, palette.toml origin)
GREEN = {
    1:  ("#020a04", "App background, text fields, terminal background", "core.base"),
    2:  ("#041208", "Bevel shadow, sunken wells", "core.shadow"),
    3:  ("#0a2412", "Face: windows, panels, buttons", "core.face"),
    4:  ("#0e3018", "Face hover", "core.face_hover"),
    5:  ("#0b4419", "Subtle selected / inactive title bar", "title.inactive_bg"),
    6:  ("#0f5a24", "Faint: disabled text, hairlines (decorative only, below 3:1)", "text.fg_faint"),
    7:  ("#1c7a36", "Border, bevel light", "core.bevel_light"),
    8:  ("#1fa046", "Dim: secondary text, hints, placeholders", "text.fg_dim"),
    9:  ("#2fbf55", "Solid: bevel highlight, strong border", "core.bevel_hi"),
    10: ("#33ff66", "Phosphor: primary text, solid fills, selection", "text.fg"),
    11: ("#7dffa8", "Bright: info, links, hover text", "status.info"),
    12: ("#b6ffc8", "Glow: hot text, focus, cursor", "text.glow"),
}

# name -> (hue/chroma source hex, its lightness-matched step, {step: anchor hex}, description)
# The source sets hue and the chroma ratio against green's step of similar lightness.
# Anchors replace derived steps exactly; they must keep the ramp monotonic (asserted).
RAMPS = {
    "amber": ("#ffb000", 10, {10: "#ffb000"}, "P3 amber phosphor. amber.10 = the theme's warn colour #ffb000."),
    "white": ("#e0e8f0", 10, {}, "P4 white phosphor: a faintly cool white."),
    "red":   ("#ff3b3b", 9, {9: "#ff3b3b"}, "Errors. red.9 = the theme's error colour #ff3b3b (its lightness sits at step 9)."),
    "blue":  ("#5fb4ff", 10, {}, "Cool accent: info in the white theme, ANSI blue/cyan in amber and white. Never a UI ramp."),
}


# Contrast floors every ramp must meet against its face step (3), whatever the hue does to
# perceived vs WCAG lightness: step -> minimum ratio on step 3. A derived step is lightened in
# small OKLCH-L increments until it passes. Anchored steps are never moved (gate checks them).
FLOORS = {7: 3.05, 8: 4.6, 10: 7.0}


def derive(src_hex: str, src_step: int, anchors: dict[int, str]) -> dict[int, str]:
    _, cs, h = rgb_to_oklch(hex_to_rgb(src_hex))
    _, cg, _ = rgb_to_oklch(hex_to_rgb(GREEN[src_step][0]))
    k = cs / cg
    out = {}
    for step, (g, _, _) in GREEN.items():
        L, C, _ = rgb_to_oklch(hex_to_rgb(g))
        out[step] = anchors.get(step) or oklch_to_hex(L, C * k, h)
    face = hex_to_rgb(out[3])
    for step, floor in FLOORS.items():
        if step in anchors:
            continue
        L, C, _ = rgb_to_oklch(hex_to_rgb(GREEN[step][0]))
        while contrast(hex_to_rgb(out[step]), face) < floor and L < 1:
            L += 0.002
            out[step] = oklch_to_hex(L, C * k, h)
    ls = [rgb_to_oklch(hex_to_rgb(out[st]))[0] for st in sorted(out)]
    assert ls == sorted(ls), f"ramp from {src_hex} is not monotonic in lightness: {out}"
    return out


# The Operator: the six opaque colours of brand/source/avatar-phosphor95-48.png (the
# lock-screen avatar), exact. tools/brand.py asserts the master still uses exactly these.
AVATAR = {"hair": "#04170a", "shade-1": "#072710", "shade-2": "#093516",
          "mid": "#1fa146", "skin": "#35ff67", "light": "#b6ffc8"}

ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
              "bright-black", "bright-red", "bright-green", "bright-yellow",
              "bright-blue", "bright-magenta", "bright-cyan", "bright-white"]


def shift(hex_: str, src_hex: str, src_step: int) -> str:
    """Move a green-hued colour into another ramp's hue, keeping its lightness."""
    _, cs, h = rgb_to_oklch(hex_to_rgb(src_hex))
    _, cg, _ = rgb_to_oklch(hex_to_rgb(GREEN[src_step][0]))
    L, C, _ = rgb_to_oklch(hex_to_rgb(hex_))
    return oklch_to_hex(L, C * cs / cg, h)


def ansi_sets(ramps: dict[str, dict[int, str]]) -> dict[str, dict[str, str]]:
    import tomllib
    with open(ROOT / "brand/source/palette-phosphor95.toml", "rb") as fh:
        green = {k.replace("_", "-"): v for k, v in tomllib.load(fh)["ansi"].items()}
    assert list(green) == ANSI_NAMES, list(green)
    a, w, r, b = ramps["amber"], ramps["white"], ramps["red"], ramps["blue"]
    # Hand-mapped so every slot keeps a distinct hue or lightness: a plain hue shift
    # collapsed cyan/magenta/white into near-identical pale tints.
    amber = {
        "black": a[1], "red": r[9], "green": a[10], "yellow": w[10],
        "blue": a[8], "magenta": r[10], "cyan": b[10], "white": a[12],
        "bright-black": a[6], "bright-red": green["bright-red"], "bright-green": a[11], "bright-yellow": w[12],
        "bright-blue": a[9], "bright-magenta": r[11], "bright-cyan": b[11], "bright-white": shift(green["bright-white"], *RAMPS["amber"][:2]),
    }
    white = {
        "black": w[1], "red": r[9], "green": green["green"], "yellow": green["yellow"],
        "blue": b[8], "magenta": r[10], "cyan": b[10], "white": w[10],
        "bright-black": w[6], "bright-red": green["bright-red"], "bright-green": green["bright-green"], "bright-yellow": green["bright-yellow"],
        "bright-blue": b[9], "bright-magenta": r[11], "bright-cyan": b[11], "bright-white": w[12],
    }
    hc = dict(green, black="#000000")
    hc["bright-black"] = GREEN[8][0]  # readable dim instead of faint
    hc["blue"] = b[9]                  # green.8 is taken by bright-black; keep all 16 distinct
    return {"green": green, "amber": amber, "white": white, "hc": hc}


def main():
    color: dict = {"$type": "color"}
    ls = [rgb_to_oklch(hex_to_rgb(GREEN[s][0]))[0] for s in sorted(GREEN)]
    assert ls == sorted(ls), "green ramp must increase in lightness"
    color["green"] = {
        "$description": "P1 green phosphor. The Phosphor-95 palette verbatim; step jobs are listed per token.",
        **{str(s): {"$value": hex_to_dtcg(h), "$description": f"{job} (palette.toml {src})"} for s, (h, job, src) in GREEN.items()},
    }
    for name, (src, src_step, anchors, desc) in RAMPS.items():
        r = derive(src, src_step, anchors)
        color[name] = {"$description": desc, **{str(s): {"$value": hex_to_dtcg(h)} for s, h in r.items()}}
    ramps = {n: {int(k): v["$value"]["hex"] for k, v in color[n].items() if k.isdigit()} for n in RAMPS}
    ansi = ansi_sets(ramps)
    ansi_doc = {"color": {"ansi": {
        "$type": "color",
        "$description": "Terminal ANSI-16 per theme. green = palette.toml verbatim; amber/white = hand-mapped onto ramp steps so every slot stays distinct (amber: yellow -> white, cyan -> blue; white: keeps real green/yellow, blue/cyan from the blue ramp); hc = green with true-black and a readable bright-black.",
        **{t: {n: {"$value": hex_to_dtcg(h)} for n, h in cols.items()} for t, cols in ansi.items()},
    }}}
    out_ansi = TOKENS / "primitive/color-ansi.json"
    out_ansi.write_text(json.dumps(ansi_doc, indent=2) + "\n", encoding="utf-8")
    color["avatar"] = {
        "$description": "Operator avatar colours per ramp. green = the lock-screen PNG exactly; others shifted at equal lightness.",
        "green": {k: {"$value": hex_to_dtcg(v)} for k, v in AVATAR.items()},
        **{r: {k: {"$value": hex_to_dtcg(shift(v, *RAMPS[r][:2]))} for k, v in AVATAR.items()} for r in ("amber", "white")},
    }
    color["void"] = {"$value": hex_to_dtcg("#000000"), "$description": "True black: bevel dark edge, CRT off."}
    out = TOKENS / "primitive/color-ramps.json"
    out.write_text(json.dumps({"color": color}, indent=2) + "\n", encoding="utf-8")
    print(f"  [ OK ] ramps green, {', '.join(RAMPS)} -> {out.relative_to(ROOT)}")
    for name in ["green", *RAMPS]:
        steps = [color[name][str(s)]["$value"]["hex"] for s in range(1, 13)]
        print(f"         {name:<6} " + " ".join(steps))
    print(f"  [ OK ] ansi  {', '.join(ansi)} -> {out_ansi.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
