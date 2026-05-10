let ARCHETYPES = {};

async function loadArchetypes() {
  const r = await fetch("/static/archetypes.json");
  ARCHETYPES = await r.json();
  renderAllCards();
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else node.setAttribute(k, v);
  }
  for (const c of [].concat(children)) {
    if (c == null) continue;
    node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  }
  return node;
}

function renderCardImage(arche) {
  if (arche.card_image) {
    return el("div", { class: "card-image" }, [
      el("img", { src: arche.card_image, alt: arche.title_en }),
    ]);
  }
  return el("div", { class: "card-image" }, [
    el("div", { class: "card-image-placeholder" }, [arche.number]),
  ]);
}

function renderCard(arche, { featured = false } = {}) {
  const compat = ARCHETYPES[arche.compatible.type];
  const compatLabel = compat
    ? `${compat.title_ko} (${arche.compatible.type})`
    : arche.compatible.type;

  const body = el("div", { class: "card-body" }, [
    el("div", { class: "card-num" }, [`TYPE ${arche.number} · ${arche.label_en}`]),
    el("div", { class: "card-title-en" }, [arche.title_en]),
    el("div", { class: "card-title-ko" }, [arche.title_ko]),
    el("div", { class: "card-catch" }, [arche.catchphrase]),
    el("p", { class: "card-character" }, [arche.character]),
    el("p", { class: "card-sound" }, [arche.sound]),
    el("div", { class: "card-meta" }, [
      el("div", { class: "card-meta-row" }, [
        el("span", { class: "card-meta-label" }, ["호환 유형"]),
        el("span", { class: "card-meta-value" }, [
          `${compatLabel} — `,
          el("span", { class: "card-meta-note" }, [arche.compatible.note]),
        ]),
      ]),
      el("div", { class: "card-meta-row" }, [
        el("span", { class: "card-meta-label" }, ["다음 모듈"]),
        el("span", { class: "card-meta-value" }, [
          `${arche.next_module.name} — `,
          el("span", { class: "card-meta-note" }, [arche.next_module.note]),
        ]),
      ]),
    ]),
    el("div", { class: "card-share" }, [`"${arche.share_line}"`]),
  ]);

  return el("article", { class: "card" + (featured ? " featured" : "") }, [
    renderCardImage(arche),
    body,
  ]);
}

function renderAllCards() {
  const grid = document.getElementById("cards-grid");
  grid.innerHTML = "";
  for (const key of Object.keys(ARCHETYPES)) {
    grid.appendChild(renderCard(ARCHETYPES[key]));
  }
}

function renderResult(data) {
  const section = document.getElementById("result");
  section.hidden = false;

  const banner = document.getElementById("result-banner");
  const allZero = data.scores.every((s) => s.score === 0);
  banner.innerHTML = "";
  banner.append(
    el("div", {}, [
      el("strong", {}, [data.rack.name || `Rack #${data.rack.id}`]),
      ` · 모듈 ${data.module_count}개 · 기능 태그 ${data.function_count}개`,
    ]),
  );
  if (allZero) {
    banner.append(
      el("div", { style: "margin-top:8px;color:var(--muted);font-size:0.85rem" }, [
        "매칭 가중치 캘리브레이션 전이라 점수 차이가 없습니다. 미리보기로 첫 번째 유형 카드를 보여드려요.",
      ]),
    );
  }

  const winner = data.scores[0];
  const featured = document.getElementById("featured-card");
  featured.innerHTML = "";
  if (ARCHETYPES[winner.archetype]) {
    featured.appendChild(renderCard(ARCHETYPES[winner.archetype], { featured: true }));
  }

  const scoresList = document.getElementById("scores");
  scoresList.innerHTML = "";
  for (const s of data.scores) {
    const arche = ARCHETYPES[s.archetype];
    const label = arche ? `${arche.title_ko} (${s.archetype})` : s.archetype;
    const pct = Math.max(0, Math.min(1, s.score)) * 100;
    scoresList.appendChild(
      el("li", {}, [
        `${label} — ${s.score.toFixed(3)}`,
        pct > 0 ? el("span", { class: "score-bar", style: `width:${pct}px` }) : null,
      ]),
    );
  }

  renderDiagnostic(data);

  document.getElementById("all-types").hidden = true;
  document.getElementById("explore-cta").hidden = false;

  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

document.getElementById("explore-btn").addEventListener("click", () => {
  const all = document.getElementById("all-types");
  all.hidden = false;
  document.getElementById("explore-cta").hidden = true;
  all.scrollIntoView({ behavior: "smooth", block: "start" });
});

function renderDiagnostic(data) {
  const counts = data.function_counts || {};
  const matched = new Set(data.matched_functions || []);
  const unmatched = new Set(data.unmatched_functions || []);

  const totalTags = Object.values(counts).reduce((a, b) => a + b, 0);
  const uniqueTags = Object.keys(counts).length;
  document.getElementById("diag-summary").textContent =
    `· ${uniqueTags}종 / 총 ${totalTags}회 등장`;
  document.getElementById("matched-count").textContent = `(${matched.size}종)`;
  document.getElementById("unmatched-count").textContent = `(${unmatched.size}종)`;

  fillDiagList("matched-list", counts, matched);
  fillDiagList("unmatched-list", counts, unmatched);
}

function fillDiagList(elemId, counts, nameSet) {
  const ul = document.getElementById(elemId);
  ul.innerHTML = "";
  const rows = [...nameSet]
    .map((name) => [name, counts[name] || 0])
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  if (!rows.length) {
    ul.appendChild(el("li", { class: "diag-empty" }, ["없음"]));
    return;
  }
  for (const [name, count] of rows) {
    ul.appendChild(
      el("li", {}, [
        el("span", { class: "diag-name" }, [name]),
        el("span", { class: "diag-count" }, [String(count)]),
      ]),
    );
  }
}

document.getElementById("go").addEventListener("click", async () => {
  const url = document.getElementById("url").value.trim();
  const status = document.getElementById("status");
  if (!url) {
    status.textContent = "URL을 입력해주세요.";
    return;
  }
  status.textContent = "분석 중...";
  document.getElementById("go").disabled = true;
  try {
    const r = await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rack_url: url }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${r.status}`);
    }
    const data = await r.json();
    status.textContent = "";
    renderResult(data);
  } catch (e) {
    status.textContent = "오류: " + e.message;
  } finally {
    document.getElementById("go").disabled = false;
  }
});

loadArchetypes();
