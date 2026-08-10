import { extractSelection, normalizeWhitespace, sentenceAround } from "../src/content/selection";

describe("selection extraction", () => {
  test("normalizes whitespace while retaining German punctuation", () => {
    expect(normalizeWhitespace("  Grüß   dich!\nWie geht’s? ")).toBe("Grüß dich! Wie geht’s?");
  });

  test("finds a bounded surrounding sentence", () => {
    expect(sentenceAround("Zuerst etwas. Die Universität ist groß! Danach mehr.", "Universität"))
      .toBe("Die Universität ist groß!");
  });

  test("keeps context centered on a selection late in a long block", () => {
    const context = sentenceAround(`${"Früher. ".repeat(300)}Das Zielwort steht hier.`, "Zielwort", 120);
    expect(context).toContain("Zielwort");
    expect(context!.length).toBeLessThanOrEqual(120);
  });

  test("extracts selection from a nested link and nearest block", () => {
    document.body.innerHTML = "<p>Heute besuche ich die <a><strong>Universität</strong></a>. Danach lerne ich.</p>";
    const text = document.querySelector("strong")!.firstChild!;
    const range = document.createRange(); range.selectNodeContents(text);
    const selection = window.getSelection()!; selection.removeAllRanges(); selection.addRange(range);
    expect(extractSelection(selection)).toEqual({ text: "Universität", context: "Heute besuche ich die Universität.", contextUnavailable: false });
  });

  test("reports unavailable context and rejects excessive selections", () => {
    expect(extractSelection(null).contextUnavailable).toBe(true);
    document.body.innerHTML = `<p>${"a".repeat(501)}</p>`;
    const range = document.createRange(); range.selectNodeContents(document.querySelector("p")!);
    const selection = window.getSelection()!; selection.removeAllRanges(); selection.addRange(range);
    expect(() => extractSelection(selection, 500)).toThrow("Selection exceeds");
  });
});
