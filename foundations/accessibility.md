# Accessibility

Accessibility beats every other principle. These rules are what lets a green-on-black, pixel-font system be one people can use all day.

## Contrast

- **Policy:** body text ≥ 7:1 (AAA); secondary text, links and status text ≥ 4.5:1 (AA); UI boundaries, focus rings and graphics ≥ 3:1 (WCAG 1.4.11).
- **Gate:** `tokens/checks.json` lists every meaningful pair. `tools/build.py` measures them in every theme and **fails the build** on a regression. Current numbers: **[contrast.generated.md](contrast.generated.md)**.
- **Exemptions, by design:**
  - `text.disabled`: WCAG exempts inactive controls, and it must look off.
  - `border.subtle`: decorative only.
  - `text.secondary` on `surface.face-hover`: never drawn, because hover brightens text to primary.
  - Never use an exempt token for information.
- **Effects:** the gate measures colors without effects. Scanlines and the vignette darken slightly, so pages with effects on get checked by eye.
- **Need more?** The `hc` theme (`data-theme="hc"`) has true-black surfaces, no dim text, and solid frames. Offer it whenever the OS asks for more contrast (`prefers-contrast: more`).

## Focus

- Every interactive element shows a visible focus indicator: the dotted `focus.ring` in `border.focus` (step 12). On the web, use `:focus-visible`, with `outline-offset: -4px` inside bevels.
- **Never remove it** (`outline: none` without a replacement is a bug).
- Focus order follows reading order. Dialogs trap focus and give it back to the element that opened them.
- TUI: the focused pane uses `╔═╗` plus `border.focus`, and the focused item is reverse video. Both must show without color.

## Keyboard first

- Everything works without a pointer: Tab/Shift+Tab between controls, arrow keys inside composite widgets (menus, lists, tabs, radio groups), Enter for the default button, Esc to close, Space to toggle.
- Menus show their accelerators (`menu.shortcut`), and TUIs always show a key-hint bar (`statusbar.*`).
- Don't trap shortcuts the user's OS or terminal already owns.

## Status and color

- Never show a state by color alone. Every `status.*` use carries its prefix (`[ OK ]` `[INFO]` `[WARN]` `[ERR ]`) or a glyph from [iconography.md](iconography.md). This matters even more in the amber and white themes, where ok and info are close to the text color.
- Errors say what happened, why, and how to fix it, in text next to the control (`field.invalid-border` plus a message). On the web, link them with `aria-describedby`.

## Motion and flashing

- Nothing flashes more than 3 times per second (WCAG 2.3.1).
- `prefers-reduced-motion: reduce` turns off rain, flicker and zoom, and makes typed text and decay instant. See [motion.md](motion.md).
- `prefers-reduced-transparency`: drop the scanline and vignette overlays, and make `surface.overlay` opaque.
- Typed-out text must not hold up interaction. A keypress or click skips to the end.

## Terminals: NO_COLOR and mono

- Honor `NO_COLOR` (set and non-empty, per no-color.org): no color escapes. Use bold, reverse video and the box styles only.
- With `TERM=dumb`, or when output isn't a TTY: plain ASCII (tier 1 glyphs), no cursor movement, no spinners. Print progress as lines.
- Every TUI screen must be usable in mono: focus by `╔═╗` and reverse video, status by prefix, selection by reverse video.

## Screen readers (web)

- **ASCII and ANSI art** (the Operator, the wordmark, boot banners) gets `aria-hidden="true"` if the text duplicates something nearby. Otherwise wrap it in `role="img"` with an `aria-label` (for example "Phosphor95 Operator").
- **Boot lines and live logs** go in a live region: `role="log"` with `aria-live="polite"`. Errors in it should also be sent to an `aria-live="assertive"` alert.
- Typed-out text is in the DOM in full from the start, with the animation done visually (or `aria-busy` until it finishes), so screen readers read it once rather than letter by letter.
- The Win95 chrome is decoration: title-bar buttons are real `<button>`s with labels ("Close", "Minimize"), and windows are `role="dialog"` with `aria-labelledby` pointing at the title bar.

## Targets and sizing (web)

- Minimum target is **24×24 px** (`size.control.sm`, WCAG 2.5.8). Touch-first pages use `size.control.md` (32 px), with at least `space.8` between targets.
- Text zoom: pixel fonts snap to `font.size.*` steps, but the page must still reflow at 200% browser zoom. Use whole-cell widths and no fixed-height text containers.
