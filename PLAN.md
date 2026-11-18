# Phosphor95 Design System: Plan

**Status:** approved 2026-11-04. Phase 0 done (scaffold, generator, seed tokens, 19 tests). Renamed from "TERMINAL-01 Design System" to **Phosphor95** (prefix `p95-`). Phase 1 done (§10). Phase 2 done (§11). Phase 3 done (§12). **Phase 4 skipped** (decided 2026-11-04): the GNOME theme and terminal01 stay as they are
**Sources:** `../theme` (Phosphor-95 GNOME theme) and `../terminal01` (voice and face app)
**Goal:** one design system, extracted from Phosphor-95, that works on the web and in terminals, with your profile avatar as its persona and logo.

---

## 1. What we're starting from

The Phosphor-95 theme already holds most of a design system. It just isn't packaged for reuse.

| Asset | Where | Reuse |
|---|---|---|
| Palette (single source of truth) | `theme/config/palette.toml` | Seeds the color tokens. 25 roles plus a 16-color ANSI set |
| Identity | `theme/config/system.toml` | Name `TERMINAL-01`, tagline `PHOSPHOR-95 // LOCAL INTELLIGENCE NODE`, BIOS string |
| Fonts | `~/.local/share/fonts/phosphor95/` | PxPlus IBM VGA 8x16 / 9x16 (UI and mono), VT323 (display), W95FA (alternate UI) |
| **Profile avatar** (the lock-screen image) | `~/.local/share/icons/Phosphor95/status/48/avatar-default.png`. GNOME Shell's lock screen asks for `avatar-default-symbolic` (no `~/.face` is set), which is a symlink to this file, drawn at 100 px. An SVG of the same drawing is in `status/scalable/` | Dithered 48×48 pixel-art head in profile, in phosphor green. **This becomes the persona and logo.** Master: `brand/source/avatar-phosphor95-48.png` |
| Icons | Chicago95, recolored by luminance (`theme/tools/components/icons.py`) | A curated subset for web and docs |
| Imagery | wallpaper (digital rain), boot logo, POST screen, GRUB, lock screen | Brand imagery and texture library |
| Component language | GTK and Shell CSS templates | Win95 bevels in green, inverted selection, bright title bars, block progress bars |
| Terminal language | starship (ASCII only), fastfetch, btop, the `[ OK ]` boot lines, CRT shader | The TUI foundations |
| The face | `terminal01/crates/t01-face` | A glyph-cloud head with HUD rings, the animated counterpart to the avatar |

**Contrast audit of the current palette** (WCAG 2.x):

| Pair | Ratio | Result |
|---|---|---|
| fg `#33ff66` on base / face | 14.9 / 12.3 | AAA |
| fg_dim on base / face | 5.9 / 4.9 | AA |
| fg_dim on title-inactive `#0b4419` | 3.3 | UI and large text only |
| error `#ff3b3b` on face | 4.7 | AA |
| warn, info, glow on face | 9–14 | AAA |
| **fg_faint `#0f5a24` on base / face** | **2.4 / 2.0** | **Fails.** OK for disabled controls (WCAG exempts them), never for hints or placeholders |

→ The tokens add a `text.subtle` step at about 4.5:1 for hints and placeholders, and keep `fg_faint` for disabled states only.

---

## 2. Quick research: what to borrow

