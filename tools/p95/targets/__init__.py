"""Output targets. Each module exposes `build(ctx, out_dir) -> list[Path]`.

`json`, `css` and `report` (the contrast report in foundations/). Later phases add web (components, fonts), terminal
schemes and the Rust crate.
"""
from . import css, json_out, report, site, tui, web

TARGETS = {
    "json": json_out.build,
    "css": css.build,
    "report": report.build,
    "web": web.build,
    "site": site.build,
    "tui": tui.build,
}
