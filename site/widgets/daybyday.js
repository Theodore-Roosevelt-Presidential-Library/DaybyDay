/*! Theodore Roosevelt Day by Day widgets | Theodore Roosevelt Presidential Library | MIT
 *
 * <script src="https://daybyday.labs.trlibrary.com/widgets/daybyday.js" defer></script>
 *
 * <trpl-on-this-day count="3"></trpl-on-this-day>          today's date across TR's life
 * <trpl-on-this-day date="06-25" count="5"></trpl-on-this-day>
 * <trpl-day date="1884-06-25"></trpl-day>                  one day, full card
 * <trpl-where-was-tr></trpl-where-was-tr>                    where TR was on this date, each year
 *
 * Optional attributes on every widget:
 *   theme="light|dark"   (default light)
 *   api="https://…/api/v1/"  (default: the published API)
 *   cta="off"            hide the "Plan your visit" link
 * Fonts inherit the page's --dbd-display / --dbd-serif / --dbd-sans CSS variables when set.
 */
(() => {
  const SCRIPT = document.currentScript;
  const DEFAULT_API = SCRIPT ? new URL("../api/v1/", SCRIPT.src).href : "https://daybyday.labs.trlibrary.com/api/v1/";
  const SITE = SCRIPT ? new URL("../", SCRIPT.src).href : "https://daybyday.labs.trlibrary.com/";
  const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const cache = new Map();
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (iso, noYear) => { const [y, m, d] = iso.split("-").map(Number); return `${MONTHS[m - 1]} ${d}${noYear ? "" : ", " + y}`; };
  const todayMD = () => { const t = new Date(); return `${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`; };
  function get(api, path) {
    const url = api + path;
    if (!cache.has(url)) cache.set(url, fetch(url).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }));
    return cache.get(url);
  }
  const CSS = `
    :host { display: block; --night: #092A4D; --ink: #25282A; --muted: #4A4F52; --line: #D1CCBD; --bg: #fff; --accent: #E7805D; --link: #1B4532;
      --display: var(--dbd-display, "Dharma Gothic E", "Oswald", "Arial Narrow", sans-serif);
      --serif: var(--dbd-serif, "ITC Clearface", "Lora", Georgia, serif);
      --sans: var(--dbd-sans, "Frutiger Next", "Source Sans 3", system-ui, sans-serif); }
    :host([theme=dark]) { --ink: #F3F1EB; --muted: #C9D3DF; --line: #24496F; --bg: #092A4D; --link: #8FC895; }
    .w { background: var(--bg); color: var(--ink); font: 16px/1.55 var(--serif); padding: 18px 20px; border-top: 5px solid var(--accent); }
    .kicker { font: 700 26px/1 var(--display); text-transform: uppercase; color: var(--night); margin: 0 0 10px; letter-spacing: .01em; }
    :host([theme=dark]) .kicker { color: #fff; }
    ul { list-style: none; margin: 0; padding: 0; }
    li { padding: 10px 0; border-top: 1px solid var(--line); }
    li:first-child { border-top: 0; padding-top: 0; }
    .yr { font: 700 22px/1 var(--display); color: var(--accent); margin-right: 8px; }
    .h { font-weight: 700; color: var(--ink); text-decoration: none; }
    a.h:hover, a.h:focus-visible { text-decoration: underline; }
    .s { margin: 4px 0 0; }
    .m { font: 13px/1.4 var(--sans); color: var(--muted); margin-top: 3px; }
    .q { margin: 10px 0 0; padding: 8px 12px; border-left: 3px solid var(--link); font-style: italic; }
    .foot { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-top: 12px; font: 600 13px var(--sans); }
    .foot a { color: var(--link); }
    .src { font: 12px/1.4 var(--sans); color: var(--muted); margin-top: 8px; }
    :focus-visible { outline: 3px solid #FC924E; outline-offset: 2px; }`;

  class Base extends HTMLElement {
    connectedCallback() {
      if (!this.shadowRoot) this.attachShadow({ mode: "open" });
      this.api = this.getAttribute("api") || DEFAULT_API;
      this.render().catch(() => this.paint(`<p class="m">Theodore Roosevelt Day by Day is unavailable right now.</p>`));
    }
    static get observedAttributes() { return ["date", "count", "theme"]; }
    attributeChangedCallback(n, o, v) { if (this.shadowRoot && o !== v) this.connectedCallback(); }
    paint(inner) {
      const cta = this.getAttribute("cta") === "off" ? "" : `<a href="https://www.trlibrary.com/visit" target="_top">Plan your visit</a>`;
      this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="w">${inner}<div class="foot"><a href="${SITE}" target="_top">Explore every day of his life</a>${cta}</div><div class="src">Theodore Roosevelt Presidential Library</div></div>`;
    }
    dayLink(date) { return `${SITE}day.html?date=${date}`; }
  }

  class OnThisDay extends Base {
    async render() {
      const md = this.getAttribute("date") || todayMD();
      const n = Math.max(1, Math.min(10, +(this.getAttribute("count") || 3)));
      const o = await get(this.api, `on-this-day/${md}.json`);
      const [m, d] = md.split("-").map(Number);
      const items = o.days.slice(0, n).map(x => `<li><span class="yr">${x.date.slice(0, 4)}</span><a class="h" href="${this.dayLink(x.date)}" target="_top">${esc(x.headline)}</a>
        <p class="s">${esc(x.summary)}</p><div class="m">Age ${x.age}${x.location ? ` | ${esc(x.location)}` : ""}</div></li>`).join("");
      this.paint(`<p class="kicker">${MONTHS[m - 1]} ${d} in Theodore Roosevelt's life</p><ul>${items || `<li class="m">No entries for this date.</li>`}</ul>`);
    }
  }

  class Day extends Base {
    async render() {
      const date = this.getAttribute("date");
      const x = await get(this.api, `days/${date}.json`);
      const q = (x.tr_quotes || [])[0];
      this.paint(`<p class="kicker">${fmt(date)}</p>
        <a class="h" href="${this.dayLink(date)}" target="_top">${esc(x.headline || "No entry in the record")}</a>
        ${x.summary ? `<p class="s">${esc(x.summary)}</p>` : ""}
        ${q ? `<p class="q">“${esc(q.text)}”</p>` : ""}
        <div class="m">Age ${x.age}${x.location ? ` | ${esc(x.location.name)}` : ""}</div>`);
    }
  }

  class WhereWasTR extends Base {
    async render() {
      const md = this.getAttribute("date") || todayMD();
      const n = Math.max(1, Math.min(12, +(this.getAttribute("count") || 6)));
      const o = await get(this.api, `on-this-day/${md}.json`);
      const [m, d] = md.split("-").map(Number);
      const rows = o.days.filter(x => x.location).sort((a, b) => b.significance - a.significance || a.date.localeCompare(b.date)).slice(0, n)
        .sort((a, b) => a.date.localeCompare(b.date))
        .map(x => `<li><span class="yr">${x.date.slice(0, 4)}</span><a class="h" href="${this.dayLink(x.date)}" target="_top">${esc(x.location)}</a><div class="m">${esc(x.headline)}</div></li>`).join("");
      this.paint(`<p class="kicker">Where was TR on ${MONTHS[m - 1]} ${d}?</p><ul>${rows}</ul>`);
    }
  }

  customElements.get("trpl-on-this-day") || customElements.define("trpl-on-this-day", OnThisDay);
  customElements.get("trpl-day") || customElements.define("trpl-day", Day);
  customElements.get("trpl-where-was-tr") || customElements.define("trpl-where-was-tr", WhereWasTR);
})();
