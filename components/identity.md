# Identity

Avatar (the Operator), wordmark, splash/boot screen. Brand usage rules live in `brand/`. This file covers the components that render them.

---

### Avatar (the Operator)

**Purpose:** the face of Phosphor95 and TERMINAL-01. It's the lock-screen pixel head. It's used for the logo mark, about screens, empty states, the assistant's presence, and the user/agent identity in chat-like views.

**Anatomy:**
1. The 48×48 pixel drawing, in six colour roles.
2. Optionally, the mark frame: a 64×64 sunken 2px bevel well (`surface.base`), with the avatar inset 8px.

| Part | Token |
|---|---|
| Hair | `operator.hair` |
| Shade 1 / Shade 2 (shirt, shadow) | `operator.shade-1` / `operator.shade-2` |
| Mid (features) | `operator.mid` |
| Skin (face fill) | `operator.skin` |
| Light (dither highlights) | `operator.light` |
| Frame well | `operator.frame-bg`, sunken `bevel.*` |
| Native size | `operator.size` (48px) |

The green colours are the lock-screen PNG exactly (`color.avatar.green.*`). Amber and white use lightness-matched sets (`color.avatar.amber.*`, `color.avatar.white.*`). HC uses green.

**Sizes:** integer multiples of 48px only: 48, 96, 144, 192, 384. Below 48px, use the hand-pixelled 16px sprite (`brand/source/avatar-phosphor95-16.png`) at 16 or 32px. **Never smooth, resample, rotate or crop the drawing**, and never draw it at a fractional scale.

| State | Change |
|---|---|
| idle | Static |
| thinking | The `operator.light` dither pixels alternate with `operator.skin` every `duration.slow`, stepped. A slow shimmer |
| speaking | A `glow.hot` halo at `effect.glow-strength`, pulsing with the speech envelope (stepped, ≤ 4 Hz) |
| offline | All six roles drop to `text.disabled`, and the frame shows `[ .. ]` |
| reduced motion | Every state is static. Thinking and speaking show as a Badge instead (`[ .. ]`, `[ >> ]`) |

**Keyboard:** none. The avatar isn't interactive. If it's a link (e.g. to About), the link takes the focus ring.

**Accessibility:**
- Decorative (`alt=""`, `aria-hidden`) next to the wordmark or a name.
- Standalone, it has `role="img"` and `aria-label="Phosphor95 Operator"`.
- State changes are announced through a separate `role="status"` text ("Thinking"), never by the image.

**Content rules:** the Operator doesn't speak in exclamation marks. Captions beside it follow the machine voice (see `brand/voice.md`).

**Web:**
- `<p95-operator size="2" state="idle">` renders the themeable `brand/logo/operator.svg`. Its fills read `--p95-operator-*`, so the avatar recolours with `data-theme`.
- Static: `<img src="operator-green@2x.png" style="image-rendering: pixelated">`.

**TUI:** half-block truecolor art (`brand/logo/operator-<theme>.ansi`, 48×24 cells). Use the 16px sprite (`operator-small.ansi`, 16×8 cells) in narrow panes.
```
   ▄▄▄██▄▄▄
 ▄██████▀▀▀█▄
 ████▀▀░░▒▒█▌     (truecolor half-blocks)
 ASCII fallback: brand/logo/operator.txt   (: - = + # @ ramp)
```
- At 256 or 16 colours, quantize to `ansi.*` (phase 3 ladder).
- In mono, use the ASCII art.

**ratatui:** a `Paragraph` from the pre-rendered `.ansi` file (via `ansi-to-tui`), or drawn cell by cell from the 48×48 role grid.

---

### Wordmark

**Purpose:** the name `PHOSPHOR95` set in the logo face: PxPlus IBM VGA 8x16, 1-bit, followed by a block cursor.

**Anatomy:** ten glyphs and the block cursor cell. The cursor is a full 8×16 cell with rows 1–14 lit. Lockups add the mark to the left and the tagline below.

