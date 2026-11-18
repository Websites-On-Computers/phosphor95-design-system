// Gallery wiring: theme switcher, CRT toggle, demos. Uses only the public package API.
import * as p95 from "./web/js/index.js";
const { setTheme, toast } = p95;

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const THEMES = ["green", "amber", "white", "hc"];

function applyTheme(name) {
  if (!THEMES.includes(name)) return;
  setTheme(name);
  $$("[data-theme-set]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.themeSet === name)));
  try { localStorage.setItem("p95-theme", name); } catch {}
  renderSwatches();
}
$$("[data-theme-set]").forEach((b) => b.addEventListener("click", () => applyTheme(b.dataset.themeSet)));

const crt = $("#crt");
function applyCrt(on) {
  document.body.classList.toggle("p95-crt", on);
  document.body.classList.toggle("p95-crt-fixed", on);
  crt.setAttribute("aria-checked", String(on));
}
crt.addEventListener("change", () => applyCrt(crt.getAttribute("aria-checked") === "true"));

// Toggle buttons
$$("[data-toggle]").forEach((b) => b.addEventListener("click", () => b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true"))));
$$("[data-toggle-group]").forEach((b) => b.addEventListener("click", () => {
  $$("[data-toggle-group]", b.parentElement).forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
}));

// Slider output, spin box
const temp = $("#temp");
temp.addEventListener("input", () => { $("#temp-out").textContent = temp.value; });
$$("[data-spin]").forEach((b) => b.addEventListener("click", () => {
  const s = $("#spin");
  s.value = Math.min(+s.max, Math.max(+s.min, +s.value + +b.dataset.spin));
}));

// Toasts, alert
const TOASTS = {
  ok: { level: "ok", title: "3 files saved", message: "~/Documents/phosphor" },
  warn: { level: "warn", title: "Battery 9%", message: "Save your work." },
  error: { level: "error", title: "Brain unreachable", message: "node-01 did not answer (5 s). Local commands still work." },
};
$$("[data-toast]").forEach((b) => b.addEventListener("click", () => toast(TOASTS[b.dataset.toast])));
$("#show-alert").addEventListener("click", () => $("#alert").show());
$("#alert").addEventListener("p95-close", (e) => {
  if (e.detail.value === "delete") toast({ level: "ok", title: "3 files deleted" });
});

// Palette
$("#open-palette").addEventListener("click", () => $("p95-palette").show());
document.addEventListener("p95-command", (e) => {
  const c = e.detail.command;
  if (!c) return;
  if (c.startsWith("theme-")) applyTheme(c.slice(6));
  if (c === "crt") applyCrt(crt.getAttribute("aria-checked") !== "true");
  if (c === "toast") toast(TOASTS.ok);
  if (c === "alert") $("#alert").show();
  if (c === "boot") { const b = $("#boot"); b.finished = false; b.play(); }
});

// Prompt demo: tiny canned "rules router"
const prompt = $("#prompt");
prompt.addEventListener("p95-command", (e) => {
  e.stopPropagation();
  const v = e.detail.value.toLowerCase();
  prompt.busy = true;
  setTimeout(() => {
    prompt.busy = false;
    if (v === "time") prompt.print(new Date().toTimeString().slice(0, 5), "ok");
    else if (v === "status") { prompt.print("CPU 12% · MEM 540 MB · UPLINK 62%", "info"); }
    else if (v.startsWith("theme ")) { applyTheme(v.slice(6)); prompt.print(`THEME ${v.slice(6).toUpperCase()}`, "ok"); }
    else if (v === "help") prompt.print("time · status · theme green|amber|white|hc · clear");
    else if (v === "clear") prompt.querySelector(".p95-prompt-log").replaceChildren();
    else prompt.print(`UNKNOWN COMMAND "${v}". Try help.`, "warn");
  }, 300);
});

// Swatches, read live from the theme
const JOBS = ["base", "shadow", "face", "face hover", "subtle sel.", "faint", "border", "dim", "solid", "phosphor", "bright", "glow"];
function swatch(name, varName, sub) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
  const probe = document.createElement("div");
  probe.style.color = v;
  document.body.append(probe);
  const rgb = getComputedStyle(probe).color.match(/\d+/g).slice(0, 3).map(Number);
  probe.remove();
  const hex = "#" + rgb.map((n) => n.toString(16).padStart(2, "0")).join("");
  return `<div class="swatch"><div class="swatch-chip"><div style="background:var(${varName})"></div></div>${name}<code>${sub ? sub + " " : ""}${hex}</code></div>`;
}
function renderSwatches() {
  $("#ramp").innerHTML = JOBS.map((j, i) => swatch(`${i + 1} ${j}`, `--p95-color-phosphor-${i + 1}`)).join("");
  const TAG = { ok: "[ OK ]", info: "[INFO]", warn: "[WARN]", error: "[ERR ]" };
  $("#status").innerHTML = Object.entries(TAG).map(([s, tag]) => swatch(tag, `--p95-status-${s}-fg`)).join("");
}

let saved = null;
try { saved = localStorage.getItem("p95-theme"); } catch {}
const fromUrl = new URLSearchParams(location.search).get("theme");
applyTheme(fromUrl || saved || "green");
if (new URLSearchParams(location.search).has("crt")) applyCrt(true);

// ?open=alert|palette|menu|toasts  (for screenshots and reviews)
const open = new URLSearchParams(location.search).get("open");
if (open === "alert") $("#alert").show();
if (open === "palette") { const p = $("p95-palette"); p.show(); p.input.value = "theme"; p.input.dispatchEvent(new Event("input")); }
if (open === "menu") { $("p95-menu[for='m-file']").show(480, 260); $("p95-menu[for='m-file']").enabled[1].focus(); }
if (open === "toasts") Object.values(TOASTS).forEach((t) => toast({ ...t, timeout: 0 }));

if (new URLSearchParams(location.search).has("selftest")) {
  window.__p95 = p95;
  await document.fonts.ready;
  (await import("./selftest.js")).run();
}
