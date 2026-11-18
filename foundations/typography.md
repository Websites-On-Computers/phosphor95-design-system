# Typography

Phosphor95 is set in bitmap fonts, and bitmap fonts have rules.

## Families

| Token | Stack | Native size | Use for |
|---|---|---|---|
| `font.family.ui` | PxPlus IBM VGA 8x16, W95FA, ui-monospace, monospace | 16 px | All UI text, and the wordmark |
| `font.family.small` | PxPlus IBM VGA 8x14, PxPlus IBM VGA 8x16, … | 14 px | Captions, dense tables |
| `font.family.mono` | PxPlus IBM VGA 9x16, ui-monospace, monospace | 16 px (9 px advance) | Code, terminal output, tabular numbers |
| `font.family.display` | VT323, PxPlus IBM VGA 8x16, monospace | – | Big text only: splash screens, clocks, headings ≥ 32 px |
| `font.family.alt-ui` | W95FA, PxPlus IBM VGA 8x16, sans-serif | 16 px | Optional proportional Win95-style UI face |

The font files and their licenses are in `assets/fonts/`. PxPlus is CC BY-SA 4.0 and needs attribution; VT323 and W95FA are OFL. See `LICENSES.md`.

## Roles (`type.*`)

Every role is a DTCG `typography` composite. Weight is always `font.weight.regular` (400), and letter spacing is `space.0`.

| Token | Family | Size | Line height | Case |
|---|---|---|---|---|
| `type.body` | ui | `font.size.16` | `font.line-height.prose` (1.5 = 24 px) | as written |
| `type.ui` | ui | 16 | `font.line-height.cell` (1) | as written |
| `type.small` | small | `font.size.14` | cell | as written |
| `type.code` | mono | 16 | cell | as written |
| `type.label` | ui | 16 | cell | **uppercase** |
| `type.heading-3` | display | `font.size.32` | cell | as written |
| `type.heading-2` | display | `font.size.48` | cell | as written |
| `type.heading-1` | display | `font.size.64` | cell | **uppercase** |
| `type.display` | display | `font.size.96` | cell | **uppercase** |

Case is carried in `$extensions.com.phosphor95.textCase`, because DTCG has no text-case property. On the web it maps to `text-transform: uppercase`.

## Rules

1. **Pixel-exact sizes only.** PxPlus renders crisply only at its native size and whole multiples of it: 8x16 and 9x16 at 16/32/48/64 px, 8x14 at 14/28 px. Use the `font.size.*` steps and nothing in between. No `rem` scaling, no fluid type.
2. **No bold.** There's one weight, and synthetic bold smears pixel fonts. For emphasis, in order of strength:
   - **case** (`type.label`)
   - **glow** (`text.hot`)
   - **inversion** (`select.bg`/`select.fg`, for one or two words at most)
3. **No italic.** For a mention or citation, use `text.secondary` or quotation marks.
4. **Uppercase** is for system voice: title bars, status lines, boot lines, button labels for system actions (`OK`, `CANCEL`), headings at `heading-1` and above, and the wordmark. Help text, body copy and messages that explain something are sentence case. Never uppercase more than a short line.
5. **Line height.** Controls, tables, terminals and labels use `font.line-height.cell`, so one line = one 16 px cell. Running text on the web uses `font.line-height.prose` (24 px, 1.5 cells).
6. **VT323 is for display only.** It's outlined, not a true bitmap. Its stems don't sit on a consistent pixel grid, so it is not pixel-exact at any size. Use it at 32 px and up, where antialiasing is acceptable. For the same reason the wordmark uses **PxPlus IBM VGA 8x16**, rendered 1-bit (see `brand/logo/`).
7. **Measure.** Keep body text at 60–80 characters per line (about 480–640 px at 8 px per character).

## Web

Turn antialiasing off for the bitmap faces, so their pixels stay hard:

```css
.p95, .p95 * {
  -webkit-font-smoothing: none;     /* Safari/Chrome on macOS */
  -moz-osx-font-smoothing: unset;
  font-smooth: never;               /* where supported */
  text-rendering: optimizeSpeed;
  font-kerning: none;
  font-variant-ligatures: none;
}
.p95 :is(h1, h2, .p95-display) {    /* VT323 */
  -webkit-font-smoothing: antialiased;
}
```

Load the fonts with `font-display: block` and preload `PxPlus IBM VGA 8x16`, so the layout doesn't jump when the bitmap metrics arrive.

## TUI

In a terminal the font belongs to the user, so you can't pick a family or size. Type rules turn into cell rules:

| Web | TUI |
|---|---|
| `type.label` (uppercase) | Uppercase |
| `text.hot` (glow) | Bright variant, or bold rendered as bright (most terminals do this) |
| Inversion | Reverse video (SGR 7) |
| `text.secondary` | Dim color (`ansi.blue` in green). Never SGR 2 "faint" alone, which some terminals don't support |
| `type.heading-*` | An uppercase line plus a rule (`──`), or the half-block wordmark for the app banner |

Don't use italics or underline as the only signal. Many terminals render them poorly or not at all.
