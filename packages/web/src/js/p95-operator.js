// <p95-operator size="2" state="idle|thinking" framed label="…">
// The Operator avatar as inline SVG, so it recolours with data-theme (fills read --p95-operator-*).
// Integer scale only. "thinking" swaps the two face tones in steps, at duration.slow; it's static
// under reduced motion.
import svg from "./operator-svg.js";
import { define, ms, reducedMotion } from "./util.js";

class P95Operator extends HTMLElement {
  static observedAttributes = ["size", "state", "label"];

  connectedCallback() {
    if (!this.firstElementChild) this.innerHTML = svg;
    this.svg = this.querySelector("svg");
    this.update();
  }
  disconnectedCallback() { this.stop(); }
  attributeChangedCallback() { if (this.svg) this.update(); }

  update() {
    const size = Math.max(1, Math.round(Number(this.getAttribute("size") || 1)));
    this.style.setProperty("--_scale", size);
    const label = this.getAttribute("label");
    if (label) { this.svg.setAttribute("role", "img"); this.svg.setAttribute("aria-label", label); }
    else { this.svg.setAttribute("aria-hidden", "true"); this.svg.removeAttribute("role"); }
    this.svg.querySelector("title")?.remove();
    this.stop();
    if (this.getAttribute("state") === "thinking" && !reducedMotion()) {
      const [skin, light] = ["skin", "light"].map((r) =>
        [...this.svg.querySelectorAll("path")].find((p) => p.getAttribute("fill")?.includes(`operator-${r}`)));
      if (skin && light) {
        const a = skin.getAttribute("fill"), b = light.getAttribute("fill");
        let flip = false;
        this.timer = setInterval(() => {
          flip = !flip;
          skin.setAttribute("fill", flip ? b : a);
          light.setAttribute("fill", flip ? a : b);
        }, ms("duration-slow", this, 400));
        this.restore = () => { skin.setAttribute("fill", a); light.setAttribute("fill", b); };
      }
    }
  }
  stop() { clearInterval(this.timer); this.restore?.(); this.restore = null; }
}
define("p95-operator", P95Operator);
export default P95Operator;
