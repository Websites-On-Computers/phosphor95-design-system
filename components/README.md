# Components

Each component is specified once here, with both a web rendering and a TUI rendering. Specs are grouped by category, one file per category. Every token named here is a real path in `tokens/`; when a token changes, its spec follows.

| Component | File |
|---|---|
| Button (default, primary, flat) | [actions.md](actions.md#button) |
| Icon button | [actions.md](actions.md#icon-button) |
| Toggle button | [actions.md](actions.md#toggle-button) |
| Link | [actions.md](actions.md#link) |
| Text field | [inputs.md](inputs.md#text-field) |
| Textarea | [inputs.md](inputs.md#textarea) |
| Select / dropdown | [inputs.md](inputs.md#select--dropdown) |
| Checkbox | [inputs.md](inputs.md#checkbox) |
| Radio | [inputs.md](inputs.md#radio) |
| Switch | [inputs.md](inputs.md#switch) |
| Slider | [inputs.md](inputs.md#slider) |
| Spin box | [inputs.md](inputs.md#spin-box) |
| Search | [inputs.md](inputs.md#search) |
| Command prompt | [inputs.md](inputs.md#command-prompt) |
| Window | [containers.md](containers.md#window) |
| Dialog | [containers.md](containers.md#dialog) |
| Panel | [containers.md](containers.md#panel) |
| Group box (fieldset) | [containers.md](containers.md#group-box-fieldset) |
| Tabs | [containers.md](containers.md#tabs) |
| Accordion | [containers.md](containers.md#accordion) |
| Split pane | [containers.md](containers.md#split-pane) |
| Card / frame | [containers.md](containers.md#card--frame) |
| Scrollbar | [containers.md](containers.md#scrollbar) |
| Menubar | [navigation.md](navigation.md#menubar) |
| Menu | [navigation.md](navigation.md#menu) |
| Context menu | [navigation.md](navigation.md#context-menu) |
| Taskbar / status bar | [navigation.md](navigation.md#taskbar--status-bar) |
| Breadcrumbs (path bar) | [navigation.md](navigation.md#breadcrumbs-path-bar) |
| Command palette | [navigation.md](navigation.md#command-palette) |
| Key-hint bar | [navigation.md](navigation.md#key-hint-bar) |
| List | [data.md](data.md#list) |
| Table | [data.md](data.md#table) |
| Tree | [data.md](data.md#tree) |
| Key-value list | [data.md](data.md#key-value-list) |
| Log viewer | [data.md](data.md#log-viewer) |
| Code block | [data.md](data.md#code-block) |
| Diff | [data.md](data.md#diff) |
| Progress | [feedback.md](feedback.md#progress) |
| Meter | [feedback.md](feedback.md#meter) |
| Spinner | [feedback.md](feedback.md#spinner) |
| Toast / notification | [feedback.md](feedback.md#toast--notification) |
| Alert dialog | [feedback.md](feedback.md#alert-dialog) |
| Tooltip | [feedback.md](feedback.md#tooltip) |
| Badge / status tag | [feedback.md](feedback.md#badge--status-tag) |
| Boot line | [feedback.md](feedback.md#boot-line) |
| Empty state | [feedback.md](feedback.md#empty-state) |
| Avatar (the Operator) | [identity.md](identity.md#avatar-the-operator) |
| Wordmark | [identity.md](identity.md#wordmark) |
| Splash / boot screen | [identity.md](identity.md#splash--boot-screen) |

## The spec template

Every component follows the same sections, in this order:

| Section | What it holds |
|---|---|
| **Purpose** | What it's for, and when to use something else instead |
| **Anatomy** | The named parts. These names are used in the tables below |
| **Tokens** | Part → exact token path. Component tokens (`button.*`, `list.*`…) come first. If a part has no component token, it uses a semantic token (`surface.*`, `text.*`, `bevel.*`) |
| **States** | default, hover, pressed, focus, selected, disabled and invalid, as they apply. Each row says what changes, by token |
| **Keyboard** | Every interaction must work without a pointer |
| **Accessibility** | Web role and ARIA, and what a screen reader announces. TUI accessibility is covered by the keyboard rules, plus text cues for every colour cue |
| **Content rules** | Labels and copy, in the machine voice: terse, uppercase for system and status labels, sentence case for help, no exclamation marks |
| **Web** | Native element first. Then the `.p95-*` class, `data-variant`/`data-level` attributes, and a `<p95-*>` web component only where JavaScript is needed |
| **TUI** | A literal mockup using box-drawing, half-blocks and inversion. Then the ASCII fallback, and the ratatui widget it maps to |

## Rules every component inherits

- **Shape:** radius is `border.radius.none`, and there are no shadows. Depth comes from the four-edge bevel. Raised: `bevel.hi` / `bevel.light` top-left, `bevel.dark` / `bevel.shadow` bottom-right. Sunken is the reverse.
- **Pressed:** the bevel turns sunken, and the content shifts 1px.
- **Focus:** the dotted `focus.ring` (`border.focus`), `focus.inset` inside the control.
- **Selection:** inverted (`select.bg` / `select.fg`). Hover brightens text to primary/hot, because glow means hot.
- **Disabled:** `text.disabled`, which is exempt from contrast as an inactive control. The edge uses `disabled.border-style`, which is dashed in HC.
- **Status:** always a text or glyph cue (`[ OK ]` `[INFO]` `[WARN]` `[ERR ]`) as well as `status.*` colour.
- **Type:** pixel fonts only at their native sizes or integer multiples (`font.size.*`).
- **Motion:** stepped (`easing.steps`, `duration.tick`). All of it is off under reduced motion.
- **TUI colour:** must survive the capability ladder: truecolor → 256 → ANSI-16 (`ansi.*`) → mono. Mono keeps reverse video and the text cues.
