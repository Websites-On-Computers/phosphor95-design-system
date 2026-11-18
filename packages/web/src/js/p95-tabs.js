// <p95-tabs> — wires the ARIA tabs pattern onto light-DOM children:
//   <div role="tablist"><button role="tab">General</button>…</div>
//   <section role="tabpanel">…</section>…   (panels in the same order as tabs)
// Arrow keys move and select (automatic activation); Home/End jump. Fires "p95-change" {index}.
import { define, nextId, rovingKey } from "./util.js";

class P95Tabs extends HTMLElement {
  connectedCallback() {
    const tabs = this.tabs, panels = this.panels;
    tabs.forEach((tab, i) => {
      const panel = panels[i];
      tab.id ||= nextId("tab");
      if (panel) {
        panel.id ||= nextId("panel");
        tab.setAttribute("aria-controls", panel.id);
        panel.setAttribute("aria-labelledby", tab.id);
        panel.tabIndex = 0;
      }
      tab.addEventListener("click", () => this.select(i));
    });
    this.querySelector("[role='tablist']")?.addEventListener("keydown", (e) => {
      if (rovingKey(e, this.tabs, document.activeElement, { vertical: false })) this.select(this.tabs.indexOf(document.activeElement), false);
    });
    const initial = Math.max(0, tabs.findIndex((t) => t.getAttribute("aria-selected") === "true"));
    this.select(initial, false, true);
  }
  get tabs() { return [...this.querySelectorAll("[role='tab']")]; }
  get panels() { return [...this.querySelectorAll(":scope > [role='tabpanel']")]; }
  select(index, focus = true, silent = false) {
    this.tabs.forEach((t, i) => {
      const on = i === index;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
      if (this.panels[i]) this.panels[i].hidden = !on;
    });
    if (focus) this.tabs[index]?.focus();
    if (!silent) this.dispatchEvent(new CustomEvent("p95-change", { bubbles: true, detail: { index } }));
  }
}
define("p95-tabs", P95Tabs);
export default P95Tabs;
