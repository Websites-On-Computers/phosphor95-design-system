# Licenses

**This project's own license is not chosen yet.** Until one is added, the project's own code and docs are all rights reserved. The third-party material below keeps its own licenses.

## Third-party material in this repo

| Material | Path | License | Notes |
|---|---|---|---|
| PxPlus IBM VGA 8x14 / 8x16 / 9x8 / 9x16 (VileR, int10h.org "Ultimate Oldschool PC Font Pack") | `assets/fonts/PxPlus_*.ttf` | CC BY-SA 4.0 (`assets/fonts/licenses/int10h-CC-BY-SA-4.0.txt`) | Attribution required. Share-alike applies to modified fonts (e.g. subsets or woff2 conversions), not to work that only uses them |
| VT323 (Peter Hull) | `assets/fonts/VT323-Regular.ttf` | SIL OFL 1.1 (`assets/fonts/licenses/VT323-OFL.txt`) | |
| W95FA | `assets/fonts/W95F.otf` | SIL OFL 1.1 (`assets/fonts/licenses/W95FA-OFL.txt`) | |
| Chicago95 `avatar-default` (grassmunk et al.), recolored by Phosphor-95 | `brand/source/avatar-phosphor95-48.png` (master, the lock-screen image) and `avatar-phosphor95.svg`. Originals: `avatar-chicago95-original{,-48}.{svg,png}` | GPL-3.0+/MIT (Chicago95 project) | **Shipped as the Phosphor95 persona and logo.** Redistributed under GPL-3.0+; see [licenses/CHICAGO95.md](licenses/CHICAGO95.md) and [licenses/GPL-3.0.txt](licenses/GPL-3.0.txt). The same applies to the icon subset in `assets/icons/` |

## Our own source material

- `brand/source/palette-phosphor95.toml` and `system-phosphor95.toml`: snapshots of `../theme/config/`.
- `brand/imagery/*.png`: generated or rendered by the Phosphor-95 theme tooling (wallpaper, boot splash, POST screen).
