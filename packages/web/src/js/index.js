// @phosphor95/web — registers every component and enhances plain-HTML ones.
//   <script type="module" src="js/index.js"></script>
// or import selectively:  import "@phosphor95/web/js/p95-menu.js";
import "./p95-operator.js";
import "./p95-wordmark.js";
import "./p95-rain.js";
import "./p95-menu.js";
import "./p95-tabs.js";
import "./p95-dialog.js";
import "./p95-boot.js";
import "./p95-prompt.js";
import "./p95-palette.js";
import "./p95-toast.js";
import { enhance } from "./behaviors.js";

export { toast } from "./p95-toast.js";
export { enhance };

/** Set the theme on <html> (or any element): green | amber | white | hc. */
export function setTheme(name, el = document.documentElement) {
  el.dataset.theme = name;
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => enhance());
else enhance();
