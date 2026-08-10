export type ItemType = "word" | "phrase" | "sentence";
export type Status = "new" | "learning" | "reviewing" | "known" | "suspended";

export interface PendingSelection {
  text: string;
  context: string | null;
  contextUnavailable: boolean;
  pageTitle: string;
  pageUrl: string;
  sourceDomain: string;
  sourceLanguage: string;
  targetLanguage: string;
  capturedAt: string;
  error?: string;
}

export interface TranslationResult {
  translated_text: string;
  source_language: string;
  target_language: string;
  provider_name: string;
  provider_version?: string;
  model_or_package?: string;
  confidence_or_unknown: string;
  warnings: string[];
}

export interface Occurrence {
  source_sentence?: string;
  page_title?: string;
  page_url?: string;
  source_domain?: string;
}

export interface Flashcard {
  id: number;
  card_type: string;
  review_state?: { due_at: string };
}

export interface LearningItem {
  id: number;
  original_text: string;
  translation?: string;
  item_type: ItemType;
  status: Status;
  article?: string;
  plural?: string;
  infinitive?: string;
  verb_forms?: string;
  separable?: boolean;
  required_preposition?: string;
  required_case?: string;
  notes?: string;
  topic?: string;
  created_at: string;
  occurrences: Occurrence[];
  flashcards: Flashcard[];
}

export interface DueCard {
  id: number;
  card_type: string;
  german: string;
  translation?: string;
  article?: string;
  source_sentence?: string;
  due_at: string;
}

