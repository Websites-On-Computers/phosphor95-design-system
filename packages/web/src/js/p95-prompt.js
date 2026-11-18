// <p95-prompt placeholder="Ask TERMINAL-01" label="Command"> — "> _" command line with a log.
// Enter fires "p95-command" {value}; Up/Down walk history. Write replies with
//   prompt.print(text, level?)   level: ok|info|warn|error adds the status tag
//   prompt.busy = true            shows a hot ">" and sets aria-busy
// The log is role="log" so screen readers hear replies as they arrive.
import { define, nextId } from "./util.js";

const TAG = { ok: "[ OK ] ", info: "[INFO] ", warn: "[WARN] ", error: "[ERR ] " };

class P95Prompt extends HTMLElement {
  connectedCallback() {
    if (this.input) return;
    const id = nextId("prompt");
    this.log = document.createElement("div");
    this.log.className = "p95-prompt-log";
    this.log.setAttribute("role", "log");
    this.log.setAttribute("aria-live", "polite");
    // Any initial content becomes history (drop whitespace-only text: the log is pre-wrap).
    this.log.append(...[...this.childNodes].filter((n) => n.nodeType !== Node.TEXT_NODE || n.textContent.trim()));
    const line = document.createElement("div");
    line.className = "p95-prompt-line";
    const glyph = document.createElement("span");
    glyph.className = "p95-prompt-glyph";
    glyph.setAttribute("aria-hidden", "true");
    glyph.textContent = ">";
    this.input = document.createElement("input");
    this.input.id = id;
    this.input.autocomplete = "off";
    this.input.spellcheck = false;
    this.input.placeholder = this.getAttribute("placeholder") || "";
    this.input.setAttribute("aria-label", this.getAttribute("label") || "Command");
    line.append(glyph, this.input);
    this.append(this.log, line);
    this.history = [];
    this.pos = 0;
    this.input.addEventListener("keydown", (e) => this.onKey(e));
    this.addEventListener("click", (e) => { if (!this.log.contains(e.target) || !getSelection().toString()) this.input.focus(); });
  }
  set busy(v) { this.toggleAttribute("busy", !!v); this.setAttribute("aria-busy", String(!!v)); }
  get busy() { return this.hasAttribute("busy"); }

  print(text, level) {
    const p = document.createElement("div");
    if (level && TAG[level]) {
      const tag = document.createElement("span");
      tag.className = `p95-text-${level}`;
      tag.textContent = TAG[level];
      p.append(tag);
    }
    p.append(document.createTextNode(text));
    this.log.append(p);
    this.log.scrollTop = this.log.scrollHeight;
    return p;
  }
  onKey(e) {
    if (e.key === "Enter") {
      const value = this.input.value.trim();
      if (!value) return;
      const echo = this.print(value);
      echo.className = "p95-prompt-entry-user";
      this.history.push(value);
      this.pos = this.history.length;
      this.input.value = "";
      this.dispatchEvent(new CustomEvent("p95-command", { bubbles: true, detail: { value } }));
    } else if (e.key === "ArrowUp" && this.pos > 0) {
      e.preventDefault();
      this.input.value = this.history[--this.pos];
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      this.pos = Math.min(this.history.length, this.pos + 1);
      this.input.value = this.history[this.pos] ?? "";
    }
  }
}
define("p95-prompt", P95Prompt);
export default P95Prompt;
