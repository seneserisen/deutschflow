import type { PendingSelection } from "../types";

export interface ExtensionSettings {
  backendUrl: string;
  apiToken: string;
  sourceLanguage: string;
  targetLanguage: string;
  maxSelectionLength: number;
  defaultCardTypes: string[];
}

export const DEFAULT_SETTINGS: ExtensionSettings = {
  backendUrl: "http://127.0.0.1:8765",
  apiToken: "",
  sourceLanguage: "de",
  targetLanguage: "en",
  maxSelectionLength: 500,
  defaultCardTypes: ["recognition", "production", "cloze", "article"],
};

export async function getSettings(): Promise<ExtensionSettings> {
  const stored = await chrome.storage.local.get("settings");
  return { ...DEFAULT_SETTINGS, ...(stored.settings ?? {}) };
}

export async function saveSettings(settings: ExtensionSettings): Promise<void> {
  await chrome.storage.local.set({ settings });
}

export async function getPendingSelection(): Promise<PendingSelection | null> {
  const result = await chrome.storage.local.get("pendingSelection");
  return (result.pendingSelection as PendingSelection | undefined) ?? null;
}

export async function setPendingSelection(selection: PendingSelection): Promise<void> {
  await chrome.storage.local.set({ pendingSelection: selection });
}
