import React from "react";
import { createRoot } from "react-dom/client";
import "../sidepanel/styles.css";

function Popup() {
  async function open() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.id !== undefined && chrome.sidePanel?.open) { try { await chrome.sidePanel.open({ tabId: tab.id }); window.close(); return; } catch { /* fallback */ } }
    await chrome.tabs.create({ url: chrome.runtime.getURL("panel.html") }); window.close();
  }
  return <div className="app-shell" style={{ width: 300, minHeight: "auto" }}><header className="masthead"><div className="logo">DF</div><div><h1>DeutschFlow</h1><p>Local German immersion</p></div></header><div className="stack" style={{ marginTop: 20 }}><p>Select German text, right-click, then choose <strong>DeutschFlow: Learn selection</strong>.</p><button className="primary" onClick={() => void open()}>Open DeutschFlow</button></div></div>;
}
createRoot(document.getElementById("root")!).render(<Popup />);

