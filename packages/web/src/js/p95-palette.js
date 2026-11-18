// <p95-palette hotkey="k">  — command palette (Ctrl/⌘+K by default).
//   <button data-command="theme-amber" data-shortcut="Ctrl+3">Theme: amber</button> …
// Children are the command source (hidden); the palette shows a filterable listbox.
// Arrow keys move, Enter runs, Esc closes. Fires "p95-command" {command, label}.
import { define, nextId } from "./util.js";

class P95Palette extends HTMLElement {
  connectedCallback() {
    if (this.dialog) return;
    const listId = nextId("palette-list");
    this.dialog = document.createElement("dialog");
    this.dialog.className = "p95-window";
    this.dialog.setAttribute("aria-label", this.getAttribute("label") || "Command palette");
    this.dialog.innerHTML = `
      <header class="p95-titlebar"><span class="p95-titlebar-title">${this.getAttribute("title") || "RUN COMMAND"}</span></header>
      <div class="p95-window-body p95-stack">
        <input class="p95-field" role="combobox" aria-expanded="true" aria-controls="${listId}" aria-autocomplete="list" placeholder="Type a command">
        <ul class="p95-palette-list" role="listbox" id="${listId}"></ul>
      </div>`;
    this.append(this.dialog);
    this.input = this.dialog.querySelector("input");
    this.list = this.dialog.querySelector("ul");
    this.input.addEventListener("input", () => this.render());
    this.input.addEventListener("keydown", (e) => this.onKey(e));
    this.list.addEventListener("click", (e) => { const li = e.target.closest("li"); if (li) this.run(li); });
    this.dialog.addEventListener("click", (e) => { if (e.target === this.dialog) this.close(); });
    const key = (this.getAttribute("hotkey") || "k").toLowerCase();
    this.onHotkey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === key) { e.preventDefault(); this.dialog.open ? this.close() : this.show(); }
    };
    document.addEventListener("keydown", this.onHotkey);
  }
  disconnectedCallback() { document.removeEventListener("keydown", this.onHotkey); }

  get commands() {
    return [...this.querySelectorAll(":scope > [data-command]")].map((el) => ({
      command: el.dataset.command, label: el.textContent.trim(), shortcut: el.dataset.shortcut || "",
    }));
  }
  show() { this.input.value = ""; this.render(); this.dialog.showModal(); this.input.focus(); }
  close() { this.dialog.close(); }

  render() {
    const q = this.input.value.trim().toLowerCase();
    const hits = this.commands.filter((c) => c.label.toLowerCase().includes(q));
    this.list.replaceChildren(...hits.map((c, i) => {
      const li = document.createElement("li");
      li.id = `${this.list.id}-${i}`;
      li.setAttribute("role", "option");
      li.dataset.command = c.command;
      const label = document.createElement("span");
      if (q) {
        const at = c.label.toLowerCase().indexOf(q);
        const m = document.createElement("mark");
        m.textContent = c.label.slice(at, at + q.length);
        label.append(c.label.slice(0, at), m, c.label.slice(at + q.length));
      } else label.textContent = c.label;
      li.append(label);
      if (c.shortcut) { const k = document.createElement("kbd"); k.textContent = c.shortcut; li.append(k); }
      return li;
    }));
    if (!hits.length) {
      const li = document.createElement("li");
      li.className = "p95-palette-empty";
      li.textContent = `NO MATCHES FOR "${this.input.value.trim()}"`;
      this.list.append(li);
    }
    this.move(0);
  }
  get options() { return [...this.list.querySelectorAll("[role='option']")]; }
  move(i) {
    const opts = this.options;
    opts.forEach((o, j) => o.setAttribute("aria-selected", String(j === i)));
    this.active = opts[i] ? i : -1;
    if (opts[i]) { this.input.setAttribute("aria-activedescendant", opts[i].id); opts[i].scrollIntoView({ block: "nearest" }); }
    else this.input.removeAttribute("aria-activedescendant");
  }
  onKey(e) {
    const n = this.options.length;
    if (e.key === "ArrowDown") { e.preventDefault(); this.move((this.active + 1) % n); }
    else if (e.key === "ArrowUp") { e.preventDefault(); this.move((this.active - 1 + n) % n); }
    else if (e.key === "Enter") { e.preventDefault(); const o = this.options[this.active]; if (o) this.run(o); }
  }
  run(li) {
    if (!li.dataset.command) return;
    this.close();
    this.dispatchEvent(new CustomEvent("p95-command", { bubbles: true, detail: { command: li.dataset.command, label: li.textContent } }));
  }
}
define("p95-palette", P95Palette);
export default P95Palette;
