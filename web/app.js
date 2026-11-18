import { RESULTS, SUGGESTION_IDS } from "./suggestions.js";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const form = $("#ask-form");
const input = $("#query");
const submitButton = $("#ask-button");
const resultSection = $("#result");
const emptySection = $("#empty");
const loadingSection = $("#loading");
const suggestionList = $("#suggestion-list");
const emptySuggestions = $("#empty-suggestions");
const historySection = $("#history");
const historyList = $("#history-list");
const answerBody = $("#answer-body");
const answerQuestion = $("#result-question");
const evidenceList = $("#evidence-list");
const evidenceCount = $("#evidence-count");
const traceList = $("#trace");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const resultById = new Map(RESULTS.map((result) => [result.id, result]));
const HISTORY_KEY = "infraagent.live.history.v1";
const API_BASE = window.location.port === "5173" ? "http://127.0.0.1:8000" : "";
let serviceHealth = null;

let requestToken = 0;
let activeRequest = null;
let focusTimer = null;

init();

function init() {
  connectService();
  renderSuggestions(suggestionList, SUGGESTION_IDS);
  renderHistory();
  form.addEventListener("submit", handleSubmit);
  document.addEventListener("click", handleClick);
  document.addEventListener("keydown", handleKeydown);
  evidenceList.addEventListener("pointerover", handleEvidencePointer);
  evidenceList.addEventListener("pointerout", handleEvidencePointer);

  const initialQuery = new URLSearchParams(window.location.search).get("q");
  if (initialQuery) {
    input.value = initialQuery;
    runQuery(initialQuery);
  }
}

function handleSubmit(event) {
  event.preventDefault();
  const query = input.value.trim();
  if (!query) {
    input.focus();
    return;
  }
  runQuery(query);
}

async function connectService() {
  try {
    const response = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(10000) });
    if (!response.ok) throw new Error("Service unavailable");
    serviceHealth = await response.json();
    $("#service-status").textContent = "已连接本地服务";
    $("#snapshot-note").textContent =
      `${serviceHealth.sources} 篇资料，${serviceHealth.chunks.toLocaleString()} 个知识片段。`;
  } catch {
    $("#service-status").textContent = "本地服务未连接";
    $("#snapshot-note").textContent = "服务暂未连接，提交问题时可以重试。";
  }
}

async function runQuery(query) {
  const submittedAt = performance.now();
  const token = (requestToken += 1);
  activeRequest?.abort();
  const controller = new AbortController();
  activeRequest = controller;
  const timeout = window.setTimeout(() => controller.abort(), 240000);
  clearTimeout(focusTimer);
  document.body.classList.add("has-result");
  resultSection.hidden = true;
  emptySection.hidden = true;
  loadingSection.hidden = false;
  submitButton.disabled = true;
  submitButton.textContent = "检索中";
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: query }),
      signal: controller.signal,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof data.detail === "string" ? data.detail : `HTTP ${response.status}`;
      throw new Error(detail);
    }
    if (token !== requestToken) return;
    if (typeof data.answer !== "string" || !Array.isArray(data.citations)) {
      throw new Error("服务返回的数据格式不完整");
    }
    addHistory(query);
    updateUrl(query);
    renderResult(adaptResponse(query, data, performance.now() - submittedAt));
    resultSection.dataset.requestId = response.headers.get("X-Request-ID") || "";
    connectService();
  } catch (error) {
    if (token !== requestToken) return;
    const message = error.name === "AbortError"
      ? "请求超时，请稍后重试。首次检索需要加载本地模型。"
      : `暂时无法完成问答：${error.message}。请检查本地服务和回答模型配置。`;
    renderEmpty(query, message, "服务暂不可用");
  } finally {
    clearTimeout(timeout);
    if (token === requestToken) {
      activeRequest = null;
      loadingSection.hidden = true;
      submitButton.disabled = false;
      submitButton.textContent = "检索";
    }
  }
}

