import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { api, ApiError, downloadExport } from "../api/client";
import { DEFAULT_SETTINGS, getPendingSelection, getSettings, saveSettings, type ExtensionSettings } from "../storage";
import type { DueCard, ItemType, LearningItem, PendingSelection, TranslationResult } from "../types";
import { reviewAction } from "../review/keyboard";
import "./styles.css";
import "./settings.css";

type View = "learn" | "wordbook" | "review" | "settings";

function message(error: unknown): string {
  return error instanceof Error ? error.message : "An unexpected local error occurred.";
}

function App() {
  const [view, setView] = useState<View>("learn");
  return <div className="app-shell">
    <header className="masthead"><div className="logo">DF</div><div><h1>DeutschFlow</h1><p>Learn from what you choose to read.</p></div></header>
    <nav aria-label="Main sections" className="tabs">
      {(["learn", "wordbook", "review", "settings"] as View[]).map((tab) =>
        <button key={tab} className={view === tab ? "active" : ""} onClick={() => setView(tab)}>{tab[0].toUpperCase() + tab.slice(1)}</button>)}
    </nav>
    <main>{view === "learn" && <LearnView goWordbook={() => setView("wordbook")} />}
      {view === "wordbook" && <WordbookView />}{view === "review" && <ReviewView />}
      {view === "settings" && <SettingsView />}</main>
    <footer>Local-first · No remote fallback</footer>
  </div>;
}

