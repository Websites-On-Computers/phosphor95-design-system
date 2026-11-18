# Color

Color comes in three tiers. Use the highest tier that fits:

1. **Component** (`button.face`, `list.row-selected-bg`, and so on): when you're building that component.
2. **Semantic** (`text.secondary`, `surface.face`, `status.warn.fg`, and so on): for everything else.
3. **Primitive** (`color.green.8`, `color.amber.10`, and so on): inside `tokens/` only. App code never uses primitives directly. `color.source.*` is a verbatim import of the GNOME theme's palette, kept for provenance only.

**Token names on each platform.** A dotted path becomes a CSS custom property with a `--p95-` prefix: `text.secondary` → `--p95-text-secondary`. Semantic tokens point at other tokens, so devtools show the chain: `--p95-text-secondary: var(--p95-color-phosphor-8)`. The Rust crate (`p95-style`) uses the same paths as fields: `theme.text.secondary`.

Every pair below is contrast-checked at build time. The measured numbers are in **[contrast.generated.md](contrast.generated.md)**.

---

## The 12-step ramp

Every hue is a ramp of 12 steps, ordered from darkest to brightest. **Each step has a fixed job, and that job is the same in every ramp.** The green ramp is the Phosphor-95 palette itself: its 12 colors, sorted by lightness.

| Step | Job | Green | From `palette.toml` |
|---|---|---|---|
| 1 | App background, text fields, terminal background | `#020a04` | `core.base` |
| 2 | Bevel shadow, sunken wells | `#041208` | `core.shadow` |
| 3 | Face: windows, panels, buttons | `#0a2412` | `core.face` |
| 4 | Face hover | `#0e3018` | `core.face_hover` |
| 5 | Subtle selected / inactive title bar | `#0b4419` | `title.inactive_bg` |
| 6 | Faint: disabled text, hairlines (decorative, below 3:1) | `#0f5a24` | `text.fg_faint` |
| 7 | Border, bevel light | `#1c7a36` | `core.bevel_light` |
| 8 | Dim: secondary text, hints, placeholders | `#1fa046` | `text.fg_dim` |
| 9 | Solid: bevel highlight, strong border, status borders | `#2fbf55` | `core.bevel_hi` |
| 10 | Phosphor: primary text, solid fills, selection | `#33ff66` | `text.fg` |
| 11 | Bright: info, links, hover text | `#7dffa8` | `status.info` |
| 12 | Glow: hot text, focus, cursor | `#b6ffc8` | `text.glow` |

Ramps: `color.green.*` (P1 phosphor), `color.amber.*` (P3), `color.white.*` (P4), `color.red.*` (errors) and `color.blue.*` (a cool accent for white-theme info and ANSI blue/cyan; never a UI ramp). `color.void` is true black, `#000000`.

### How the other ramps are derived

`tools/gen_ramps.py` builds amber, white, red and blue from green. Ramp steps are never hand-picked (the ANSI sets are hand-mapped onto ramp steps; see below).

1. **Lightness-matched.** Each step keeps green's OKLCH lightness for that step, in the new hue. Chroma is scaled by the ratio between a source color and green's step of similar lightness.
2. **Anchors.** Some steps are pinned to existing theme colors exactly: `color.amber.10` = `#ffb000` (the theme's warn), and `color.red.9` = `#ff3b3b` (the theme's error, whose lightness falls at step 9). White has no anchor; its hue comes from `#e0e8f0`.
3. **Contrast floors.** Each derived step is lightened, in small increments, until it clears its floor against step 3 (the face). The floors are: step 7 ≥ 3.05:1, step 8 ≥ 4.6:1, step 10 ≥ 7:1. Anchored steps are never moved; the gate checks them instead.
4. **Monotonic.** The script fails if any ramp stops increasing in lightness.

To change a ramp, edit `GREEN`, `RAMPS` or `FLOORS` in the script and re-run it. Never edit `color-ramps.json` by hand.

### `color.phosphor.*`: the theme ramp

