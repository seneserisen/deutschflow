export interface ExtractedSelection {
  text: string;
  context: string | null;
  contextUnavailable: boolean;
}

export function normalizeWhitespace(value: string): string {
  return value.replace(/\s+/gu, " ").trim();
}

export function sentenceAround(text: string, selected: string, maxContext = 1200): string | null {
  const full = normalizeWhitespace(text);
  const needle = normalizeWhitespace(selected);
  const fullIndex = full.indexOf(needle);
  if (!needle || fullIndex < 0) return full.slice(0, maxContext) || null;
  const windowStart = Math.max(0, fullIndex - Math.floor((maxContext - needle.length) / 2));
  const normalized = full.slice(windowStart, windowStart + maxContext);
  const index = fullIndex - windowStart;
  const before = normalized.slice(0, index);
  const after = normalized.slice(index + needle.length);
  const startBoundary = Math.max(before.lastIndexOf("."), before.lastIndexOf("!"), before.lastIndexOf("?"));
  const endings = [after.indexOf("."), after.indexOf("!"), after.indexOf("?")].filter((value) => value >= 0);
  const endBoundary = endings.length ? Math.min(...endings) : after.length - 1;
  return normalizeWhitespace(normalized.slice(startBoundary + 1, index + needle.length + endBoundary + 1));
}

export function extractSelection(selection: Selection | null, maxSelection = 500, maxContext = 1200): ExtractedSelection {
  if (!selection || selection.rangeCount === 0) return { text: "", context: null, contextUnavailable: true };
  const text = selection.toString();
  if (!text.trim()) return { text: "", context: null, contextUnavailable: true };
  if (text.length > maxSelection) throw new Error(`Selection exceeds ${maxSelection} characters.`);
  const range = selection.getRangeAt(0);
  const element = range.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
    ? range.commonAncestorContainer as Element
    : range.commonAncestorContainer.parentElement;
  const block = element?.closest("p, li, blockquote, td, th, figcaption, article, section") ?? element;
  const context = block?.textContent ? sentenceAround(block.textContent, text, maxContext) : null;
  return { text, context, contextUnavailable: !context };
}
