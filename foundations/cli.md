# Command-line and terminal UI guidelines

These are rules for CLIs and TUIs built with Phosphor95. The voice comes from [../brand/voice.md](../brand/voice.md),
glyphs from [iconography.md](iconography.md), and colors from the `p95-style` crate
([../packages/tui](../packages/tui/README.md)).

## Environment

Every Phosphor95 terminal program reads the same switches. `p95_style::Env::detect()` implements them.

| Variable | Effect |
|---|---|
| `NO_COLOR` (non-empty) | No color escapes. Bold, dim, reverse and the border styles only |
| `P95_COLOR` = `truecolor` \| `256` \| `16` \| `mono` | Overrides color-depth detection |
| `COLORTERM`, `TERM` | Detection. `truecolor`/`24bit` means 24-bit; `*-256color` means 256; `dumb` means mono; anything else gets 16 |
| `LANG` / `LC_*` UTF-8 | Unicode glyph tier. Otherwise ASCII |
| `P95_ASCII=1` | Forces the ASCII tier (logs, serial consoles, screen readers) |
| `P95_NERD_FONT=1` | Nerd Font icons (tier 3) |
| `P95_REDUCED_MOTION=1` | No spinners, typing or blinking. Spinners become `[ .. ]` |
| `P95_THEME` = `green` \| `amber` \| `white` \| `hc` | Theme. Default green |

When stdout is **not a TTY**: no color (unless forced), no animation, no cursor movement, and one
complete line per event.

## Output lines

```
[ OK ] NETWORK UP
[INFO] WHISPER BASE.EN LOADED 0.15 S
[WARN] CPU 95 °C. THROTTLING
[ERR ] BRAIN UNREACHABLE
       node-01 did not answer on 192.0.2.10:8080 (timed out after 5 s).
       Check that llama.cpp is running, then retry. Local commands still work.
[ .. ] RECONNECTING 2/5
```

- Every status line starts with a 6-character tag. `Level::tag()` returns it, and `Theme::status_line()` builds the whole line.
- The status line is uppercase. Continuation lines are sentence case, indented 7 spaces so they sit under the message.
- **Errors give what, why and fix:** the tag line says what failed; the next lines say why and what to do.
- Errors and warnings go to **stderr**. Results go to **stdout**, plain and parseable: no tags, no color when piped.
- Numbers include their units (`0.58 S`, `62%`, `3 FILES`).

## Help text

```
PHOSPHOR // apply the Phosphor-95 theme

USAGE
  phosphor <command> [options]

COMMANDS
  apply      Build and install (user level)
  doctor     Check the installation
  rename     Rename the machine persona everywhere

OPTIONS
  -n, --dry-run    Show what would change
  -h, --help       Show this help
      --version    Show the version

EXAMPLES
  phosphor apply
  phosphor rename TERMINAL-02
```

- The first line is `NAME // one-line purpose`.
- Section headers are uppercase. The body is sentence case. Columns align on two spaces. Lines are 80 columns at most.
- `--help` and `-h` print to stdout and exit 0. A usage error prints the usage line plus one hint to stderr, and exits 2.
- `--version` prints `name x.y.z`, optionally followed by the Operator banner (`brand/logo/operator-small.ansi`) when stdout is a TTY.

## Prompts and confirmation

```
DELETE 3 FILES? This can't be undone. [y/N] _
```

- Use the question form from the voice guide. Put the default in capitals, and Enter accepts it.
- **Never prompt when stdin isn't a TTY.** Fail with an error that names the flag to pass instead (`--yes`).
- Destructive actions default to No.

## Progress

| Duration | Show |
|---|---|
| Under 1 s | Nothing |
| Unknown length | A spinner plus a noun: `⠹ TRANSCRIBING`. Under reduced motion: `[ .. ] TRANSCRIBING` |
| Known length | Whole-cell bar plus a count: `▕██████████░░░░░░▏ 62%` (`Theme::progress`) |
| Multi-step | One status line per step, rewritten in place from `[ .. ]` to `[ OK ]` (one new line per step when not a TTY) |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Failure. The error is already printed |
| 2 | Usage error: bad flag or argument |
| 3 | Partial success. Some items failed; each one is listed with `[ERR ]` |
| 130 | Interrupted (Ctrl+C). Print `[WARN] INTERRUPTED` and clean up |

## Full-screen TUIs

- **Layout:** a menubar row at the top (optional), the panes, then a key-hint bar and a status bar
  in the last two rows (`Theme::key_hints`, `Theme::status_bar`).
- **Focus:** exactly one pane has the double border (`Theme::panel(.., true)`). Tab cycles panes.
  In mono, that border is the only cue, so never drop it.
- **Selection:** inverse video (`Theme::selected`). An unfocused list keeps its selection underlined
  (`selected_inactive`). ASCII and mono add the `> ` marker.
- **Keys:** `q`/`Esc` quits or backs out, `?`/`F1` opens help, `/` searches, `Tab` moves focus, and
  arrows/`hjkl` move within a pane. Show the main keys in the hint bar at all times.
- **Resize:** reflow, never crash. Below 80×24, show `[WARN] TERMINAL TOO SMALL (80x24 NEEDED)`.
- **Colors:** never hard-code them. Read everything from `Theme` so all four themes and all four
  depths work. The gallery test renders 96 combinations, and so should yours.
