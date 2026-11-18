# Data

List, table, tree, key-value list, log viewer, code block, diff.

Shared rules for this file:
- **Bodies:** data bodies sit in a **sunken base well** (`list.bg` with sunken `bevel.*`).
- **Selection:** selected rows are inverted. Unfocused selection drops to `list.row-selected-inactive-*`.
- **Type:** tabular text uses `type.code` (monospace, so columns align). Prose cells use `type.ui`.

---

### List

**Purpose:** a vertical collection of selectable items.

**Anatomy:** a sunken well, rows (an optional 16px icon, the primary label and an optional secondary text), and a Scrollbar.

| Part | Token |
|---|---|
| Well | `list.bg`, sunken `bevel.*` |
| Row | `list.text`, height `list.row-height`, padding-x `list.cell-padding-x` |
| Secondary text | `text.secondary`. On a hovered or selected row it changes to that row's foreground |
| Zebra (optional) | `list.row-alt-bg` |
| Hover | `list.row-hover-bg`, and the text brightens to `text.primary` |
| Selected, focused | `list.row-selected-bg` / `list.row-selected-fg` |
| Selected, unfocused | `list.row-selected-inactive-bg` / `list.row-selected-inactive-fg` |
| Focus | `focus.ring` around the focused row (it may be unselected in multi-select) |

