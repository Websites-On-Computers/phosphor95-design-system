"""DTCG 2025.10 token loading, validation and alias resolution.

Subset implemented (enough for this system; extend as needed):
  * groups and tokens (`$value`), `$type` inherited from the nearest group
  * `$description`, `$extensions`, `$deprecated` carried through
  * curly-brace aliases, `"{color.green.9}"`, as a whole value or inside composites
  * types: color, dimension, duration, number, fontFamily, fontWeight,
    cubicBezier, plus the composites border, typography, transition, shadow,
    strokeStyle (structure-checked, members resolved)
Not implemented: `$ref` JSON-pointer references, `$extends` group inheritance, and the
Resolver module. Themes are layered by `tokens/manifest.json` instead, which plays the
same role as the resolver's sets and modifiers.
"""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import color as colour

ALIAS = re.compile(r"^\{([^{}]+)\}$")
NAME_OK = re.compile(r"^[^{}.$][^{}.]*$")  # spec: names can't start with $ or contain { } .

SIMPLE_TYPES = {"color", "dimension", "duration", "number", "fontFamily", "fontWeight", "cubicBezier"}
COMPOSITE_KEYS = {
    "border": {"color", "width", "style"},
    "typography": {"fontFamily", "fontSize", "fontWeight", "letterSpacing", "lineHeight"},
    "transition": {"duration", "delay", "timingFunction"},
    "shadow": {"color", "offsetX", "offsetY", "blur", "spread"},
    "strokeStyle": None,  # string keyword or object, checked loosely
}
FONT_WEIGHT_WORDS = {
    "thin", "hairline", "extra-light", "ultra-light", "light", "normal", "regular", "book",
    "medium", "semi-bold", "demi-bold", "bold", "extra-bold", "ultra-bold", "black", "heavy",
    "extra-black", "ultra-black",
}


class TokenError(ValueError):
    pass


@dataclass
class Token:
    path: str                  # dotted, e.g. "color.green.9"
    type: str
    raw: object                # $value as authored (may contain aliases)
    value: object = None       # resolved
    description: str = ""
    extensions: dict = field(default_factory=dict)
    deprecated: object = False
    source: str = ""           # file the final definition came from

    @property
    def alias_of(self) -> str | None:
        """Target path if the whole value is a single alias, else None."""
        if isinstance(self.raw, str):
            m = ALIAS.match(self.raw)
            if m:
                return m.group(1)
        return None