function LearnView({ goWordbook }: { goWordbook: () => void }) {
  const [selection, setSelection] = useState<PendingSelection | null>(null);
  const [translation, setTranslation] = useState<TranslationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [duplicateId, setDuplicateId] = useState<number | null>(null);
  const [type, setType] = useState<ItemType>("word");
  const [notes, setNotes] = useState(""); const [topic, setTopic] = useState("");
  const [grammar, setGrammar] = useState({ article: "", plural: "", infinitive: "", verb_forms: "", required_preposition: "", required_case: "", separable: false });

  useEffect(() => {
    void getPendingSelection().then((pending) => { setSelection(pending); if (pending) void translate(pending); });
    const listener = (changes: Record<string, chrome.storage.StorageChange>) => {
      if (changes.pendingSelection?.newValue) { const pending = changes.pendingSelection.newValue as PendingSelection; setSelection(pending); setTranslation(null); setError(pending.error ?? ""); void translate(pending); }
    };
    chrome.storage.onChanged.addListener(listener); return () => chrome.storage.onChanged.removeListener(listener);
  }, []);

  async function translate(pending = selection) {
    if (!pending || pending.error) return;
    setLoading(true); setError(""); setDuplicateId(null);
    try { setTranslation(await api<TranslationResult>("/api/v1/translate", { method: "POST", body: JSON.stringify({ text: pending.text, context: pending.context, source_language: pending.sourceLanguage, target_language: pending.targetLanguage }) })); }
    catch (cause) { setError(message(cause)); } finally { setLoading(false); }
  }

  async function save(duplicate_action: "reject" | "create_new" | "attach_occurrence" = "reject") {
    if (!selection) return;
    setLoading(true); setError("");
    try {
      const extensionSettings = await getSettings();
      await api("/api/v1/items", { method: "POST", body: JSON.stringify({ original_text: selection.text, item_type: type,
        translation: translation?.translated_text || null, notes: notes || null, topic: topic || null, ...grammar,
        article: grammar.article || null, plural: grammar.plural || null, infinitive: grammar.infinitive || null,
        verb_forms: grammar.verb_forms || null, required_preposition: grammar.required_preposition || null, required_case: grammar.required_case || null,
        source_language: selection.sourceLanguage, target_language: selection.targetLanguage, duplicate_action,
        card_types: extensionSettings.defaultCardTypes,
        occurrence: { selected_text: selection.text, source_sentence: selection.context, page_title: selection.pageTitle,
          page_url: selection.pageUrl || null, source_domain: selection.sourceDomain || null },
        meaning: translation ? { translation: translation.translated_text, provider: translation.provider_name, confidence: translation.confidence_or_unknown } : null }) });
      setDuplicateId(null); goWordbook();
    } catch (cause) {
      if (cause instanceof ApiError && cause.code === "DUPLICATE_ITEM") { const found = cause.message.match(/#(\d+)/); setDuplicateId(found ? Number(found[1]) : 0); }
      else setError(message(cause));
    } finally { setLoading(false); }
  }

  if (!selection) return <EmptyState title="Select something German" body="Highlight a word or phrase on a webpage, right-click, and choose “DeutschFlow: Learn selection”." />;
  return <section className="stack" aria-labelledby="learn-heading">
    <div className="eyebrow">Current selection</div><h2 id="learn-heading" className="german">{selection.text}</h2>
    <div className="meta">{selection.sourceDomain || "Restricted/local page"}{selection.pageTitle ? ` · ${selection.pageTitle}` : ""}</div>
    {selection.context ? <blockquote>{selection.context}</blockquote> : <p className="muted">Surrounding context unavailable. Only your explicit selection will be saved.</p>}
    <div className="translation-card" aria-live="polite">
      <span className="eyebrow">Meaning</span>
      {loading && !translation ? <p>Asking the local provider…</p> : translation ? <><strong>{translation.translated_text}</strong><small>{translation.provider_name} · confidence {translation.confidence_or_unknown}</small></> : <p>Translation unavailable. You can still save this item.</p>}
    </div>
    {error && <div className="alert" role="alert"><strong>Needs attention</strong><span>{error}</span><button onClick={() => void translate()}>Retry translation</button></div>}
    {duplicateId !== null && <div className="alert warning" role="alert"><strong>Possible duplicate</strong><span>An exact German text and translation already exists.</span><div className="button-row"><button onClick={() => void save("attach_occurrence")}>Add this occurrence</button><button className="secondary" onClick={() => void save("create_new")}>Keep separate sense</button></div></div>}
    <label>Item type<select value={type} onChange={(event) => setType(event.target.value as ItemType)}><option value="word">Word</option><option value="phrase">Phrase</option><option value="sentence">Sentence</option></select></label>
    <details><summary>Grammar details (manual)</summary><div className="form-grid">
      <label>Article<input value={grammar.article} onChange={(e) => setGrammar({ ...grammar, article: e.target.value })} placeholder="der / die / das" /></label>
      <label>Plural<input value={grammar.plural} onChange={(e) => setGrammar({ ...grammar, plural: e.target.value })} /></label>
      <label>Infinitive<input value={grammar.infinitive} onChange={(e) => setGrammar({ ...grammar, infinitive: e.target.value })} /></label>
      <label>Principal forms<input value={grammar.verb_forms} onChange={(e) => setGrammar({ ...grammar, verb_forms: e.target.value })} /></label>
      <label>Required preposition<input value={grammar.required_preposition} onChange={(e) => setGrammar({ ...grammar, required_preposition: e.target.value })} /></label>
      <label>Required case<input value={grammar.required_case} onChange={(e) => setGrammar({ ...grammar, required_case: e.target.value })} /></label>
      <label className="check"><input type="checkbox" checked={grammar.separable} onChange={(e) => setGrammar({ ...grammar, separable: e.target.checked })} /> Separable</label>
    </div><p className="muted">These facts are not generated by the translation provider. Verify and edit them yourself.</p></details>
    <label>Topic<input value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="University, work, everyday…" /></label>
    <label>Notes<textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={3} /></label>
    <button className="primary" disabled={loading} onClick={() => void save()}>{loading ? "Working…" : "Save to wordbook"}</button>
  </section>;
}

function WordbookView() {
  const [items, setItems] = useState<LearningItem[]>([]); const [error, setError] = useState("");
  const [filters, setFilters] = useState({ q: "", status: "", item_type: "", source_domain: "", review_state: "" });
  async function load() { try { const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v)); const data = await api<{ items: LearningItem[] }>(`/api/v1/items?${params}`); setItems(data.items); setError(""); } catch (cause) { setError(message(cause)); } }
  useEffect(() => { void load(); }, []);
  async function patch(id: number, body: object) { await api(`/api/v1/items/${id}`, { method: "PATCH", body: JSON.stringify(body) }); await load(); }
  async function remove(id: number) { if (confirm("Delete this learning item and its review history?")) { await api(`/api/v1/items/${id}`, { method: "DELETE" }); await load(); } }
  return <section className="stack"><div className="section-heading"><div><div className="eyebrow">Saved locally</div><h2>Wordbook</h2></div><span className="count">{items.length}</span></div>
    <form className="filters" onSubmit={(e) => { e.preventDefault(); void load(); }}>
      <label>Search<input value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} placeholder="German or meaning" /></label>
      <label>Status<select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}><option value="">All</option>{["new","learning","reviewing","known","suspended"].map(v => <option key={v}>{v}</option>)}</select></label>
      <label>Type<select value={filters.item_type} onChange={(e) => setFilters({ ...filters, item_type: e.target.value })}><option value="">All</option><option>word</option><option>phrase</option><option>sentence</option></select></label>
      <label>Source domain<input value={filters.source_domain} onChange={(e) => setFilters({ ...filters, source_domain: e.target.value })} placeholder="example.org" /></label>
      <label>Review<select value={filters.review_state} onChange={(e) => setFilters({ ...filters, review_state: e.target.value })}><option value="">All</option><option value="due">Due</option><option value="suspended">Suspended</option></select></label>
      <button>Apply filters</button>
    </form>
    {error && <div className="alert" role="alert">{error}</div>}
    <div className="item-list">{items.map((item) => <article className="item" key={item.id}>
      <div><span className="pill">{item.item_type}</span><h3>{item.original_text}</h3><p>{item.translation || "No translation saved"}</p>
        <small>{item.status} · {new Date(item.created_at).toLocaleDateString()} · {item.occurrences[0]?.source_domain || "no source"}</small></div>
      <label>Notes<textarea defaultValue={item.notes} onBlur={(e) => { if (e.target.value !== (item.notes ?? "")) void patch(item.id, { notes: e.target.value }); }} /></label>
      <div className="button-row">{item.occurrences[0]?.page_url && <a className="button-link" href={item.occurrences[0].page_url} target="_blank" rel="noreferrer">Open source</a>}
        <button className="secondary" onClick={() => void patch(item.id, { status: item.status === "suspended" ? "learning" : "suspended" })}>{item.status === "suspended" ? "Resume" : "Suspend"}</button>
        <button className="danger" onClick={() => void remove(item.id)}>Delete</button></div>
    </article>)}</div>{!items.length && !error && <EmptyState title="No matching items" body="Save a selection or adjust the filters." />}
  </section>;
}

