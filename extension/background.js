const DEFAULT_API = "http://127.0.0.1:5000";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "truthguard-check",
    title: "🛡️ Check with TruthGuard",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "truthguard-check" || !info.selectionText) return;
  const text = info.selectionText.trim();
  chrome.tabs.sendMessage(tab.id, { type: "TG_LOADING", text });

  const { apiUrl } = await chrome.storage.sync.get({ apiUrl: DEFAULT_API });
  try {
    const res = await fetch(apiUrl.replace(/\/$/, "") + "/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, mode: "auto" })
    });
    if (!res.ok) throw new Error("Server returned " + res.status);
    const data = await res.json();
    chrome.tabs.sendMessage(tab.id, { type: "TG_RESULT", data, text });
  } catch (e) {
    chrome.tabs.sendMessage(tab.id, {
      type: "TG_ERROR",
      error: "Could not reach TruthGuard at " + apiUrl +
             ". Make sure the app is running (python app.py) or set your live URL in the extension popup."
    });
  }
});