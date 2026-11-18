# Navigation

Menubar, menu, context menu, taskbar/status bar, breadcrumbs, command palette, key-hint bar.

Shared rule for this file: a hovered or highlighted item is **inverted** (`menu.item-hover-bg` / `menu.item-hover-fg`, which alias `select.*`). Inversion is the single "you are here" signal across the system.

---

### Menubar

**Purpose:** the top-level command menus of a window (File, Edit, View, Help).

**Anatomy:**
- A strip of flat items. The mnemonic letter is underlined.
- Each item opens a Menu.

| Part | Token |
|---|---|
| Strip | `menu.bg`, bottom rule `border.subtle` |
| Item | `menu.text`, `type.ui`, padding-x `space.8`, height `menu.item-height` |
| Item open / hovered | `menu.item-hover-bg` / `menu.item-hover-fg` |
| Disabled item | `menu.text-disabled` |

| State | Change |
|---|---|
| hover (while a menu is open) | Opens that item's menu immediately |
| open | The item is inverted |
| focus (Alt or F10 pressed) | The first item is inverted and mnemonics are shown |

**Keyboard:**
- Alt or F10 focuses the strip.
- ← and → move between items. ↓ or Enter opens the menu.
- Alt + a mnemonic letter opens that menu directly.
- Esc closes the menu, then leaves the strip.

**Accessibility:**
- `role="menubar"` with `role="menuitem"` children carrying `aria-haspopup="menu"` and `aria-expanded`.
- A screen reader hears "File, menu item, collapsed".

**Content rules:** single words in title case: File, Edit, View, Help. Keep the standard order.

**Web:** `<nav class="p95-menubar" role="menubar">`. Each item is a `<button role="menuitem">` driving a `<p95-menu>`.

**TUI:**
```
 ▐File▌ Edit  View  Help              ← File open (inverted)
 ASCII:  [File] Edit  View  Help
```
**ratatui:** a `Paragraph` line of `Span`s, with the open item styled as `select.*`.

---

### Menu

**Purpose:** a list of commands that drops down from a menubar, a button or a select.

**Anatomy:**
1. Raised frame
2. Items: an optional 16px icon or check column, the label, the shortcut (right-aligned), and a submenu arrow ▶
3. Separators

| Part | Token |
|---|---|
| Frame | `menu.bg`, raised `bevel.*`, width `border.width.bevel` |
| Item | `menu.text`, height `menu.item-height`, padding-x `menu.padding-x` |
| Hovered item | `menu.item-hover-bg` / `menu.item-hover-fg` (the shortcut inverts too) |
| Shortcut | `menu.shortcut` |
| Disabled | `menu.text-disabled`. Not highlighted on hover |
| Separator | 1px `menu.separator`, with `space.4` margin above and below |
| Check / radio mark | `menu.text` (✓ / •) |
| Layer | `layer.menu` |

| State | Change |
|---|---|
| hover / arrow-key focus | Inverted |
| submenu open | The parent stays inverted, and the submenu opens to the right (to the left if it would overflow) |
| disabled | `menu.text-disabled`. Skipped by arrow keys only if the platform does that natively; otherwise it can be focused but does nothing |

**Keyboard:**
- ↑ and ↓ move; → opens a submenu and ← closes it.
- Enter activates an item; Esc closes the menu.
- A mnemonic letter or typed text jumps to the matching item.

**Accessibility:**
- `role="menu"`, containing `menuitem`, `menuitemcheckbox` and `menuitemradio` items.
- Shortcuts go in `aria-keyshortcuts`.
- A screen reader hears "Save log, Ctrl+S, menu item".

**Content rules:**
- Labels are verb + object in sentence case: "Save log".
- An item that opens a dialog ends in "…".
- Shortcuts use the platform format, e.g. "Ctrl+S".

**Web:** `<p95-menu>` with `<button role="menuitem">` children and `<hr>` separators.

**TUI:**
```
 ┌──────────────────────┐
 │ New window   Ctrl+N  │
 │▐Save log…    Ctrl+S ▌│
 ├──────────────────────┤
 │ Quit         Ctrl+Q  │
 └──────────────────────┘
 ASCII: +---- ... ----+ with >Save log<  highlighted by brackets
```
**ratatui:** a `List` inside a `Block`, drawn over a `Clear`, with the highlight style `select.*`.

---

### Context menu

**Purpose:** commands for the object under the pointer or focus.

**Anatomy, tokens and states:** the same as Menu. It opens at the pointer position, or at the focused object's position when opened from the keyboard.

**Keyboard:** Shift+F10 or the Menu key opens it. Everything else behaves as in Menu.

**Accessibility:** the same as Menu. Focus returns to the invoking object on close.

**Content rules:**
- At most about 10 items. Put the most frequent action first.
- Never put an action *only* in a context menu.

**Web:** `<p95-menu data-context>`, opened from the `contextmenu` event.

**TUI:** a Menu anchored at the cursor cell.

**ratatui:** as Menu.

---

### Taskbar / status bar

**Purpose:**
- **Status bar** (bottom of a window): state readouts, such as cursor position or connection.
- **Taskbar** (bottom of the screen): START, the open windows, and the tray clock.

**Anatomy:**
- Status bar: a raised strip divided into sunken fields.
- Taskbar: the START button, a window button per window (the active one is pressed in), and a sunken tray.

| Part | Token |
|---|---|
| Strip | `statusbar.bg`, `statusbar.fg`, height `statusbar.height`, top edge `bevel.hi` |
| Sunken field | `surface.face`, sunken `bevel.*`, padding-x `space.4` |
| Window button | Button tokens. The active window's button is pressed (`button.face-pressed`, sunken) |
| START | Button with label `type.label` (uppercase) |
| Live values | `text.primary`. Stale values → `text.secondary` |
| Layer | `layer.sticky` |

