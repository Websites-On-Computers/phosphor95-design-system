#!/usr/bin/env python3
"""Phosphor95 design-system build.

    python3 tools/build.py              validate, contrast-check, build every target
    python3 tools/build.py css json     build only these targets
    python3 tools/build.py --check      validate + contrast-check only (CI / pre-commit)
    python3 tools/build.py --list       list targets

Exit status is non-zero on any token error or contrast failure.
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from p95 import DIST, ROOT, TokenError, load_context, run_checks  # noqa: E402
from p95.targets import TARGETS  # noqa: E402


def say(tag: str, msg: str) -> None:
    print(f"  [{tag:^4}] {msg}")


def main(argv: list[str]) -> int:
    if "--list" in argv:
        print("\n".join(TARGETS))
        return 0
    check_only = "--check" in argv
    wanted = [a for a in argv if not a.startswith("--")] or list(TARGETS)
    unknown = set(wanted) - set(TARGETS)
    if unknown:
        say("ERR", f"unknown target(s): {', '.join(sorted(unknown))}. choose from: {', '.join(TARGETS)}")
        return 2

    t0 = time.time()
    try:
        ctx = load_context()
    except TokenError as e:
        say("ERR", f"tokens: {e}")
        return 1
    n = len(ctx.default)
    say("OK", f"tokens     {n} per theme, themes: {', '.join(ctx.themes)} (default {ctx.default_theme})")

    failures = run_checks(ctx)
    if failures:
        for f in failures:
            say("ERR", f"contrast   {f}")
        return 1
    say("OK", "contrast   all checks pass")
    if check_only:
        return 0

    for name in wanted:
        t = time.time()
        out = DIST / name
        if out.exists():
            shutil.rmtree(out)
        files = TARGETS[name](ctx, out)
        where = sorted({str(f.parent.relative_to(ROOT)) for f in files})
        say("OK", f"{name:<10} {time.time() - t:4.2f}s  {len(files)} file(s) -> {', '.join(w + '/' for w in where)}")
    say("OK", f"done       {time.time() - t0:4.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
