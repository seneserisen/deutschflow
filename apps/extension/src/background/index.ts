import { getSettings, setPendingSelection } from "../storage";
import type { PendingSelection } from "../types";

const MENU_ID = "deutschflow-learn-selection";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => chrome.contextMenus.create({ id: MENU_ID, title: "DeutschFlow: Learn selection", contexts: ["selection"] }));
  if (chrome.sidePanel?.setPanelBehavior) void chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
});

async function openLearningSurface(tabId?: number): Promise<void> {
  if (tabId !== undefined && chrome.sidePanel?.open) {
    try { await chrome.sidePanel.open({ tabId }); return; } catch { /* Opera/restricted fallback */ }
  }
  await chrome.tabs.create({ url: chrome.runtime.getURL("panel.html") });
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== MENU_ID) return;
  const settings = await getSettings();
  const raw = info.selectionText ?? "";
  if (!raw.trim()) return;
  if (raw.length > settings.maxSelectionLength) {
    await setPendingSelection({ text: raw.slice(0, settings.maxSelectionLength), context: null, contextUnavailable: true,
    pageTitle: tab?.title ?? "", pageUrl: safePageUrl(tab?.url), sourceDomain: "", sourceLanguage: settings.sourceLanguage,
      targetLanguage: settings.targetLanguage, capturedAt: new Date().toISOString(), error: `Selection exceeds ${settings.maxSelectionLength} characters.` });
    await openLearningSurface(tab?.id); return;
  }
  const fallback: PendingSelection = { text: raw, context: null, contextUnavailable: true, pageTitle: tab?.title ?? "",
    pageUrl: safePageUrl(tab?.url), sourceDomain: safeDomain(tab?.url), sourceLanguage: settings.sourceLanguage,
    targetLanguage: settings.targetLanguage, capturedAt: new Date().toISOString() };
  await setPendingSelection(fallback);
  if (tab?.id !== undefined) {
    try { await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["assets/selection.js"] }); }
    catch { await setPendingSelection(withRestrictedPageError(fallback)); }
  }
  await openLearningSurface(tab?.id);
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "SELECTION_EXTRACTED") {
    void getSettings().then(async (settings) => {
      const current = (await chrome.storage.local.get("pendingSelection")).pendingSelection as PendingSelection;
      await setPendingSelection({ ...current, ...message.payload, sourceLanguage: settings.sourceLanguage, targetLanguage: settings.targetLanguage });
      sendResponse({ ok: true });
    });
    return true;
  }
  return false;
});

function safeDomain(url?: string): string {
  try { const parsed = url ? new URL(url) : null; return parsed && ["http:", "https:"].includes(parsed.protocol) ? parsed.hostname : ""; } catch { return ""; }
}

function safePageUrl(url?: string): string {
  try { const parsed = url ? new URL(url) : null; return parsed && ["http:", "https:"].includes(parsed.protocol) ? parsed.href : ""; } catch { return ""; }
}

function withRestrictedPageError(selection: PendingSelection): PendingSelection {
  return { ...selection, context: null, contextUnavailable: true,
    error: "This browser page does not allow selection context access. The selected text is still available." };
}

export { openLearningSurface, safeDomain, safePageUrl, withRestrictedPageError };
