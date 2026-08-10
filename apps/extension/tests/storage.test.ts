import { getPendingSelection, setPendingSelection } from "../src/storage";
import type { PendingSelection } from "../src/types";

test("pending selection round-trips through extension-local state", async () => {
  const pending: PendingSelection = { text: "arbeiten", context: "Wir arbeiten heute.", contextUnavailable: false, pageTitle: "Test", pageUrl: "https://example.test", sourceDomain: "example.test", sourceLanguage: "de", targetLanguage: "en", capturedAt: new Date().toISOString() };
  await setPendingSelection(pending);
  expect(await getPendingSelection()).toEqual(pending);
});

