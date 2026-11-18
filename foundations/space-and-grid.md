# Space and grid

## Units

| Unit | Value | Token |
|---|---|---|
| Base unit | 4 px | All `space.*` steps are multiples of it |
| Cell width | 8 px | `size.cell.width`, one UI-font character, one TUI column |
| Cell height | 16 px | `size.cell.height`, one line, one TUI row |

Lay things out in cells. Use 4 px steps only to fine-tune inside a component.

## Spacing scale (`space.*`)

Each token is named for its pixel value.

| Token | px | Typical use |
|---|---|---|
| `space.0` | 0 | Reset |
| `space.2` | 2 | Gaps the width of a bevel only (progress segment gap) |
| `space.4` | 4 | Field padding, icon-to-label gap |
| `space.8` | 8 | One cell: window padding, gap between buttons, table cell padding |
| `space.12` | 12 | Button horizontal padding |
| `space.16` | 16 | One cell tall: menu item padding, gap between groups |
| `space.24` | 24 | Section gap inside a panel |
| `space.32` | 32 | Gap between panels |
| `space.48` | 48 | Page section gap |
| `space.64` | 64 | Hero and splash margins |

## Sizes (`size.*`)

| Token | px | Use |
|---|---|---|
| `size.control.sm` | 24 | Default height for buttons, fields, menu items, list rows, tabs, title bars and status bars |
| `size.control.md` | 32 | Large controls, for touch-first pages and toolbars |
| `size.icon.sm` | 16 | Inline icons, checkboxes |
| `size.icon.md` | 32 | Desktop and launcher icons |
| `size.icon.lg` | 48 | The Operator at native size |
| `size.scrollbar` | 16 | Scrollbar thickness |
| `border.width.hair` | 1 | Focus ring, separators |
| `border.width.bevel` | 2 | A full bevel (1 px outer + 1 px inner) |
| `border.radius.none` | 0 | The only radius |

Component tokens use these. For example, `button.height` → `size.control.sm`, and `button.min-width` = 72 px, Win95's 75 px snapped to the cell grid.

## Layout (web)

| Token | px | Meaning |
|---|---|---|
| `breakpoint.sm` | 640 | Phone to tablet. One column; window chrome can collapse to panels |
| `breakpoint.md` | 960 | Two columns: sidebar plus content |
| `breakpoint.lg` | 1440 | The 1440×900 MacBook Air screen the theme was born on |

CSS can't use custom properties inside media queries, so the web package outputs breakpoints as literal values.

- Page gutters are at least `space.16` on phones and `space.32` from `md` up.
- Content columns are widths in whole cells (multiples of 8 px).
- Keep width changes in steps at the breakpoints, rather than fluid scaling that breaks the pixel grid.

## TUI mapping

1 column = 8 px and 1 row = 16 px. Round every spacing value to whole cells:

| Web token | TUI |
|---|---|
| `space.4` | 0 or 1 column (usually 1 for horizontal padding, 0 vertical) |
| `space.8` | 1 column |
| `space.16` | 2 columns, or 1 row |
| `space.24` / `space.32` | 3–4 columns, or 1–2 rows |
| `size.control.sm` (24 px) | 1 row (controls are one line tall) |

Horizontal padding inside a box is 1 column. Leave one blank row between groups, and none between list items. The layout must still work at **80×24**; wider terminals get more columns of content, not bigger margins.
