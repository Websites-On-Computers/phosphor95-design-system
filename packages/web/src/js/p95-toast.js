// <p95-toast level="ok|info|warn|error" title="Saved" timeout="5000">Message</p95-toast>
// and the helper  toast({ level, title, message, timeout })  which creates the region on demand.
// The region (.p95-toasts) is a polite live region; errors are role="alert". Toasts don't
// steal focus. Hovering or focusing one pauses its timeout.
import { define } from "./util.js";

const TAG = { ok: "[ OK ]", info: "[INFO]", warn: "[WARN]", error: "[ERR ]" };

class P95Toast extends HTMLElement {
  connectedCallback() {
    if (this.built) return;
    this.built = true;
    const level = this.getAttribute("level") || "info";
    if (level === "error") this.setAttribute("role", "alert");
    const title = document.createElement("span");
    title.className = "p95-toast-title";
    title.textContent = `${TAG[level] || ""} ${this.getAttribute("title") || ""}`.trim();
    const msg = document.createElement("span");
    msg.className = "p95-toast-message";
    msg.append(...this.childNodes);
    const close = document.createElement("button");
    close.setAttribute("aria-label", "Dismiss");
    close.addEventListener("click", () => this.dismiss());
    this.append(title, close);
    if (msg.textContent.trim()) this.append(msg);
    const t = Number(this.getAttribute("timeout") ?? (level === "error" ? 0 : 6000));
    if (t > 0) {
      let left = t, started = Date.now(), timer = setTimeout(() => this.dismiss(), left);
      const pause = () => { clearTimeout(timer); left -= Date.now() - started; };
      const resume = () => { started = Date.now(); timer = setTimeout(() => this.dismiss(), Math.max(1000, left)); };
      this.addEventListener("pointerenter", pause);
      this.addEventListener("pointerleave", resume);
      this.addEventListener("focusin", pause);
      this.addEventListener("focusout", resume);
    }
  }
  dismiss() { this.dispatchEvent(new CustomEvent("p95-dismiss", { bubbles: true })); this.remove(); }
}
define("p95-toast", P95Toast);

export function toast({ level = "info", title = "", message = "", timeout } = {}) {
  let region = document.querySelector(".p95-toasts");
  if (!region) {
    region = document.createElement("div");
    region.className = "p95-toasts";
    region.setAttribute("role", "status");
    region.setAttribute("aria-live", "polite");
    document.body.append(region);
  }
  const t = document.createElement("p95-toast");
  t.setAttribute("level", level);
  t.setAttribute("title", title);
  if (timeout !== undefined) t.setAttribute("timeout", String(timeout));
  t.textContent = message;
  region.append(t);
  return t;
}
export default P95Toast;