function adaptResponse(query, data, totalMs) {
  const trace = Array.isArray(data.trace) ? data.trace : [];
  const retrieval = trace.find((step) => step.step === "retrieve") || {};
  const generation = trace.find((step) => step.step === "generate") || {};
  const citations = data.citations.map((citation) => {
    if (!/^E[A-Za-z0-9_-]+$/.test(citation.citation_id)) {
      throw new Error("服务返回的引用ID不合法");
    }
    const metadata = citation.metadata || {};
    const source = citation.source || "来源未提供";
    const lines = citation.start_line != null
      ? `L${citation.start_line}${citation.end_line != null && citation.end_line !== citation.start_line ? `–L${citation.end_line}` : ""}`
      : citation.locator || "位置未提供";
    const sourceUrl = metadata.source_url || metadata.url;
    let url = typeof sourceUrl === "string" && /^https?:\/\//i.test(sourceUrl) ? sourceUrl : null;
    if (url && citation.start_line != null) {
      url = `${url.split("#")[0]}#${lines.replace("–", "-")}`;
    }
    const documentPath = metadata.document_id || source.split("/corpus/").pop();
    const repo = documentPath.includes("/") ? documentPath.split("/")[0] : metadata.product || "知识库";
    let content = citation.content || "";
    if (metadata.search_view_version === "source-heading-previous-line-v1") {
      content = content.replace(/^Document: [^\n]*\nSection: [^\n]*\n/, "")
        .replace(/^Previous source line: /, "相邻原文：");
    }
    return {
      id: citation.citation_id,
      repo,
      file: documentPath.split(/[\\/]/).pop(),
      section: metadata.topic || metadata.title || "原文片段",
      sourceLocator: citation.locator || `${source}#${lines}`,
      locator: lines,
      kind: "text",
      channels: [],
      content,
      url,
    };
  });
  return {
    question: query,
    answer: data.answer,
    citations,
    domain: "知识库",
    trace: {
      totalMs,
      hits: retrieval.hits ?? null,
      retrievalMs: retrieval.duration_ms ?? null,
      generateMs: generation.duration_ms ?? null,
      model: generation.model || serviceHealth?.assistant?.model || "—",
    },
  };
}

function updateUrl(query) {
  const url = new URL(window.location.href);
  url.searchParams.set("q", query);
  window.history.replaceState(null, "", url);
}


function renderResult(result) {
  emptySection.hidden = true;
  loadingSection.hidden = true;
  resultSection.hidden = false;
  document.body.classList.add("has-result");

  answerQuestion.textContent = result.question;
  answerBody.innerHTML = renderAnswer(result.answer, result.citations);
  traceList.innerHTML = renderTrace(result);
  evidenceCount.textContent = `${result.citations.length} 条引用`;
  evidenceList.innerHTML = result.citations
    .map((citation, index) => renderEvidence(citation, index, result.domain))
    .join("");

  $$(".answer-body > p", resultSection).forEach((paragraph, index) => {
    paragraph.style.setProperty("--i", index);
  });
  $$(".evidence-item", evidenceList).forEach((item, index) => {
    item.style.setProperty("--i", index);
  });

  scrollToPanel(resultSection);
}

function renderEmpty(query, message, title = "暂未找到可用证据") {
  resultSection.hidden = true;
  loadingSection.hidden = true;
  emptySection.hidden = false;
  document.body.classList.add("has-result");
  $("#empty-title").textContent = title;
  $("#empty-copy").textContent = message || `暂未找到支持“${query}”的证据，可以补充描述后重试。`;

  const nearest = nearestResults(query, 3);
  renderSuggestions(emptySuggestions, nearest.map((result) => result.id));
  scrollToPanel(emptySection);
}

