# Bevels and elevation

Depth is drawn with edges, as in Windows 95. There are no shadows, no blur, and no rounded corners (`border.radius.none`).

## The four edges

| Token | Step | Win95 original | Role |
|---|---|---|---|
| `bevel.hi` | 9 | `#FFFFFF` | Inner highlight |
| `bevel.light` | 7 | `#DFDFDF` | Outer highlight |
| `bevel.shadow` | 2 | `#808080` | Inner shadow |
| `bevel.dark` | void | `#000000` | Outer shadow |

A full bevel is `border.width.bevel` (2 px): a 1 px outer ring and a 1 px inner ring. Light comes from the top-left.

## Recipes

The notation is outer ring / inner ring, for the top-left (TL) and bottom-right (BR) edges.

| Recipe | TL outer | TL inner | BR inner | BR outer | Fill | Used by |
|---|---|---|---|---|---|---|
| **Raised** | `bevel.light` | `bevel.hi` | `bevel.shadow` | `bevel.dark` | `surface.face` | Buttons, title-bar buttons, scrollbar thumbs, toolbar |
| **Pressed** | `bevel.dark` | `bevel.shadow` | `bevel.hi` | `bevel.light` | `surface.face-pressed` | Button while held. Content shifts 1 px down and right |
| **Sunken / field (well)** | `bevel.shadow` | `bevel.dark` | `bevel.light` | `bevel.hi` | `surface.base` | Text fields, list and table bodies, checkbox and radio wells, the Operator mark |
| **Window** | `bevel.light` | `bevel.hi` | `bevel.shadow` | `bevel.dark` | `surface.face` | Windows and dialogs: raised, with `window.padding` and a title bar |
| **Group (etched)** | `bevel.shadow` then `bevel.hi` | – | `bevel.hi` then `bevel.shadow` | – | none | Group box (fieldset), separators: a 1 px groove, 2 px total |
| **Default-button frame** | 1 px `button.frame-default` (`border.strong`) all round, outside a raised bevel | | | | | The button that Enter activates |

```
Raised                    Pressed                   Sunken (field)
L L L L L L L L D         D D D D D D D D L         S S S S S S S S H
L H H H H H H S D         D S S S S S S H L         S D D D D D D L H
L H . . . . . S D         D S . . . . . H L         S D . . . . . L H
L H . . . . . S D         D S . . . . . H L         S D . . . . . L H
L S S S S S S S D         D H H H H H H H L         S L L L L L L L H
D D D D D D D D D         L L L L L L L L L         H H H H H H H H H

L = bevel.light   H = bevel.hi   S = bevel.shadow   D = bevel.dark   . = fill
```

**Focus** sits inside the bevel: a 1 px dotted `focus.ring`, inset 2 px from the inner edge (on the web, `outline: 1px dotted var(--p95-border-focus); outline-offset: -4px`). It never replaces the bevel.

**High-contrast theme.** All four `bevel.*` tokens are step 10, so every recipe flattens into a 2 px solid frame. Pressed and raised then look the same, so the pressed state also needs the 1 px content shift and the `surface.face-pressed` fill.

## Elevation

Stacking order is a number, never a shadow.

| Token | Value | Layer |
|---|---|---|
| `layer.base` | 0 | Page content |
| `layer.raised` | 1 | Raised panels, sticky table headers inside a panel |
| `layer.sticky` | 10 | Sticky app bars, the taskbar |
| `layer.menu` | 100 | Menus, dropdowns, tooltips |
| `layer.dialog` | 200 | Modal dialogs, over `surface.overlay` |
| `layer.toast` | 300 | Toasts and notifications |
| `layer.overlay` | 400 | CRT effects: `pointer-events: none`, always on top |

What tells you something is on top is its **bevel** and its **title bar**. An active window gets `title.active.*` and a `border.strong` frame; everything beneath gets `title.inactive.*`. Never signal elevation with a lighter surface, a glow or a shadow.

## TUI equivalents

| Web | Unicode | ASCII fallback |
|---|---|---|
| Panel / group (`border.default`) | `┌─┐ │ └─┘` | `+-+ \| +-+` |
| Focused or active window (`border.strong` or `border.focus`) | `╔═╗ ║ ╚═╝` | `#=# \| #=#` |
| Title bar (`title.active.*`) | Reverse-video row: ` FILE MANAGER ` | Same (SGR 7) |
| Raised button | Half blocks: `▄` row above in `bevel.light`, `▀` row below in `bevel.dark`, or `[ OK ]` | `[ OK ]` |
| Pressed button | `[▓OK▓]` or reverse video | `[*OK*]` |
| Sunken well | Fill `surface.base` inside `┌─┐`, or `▕ ▏` edges | `[ ]` |
| Dither / shading (scrollbar track, disabled fill) | `░` light, `▒` medium, `▓` dark | `.` `:` `#` |
| Separator | `─` (subtle), `━` (strong) | `-` `=` |

Box borders take `border.*` colors; the title row takes `title.*`. In mono and `NO_COLOR` terminals, use `╔═╗` for the focused pane and `┌─┐` for the others. That's the only depth cue left, so it has to be there.
