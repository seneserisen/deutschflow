import { extractSelection } from "./selection";

(() => {
  try {
    const result = extractSelection(window.getSelection());
    chrome.runtime.sendMessage({ type: "SELECTION_EXTRACTED", payload: result });
  } catch (error) {
    chrome.runtime.sendMessage({ type: "SELECTION_ERROR", error: error instanceof Error ? error.message : "Selection could not be read." });
  }
})();