| System | What we take from it |
|---|---|
| **W3C DTCG format 2025.10** (first stable spec, Oct 2025) | The token file format: `$value`, `$type`, aliases, plus the Color and Resolver modules for themes. Tool-neutral and future-proof |
| **Style Dictionary v5 / Terrazzo** | The reference DTCG pipelines. Their pattern: primitive → semantic → component builds, emitting one output per platform. We copy the architecture; the tooling choice is in section 6 |
| **Material 3** | Three token tiers (reference → system → component) and **state layers** (hover, pressed and focus as defined overlays). Our version of a state layer is *glow intensity* |
| **IBM Carbon** | Themes swap only the semantic tier. Accessibility docs written per component. Its well-known 2x grid |
| **GitHub Primer** | Primitives vs functional tokens, named by role (`fg.muted`, `canvas.inset`) and never by hue. Also has a CLI-adjacent heritage |
| **Radix Colors** | A 12-step scale per hue where each step has a defined job (bg, hover bg, border, solid, text). We build our green ramp this way |
| **Shopify Polaris** | Content and voice guidelines as a first-class part of the system. Our voice is a "machine voice" |
| **98.css / XP.css** | The nearest web relative: semantic HTML styled as a retro OS, mostly classless, no JS required |
| **WebTUI** | Terminal look on the web. Uses CSS `@layer` for clean overrides, and attribute-driven markup on ordinary elements |
| **Charm (Lip Gloss, Gum, Bubble Tea)** | TUI conventions: adaptive color (truecolor → 256 → 16), border styles as data, key-hint footers |
| **Ratatui theming crates** (themekit, opaline) | Palette → semantic → **widget style bundles**, honoring `NO_COLOR`, as a Rust crate. This is the shape of our TUI package |

---

## 3. Architecture

```
                 ┌──────────────────────────────────────────────┐
  BASE           │ tokens/ (DTCG JSON)  brand/  foundations/     │
  (platform-     │ primitive → semantic → component              │
   agnostic)     │ + principles, voice, persona, component specs │
                 └───────────────┬──────────────────────────────┘
                                 │  build (one generator, many formats)
            ┌────────────────────┼──────────────────────────┐
            ▼                    ▼                          ▼
  WEB                      TUI                        FEEDS BACK INTO
  css (vars, base,         terminal color schemes     theme/config/palette.toml
  components, effects)     Rust crate (ratatui)       terminal01 face colors
  web components           CLI/TUI guidelines         (phase 4: skipped)
  fonts, icons, docs site  gallery demo app
```

### Token tiers

1. **Primitive.** Raw values with no meaning: `green.1…12`, `amber.*`, `red.*`, `void`, font families, the pixel grid, durations.
2. **Semantic.** Roles, and the only tier that themes override:
   - `surface.{void, base, face, face-hover, raised, sunken, overlay}`
   - `text.{primary, secondary, subtle, disabled, hot, inverse}`
   - `bevel.{hi, light, shadow, dark}`
   - `border.{default, strong, focus}`
   - `select.{bg, fg}`
   - `title.{active, inactive}.{bg, fg}`
   - `status.{ok, info, warn, error}.{fg, bg}`
   - `focus.ring`
   - `glow.{none, low, high}`
3. **Component.** For example `button.face`, `window.titlebar.active.bg`, `progress.fill`, `table.row.selected.bg`.

### Themes (semantic overrides)

