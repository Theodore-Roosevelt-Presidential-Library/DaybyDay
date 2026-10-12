/*! Today in Theodore Roosevelt's life | rotating widget | Theodore Roosevelt Presidential Library | MIT
 *
 *   <div data-trpl-today data-layout="banner"></div>
 *   <script src="https://daybyday.labs.trlibrary.com/widgets/today.js" async></script>
 *
 * Attributes (all optional):
 *   data-layout    banner | card | wall | inline     (default banner)
 *   data-date      MM-DD to show a fixed date        (default: today, visitor's clock)
 *   data-count     how many years to cycle or show   (default 6; wall default 3)
 *   data-min       lowest significance to include, 1-5 (default 1)
 *   data-interval  seconds between slides, 0 = off   (default 9)
 *   data-theme     auto | light | dark — names the BACKGROUND (default auto)
 *   data-text      white | dark — names the TEXT; wins over data-theme
 *   data-align     left | center                     (default center for banner)
 *   data-height    fixed | auto                      (default fixed: reserves the tallest slide)
 *   data-cta       off to hide the "Plan your visit" link
 *   data-api       API base URL                      (default: the published Day by Day API)
 *
 * Mirrors the visitor-quotes widget (reviews.labs.trlibrary.com): renders in a shadow root so
 * Drupal/Bootstrap styles can't reach in; reads the background it lands on and picks light or
 * dark text by luminance (photo/video/gradient backgrounds get white text with a soft shadow);
 * rotation pauses when off screen, when the tab is hidden, on hover or focus, and for reduced
 * motion. Slides are each year's entry for the date, biggest days first. Roosevelt quotations
 * are deliberately left out until they are verified against the originals.
 */
