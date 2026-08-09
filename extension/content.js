let tgCard = null;

function removeCard() {
  if (tgCard && tgCard.parentNode) tgCard.parentNode.removeChild(tgCard);
  tgCard = null;
}
function getAnchorRect() {
  const sel = window.getSelection();
  if (sel && sel.rangeCount > 0) {
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    if (rect && (rect.top || rect.left)) return rect;
  }
  return { bottom: 80, left: 80, top: 80 };
}
function baseCard() {
  removeCard();
  const rect = getAnchorRect();
  const card = document.createElement("div");
  card.className = "tg-card";
  card.style.top = (window.scrollY + rect.bottom + 8) + "px";
  const left = Math.min(window.scrollX + rect.left, window.scrollX + window.innerWidth - 360);
  card.style.left = Math.max(left, window.scrollX + 8) + "px";
  document.body.appendChild(card);
  tgCard = card;
  return card;
}
function meter(pct, bad) {
  const col = bad ? "linear-gradient(90deg,#ff8a5d,#ff5d6c)" : "linear-gradient(90deg,#2fd07f,#37c8ff)";
  return `<div class="tg-meter"><span style="width:${pct}%;background:${col}"></span></div>`;
}
function esc(s) {
  return (s + "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function verdictBlock(title, label, bad, prob, probLabel) {
  return `<div class="tg-block">
    <div class="tg-row"><span class="tg-title">${title}</span>
      <span class="tg-badge ${bad ? "tg-bad" : "tg-good"}">${esc(label)}</span></div>
    ${meter(prob, bad)}
    <div class="tg-sub">${probLabel}: <b>${prob}%</b></div>
  </div>`;
}

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "TG_LOADING") {
    const card = baseCard();
    card.innerHTML = `<div class="tg-head">🛡️ TruthGuard <span class="tg-x">✕</span></div>
      <div class="tg-body"><div class="tg-spin"></div> Analyzing selected text…</div>`;
    card.querySelector(".tg-x").onclick = removeCard;
  }
  if (msg.type === "TG_ERROR") {
    const card = tgCard || baseCard();
    card.innerHTML = `<div class="tg-head">🛡️ TruthGuard <span class="tg-x">✕</span></div>
      <div class="tg-body tg-err">${esc(msg.error)}</div>`;
    card.querySelector(".tg-x").onclick = removeCard;
  }
  if (msg.type === "TG_RESULT") {
    const d = msg.data;
    const card = tgCard || baseCard();
    let html = `<div class="tg-head">🛡️ TruthGuard <span class="tg-x">✕</span></div><div class="tg-body">`;
    if (d.fake_news) html += verdictBlock("📰 Fake news", d.fake_news.label, d.fake_news.is_fake, d.fake_news.fake_probability, "Fake prob.");
    if (d.spam) html += verdictBlock("✉️ Spam", d.spam.label, d.spam.is_spam, d.spam.spam_probability, "Spam prob.");
    const kw = ((d.fake_news && d.fake_news.keywords) || []).slice(0, 5);
    if (kw.length) html += `<div class="tg-kw">${kw.map(k => `<span>${esc(k)}</span>`).join("")}</div>`;
    html += `<div class="tg-note">AI estimate — verify important claims independently.</div></div>`;
    card.innerHTML = html;
    card.querySelector(".tg-x").onclick = removeCard;
  }
});

document.addEventListener("mousedown", (e) => { if (tgCard && !tgCard.contains(e.target)) removeCard(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") removeCard(); });