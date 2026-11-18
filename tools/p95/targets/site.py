"""dist/site/: the docs and gallery site (docs/ + the web package under web/).

Serve it over HTTP (ES modules don't load from file://):
    python3 -m http.server -d dist/site 8095
"""
from __future__ import annotations

import shutil
from pathlib import Path

from .. import ROOT
from . import web


def build(ctx, out: Path) -> list[Path]:
    shutil.copytree(ROOT / "docs", out)
    web.build(ctx, out / "web")
    return [out / "index.html", out / "web"]
