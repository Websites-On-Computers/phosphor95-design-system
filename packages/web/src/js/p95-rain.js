// <p95-rain density="0.6" speed="1"> — digital rain on a canvas behind its parent's content.
// Cheap by design: 20 fps (duration.tick), one glyph per column per frame, a translucent fade
// instead of redrawing trails. Pauses when hidden or off-screen. Under reduced motion it paints
// one static frame. Colours come from the theme ramp (--p95-color-phosphor-*).
import { define, ms, reducedMotion, token } from "./util.js";

const GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789:=*+-<>";
const CELL_W = 8, CELL_H = 16;

class P95Rain extends HTMLElement {
  connectedCallback() {
    this.setAttribute("aria-hidden", "true");
    this.canvas = document.createElement("canvas");
    this.append(this.canvas);
    this.ctx = this.canvas.getContext("2d");
    this.ro = new ResizeObserver(() => this.resize());
    this.ro.observe(this);
    this.io = new IntersectionObserver(([e]) => { this.visible = e.isIntersecting; this.loop(); });
    this.io.observe(this);
    this.onVis = () => this.loop();
    document.addEventListener("visibilitychange", this.onVis);
    this.mq = matchMedia("(prefers-reduced-motion: reduce)");
    this.mq.addEventListener("change", this.onVis);
    this.resize();
  }
  disconnectedCallback() {
    this.ro.disconnect(); this.io.disconnect();
    document.removeEventListener("visibilitychange", this.onVis);
    this.mq.removeEventListener("change", this.onVis);
    clearTimeout(this.timer);
  }
  colours() {
    const c = (n) => token(`color-phosphor-${n}`, this) || "#33ff66";
    return { bg: token("surface-base", this) || "#020a04", dim: c(7), mid: c(8), head: c(12) };
  }
  resize() {
    const { width, height } = this.getBoundingClientRect();
    this.cols = Math.ceil(width / CELL_W);
    this.rows = Math.ceil(height / CELL_H);
    this.canvas.width = this.cols * CELL_W;
    this.canvas.height = this.rows * CELL_H;
    const density = Number(this.getAttribute("density") ?? token("effect-rain-density", this) ?? 0.6);
    this.drops = Array.from({ length: this.cols }, () =>
      Math.random() < density ? -Math.floor(Math.random() * this.rows) : null);
    this.pal = this.colours();
    this.ctx.fillStyle = this.pal.bg;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.font = `${CELL_H}px "PxPlus IBM VGA 8x16", monospace`;
    this.ctx.textBaseline = "top";
    // Pre-warm so the first paint already looks like rain, then animate (or stay static).
    for (let i = 0; i < this.rows; i++) this.step();
    if (reducedMotion()) this.staticFrame(); else this.loop();
  }
  staticFrame() {
    for (let i = 0; i < this.rows * 1.5; i++) this.step(true);
  }
  step(noFade = false) {
    const { ctx, pal } = this;
    if (!noFade) {
      ctx.globalAlpha = 0.18;
      ctx.fillStyle = pal.bg;
      ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      ctx.globalAlpha = 1;
    }
    for (let x = 0; x < this.cols; x++) {
      let y = this.drops[x];
      if (y === null) continue;
      if (y >= 0) {
        const g = GLYPHS[(Math.random() * GLYPHS.length) | 0];
        ctx.fillStyle = pal.mid;   // repaint the previous head as body
        if (y > 0) ctx.fillText(GLYPHS[(Math.random() * GLYPHS.length) | 0], x * CELL_W, (y - 1) * CELL_H);
        ctx.fillStyle = pal.head;
        ctx.fillText(g, x * CELL_W, y * CELL_H);
      }
      y += 1;
      if (y > this.rows && Math.random() > 0.975) y = -Math.floor(Math.random() * 20);
      this.drops[x] = y > this.rows + 20 ? -Math.floor(Math.random() * 20) : y;
    }
  }
  loop() {
    clearTimeout(this.timer);
    if (reducedMotion() || document.hidden || this.visible === false) return;
    this.step();
    const speed = Number(this.getAttribute("speed") || 1);
    this.timer = setTimeout(() => this.loop(), ms("duration-tick", this, 50) / speed);
  }
}
define("p95-rain", P95Rain);
export default P95Rain;