| State | Change |
|---|---|
| hover / selected / focus | See the table above |
| disabled row | `text.disabled`, not selectable |
| empty | Empty state: one line in `text.secondary`, or the Operator (see [feedback.md](feedback.md#empty-state)) |
| loading | Spinner row: `[ .. ] LOADING` |

**Keyboard:**
- ↑ and ↓ move; Home, End, PgUp and PgDn jump.
- Typing jumps to the first match.
- Space toggles selection in multi-select. Shift+arrows extend the selection, and Ctrl+A selects all.
- Enter opens the item.

**Accessibility:**
- `role="listbox"` with `role="option"` + `aria-selected` for a selection list. A plain `<ul>` for a static list.
- A screen reader hears "llama3-8b, 2 of 4, selected".

**Content rules:** primary labels identify the item, and secondary text adds one fact. No trailing punctuation.

**Web:** `<ul class="p95-list" role="listbox">` with `<li role="option">` items.

**TUI:**
```
 ▕ qwen2.5-7b            ▏
 ▕▐llama3-8b            ▌▏   ← selected (inverted)
 ▕ claude                ▏
 ASCII: '>' marker on the selected row:  > llama3-8b
```
**ratatui:** `List` with `highlight_style` set to `select.*` and `highlight_symbol(">")` for the ASCII/mono ladder.

---

### Table

**Purpose:** rows of records with aligned columns.

**Anatomy:**
- Header row: raised header buttons, sortable with a ▲/▼ glyph.
- Header rule.
- Body rows with cells.
- Column resize handles.
- Optional status column.

| Part | Token |
|---|---|
| Header | `list.header-bg` / `list.header-fg`, raised `bevel.*` per header cell |
| Header rule | `list.header-rule` |
| Body | As List (`list.*`) |
| Cell | padding-x `list.cell-padding-x`, height `list.row-height`. Numbers are right-aligned in `type.code` |
| Sort glyph | `text.secondary`. On the active sort column → `text.primary` |
| Status cell | Status tag (`status.*.fg` + text cue) |

| State | Change |
|---|---|
| header hover | `button.face-hover` |
| header pressed (sort) | Sunken. The glyph flips |
| row states | As List |
| cell focus (grid mode) | `focus.ring` around the cell |

**Keyboard:**
- Row mode works as List.
- Grid mode uses arrows by cell; Enter edits and Esc cancels.
- Tab moves to the header controls.

**Accessibility:**
- A native `<table>` with `<th scope="col">` and `aria-sort` on the sorted header.
- An interactive grid uses `role="grid"`.
- A screen reader hears "State, column header, sorted ascending".

**Content rules:**
- Headers are short nouns in sentence case.
- Status values are uppercase single words (`ONLINE`, `STANDBY`, `OFFLINE`).
- Empty cells show `—`, never blank.

**Web:** `<table class="p95-table">`. Sortable headers contain `<button>`.

**TUI:**
```
 Model         State
 ━━━━━━━━━━━━━━━━━━━━━━━━
 qwen2.5-7b    ONLINE
▐llama3-8b     STANDBY  ▌
 phi-3         OFFLINE
 ASCII: header rule '====', selected row '>' prefix
```
**ratatui:** `Table` with `header` styled `list.header-*` + `Modifier::BOLD` off (pixel fonts have no bold), and `row_highlight_style` set to `select.*`.

---

### Tree

**Purpose:** a hierarchical list (files, settings, JSON).

**Anatomy:** each row has indent guides, a disclosure glyph (▶/▼, or `+`/`-`), an optional icon and a label.

| Part | Token |
|---|---|
| Rows | As List (`list.*`) |
| Indent | `list.indent` per level |
| Guides | `list.guide` (1px dotted, as in Win95) |
| Disclosure glyph | `text.secondary` |

| State | Change |
|---|---|
| expanded / collapsed | The glyph changes. Children appear instantly |
| other states | As List |

**Keyboard:**
- → expands a node, or moves to its first child if already expanded.
- ← collapses a node, or moves to its parent if already collapsed.
- `*` expands all siblings. Otherwise it works as List.

**Accessibility:**
- `role="tree"` / `role="treeitem"`, with `aria-expanded` and `aria-level`.
- A screen reader hears "Pictures, expanded, level 2".

**Content rules:** labels are names only. Show counts as secondary text ("Screenshots  3").

**Web:** `<ul class="p95-tree" role="tree">`.

**TUI:**
```
 ▼ Home
 │ ├─ Documents
 │ └▐▼ Pictures      ▌
 │     └─ Screenshots
 ASCII: v Home / |-- Documents / `-- Pictures
```
**ratatui:** a `List` built from the flattened visible nodes, with box-drawing prefixes.

---

### Key-value list

**Purpose:** read-only properties: system info, details panes, fastfetch-style readouts.

**Anatomy:** rows of a key (right-aligned or fixed-width) and a value. Optional group headings.

| Part | Token |
|---|---|
| Key | `text.secondary`, `type.label` (uppercase) |
| Value | `text.primary`, `type.code` |
| Separator | None (alignment does the work), or ` // ` inline |
| Group heading | `text.hot`, `type.label` |
| Row gap | `space.4` |

**States:** static. A copyable value shows a copy icon button on hover.

**Keyboard:** none, unless values are links or copyable.

**Accessibility:** `<dl>` with `<dt>`/`<dd>` pairs.

**Content rules:** keys are uppercase nouns (`HOST`, `UPTIME`). Values are exact, with units (`8 GB`, `1440x900`).

**Web:** `<dl class="p95-kv">`.

**TUI:**
```
      HOST  terminal-01
    UPTIME  3h 12m
       GPU  Intel HD 6000
```
**ratatui:** a `Table` with two columns, no borders, and the key column styled `text.secondary`.

---

### Log viewer

**Purpose:** a stream of timestamped lines: the terminal01 JSONL logs, boot output, build logs.

**Anatomy:** a sunken well of lines, each with a timestamp, a level tag, a source and a message. A follow toggle and a search sit in the header.

| Part | Token |
|---|---|
| Well | `surface.base`, sunken `bevel.*`. No zebra |
| Timestamp | `text.secondary`, `type.code` |
| Level tag | Status tag: `[ OK ]` `status.ok.fg`, `[INFO]` `status.info.fg`, `[WARN]` `status.warn.fg`, `[ERR ]` `status.error.fg` |
| Message | `text.primary`, `type.code`, no wrapping (scroll horizontally), or wrap with a hanging indent |
| New-line arrival | The newest line glows in `glow.hot`, decaying over `duration.decay` (off with reduced motion) |
| Search match | `select.bg` / `select.fg` |

| State | Change |
|---|---|
| following | Auto-scroll to the end. The header toggle shows `FOLLOW` inverted |
| paused (user scrolled up) | Follow off. A `▼ 12 NEW` button appears |

**Keyboard:**
- `f` or End resumes following.
- `/` searches; `n` and `N` move to the next and previous match.
- Space pages down.

**Accessibility:**
- `role="log"` with `aria-live="polite"`. When the stream is fast, throttle announcements to errors only.

**Content rules:**
- Messages in the machine voice: present tense, no trailing period.
- Error lines carry what, why and fix when known (see Content rules in [feedback.md](feedback.md#boot-line)).

**Web:** `<pre class="p95-log" role="log">`, one `<span>` per line.

**TUI:**
```
 18:29:04 [ OK ] wake    heard "hey terminal"
 18:29:05 [INFO] stt     0.61s base.en
 18:29:06 [WARN] thermal 95°C
 18:29:07 [ERR ] brain   no reply from node-01 // retrying in 5s
```
**ratatui:** a `Paragraph` built from `Line`s with `scroll()`, plus a `Scrollbar`.

---

### Code block

**Purpose:** shows source code, commands or config, with optional copy and line numbers.

**Anatomy:** a sunken well, an optional language label tab, an optional gutter of line numbers, the code, and a copy button.

| Part | Token |
|---|---|
| Well | `surface.base`, sunken `bevel.*`, padding `space.8` |
| Code | `text.primary`, `type.code` |
| Gutter | `text.secondary`, right rule `border.subtle` |
| Syntax: keyword / string / number / comment | `code.keyword` / `code.string` / `code.number` / `code.comment` on `code.bg`. A mostly-monochrome palette with brightness steps, matching the ANSI map |
| Language label | `type.label`, `text.secondary` |
| Copy button | Icon button (flat). After copying it shows `[ OK ] COPIED` for `duration.slow` |
| Selection | `select.bg` / `select.fg` |

**States:** static. Hovering the block reveals the copy button.

**Keyboard:** the copy button is a Tab stop. The code itself is selectable text.

**Accessibility:**
- `<pre><code>`. Line numbers are excluded from copying (`user-select: none`) and hidden from AT.

**Content rules:** shell commands have no `$ ` prompt (so they copy cleanly). Show output in a separate block, or as a comment.

**Web:** `<pre class="p95-code"><code>…</code></pre>`.

**TUI:** the code prints as plain ANSI-coloured lines, indented 2 spaces, with no frame (so it copies cleanly).
```
   python3 tools/build.py --check
```
**ratatui:** a `Paragraph` with styled `Span`s.

---

### Diff

**Purpose:** shows changes between two versions of text.

**Anatomy:**
- Hunk header.
- Lines, each with a `+`, `-` or space marker. The gutter shows old and new line numbers.
- Optional intraline highlights.

| Part | Token |
|---|---|
| Added line | Marker `+` and text `diff.added-fg`. Background `diff.added-bg`. In TUI, `ansi.green` |
| Removed line | Marker `-` and text `diff.removed-fg`. Background `diff.removed-bg` |
| Context line | `text.secondary` |
| Hunk header | `text.link`, `type.code` |
| Intraline change | Inverted: `diff.added-intraline-fg` on `diff.added-intraline-bg`; `diff.removed-intraline-fg` on `diff.removed-intraline-bg` |
| Gutter | `text.secondary`, rule `border.subtle` |

**States:** static. Hunks can collapse like an accordion.

**Keyboard:** `n` and `p` move to the next and previous hunk.

**Accessibility:**
- **Colour is not the cue: the `+`/`-` markers are mandatory.** On the web, wrap lines in `<ins>`/`<del>`, which screen readers announce.

**Content rules:** —

**Web:** `<pre class="p95-diff">`, with `<ins>` and `<del>` lines.

**TUI:**
```
 @@ -12,3 +12,4 @@
   [identity]
 - name = "TERMINAL-01"
 + name = "PHOSPHOR95"
```
**ratatui:** a `Paragraph` of `Line`s styled per marker. In mono mode, the markers alone carry the meaning.
