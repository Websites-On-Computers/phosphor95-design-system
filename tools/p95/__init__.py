"""Phosphor95 design-system token pipeline (python3 stdlib only)."""
from __future__ import annotations

import glob
import json
from dataclasses import dataclass
from pathlib import Path

from . import color as colour
from .dtcg import Token, TokenError, build_theme

ROOT = Path(__file__).resolve().parents[2]
TOKENS = ROOT / "tokens"
DIST = ROOT / "dist"
PREFIX = "p95"


@dataclass
class Context:
    themes: dict[str, dict[str, Token]]  # theme name -> resolved tokens
    default_theme: str
    manifest: dict

    @property
    def default(self) -> dict[str, Token]:
        return self.themes[self.default_theme]


def _expand(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pat in patterns:
        hits = sorted(glob.glob(str(TOKENS / pat)))
        if not hits:
            raise TokenError(f"manifest pattern {pat!r} matched no files")
        files += [Path(h) for h in hits if Path(h) not in files]
    return files


def load_context() -> Context:
    with open(TOKENS / "manifest.json", encoding="utf-8") as fh:
        manifest = json.load(fh)
    base = manifest["sources"]
    themes = {}
    for name, layers in manifest["themes"].items():
        themes[name] = build_theme(TOKENS, _expand(base + layers))
    default = manifest["defaultTheme"]
    if default not in themes:
        raise TokenError(f"defaultTheme {default!r} is not in themes")
    return Context(themes=themes, default_theme=default, manifest=manifest)


def run_checks(ctx: Context, checks: list[dict] | None = None) -> list[str]:
    """Contrast gate (default: tokens/checks.json). Returns failure messages (empty = pass)."""
    if checks is None:
        with open(TOKENS / "checks.json", encoding="utf-8") as fh:
            checks = json.load(fh)["contrast"]
    failures = []
    for theme, toks in ctx.themes.items():
        for c in checks:
            if c.get("themes") and theme not in c["themes"]:
                continue
            for key in ("fg", "bg"):
                if c[key] not in toks:
                    failures.append(f"{theme}: check refers to unknown token '{c[key]}'")
                    break
            else:
                fg = colour.dtcg_to_rgba(toks[c["fg"]].value)
                bg = colour.dtcg_to_rgba(toks[c["bg"]].value)
                ratio = colour.contrast(fg, bg)
                if ratio + 1e-9 < c["min"]:
                    failures.append(
                        f"{theme}: {c['fg']} on {c['bg']} = {ratio:.2f}:1, needs {c['min']}:1 ({c.get('why', '')})"
                    )
    return failures