function renderSuggestions(container, ids) {
  container.innerHTML = ids
    .map((id) => {
      const result = resultById.get(id);
      if (!result) return "";
      return `<li><button class="suggestion" type="button" data-ask="${escapeHtml(result.question)}">
        <span class="suggestion-q">${escapeHtml(result.question)}</span>
        <span class="domain-tag" data-domain="${escapeHtml(result.domain)}">${escapeHtml(result.domain)}</span>
      </button></li>`;
    })
    .join("");
}

function renderAnswer(text, citations) {
  const delivered = new Set(citations.map((citation) => citation.id));
  return text
    .split(/\n{2,}/)
    .filter(Boolean)
    .map((paragraph) => `<p>${formatInline(paragraph, delivered)}</p>`)
    .join("");
}

function renderEvidence(citation, index, domain) {
  const isImage = citation.kind === "image";
  const isCode = citation.kind === "code";
  const bodyId = `evidence-body-${index}`;
  let body = "";
  let toggle = "";

  if (isImage) {
    const bbox = Array.isArray(citation.bbox) ? citation.bbox.join(", ") : "";
    body = `<figure class="ev-figure">
      <img src="${escapeHtml(citation.image)}" alt="${escapeHtml(citation.content)}" width="640" height="420" decoding="sync">
      <figcaption><span>${escapeHtml(citation.content)}</span>${bbox ? `<span class="ev-bbox">bbox ${escapeHtml(bbox)}</span>` : ""}</figcaption>
    </figure>`;
  } else if (isCode) {
    body = `<div class="ev-excerpt ev-code" id="${bodyId}"><pre><code>${escapeHtml(cleanRaw(citation.content))}</code></pre></div>`;
    toggle = `<button class="link-btn ev-toggle" type="button" data-expand aria-expanded="false" aria-controls="${bodyId}">展开全文</button>`;
  } else {
    body = `<div class="ev-excerpt" id="${bodyId}">${renderExcerpt(citation.content)}</div>`;
    const long = citation.content.length > 200 || citation.content.split("\n").length > 6;
    if (long) {
      toggle = `<button class="link-btn ev-toggle" type="button" data-expand aria-expanded="false" aria-controls="${bodyId}">展开全文</button>`;
    }
  }

  const copyText = citation.url || citation.sourceLocator || `${citation.file} ${citation.locator}`;
  const github = citation.url
    ? `<a class="link-btn" href="${escapeHtml(citation.url)}" target="_blank" rel="noreferrer">在 GitHub 查看</a>`
    : "";

  return `<li class="evidence-item" data-cite-item="${citation.id}" data-domain="${escapeHtml(domain)}">
    <div class="ev-top">
      <span class="ev-file">${escapeHtml(citation.file)}</span>
      <span class="domain-tag" data-domain="${escapeHtml(domain)}">${escapeHtml(domain)}</span>
    </div>
    <p class="ev-meta">${escapeHtml(citation.repo)}<span class="ev-sep">/</span>${escapeHtml(citation.section)}</p>
    <p class="ev-locator"><span>${escapeHtml(citation.locator)}</span><span class="ev-channels">${citation.channels.map(escapeHtml).join(" + ")}</span></p>
    ${body}
    ${toggle}
    <div class="ev-actions">
      <button class="link-btn" type="button" data-copy="${escapeHtml(copyText)}">复制定位</button>
      ${github}
    </div>
  </li>`;
}

function renderTrace(result) {
  const trace = result.trace;
  const items = [
    ["总耗时", formatDuration(trace.totalMs)],
    ["命中", trace.hits == null ? "—" : `${trace.hits} 个片段`],
    ["引用", `${result.citations.length} 条`],
    ["检索", formatDuration(trace.retrievalMs)],
    ["生成", formatDuration(trace.generateMs)],
    ["模型", trace.model],
  ];
  return items
    .map(([label, value]) => `<div class="trace-item"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`)
    .join("");
}

