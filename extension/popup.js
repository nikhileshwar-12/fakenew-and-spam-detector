const DEFAULT_API = "http://127.0.0.1:5000";
const urlInput = document.getElementById("url");
const statusEl = document.getElementById("status");

chrome.storage.sync.get({ apiUrl: DEFAULT_API }, (d) => { urlInput.value = d.apiUrl; });

document.getElementById("save").onclick = () => {
  const apiUrl = urlInput.value.trim() || DEFAULT_API;
  chrome.storage.sync.set({ apiUrl }, () => {
    statusEl.textContent = "✔ Saved.";
    statusEl.className = "status ok";
  });
};

document.getElementById("test").onclick = async () => {
  const apiUrl = (urlInput.value.trim() || DEFAULT_API).replace(/\/$/, "");
  statusEl.textContent = "Testing…"; statusEl.className = "status";
  try {
    const res = await fetch(apiUrl + "/api/analyze", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "This is a test message.", mode: "spam" })
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    await res.json();
    statusEl.textContent = "✔ Connected! TruthGuard is reachable.";
    statusEl.className = "status ok";
  } catch (e) {
    statusEl.textContent = "✗ Could not connect. Is the app running?";
    statusEl.className = "status bad";
  }
};