# Principles

Six rules decide every Phosphor95 design question. When two of them conflict, the lower number wins, with one exception: accessibility (see [accessibility.md](accessibility.md)) beats all of them.

---

## 1. Phosphor on void

**Light is information. Dark is the default, and brightness means importance.**

A green screen only lights the pixels that matter. The darkest ramp steps are surfaces, and brighter steps carry meaning. The brightest step, `text.hot`, is kept for what is live right now.

| | Do | Don't |
|---|---|---|
| Web | Put body text in `text.primary` on `surface.base` or `surface.face` | Use large areas of `fill.solid` as a background ("light mode") |
| Web | Rank information by brightness: `text.hot` > `text.primary` > `text.secondary` | Rank by hue or saturation |
| TUI | Leave the terminal's default background alone, or use `surface.base` | Paint full-screen bright backgrounds |
| TUI | Show the current row with reverse video | Highlight it with a second hue |

## 2. Structure from bevels, not shadows

**Depth comes from Win95 light and dark edges. No blur, no drop shadows, and the radius is always 0.**

Raised, sunken and pressed are drawn with the four `bevel.*` edges. Stacking order is a `layer.*` value, never a shadow. See [bevels-and-elevation.md](bevels-and-elevation.md).

| | Do | Don't |
|---|---|---|
| Web | Draw a raised button with `bevel.hi`/`bevel.light` on the top-left and `bevel.shadow`/`bevel.dark` on the bottom-right | Use `box-shadow` blur, `border-radius`, or gradients |
| Web | Lift a menu by giving it a raised bevel and `layer.menu` | Fake elevation with a lighter surface or a glow |
| TUI | Use `┌─┐` for panels and `╔═╗` for the focused or active window | Use rounded corners (`╭╮`) |

## 3. On the grid

**Everything snaps to the character cell (8×16). Pixel fonts render only at whole multiples of their native size.**

`space.*` steps are 4 px multiples. Layouts land on the 8 px cell width and the 16 px cell height wherever possible. Fonts render only at `font.size.*`. Images and the Operator scale by whole numbers, with nearest-neighbour sampling. See [space-and-grid.md](space-and-grid.md) and [typography.md](typography.md).

| | Do | Don't |
|---|---|---|
| Web | Set type at 16, 32 or 48 px | Use 13 px, 18 px, `1.1rem` or fluid `clamp()` sizes |
| Web | Scale the Operator to 96 or 192 px with `image-rendering: pixelated` | Use 100 px or smooth scaling |
| TUI | Round spacing to whole columns and rows | Rely on half-cell alignment |

## 4. Glow means hot

**Hover, focus, active and live states show up as more luminance.**

Interaction brightens things. It never changes their hue. Hovered and focused text moves up to `text.hot`, and the glow effect (`glow.base`, `glow.hot`) marks the one live thing on screen. When the pointer or focus leaves, the glow fades over `duration.decay`.

**Hover rule:** on hover, secondary text brightens to `text.primary`, or to `text.hot` if it is the item's label. `text.secondary` is never drawn on `surface.face-hover`, which is why the contrast gate doesn't check that pair.

| | Do | Don't |
|---|---|---|
| Web | Hovered menu item: invert to `select.bg`/`select.fg` | Recolor it in a new hue |
| Web | Focused field: dotted `focus.ring` in `border.focus` | Remove the outline, or use a soft blue glow |
| Web | Hovered list row: `surface.face-hover`, with its secondary text moved to `text.primary` | Leave dim text on the hover background |
| TUI | Selected item: reverse video. Focused pane: bright border | Underline or italics alone |

## 5. Monochrome first, color only for status

**Amber is a warning and red is an error. Each always comes with a text or glyph cue (`[WARN]`, `[ERR ]`).**

Everything that isn't a status uses one ramp, `color.phosphor.*`. Status colors (`status.ok|info|warn|error.*`) are the only other hues, and color is never the only signal. In the amber and white themes the status hues change (see [color.md](color.md)), so the cue matters even more there.

| | Do | Don't |
|---|---|---|
| Web | `[WARN] Disk 91% full` in `status.warn.fg` | Show an amber dot with no label |
| Web | An error field: `field.invalid-border` plus an `[ERR ]` message below | A red border alone |
| TUI | `[ OK ] network up` | Show a green line and expect "green = good" |

## 6. Effects are garnish

**CRT, scanlines and rain are opt-in and cheap, and they turn off under `prefers-reduced-motion`. Content stays readable with effects off.**

Design and test with every effect off first. Effects layer on top (`layer.overlay`), never behind body text, and stay within the 2015 MacBook Air's budget. See [effects.md](effects.md).

| | Do | Don't |
|---|---|---|
| Web | Ship `.p95-crt` as an opt-in class, with scanlines at `effect.scanline-opacity` | Turn scanlines on by default over forms |
| Web | Put digital rain behind a splash screen | Put rain behind a paragraph or a table |
| TUI | Make the gallery's rain a toggle that is off when `NO_COLOR` or a dumb terminal is detected | Animate the background of a log view |
