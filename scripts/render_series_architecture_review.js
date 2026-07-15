const fs = require("fs");
const path = require("path");

const root = process.cwd();
const depsRoot = path.join(root, "tmp", "review-node", "node_modules");
const { chromium } = require(path.join(depsRoot, "playwright-core"));
const { marked } = require(path.join(depsRoot, "marked"));
const sharp = require(path.join(depsRoot, "sharp"));

const chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const outDir = path.join(root, "reports", "renders");

function writeText(rel, text) {
  const full = path.join(root, rel);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, text.replace(/\r?\n/g, "\r\n"), "utf8");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[ch]);
}

function readArchitectureMarkdown() {
  return fs.readFileSync(path.join(root, "docs", "series-architecture.md"), "utf8");
}

function extractMermaidBlocks(markdown) {
  const blocks = [];
  const re = /```mermaid\r?\n([\s\S]*?)```/g;
  let match;
  while ((match = re.exec(markdown)) !== null) {
    blocks.push(match[1].trim());
  }
  return blocks;
}

function parseMermaidFlowchart(source) {
  const nodes = new Map();
  const edges = [];
  const lines = source.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);

  function ensureNode(id, label) {
    if (!nodes.has(id)) {
      nodes.set(id, label || id);
    } else if (label && nodes.get(id) === id) {
      nodes.set(id, label);
    }
  }

  function parseEndpoint(raw) {
    const cleaned = raw.trim().replace(/;$/, "");
    const match = cleaned.match(/^([A-Za-z0-9_]+)(?:\["([^"]+)"\])?$/);
    if (!match) {
      return null;
    }
    const [, id, label] = match;
    ensureNode(id, label);
    return id;
  }

  for (const line of lines) {
    if (line.startsWith("flowchart")) {
      continue;
    }
    const parts = line.split(/\s*-->\s*/);
    if (parts.length !== 2) {
      continue;
    }
    const from = parseEndpoint(parts[0]);
    const to = parseEndpoint(parts[1]);
    if (from && to) {
      edges.push({ from, to });
    }
  }
  return { nodes, edges };
}