function ReviewView() {
  const [cards, setCards] = useState<DueCard[]>([]); const [index, setIndex] = useState(0); const [revealed, setRevealed] = useState(false);
  const [response, setResponse] = useState(""); const [error, setError] = useState(""); const [reviewed, setReviewed] = useState(0);
  const card = cards[index];
  async function load() { try { const data = await api<{ cards: DueCard[] }>("/api/v1/review/due"); setCards(data.cards); setIndex(0); } catch (cause) { setError(message(cause)); } }
  useEffect(() => { void load(); }, []);
  async function grade(rating: string) { if (!card) return; try { await api(`/api/v1/review/${card.id}`, { method: "POST", body: JSON.stringify({ rating, response: response || null, was_correct: null }) }); setReviewed((v) => v + 1); setIndex((v) => v + 1); setRevealed(false); setResponse(""); } catch (cause) { setError(message(cause)); } }
  useEffect(() => {
    const handler = (event: KeyboardEvent) => { const action = reviewAction(event, revealed); if (action === "reveal") { if (event.code === "Space") event.preventDefault(); setRevealed(true); } else if (action) void grade(action); };
    window.addEventListener("keydown", handler); return () => window.removeEventListener("keydown", handler);
  }, [revealed, card, response]);
  if (!card) return <section className="stack"><div className="section-heading"><div><div className="eyebrow">Daily practice</div><h2>Review</h2></div></div>{error ? <div className="alert">{error}</div> : <EmptyState title={reviewed ? "Session complete" : "You’re caught up"} body={reviewed ? `${reviewed} card${reviewed === 1 ? "" : "s"} reviewed.` : "No cards are due right now."} />}</section>;
  const escapedGerman = card.german.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const sentencePrompt = card.source_sentence?.replace(new RegExp(escapedGerman, "i"), "_____");
  const prompt = card.card_type === "recognition" ? card.german : card.card_type === "article" ? `Article: ${card.german}` : ["cloze", "source_sentence"].includes(card.card_type) ? sentencePrompt || card.translation || card.german : card.translation || card.german;
  const answer = card.card_type === "recognition" ? card.translation : card.card_type === "article" ? `${card.article} ${card.german}` : card.german;
  return <section className="stack review"><div className="section-heading"><div><div className="eyebrow">Daily practice</div><h2>Review</h2></div><span className="count">{cards.length - index}</span></div>
    <div className="progress"><span style={{ width: `${(index / cards.length) * 100}%` }} /></div><div className="review-card"><span className="pill">{card.card_type}</span><h3>{prompt}</h3>
      {!revealed ? <><label>Your answer<input autoFocus value={response} onChange={(e) => setResponse(e.target.value)} /><small>Press Enter to reveal</small></label><button className="primary" onClick={() => setRevealed(true)}>Reveal answer <kbd>Space</kbd></button></>
        : <><div className="answer"><span className="eyebrow">Answer</span><strong>{answer}</strong>{card.source_sentence && <blockquote>{card.source_sentence}</blockquote>}</div><div className="grade-grid">{[["Again","1"],["Hard","2"],["Good","3"],["Easy","4"]].map(([label,key]) => <button key={key} onClick={() => void grade(label.toLowerCase())}>{label}<kbd>{key}</kbd></button>)}</div></>}
    </div><p className="muted center">{reviewed} reviewed this session</p></section>;
}

