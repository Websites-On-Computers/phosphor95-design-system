# Motion

A CRT doesn't tween. Motion is stepped, brief, and mostly about light changing. Things don't fly around.

## Tokens

| Token | Value | Use |
|---|---|---|
| `duration.instant` | 0 ms | State changes that must feel immediate: pressed, checked, selected |
| `duration.tick` | 50 ms | One step of `steps()` motion (20 fps, CRT-era feel) |
| `duration.fast` | 100 ms | Hover glow in, menu open |
| `duration.base` | 200 ms | Dialogs and toasts appearing, tab panel swaps |
| `duration.slow` | 400 ms | Window open or close, splash transitions |
| `duration.decay` | 300 ms | Phosphor afterglow: glow fading **out** after hover or focus leaves |
| `duration.blink` | 530 ms | Half-period of the block cursor blink (classic VGA timing) |
| `duration.type` | 30 ms | Per character, for typed-out text |
| `easing.linear` | `[0, 0, 1, 1]` | Progress, rain |
| `easing.decay` | `[0.2, 0, 0, 1]` | A fast drop and a long tail: phosphor fading out |
| `easing.steps` | `[0, 0, 1, 1]` + `$extensions.com.phosphor95.steps: 4` | Stepped motion (see below) |

## Stepped motion

DTCG has no `steps()` timing function. So `easing.steps` holds a linear value for tools that ignore extensions, and platforms read the step count from `$extensions.com.phosphor95.steps`. On the web: `animation-timing-function: steps(4, end)`. In a TUI: update every `duration.tick`.

Use steps for anything that moves or grows: windows opening (an outline that grows in four steps, as in Win95), progress segments filling, spinners. Use `easing.decay` only for changes in luminance.

## Signature motions

| Motion | Recipe |
|---|---|
| **Cursor blink** | Block cursor (`text.hot`) toggles every `duration.blink`. A hard on/off, with no fade |
| **Phosphor decay** | Hover or focus on: glow and `text.hot` appear within `duration.fast`. Off: they fade over `duration.decay` with `easing.decay`. Light lingers, the way real phosphor does |
| **Typed text** | Boot lines and Operator speech appear one character per `duration.type`, each line ending in a blinking cursor. Anything longer than about 80 characters shows the rest at once, so nobody waits for it |
| **Menu or dropdown** | Appears at once, or unrolls in `steps(4)` over `duration.fast` |
| **Window open/close** | Outline zoom in `steps(4)` over `duration.slow`, then the content draws at once |
| **Progress** | Segments (`progress.segment-width`) are added whole, never as fractional widths |

## Reduced motion

When `prefers-reduced-motion: reduce` is set (web), or `P95_REDUCED_MOTION=1` / no TTY (TUI):

| Turns off | Becomes instant | Stays |
|---|---|---|
| Digital rain, flicker, CRT roll | Typed text (shows whole lines) | Cursor blink, which is user-configurable and also off if the OS disables caret blink |
| Window zoom | Phosphor decay (glow off at once) | Color and luminance state changes |
| Spinner animation (show a static `[....]` or a percentage) | Menu unroll | Progress fill (stepped, driven by real progress) |

Nothing ever flashes more than 3 times per second; see [effects.md](effects.md) and [accessibility.md](accessibility.md).