| State | Change |
|---|---|
| field updating | The value repaints in place; no animation |
| warning / error | The field shows an `[WARN]` / `[ERR ]` prefix in `status.warn.fg` / `status.error.fg` |

**Keyboard:**
- The status bar isn't focusable unless a field is interactive.
- Taskbar: Super (or Ctrl+Esc) focuses START. ← and → move between window buttons.

**Accessibility:**
- Status bar: `role="status"`, announcing changes politely.
- Taskbar: `role="toolbar"` with `aria-label="Taskbar"`.

**Content rules:**
- Status fields are terse uppercase readouts: `LN 12 COL 4`, `UPLINK 62%`.
- Separate readouts with ` // `.

**Web:** `<footer class="p95-statusbar">` with `<span class="p95-statusbar-field">` fields.

**TUI:** the bottom row, drawn inverted or on `statusbar.bg`. Fields are separated by `│`.
```
 TERMINAL-01 │ UPLINK 62% │ [WARN] 95°C │ 18:29
 ASCII:  TERMINAL-01 | UPLINK 62% | [WARN] 95C | 18:29
```
**ratatui:** a `Paragraph` with `Line::from(spans)` in the last `Rect`.

---

### Breadcrumbs (path bar)

**Purpose:** shows where the current item sits in a hierarchy, and lets you jump up.

**Anatomy:** a row of flat buttons separated by a `/` glyph. The last segment is the current location and isn't a link.

| Part | Token |
|---|---|
| Segment | Flat button (`button.*`). Label `text.primary` |
| Segment hover | `button.face-hover`, `button.text-hover` |
| Current segment | Sunken well: `field.bg`, sunken `bevel.*`, label `text.primary` |
| Separator | `text.secondary` |

| State | Change |
|---|---|
| hover | Raised bevel appears |
| focus | `focus.ring` |
| overflow | Leading segments collapse into a `…` menu button |

**Keyboard:** each segment is a Tab stop, or use a roving tabindex with ← and →.

**Accessibility:**
- `<nav aria-label="Breadcrumb">` containing an `<ol>`.
- The current segment has `aria-current="page"`.

**Content rules:** segments are real names, not paths with slashes in them.

**Web:** `<nav class="p95-path" aria-label="Breadcrumb"><ol><li><a>Home</a></li>…</ol></nav>`.

**TUI:**
```
 Home / Pictures / ▐Screenshots▌
 ASCII:  Home / Pictures / [Screenshots]
```
**ratatui:** a `Line` of `Span`s.

---

### Command palette

**Purpose:** keyboard-first search across all commands and objects.

**Anatomy:** a dialog-like window at the top centre, containing a prompt field (`>`) and a results list. Each result is a label + shortcut, with matched characters marked.

| Part | Token |
|---|---|
| Window | `window.*`, layer `layer.dialog`. No scrim (it's non-modal) |
| Prompt | Command prompt (`text.secondary` `>`, `field.caret`) |
| Results | `list.*`. The highlighted result → `list.row-selected-bg` / `list.row-selected-fg` |
| Match chars | `text.hot` (inverted inside the highlighted row) |
| Shortcut | `menu.shortcut` |
| Group header | `type.label`, `text.secondary` |

| State | Change |
|---|---|
| typing | Results filter live. The first result is highlighted |
| empty | One line: `NO MATCHES` in `text.secondary` |

**Keyboard:**
- Ctrl+K or Ctrl+Shift+P opens the palette.
- ↑ and ↓ move, Enter runs, Esc closes.
- Typing `>` lists commands only, and `/` lists files only.

**Accessibility:**
- `role="combobox"` + `aria-controls` → `role="listbox"`, with `aria-activedescendant` tracking the highlighted result.
- The result count is announced politely.

**Content rules:** results are commands as verb + object ("Toggle CRT"). Show the shortcut whenever one exists.

**Web:** `<p95-palette>`.

**TUI:**
```
 ╔══════════════════════════════════╗
 ║ > crt█                           ║
 ║▐Toggle CRT              Ctrl+Alt+C▌║
 ║ CRT intensity…                    ║
 ╚══════════════════════════════════╝
```
**ratatui:** `Clear` + `Block` + a one-line input + `List`.

---

### Key-hint bar

**Purpose:** a persistent footer that lists the keys available now. It's essential in TUI, and useful in web kiosk UIs.

**Anatomy:** pairs of a key cap and a label, separated by two spaces.

| Part | Token |
|---|---|
| Bar | `statusbar.bg`, height `statusbar.height` |
| Key cap | `statusbar.key-bg` / `statusbar.key-fg` (inverted) |
| Label | `statusbar.fg` |
| Unavailable key | Hidden. Never show a disabled hint |

| State | Change |
|---|---|
| context change | The hints update with the focused pane or mode |

**Keyboard:** display only. Pressing the key does the action.

**Accessibility:**
- On the web, `<footer>` containing `<kbd>` elements.
- Hints duplicate shortcuts that must also be discoverable elsewhere (menus, help).

**Content rules:**
- Keys are written terminal-style: `^Q` for Ctrl+Q and `F1`. The web may write `Ctrl+Q`.
- Labels are one word in sentence case ("Quit"). Put the most important hint first.

**Web:** `<footer class="p95-keyhints"><kbd>F1</kbd> Help <kbd>^Q</kbd> Quit</footer>`.

**TUI:**
```
 ▐F1▌Help  ▐^S▌Save  ▐/▌Search  ▐^Q▌Quit
 ASCII:  [F1]Help  [^S]Save  [/]Search  [^Q]Quit
```
**ratatui:** a `Paragraph` with alternating key/label `Span`s, in the last row.
