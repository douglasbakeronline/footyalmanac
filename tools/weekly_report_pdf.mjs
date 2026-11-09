#!/usr/bin/env node
// The weekly report as a PDF (9 Nov 2026). Reads weekly-report.json from
// tools/weekly_report.py, writes an HTML page in the almanac's own colours
// and prints it to A4 with Playwright's Chromium. Run by the Sunday session,
// not by CI (CI has no browser and the record files are the same).
//
//   node tools/weekly_report_pdf.mjs <weekly-report.json> <out.pdf> [--html out.html]
import fs from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);   // the sandbox's playwright is a global require, not an ES package

const [, , inPath, outPath, ...rest] = process.argv;
if (!inPath || !outPath) { console.error("usage: weekly_report_pdf.mjs <weekly-report.json> <out.pdf> [--html FILE]"); process.exit(2); }
const htmlOut = rest.includes("--html") ? rest[rest.indexOf("--html") + 1] : null;
const r = JSON.parse(fs.readFileSync(inPath, "utf8"));

const esc = (s) => String(s ?? "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const pct = (x, d = 0) => (x == null ? "n/a" : `${(x * 100).toFixed(d)}%`);
const signed = (x, d = 0) => (x == null ? "n/a" : `${x >= 0 ? "+" : ""}${(x * 100).toFixed(d)}%`);
const niceDate = (s) => { const d = new Date(s + "T12:00:00Z"); return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" }); };
const longDate = (s) => { const d = new Date(s + "T12:00:00Z"); return d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }); };
const SPORT = { football: "Football", tennis: "Tennis", nba: "NBA", nfl: "NFL", cfb: "College football", ncaab: "College basketball", rugby: "Rugby", mlb: "Baseball", nhl: "Hockey", wnba: "WNBA" };
const sport = (s) => SPORT[s] || s;

const w = r.card.week, t = r.card.toDate, p = r.period;
const tone = (x) => (x == null ? "" : x > 0 ? "good" : x < 0 ? "bad" : "");
const kpis = [
  { label: "Card groups", value: `${w.won} of ${w.groups}`, note: `${w.expected} expected${w.z != null ? `, z ${w.z}` : ""}` },
  { label: "Return, average price", value: w.return == null ? "n/a" : signed(w.return - 1), note: `one unit a group, ${w.units} units`, tone: tone(w.return == null ? null : w.return - 1) },
  { label: "Return, best price", value: w.returnBest == null ? "n/a" : signed(w.returnBest - 1), note: `since ${niceDate(t.from)}: ${signed((t.return || 1) - 1)} on ${t.units} units`, tone: tone(w.returnBest == null ? null : w.returnBest - 1) },
  { label: "Days with a Card", value: `${w.daysWithCard} of ${w.daysInRecord}`, note: `Card 3x built: ${w.card3x}` },
];

const legRows = Object.entries(w.legsBySport).map(([s, v]) =>
  `<tr><td>${esc(sport(s))}</td><td class="n">${v.legs}</td><td class="n">${v.landed} <span class="mute">(${pct(v.landed / v.legs)})</span></td><td class="n">${pct(v.quoted)}</td><td class="n ${tone(v.landed / v.legs - v.quoted)}">${signed(v.landed / v.legs - v.quoted, 1)}</td></tr>`).join("");

const groupRows = w.groupList.map((g) =>
  `<tr class="${g.status}"><td class="nowrap">${esc(niceDate(g.date))}</td><td class="nowrap">${esc(g.name)}</td><td class="n">${g.odds}</td><td class="n">${pct(g.p)}</td><td class="status">${g.status}</td><td class="legs">${esc(g.legs.join("; "))}</td></tr>`).join("");