function renderExcerpt(text) {
  const parts = cleanRaw(text).split("```");
  let html = "";
  parts.forEach((part, index) => {
    if (index % 2 === 1) {
      const code = part.replace(/^[a-zA-Z0-9_-]*\n/, "").trimEnd();
      html += `<pre><code>${escapeHtml(code)}</code></pre>`;
      return;
    }
    const cleaned = part
      .split("\n")
      .map((line) => line.replace(/^#{1,6}\s+/, "").replace(/^>\s?/, ""))
      .join("\n")
      .trim();
    if (cleaned) {
      html += `<p>${formatInline(cleanMath(cleaned), new Set())}</p>`;
    }
  });
  return html || `<p>${escapeHtml(cleanMath(cleanRaw(text)))}</p>`;
}

function cleanMath(text) {
  return text.replace(/\$([^$]+)\$/g, (match, expression) => simplifyTex(expression));
}

function simplifyTex(expression) {
  return expression
    .replace(/\\text\{([^{}]*)\}/g, "$1")
    .replace(/\\mathrm\{([^{}]*)\}/g, "$1")
    .replace(/\\_/g, "_")
    .replace(/\\sim/g, "~")
    .replace(/\\cdot/g, "·")
    .replace(/\\times/g, "×")
    .replace(/\\leq/g, "≤")
    .replace(/\\geq/g, "≥")
    .replace(/\\left|\\right/g, "")
    .replace(/\\[a-zA-Z]+/g, "");
}

function cleanRaw(text) {
  return String(text).replace(/\\`/g, "`");
}

function formatInline(text, deliveredCitations) {
  let html = escapeHtml(text);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\[(E[A-Za-z0-9_-]+)\]/g, (match, id) => {
    if (!deliveredCitations.has(id)) return match;
    return `<button class="cite" type="button" data-cite="${id}" title="${id}" aria-label="查看证据 ${id}">E${id.slice(1, 9)}</button>`;
  });
  return html.replace(/\n/g, "<br>");
}

function formatDuration(milliseconds) {
  if (milliseconds == null) return "—";
  if (milliseconds >= 1000) return `${(milliseconds / 1000).toFixed(1)} s`;
  return `${Math.round(milliseconds)} ms`;
}

function handleClick(event) {
  const ask = event.target.closest("[data-ask]");
  if (ask) {
    const query = ask.dataset.ask;
    input.value = query;
    runQuery(query);
    return;
  }

  const citation = event.target.closest("[data-cite]");
  if (citation) {
    focusCitation(citation.dataset.cite);
    return;
  }

  const copy = event.target.closest("[data-copy]");
  if (copy) {
    copyToClipboard(copy.dataset.copy, copy);
    return;
  }

  const toggle = event.target.closest("[data-expand]");
  if (toggle) {
    toggleExcerpt(toggle);
  }
}

function handleKeydown(event) {
  if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return;

  if (event.key === "/" && !isTypingTarget(event.target)) {
    event.preventDefault();
    input.focus();
    input.select();
    return;
  }

  if (event.key === "Escape") {
    $$(".evidence-item.is-focused", evidenceList).forEach((item) => item.classList.remove("is-focused"));
    $$(".cite.is-active, .cite.is-linked", answerBody).forEach((element) => {
      element.classList.remove("is-active", "is-linked");
    });
    clearTimeout(focusTimer);
    if (document.activeElement === input) input.blur();
  }
}

function handleEvidencePointer(event) {
  const item = event.target.closest(".evidence-item");
  if (!item) return;

  if (event.type === "pointerout") {
    if (event.relatedTarget && item.contains(event.relatedTarget)) return;
    setLinkedCitations(item.dataset.citeItem, false);
  } else {
    setLinkedCitations(item.dataset.citeItem, true);
  }
}

function setLinkedCitations(id, linked) {
  $$(`.cite[data-cite="${id}"]`, answerBody).forEach((element) => {
    element.classList.toggle("is-linked", linked);
  });
}

function focusCitation(id) {
  const item = $(`[data-cite-item="${id}"]`, evidenceList);
  if (!item) return;

  $$(".evidence-item.is-focused", evidenceList).forEach((element) => element.classList.remove("is-focused"));
  $$(".cite.is-active", answerBody).forEach((element) => element.classList.remove("is-active"));

  item.classList.add("is-focused");
  $$(`.cite[data-cite="${id}"]`, answerBody).forEach((element) => element.classList.add("is-active"));
  item.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "nearest" });

  clearTimeout(focusTimer);
  focusTimer = window.setTimeout(() => {
    item.classList.remove("is-focused");
    $$(".cite.is-active", answerBody).forEach((element) => element.classList.remove("is-active"));
  }, 3000);
}

