# Iconography

## Pixel icons (web and desktop)

- **Source:** a curated subset of Chicago95, recolored by luminance onto the green ramp by the Phosphor-95 theme tooling (`../theme/tools/components/icons.py`). It ships in `assets/icons/` **under Chicago95's license (GPL-3.0+/MIT), with attribution**. See `LICENSES.md`.
- **Sizes:** `size.icon.sm` (16 px) inline and in menus; `size.icon.md` (32 px) for desktop, launcher and dialog icons. Use the hand-drawn bitmap for each size. Never scale a 32 px icon down to 16.
- **Pixel-snapped:** render at native size or whole multiples, with `image-rendering: pixelated`. Never smooth-scale, rotate or blur an icon.
- **Color:** icons are luminance-mapped to `color.phosphor.*`. In other themes they get the same mapping onto that theme's ramp. Don't tint icons with status colors; put a status glyph or badge next to the icon instead.
- **Spacing:** 4 px (`space.4`) between an icon and its label, and the icon is vertically centered in its cell.
- **Meaning:** an icon next to text is decorative (`aria-hidden="true"`). An icon on its own needs an accessible name and a tooltip.

**The Operator is not an icon.** It's the system's persona: logo, avatar, empty states, about screens. Don't use it as a "user" or "account" icon, and don't put it in toolbars. It has its own tokens (`operator.*`, `size.icon.lg`) and assets in `brand/logo/`.

## TUI glyphs

Tier 1 is **ASCII-safe**: it works in any terminal, over SSH, and in logs. Tier 2 uses Unicode box and block characters, and is the default when the locale is UTF-8. Tier 3 is **Nerd Font**, opt-in only (`P95_NERD_FONT=1`). Every app must work on tier 1.

| Meaning | ASCII (tier 1) | Unicode (tier 2) | Nerd Font (tier 3, optional) | Color token |
|---|---|---|---|---|
| OK | `[ OK ]` | `[ OK ]` or `✓` | `` | `status.ok.fg` |
| Info | `[INFO]` | `[INFO]` or `i` | `` | `status.info.fg` |
| Warning | `[WARN]` | `[WARN]` or `!` | `` | `status.warn.fg` |
| Error | `[ERR ]` | `[ERR ]` or `✗` | `` | `status.error.fg` |
| Checkbox on / off | `[x]` / `[ ]` | `[■]` / `[ ]` | `` / `` | `check.mark` |
| Radio on / off | `(*)` / `( )` | `(●)` / `( )` | `` / `` | `check.mark` |
| Arrows | `<` `>` `^` `v` | `◄` `►` `▲` `▼` | `` `` `` `` | `text.primary` |
| Tree expanded / collapsed | `[-]` / `[+]` | `▼` / `►` (with `├─` `└─` `│` guides) | `` / `` | `text.secondary` (guides) |
| Spinner | `\| / - \` | Braille `⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏` | – | `text.hot` |
| Progress, full → empty | `#` `=` `-` `.` | `█` `▓` `▒` `░` | – | `progress.fill` / `progress.track` |
| Separators | `//` and `\|` | `//` and `│` | – | `text.secondary` |
| Cursor | `_` | `█` | – | `text.hot` |
| Menu / submenu | `>` | `►` | `` | `text.primary` |
| Key hint | `^Q Quit` | `^Q Quit` | – | `statusbar.key-*` |

Rules:
- Status prefixes are exactly 6 characters wide (`[ OK ]`, `[INFO]`, `[WARN]`, `[ERR ]`) so log columns line up.
- Spinners advance every 80–100 ms (`duration.fast`), and stop when reduced motion is on; show `[....]` or a percentage instead.
- Progress bars fill with whole cells. Use the partial blocks (`▓▒░`) only for the single leading cell.
