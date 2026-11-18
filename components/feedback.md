# Feedback

Progress, meter, spinner, toast, alert dialog, tooltip, badge/status tag, boot line, empty state.

Shared rules for this file:
- **Status always comes with a text cue.** Every status is shown by a tag, `[ OK ]` `[INFO]` `[WARN]` `[ERR ]`, as well as by colour (`status.*.fg`). In mono, 16-colour and amber themes, the tag alone carries the meaning.
- **Motion is stepped and short.** It is replaced by static frames under `prefers-reduced-motion` (or the TUI equivalent `P95_REDUCED_MOTION=1`).

| Level | Tag (fixed 6 cells) | fg | bg (tinted surface) | border |
|---|---|---|---|---|
| ok | `[ OK ]` | `status.ok.fg` | `status.ok.bg` | `status.ok.border` |
| info | `[INFO]` | `status.info.fg` | `status.info.bg` | `status.info.border` |
| warn | `[WARN]` | `status.warn.fg` | `status.warn.bg` | `status.warn.border` |
| error | `[ERR ]` | `status.error.fg` | `status.error.bg` | `status.error.border` |

---

### Progress

**Purpose:** determinate progress toward completion. This is the segmented bar from the boot screen.

**Anatomy:**
- A sunken track.
- Fill segments, each `progress.segment-width` wide, separated by `progress.segment-gap`. Partial segments are never drawn.
- An optional label above or beside the track.

| Part | Token |
|---|---|
| Track | `progress.track`, sunken `bevel.*`, height `progress.height` |
| Segments | `progress.fill` |
| Label | `progress.label`, `type.label` (e.g. `UPLINK 62%`) |
| Indeterminate | 3 lit segments sweeping across, one segment per `duration.tick` (`easing.steps`) |

| State | Change |
|---|---|
| running | Segments fill as whole steps |
| complete | Track full. The label reads `[ OK ] DONE`, or the bar is removed |
| error | The fill stops. The label reads `[ERR ] <reason>` in `status.error.fg` |
| paused | Label `PAUSED`, in `text.secondary` |

**Keyboard:** none.

**Accessibility:**
- `<progress value max>`, or `role="progressbar"` with `aria-valuenow`. The label is linked with `aria-labelledby`.
- Announce only the milestones (25%, 50%, done), not every tick.

**Content rules:** the label is an uppercase noun + percent: `UPLINK 62%`, `LOADING MODEL 40%`.

**Web:** `<progress class="p95-progress" value="62" max="100">`, segmented with a `repeating-linear-gradient`.

**TUI:** the empty part of the track is drawn as `░` in `progress.track`.
```
 UPLINK 62%
 ▕████████████████████░░░░░░░░░░░░▏
 ASCII: [################--------] 62%
```
**ratatui:** `Gauge` with `use_unicode(false)`, or `LineGauge` with `filled_style` set to `progress.fill`. Snap the value down to whole cells.

---

### Meter

**Purpose:** a static measurement within a known range, such as CPU, temperature or signal. Unlike Progress, it isn't working toward completion.

**Anatomy:** the same as Progress, plus optional threshold marks. The fill colour switches to the warn or error colour once the value crosses a threshold.

| Part | Token |
|---|---|
| Track and segments | `progress.track`, `progress.fill` |
| Over warn threshold | Segments `status.warn.fg`. Label prefixed `[WARN]` |
| Over error threshold | Segments `status.error.fg`. Label prefixed `[ERR ]` |
| Threshold tick | `border.strong` |

**States:** as above. The value updates in place, with no animation.

**Accessibility:** `<meter min max low high optimum value>`, or `role="meter"`.

**Content rules:** the label shows the unit: `CPU 12%`, `95°C`.

**Web:** `<meter class="p95-meter">`.

**TUI:** one row: label, bar and value. This is the btop style.
```
 CPU  ▕███░░░░░░░░░▏ 12%
 TEMP ▕██████████▓░▏ 95°C [WARN]
```
**ratatui:** `Gauge` or `Sparkline` for history.

---

### Spinner

**Purpose:** indeterminate activity that lasts under ~10 seconds. For anything longer, use Progress.

**Anatomy:** a single cell cycling through frames, plus an optional label.

| Part | Token |
|---|---|
| Glyph | `text.primary` |
| Frame time | `duration.tick` × 2 (100ms), stepped (`easing.steps`) |
| Label | `text.secondary` |

