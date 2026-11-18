# Inputs

Text field, textarea, select, checkbox, radio, switch, slider, spin box, search, command prompt.

Shared rules for this file:
- **Sunken well:** inputs sit in a sunken bevel, the reverse of Button. `bevel.shadow` / `bevel.dark` are on the top-left and `bevel.hi` / `bevel.light` on the bottom-right, with a `field.bg` well inside.
- **Focus:** shown by the dotted `focus.ring` plus the blinking block caret.
- **Invalid:** shown by `field.invalid-border` *and* a `[ERR ]` message underneath. Colour is never the only cue.

---

### Text field

**Purpose:** single-line text entry.

**Anatomy:**
1. Label (outside, above or to the left)
2. Sunken well
3. Value or placeholder
4. Block caret
5. Help or error line (below)

| Part | Token |
|---|---|
| Well | `field.bg`, bevel `bevel.*`, width `border.width.bevel` |
| Value | `field.text`, `type.ui` |
| Placeholder | `field.placeholder` (meets 4.5:1) |
| Caret | `field.caret`, a full cell `size.cell.width` × `size.cell.height`, blinking at `duration.blink` with `easing.steps` |
| Text selection | `field.selection-bg` / `field.selection-fg` |
| Size | height `field.height`, padding-x `field.padding-x` |
| Help line | `text.secondary`, `type.small` |
| Error line | `status.error.fg` with an `[ERR ]` prefix |

| State | Change |
|---|---|
| default | Sunken well, `field.text` |
| hover | No change. Fields don't glow on hover |
| focus | `focus.ring` inside the well, and the caret appears |
| disabled | Well → `field.bg-disabled`, text → `field.text-disabled`. edge style `disabled.border-style` (dashed in HC) |
| read-only | `field.bg-disabled`, text stays `field.text`, no caret |
| invalid | The outer bevel edge is replaced by 1px `field.invalid-border`, plus an `[ERR ]` line |

**Keyboard:** standard editing. Esc reverts an uncommitted edit, where the context supports it.

**Accessibility:**
- Use `<label for>` for the label.
- The help or error line is linked with `aria-describedby`.
- Invalid fields set `aria-invalid="true"`.
- A screen reader hears "Model endpoint, edit text, http://localhost…".

**Content rules:**
- Labels are nouns in sentence case: "Model endpoint".
- Placeholders show the format ("http://host:port") and never replace the label.
- Errors say what is wrong and how to fix it: `[ERR ] Port must be 1–65535.`

**Web:** use `<input class="p95-field">`. A bare `<input>` is styled by `base.css`.

**TUI:** the well is drawn with `▕` `▏` edges around an underscore run. When focused, the caret is a full `█` block in `field.caret`.
```
 Model endpoint
 ▕http://localhost:11434█____▏
 [ERR ] Port must be 1-65535.
 ASCII:  [http://localhost:11434_    ]
```
**ratatui:** a `Paragraph` inside a `Block` with `Borders::ALL`. Text-area crates (e.g. tui-textarea) take the `field.*` styles.

---

### Textarea

**Purpose:** multi-line text entry.