| Part | Token |
|---|---|
| Letters | `text.primary` |
| Cursor | `text.primary`. When animated, it blinks at `duration.blink` with `easing.steps` |
| Tagline | `text.secondary`, `type.ui` (`DESIGN SYSTEM`) |
| Lockup background | `surface.face` or `surface.base` |
| Glow (optional, hero use) | `glow.base`, `effect-size.glow-radius`, `effect.glow-strength` |

**Sizes:** 16px tall (1×) and integer multiples: 32, 48, 64. Don't set the wordmark as live text in VT323 or any other face. Use the SVG or PNG assets.

**States:**
- static.
- blinking cursor: splash and hero only, and never under reduced motion.

**Accessibility:** `<img alt="Phosphor95">`, or the SVG with `role="img"` and `aria-label`. The cursor is part of the image.

**Content rules:**
- Always one word, uppercase, no hyphen: `PHOSPHOR95`.
- In running text, the name is written "Phosphor95".
- The GNOME theme stays "Phosphor-95".
- TERMINAL-01 is the machine and persona name, not a substitute for the wordmark.

**Web:** `<p95-wordmark size="2">` inlines the themeable SVG (fills read `--p95-text-primary`), so it recolours with `data-theme`. Static: `<img class="p95-wordmark" src="wordmark.svg">` renders green; use `wordmark-<theme>.png` for other themes. Rasters need `image-rendering: pixelated`.

**TUI:** `brand/logo/wordmark.txt`: 8 rows of half-blocks, 88 columns.
```
 ▀██▀▀█▄ ██   ██ ▄█▀▀▀█▄ ... ███████
 ASCII: PHOSPHOR95_   (plain text; terminals below 88 cols)
```
**ratatui:** a `Paragraph` of the text file, styled `text.primary`.

---

### Splash / boot screen

**Purpose:** the launch screen: the boot logo and POST sequence seen in Plymouth and on the TERMINAL-01 face app's startup.

**Anatomy:**
1. A full-screen `surface.void` or `surface.base` background, with optional digital rain behind at `effect.rain-density`.
2. The centred wordmark (or the TERMINAL-01 product name) at 4× or larger.
3. A tagline line.
4. A segmented Progress bar.
5. Optionally, a scrolling log of Boot lines, or a prompt dialog (e.g. UNLOCK DISK).

| Part | Token |
|---|---|
| Background | `surface.void` |
| Name | `type.display` (VT323, for product names set live) or the wordmark asset. Colour `text.hot` with `glow.base` |
| Tagline | `text.secondary`, `type.label` (`PHOSPHOR-95 // LOCAL INTELLIGENCE NODE`) |
| Progress | `progress.*` |
| Boot log | Boot line (`status.*`, `type.code`), typed at `duration.type` |
| Effects layer | Scanlines `effect.scanline-opacity` / `effect-size.scanline-period`, vignette `effect.vignette`, at `layer.overlay` |

| State | Change |
|---|---|
| booting | Progress advances. Lines are typed out |
| waiting for input | A Dialog appears over the splash |
| failed | Progress stops. An `[ERR ]` boot line is shown, plus a Retry or "Press any key" line |
| reduced motion | No rain, no typing, no flicker. Lines appear whole |

**Keyboard:** Esc skips to the log view (showing details). Any key continues past a "Press any key" prompt.

**Accessibility:**
- `role="progressbar"` for the bar, and a `role="log"` region for the lines.
- The splash must never block for more than a few seconds without an accessible status text.

**Content rules:** POST-style uppercase lines (`PHOSPHOR BIOS v4.51`, `MEMORY TEST 8192 MB OK`). Use the BIOS and tagline strings from `brand/source/system-phosphor95.toml`.

**Web:** `<p95-boot>` (sequence + progress), with `<p95-rain>` behind it and the `.p95-crt` effects class on the container.

**TUI:** the full terminal, cleared, with everything centred.
```

               ▀██▀▀█▄ ██   ██ ...  (wordmark.txt)
             PHOSPHOR-95 // LOCAL INTELLIGENCE NODE
             ▕████████████░░░░░░░░░░░░░░░░▏
 [ OK ] memory      8192 MB
 [ OK ] uplink      node-01 192.0.2.10
```
**ratatui:** a `Layout` with centred `Rect`s, holding `Paragraph`s and a `Gauge`, inside a full-screen `Clear`.
