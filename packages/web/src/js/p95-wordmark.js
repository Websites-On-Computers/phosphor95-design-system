// <p95-wordmark size="2"> — PHOSPHOR95▮ as inline SVG (fills read --p95-text-primary), so it
// recolours with data-theme. Integer scale only.
import svg from "./wordmark-svg.js";
import { define } from "./util.js";

class P95Wordmark extends HTMLElement {
  static observedAttributes = ["size"];
  connectedCallback() {
    if (!this.firstElementChild) this.innerHTML = svg;
    const s = this.querySelector("svg");
    s.setAttribute("role", "img");
    s.setAttribute("aria-label", this.getAttribute("label") || "PHOSPHOR95");
    s.querySelector("title")?.remove();
    this.update();
  }
  attributeChangedCallback() { this.update(); }
  update() { this.style.setProperty("--_scale", Math.max(1, Math.round(Number(this.getAttribute("size") || 2)))); }
}
define("p95-wordmark", P95Wordmark);
export default P95Wordmark;
