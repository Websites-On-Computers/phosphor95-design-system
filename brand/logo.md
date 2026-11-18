# Logo

Every file in `logo/` is generated from the two avatar masters in `source/` by `python3 tools/brand.py`.
Don't edit the outputs; change the tokens or the masters and regenerate.

| Asset | Files | Use |
|---|---|---|
| **Mark**: the Operator in a sunken bevel well, 64×64 | `mark.svg` (themeable), `mark-<theme>.png` @1x/2x/4x | App icon, avatar slot, social image |
| **Operator**: bare, transparent | `operator.svg` (themeable), `operator-<theme>.svg`, `operator-<theme>.png` @1x/2x/4x/8x | Splash, empty states, about screens |
| **Wordmark**: `PHOSPHOR95▮` in PxPlus IBM VGA 8x16, 1-bit, block cursor | `wordmark.svg` (themeable), `wordmark-<theme>.png` @1x–4x | Headers, docs, title screens |
| **Lockup**: mark + wordmark @2x + `DESIGN SYSTEM` | `lockup-<theme>.png` @1x/2x | Docs site header, README, slides |
| **Favicons / app icons** (green) | `favicon.ico` (16/32/48), `favicon-16.png`, `favicon-32.png`, `icon-180.png` (Apple touch), `icon-192.png`, `icon-512.png` | Web |
| **Terminal** | `operator-<theme>.ansi` (truecolor half-blocks, 20 rows), `operator-small.ansi` (16px sprite), `operator.txt` (pure ASCII), `wordmark.txt` (mono half-blocks) | fastfetch logo, MOTD, `--version` banners |

`<theme>` is `green`, `amber`, `white` or `hc`. `_sheet.png` is a contact sheet for checking the set,
not a deliverable.

## Themeable SVGs

`mark.svg`, `operator.svg` and `wordmark.svg` fill with `var(--p95-…, <green fallback>)`, so when inlined
in a page they recolour with `data-theme`. As `<img>` sources they render green; use the per-theme SVG
or PNG in that case.

```html
<link rel="stylesheet" href="tokens.css">
<div data-theme="amber"><!-- inline operator.svg here: it renders amber --></div>
```

Always set `image-rendering: pixelated` on raster logos scaled in CSS. SVGs use
`shape-rendering="crispEdges"` and are built from 1px rectangles, so they stay sharp at any size.

## Rules

- **Clear space:** one cell (8px at 1x) on every side of the mark; two cells around the lockup.
- **Minimum size:** mark 32px (below that, use `favicon-16.png`); wordmark 1x (16px tall).
- **Scale by whole multiples only.** If a layout needs 100px, use 96px.
- **Backgrounds:** `surface.base` or `surface.face`. On anything else, use the mark (it brings its own well).
- **Don't:** recolour by hand, add glow or outlines, set the wordmark in another font, separate the
  cursor from the wordmark, stretch, rotate, or put it on photos.
- **The cursor** is part of the wordmark. On the web it may blink (`duration.blink`, steps), and it's
  static under reduced motion.

## Why PxPlus, not VT323, for the wordmark

VT323 is traced outlines on an uneven grid (stems alternate between 2 and 3 design pixels), so it
can't be rendered pixel-exact or turned into a crisp vector. PxPlus IBM VGA 8x16 is a true bitmap
font, and it's already the UI, boot and terminal face. VT323 stays the display face for large web
headings (`type.heading-*`), where antialiasing is acceptable.
