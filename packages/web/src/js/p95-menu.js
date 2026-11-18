// <p95-menu for="button-id"> — dropdown / context menu.
//   children: <button role="menuitem">, role="menuitemcheckbox" (aria-checked), <hr>
//   for="id"       the trigger button; click/Enter/Space/ArrowDown opens below it
//   data-context   attach to the parent's contextmenu event instead
// Keyboard: arrows/Home/End move, Enter/Space activate, Esc closes and returns focus, type-ahead.
// Fires "p95-select" with detail {item, value}. Menubar triggers (.p95-menubar) move with Left/Right.
import { define, rovingKey } from "./util.js";

class P95Menu extends HTMLElement {
  connectedCallback() {
    this.setAttribute("role", "menu");
    this.items.forEach((i) => i.setAttribute("tabindex", "-1"));
    this.addEventListener("keydown", (e) => this.onKey(e));
    this.addEventListener("click", (e) => {
      const item = e.target.closest("[role^='menuitem']");
      if (item && item.getAttribute("aria-disabled") !== "true") this.activate(item);
    });
    this.onDocDown = (e) => { if (this.open && !this.contains(e.target) && e.target !== this.trigger) this.close(false); };
    document.addEventListener("pointerdown", this.onDocDown);

    if (this.hasAttribute("data-context")) {
      const host = this.parentElement;
      host.addEventListener("contextmenu", (e) => { e.preventDefault(); this.show(e.clientX, e.clientY); });
      host.addEventListener("keydown", (e) => {
        if (e.key === "ContextMenu" || (e.shiftKey && e.key === "F10")) {
          e.preventDefault();
          const r = host.getBoundingClientRect();
          this.show(r.left + 8, r.top + 8);
        }
      });
    }
    const id = this.getAttribute("for");
    this.trigger = id ? document.getElementById(id) : null;
    if (this.trigger) {
      this.trigger.setAttribute("aria-haspopup", "menu");
      this.trigger.setAttribute("aria-expanded", "false");
      this.trigger.addEventListener("click", () => (this.open ? this.close() : this.showBelow()));
      this.trigger.addEventListener("keydown", (e) => {
        if (e.key === "ArrowDown") { e.preventDefault(); this.showBelow(); }
        const bar = this.trigger.closest(".p95-menubar");
        if (bar && (e.key === "ArrowRight" || e.key === "ArrowLeft")) {
          rovingKey(e, [...bar.querySelectorAll("[role='menuitem']")], this.trigger, { vertical: false });
        }
      });
    }
  }
  disconnectedCallback() { document.removeEventListener("pointerdown", this.onDocDown); }

  get items() { return [...this.querySelectorAll(":scope > [role^='menuitem']")]; }
  get enabled() { return this.items.filter((i) => i.getAttribute("aria-disabled") !== "true"); }
  get open() { return this.hasAttribute("open"); }

  showBelow() {
    const r = this.trigger.getBoundingClientRect();
    this.show(r.left, r.bottom);
  }
  show(x, y) {
    this.setAttribute("open", "");
    this.trigger?.setAttribute("aria-expanded", "true");
    const { width, height } = this.getBoundingClientRect();
    this.style.left = `${Math.max(0, Math.min(x, innerWidth - width))}px`;
    this.style.top = `${Math.max(0, Math.min(y, innerHeight - height))}px`;
    this.returnFocus = document.activeElement;
    this.enabled[0]?.focus();
  }
  close(restoreFocus = true) {
    this.removeAttribute("open");
    this.trigger?.setAttribute("aria-expanded", "false");
    if (restoreFocus) (this.trigger || this.returnFocus)?.focus?.();
  }
  activate(item) {
    if (item.getAttribute("role") === "menuitemcheckbox") {
      item.setAttribute("aria-checked", String(item.getAttribute("aria-checked") !== "true"));
    }
    this.dispatchEvent(new CustomEvent("p95-select", { bubbles: true, detail: { item, value: item.dataset.value ?? item.textContent.trim() } }));
    this.close();
  }
  onKey(e) {
    const current = document.activeElement;
    if (rovingKey(e, this.enabled, current)) return;
    if (e.key === "Escape" || e.key === "Tab") { if (e.key === "Escape") e.preventDefault(); this.close(e.key === "Escape"); return; }
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (current?.matches("[role^='menuitem']")) this.activate(current); return; }
    if (e.key.length === 1 && /\S/.test(e.key)) {   // type-ahead on first letter
      const k = e.key.toLowerCase();
      const list = this.enabled;
      const start = list.indexOf(current);
      const hit = [...list.slice(start + 1), ...list.slice(0, start + 1)].find((i) => i.textContent.trim().toLowerCase().startsWith(k));
      hit?.focus();
    }
  }
}
define("p95-menu", P95Menu);
export default P95Menu;
