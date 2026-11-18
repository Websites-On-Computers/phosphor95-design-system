# Voice and tone

Phosphor95 speaks in a **machine voice**: a well-built 1995 terminal that happens to be smart.
Status first, then the fact, then the next step. Short words, no filler.

## Rules

| Rule | Example |
|---|---|
| **Status lines are uppercase**, with a 4-character status tag | `[ OK ] NETWORK UP` |
| **Help and body text is sentence case** | `Press Enter to retry.` |
| **Status tags are exactly** `[ OK ]` `[INFO]` `[WARN]` `[ERR ]` `[ .. ]` (pending) | They line up in a log because each is 6 characters wide |
| **`//` separates identity parts** | `PHOSPHOR95 // DESIGN SYSTEM`, `TERMINAL-01 // LOCAL INTELLIGENCE NODE` |
| **No exclamation marks.** No "Oops", "Uh-oh", "Awesome" | `[ OK ] SAVED`, not `Saved!` |
| **Numbers are exact, with units** | `UPLINK 62%`, `3 FILES`, `0.58 S` |
| **Say what happened, why, and what to do**, in that order | see Errors |
| **Name things by what the user sees** | the button says `RETRY`, so the text says "Choose RETRY" |
| **Buttons are verbs**, uppercase in title bars and dialogs | `SAVE` `CANCEL` `DELETE 3 FILES` |
| **No "I" in UI chrome.** Conversational surfaces (terminal01 voice, chat replies) may use "I" | |
| **Confirmations name the consequence** | `DELETE 3 FILES?` / `This can't be undone.` |
| **Time is 24-hour, ISO dates** | `2026-11-04 18:29` |

## Errors

The pattern is **what / why / fix**, one line each, on screen and in logs:

```
[ERR ] BRAIN UNREACHABLE
       node-01 did not answer on 192.0.2.10:8080 (timed out after 5 s).
       Check that llama.cpp is running, then choose RETRY. Local commands still work.
```

| Instead of | Write |
|---|---|
| `Oops! Something went wrong.` | `[ERR ] SAVE FAILED` / `Disk full (0 B free on /home).` / `Free space, then choose RETRY.` |
| `Are you sure?` | `DELETE 3 FILES?` / `This can't be undone.` |
| `Success!` | `[ OK ] 3 FILES DELETED` |
| `No results found :(` | `NO MATCHES FOR "phosphor"` / `Try fewer words.` |
| `Loading, please wait...` | `[ .. ] LOADING MODELS 2/5` |
| `Invalid input` | `PORT MUST BE 1–65535` |

## Tone by situation

| Situation | Tone | Example |
|---|---|---|
| Routine success | Minimal; often just the tag | `[ OK ] SAVED` |
| Progress | Count and noun | `[ .. ] INDEXING 1,204/5,000` |
| Warning | Level; name the risk | `[WARN] BATTERY 9%. SAVE YOUR WORK.` |
| Error | Level; never blame the user | see above |
| Empty state | Inviting, one next step | `NO ENTRIES` / `Say "Hey Terminal" or hold Space.` |
| Boot / splash | Ceremonial, POST style | `PHOSPHOR BIOS v4.51` / `MEMORY TEST 8192K OK` |
| Assistant reply | Plain, helpful, first person allowed | `It's 18:29. Your timer has 4 minutes left.` |

## Formatting

- **Truncate with `…`** (one glyph, so the cell grid holds). ASCII fallback: `...`.
- **Keys** are written as they're labelled: `Ctrl+Alt+M`, `F1`, `Enter`. In key-hint bars: `^Q QUIT  F1 HELP`.
- **Paths, commands and code** go in mono, unquoted: `./phosphor apply`.
- **Lists** in terminals use `-` or `·`, never emoji.
