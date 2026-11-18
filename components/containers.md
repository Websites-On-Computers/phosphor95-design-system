# Containers

Window, dialog, panel, group box, tabs, accordion, split pane, card/frame, scrollbar.

Shared rule for this file: containers separate regions with bevels and rules, never with shadows or rounded corners. Elevation is the stacking order (`layer.*`) plus the inverted active title bar.

---

### Window

**Purpose:** a movable, titled region. It's the primary unit of a desktop-style app.

**Anatomy:**
1. 2px raised outer bevel
2. Title bar: 16px icon, title, and min, max and close controls
3. Optional menubar
4. Client area
5. Optional status bar

| Part | Token |
|---|---|
| Frame | `window.bg`, raised `bevel.*`, width `border.width.bevel` |
| Title bar, active | `window.titlebar.active-bg` / `window.titlebar.active-fg` |
| Title bar, inactive | `window.titlebar.inactive-bg` / `window.titlebar.inactive-fg` |
| Title bar height | `window.titlebar.height` |
| Title text | `type.label` (uppercase is fine for system windows; documents keep their real name) |
| Controls | Icon buttons at `window.control-size` (`button.*`) |
| Client area | `window.client-bg` for document or list content, `window.bg` for form content |
| Padding | `window.padding` |
| Layer | `layer.raised`. The focused window is raised above siblings |

| State | Change |
|---|---|
| active | Inverted title bar (phosphor fill, void text). Frame edge `border.strong` |
| inactive | Title bar → `window.titlebar.inactive-*`. Content unchanged |
| maximised | Bevel hidden at the screen edges. The max control shows the restore glyph |
| moving | Outline-only drag in `border.focus`, 1px dotted. No live content drag on slow GPUs |

**Keyboard:**
- Alt+F4 or Ctrl+W closes.
- Alt+Space opens the window menu, when there is one.
- F6 cycles between panes inside the window.

**Accessibility:**
- On the web the window is a region: `<section aria-labelledby="title-id">`.
- Title-bar controls are buttons with labels ("Minimise", "Maximise", "Close").

**Content rules:**
- Titles name the object, then the app: "New Document — Notes".
- System windows use uppercase dotted names: `SYS.TERMINAL — Properties`.

**Web:** `<section class="p95-window" data-active>`, with `<header class="p95-titlebar">` and `<div class="p95-window-body">`.

**TUI:**
- **Active:** a double-line `╔═╗` frame with the title inverted inside the top edge, and the controls at the right of that edge.
- **Inactive:** a single-line `┌─┐` frame with the title in `title.inactive.fg`.

```
 ╔▐ SYS.TERMINAL — Properties ▌═════════[_][□][x]╗
 ║ Model endpoint ▕http://localhost:11434    ▏   ║
 ╚═══════════════════════════════════════════════╝
 ASCII:  +=[ SYS.TERMINAL ]==============[_][#][x]+
```
**ratatui:** a `Block` with `BorderType::Double` when focused and `Plain` otherwise. The title goes in `Block::title` with the title style.

---

### Dialog

**Purpose:** a modal window that asks for a decision or input. For a notice the user doesn't have to act on, use a [Toast](feedback.md#toast--notification).

**Anatomy:** a Window without min/max controls (close only), centred, over the `surface.overlay` scrim. It has a body and a right-aligned button row: default button first, Cancel last.

| Part | Token |
|---|---|
| Window parts | As Window (`window.*`) |
| Scrim | `surface.overlay` |
| Layer | `layer.dialog` |
| Button row | `button.gap` between buttons. Top rule `border.subtle`. Padding `space.8` |

| State | Change |
|---|---|
| open | Appears instantly (`duration.instant`), optionally with a `duration.tick` stepped reveal. No zoom or fade |
| busy | Buttons disabled, Spinner in the body |

**Keyboard:**
- Focus moves into the dialog on open and is trapped there.
- Enter activates the default button and Esc activates Cancel.
- Focus returns to the invoking control on close.

**Accessibility:**
- Native `<dialog>` opened with `showModal()`, with `aria-labelledby` (the title) and `aria-describedby` (the body).
- A screen reader hears "Unlock disk, dialog".

**Content rules:**
- Title: a short uppercase system phrase ("UNLOCK DISK"), or a question.
- Body: one or two sentences.
- Buttons: verbs ("Delete log", "Cancel"), never "Yes/No".

**Web:** `<p95-dialog>` wraps a native `<dialog class="p95-window">`.

**TUI:** a centred `╔═╗` window over a dimmed screen. When drawn, the background is redrawn in `text.disabled`.
```
        ╔▐ UNLOCK DISK ▌═════════════╗
        ║ ENTER PASSPHRASE:          ║
        ║ ▕●●●●●●●●●█        ▏       ║
        ║          «[ OK ]» [Cancel] ║
        ╚════════════════════════════╝
```
**ratatui:** `Clear` + `Block` + `Paragraph`, in a centred `Rect`.

