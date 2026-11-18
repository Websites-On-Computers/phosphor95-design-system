# Actions

Buttons, icon buttons, toggle buttons, links. The spec template is explained in [README.md](README.md).

Shared rules for this file:
- **Raised bevel:** `bevel.hi` / `bevel.light` on the top-left, `bevel.dark` / `bevel.shadow` on the bottom-right, `border.width.bevel` (2px) in total.
- **Pressed:** the bevel turns sunken, the face becomes `button.face-pressed`, and the content shifts 1px right and 1px down.
- **Focus:** the `focus.ring` dotted rectangle, drawn `focus.inset` inside the bevel (4px from the outer edge).
- **Shape:** radius is `border.radius.none`, and there are no shadows.

---

### Button

**Purpose:** triggers an action. There are three variants:
- **default:** raised.
- **primary:** solid phosphor. Use one per view, for the main action.
- **flat:** the toolbar variant. No bevel until hovered.

**Anatomy:**
1. Bevel (2px)
2. Face
3. Label (with an optional 16px leading icon)
4. Focus ring
5. Default-frame. This is an extra 1px outer frame on the button that Enter activates.

| Part | Token |
|---|---|
| Face | `button.face` · hover `button.face-hover` · pressed `button.face-pressed` |
| Label | `button.text` · hover `button.text-hover` · disabled `button.text-disabled` |
| Bevel | `bevel.hi`, `bevel.light`, `bevel.shadow`, `bevel.dark`, width `border.width.bevel` |
| Default-frame | `button.frame-default`, width `border.width.hair` |
| Primary | face `button.primary.face` · hover `button.primary.face-hover` · label `button.primary.text` |
| Focus | `focus.ring` (colour `border.focus`) |
| Size | height `button.height`, min-width `button.min-width`, padding-x `button.padding-x`, gap between buttons `button.gap` |
| Type | `type.ui`. Labels in system dialogs use `type.label` (uppercase) |

| State | Change |
|---|---|
| default | Raised bevel, `button.face`, `button.text` |
| hover | Face → `button.face-hover`, label → `button.text-hover` (glow means hot). Flat variant: the bevel appears |
| pressed | Sunken bevel, face → `button.face-pressed`, content +1px x/y |
| focus | Dotted `focus.ring` inside the face. Also shows when pressed |
| disabled | Label → `button.text-disabled`, no hover, raised bevel kept. edge style `disabled.border-style` (dashed in HC) |
| primary hover | Face → `button.primary.face-hover`. The label stays `button.primary.text` |

**Keyboard:**
- Tab focuses the button.
- Space and Enter activate it, firing on key-up.
- Enter anywhere in a dialog activates the default-framed button.
- Esc activates Cancel.

**Accessibility:**
- On the web, use a native `<button>`. A screen reader hears "Apply, button".
- Disabled buttons use `disabled`. If the button must stay focusable to explain why it's disabled, use `aria-disabled="true"` instead.
- An icon-only flat button needs `aria-label`.

**Content rules:**
- Verb-first, one or two words, sentence case: "Apply", "Save log".
- Use system words (OK, CANCEL, RETRY) in uppercase only in system dialogs.
- No exclamation marks. Never write "Click here".

**Web:** use `<button class="p95-btn">` and set `data-variant="primary|flat"` for the other variants. The default-framed button gets `data-default`. A bare `<button>` gets default styling from `base.css`.

**TUI:** brackets stand in for the bevel. The focused button is inverted (`select.bg` / `select.fg`), and the default button gets double angle marks.
```
 [ Apply ]  «[ OK ]»  ▌Cancel▐        ← ▌▐ = inverted (focused)
 ASCII:  [ Apply ]  <[ OK ]>  >Cancel<
```
- The primary variant renders inverted when idle, and hot (`text.hot`) when focused.
- A disabled button's label renders in `text.disabled`.
- **ratatui:** `Paragraph` with a styled `Span`. For a row of buttons, use a `Line` of spans.

---

### Icon button

**Purpose:** a square button with a 16px icon. It's for toolbars and the window title-bar controls.

**Anatomy:** bevel, face, 16px icon (`size.icon.sm`), and an optional tooltip.