function diagramHtml(title, graph, layout, viewportName = "desktop") {
  const labelFor = (id) => graph.nodes.get(id) || id;
  if (viewportName === "mobile") {
    const mobileEdges = graph.edges.map((edge, index) => {
      return `<li><span class="edge-index">${index + 1}</span><span>${escapeHtml(labelFor(edge.from))} → ${escapeHtml(labelFor(edge.to))}</span></li>`;
    }).join("\n");
    return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${escapeHtml(title)}</title>
<style>
:root{color-scheme:light}
body{margin:0;background:#fff;color:#111827;font:16px/1.25 "Microsoft YaHei",Arial,sans-serif}
main{box-sizing:border-box;width:100vw;height:100vh;padding:8px;display:grid;grid-template-rows:auto 1fr;gap:6px}
h1{font-size:20px;line-height:1.15;margin:0;text-align:center}
.mobile-edge-list{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:1fr;gap:3px;align-content:start}
.mobile-edge-list li{display:grid;grid-template-columns:22px minmax(0,1fr);gap:4px;align-items:center;border:1px solid #d8dee8;border-radius:6px;padding:2px 5px;background:#fbfdff;font-size:16px;line-height:1.08}
.edge-index{font-weight:700;color:#1d4ed8}
.mobile-edge-list span{overflow-wrap:anywhere;word-break:break-word}
</style>
</head>
<body class="mobile" data-node-count="${graph.nodes.size}" data-edge-count="${graph.edges.length}">
<main>
<h1>${escapeHtml(title)}</h1>
<ul class="mobile-edge-list">${mobileEdges}</ul>
</main>
</body>
</html>`;
  }
  const nodeDivs = Array.from(graph.nodes.entries()).map(([id, label]) => {
    const position = layout[id];
    if (!position) {
      throw new Error(`missing layout for node ${id}`);
    }
    return `<div class="node" data-node-id="${escapeHtml(id)}" style="left:${position.x}%;top:${position.y}%">${escapeHtml(label)}</div>`;
  }).join("\n");
  const edgeList = graph.edges.map((edge) => {
    return `<li>${escapeHtml(labelFor(edge.from))}→${escapeHtml(labelFor(edge.to))}</li>`;
  }).join("\n");
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${escapeHtml(title)}</title>
<style>
:root{color-scheme:light}
body{margin:0;background:#fff;color:#111827;font:16px/1.35 "Microsoft YaHei",Arial,sans-serif}
main{box-sizing:border-box;width:100vw;height:100vh;padding:18px;display:grid;grid-template-rows:auto 1fr auto;gap:10px}
h1{font-size:24px;line-height:1.15;margin:0;text-align:center}
.canvas{position:relative;border:1px solid #d8dee8;border-radius:8px;background:#fbfdff;overflow:hidden}
.node{position:absolute;transform:translate(-50%,-50%);box-sizing:border-box;min-width:118px;max-width:160px;padding:6px 8px;border:2px solid #1d4ed8;border-radius:7px;background:#eff6ff;text-align:center;font-weight:700;font-size:16px;line-height:1.15;overflow-wrap:anywhere;word-break:break-word}
svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.edge-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px 12px;margin:0;padding:0;list-style:none;font-size:16px}
.edge-list li{white-space:nowrap;overflow:hidden;text-overflow:clip}
body.mobile main{padding:8px;gap:6px;grid-template-rows:auto 520px auto}
body.mobile h1{font-size:20px}
body.mobile .node{min-width:84px;max-width:108px;padding:3px 4px;font-size:16px;line-height:1.08;border-width:1.5px}
body.mobile .edge-list{grid-template-columns:repeat(2,minmax(0,1fr));font-size:16px;line-height:1.15;gap:2px 8px}
</style>
</head>
<body class="${escapeHtml(viewportName)}">
<main>
<h1>${escapeHtml(title)}</h1>
<div class="canvas">
<svg aria-hidden="true"></svg>
${nodeDivs}
</div>
<ul class="edge-list">${edgeList}</ul>
</main>
<script>
const edges = ${JSON.stringify(graph.edges)};
function drawEdges(){
  const svg = document.querySelector('svg');
  if (!svg) return;
  svg.innerHTML = '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#475569"></path></marker></defs>';
  const canvas = document.querySelector('.canvas').getBoundingClientRect();
  for (const edge of edges) {
    const from = document.querySelector('[data-node-id="' + edge.from + '"]').getBoundingClientRect();
    const to = document.querySelector('[data-node-id="' + edge.to + '"]').getBoundingClientRect();
    const x1 = from.left + from.width / 2 - canvas.left;
    const y1 = from.top + from.height / 2 - canvas.top;
    const x2 = to.left + to.width / 2 - canvas.left;
    const y2 = to.top + to.height / 2 - canvas.top;
    const dx = x2 - x1;
    const dy = y2 - y1;
    const len = Math.max(1, Math.sqrt(dx * dx + dy * dy));
    const sourcePad = Math.min(42, len * 0.22);
    const targetPad = Math.min(54, len * 0.28);
    const line = document.createElementNS('http://www.w3.org/2000/svg','line');
    line.setAttribute('x1', x1 + dx / len * sourcePad);
    line.setAttribute('y1', y1 + dy / len * sourcePad);
    line.setAttribute('x2', x2 - dx / len * targetPad);
    line.setAttribute('y2', y2 - dy / len * targetPad);
    line.setAttribute('stroke', '#475569');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('marker-end', 'url(#arrow)');
    svg.appendChild(line);
  }
}
window.addEventListener('DOMContentLoaded', drawEdges);
window.addEventListener('resize', drawEdges);
</script>
</body>
</html>`;
}

function mainHtml(markdown) {
  const body = marked.parse(markdown, { mangle: false, headerIds: false });
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>BLDC series architecture review render</title>
<style>
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#f6f7f9;color:#15171a;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",Arial,sans-serif}
main{max-width:1120px;margin:0 auto;padding:32px 24px 64px;background:#fff;min-height:100vh;box-sizing:border-box}
h1{font-size:34px;line-height:1.2;margin:0 0 22px}
h2{font-size:26px;margin:38px 0 16px;border-top:1px solid #dde1e6;padding-top:24px}
h3{font-size:20px;margin:28px 0 12px}
p,li{font-size:16px}
code{background:#eef2f5;padding:1px 4px;border-radius:4px}
pre{background:#111827;color:#f8fafc;padding:16px;border-radius:8px;overflow:auto}
pre code{background:transparent;color:inherit;padding:0}
table{border-collapse:collapse;width:100%;margin:14px 0 24px;font-size:15px}
th,td{border:1px solid #cfd6df;padding:8px 10px;vertical-align:top}
th{background:#edf2f7;font-weight:700}
.table-wrap{overflow-x:auto;margin:12px 0 22px;max-width:100%}
.table-wrap table{min-width:760px;margin:0}
.evidence-cards{display:none}
.table-wrap.evidence-section{display:none}
.evidence-cards.evidence-section{display:block}
.evidence-card{border:1px solid #cfd6df;border-radius:7px;margin:10px 0;padding:10px;background:#fff}
.evidence-card h3{font-size:18px;margin:0 0 8px;border:0;padding:0}
.evidence-field{display:grid;grid-template-columns:96px 1fr;gap:6px;border-top:1px solid #e5e9f0;padding:6px 0}
.evidence-field:first-of-type{border-top:0}
.evidence-label{font-weight:700;color:#344054}
.evidence-field>div:last-child{min-width:0;overflow-wrap:anywhere;word-break:break-word}
.contract-card{display:none}
.coverage-cards{display:none}
.coverage-card{border:1px solid #cfd6df;border-radius:7px;margin:10px 0;padding:10px;background:#fff}
.coverage-card h3{font-size:18px;margin:0 0 8px;border:0;padding:0}
.coverage-field{display:grid;grid-template-columns:96px 1fr;gap:6px;border-top:1px solid #e5e9f0;padding:6px 0}
.coverage-field:first-of-type{border-top:0}
.coverage-label{font-weight:700;color:#344054}
.coverage-field>div:last-child{min-width:0;overflow-wrap:anywhere;word-break:break-word}
a{color:#0f5cc0}
@media(max-width:600px){
  main{padding:20px 14px 48px}
  h1{font-size:27px}
  h2{font-size:22px}
  h3{font-size:18px}
  p,li{font-size:16px}
  pre{max-width:100%;white-space:pre-wrap;overflow-wrap:anywhere}
  pre code{white-space:pre-wrap;overflow-wrap:anywhere}
  code{overflow-wrap:anywhere;word-break:break-word}
  table{font-size:13px;table-layout:fixed;width:100%}
  th,td{padding:6px 5px;overflow-wrap:anywhere;word-break:break-word}
  .table-wrap{overflow-x:visible}
  .table-wrap table{min-width:0;width:100%}
  .table-wrap.detailed-contract-section{display:none}
  .table-wrap.bidirectional-coverage-section{display:none}
  .coverage-cards.bidirectional-coverage-section{display:block}
  .contract-card{display:block;border:1px solid #cfd6df;border-radius:7px;margin:8px 0 20px;padding:10px;background:#fff}
  .contract-field{display:grid;grid-template-columns:minmax(88px,32%) 1fr;gap:8px;border-top:1px solid #e5e9f0;padding:7px 0}
  .contract-field:first-child{border-top:0}
  .contract-label{font-weight:700;color:#344054;word-break:keep-all;overflow-wrap:anywhere}
  .contract-value{overflow-wrap:anywhere;word-break:break-word}
}
</style>
</head>
<body><main>${body}</main>
<script>
function wrapTables(){
  document.querySelectorAll('table').forEach((table) => {
    if (table.parentElement && table.parentElement.classList.contains('table-wrap')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'table-wrap';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });
}
function enhanceEvidenceMapping(){
  const headings = Array.from(document.querySelectorAll('h2'));
  const h2 = headings.find((node) => node.textContent.trim().startsWith('9. 证据与掌握映射'));
  if (!h2) return;
  const sectionNodes = [];
  for (let node = h2; node; node = node.nextElementSibling) {
    if (node !== h2 && node.tagName === 'H2') break;
    sectionNodes.push(node);
  }
  sectionNodes.forEach((node) => node.classList && node.classList.add('evidence-section'));
  const table = sectionNodes.find((node) => node.querySelector && node.querySelector('table'))?.querySelector('table');
  if (!table) return;
  const headers = Array.from(table.querySelectorAll('thead th')).map((th) => th.textContent.trim());
  const cards = document.createElement('div');
  cards.className = 'evidence-cards evidence-section';
  table.querySelectorAll('tbody tr').forEach((tr) => {
    const cells = Array.from(tr.children).map((td) => td.textContent.trim());
    const card = document.createElement('article');
    card.className = 'evidence-card';
    const title = document.createElement('h3');
    title.textContent = cells[0] || '证据链';
    card.appendChild(title);
    for (let i = 1; i < cells.length; i += 1) {
      const field = document.createElement('div');
      field.className = 'evidence-field';
      const label = document.createElement('div');
      label.className = 'evidence-label';
      label.textContent = headers[i] || '';
      const value = document.createElement('div');
      value.textContent = cells[i] || '';
      field.append(label, value);
      card.appendChild(field);
    }
    cards.appendChild(card);
  });
  table.closest('.table-wrap').after(cards);
}
function enhanceDetailedContracts(){
  const headings = Array.from(document.querySelectorAll('h2'));
  const h2 = headings.find((node) => node.textContent.trim().startsWith('8. 单章详细契约'));
  if (!h2) return;
  const nodes = [];
  for (let node = h2.nextElementSibling; node; node = node.nextElementSibling) {
    if (node.tagName === 'H2') break;
    nodes.push(node);
  }
  nodes.forEach((node) => {
    if (!node.querySelectorAll) return;
    node.querySelectorAll('table').forEach((table) => {
      const wrapper = table.closest('.table-wrap');
      if (!wrapper) return;
      wrapper.classList.add('detailed-contract-section');
      const card = document.createElement('article');
      card.className = 'contract-card';
      table.querySelectorAll('tbody tr').forEach((tr) => {
        const cells = Array.from(tr.children).map((cell) => cell.textContent.trim());
        if (cells.length < 2) return;
        const field = document.createElement('div');
        field.className = 'contract-field';
        const label = document.createElement('div');
        label.className = 'contract-label';
        label.textContent = cells[0];
        const value = document.createElement('div');
        value.className = 'contract-value';
        value.textContent = cells.slice(1).join(' ');
        field.append(label, value);
        card.appendChild(field);
      });
      wrapper.after(card);
    });
  });
}
function enhanceBidirectionalCoverage(){
  const headings = Array.from(document.querySelectorAll('h2'));
  const h2 = headings.find((node) => node.textContent.trim().startsWith('10. 双向覆盖检查'));
  if (!h2) return;
  const sectionNodes = [];
  for (let node = h2; node; node = node.nextElementSibling) {
    if (node !== h2 && node.tagName === 'H2') break;
    sectionNodes.push(node);
  }
  sectionNodes.forEach((node) => node.classList && node.classList.add('bidirectional-coverage-section'));
  sectionNodes.forEach((node) => {
    if (!node.querySelectorAll) return;
    node.querySelectorAll('table').forEach((table) => {
      const wrapper = table.closest('.table-wrap');
      if (!wrapper) return;
      wrapper.classList.add('bidirectional-coverage-section');
      const headers = Array.from(table.querySelectorAll('thead th')).map((th) => th.textContent.trim());
      const cards = document.createElement('div');
      cards.className = 'coverage-cards bidirectional-coverage-section';
      table.querySelectorAll('tbody tr').forEach((tr) => {
        const cells = Array.from(tr.children).map((td) => td.textContent.trim());
        const card = document.createElement('article');
        card.className = 'coverage-card';
        const title = document.createElement('h3');
        title.textContent = cells[0] || '覆盖项';
        card.appendChild(title);
        for (let i = 1; i < cells.length; i += 1) {
          const field = document.createElement('div');
          field.className = 'coverage-field';
          const label = document.createElement('div');
          label.className = 'coverage-label';
          label.textContent = headers[i] || '';
          const value = document.createElement('div');
          value.textContent = cells[i] || '';
          field.append(label, value);
          card.appendChild(field);
        }
        cards.appendChild(card);
      });
      wrapper.after(cards);
    });
  });
}
window.addEventListener('DOMContentLoaded', () => {
  wrapTables();
  enhanceEvidenceMapping();
  enhanceDetailedContracts();
  enhanceBidirectionalCoverage();
});
</script>
</body></html>`;
}

function layoutsFor(graphName, viewportName) {
  if (graphName === "system") {
    if (viewportName === "mobile") {
      return {
        DC: { x: 16, y: 8 },
        GATE: { x: 50, y: 8 },
        INV: { x: 84, y: 8 },
        PH: { x: 84, y: 22 },
        BEMF: { x: 50, y: 22 },
        MECH: { x: 16, y: 22 },
        POWER: { x: 84, y: 36 },
        TORQUE: { x: 50, y: 36 },
        LOAD: { x: 16, y: 36 },
        HALL: { x: 16, y: 50 },
        DEC: { x: 50, y: 50 },
        EVENT: { x: 84, y: 50 },
        SPEED: { x: 84, y: 64 },
        FAULT: { x: 50, y: 64 },
        REF: { x: 16, y: 64 },
        PI: { x: 16, y: 78 },
        DUTY: { x: 50, y: 78 },
        TABLE: { x: 84, y: 78 },
        SAFE: { x: 50, y: 92 },
      };
    }
    return {
      DC: { x: 5, y: 34 },
      INV: { x: 17, y: 34 },
      PH: { x: 29, y: 34 },
      BEMF: { x: 42, y: 14 },
      POWER: { x: 42, y: 34 },
      TORQUE: { x: 55, y: 34 },
      MECH: { x: 68, y: 34 },
      LOAD: { x: 68, y: 14 },
      HALL: { x: 82, y: 34 },
      DEC: { x: 82, y: 56 },
      EVENT: { x: 66, y: 56 },
      SPEED: { x: 50, y: 56 },
      REF: { x: 27, y: 70 },
      PI: { x: 43, y: 70 },
      DUTY: { x: 58, y: 70 },
      TABLE: { x: 82, y: 74 },
      FAULT: { x: 66, y: 86 },
      SAFE: { x: 50, y: 86 },
      GATE: { x: 30, y: 88 },
    };
  }
  if (viewportName === "mobile") {
    return {
      E1: { x: 18, y: 7 },
      E2: { x: 50, y: 7 },
      E3: { x: 82, y: 7 },
      K1: { x: 18, y: 20 },
      K2: { x: 50, y: 20 },
      K3: { x: 82, y: 20 },
      K4: { x: 18, y: 34 },
      K5: { x: 50, y: 34 },
      K9: { x: 82, y: 34 },
      C5O: { x: 50, y: 48 },
      K10: { x: 82, y: 48 },
      K6: { x: 18, y: 58 },
      K12: { x: 82, y: 62 },
      K7: { x: 18, y: 72 },
      K11: { x: 50, y: 72 },
      K13: { x: 82, y: 76 },
      K8: { x: 28, y: 88 },
      O1: { x: 70, y: 88 },
    };
  }
  return {
    E1: { x: 10, y: 14 },
    E2: { x: 28, y: 14 },
    E3: { x: 46, y: 14 },
    K1: { x: 10, y: 36 },
    K2: { x: 28, y: 36 },
    K3: { x: 46, y: 36 },
    K4: { x: 14, y: 55 },
    K5: { x: 38, y: 55 },
    K9: { x: 62, y: 55 },
    C5O: { x: 30, y: 68 },
    K6: { x: 16, y: 78 },
    K10: { x: 60, y: 68 },
    K12: { x: 76, y: 68 },
    K7: { x: 16, y: 91 },
    K11: { x: 52, y: 82 },
    K8: { x: 32, y: 94 },
    K13: { x: 78, y: 82 },
    O1: { x: 90, y: 94 },
  };
}

async function captureDiagram(browser, visualId, viewportName, sourceHeading, title, graph, layout, relPng, viewport) {
  const relHtml = `reports/renders/_tmp-${visualId}-${viewportName}.html`;
  writeText(relHtml, diagramHtml(title, graph, layout, viewportName));
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto("file:///" + path.join(root, relHtml).replace(/\\/g, "/"));
  await page.waitForLoadState("load");
  await page.waitForTimeout(100);
  await page.screenshot({ path: path.join(root, relPng) });
  const metrics = await page.evaluate(() => {
    const fonts = Array.from(document.querySelectorAll(".node,h1,.edge-list li,.mobile-edge-list li")).map((el) => parseFloat(getComputedStyle(el).fontSize));
    const canvasElement = document.querySelector(".canvas");
    const canvas = canvasElement ? canvasElement.getBoundingClientRect() : {
      left: 0,
      top: 0,
      right: window.innerWidth,
      bottom: window.innerHeight,
      width: window.innerWidth,
      height: window.innerHeight,
    };
    const edgeList = document.querySelector(".edge-list");
    const nodeInfos = Array.from(document.querySelectorAll(".node")).map((el) => {
      const rect = el.getBoundingClientRect();
      return {
        id: el.getAttribute("data-node-id"),
        label: el.textContent.trim(),
        left: rect.left,
        top: rect.top,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
      };
    });
    const outOfBounds = nodeInfos
      .filter((node) => node.left < canvas.left - 1 || node.right > canvas.right + 1 || node.top < canvas.top - 1 || node.bottom > canvas.bottom + 1)
      .map((node) => node.id);
    const overlaps = [];
    for (let i = 0; i < nodeInfos.length; i += 1) {
      for (let j = i + 1; j < nodeInfos.length; j += 1) {
        const a = nodeInfos[i];
        const b = nodeInfos[j];
        const overlapW = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const overlapH = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (overlapW > 1 && overlapH > 1) {
          overlaps.push(`${a.id}/${b.id}`);
        }
      }
    }
    const visibleLabels = nodeInfos
      .filter((node) => node.bottom > 0 && node.top < window.innerHeight && node.right > 0 && node.left < window.innerWidth)
      .map((node) => node.label);
    const mobileEdgeLabels = Array.from(document.querySelectorAll(".mobile-edge-list li"))
      .filter((el) => {
        const rect = el.getBoundingClientRect();
        return rect.bottom > 0 && rect.top < window.innerHeight && rect.right > 0 && rect.left < window.innerWidth;
      })
      .map((el) => el.textContent.trim());
    const edgeListClipped = edgeList ? edgeList.scrollHeight > edgeList.clientHeight + 1 : false;
    const verticalOverflow = document.documentElement.scrollHeight > document.documentElement.clientHeight + 2;
    const horizontalOverflow = document.documentElement.scrollWidth > document.documentElement.clientWidth + 2;
    return {
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      scrollHeight: document.documentElement.scrollHeight,
      clientHeight: document.documentElement.clientHeight,
      minFont: Math.floor(Math.min(...fonts)),
      visibleLabels: visibleLabels.length ? visibleLabels : mobileEdgeLabels,
      nodeCount: nodeInfos.length || Number(document.body.dataset.nodeCount || 0),
      edgeCount: Number(document.body.dataset.edgeCount || 0) || document.querySelectorAll(".edge-list li").length,
      outOfBounds,
      overlaps,
      edgeListClipped,
      verticalOverflow,
      horizontalOverflow,
    };
  });
  await context.close();
  fs.rmSync(path.join(root, relHtml), { force: true });
  const violations = [
    ...metrics.outOfBounds.map((id) => `node_out_of_bounds:${id}`),
    ...metrics.overlaps.map((pair) => `node_overlap:${pair}`),
    ...(metrics.edgeListClipped ? ["edge_list_clipped"] : []),
    ...(metrics.verticalOverflow ? ["page_vertical_overflow"] : []),
    ...(metrics.horizontalOverflow ? ["page_horizontal_overflow"] : []),
    ...(metrics.minFont < 16 ? [`font_below_16:${metrics.minFont}`] : []),
  ];
  const check = {
    visual_id: visualId,
    viewport: viewportName,
    screenshot: relPng,
    node_count: metrics.nodeCount,
    edge_count: metrics.edgeCount,
    min_font_px: metrics.minFont,
    out_of_bounds_nodes: metrics.outOfBounds,
    overlapping_node_pairs: metrics.overlaps,
    edge_list_clipped: metrics.edgeListClipped,
    page_vertical_overflow: metrics.verticalOverflow,
    page_horizontal_overflow: metrics.horizontalOverflow,
    result: violations.length ? "FAIL" : "PASS",
    violations,
  };
  if (violations.length) {
    throw new Error(`diagram geometry check failed for ${visualId}/${viewportName}: ${violations.join(", ")}`);
  }
  return {
    matrix: {
    visual_id: visualId,
    viewport: viewportName,
    source_heading: sourceHeading,
    screenshot: relPng,
    width: viewport.width,
    height: viewport.height,
    scroll_y: 0,
    page_scroll_width: metrics.scrollWidth,
    page_client_width: metrics.clientWidth,
    page_scroll_height: metrics.scrollHeight,
    page_client_height: metrics.clientHeight,
    reported_minimum_font_px: metrics.minFont,
      reported_visible_labels: metrics.visibleLabels.slice(0, 4),
    },
    check,
  };
}

async function captureViewport(browser, viewportName, anchor, relPng, viewport, desiredScroll) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto("file:///" + path.join(root, "reports/renders/series-architecture.html").replace(/\\/g, "/"));
  await page.waitForLoadState("load");
  await page.waitForTimeout(100);
  const dims = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollHeight: document.documentElement.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
  }));
  const maxScroll = Math.max(0, dims.scrollHeight - dims.clientHeight);
  const y = Math.max(0, Math.min(desiredScroll(dims), maxScroll));
  await page.evaluate((scrollY) => window.scrollTo(0, scrollY), y);
  await page.waitForTimeout(80);
  const actualY = Math.round(await page.evaluate(() => window.scrollY));
  await page.screenshot({ path: path.join(root, relPng) });
  const visible = await page.evaluate(() => {
    const vh = window.innerHeight;
    const out = [];
    for (const el of Array.from(document.querySelectorAll("h1,h2,h3"))) {
      const rect = el.getBoundingClientRect();
      if (rect.bottom > 0 && rect.top < vh) out.push(el.textContent.trim());
    }
    return out.slice(0, 4);
  });
  await context.close();
  return {
    viewport: viewportName,
    anchor,
    width: viewport.width,
    height: viewport.height,
    scroll_y: actualY,
    screenshot: relPng,
    page_scroll_width: dims.scrollWidth,
    page_client_width: dims.clientWidth,
    page_scroll_height: dims.scrollHeight,
    page_client_height: dims.clientHeight,
    content_anchor: `${anchor} visible headings`,
    expected_visible_content: visible.length ? visible : ["visible architecture content"],
  };
}

async function stitchedSection(page, relPng, top, height, width, viewportHeight) {
  const composites = [];
  let offset = 0;
  while (offset < height) {
    const desired = top + offset;
    await page.evaluate((scrollY) => window.scrollTo(0, scrollY), desired);
    await page.waitForTimeout(30);
    const actual = await page.evaluate(() => window.scrollY);
    const sourceTop = Math.max(0, desired - actual);
    const available = Math.max(0, viewportHeight - sourceTop);
    const chunkHeight = Math.min(height - offset, available);
    if (chunkHeight <= 0) {
      throw new Error(`empty screenshot chunk for ${relPng}`);
    }
    const viewportBuffer = await page.screenshot();
    const chunk = await sharp(viewportBuffer)
      .extract({ left: 0, top: Math.round(sourceTop), width, height: Math.round(chunkHeight) })
      .png()
      .toBuffer();
    composites.push({ input: chunk, left: 0, top: Math.round(offset) });
    offset += chunkHeight;
  }
  const output = await sharp({
    create: { width, height, channels: 4, background: { r: 255, g: 255, b: 255, alpha: 1 } },
  }).composite(composites).png().toBuffer();
  fs.writeFileSync(path.join(root, relPng), output);
}

async function cropContractSections(browser, viewportName, viewport) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto("file:///" + path.join(root, "reports/renders/series-architecture.html").replace(/\\/g, "/"));
  await page.waitForLoadState("load");
  await page.waitForTimeout(100);
  const metrics = await page.evaluate(() => {
    const headings = Array.from(document.querySelectorAll("h2")).map((h2) => ({
      text: h2.textContent.trim(),
      top: Math.floor(h2.getBoundingClientRect().top + window.scrollY),
    }));
    return {
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      scrollHeight: document.documentElement.scrollHeight,
      clientHeight: document.documentElement.clientHeight,
      headings,
    };
  });
  const defs = [
    ["chapter_index", "7. 章节索引", "architecture-contract-chapter-index"],
    ["detailed_chapter_contract", "8. 单章详细契约", "architecture-contract-detailed-chapter-contract"],
    ["evidence_mastery_mapping", "9. 证据与掌握映射", "architecture-contract-evidence-mastery-mapping"],
    ["bidirectional_coverage", "10. 双向覆盖检查", "architecture-contract-bidirectional-coverage"],
  ];
  const rows = [];
  for (const [sectionId, headingPrefix, fileBase] of defs) {
    const index = metrics.headings.findIndex((heading) => heading.text.startsWith(headingPrefix));
    if (index < 0) throw new Error(`heading not found: ${headingPrefix}`);
    const top = metrics.headings[index].top;
    const nextTop = index + 1 < metrics.headings.length ? metrics.headings[index + 1].top : metrics.scrollHeight;
    const bottom = Math.min(nextTop, metrics.scrollHeight);
    const height = bottom - top;
    const relPng = `reports/renders/${fileBase}-${viewportName}.png`;
    await stitchedSection(page, relPng, top, height, metrics.clientWidth, metrics.clientHeight);
    rows.push({
      section_id: sectionId,
      viewport: viewportName,
      source_heading: `## ${headingPrefix}`,
      screenshot: relPng,
      width: metrics.clientWidth,
      height,
      section_top: top,
      section_bottom: bottom,
      page_scroll_width: metrics.scrollWidth,
      page_client_width: metrics.clientWidth,
      page_scroll_height: metrics.scrollHeight,
      page_client_height: metrics.clientHeight,
    });
  }
  await context.close();
  return rows;
}

async function run() {
  fs.mkdirSync(outDir, { recursive: true });
  const markdown = readArchitectureMarkdown();
  const [systemSource, dagSource] = extractMermaidBlocks(markdown);
  const systemGraph = parseMermaidFlowchart(systemSource);
  const dagGraph = parseMermaidFlowchart(dagSource);

  writeText("reports/renders/series-architecture.html", mainHtml(markdown));
  writeText("reports/renders/series-architecture-system-map.html", diagramHtml("系统因果 / 数据流图", systemGraph, layoutsFor("system", "desktop"), "desktop"));
  writeText("reports/renders/series-architecture-knowledge-dag.html", diagramHtml("知识依赖 DAG", dagGraph, layoutsFor("dag", "desktop"), "desktop"));

  const browser = await chromium.launch({ executablePath: chrome, headless: true });
  const desktop = { width: 1365, height: 900 };
  const mobile = { width: 390, height: 844 };

  const viewportRows = [];
  for (const [name, viewport] of [["desktop", desktop], ["mobile", mobile]]) {
    viewportRows.push(await captureViewport(browser, name, "top", `reports/renders/architecture-${name}-top.png`, viewport, () => 0));
    viewportRows.push(await captureViewport(browser, name, "middle", `reports/renders/architecture-${name}-middle.png`, viewport, (dims) => Math.floor((dims.scrollHeight - dims.clientHeight) / 2)));
    viewportRows.push(await captureViewport(browser, name, "bottom", `reports/renders/architecture-${name}-bottom.png`, viewport, (dims) => dims.scrollHeight - dims.clientHeight));
  }
  writeText("reports/renders/series-architecture-viewport-matrix.json", JSON.stringify(viewportRows, null, 2));

  const diagramRows = [];
  const renderChecks = [];
  async function addDiagram(visualId, viewportName, sourceHeading, title, graph, graphName, relPng, viewport) {
    const captured = await captureDiagram(
      browser,
      visualId,
      viewportName,
      sourceHeading,
      title,
      graph,
      layoutsFor(graphName, viewportName),
      relPng,
      viewport,
    );
    diagramRows.push(captured.matrix);
    renderChecks.push(captured.check);
  }
  await addDiagram("system_causal_map", "desktop", "## 3. 系统因果与数据流", "系统因果 / 数据流图", systemGraph, "system", "reports/renders/architecture-system-causal-map-desktop.png", desktop);
  await addDiagram("system_causal_map", "mobile", "## 3. 系统因果与数据流", "系统因果 / 数据流图", systemGraph, "system", "reports/renders/architecture-system-causal-map-mobile.png", mobile);
  await addDiagram("knowledge_dependency_dag", "desktop", "## 4. 知识依赖图", "知识依赖 DAG", dagGraph, "dag", "reports/renders/architecture-knowledge-dependency-dag-desktop.png", desktop);
  await addDiagram("knowledge_dependency_dag", "mobile", "## 4. 知识依赖图", "知识依赖 DAG", dagGraph, "dag", "reports/renders/architecture-knowledge-dependency-dag-mobile.png", mobile);
  writeText("reports/renders/series-architecture-diagram-matrix.json", JSON.stringify(diagramRows, null, 2));
  writeText("reports/renders/series-architecture-render-check.json", JSON.stringify({
    schema_version: 1,
    generated_utc: new Date().toISOString(),
    checks: renderChecks,
  }, null, 2));

  const contractRows = [];
  contractRows.push(...await cropContractSections(browser, "desktop", desktop));
  contractRows.push(...await cropContractSections(browser, "mobile", mobile));
  await browser.close();
  const order = { chapter_index: 0, detailed_chapter_contract: 1, evidence_mastery_mapping: 2, bidirectional_coverage: 3 };
  contractRows.sort((a, b) => order[a.section_id] - order[b.section_id] || (a.viewport === "desktop" ? -1 : 1));
  writeText("reports/renders/series-architecture-contract-matrix.json", JSON.stringify(contractRows, null, 2));

  console.log(JSON.stringify({
    viewportRows: viewportRows.length,
    diagramRows: diagramRows.length,
    contractRows: contractRows.length,
    systemEdges: systemGraph.edges.length,
    dagEdges: dagGraph.edges.length,
  }, null, 2));
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