(function () {
  "use strict";
  var SCRIPT = document.currentScript;
  var BASE = SCRIPT ? new URL("../", SCRIPT.src).href : "https://daybyday.labs.trlibrary.com/";
  var MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  var ACCENT = "#E7805D", ACCENT_ON_DARK = "#FC924E";
  var cache = {};

  function get(url) {
    if (!cache[url]) cache[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
    return cache[url];
  }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function todayMD() { var t = new Date(); return ("0" + (t.getMonth() + 1)).slice(-2) + "-" + ("0" + t.getDate()).slice(-2); }

  function parseRGB(s) { var m = (s || "").match(/[\d.]+/g); return m ? m.map(Number) : null; }
  function luminance(rgb) {
    var c = rgb.slice(0, 3).map(function (v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  /** Walk up until something paints: an opaque colour, or an image/gradient/media we can't measure. */
  function backdrop(el) {
    for (var n = el.parentElement; n; n = n.parentElement) {
      var cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== "none") return { media: true };
      if (n.querySelector(":scope > video, :scope > picture, :scope > img.bg, :scope > .background-media")) return { media: true };
      var rgb = parseRGB(cs.backgroundColor);
      if (rgb && (rgb.length < 4 || rgb[3] > 0.5)) return { rgb: rgb };
    }
    return { rgb: [255, 255, 255] };
  }

  function css(dark, media, align) {
    var ink = dark ? "#FFFFFF" : "#25282A", muted = dark ? "rgba(255,255,255,.78)" : "#4A4F52";
    var accent = dark ? ACCENT_ON_DARK : ACCENT, line = dark ? "rgba(255,255,255,.28)" : "#D1CCBD";
    return [
      ":host{display:block}",
      ".w{color:" + ink + ";text-align:" + align + ";font-family:var(--dbd-serif,'ITC Clearface','Clearface','Lora',Georgia,serif)" + (media ? ";text-shadow:0 1px 3px rgba(0,0,0,.55)" : "") + "}",
      ".label{font:600 13px/1.3 var(--dbd-sans,'Frutiger Next','Source Sans 3',system-ui,sans-serif);color:" + muted + ";margin:0 0 .5rem}",
      ".stage{position:relative;transition:opacity .32s ease}",
      ".stage.out{opacity:0}",
      ".slide{display:block}",
      ".yr{font:700 clamp(2.2rem,5vw,3.4rem)/.95 var(--dbd-display,'Dharma Gothic E','Oswald','Arial Narrow',sans-serif);color:" + accent + ";letter-spacing:.01em;margin:0}",
      ".meta{font:13px/1.4 var(--dbd-sans,'Frutiger Next','Source Sans 3',system-ui,sans-serif);color:" + muted + ";margin:.35rem 0 .6rem}",
      ".h{font-weight:700;font-size:1.3rem;line-height:1.25;margin:0 0 .35rem;color:inherit;text-decoration:none;display:inline-block}",
      "a.h:hover,a.h:focus-visible{text-decoration:underline}",
      ".s{font-size:1.05rem;line-height:1.55;margin:0 auto;max-width:62ch}",
      ".w.left .s{margin:0}",
      ".foot{display:flex;gap:1rem;justify-content:" + (align === "center" ? "center" : "space-between") + ";flex-wrap:wrap;margin-top:1rem;font:600 13px var(--dbd-sans,'Source Sans 3',system-ui,sans-serif)}",
      ".foot a{color:" + (dark ? "#FFFFFF" : "#1B4532") + "}",
      ".dots{display:flex;gap:.45rem;margin-top:1rem;justify-content:" + (align === "center" ? "center" : "flex-start") + "}",
      ".dots button{all:unset;cursor:pointer;width:9px;height:9px;border-radius:50%;background:" + line + "}",
      ".dots button[aria-current=true]{background:" + accent + "}",
      ".dots button:focus-visible,:focus-visible{outline:3px solid " + accent + ";outline-offset:2px}",
      ".card{border:1px solid " + line + ";border-top:5px solid " + accent + ";padding:1.25rem 1.4rem;background:" + (dark ? "transparent" : "#FFFFFF") + "}",
      ".inline{border-left:4px solid " + accent + ";padding:.2rem 0 .2rem 1rem}",
      ".inline .yr{font-size:1.6rem}.inline .h{font-size:1.1rem}",
      ".wall{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.5rem;text-align:left}",
      ".wall .slide{border-top:3px solid " + accent + ";padding-top:.8rem}",
      ".wall .yr{font-size:2.2rem}.wall .h{font-size:1.1rem}.wall .s{font-size:.98rem}",
      "@media (prefers-reduced-motion:reduce){.stage{transition:none}}"
    ].join("");
  }

  function slideHTML(x, base) {
    var parts = x.date.split("-");
    return '<div class="slide"><p class="yr">' + parts[0] + '</p>' +
      '<div class="meta">' + MONTHS[+parts[1] - 1] + " " + (+parts[2]) + ", " + parts[0] + " | Age " + x.age + (x.location ? " | " + esc(x.location) : "") + "</div>" +
      '<a class="h" href="' + base + "day.html?date=" + x.date + '" target="_top">' + esc(x.headline) + "</a>" +
      '<p class="s">' + esc(x.summary) + "</p></div>";
  }

  function mount(host) {
    if (host.__trplToday) return;
    host.__trplToday = true;
    var root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;
    var layout = (host.getAttribute("data-layout") || "banner").toLowerCase();
    var api = host.getAttribute("data-api") || BASE + "api/v1/";
    var md = host.getAttribute("data-date") || todayMD();
    var count = parseInt(host.getAttribute("data-count") || (layout === "wall" ? "3" : "6"), 10);
    var min = parseInt(host.getAttribute("data-min") || "1", 10);
    var interval = host.hasAttribute("data-interval") ? parseFloat(host.getAttribute("data-interval")) * 1000 : 9000;
    var align = (host.getAttribute("data-align") || (layout === "banner" ? "center" : "left")).toLowerCase();
    var themeAttr = (host.getAttribute("data-theme") || "auto").toLowerCase();
    var textAttr = (host.getAttribute("data-text") || "").toLowerCase();
    var back = backdrop(host);
    var dark = back.media ? true : luminance(back.rgb) < 0.45;
    if (themeAttr === "dark") dark = true; else if (themeAttr === "light") dark = false;
    if (textAttr === "white") dark = true; else if (textAttr === "dark") dark = false;
    var media = back.media && textAttr !== "dark" && themeAttr === "auto";

    get(api + "on-this-day/" + md + ".json").then(function (o) {
      var days = o.days.filter(function (d) { return d.significance >= min && d.headline; }).slice(0, Math.max(1, count));
      days.sort(function (a, b) { return a.date < b.date ? -1 : 1; });
      if (!days.length) { host.style.display = "none"; return; }
      var p = md.split("-");
      var label = '<p class="label">' + (host.hasAttribute("data-date") ? MONTHS[+p[0] - 1] + " " + (+p[1]) : "Today") + " in Theodore Roosevelt's life</p>";
      var cta = host.getAttribute("data-cta") === "off" ? "" : '<a href="https://www.trlibrary.com/visit" target="_top">Plan your visit</a>';
      var foot = '<div class="foot"><a href="' + BASE + '" target="_top">Every day of his life</a>' + cta + "</div>";
      var shell = '<style>' + css(dark, media, align === "center" ? "center" : "left") + "</style>";

      if (layout === "wall") {
        root.innerHTML = shell + '<div class="w left">' + label + '<div class="wall">' + days.map(function (d) { return slideHTML(d, BASE); }).join("") + "</div>" + foot + "</div>";
        return;
      }
      var boxClass = layout === "card" ? "card" : layout === "inline" ? "inline" : "";
      root.innerHTML = shell + '<div class="w ' + (align === "center" ? "" : "left") + '"><div class="' + boxClass + '">' + label +
        '<div class="stage" aria-live="off"></div>' +
        (days.length > 1 ? '<div class="dots" role="tablist" aria-label="Choose a year"></div>' : "") + foot + "</div></div>";
      var stage = root.querySelector(".stage"), dots = root.querySelector(".dots");
      var i = 0, timer = null, visible = true, hovering = false;
      var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (dots) days.forEach(function (d, k) {
        var b = document.createElement("button");
        b.type = "button"; b.setAttribute("role", "tab"); b.setAttribute("aria-label", d.date.slice(0, 4));
        b.addEventListener("click", function () { show(k, true); });
        dots.appendChild(b);
      });
      function paint(n) {
        stage.innerHTML = slideHTML(days[n], BASE);
        if (dots) Array.prototype.forEach.call(dots.children, function (b, k) { b.setAttribute("aria-current", k === n ? "true" : "false"); });
      }
      function show(n, user) {
        i = (n + days.length) % days.length;
        if (user) stage.setAttribute("aria-live", "polite");
        if (reduce) { paint(i); return; }
        stage.classList.add("out");
        setTimeout(function () { paint(i); stage.classList.remove("out"); }, 320);
      }
      function run() {
        clearInterval(timer); timer = null;
        if (interval > 0 && days.length > 1 && visible && !hovering && !reduce && !document.hidden) {
          timer = setInterval(function () { show(i + 1); }, interval);
        }
      }
      paint(0);
      if ((host.getAttribute("data-height") || "fixed").toLowerCase() !== "auto") {
        var tallest = 0;
        days.forEach(function (d, k) { paint(k); tallest = Math.max(tallest, stage.offsetHeight); });
        paint(0);
        stage.style.minHeight = tallest + "px";
        stage.style.display = "flex"; stage.style.flexDirection = "column"; stage.style.justifyContent = "center";
      }
      host.addEventListener("mouseenter", function () { hovering = true; run(); });
      host.addEventListener("mouseleave", function () { hovering = false; run(); });
      host.addEventListener("focusin", function () { hovering = true; run(); });
      host.addEventListener("focusout", function () { hovering = false; run(); });
      document.addEventListener("visibilitychange", run);
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (es) { visible = es[0].isIntersecting; run(); }).observe(host);
      }
      run();
    }).catch(function () { host.style.display = "none"; });
  }

  function boot() { Array.prototype.forEach.call(document.querySelectorAll("[data-trpl-today]"), mount); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
  if ("MutationObserver" in window) new MutationObserver(boot).observe(document.documentElement, { childList: true, subtree: true });
})();