| Frames | Set |
|---|---|
| Default (ASCII-safe) | `\| / - \` |
| Block | `▖ ▘ ▝ ▗` |
| Boot | `[    ] [=   ] [==  ] [=== ] [ ===] [  ==] [   =]` |

**States:**
- running.
- done: the spinner is replaced by `[ OK ]` or `[ERR ]`.
- reduced motion: a static `[ .. ]` with the label.

**Accessibility:** `role="status"` with the label text ("Transcribing"). The glyph is `aria-hidden`.

**Content rules:** the label is a present participle in sentence case: "Transcribing", "Contacting node-01".

**Web:** `<span class="p95-spinner" role="status"><span aria-hidden="true"></span>Transcribing</span>` (CSS steps animation).

**TUI:**
```
 / Transcribing        ASCII: same
```
**ratatui:** a `Span` whose glyph is chosen by `tick % frames.len()`.

---

### Toast / notification

**Purpose:** a transient, non-blocking message about an event, such as "Log saved" or "Brain reconnected".

**Anatomy:** a small window: a mini title bar with the tag and source, a body (1–2 lines), an optional single action, and close.

| Part | Token |
|---|---|
| Frame | `toast.bg`, raised `bevel.*`, width `toast.width` |
| Accent edge | Left edge, `toast.accent-width` wide, in `status.<level>.border` |
| Title strip | `title.inactive.bg` / `title.inactive.fg`. The level tag is in `status.<level>.fg` |
| Body | `toast.text`, `type.ui` |
| Action | Flat button |
| Layer | `layer.toast`, stacked bottom-right (web) or top-right (TUI) with a `space.8` gap |
| Timing | Appears instantly. Auto-dismiss after 5s (ok/info). Warn and error stay until dismissed |

| State | Change |
|---|---|
| hover / focus within | The auto-dismiss timer pauses |
| dismissed | Removed instantly, with no slide |

**Keyboard:** F6 or a documented shortcut reaches the toast region. Esc dismisses the focused toast.

**Accessibility:**
- The region is `role="status"` (ok/info) or `role="alert"` (error). Don't move focus to it.
- A screen reader hears "Info: Brain reconnected".

**Content rules:**
- Title: the uppercase tag + source (`[INFO] BRAIN`).
- Body: what happened, in the past tense, with no period on a single line.
- Errors add the fix.

**Web:** `<p95-toast level="info">`, inside a `<div class="p95-toasts" role="status">` region.

**TUI:**
```
                      ┌▐[INFO] BRAIN ▌─────[x]┐
                      │ Reconnected to node-01 │
                      └────────────────────────┘
```
**ratatui:** `Clear` + `Block` in a corner `Rect`.

---

### Alert dialog

**Purpose:** a modal interruption for something the user must acknowledge or decide, such as destructive confirmations or fatal errors.

**Anatomy:** a Dialog with a 32px status icon at the left of the body, plus the tag in the title.

| Part | Token |
|---|---|
| Dialog | As Dialog (`window.*`, `surface.overlay`, `layer.dialog`) |
| Title | `[WARN] DELETE LOG`. The tag is in `status.<level>.fg`, inside the inverted title bar |
| Icon | 32px (`size.icon.md`) in `status.<level>.fg` |
| Destructive button | Default button. The label names the action, and focus starts on **Cancel** |

**States:** as Dialog.

**Keyboard:** as Dialog. For a destructive action, Enter on open activates Cancel.

**Accessibility:** `role="alertdialog"`, with `aria-describedby` on the body. It's announced immediately.

**Content rules:**
- Title: the tag + an uppercase verb phrase.
- Body: the consequence in one sentence ("This deletes 3 days of logs.").
- Buttons: "Delete log" / "Cancel".

**Web:** `<p95-dialog role="alertdialog" level="warn">`.

**TUI:** as Dialog, with the tag in the title row.

**ratatui:** as Dialog.

---

### Tooltip

**Purpose:** a short label or hint for a control, shown on hover or focus. Never put essential information only in a tooltip.

**Anatomy:** a small inverted box with no bevel. It sits below the target, offset `space.4`.

| Part | Token |
|---|---|
| Box | `tooltip.bg`, 1px `tooltip.border` edge |
| Text | `tooltip.fg`, `type.small` |
| Delay | Shows after `duration.slow` on hover, immediately on keyboard focus. Hides after `duration.fast` |
| Layer | `layer.menu` |

**States:** shown or hidden. A tooltip is never interactive.

**Keyboard:** appears on focus; Esc hides it.

**Accessibility:**
- `role="tooltip"`, referenced from the target by `aria-describedby`.
- For an icon button, the accessible name comes from `aria-label`, not from the tooltip.

**Content rules:** a phrase in sentence case, with no period. Add the shortcut after two spaces: "Close  Ctrl+W".

**Web:** `<span role="tooltip" class="p95-tooltip">`, positioned by CSS anchor positioning with a JS fallback.

**TUI:** usually omitted. The key-hint bar or the status line carries the hint instead. If shown, it's an inverted one-row box.
```
 [x]
 ▐Close  ^W▌