# ------------------------------------------------------------------- loading
def load_json(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        raise TokenError(f"{path}: invalid JSON: {e}") from None
    if not isinstance(data, dict):
        raise TokenError(f"{path}: top level must be an object")
    return data


def deep_merge(base: dict, over: dict, src: str, sources: dict, prefix: str = "") -> dict:
    """Merge `over` into `base`. A token in `over` replaces the whole token in `base`.

    `sources` records which file last defined each token path (for error messages).
    """
    for k, v in over.items():
        p = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and "$value" in v:
            base[k] = copy.deepcopy(v)
            sources[p] = src
        elif isinstance(v, dict) and not k.startswith("$"):
            if k in base and isinstance(base[k], dict) and "$value" in base[k]:
                raise TokenError(f"{src}: '{p}' is a token in an earlier file but a group here")
            base[k] = deep_merge(base.get(k, {}), v, src, sources, p)
        else:
            base[k] = copy.deepcopy(v)
    return base


def load_layers(files: list[Path], root: Path) -> tuple[dict, dict]:
    tree: dict = {}
    sources: dict = {}
    for f in files:
        deep_merge(tree, load_json(f), str(f.relative_to(root)), sources)
    return tree, sources


def flatten(tree: dict, sources: dict) -> dict[str, Token]:
    out: dict[str, Token] = {}

    def walk(node: dict, path: list[str], inherited_type: str | None):
        gtype = node.get("$type", inherited_type)
        for k, v in node.items():
            if k.startswith("$"):
                continue
            if not NAME_OK.match(k):
                raise TokenError(f"invalid token/group name {'.'.join(path + [k])!r}")
            if not isinstance(v, dict):
                raise TokenError(f"'{'.'.join(path + [k])}' must be an object (group or token)")
            p = path + [k]
            dotted = ".".join(p)
            if "$value" in v:
                ttype = v.get("$type", gtype)
                if not ttype:
                    raise TokenError(f"'{dotted}' has no $type (set it on the token or a parent group)")
                out[dotted] = Token(
                    path=dotted,
                    type=ttype,
                    raw=v["$value"],
                    description=v.get("$description", ""),
                    extensions=v.get("$extensions", {}),
                    deprecated=v.get("$deprecated", False),
                    source=sources.get(dotted, ""),
                )
            else:
                walk(v, p, gtype)

    walk(tree, [], None)
    return out


# ---------------------------------------------------------------- resolution
def resolve(tokens: dict[str, Token]) -> dict[str, Token]:
    """Resolve aliases in place (with cycle detection), then validate every value."""
    state: dict[str, str] = {}  # path -> "visiting" | "done"

    def deref(path: str, chain: list[str]):
        if path not in tokens:
            raise TokenError(f"alias {{{path}}} in '{chain[-1]}' points to no token")
        tok = tokens[path]
        if state.get(path) == "done":
            return tok.value
        if state.get(path) == "visiting":
            cyc = " -> ".join(chain[chain.index(path):] + [path])
            raise TokenError(f"alias cycle: {cyc}")
        state[path] = "visiting"
        tok.value = sub(tok.raw, chain + [path])
        state[path] = "done"
        return tok.value

    def sub(raw, chain):
        if isinstance(raw, str):
            m = ALIAS.match(raw)
            if m:
                target = m.group(1)
                return copy.deepcopy(deref(target, chain))
            return raw
        if isinstance(raw, dict):
            return {k: sub(v, chain) for k, v in raw.items()}
        if isinstance(raw, list):
            return [sub(v, chain) for v in raw]
        return raw

    for p in tokens:
        deref(p, [p])

    # A whole-value alias must point at a token of the same type.
    for t in tokens.values():
        if t.alias_of and tokens[t.alias_of].type != t.type:
            raise TokenError(
                f"'{t.path}' ({t.type}) aliases '{t.alias_of}' ({tokens[t.alias_of].type}): type mismatch"
            )
    for t in tokens.values():
        try:
            validate(t.type, t.value)
        except (TokenError, colour.ColorError) as e:
            where = f" [{t.source}]" if t.source else ""
            raise TokenError(f"'{t.path}'{where}: {e}") from None
    return tokens


# ---------------------------------------------------------------- validation
def _dim(v, units):
    if not (isinstance(v, dict) and set(v) == {"value", "unit"}):
        raise TokenError(f"expected {{value, unit}}, got {v!r}")
    if not isinstance(v["value"], (int, float)):
        raise TokenError(f"value must be a number, got {v['value']!r}")
    if v["unit"] not in units:
        raise TokenError(f"unit must be one of {sorted(units)}, got {v['unit']!r}")


def validate(ttype: str, v) -> None:
    if ttype == "color":
        colour.dtcg_to_rgba(v)
    elif ttype == "dimension":
        _dim(v, {"px", "rem"})
    elif ttype == "duration":
        _dim(v, {"ms", "s"})
    elif ttype == "number":
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise TokenError(f"expected a number, got {v!r}")
    elif ttype == "fontFamily":
        ok = isinstance(v, str) or (isinstance(v, list) and v and all(isinstance(s, str) for s in v))
        if not ok:
            raise TokenError(f"fontFamily must be a string or a non-empty list of strings, got {v!r}")
    elif ttype == "fontWeight":
        if isinstance(v, (int, float)):
            if not 1 <= v <= 1000:
                raise TokenError(f"fontWeight must be within 1..1000, got {v}")
        elif v not in FONT_WEIGHT_WORDS:
            raise TokenError(f"unknown fontWeight keyword {v!r}")
    elif ttype == "cubicBezier":
        if not (isinstance(v, list) and len(v) == 4 and all(isinstance(n, (int, float)) for n in v)):
            raise TokenError(f"cubicBezier must be 4 numbers, got {v!r}")
        if not (0 <= v[0] <= 1 and 0 <= v[2] <= 1):
            raise TokenError("cubicBezier x values (P1x, P2x) must be within 0..1")
    elif ttype in COMPOSITE_KEYS:
        keys = COMPOSITE_KEYS[ttype]
        if keys is None:
            return
        if ttype == "shadow" and isinstance(v, list):
            for layer in v:
                validate("shadow", layer)
            return
        if not isinstance(v, dict):
            raise TokenError(f"{ttype} must be an object, got {v!r}")
        missing = keys - set(v) - ({"inset"} if ttype == "shadow" else set())
        if missing:
            raise TokenError(f"{ttype} is missing {sorted(missing)}")
    else:
        raise TokenError(f"unsupported $type {ttype!r}")


# ------------------------------------------------------------------- facade
def build_theme(root: Path, files: list[Path]) -> dict[str, Token]:
    tree, sources = load_layers(files, root)
    return resolve(flatten(tree, sources))
