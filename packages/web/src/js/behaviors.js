// Progressive enhancements for plain-HTML components (no custom element needed):
//   .p95-switch      toggles aria-checked on click; fires "change"
//   .p95-splitter    drag or arrow keys resize the previous sibling (role="separator")
//   .p95-tooltip     shown on hover/focus of the element that references it via aria-describedby
//   .p95-list[role=listbox]  single-select with arrows, Home/End, click
// Call enhance(root) after inserting new markup; index.js runs it once on load.
import { rovingKey } from "./util.js";

export function enhance(root = document) {
  root.querySelectorAll(".p95-switch:not([data-p95])").forEach((sw) => {
    sw.dataset.p95 = "";
    sw.setAttribute("role", "switch");
    if (!sw.hasAttribute("aria-checked")) sw.setAttribute("aria-checked", "false");
    sw.addEventListener("click", () => {
      sw.setAttribute("aria-checked", String(sw.getAttribute("aria-checked") !== "true"));
      sw.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });

  root.querySelectorAll(".p95-splitter:not([data-p95])").forEach((sp) => {
    sp.dataset.p95 = "";
    const split = sp.parentElement;
    const vertical = split.dataset.orientation === "vertical";
    sp.setAttribute("aria-orientation", vertical ? "horizontal" : "vertical");
    const pane = sp.previousElementSibling;
    const size = () => (vertical ? pane.getBoundingClientRect().height : pane.getBoundingClientRect().width);
    const total = () => (vertical ? split.clientHeight : split.clientWidth);
    const set = (px) => {
      const clamped = Math.max(48, Math.min(total() - 48, px));
      pane.style.flex = `0 0 ${clamped}px`;
      sp.setAttribute("aria-valuenow", String(Math.round((clamped / total()) * 100)));
    };
    sp.addEventListener("pointerdown", (e) => {
      sp.setPointerCapture(e.pointerId);
      sp.dataset.dragging = "";
      const start = vertical ? e.clientY : e.clientX, from = size();
      const move = (ev) => set(from + (vertical ? ev.clientY : ev.clientX) - start);
      const up = () => { sp.removeEventListener("pointermove", move); delete sp.dataset.dragging; };
      sp.addEventListener("pointermove", move);
      sp.addEventListener("pointerup", up, { once: true });
    });
    sp.addEventListener("keydown", (e) => {
      const step = e.shiftKey ? 64 : 16;
      const dec = vertical ? "ArrowUp" : "ArrowLeft", inc = vertical ? "ArrowDown" : "ArrowRight";
      if (e.key === dec) { e.preventDefault(); set(size() - step); }
      if (e.key === inc) { e.preventDefault(); set(size() + step); }
    });
  });

  root.querySelectorAll(".p95-tooltip[id]:not([data-p95])").forEach((tip) => {
    tip.dataset.p95 = "";
    tip.setAttribute("role", "tooltip");
    const target = document.querySelector(`[aria-describedby~="${tip.id}"]`);
    if (!target) return;
    let timer;
    const show = () => {
      timer = setTimeout(() => {
        tip.dataset.open = "";
        const r = target.getBoundingClientRect();
        tip.style.left = `${r.left + scrollX}px`;
        tip.style.top = `${r.bottom + scrollY + 4}px`;
      }, 400);
    };
    const hide = () => { clearTimeout(timer); delete tip.dataset.open; };
    target.addEventListener("pointerenter", show);
    target.addEventListener("pointerleave", hide);
    target.addEventListener("focus", show);
    target.addEventListener("blur", hide);
    target.addEventListener("keydown", (e) => { if (e.key === "Escape") hide(); });
    if (tip.parentElement !== document.body) document.body.append(tip);
  });

  root.querySelectorAll(".p95-list[role='listbox']:not([data-p95])").forEach((list) => {
    list.dataset.p95 = "";
    const opts = () => [...list.querySelectorAll("[role='option']:not([aria-disabled='true'])")];
    if (!list.hasAttribute("tabindex")) list.tabIndex = 0;
    const select = (o) => {
      if (!o) return;
      list.querySelectorAll("[aria-selected='true']").forEach((x) => x.setAttribute("aria-selected", "false"));
      o.setAttribute("aria-selected", "true");
      o.id ||= `p95-opt-${Math.random().toString(36).slice(2, 8)}`;
      list.setAttribute("aria-activedescendant", o.id);
      o.scrollIntoView({ block: "nearest" });
      list.dispatchEvent(new CustomEvent("p95-change", { bubbles: true, detail: { option: o } }));
    };
    list.addEventListener("click", (e) => select(e.target.closest("[role='option']:not([aria-disabled='true'])")));
    list.addEventListener("keydown", (e) => {
      const all = opts();
      const cur = list.querySelector("[aria-selected='true']") || all[0];
      const fake = { focus() {} };
      const items = all.map((o) => ({ o, focus() { select(o); } }));
      const curItem = items.find((i) => i.o === cur) || fake;
      rovingKey(e, items, curItem, { wrap: false });
    });
  });
}