```
**ratatui:** a `Paragraph` with the `select.*` style, over a `Clear`.

---

### Badge / status tag

**Purpose:** a compact label of state or count: `[ OK ]`, `ONLINE`, `3 NEW`.

**Anatomy:** a fixed-width bracketed tag, or a filled pill-free block (radius 0).

| Part | Token |
|---|---|
| Neutral | `badge.bg` / `badge.fg` |
| Status variants | `status.<level>.fg` on `status.<level>.bg`, 1px `status.<level>.border` |
| Solid (high emphasis) | Inverted: `status.<level>.fg` as the background, `text.inverse` as the text |
| Type | `type.label` (uppercase), padding-x `space.4` |

**States:** static. A count badge updates in place.

**Accessibility:**
- The tag text is the accessible text, so `[WARN]` reads as "WARN".
- A count badge on an icon needs context: `aria-label="3 new messages"`.

**Content rules:**
- Tags are uppercase and fixed width: 4 characters inside brackets, space-padded (`[ OK ]`, `[ERR ]`).
- Counts are numbers + an uppercase noun.

**Web:** `<span class="p95-badge" data-level="warn">WARN</span>`. The CSS adds the brackets.

**TUI:**
```
 [ OK ] [INFO] [WARN] [ERR ]   ONLINE   ▐3 NEW▌
```
**ratatui:** a `Span` styled with `status.<level>.fg`.

---

### Boot line

**Purpose:** a single line of system output in the POST/systemd style. It's the default format for CLI status, the TERMINAL-01 boot sequence, and log summaries.

**Anatomy:** `[TAG] subject   detail // detail`

| Part | Token |
|---|---|
| Tag | Status tag (`status.<level>.fg`) |
| Subject | `text.primary`, `type.code`, padded to a column |
| Detail | `text.secondary` |
| Separator | ` // ` in `text.secondary` |
| Typed reveal | `duration.type` per character, optional (off with reduced motion) |

**States:** pending (`[ .. ]` with a spinner), then ok, info, warn or error.

**Accessibility:** a boot sequence is a `role="log"` region. Each line is plain text.

**Content rules:**
- Subject: a lowercase component name or an uppercase system noun.
- Detail: terse facts with units.
- Errors follow **what // why // fix**: `[ERR ] brain  no reply // node-01 unreachable // check LAN`.
- Present tense, no trailing period.

**Web:** `<p95-boot>` types out a sequence of `<li>` lines. A static line is `<div class="p95-bootline" data-level="ok">`.

**TUI:**
```
 [ OK ] zsh is login shell
 [ OK ] starship   ascii prompt
 [WARN] thermal    95°C // throttling likely
```
**ratatui:** a `Line` of `Span`s. For CLIs, plain `println!` with ANSI.

---

### Empty state

**Purpose:** fills a view with nothing to show, and says what to do next. It's the Operator's main appearance.

**Anatomy:** the Operator avatar (48 or 96px), a one-line uppercase status, one line of help in sentence case, and an optional primary action.

| Part | Token |
|---|---|
| Avatar | Operator at `operator.size` (×1) or ×2. See [identity.md](identity.md#avatar-the-operator) |
| Status | `text.primary`, `type.label` (`NO LOGS YET`) |
| Help | `text.secondary`, `type.body` |
| Action | Button (default or primary) |
| Spacing | `space.16` between parts, centred in the view |

**States:**
- empty: no data yet.
- filtered-empty: `NO MATCHES`, with a "Clear filter" action and no avatar.
- error-empty: `[ERR ] COULD NOT LOAD`, with Retry.

**Accessibility:** the avatar is decorative (`alt=""`). The status is a heading or `role="status"` when it appears dynamically.

**Content rules:** status in uppercase; help as one sentence that names the next step ("Say "Hey Terminal" to start a conversation."). No jokes in error states.

**Web:** `<div class="p95-empty"><p95-operator size="2"></p95-operator><h2>NO LOGS YET</h2><p>…</p></div>`.

**TUI:** the small Operator (`brand/logo/operator-small.ansi`, 8 rows), or no art below 40 columns.
```
   ▄██▄
  ██▀▀█▌      NO LOGS YET
  ▀███▀       Say "Hey Terminal" to start.
```
**ratatui:** a `Paragraph` of the pre-rendered ANSI art (converted to `Text`), centred.