function toggleExcerpt(button) {
  const item = button.closest(".evidence-item");
  if (!item) return;
  const expanded = item.classList.toggle("is-expanded");
  button.textContent = expanded ? "收起" : "展开全文";
  button.setAttribute("aria-expanded", String(expanded));
}

async function copyToClipboard(text, button) {
  const original = button.textContent;
  let copied = false;
  try {
    await navigator.clipboard.writeText(text);
    copied = true;
  } catch {
    copied = fallbackCopy(text);
  }
  button.textContent = copied ? "已复制" : "复制失败";
  window.setTimeout(() => {
    button.textContent = original;
  }, 1600);
}

function fallbackCopy(text) {
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  let copied = false;
  try {
    copied = document.execCommand("copy");
  } catch {
    copied = false;
  }
  area.remove();
  return copied;
}

function addHistory(query) {
  const next = [query, ...readHistory().filter((item) => item !== query)].slice(0, 5);
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
  } catch {
    return;
  }
  renderHistory();
}

function readHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string") : [];
  } catch {
    return [];
  }
}

function renderHistory() {
  const items = readHistory();
  historySection.hidden = items.length === 0;
  historyList.innerHTML = items
    .map((query) => `<li><button type="button" data-ask="${escapeHtml(query)}">${escapeHtml(query)}</button></li>`)
    .join("");
}

function nearestResults(query, limit) {
  const normalized = normalize(query);
  const ranked = RESULTS.map((result) => ({
    result,
    score: diceCoefficient(normalized, normalize(result.question)),
  })).sort((a, b) => b.score - a.score);
  return ranked.slice(0, limit).map((entry) => entry.result);
}

function diceCoefficient(left, right) {
  if (!left || !right) return 0;
  if (left === right) return 1;

  const counts = new Map();
  for (const gram of bigrams(left)) {
    counts.set(gram, (counts.get(gram) || 0) + 1);
  }

  let intersection = 0;
  for (const gram of bigrams(right)) {
    const count = counts.get(gram) || 0;
    if (count > 0) {
      intersection += 1;
      counts.set(gram, count - 1);
    }
  }

  const total = Math.max(left.length - 1, 0) + Math.max(right.length - 1, 0);
  return total === 0 ? 0 : (2 * intersection) / total;
}

function bigrams(value) {
  const grams = [];
  for (let index = 0; index < value.length - 1; index += 1) {
    grams.push(value.slice(index, index + 2));
  }
  return grams;
}

function normalize(value) {
  return String(value).toLowerCase().replace(/[\s\p{P}\p{S}]+/gu, "");
}

function isTypingTarget(target) {
  if (!(target instanceof HTMLElement)) return false;
  return (
    target.tagName === "INPUT" ||
    target.tagName === "TEXTAREA" ||
    target.tagName === "SELECT" ||
    target.isContentEditable
  );
}

function scrollToPanel(element) {
  element.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "start" });
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => {
    switch (character) {
      case "&":
        return "&amp;";
      case "<":
        return "&lt;";
      case ">":
        return "&gt;";
      case '"':
        return "&quot;";
      case "'":
        return "&#39;";
      default:
        return character;
    }
  });
}
