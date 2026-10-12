// Day by Day — shared helpers for the explorer pages
const DBD = (() => {
  const API = new URL("api/v1/", document.baseURI).href;
  const cache = new Map();
  const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const ACTION_LABEL = { official_act: "official act", natural_history: "natural history" };

  async function get(path) {
    if (!cache.has(path)) cache.set(path, fetch(API + path).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }));
    return cache.get(path);
  }
  function esc(s) { return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
  function fmtDate(iso, opts = {}) {
    const [y, m, d] = iso.split("-").map(Number);
    return `${MONTHS[m - 1]} ${d}${opts.noYear ? "" : ", " + y}`;
  }
  function param(name) { return new URLSearchParams(location.search).get(name); }
  function personLink(p) { return `<a href="person.html?id=${encodeURIComponent(p.id)}">${esc(p.name)}</a>`; }
  function placeLink(p) { return `<a href="place.html?id=${encodeURIComponent(p.id)}">${esc(p.name)}</a>`; }

  function renderDay(d) {
    const loc = d.location;
    const meta = [d.weekday && `${d.weekday}.`, `Age ${d.age}`, loc && `${loc.source === "carried" ? "Probably at " : ""}${placeLink(loc)}`].filter(Boolean).join(" &nbsp;|&nbsp; ");
    const sigColor = ["--none", "--s1", "--s2", "--s3", "--s4", "--s5"][Math.max(0, d.significance)] || "--s1";
    let h = `<article class="daycard" style="border-top-color: var(${sigColor})">
      <div class="date">${esc(fmtDate(d.date))}</div>
      <div class="meta">${meta}</div>`;
    if (!d.has_entry) {
      h += `<p class="empty">The record has no entry for this day.${loc ? ` He was most likely at ${esc(loc.name)}.` : ""}</p>`;
    } else {
      h += `<h3 class="headline">${esc(d.headline)}</h3><p class="summary">${esc(d.summary)}</p>`;
      if (d.events?.length > 1) {
        h += `<ol class="events">` + d.events.map(e => `<li><span class="act">${esc(ACTION_LABEL[e.action] || e.action)}</span>${e.time ? `<b>${esc(e.time)}</b> ` : ""}${esc(e.detail)}</li>`).join("") + `</ol>`;
      }
      for (const q of d.tr_quotes || []) {
        h += `<blockquote class="trq">“${esc(q.text)}”<footer>Theodore Roosevelt, ${esc(q.kind)}. Unverified transcription; check the original before quoting.</footer></blockquote>`;
      }
      if (d.people?.length) h += `<h3>People</h3><ul class="who">` + d.people.map(p => `<li>${personLink(p)} <span class="role">${esc(p.role || "")}</span></li>`).join("") + `</ul>`;
      if (d.letters?.length) {
        h += `<h3 style="margin-top:14px">Letters</h3><ul class="who">` + d.letters.map(l => {
          const who = typeof l.correspondent === "string" && l.correspondent_resolved ? `<a href="person.html?id=${encodeURIComponent(l.correspondent)}">${esc(l.correspondent_name || l.correspondent)}</a>` : esc(l.correspondent);
          return `<li>${l.direction === "from_tr" ? "To" : "From"} ${who}<br><span class="role">${esc(l.topic || "")}</span></li>`;
        }).join("") + `</ul>`;
      }
      if (d.tags?.length) h += `<ul class="taglist">` + d.tags.map(t => `<li><a href="index.html?tag=${encodeURIComponent(t)}">${esc(t.replace(/-/g, " "))}</a></li>`).join("") + `</ul>`;
    }
    const pages = (d.sources?.[0]?.pages || []).join(", ");
    h += `<div class="src">Written by the Theodore Roosevelt Presidential Library from the Theodore Roosevelt Association's <i>Chronological Record</i>${pages ? ` (${esc(pages)})` : ""}.${d.uncertain ? ` Note: ${esc(d.uncertain)}` : ""}</div>`;
    if (d.prev || d.next) h += `<nav class="daynav">${d.prev ? `<a href="day.html?date=${d.prev}" data-date="${d.prev}">Previous day</a>` : "<span></span>"}<a href="day.html?date=${d.date}">Permalink</a>${d.next ? `<a href="day.html?date=${d.next}" data-date="${d.next}">Next day</a>` : "<span></span>"}</nav>`;
    return h + `</article>`;
  }
  return { API, get, esc, fmtDate, param, renderDay, personLink, placeLink, MONTHS };
})();
