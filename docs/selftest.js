// In-page self-test for the web components: open the gallery with ?selftest.
// Synchronous on purpose so a headless screenshot (taken at "load") captures the results.
const results = [];
const errors = [];
addEventListener("error", (e) => errors.push(e.message));
addEventListener("unhandledrejection", (e) => errors.push(String(e.reason)));

function check(name, fn) {
  try {
    const ok = fn();
    results.push([ok === false ? "FAIL" : "PASS", name]);
  } catch (err) {
    results.push(["FAIL", `${name}: ${err.message}`]);
  }
}
const key = (el, k, opts = {}) => el.dispatchEvent(new KeyboardEvent("keydown", { key: k, bubbles: true, cancelable: true, ...opts }));
const assert = (c, msg) => { if (!c) throw new Error(msg || "assertion failed"); };
const css = (el, prop) => getComputedStyle(el).getPropertyValue(prop).trim();

export function run() {
  check("all custom elements defined", () => {
    const names = ["p95-operator", "p95-wordmark", "p95-rain", "p95-menu", "p95-tabs", "p95-dialog", "p95-boot", "p95-prompt", "p95-palette", "p95-toast"];
    const missing = names.filter((n) => !customElements.get(n));
    assert(!missing.length, `missing ${missing}`);
  });

  check("theming works on a subtree (data-theme on a div)", () => {
    const d = document.createElement("div");
    d.dataset.theme = "amber";
    const p = document.createElement("p");
    d.append(p);
    document.body.append(d);
    const c = getComputedStyle(p).color;
    d.remove();
    assert(c === "rgb(255, 176, 0)", `text in amber subtree is ${c}`);
  });

  check("bevel recipe re-resolves in a themed subtree", () => {
    const d = document.createElement("div");
    d.dataset.theme = "white";
    document.body.append(d);
    const v = css(d, "--p95-bevel-raised");
    d.remove();
    assert(!v.includes("var("), "recipe not computed");
  });

  check("operator recolours with theme", () => {
    const d = document.createElement("div");
    d.dataset.theme = "amber";
    d.innerHTML = "<p95-operator></p95-operator>";
    document.body.append(d);
    const path = [...d.querySelectorAll("path")].find((x) => x.getAttribute("fill").includes("operator-skin"));
    const fill = getComputedStyle(path).fill;
    d.remove();
    assert(fill === "rgb(255, 205, 130)", `amber skin is ${fill}`);
  });

  check("dialog: show focuses default, close sets returnValue + event", () => {
    const dlg = document.querySelector("#alert");
    let value = null;
    dlg.addEventListener("p95-close", (e) => { value = e.detail.value; }, { once: true });
    dlg.show();
    assert(dlg.dialog.open, "not open");
    assert(document.activeElement?.dataset.default !== undefined, `focus on ${document.activeElement?.textContent}`);
    dlg.close("cancel");
    assert(!dlg.dialog.open && value === "cancel" && dlg.returnValue === "cancel", "close failed");
  });

  check("menu: open from trigger, arrows, Esc returns focus", () => {
    const trigger = document.querySelector("#m-file");
    const menu = document.querySelector("p95-menu[for='m-file']");
    trigger.click();
    assert(menu.hasAttribute("open") && trigger.getAttribute("aria-expanded") === "true", "not open");
    const items = menu.enabled;
    assert(document.activeElement === items[0], "first item not focused");
    key(menu, "ArrowDown");
    assert(document.activeElement === items[1], "ArrowDown did not move");
    key(menu, "End");
    assert(document.activeElement === items.at(-1), "End did not move (disabled items skipped?)");
    key(menu, "Escape");
    assert(!menu.hasAttribute("open") && document.activeElement === trigger, "Esc did not close/restore");
  });

  check("menu: checkbox item toggles aria-checked", () => {
    const menu = document.querySelector("p95-menu[for='m-view']");
    const item = menu.querySelector("[role='menuitemcheckbox'][aria-checked='false']");
    menu.showBelow();
    item.click();
    assert(item.getAttribute("aria-checked") === "true", "not toggled");
    item.setAttribute("aria-checked", "false");
  });

  check("tabs: select(1) shows panel 1, roving tabindex", () => {
    const tabs = document.querySelector("p95-tabs");
    tabs.select(1, false);
    assert(!tabs.panels[1].hidden && tabs.panels[0].hidden, "panels wrong");
    assert(tabs.tabs[1].tabIndex === 0 && tabs.tabs[0].tabIndex === -1, "tabindex wrong");
    tabs.select(0, false);
  });

  check("palette: filter + Enter runs command", () => {
    const pal = document.querySelector("p95-palette");
    let cmd = null;
    const h = (e) => { cmd = e.detail.command; e.stopImmediatePropagation(); };
    document.addEventListener("p95-command", h, { capture: true, once: true });
    pal.show();
    pal.input.value = "high";
    pal.input.dispatchEvent(new Event("input"));
    assert(pal.options.length === 1, `${pal.options.length} options`);
    key(pal.input, "Enter");
    assert(cmd === "theme-hc", `ran ${cmd}`);
    assert(!pal.dialog.open, "still open");
  });

  check("toast: helper creates region + tagged title", async () => {
    const mod = window.__p95;
    const t = mod.toast({ level: "warn", title: "Self-test", timeout: 0 });
    assert(document.querySelector(".p95-toasts[role='status']"), "no region");
    assert(t.querySelector(".p95-toast-title").textContent.startsWith("[WARN]"), "no tag");
    t.dismiss();
  });

  check("prompt: Enter fires p95-command and echoes", () => {
    const p = document.querySelector("#prompt");
    let got = null;
    p.addEventListener("p95-command", (e) => { got = e.detail.value; e.stopImmediatePropagation(); }, { capture: true, once: true });
    p.input.value = "selftest";
    key(p.input, "Enter");
    assert(got === "selftest", `got ${got}`);
    assert(p.log.lastElementChild.textContent === "selftest", "no echo");
    p.log.lastElementChild.remove();
    key(p.input, "ArrowUp");
    assert(p.input.value === "selftest", "history");
    p.input.value = "";
  });

  check("boot: skip() reveals all lines, fills progress, fires done", () => {
    const b = document.querySelector("#boot");
    let done = false;
    b.finished = false;
    b.addEventListener("p95-done", () => { done = true; }, { once: true });
    b.skip();
    assert(b.lines.every((li) => !li.hasAttribute("data-pending")), "pending lines");
    assert(b.progress.value === b.progress.max, "progress");
    assert(done, "no done event");
  });

  check("switch toggles aria-checked", () => {
    const sw = document.querySelector("[aria-labelledby='sw-l']");
    const before = sw.getAttribute("aria-checked");
    sw.click();
    assert(sw.getAttribute("aria-checked") !== before, "no toggle");
    sw.click();
  });

  check("listbox: ArrowDown selects next option", () => {
    const list = document.querySelector(".p95-list[role='listbox']");
    const opts = [...list.querySelectorAll("[role='option']")];
    const i = opts.findIndex((o) => o.getAttribute("aria-selected") === "true");
    key(list, "ArrowDown");
    assert(opts[i + 1].getAttribute("aria-selected") === "true", "not moved");
    key(list, "ArrowUp");
  });

  check("closed dialogs are not rendered", () => {
    const d = document.querySelector("p95-palette dialog");
    assert(getComputedStyle(d).display === "none", `display ${getComputedStyle(d).display}`);
  });

  check("pixel font loaded", () => document.fonts.check('16px "PxPlus IBM VGA 8x16"'));

  check("no uncaught errors", () => { assert(!errors.length, errors.join("; ")); });

  const pass = results.filter((r) => r[0] === "PASS").length;
  const panel = document.createElement("section");
  panel.className = "p95-window";
  panel.dataset.active = "";
  panel.style.cssText = "position:fixed;top:8px;left:8px;z-index:9999;max-width:560px";
  panel.innerHTML = `<header class="p95-titlebar"><span class="p95-titlebar-title">SELFTEST ${pass}/${results.length}</span></header>
    <div class="p95-window-body">${results.map(([s, n]) =>
      `<div class="p95-bootline" data-level="${s === "PASS" ? "ok" : "error"}">${n.replace(/</g, "&lt;")}</div>`).join("")}</div>`;
  document.body.append(panel);
  document.title = `SELFTEST ${pass}/${results.length}`;
  scrollTo(0, 0);
}