const listRows = Object.entries(r.list).filter(([, v]) => v.list.n || v.reserve.n).map(([s, v]) => {
  const li = v.list, re = v.reserve;
  return `<tr><td>${esc(sport(s))}</td><td class="n">${li.n}</td><td class="n">${li.n ? `${li.landed} <span class="mute">(${pct(li.rate)})</span>` : "<span class='mute'>none</span>"}</td><td class="n">${li.n ? pct(li.quoted) : ""}</td><td class="n ${li.n ? tone(li.rate - li.quoted) : ""}">${li.n ? signed(li.rate - li.quoted, 1) : ""}</td><td class="n mute">${re.n ? `${re.landed}/${re.n} (${pct(re.rate)})` : ""}</td></tr>`;
}).join("");

const shipped = r.shipped.map((s) => `<li><span class="date">${esc(niceDate(s.date))}</span><div><strong>${esc(s.title)}</strong>${s.what ? `<div class="what">${esc(s.what.length > 230 ? s.what.slice(0, 227).replace(/\s+\S*$/, "") + "…" : s.what)}</div>` : ""}</div></li>`).join("");
const bullets = (xs) => (xs || []).map((x) => `<li>${esc(x)}</li>`).join("");

const html = `<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>Sports Almanac, week to ${esc(niceDate(p.to))}</title>
<style>
  @page { size: A4; margin: 16mm 14mm 18mm; }
  :root { --ink:#1a1511; --mute:#6e6355; --paper:#f0e8d6; --surface:#fbf6ea; --rule:#c6b89e; --rule-soft:#ded3bd; --red:#b4222b; --home:#1f3b5c; --yellow:#f4d21c; --good:#2d5f3a; --bad:#96271d; }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: #fff; color: var(--ink); font: 10.5pt/1.45 "Archivo", "Helvetica Neue", Arial, sans-serif; }
  .cover { background: var(--paper); border: 1px solid var(--ink); padding: 0 0 14px; margin-bottom: 18px; }
  .star { background: var(--red); color: #fff; font-size: 9pt; letter-spacing: .14em; text-transform: uppercase; padding: 5px 16px; }
  .title { padding: 18px 16px 6px; }
  .title h1 { margin: 0; font: 800 30pt/1 "Archivo Black", "Arial Black", Arial, sans-serif; letter-spacing: -.01em; }
  .title h1 .sports { color: var(--red); display: block; }
  .title p { margin: 8px 0 0; color: var(--mute); font-size: 10pt; }
  .band { background: var(--ink); color: var(--yellow); font-weight: 700; padding: 6px 16px; font-size: 11pt; letter-spacing: .04em; }
  h2 { font-size: 13pt; margin: 22px 0 8px; padding-bottom: 4px; border-bottom: 1px solid var(--ink); letter-spacing: .01em; }
  h2 small { color: var(--mute); font-weight: 400; font-size: 9.5pt; margin-left: 8px; }
  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0 4px; }
  .kpi { border: 1px solid var(--rule); background: var(--surface); padding: 10px 12px; }
  .kpi .label { font-size: 8.5pt; color: var(--mute); text-transform: uppercase; letter-spacing: .08em; }
  .kpi .value { font-size: 20pt; font-weight: 700; line-height: 1.1; margin: 4px 0 2px; }
  .kpi .note { font-size: 8.5pt; color: var(--mute); }
  .good { color: var(--good); } .bad { color: var(--bad); }
  table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 9.5pt; }
  th { text-align: left; font-weight: 600; color: var(--mute); font-size: 8.5pt; text-transform: uppercase; letter-spacing: .06em; border-bottom: 1px solid var(--ink); padding: 4px 6px; }
  td { padding: 5px 6px; border-bottom: 1px solid var(--rule-soft); vertical-align: top; }
  td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; }
  td.legs { color: var(--mute); font-size: 8.8pt; }
  td.status { text-transform: capitalize; font-weight: 600; }
  td.nowrap { white-space: nowrap; }
  tr.won td.status { color: var(--good); } tr.lost td.status { color: var(--bad); }
  .mute { color: var(--mute); }
  p.read { margin: 6px 0 0; font-size: 10pt; }
  ul.ship { list-style: none; padding: 0; margin: 6px 0; }
  ul.ship li { display: grid; grid-template-columns: 52px 1fr; gap: 8px; padding: 5px 0; border-bottom: 1px solid var(--rule-soft); font-size: 9.5pt; }
  ul.ship .date { color: var(--mute); font-variant-numeric: tabular-nums; }
  ul.ship .what { color: var(--mute); font-size: 8.8pt; margin-top: 2px; }
  ul.plain { margin: 6px 0; padding-left: 18px; font-size: 10pt; } ul.plain li { margin: 3px 0; }
  .foot { margin-top: 20px; color: var(--mute); font-size: 8.5pt; border-top: 1px solid var(--rule); padding-top: 6px; }
  .break { break-before: page; }
</style></head><body>
<div class="cover">
  <div class="star">Weekly report</div>
  <div class="title"><h1><span class="sports">Sports</span>Almanac</h1>
    <p>Week ${esc(longDate(p.from))} to ${esc(longDate(p.to))}. Prepared ${esc(longDate(r.reportDate))}. Every number comes from the published record; nothing is fitted or restated.</p></div>
  <div class="band">The Card: ${w.won} of ${w.groups} groups won, ${w.return == null ? "no return" : signed(w.return - 1) + " at the average price"}</div>
</div>

<h2>The Card <small>Bets tab, full-rule groups settled this week</small></h2>
<div class="kpis">${kpis.map((k) => `<div class="kpi"><div class="label">${esc(k.label)}</div><div class="value ${k.tone || ""}">${esc(k.value)}</div><div class="note">${esc(k.note)}</div></div>`).join("")}</div>
<table><thead><tr><th>Legs by sport</th><th class="n">Legs</th><th class="n">Landed</th><th class="n">Quoted</th><th class="n">Gap</th></tr></thead><tbody>${legRows}</tbody></table>
<table><thead><tr><th>Day</th><th>Group</th><th class="n">Price</th><th class="n">Chance</th><th>Result</th><th>Legs</th></tr></thead><tbody>${groupRows || `<tr><td colspan="6" class="mute">No Card group settled this week.</td></tr>`}</tbody></table>
<p class="read">Since ${esc(niceDate(t.from))}: ${t.groups} groups, ${t.won} won against ${t.expected} expected (z ${t.z}), ${signed((t.return || 1) - 1)} at the average price and ${signed((t.returnBest || 1) - 1)} at the best, one unit a group.</p>

<h2>The Daily List <small>picks that cleared the bar, landed against the quoted chance</small></h2>
<table><thead><tr><th>Sport</th><th class="n">List picks</th><th class="n">Landed</th><th class="n">Quoted</th><th class="n">Gap</th><th class="n">Reserve</th></tr></thead><tbody>${listRows}</tbody></table>

${r.health?.length ? `<h2>Health</h2><ul class="plain">${bullets(r.health)}</ul>` : ""}

<h2 class="${r.shipped.length > 8 ? "break" : ""}">Shipped <small>releases to ${esc(niceDate(r.reportDate))}</small></h2>
<ul class="ship">${shipped || `<li><span></span><div class="mute">Nothing released.</div></li>`}</ul>

${r.next?.length ? `<h2>Next week</h2><ul class="plain">${bullets(r.next)}</ul>` : ""}
${r.decisions?.length ? `<h2>Decisions waiting on Douglas</h2><ul class="plain">${bullets(r.decisions)}</ul>` : ""}

<div class="foot">Sports Almanac, douglasbakeronline.github.io/footyalmanac. Record files graded ${esc(r.stamps["groupings-record.json"] || "")} (groups), ${esc(r.stamps["record.json"] || "")} (football). Returns assume one unit on every group at the published average price; "best" is the best UK bookmaker price recorded at publication.</div>
</body></html>`;

if (htmlOut) fs.writeFileSync(htmlOut, html);
const { chromium } = require("playwright");
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setContent(html, { waitUntil: "load" });
await page.pdf({ path: outPath, format: "A4", printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log(`wrote ${outPath}`);