---

### Panel

**Purpose:** a raised or sunken area inside a window that groups content, like a sidebar or toolbar.

**Anatomy:** a bevel (raised for toolbars and sidebars, sunken for content wells) and the content.

| Part | Token |
|---|---|
| Raised panel | `surface.face`, raised `bevel.*` |
| Sunken panel (well) | `surface.base`, sunken `bevel.*` |
| Padding | `space.8` |

**States:** static. A focus-within panel may draw its outer edge in `border.strong`.

**Keyboard:** none of its own. F6 moves between panels.

**Accessibility:** a `<div>`, or a landmark (`<aside>`, `<nav>`) when it holds navigation.

**Content rules:** —

**Web:** `<div class="p95-panel" data-variant="sunken">`.

**TUI:**
```
 ┌───────────┐       ASCII: +-----------+
 │ panel     │              | panel     |
 └───────────┘              +-----------+
```
**ratatui:** a `Block` with `Borders::ALL`. A sunken well may use the `▕▏` half-block edges.

---

### Group box (fieldset)

**Purpose:** labels a group of related controls, like the "Models" group in the properties dialog.

**Anatomy:** an etched 2px frame and a legend inset on the top edge.

| Part | Token |
|---|---|
| Etched frame | Outer `bevel.shadow`, inner `bevel.light` (a 1px pair) |
| Legend | `text.primary`, `type.ui`, background `surface.face` |
| Padding | `space.8`, with `space.16` above the content |

**States:** disabled → legend `text.disabled`, and every child disabled.

**Keyboard:** none.

**Accessibility:**
- `<fieldset>` with a `<legend>`. A screen reader announces "Models, group" when entering it.

**Content rules:** the legend is a short noun in sentence case.

**Web:** native `<fieldset class="p95-group"><legend>Models</legend>…</fieldset>`.

**TUI:**
```
 ┌─ Models ───────────────┐      ASCII: +- Models --------+
 │ qwen2.5-7b   ONLINE    │             | ...             |
 └────────────────────────┘             +-----------------+
```
**ratatui:** a `Block` with a title and `Borders::ALL`.

---

### Tabs

**Purpose:** switch between peer views inside one container.

**Anatomy:**
1. Tab strip
2. Raised tabs. The active tab is taller, joined to the page, with no bottom edge.
3. Page: a raised panel.

| Part | Token |
|---|---|
| Active tab | `tabs.active-bg` / `tabs.active-fg` |
| Inactive tab | `tabs.inactive-bg` / `tabs.inactive-fg` |
| Height | `tabs.height` (active +2px) |
| Edges | Raised `bevel.*` on the top, left and right |
| Page | `surface.face`, raised `bevel.*` |

| State | Change |
|---|---|
| hover (inactive) | Label → `text.primary` |
| active | Joined to the page, label `tabs.active-fg` |
| focus | `focus.ring` around the active tab's label |
| disabled | Label `text.disabled` |

**Keyboard:**
- ← and → move between tabs. Selection follows focus unless the page is expensive to render.
- Ctrl+Tab and Ctrl+PgDn cycle tabs.
- Home and End jump to the first and last tab.

**Accessibility:**
- `role="tablist"` with `role="tab"` / `aria-selected` on each tab, and `role="tabpanel"` with `aria-labelledby` on the page.
- A screen reader hears "Network, tab, 2 of 3".

**Content rules:** one or two words in sentence case, and no counts in the label.

**Web:** `<p95-tabs>` with `<button role="tab">` children and `<section role="tabpanel">` pages.

**TUI:**
```
 ┌─────────┐┌─────────┐┌─────────┐
 │▐General▌│ Network  │ Display  │
 ┘         └──────────┴──────────┴────
 ASCII:  [*General*] [ Network ] [ Display ]
```
**ratatui:** `Tabs`, with the highlight style set to `select.bg` / `select.fg`.

---

### Accordion

**Purpose:** collapsible sections for long settings pages, or details on demand.

**Anatomy:** a header row (a disclosure glyph ▶/▼ and a title) and the body.

| Part | Token |
|---|---|
| Header | `surface.face`, `text.primary`, height `size.control.sm` |
| Header hover | `surface.face-hover`, `text.hot` |
| Glyph | `text.secondary`. When expanded → `text.primary` |
| Body | `surface.face`, padding `space.8`, top rule `border.subtle` |

| State | Change |
|---|---|
| collapsed / expanded | Glyph ▶ / ▼. The body appears instantly, with no height animation |
| focus | `focus.ring` around the header |
| disabled | Header `text.disabled` |

**Keyboard:** Enter or Space toggles the section. ↑ and ↓ move between headers.