Semantic tokens never name a hue. They point at `color.phosphor.1`–`12`, an abstract ramp that each theme maps onto a real one: `color.phosphor.N → color.green.N` in the green theme, `→ color.amber.N` in amber, and so on. Swapping the theme swaps the whole ramp, and because the step jobs match, every role still works.

---

## Semantic roles

### `surface.*`: backgrounds

| Token | Step | Use for |
|---|---|---|
| `surface.void` | void | Behind everything: desktop edges, the CRT-off frame |
| `surface.base` | 1 | Page and app background, text fields, list and table bodies, terminal background |
| `surface.sunken` | 2 | Wells, tracks, zebra rows |
| `surface.face` | 3 | Windows, panels, buttons, menus, dialogs |
| `surface.face-hover` | 4 | Hovered face (button, list row). Text on it moves to `text.primary` |
| `surface.face-pressed` | 2 | A pressed button face, with its bevel inverted |
| `surface.selected-subtle` | 5 | Selection in an unfocused list, the inactive title bar |
| `surface.overlay` | black at 72% | The scrim behind modal dialogs |

### `text.*`: foreground

| Token | Step | Use for |
|---|---|---|
| `text.primary` | 10 | Body text, labels, values. This is the default |
| `text.secondary` | 8 | Secondary text, hints, placeholders, captions. Meets 4.5:1 on `surface.base` and `surface.face` |
| `text.disabled` | 6 | **Disabled controls only.** It is below 3:1 on purpose, as WCAG allows for inactive controls. Never use it for hints |
| `text.hot` | 12 | Hover and focus text, headings that should glow, the cursor |
| `text.link` | 11 | Links |
| `text.inverse` | void | Text on solid phosphor: selection, the active title bar, `fill.solid` |

### `bevel.*`: the four edges

`bevel.hi` (9), `bevel.light` (7), `bevel.shadow` (2), `bevel.dark` (void). Which edge goes where is set out in [bevels-and-elevation.md](bevels-and-elevation.md).

### `border.*`: lines

| Token | Step | Use for |
|---|---|---|
| `border.subtle` | 6 | Decorative rules and separators. Not checked for contrast, so never use it for a boundary that matters |
| `border.default` | 7 | Control and panel boundaries (≥ 3:1 on face) |
| `border.strong` | 9 | Default-button frame, active window frame, table header rule |
| `border.focus` | 12 | The focus ring; see `focus.ring` |

`focus.ring` is a composite border: `border.focus`, `border.width.hair`, `dotted`. It is the Win95 dotted rectangle, drawn in hot phosphor.

### `select.*`, `title.*`, `fill.*`, `glow.*`

| Token | Use for |
|---|---|
| `select.bg` / `select.fg` | Inverted selection (step 10 on void), as on a real terminal |
| `select.inactive-bg` / `select.inactive-fg` | Selection when the list doesn't have focus (step 5 with step-10 text) |
| `title.active.bg` / `.fg` | Focused window title bar: solid phosphor, void text |
| `title.inactive.bg` / `.fg` | Unfocused title bar: `surface.selected-subtle`, step-8 text (≥ 3:1, UI label) |
| `fill.solid` / `fill.track` | Progress, meters, toggles that are on, the primary button / the empty track behind them |
| `glow.base` / `glow.hot` | Halo color for text glow. The alpha comes from `effect.glow-strength`; see [effects.md](effects.md) |

### `status.*`: the only extra hues

Each status has `fg`, `bg` (a tinted surface, step 3 of its hue) and `border` (step 9 of its hue). Use `fg` for text and icons, `bg` for a toast or banner fill, and `border` for the frame around it.

| Status | Prefix | green | amber | white | hc |
|---|---|---|---|---|---|
| `status.ok.*` | `[ OK ]` | green | amber | **real green** | green |
| `status.info.*` | `[INFO]` | green.11 | amber.11 | **blue.10** | green.11 |
| `status.warn.*` | `[WARN]` | amber | **white** | amber | amber |
| `status.error.*` | `[ERR ]` | red | red | red | red |