| Part | Token |
|---|---|
| Face, bevel, states | Same as Button (`button.*`, `bevel.*`) |
| Icon colour | `button.text` · hover `button.text-hover` · disabled `button.text-disabled` |
| Size | `button.height` square. In a title bar, `window.control-size` |

**States:** the same as Button. The flat toolbar variant shows its bevel only on hover, pressed or focus.

**Keyboard:** the same as Button. In a toolbar, arrow keys move between buttons (roving tabindex).

**Accessibility:**
- `aria-label` is required. A screen reader hears "Close, button".
- Show a Tooltip with the same text, plus the keyboard shortcut if one exists.

**Content rules:** the label is the action ("Close", "Maximise"), not a description of the icon.

**Web:** `<button class="p95-btn" data-variant="icon" aria-label="Close">` with an `<svg>` from the icon sprite inside. Add `data-variant="icon flat"` for toolbars.

**TUI:** a single glyph inside brackets, inverted when focused.
```
 [x] [_] [□]        ASCII: [x] [_] [#]
```
**ratatui:** `Span` inside the title row of a `Block`.

---

### Toggle button

**Purpose:** a button that stays pressed while on. Examples: Bold, "Stream tokens", view switches.

**Anatomy:** the same as Button. The on state is shown by a sunken bevel and a fill.

| Part | Token |
|---|---|
| Off | Same as Button default |
| On | Sunken bevel, face `button.toggle.face-on`, label `button.toggle.text-on` |
| On + hover | Face `button.toggle.face-on-hover` |

| State | Change |
|---|---|
| off | Raised, `button.face` |
| on | Sunken, `button.toggle.face-on` / `button.toggle.text-on` |
| focus | `focus.ring` in both states |
| disabled | `button.text-disabled`. When on, the face is `surface.selected-subtle` |

**Keyboard:** Space and Enter toggle. In a segmented group, arrows move and Space toggles.

**Accessibility:**
- `<button aria-pressed="true|false">`. A screen reader hears "Stream tokens, toggle button, pressed".
- A group of exclusive toggles is a radio group: use `role="radiogroup"` and `role="radio"`.

**Content rules:** the label names the thing being toggled ("Wrap"), not "Turn on wrap".

**Web:** `<button class="p95-btn" aria-pressed="false">`. A segmented group goes inside `<div class="p95-segmented" role="group">`.

**TUI:**
```
 [ Wrap ] ▐ Wrap ▌        ← off, on (inverted)
 ASCII:  [ Wrap ] [*Wrap*]
```
**ratatui:** a `Span` styled with `select.bg` / `select.fg` when on. A group is a `Tabs`-like line of spans.

---

### Link

**Purpose:** inline navigation to another page, document or anchor.

**Anatomy:** text with a 1px underline, plus a focus ring.

| Part | Token |
|---|---|
| Text | `text.link` |
| Hover | `text.hot`, glow `glow.hot` at `effect.glow-strength`, radius `effect-size.glow-radius` |
| Underline | `border.width.hair` in currentColor |
| Focus | `focus.ring` around the inline box |
| Visited | Same as `text.link`. Phosphor has no second hue to spare |

| State | Change |
|---|---|
| hover | Colour → `text.hot`, plus a glow halo. The halo fades out over `duration.decay` with `easing.decay` |
| focus | Dotted `focus.ring` |
| pressed | Inverted: `select.bg` / `select.fg` for the duration of the press |
| disabled | Don't render a disabled link. Render plain `text.secondary` text instead |

**Keyboard:** Tab focuses the link and Enter follows it.

**Accessibility:**
- Native `<a href>`.
- Link text must make sense out of context.
- A link that opens a new window announces it in its text: "Docs (new window)".

**Content rules:** describe the destination ("Contrast report"), never "here".

**Web:** `<a class="p95-link">`. A bare `<a>` gets link styling from `base.css`.

**TUI:** the link renders underlined in `text.link`. If the terminal supports OSC 8 hyperlinks, wrap the text in one.
```
 See the contrast report.        (underlined; OSC 8 when supported)
 ASCII:  See <contrast report>.
```
**ratatui:** a `Span` with `Modifier::UNDERLINED`.
