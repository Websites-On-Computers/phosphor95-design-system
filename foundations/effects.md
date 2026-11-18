# Effects

Effects make the system look like a CRT, and they are optional (principle 6). Every effect is **opt-in**, cheap, layered *over* content at `layer.overlay` with `pointer-events: none`, and never placed behind body text.

## Budget

The reference machine is a 2015 MacBook Air (Intel HD 6000, 1440×900). Rules:

- **No blur-heavy effects.** No `backdrop-filter`, no full-screen `filter: blur()`, no stacked text-shadows wider than `effect-size.glow-radius-hot`.
- An effect may cost **≤ 1 ms per frame** on the reference machine. Animated effects run at 20–30 fps, not 60.
- Effects pause when the page or window is hidden.
- In a TUI, effects are limited to color and glyphs. There are no shaders; the CRT shader lives in the terminal itself (Ghostty), not in apps.

## Catalog

| Effect | Purpose | Tokens | Web | TUI | Reduced motion |
|---|---|---|---|---|---|
| **Glow** | Marks hot (live, focused, hovered) text | `glow.base`, `glow.hot`, `effect.glow-strength`, `effect-size.glow-radius`, `effect-size.glow-radius-hot` | One `text-shadow: 0 0 <radius> <glow at strength alpha>` on headings and hot elements only. Never on body paragraphs | Bright color variant only | Static (no fade) |
| **Scanlines** | CRT texture | `effect.scanline-opacity`, `effect-size.scanline-period` | Fixed overlay, `repeating-linear-gradient`: transparent, then black at `scanline-opacity`, every `scanline-period` | None | Static, so allowed |
| **Vignette** | Darkens the screen edges | `effect.vignette` | Fixed overlay, one `radial-gradient` | None | Static, so allowed |
| **Flicker** | Faint brightness wobble | `effect.flicker` | Opacity animation on the overlay, amplitude `effect.flicker`, irregular and ≥ 1 s period | None | **Off** |
| **CRT curvature** | Barrel distortion | none: no token; avoid on the web | Not supported (it costs too much and distorts text). Suggest it with the vignette | Terminal shader only | n/a |
| **Digital rain** | Ambient identity on splash, lock and empty states | `effect.rain-density`, `duration.tick` | `<p95-rain>` canvas at 20 fps, colored `color.phosphor.6`–`10`, behind splash content only | Gallery or screensaver mode only | **Off** (a static frame or nothing) |

## Placement rules

1. **Never behind body text, forms or tables.** Rain and flicker are for splash screens, lock screens, empty states and hero areas. Scanlines may sit over the whole page only at `effect.scanline-opacity` (0.18) or below, and the contrast of text under them must still pass the gate's minimums. The gate measures colors without effects, so check scanlined pages by eye.
2. **One glowing thing per view.** Glow means hot; if everything glows, nothing is hot.
3. **Effects are off by default.** On the web, a page opts in with `.p95-crt` (scanlines + vignette + flicker) or the individual classes. On the desktop, the theme's `crt on|off` toggle is the equivalent.
4. **Flashing limit:** nothing may flash more than **3 times per second** (WCAG 2.3.1), and `effect.flicker` stays a small wobble, not a flash. Cursor blink (`duration.blink`, about 0.94 Hz) is well under the limit.
5. **Respect `prefers-reduced-transparency` and `prefers-contrast: more`:** drop the overlays, or switch to the `hc` theme.
