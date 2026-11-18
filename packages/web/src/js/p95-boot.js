// <p95-boot autoplay>
//   <ol><li data-level="ok">Memory test 8192K</li><li data-level="pending">Loading models</li>…</ol>
//   <progress class="p95-progress" max="100"></progress>   (optional; advanced per line)
// </p95-boot>
// Types each line at duration.type per character (POST style). Under reduced motion every
// line appears at once. The list is a polite live log. API: .play(), .skip(). Fires "p95-done".
import { define, ms, reducedMotion } from "./util.js";

class P95Boot extends HTMLElement {
  connectedCallback() {
    const list = this.querySelector("ol, ul");
    list?.setAttribute("role", "log");
    list?.setAttribute("aria-live", "polite");
    this.lines = [...this.querySelectorAll("li")];
    this.progress = this.querySelector("progress");
    this.addEventListener("click", () => this.skip());
    this.addEventListener("keydown", (e) => { if (e.key === "Escape" || e.key === "Enter") this.skip(); });
    if (this.hasAttribute("autoplay")) this.play();
  }
  disconnectedCallback() { clearTimeout(this.timer); }

  async play() {
    clearTimeout(this.timer);
    this.cancelled = false;
    const texts = this.lines.map((li) => li.textContent);
    this.texts = texts;
    if (reducedMotion()) return this.skip();
    this.lines.forEach((li) => li.setAttribute("data-pending", ""));
    const per = ms("duration-type", this, 30);
    for (let i = 0; i < this.lines.length; i++) {
      if (this.cancelled) return;
      const li = this.lines[i];
      li.removeAttribute("data-pending");
      li.setAttribute("data-typing", "");
      li.textContent = "";
      for (let c = 1; c <= texts[i].length; c++) {
        if (this.cancelled) return;
        li.textContent = texts[i].slice(0, c);
        await this.wait(per);
      }
      li.removeAttribute("data-typing");
      if (this.progress) this.progress.value = Math.round(((i + 1) / this.lines.length) * (this.progress.max || 100));
      await this.wait(per * 6);
    }
    this.done();
  }
  wait(t) { return new Promise((r) => { this.timer = setTimeout(r, t); }); }
  skip() {
    this.cancelled = true;
    clearTimeout(this.timer);
    this.lines.forEach((li, i) => {
      li.removeAttribute("data-pending");
      li.removeAttribute("data-typing");
      if (this.texts) li.textContent = this.texts[i];
    });
    if (this.progress) this.progress.value = this.progress.max || 100;
    this.done();
  }
  done() {
    if (this.finished) return;
    this.finished = true;
    this.dispatchEvent(new CustomEvent("p95-done", { bubbles: true }));
  }
}
define("p95-boot", P95Boot);
export default P95Boot;
