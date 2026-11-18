#!/usr/bin/env python3
"""Import the Phosphor-95 palette.toml as DTCG primitive tokens.

    python3 tools/import_palette.py [path/to/palette.toml]

Default input is brand/source/palette-phosphor95.toml, a snapshot of
../theme/config/palette.toml. Output is tokens/primitive/color-source.json under the
group `color.source.<section>.<role>`, values kept exactly as they are in the theme.

This is the provenance layer. Phase 1 builds the designed ramps and semantic roles
on top of it, and nothing outside tokens/ should reference `color.source.*` directly.
"""
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p95 import ROOT, TOKENS  # noqa: E402
from p95.color import hex_to_dtcg  # noqa: E402


def main(argv):
    src = Path(argv[0]) if argv else ROOT / "brand/source/palette-phosphor95.toml"
    with open(src, "rb") as fh:
        pal = tomllib.load(fh)
    group: dict = {
        "$type": "color",
        "$description": "Phosphor-95 GNOME theme palette, imported verbatim. Provenance only: reference semantic tokens, not these.",
    }
    for section, roles in pal.items():
        group[section] = {
            role.replace("_", "-"): {"$value": hex_to_dtcg(h)} for role, h in roles.items()
        }
    out = TOKENS / "primitive/color-source.json"
    out.write_text(json.dumps({"color": {"source": group}}, indent=2) + "\n", encoding="utf-8")
    n = sum(len(r) for r in pal.values())
    print(f"  [ OK ] imported {n} colours from {src.relative_to(ROOT) if src.is_relative_to(ROOT) else src} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