**Redundancy rule:** a status is never shown by color alone. Always pair `status.*.fg` with its prefix or a glyph from [iconography.md](iconography.md). In the amber theme, ok and info are the text hue, so there the prefix is the signal. (The white theme uses the `color.blue` ramp for info to stay distinct.)

### `ansi.*`: the terminal's 16 colors

Each theme defines all 16 (`ansi.black` … `ansi.bright-white`) for terminal color schemes and TUI apps. They come from `color.ansi.<theme>.*`, generated by `gen_ramps.py`.

| Name | green | amber | white | hc |
|---|---|---|---|---|
| black | `#020a04` | `#0b0702` | `#070708` | `#000000` |
| red | `#ff3b3b` | `#ff3b3b` | `#ff3b3b` | `#ff3b3b` |
| green | `#33ff66` | `#ffb000` | `#33ff66` | `#33ff66` |
| yellow | `#ffb000` | `#cfd7df` | `#ffb000` | `#ffb000` |
| blue | `#1fa046` | `#af7d29` | `#578bbb` | `#6aa7de` |
| magenta | `#7dffa8` | `#ffc6bf` | `#ffc6bf` | `#7dffa8` |
| cyan | `#5dffb0` | `#b5dbff` | `#b5dbff` | `#5dffb0` |
| white | `#a8ffbf` | `#ffe7c4` | `#cfd7df` | `#a8ffbf` |
| bright-black | `#0f5a24` | `#624412` | `#484b4e` | `#1fa046` |
| bright-red | `#ff7a6b` | `#ff7a6b` | `#ff7a6b` | `#ff7a6b` |
| bright-green | `#66ff8c` | `#ffd9a2` | `#66ff8c` | `#66ff8c` |
| bright-yellow | `#ffd060` | `#e7ebee` | `#ffd060` | `#ffd060` |
| bright-blue | `#2fbf55` | `#ce9533` | `#6aa7de` | `#2fbf55` |
| bright-magenta | `#b6ffc8` | `#ffd4ce` | `#ffd4ce` | `#b6ffc8` |
| bright-cyan | `#9dffd0` | `#c6e3ff` | `#c6e3ff` | `#9dffd0` |
| bright-white | `#e6ffec` | `#fff6e9` | `#e7ebee` | `#e6ffec` |

How the sets are built:
- **green** is `palette.toml` verbatim.
- **amber and white** are hand-mapped onto ramp steps so all 16 slots stay distinct (a plain hue shift made cyan, magenta and white indistinguishable).
  - Amber: yellow becomes white (amber *is* yellow there), blue/cyan come from `color.blue`, magenta from the pale red steps. ANSI green is `color.amber.10`, the main text color.
  - White: keeps real green and yellow so diffs and success output stay legible; blue/cyan come from `color.blue`.
- **hc** is green with true black, `bright-black` raised to step 8 so dim terminal text stays readable, and blue moved to `color.blue.9` to keep all 16 distinct.
- A test asserts no theme repeats a colour across its 16 slots.

`ansi.bright-black` is faint (step 6) in green, amber and white. That's deliberate for shell autosuggestions; don't use it for content.

---

## Themes

Themes change only the semantic tier. Component tokens follow automatically. On the web, set `data-theme="green|amber|white|hc"` on any element; the default is green.

| Theme | Ramp | What else changes |
|---|---|---|
| `green` | `color.green` | Nothing. This is the Phosphor-95 desktop exactly |
| `amber` | `color.amber` | `status.warn` moves to white (amber is the text color). `ok` and `info` use the amber ramp. The Operator uses `color.avatar.amber.*` |
| `white` | `color.white` | Monochrome. Real green, amber and red are kept for ok, warn and error. The Operator uses `color.avatar.white.*` |
| `hc` | `color.green` | `surface.base`, `surface.sunken` and `surface.face` are all true black. `text.secondary` = step 10, and `text.disabled` = step 8 (readable; disabled is also shown by a dashed border). All four bevel edges are step 10 (flat solid frames). Borders run 8/10/12. Status backgrounds are void |
