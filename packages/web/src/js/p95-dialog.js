// <p95-dialog title="Unlock disk" level="warn" role="alertdialog" open>
//   …body… <button value="ok" data-default>OK</button> <button value="cancel">Cancel</button>
// </p95-dialog>
// Builds a native modal <dialog class="p95-window"> with a title bar and close control.
// Buttons with a `value` close the dialog and set returnValue. Esc closes (value "cancel"),
// except for role="alertdialog" without a cancel button. Enter activates [data-default].
// Fires "p95-close" with detail {value}. API: .show(), .close(value), .returnValue
import { define, nextId } from "./util.js";

const LEVEL_ICON = { info: "info", warn: "warning", error: "error" };
const LEVEL_TAG = { ok: "[ OK ]", info: "[INFO]", warn: "[WARN]", error: "[ERR ]" };

class P95Dialog extends HTMLElement {
  static observedAttributes = ["open"];

  connectedCallback() {
    if (this.dialog) return;
    const level = this.getAttribute("level");
    const titleId = nextId("dlg-title");
    const d = document.createElement("dialog");
    d.className = "p95-window";
    d.setAttribute("role", this.getAttribute("role") || "dialog");
    this.removeAttribute("role");
    d.setAttribute("aria-labelledby", titleId);
    if (level) d.dataset.level = level;

    const bar = document.createElement("header");
    bar.className = "p95-titlebar";
    const h = document.createElement("h2");
    h.className = "p95-titlebar-title";
    h.id = titleId;
    h.textContent = this.getAttribute("title") || "";
    this.removeAttribute("title");   // avoid a native tooltip on the host
    const controls = document.createElement("div");
    controls.className = "p95-titlebar-controls";
    const x = document.createElement("button");
    x.dataset.action = "close";
    x.setAttribute("aria-label", "Close");
    x.addEventListener("click", () => this.close("cancel"));
    controls.append(x);
    bar.append(h, controls);

    const body = document.createElement("div");
    body.className = "p95-window-body";
    const buttons = [...this.querySelectorAll(":scope > button")];
    const content = document.createElement("div");
    content.append(...[...this.childNodes].filter((n) => !buttons.includes(n)));
    if (level && LEVEL_ICON[level]) {
      const icon = document.createElement("img");
      icon.src = new URL(`../icons/32/${LEVEL_ICON[level]}.png`, import.meta.url).href;
      icon.alt = LEVEL_TAG[level];
      body.append(icon);
    }
    body.append(content);
    const row = document.createElement("div");
    row.className = "p95-window-buttons";
    buttons.forEach((b) => {
      b.classList.add("p95-btn");
      b.addEventListener("click", () => this.close(b.value || b.textContent.trim()));
    });
    row.append(...buttons);
    d.append(bar, body);
    if (buttons.length) d.append(row);

    d.addEventListener("cancel", (e) => {
      if (d.getAttribute("role") === "alertdialog" && !buttons.some((b) => b.value === "cancel")) { e.preventDefault(); return; }
      e.preventDefault();
      this.close("cancel");
    });
    d.addEventListener("keydown", (e) => {
      const def = row.querySelector("[data-default]");
      if (e.key === "Enter" && def && !(e.target instanceof HTMLTextAreaElement) && !(e.target instanceof HTMLButtonElement)) {
        e.preventDefault();
        def.click();
      }
    });
    this.dialog = d;
    this.append(d);
    if (this.hasAttribute("open")) this.show();
  }
  attributeChangedCallback(_n, _o, v) {
    if (!this.dialog) return;
    if (v !== null && !this.dialog.open) this.show();
    if (v === null && this.dialog.open) this.close();
  }
  show() {
    this.dialog.showModal();
    (this.dialog.querySelector("[autofocus]") || this.dialog.querySelector("[data-default]") || this.dialog.querySelector(".p95-window-body button, .p95-window-body input"))?.focus();
    if (!this.hasAttribute("open")) this.setAttribute("open", "");
  }
  close(value = "") {
    if (!this.dialog.open) return;
    this.returnValue = value;
    this.dialog.close(value);
    this.removeAttribute("open");
    this.dispatchEvent(new CustomEvent("p95-close", { bubbles: true, detail: { value } }));
  }
}
define("p95-dialog", P95Dialog);
export default P95Dialog;