**Accessibility:**
- Prefer `<details>`/`<summary>`.
- A custom accordion uses a button with `aria-expanded` and `aria-controls`.

**Content rules:** header text is a noun phrase in sentence case.

**Web:** `<details class="p95-accordion"><summary>Advanced</summary>…</details>`.

**TUI:**
```
 ▼ Advanced            ASCII: v Advanced
   Threads  4                    Threads  4
 ▶ Logging                     > Logging
```
**ratatui:** `List` or `Paragraph` rows, with the expansion state in the app.

---

### Split pane

**Purpose:** two resizable regions, like a sidebar and content, or a log and a detail view.

**Anatomy:** pane A, a splitter (4px, raised), and pane B.

| Part | Token |
|---|---|
| Splitter | `split.handle`, raised `bevel.*`, width `split.handle-size` |
| Splitter hover / drag | `split.handle-hover`. While dragging, a 1px dotted outline in `border.focus` |

| State | Change |
|---|---|
| hover | Resize cursor. Splitter `split.handle-hover` |
| focus | `focus.ring` on the splitter |
| collapsed | One pane hidden. The splitter stays as a 4px edge you can grab |

**Keyboard:**
- F6 moves focus between panes.
- With the splitter focused, ← and → resize, and Enter collapses or restores.

**Accessibility:**
- The splitter is `role="separator"` with `aria-orientation`, `aria-valuenow` (in percent) and `tabindex="0"`.

**Content rules:** —

**Web:** `<div class="p95-split"><div>…</div><div class="p95-splitter" role="separator" tabindex="0"></div><div>…</div></div>`.

**TUI:** a single `│` column between panes. The focused pane's border is double.
```
 ╔═ Models ═══╗┌─ Detail ────────────┐
 ║▐qwen2.5  ▌ ║│ ctx 32k  q4_k_m     │
 ╚════════════╝└─────────────────────┘
```
**ratatui:** `Layout` with `Constraint::Percentage`. Each pane is its own `Block`.

---

### Card / frame

**Purpose:** a self-contained summary unit in a grid, like a model card or the docs gallery tiles. It's the Win95 "frame": no shadow, just a bevel.

**Anatomy:** a raised frame, an optional inverted header strip (a mini title bar), the body, and optional actions.

| Part | Token |
|---|---|
| Frame | `surface.face`, raised `bevel.*` |
| Header strip | `title.inactive.bg` / `title.inactive.fg`. When the card is selected or focused → `title.active.bg` / `title.active.fg` |
| Body | `type.body`, padding `space.8` |
| Selected | Header inverted, plus a `border.strong` edge |

| State | Change |
|---|---|
| hover | Header text → `text.hot` |
| focus | `focus.ring` inside the frame |
| selected | Header → `title.active.*` |

**Keyboard:** a clickable card is a single link or button. Its inner actions are reachable by Tab.

**Accessibility:** use `<article>` with a heading. Don't nest interactive elements inside a clickable card's link.

**Content rules:** the header is the object's name, in uppercase when it's a system identifier (`QWEN2.5-7B`).

**Web:** `<article class="p95-card">`, with `<header class="p95-card-head">` inside.

**TUI:**
```
 ┌▐ QWEN2.5-7B ▌──────┐      ASCII: +[ QWEN2.5-7B ]----+
 │ ONLINE  32k ctx    │             | ONLINE  32k ctx  |
 └────────────────────┘             +------------------+
```
**ratatui:** a `Block` with a styled title and a `Paragraph`.

---

### Scrollbar

**Purpose:** shows the scroll position and length, and lets you drag to scroll. It appears only when content overflows.

**Anatomy:**
1. Track: a dithered `░` pattern, as in Win95
2. Thumb: raised
3. Arrow buttons: icon buttons at each end

| Part | Token |
|---|---|
| Track | `scrollbar.track`. Dither pixels in `surface.face` |
| Thumb | `scrollbar.thumb`, raised `bevel.*` |
| Arrows | Icon buttons (`button.*`) |
| Size | `scrollbar.size` |

| State | Change |
|---|---|
| hover (thumb) | `surface.face-hover` |
| dragging | Thumb sunken (`surface.face-pressed`) |
| disabled (no overflow) | Hidden. Don't render an inert scrollbar |

**Keyboard:** handled by the scroll container (arrows, PgUp/PgDn, Home/End). The scrollbar itself isn't focusable.

**Accessibility:** native scrolling. A custom scrollbar is presentational only.

**Content rules:** —

**Web:** styled with `scrollbar-color` and `::-webkit-scrollbar` in `components.css`, class `.p95-scroll`.

**TUI:**
```
 ▲
 █   ← thumb
 ░
 ░
 ▼        ASCII: ^ # | | v
```
**ratatui:** `Scrollbar` with `ScrollbarOrientation::VerticalRight`, track symbol `░`, thumb `█`.
