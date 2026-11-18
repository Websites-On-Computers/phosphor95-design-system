// Shared helpers for Phosphor95 web components.

/** True when the user asked for reduced motion (re-checked on every call). */
export const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Read a --p95-* custom property from an element (defaults to <html>). */
export function token(name, el = document.documentElement) {
  return getComputedStyle(el).getPropertyValue(`--p95-${name}`).trim();
}

/** Parse a CSS time token ("530ms", "0.2s") to milliseconds. */
export function ms(name, el, fallback = 0) {
  const v = token(name, el);
  if (!v) return fallback;
  return v.endsWith("ms") ? parseFloat(v) : parseFloat(v) * 1000;
}

/** Define a custom element once (safe to import modules twice). */
export function define(name, cls) {
  if (!customElements.get(name)) customElements.define(name, cls);
}

let uid = 0;
export const nextId = (prefix = "p95") => `${prefix}-${++uid}`;

/** Move focus among `items` with arrow keys / Home / End. Returns true if handled. */
export function rovingKey(event, items, current, { vertical = true, wrap = true } = {}) {
  const prev = vertical ? "ArrowUp" : "ArrowLeft";
  const next = vertical ? "ArrowDown" : "ArrowRight";
  let i = items.indexOf(current);
  if (event.key === next) i = i + 1 >= items.length ? (wrap ? 0 : i) : i + 1;
  else if (event.key === prev) i = i - 1 < 0 ? (wrap ? items.length - 1 : 0) : i - 1;
  else if (event.key === "Home") i = 0;
  else if (event.key === "End") i = items.length - 1;
  else return false;
  event.preventDefault();
  items[i]?.focus();
  return true;
}
