# @phosphor95/web

Phosphor95 for the web: tokens, classless base styles, components, opt-in CRT effects and vanilla
Web Components. No framework and no dependencies. It works in plain HTML, React, Svelte or anything else.

```sh
python3 tools/build.py web      # -> dist/web/   (the package)
python3 tools/build.py site     # -> dist/site/  (gallery = this package dogfooded)
python3 -m http.server -d dist/site 8095   # then open http://localhost:8095/  (?selftest runs the component self-test)
```

## Use

```html
<html data-theme="green">            <!-- green | amber | white | hc, on any element -->
<link rel="stylesheet" href="p95.css">
<script type="module" src="js/index.js"></script>

<section class="p95-window" data-active>
  <header class="p95-titlebar"><h2 class="p95-titlebar-title">Properties</h2>
    <div class="p95-titlebar-controls"><button data-action="close" aria-label="Close"></button></div></header>
  <div class="p95-window-body">
    <label class="p95-check"><input type="checkbox" checked> Stream tokens</label>
    <button class="p95-btn" data-default>OK</button>
  </div>
</section>
```

| File | What |
|---|---|
| `p95.css` | Everything, in cascade layers `p95.reset, p95.tokens, p95.base, p95.components, p95.utilities, p95.effects`. Your own unlayered CSS always wins |
| `p95-tokens.css` | Tokens, fonts, pixel masks and bevel recipes only, for when you bring your own components |
| `js/index.js` | Registers every element and runs `enhance()`. It exports `toast()`, `setTheme()`, `enhance()` |
| `js/p95-*.js` | Each element on its own, if you only need some |
| `fonts/` | PxPlus IBM VGA (CC BY-SA 4.0), VT323, W95FA (OFL). Licenses are in `fonts/licenses/` |
| `brand/` | Themeable `mark.svg`, `operator.svg`, `wordmark.svg`; favicons; per-theme PNGs |
| `icons/16`, `icons/32` | 22 Chicago95 icons, recolored (GPL-3.0+/MIT) |

## Layers of use

1. **Classless.** `base.css` styles semantic HTML (`button`, `input`, `select`, `fieldset`, `table`,
   `progress`, `meter`, `details`, `dialog`, `pre`, `kbd`…) with no classes at all.
2. **Classes.** `.p95-*` for components that have no single native element. The contract is in
   [`components/*.md`](../../components/), in the "Web" row of each spec.
3. **Elements.** Light-DOM Web Components for the pieces that need behavior. Being light DOM, they're
   styled by `p95.css` and themed by `data-theme` like everything else.

| Element | Does |
|---|---|
| `<p95-operator size state framed label>` | The avatar as inline SVG; recolors with the theme. `state="thinking"` is a stepped shimmer |
| `<p95-wordmark size>` | `PHOSPHOR95▮` as inline, themeable SVG |
| `<p95-rain density speed>` | Digital rain canvas behind its parent's content. 20 fps; pauses off-screen; static under reduced motion |
| `<p95-menu for>` / `<p95-menu data-context>` | Dropdown or context menu: roving focus, type-ahead, Esc, menubar Left/Right |
| `<p95-tabs>` | ARIA tabs over `role="tab"` / `role="tabpanel"` children |
| `<p95-dialog title level role>` | Modal `<dialog class="p95-window">` with a title bar; buttons with `value` close it |
| `<p95-boot autoplay>` | Typed POST lines (`<li data-level>`) and an optional `<progress>` |
| `<p95-prompt>` | A `> _` command line with history and a live log; `print(text, level)` |
| `<p95-palette hotkey>` | Ctrl/⌘+K command palette over `<button data-command>` children |
| `<p95-toast level title>` / `toast({...})` | Notifications in a polite live region; errors are `role="alert"` |

`enhance(root)` adds behavior to plain markup: `.p95-switch` toggling, `.p95-splitter` dragging and
arrow keys, `.p95-tooltip` show and hide, and `.p95-list[role=listbox]` selection.

## Rules the package follows

- **Theming on any subtree.** Token blocks re-declare every value that changes per theme. Derived
  variables (bevels, glow) are declared on `:root, [data-theme]`, and a themed element re-applies its
  text color and background.
- **Pixel glyphs** (check, radio, arrows, title-bar controls) are generated from ASCII pixel maps into
  CSS masks (`--p95-mask-*`). Where a mask can't be used, they become per-theme images (`--p95-img-*`).
- **Motion:** stepped timing only. `prefers-reduced-motion` stops the rain, flicker, cursor blink and
  spinners, and removes transitions. Effects are opt-in classes: `.p95-crt`, `.p95-scanlines`,
  `.p95-glow`, `.p95-cursor`, `.p95-decay`.
- **No blur** anywhere; the reference machine is a 2015 MacBook Air.

## Browser notes

- Win95-style scrollbar buttons need WebKit/Blink. Firefox gets themed standard scrollbars.
- Fonts ship as TTF/OTF. A woff2 conversion needs fonttools, which isn't installed.