- **`phosphor-green`** is the default: P1 phosphor, exactly today's theme.
- **`phosphor-amber`** is the amber-monitor variant (P3). `warn` already uses this hue.
- **`phosphor-white`** is a P4 white/grey monitor variant.
- **`high-contrast`** is pure `#000` / `#33ff66` with no dim or faint steps, for accessibility.
- *(Not proposed: a light "paper" mode. It fights the concept. It's easy to add later as a print stylesheet.)*

---

## 4. Base design system (platform-agnostic)

### 4.1 Principles
1. **Phosphor on void.** Light is information. Dark is the default, and brightness means importance.
2. **Structure from bevels, not shadows.** Depth comes from Win95 light and dark edges. No blur or drop shadows, and radius is always 0.
3. **On the grid.** Everything snaps to the character cell (8×16). Pixel fonts render only at whole multiples of their native size.
4. **Glow means hot.** Hover, focus, active and live state show as increased luminance (`text.hot`, glow).
5. **Monochrome first, color only for status.** Amber is a warning and red is an error, and each always comes with a text or glyph cue (`[WARN]`, `[ERR]`).
6. **Effects are garnish.** CRT, scanlines and rain are opt-in, cheap, and off under `prefers-reduced-motion`. Content stays readable with effects off.

### 4.2 Brand
- **Persona: the Operator.** The profile avatar is the face of Phosphor95, and of TERMINAL-01, the machine that runs it. It's the still, pixel counterpart of the terminal01 glyph-cloud head. Documented with personality traits, how it speaks, and where it appears (logo, empty states, loading, errors, about screens).
- **Logo set:**
  - avatar mark (bevel-framed square)
  - wordmark `PHOSPHOR95▮` in VT323 with a block cursor. `TERMINAL-01` stays the machine name in product lockups
  - lockup with the tagline
  - favicon and app icons (16/32/48/180/512)
  - ASCII and ANSI-block versions for terminals and fastfetch
  - mono 1-bit version
- **Imagery:** digital rain, scanline and dither textures, boot/POST compositions, the glyph-head face. Includes usage rules on density, where to put rain, and keeping it out from behind text.
- **Voice and tone:** a terse machine voice. Uppercase for system and status lines, sentence case for help text. Status prefixes `[ OK ]` `[INFO]` `[WARN]` `[ERR ]`, `//` as the separator, and no exclamation marks. Before/after examples for errors, empty states and confirmations.

### 4.3 Foundations
| Foundation | Contents |
|---|---|
| Color | 12-step ramps per hue, semantic roles, themes, contrast table, ANSI-16 mapping |
| Typography | Families (UI, mono, display) with fallbacks. Pixel-perfect size steps (16/32/48 px). Line height = one cell. Uppercase rules |
| Space and grid | 4 px base unit. The cell (8×16) as the macro unit. Spacing scale `0, 2, 4, 8, 12, 16, 24, 32, 48` |
| Bevels and borders | The 4-edge bevel recipe (raised, sunken, field, window, pressed), 1 px and 2 px. Maps to box-drawing characters in TUI |
| Elevation | Done with bevels and an inverted title bar, not shadows. Defines z-layers: base, raised, menu, dialog, toast, overlay |
| Motion | `steps()` timing (no smooth easing). Cursor blink 530 ms. Phosphor decay (a short glow fade). Typing-reveal. Reduced-motion rules |
| Effects | Glow, scanlines, CRT curvature and vignette, rain. Each one has a cost budget and an on/off token |
| Iconography | Curated Chicago95-recolored set, 16/32 px, pixel-snapped. A glyph icon set for TUI (ASCII-safe first, Nerd Font optional) |
| Accessibility | Contrast minimums, focus visibility (dashed glow ring), status redundancy, no flashing above 3 Hz, keyboard-first |

### 4.4 Component catalog (spec once, implement per platform)
Each spec covers anatomy, tokens, states (default, hover, pressed, focus, selected, disabled), keyboard behavior, a11y notes and content rules, plus a **Web** and a **TUI** rendering column.

- **Actions:** button (default, primary, flat), icon button, toggle, link
- **Inputs:** text field, textarea, select/dropdown, checkbox, radio, switch, slider, spin box, search, command prompt (`> _`)
- **Containers:** window (title bar plus controls), panel, group box (fieldset), tabs, accordion, split pane, card (Win95 "frame")
- **Navigation:** menubar, menu, context menu, taskbar/status bar, breadcrumbs (path bar), command palette, key-hint bar
- **Data:** list, table (zebra, selected-inverted), tree, key-value list, log viewer, code block, diff
- **Feedback:** progress (block chars `█▓▒░`), meter, spinner, toast/notification, dialog/alert, tooltip, badge/status tag, boot-line (`[ OK ] message`), empty state (with the Operator)
- **Identity:** avatar, wordmark, splash/boot screen

---

## 5. Platform layers

### 5.1 Web: `packages/web`
- **CSS first, framework-agnostic.** CSS custom properties generated from tokens, organized with `@layer reset, tokens, base, components, utilities, effects`.
  - `base.css`: classless styling for semantic HTML (`button`, `input`, `fieldset`, `table`, `dialog`, `progress`), like 98.css.
  - `components.css`: classes `.p95-window`, `.p95-titlebar`, etc., with data attributes for variants (`data-variant="primary"`).
  - `effects.css`: opt-in `.p95-crt`, `.p95-scanlines`, `.p95-glow`. Respects reduced motion.
  - Themes switch with `data-theme="amber"` on any element.
- **Vanilla Web Components** for the few pieces that need JavaScript, so they work in React, Svelte or plain HTML: `<p95-rain>` (canvas digital rain), `<p95-wordmark>`, `<p95-menu>`, `<p95-tabs>`, `<p95-dialog>`, `<p95-prompt>` (command prompt), `<p95-palette>` (command palette), `<p95-toast>` (notification stack) (wraps native `<dialog>`), `<p95-boot>` (typed POST sequence), `<p95-operator>` (avatar with states: idle, thinking, speaking).
- **Assets:** self-hosted woff2 fonts with licenses, an SVG icon sprite, the logo set, favicons.
- **Docs and gallery site:** a static site built with the system itself, with live components, token tables and copyable snippets. Screenshot-verified with headless Firefox.
- *Later, if wanted:* React wrappers and a Tailwind preset generated from the same tokens.

### 5.2 TUI: `packages/tui`
- **Terminal color schemes** generated for Ghostty (the current terminal), Kitty, Alacritty, WezTerm, foot, Windows Terminal and iTerm2, plus an `LS_COLORS`/`dircolors` file and a base16 YAML.
- **Color capability ladder:** truecolor → 256 (nearest xterm index, precomputed) → ANSI-16 (the palette's ANSI map) → `NO_COLOR`/mono (bold and reverse only). The design must still work in mono.
- **TUI foundations:**
  - box-drawing bevel recipes: `┌─┐` panel, `╔═╗` focused/active window, half-blocks `▀▄` for raised edges, `░▒▓` dither shading
  - title bars as inverted rows
  - selection as reverse video
  - key-hint footer (`F1 Help  ^Q Quit`)
  - status line format
  - ASCII-safe fallbacks for every glyph, matching the starship ASCII-only decision
- **Rust crate `p95-style`** for **ratatui**. Your apps are Rust, and terminal01 can use it. It contains:
  - a generated `Palette`
  - `Theme` with semantic `Style`s
  - widget style bundles (block, table, list, tabs, gauge)
  - bevel border sets
  - spinner and progress glyph sets
  - capability detection, plus the env switches the docs specify: `NO_COLOR`, `P95_REDUCED_MOTION=1`, `P95_NERD_FONT=1`
  - a `p95-gallery` example app that shows every TUI component
- **CLI guidelines:** help-text layout, `[ OK ]` log-line format, error format (what / why / fix), prompts, progress, exit codes, and ASCII art banners (the Operator in ANSI blocks).
- *Optional:* Go (Lip Gloss) and Python (Textual/Rich) theme packages. Both are cheap to generate from tokens later, but Go isn't installed today.

---

## 6. Tooling decision

**Recommendation: a small Python generator (`tools/build.py`, stdlib only) that reads DTCG 2025.10 JSON.** We still write tokens in strict DTCG format, so Style Dictionary or Terrazzo can replace the generator later without touching the tokens.

Why not Style Dictionary now: it needs Node ≥ 22, and Node isn't installed. Your theme repo already uses a Python stdlib generator (`p95.py`), so this matches it. Most of our outputs are custom anyway (Ghostty, Rust, ANSI ladders), and Style Dictionary would need custom formats for those too.

The generator also:
- runs a **contrast check** and fails the build on a regression
- computes 256-color fallbacks
- writes a `tokens.json` for any other consumer

---

## 7. Repo layout

```
terminal01-design-system/
├── PLAN.md  README.md  LICENSES.md
├── tokens/                  # DTCG source of truth
│   ├── primitive/           color.json type.json space.json motion.json
│   ├── semantic/            base.json + themes/{green,amber,white,hc}.json
│   └── component/           button.json window.json …
├── brand/                   persona.md voice.md + logo/ (svg, png, ascii, ansi) imagery/
├── foundations/             color.md type.md space.md bevel.md motion.md effects.md a11y.md icons.md
├── components/              one spec per component (.md)
├── assets/                  fonts/ (+licenses) icons/ (curated)
├── tools/                   build.py, contrast.py, rasterize helpers (PIL)
├── packages/
│   ├── web/                 css/ components/ (web components) assets/
│   └── tui/
│       ├── terminal-themes/ ghostty kitty alacritty wezterm foot …
│       └── p95-style/       Rust crate + examples/gallery.rs
├── docs/                    static docs/gallery site
└── dist/                    generated (git-ignored)
```

---

## 8. Phases

| # | Phase | Deliverable | Verified by |
|---|---|---|---|
| 0 | Scaffold | `git init`, layout, generator skeleton, fonts and avatar copied in with licenses | `tools/build.py` runs |
| 1 | Base | Tokens (3 tiers, 4 themes) from `palette.toml`, brand kit (logo set from the avatar, wordmark, favicon, ASCII/ANSI logo), principles, voice, foundations docs, component specs | Contrast check passes. Rendered logo sheet PNG |
| 2 | Web | CSS package, effects, web components, docs/gallery site | Headless-Firefox screenshots of every component, in every theme |
| 3 | TUI | Terminal schemes, `p95-style` crate, gallery example, CLI guidelines | `cargo test`, screenshot of the gallery in Ghostty, mono/16-color fallback check |
| 4 | ~~Integration~~ **skipped** | — | — |

---

## 9. Decisions (approved 2026-11-04)

| # | Decision |
|---|---|
| 1 | Name: **Phosphor95**, the design system and the parent brand of the Phosphor-95 GNOME theme. Prefix `p95-` (CSS `--p95-*`, elements `<p95-…>`, crate `p95-style`, npm `@phosphor95/web`). TERMINAL-01 is the machine and persona name *(renamed 2026-11-04)* |
| 2 | Avatar: **the Phosphor recolor of Chicago95's avatar, exactly as the lock screen shows it** (`brand/source/avatar-phosphor95-48.png`), is the persona and logo. No redraw. It ships with Chicago95 attribution (GPL-3.0+/MIT). The icon subset also ships with Chicago95's license *(changed 2026-11-04)* |
| 3 | TUI: **Rust/ratatui only** for v1. Go and Python later, generated from the same tokens |
| 4 | Web: **CSS plus vanilla Web Components**. React wrappers later if needed |
| 5 | Themes: **all four** (green, amber, white, high-contrast) in v1 |
| 6 | Phase 4: **skipped**. The design system does not edit `../theme` or `../terminal01`; they keep their own palettes *(decided 2026-11-04)* |

---

## 10. Phase 1 results (2026-11-04)

**Delivered:**
- **Tokens:** 455 per theme, in 4 themes, across all three tiers. The contrast gate has 57 checks per theme and all pass ([foundations/contrast.generated.md](foundations/contrast.generated.md)). There are 28 unit tests.
- **Ramps:** green is the palette verbatim. Amber, white, red and a blue accent are derived with lightness matching and contrast floors (`tools/gen_ramps.py`). The ANSI-16 sets are hand-mapped so no theme repeats a color.
- **Brand:**
  - the Operator, from the lock-screen avatar, pixel-exact in green and recolored per theme
  - mark, wordmark, lockup, favicons and app icons
  - themeable SVGs
  - ANSI and ASCII art
  - all generated by `tools/brand.py`
  - docs: persona, voice, logo and imagery
- **Foundations:** 9 docs plus an index.
- **Components:** 49 components across 7 category files plus an index. Every token reference in the docs resolves.

**Decisions made during phase 1:**
- **Wordmark font:** PxPlus IBM VGA 8x16. VT323 isn't pixel-exact (its stems alternate between 2 and 3 design pixels), so it can't produce a crisp vector. VT323 stays the display face for web headings.
- **Hover:** secondary text brightens to primary on hover. The pair secondary-on-hover is never drawn, so it isn't gated.
- **Status borders** use step 9, because step 7 missed 3:1 for red.
- **White theme info** uses `color.blue`, because the white ramp's info color was too close to its text color.
- **Avatar colors** are their own primitives (`color.avatar.*`), so the green Operator stays exactly the lock-screen image.
- **Component specs** are grouped by category (7 files), not one file per component.
- **Themes set `color.phosphor.*`.** The CSS target re-declares every token whose resolved value changes, so `data-theme` works on any subtree.

**Carried into later phases:**
- CRT curvature is terminal-shader only: there's no web token.
- The TUI env switches are specified in the docs but implemented in phase 3.
- The project license is still unchosen (LICENSES.md).

## 11. Phase 2 results (2026-11-04)

- **`@phosphor95/web`** (`packages/web`, built to `dist/web`):
  - CSS in six cascade layers: classless base, `.p95-*` components for all 49 specs, utilities, and opt-in effects
  - 11 light-DOM Web Components plus `enhance()` behaviors
  - fonts, brand assets, and 22 recolored Chicago95 icons
- **Gallery** (`docs/`, built to `dist/site`): every component, with a theme switcher, CRT toggle and command palette.
  - Verified with headless-Firefox screenshots in all four themes and at 390 px (`tools/shoot.sh`).
  - The `?selftest` in-page test passes **17/17**: elements, subtree theming, recipes, Operator recolor, dialog, menu, tabs, palette, toast, prompt, boot, switch, listbox, font, no errors.
- **Bugs found and fixed while verifying:**
  - closed dialogs rendered because `.p95-window` overrode the browser's hidden state
  - modal centering broken by the reset's `margin: 0`
  - text in a themed subtree inherited the page's resolved color
  - the prompt log showed whitespace as blank lines
- **Decisions:**
  - Added `<p95-wordmark>`, because an `<img>` SVG can't read CSS variables.
  - Pixel glyphs are generated (masks plus per-theme images), not hand-written SVG.
  - Fonts ship as TTF/OTF; woff2 needs fonttools, which isn't installed.
- **Known limits:**
  - Win95 scrollbar buttons render in Blink/WebKit only.
  - `:focus` styling can't be confirmed in headless screenshots, though the self-test confirms the focus logic.

## 12. Phase 3 results (2026-11-04)

- **Terminal schemes** (`packages/tui/terminal-themes`, generated by the `tui` target):
  - Ghostty, Kitty, Alacritty, WezTerm, foot, Windows Terminal, iTerm2 and base16, each × 4 themes
  - `phosphor95.dircolors`
  - The green Ghostty scheme equals the desktop's terminal palette.
- **`p95-style` crate** (Rust, ratatui 0.30 as an optional feature):
  - generated palettes: 171 colors per theme, each precomputed for truecolor, xterm-256 (OKLab nearest) and theme ANSI-16
  - `Env` detection (`NO_COLOR`, `P95_COLOR`, `COLORTERM`/`TERM`, locale, `P95_ASCII`, `P95_NERD_FONT`, `P95_REDUCED_MOTION`, `P95_THEME`)
  - three glyph tiers, with bevel border sets
  - semantic styles and widget bundles that follow the component specs' TUI renderings
  - the Operator as a half-block widget, its grid generated from `operator.svg`
- **Verification:**
  - 17 unit tests, a doc test, and a gallery render test over 96 combinations (4 themes × 4 depths × 2 tiers × 3 tabs). It asserts that mono never emits color and the ASCII tier never emits Unicode glyphs.
  - Clippy is clean.
  - Snapshots were rendered to PNG with PxPlus via `tools/ansi2png.py` and reviewed. They're in `packages/tui/screenshots/`.
- **Docs:** `foundations/cli.md` (env switches, status lines, help layout, prompts, progress, exit codes, full-screen rules) and `packages/tui/README.md`.
- **Decisions:**
  - `NO_COLOR` follows no-color.org (non-empty only); the accessibility doc was corrected to match.
  - In 16-color mode, surface backgrounds are left to the terminal.
  - In mono, meaning moves to bold, dim, reverse and underline, and the double border marks focus.
  - The crate works without ratatui, so terminal01's OpenGL HUD can use `Swatch::linear()`.
- **Not done:** Go (Lip Gloss) and Python (Textual) packages (deferred per decision 3). Phase 4 was skipped by decision.