function SettingsView() {
  const [settings, setSettings] = useState<ExtensionSettings>(DEFAULT_SETTINGS); const [status, setStatus] = useState(""); const [pairCode, setPairCode] = useState(""); const [importFile, setImportFile] = useState<File | null>(null); const [preview, setPreview] = useState("");
  useEffect(() => { void getSettings().then(setSettings); }, []);
  async function persist() { await saveSettings(settings); setStatus("Settings saved locally."); }
  async function health() { try { const data = await api<{ status: string; provider_available: boolean }>("/api/v1/health", {}, false); setStatus(`Backend ${data.status}; translation provider ${data.provider_available ? "ready" : "needs setup"}.`); } catch (cause) { setStatus(message(cause)); } }
  async function startPairing() { try { const data = await api<{ pairing_code: string }>("/api/v1/pairing/start", { method: "POST" }, false); setPairCode(data.pairing_code); setStatus("Pairing code created by the loopback service."); } catch (cause) { setStatus(message(cause)); } }
  async function completePairing() { try { const data = await api<{ token: string }>("/api/v1/pairing/complete", { method: "POST", body: JSON.stringify({ code: pairCode }) }, false); const next = { ...settings, apiToken: data.token }; setSettings(next); await saveSettings(next); setStatus("Paired. The token is stored in extension-local storage."); } catch (cause) { setStatus(message(cause)); } }
  async function previewImport() { if (!importFile) return; try { const payload = JSON.parse(await importFile.text()); const data = await api<{ item_count: number; duplicate_count: number; will_create: number }>("/api/v1/import/preview", { method: "POST", body: JSON.stringify(payload) }); setPreview(`${data.item_count} items; ${data.duplicate_count} duplicates; ${data.will_create} to create.`); } catch (cause) { setPreview(message(cause)); } }
  async function applyImport() { if (!importFile || !confirm("Apply this validated import? Existing data will not be overwritten silently.")) return; try { const payload = JSON.parse(await importFile.text()); const data = await api<{ created: number }>("/api/v1/import/apply", { method: "POST", body: JSON.stringify(payload) }); setPreview(`Import complete: ${data.created} created.`); } catch (cause) { setPreview(message(cause)); } }
  async function deleteAll() { if (confirm("Delete ALL DeutschFlow learning data? Export first if you need a backup.")) { await api("/api/v1/data", { method: "DELETE" }); setStatus("All learning data was deleted. Extension settings remain."); } }
  return <section className="stack"><div className="eyebrow">Private by default</div><h2>Settings</h2>
    <label>Backend URL<input value={settings.backendUrl} onChange={(e) => setSettings({ ...settings, backendUrl: e.target.value.replace(/\/$/, "") })} /></label>
    <div className="button-row"><button onClick={() => void health()}>Check backend</button><button className="secondary" onClick={() => void startPairing()}>Start pairing</button></div>
    <label>Pairing code<input value={pairCode} onChange={(e) => setPairCode(e.target.value)} inputMode="numeric" /><button onClick={() => void completePairing()}>Complete pairing</button></label>
    <div className="form-grid"><label>Source language<input value={settings.sourceLanguage} onChange={(e) => setSettings({ ...settings, sourceLanguage: e.target.value })} /></label><label>Target language<input value={settings.targetLanguage} onChange={(e) => setSettings({ ...settings, targetLanguage: e.target.value })} /></label><label>Maximum selection length<input type="number" min="1" max="500" value={settings.maxSelectionLength} onChange={(e) => setSettings({ ...settings, maxSelectionLength: Number(e.target.value) })} /></label></div>
    <fieldset><legend>Default card types</legend><div className="form-grid">{["recognition","production","cloze","article","source_sentence"].map((cardType) => <label className="check" key={cardType}><input type="checkbox" checked={settings.defaultCardTypes.includes(cardType)} onChange={(event) => setSettings({ ...settings, defaultCardTypes: event.target.checked ? [...settings.defaultCardTypes, cardType] : settings.defaultCardTypes.filter((value) => value !== cardType) })} /> {cardType.replace("_", " ")}</label>)}</div></fieldset><p className="muted">Cards are created only when their required translation, article, or usable source sentence exists.</p><button className="primary" onClick={() => void persist()}>Save settings</button>
    {status && <div className="notice" role="status">{status}</div>}
    <hr/><h3>Backup & control</h3><p className="muted">Database location: managed by the local service, default <code>~/.deutschflow/deutschflow.db</code>. Secrets are excluded from export.</p>
    <div className="button-row"><button onClick={() => void downloadExport("/api/v1/export/json", "deutschflow-export.json")}>Export JSON</button><button className="secondary" onClick={() => void downloadExport("/api/v1/export/csv", "deutschflow-vocabulary.csv")}>Export CSV</button></div>
    <label>Import JSON<input type="file" accept="application/json,.json" onChange={(e) => setImportFile(e.target.files?.[0] ?? null)} /></label><div className="button-row"><button onClick={() => void previewImport()}>Preview import</button><button className="secondary" disabled={!preview} onClick={() => void applyImport()}>Apply import</button></div>{preview && <div className="notice">{preview}</div>}
    <button className="danger" onClick={() => void deleteAll()}>Delete all learning data</button>
  </section>;
}

function EmptyState({ title, body }: { title: string; body: string }) { return <div className="empty"><div className="empty-icon">ß</div><h3>{title}</h3><p>{body}</p></div>; }

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
