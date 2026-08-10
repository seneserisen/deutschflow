import { openLearningSurface, safeDomain, safePageUrl, withRestrictedPageError } from "../src/background";
import type { PendingSelection } from "../src/types";

test("uses a tab fallback when side panel is unavailable", async () => {
  vi.mocked(chrome.sidePanel.open).mockRejectedValueOnce(new Error("unsupported"));
  await openLearningSurface(4);
  expect(chrome.tabs.create).toHaveBeenCalledWith({ url: expect.stringContaining("panel.html") });
});

test("handles restricted or malformed page URLs", () => {
  expect(safeDomain("https://lernen.example/path")).toBe("lernen.example");
  expect(safeDomain("chrome://settings")).toBe("");
  expect(safePageUrl("chrome://settings")).toBe("");
  expect(safeDomain("not a url")).toBe("");
});

test("marks restricted-page context failure without losing selected text", () => {
  const selection = { text: "Deutsch", context: "untrusted", contextUnavailable: false, pageTitle: "Settings",
    pageUrl: "", sourceDomain: "", sourceLanguage: "de", targetLanguage: "en", capturedAt: "2026-01-01T00:00:00Z" } satisfies PendingSelection;
  const result = withRestrictedPageError(selection);
  expect(result.text).toBe("Deutsch");
  expect(result.context).toBeNull();
  expect(result.error).toContain("does not allow");
});
