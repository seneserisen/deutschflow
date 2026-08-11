import { useState, type FormEvent } from "react";
import type { ItemType, LearningItem } from "../types";

export interface WordbookPatch {
  translation: string | null;
  item_type: ItemType;
  article: string | null;
  plural: string | null;
  infinitive: string | null;
  verb_forms: string | null;
  separable: boolean;
  required_preposition: string | null;
  required_case: string | null;
  topic: string | null;
}

interface EditorDraft {
  translation: string;
  item_type: ItemType;
  article: string;
  plural: string;
  infinitive: string;
  verb_forms: string;
  separable: boolean;
  required_preposition: string;
  required_case: string;
  topic: string;
}

function initialDraft(item: LearningItem): EditorDraft {
  return {
    translation: item.translation ?? "",
    item_type: item.item_type,
    article: item.article ?? "",
    plural: item.plural ?? "",
    infinitive: item.infinitive ?? "",
    verb_forms: item.verb_forms ?? "",
    separable: item.separable ?? false,
    required_preposition: item.required_preposition ?? "",
    required_case: item.required_case ?? "",
    topic: item.topic ?? "",
  };
}

function optional(value: string): string | null {
  const trimmed = value.trim();
  return trimmed || null;
}

export function patchFromDraft(draft: EditorDraft): WordbookPatch {
  return {
    translation: optional(draft.translation),
    item_type: draft.item_type,
    article: optional(draft.article),
    plural: optional(draft.plural),
    infinitive: optional(draft.infinitive),
    verb_forms: optional(draft.verb_forms),
    separable: draft.separable,
    required_preposition: optional(draft.required_preposition),
    required_case: optional(draft.required_case),
    topic: optional(draft.topic),
  };
}

export function WordbookEditor({ item, onSave }: { item: LearningItem; onSave: (patch: WordbookPatch) => Promise<void> }) {
  const [draft, setDraft] = useState(() => initialDraft(item));
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setSaved(false);
    setError("");
    try {
      await onSave(patchFromDraft(draft));
      setSaved(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Changes could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  return <details>
    <summary>Edit translation &amp; grammar</summary>
    <form className="stack" onSubmit={(event) => void submit(event)}>
      <div className="form-grid">
        <label>Translation<input value={draft.translation} onChange={(event) => setDraft({ ...draft, translation: event.target.value })} /></label>
        <label>Item type<select value={draft.item_type} onChange={(event) => setDraft({ ...draft, item_type: event.target.value as ItemType })}><option value="word">Word</option><option value="phrase">Phrase</option><option value="sentence">Sentence</option></select></label>
        <label>Article<input value={draft.article} onChange={(event) => setDraft({ ...draft, article: event.target.value })} placeholder="der / die / das" /></label>
        <label>Plural<input value={draft.plural} onChange={(event) => setDraft({ ...draft, plural: event.target.value })} /></label>
        <label>Infinitive<input value={draft.infinitive} onChange={(event) => setDraft({ ...draft, infinitive: event.target.value })} /></label>
        <label>Principal forms<input value={draft.verb_forms} onChange={(event) => setDraft({ ...draft, verb_forms: event.target.value })} /></label>
        <label>Required preposition<input value={draft.required_preposition} onChange={(event) => setDraft({ ...draft, required_preposition: event.target.value })} /></label>
        <label>Required case<input value={draft.required_case} onChange={(event) => setDraft({ ...draft, required_case: event.target.value })} /></label>
        <label>Topic<input value={draft.topic} onChange={(event) => setDraft({ ...draft, topic: event.target.value })} /></label>
        <label className="check"><input type="checkbox" checked={draft.separable} onChange={(event) => setDraft({ ...draft, separable: event.target.checked })} /> Separable</label>
      </div>
      <div className="button-row"><button type="submit" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>{saved && <span className="muted" role="status">Changes saved locally.</span>}</div>
      {error && <div className="alert" role="alert">{error}</div>}
    </form>
  </details>;
}