**Anatomy:** the same as Text field, plus a vertical [Scrollbar](containers.md#scrollbar) inside the well.

| Part | Token |
|---|---|
| All field parts | As Text field (`field.*`) |
| Line height | `font.line-height.cell` for code and logs, `font.line-height.prose` for prose |
| Scrollbar | `scrollbar.track`, `scrollbar.thumb`, `scrollbar.size` |

**States:** the same as Text field.

**Keyboard:**
- Enter inserts a newline.
- Ctrl+Enter submits, if the surrounding form defines a submit action.
- Tab moves focus out; it doesn't insert a tab unless the field is a code editor.

**Accessibility:** use `<textarea>` with a label. A character limit is announced through `aria-describedby`.

**Content rules:** the same as Text field.

**Web:** `<textarea class="p95-field">`.

**TUI:**
```
 ▕line one                  ▲▏
 ▕line two█                 ░▏
 ▕                          ▼▏
```
**ratatui:** a `Paragraph` with `Wrap`, plus a `Scrollbar`.

---

### Select / dropdown

**Purpose:** pick one option from a list.

**Anatomy:** a sunken well showing the value, a raised drop button with a `▼` arrow, and a popup list (styled as a Menu).

| Part | Token |
|---|---|
| Well and value | `field.bg`, `field.text` |
| Drop button | `button.face`, `bevel.*` |
| Popup | `menu.bg`, `menu.text`, items `menu.item-height`. Hovered or selected item → `menu.item-hover-bg` / `menu.item-hover-fg` |
| Popup layer | `layer.menu` |

| State | Change |
|---|---|
| focus | `focus.ring` around the value. The value is inverted (`select.bg` / `select.fg`), as in Win95 |
| open | Popup below. The drop button is sunken |
| disabled | `field.bg-disabled`, `field.text-disabled` |
| invalid | `field.invalid-border` plus an `[ERR ]` line |

**Keyboard:**
- Alt+↓ or F4 opens the popup.
- ↑ and ↓ change the value while closed, or move through the options while open.
- Enter selects, Esc closes, and typing jumps to an option.

**Accessibility:**
- Prefer a native `<select>`.
- A custom select uses `role="combobox"`, `aria-expanded` and `aria-controls`, with the popup as `role="listbox"`.
- A screen reader hears "Engine, combo box, local/qwen".

**Content rules:** options are short nouns, in a stable order (most-used first, or alphabetical).

**Web:** `<select class="p95-select">` (native). A custom select is `<p95-menu>` attached to a button.

**TUI:**
```
 Engine ▕local/qwen     [▼]▏
        ┌────────────────┐
        │▐local/qwen    ▌│   ← inverted = highlighted
        │ remote/claude  │
        └────────────────┘
 ASCII:  Engine [local/qwen  v]
```
**ratatui:** a `List` inside a `Block`, rendered over a `Clear`.

---

### Checkbox

**Purpose:** an independent on/off choice, or a mixed state for parent options.

**Anatomy:** a 16px sunken box (`check.size`), the mark (✓, or – for mixed), and a label to the right.

| Part | Token |
|---|---|
| Box | `check.bg`, sunken `bevel.*` |
| Mark | `check.mark` · disabled `check.mark-disabled` |
| Label | `text.primary` · disabled `text.disabled` |
| Size | `check.size`, gap `space.8` |

| State | Change |
|---|---|
| hover | Label → `text.hot` |
| pressed | Box → `surface.face-pressed` |
| focus | `focus.ring` around the **label**, as in Win95 |
| checked / mixed | Mark drawn |
| disabled | `check.mark-disabled`, `text.disabled`. edge style `disabled.border-style` (dashed in HC) |

**Keyboard:** Space toggles.

**Accessibility:**
- Native `<input type="checkbox">`. The mixed state is set with `indeterminate`.
- A screen reader hears "Log to disk, checkbox, not checked".

**Content rules:** the label is a positive statement ("Stream tokens"), never a double negative.

**Web:** `<label class="p95-check"><input type="checkbox"> Stream tokens</label>`.

**TUI:**
```
 [x] Stream tokens   [ ] Log to disk   [-] Some models
 ASCII: same (pure ASCII already)
```
**ratatui:** a `Span` per item, in a `List` or `Paragraph`.

---

### Radio

**Purpose:** one choice out of a small set (2–6 options).

**Anatomy:** a 16px sunken pixel circle, a dot, and a label.

| Part | Token |
|---|---|
| Circle | `check.bg`, edges `bevel.*` (stair-stepped, no antialiasing) |
| Dot | `check.mark` · disabled `check.mark-disabled` |
| Label and size | As Checkbox |

**States:** the same as Checkbox. A selected radio shows its dot.

**Keyboard:**
- Tab enters the group, landing on the selected option.
- Arrow keys move the selection and select as they move.

**Accessibility:**
- Native `<input type="radio">` inside a `<fieldset>` with a `<legend>`.
- A screen reader hears "Text, radio button, 2 of 2, selected".

**Content rules:** options are parallel in grammar. Order them by frequency or by magnitude.

**Web:** `<label class="p95-radio"><input type="radio" name="mode"> Text</label>`.

**TUI:**
```
 (•) Text   ( ) Voice          ASCII: (*) Text  ( ) Voice
```
**ratatui:** a `Span` per option.

---

### Switch

**Purpose:** an immediate on/off setting, applied with no Apply button. If the change needs confirming, use a Checkbox instead.

**Anatomy:** a two-cell segmented track (off | on) with the active half filled, and a label.

| Part | Token |
|---|---|
| Track | Sunken `bevel.*` around the track. Off half `check.switch-off-bg`, on half `check.switch-on-bg` |
| Thumb text | Active half shows `text.inverse` on `check.switch-on-bg`. Inactive half shows `text.secondary` |
| Size | Height `size.control.sm`, each half `check.switch-segment-width` wide |

| State | Change |
|---|---|
| off / on | The fill moves to the active half |
| focus | `focus.ring` around the track |
| disabled | Fill → `surface.selected-subtle`, labels → `text.disabled` |

**Keyboard:** Space toggles.

**Accessibility:**
- `<button role="switch" aria-checked>`, or `<input type="checkbox" role="switch">`.
- A screen reader hears "Voice, switch, on".

**Content rules:** the label names the setting. The track shows `I` / `O` or `ON` / `OFF`, in uppercase.

**Web:** `<button class="p95-switch" role="switch" aria-checked="false">`.

**TUI:**
```
 Voice [▐ON ▌ OFF]        ← ON inverted
 ASCII: Voice [*ON* off]
```
**ratatui:** a `Line` of two `Span`s.

---

### Slider

**Purpose:** choose a value in a range, where the approximate value matters more than the exact one. Pair it with a Spin box when precision matters.

**Anatomy:** a sunken track 4px tall, a fill from min to the value, a raised thumb (a bevelled block one cell wide), optional ticks, and a value label.

| Part | Token |
|---|---|
| Track | `slider.track`, sunken `bevel.*`, height `slider.track-height` |
| Fill | `slider.fill` |
| Thumb | `button.face` with a raised `bevel.*`, `size.cell.width` × `size.control.sm` |
| Value label | `text.secondary`, `type.small`. While dragging → `text.hot` |
| Ticks | `border.default` |

| State | Change |
|---|---|
| hover | Thumb → `button.face-hover` |
| dragging | Thumb sunken (`button.face-pressed`), value label `text.hot` |
| focus | `focus.ring` around the thumb |
| disabled | Fill → `surface.selected-subtle`, thumb label `button.text-disabled` |

**Keyboard:**
- ← and → step the value; PgUp and PgDn take big steps.
- Home and End jump to min and max.

**Accessibility:**
- Native `<input type="range">`. Use `aria-valuetext` for units, e.g. "62 percent".
- A screen reader hears "Temperature, slider, 62".

**Content rules:** show the unit in the value label. Label the ends of the track when they mean something ("Precise" … "Creative").

**Web:** `<input type="range" class="p95-slider">`.

**TUI:**
```
 Temperature  ━━━━━━━━━━━━━━━█───────  62
 ASCII:       =============#-------  62
```
**ratatui:** a `Gauge` or `LineGauge` (`slider.fill` on `slider.track`) with a thumb `Span`.

---

### Spin box

**Purpose:** exact numeric entry with step buttons.

**Anatomy:** a sunken field, plus "−" and "+" icon buttons (or stacked ▲▼ buttons).

| Part | Token |
|---|---|
| Field | `field.*` |
| Step buttons | `button.*`, `bevel.*` (Icon button) |

**States:** the field states plus the button states. At min or max, the matching step button is disabled.

**Keyboard:**
- ↑ and ↓ step the value; PgUp and PgDn take big steps.
- Typing is allowed, and the value is validated on blur.

**Accessibility:**
- `<input type="number">`, or `role="spinbutton"` with `aria-valuemin`, `aria-valuemax` and `aria-valuenow`.
- The step buttons have `aria-label` "Decrease" and "Increase", and `tabindex="-1"`.

**Content rules:** show the unit next to the field ("ms"), not inside it.

**Web:** `<div class="p95-spin"><input type="number" class="p95-field"><button aria-label="Decrease">−</button><button aria-label="Increase">+</button></div>`.

**TUI:**
```
 Threads ▕   4 ▏[-][+]          ASCII: Threads [   4 ][-][+]
```
**ratatui:** `Paragraph` and `Span`s.

---

### Search

**Purpose:** filter or find within the current view.

**Anatomy:** a Text field with a leading 16px search icon and a trailing clear button (✕) shown when it has a value. It can show a results count.

| Part | Token |
|---|---|
| Field | `field.*` |
| Icon | `text.secondary` |
| Clear button | Icon button, flat variant |
| Count | `text.secondary`, `type.small` |
| Match highlight in results | `select.bg` / `select.fg` |

**States:** the same as Text field. "No results" shows the empty-state line in `text.secondary`.

**Keyboard:**
- `/` or Ctrl+F focuses search.
- Esc clears; a second Esc blurs.
- Enter jumps to the first result. F3 or Enter moves to the next.

**Accessibility:**
- `<input type="search">` inside `role="search"`.
- The count is announced through an `aria-live="polite"` region: "3 matches".

**Content rules:** the placeholder is "Search logs" (verb + scope). Counts read "3 MATCHES" or "NO MATCHES".

**Web:** `<div role="search" class="p95-search"><input type="search" class="p95-field" placeholder="Search logs"></div>`.

**TUI:**
```
 /error█                         3 MATCHES
 ASCII: same
```
**ratatui:** a single-line `Paragraph` in the footer, as less and vim do.

---

### Command prompt

**Purpose:** free-text command entry in the terminal style. It's the TERMINAL-01 input line, and a web console.

**Anatomy:** the prompt glyph `>` (or a host prefix), the input text, the blinking block caret, an optional ghost suggestion, and the history.

| Part | Token |
|---|---|
| Line | Background `surface.base`, no bevel. It's the terminal itself |
| Prompt glyph | `text.secondary`. The `>` turns `text.hot` while busy or listening |
| Input | `text.primary`, `type.code` |
| Caret | `field.caret`, full block, blink `duration.blink` |
| Ghost suggestion | `text.secondary` |
| Typed-out replies | Revealed at `duration.type` per character |

| State | Change |
|---|---|
| idle | `> ` and the blinking caret |
| typing | Caret steady (doesn't blink while keys are coming in) |
| busy | Prompt replaced by a Spinner, and input disabled (`text.disabled`) |
| error | The reply line gets an `[ERR ]` prefix in `status.error.fg` |

**Keyboard:**
- Enter submits.
- ↑ and ↓ move through history.
- Tab or → accepts the suggestion.
- Ctrl+C cancels and Ctrl+L clears.

**Accessibility:**
- `<input>` with `aria-label="Command"`. The output region is `role="log"` with `aria-live="polite"`.
- Respect `prefers-reduced-motion`: replies appear at once and the caret doesn't blink.

**Content rules:** the prompt is `>`. Echoed system replies use the boot-line format (see [feedback.md](feedback.md#boot-line)).

**Web:** `<p95-prompt>`, a web component that wraps `<input>` and the log region.

**TUI:**
```
 > status█
 [ OK ] TERMINAL-01 ONLINE // 12% CPU
 > _
```
**ratatui:** a `Paragraph` for the history, plus a one-line input area.
