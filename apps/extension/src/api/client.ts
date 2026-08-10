import { getSettings } from "../storage";

export type ErrorCode =
  | "BACKEND_UNAVAILABLE" | "PAIRING_REQUIRED" | "INVALID_TOKEN" | "SELECTION_TOO_LONG"
  | "TRANSLATION_PROVIDER_UNAVAILABLE" | "LANGUAGE_PAIR_UNAVAILABLE" | "ITEM_NOT_FOUND"
  | "DUPLICATE_ITEM" | "IMPORT_SCHEMA_UNSUPPORTED" | "UNKNOWN_ERROR";

export class ApiError extends Error {
  constructor(public code: ErrorCode, message: string, public status = 0) { super(message); }
}

export function mapApiError(status: number, body: unknown): ApiError {
  const candidate = body as { error?: { code?: string; message?: string } };
  const code = (candidate?.error?.code ?? (status === 401 ? "PAIRING_REQUIRED" : "UNKNOWN_ERROR")) as ErrorCode;
  return new ApiError(code, candidate?.error?.message ?? `Local service returned HTTP ${status}.`, status);
}

export async function api<T>(path: string, init: RequestInit = {}, requireAuth = true): Promise<T> {
  const settings = await getSettings();
  const headers = new Headers(init.headers);
  if (init.body) headers.set("Content-Type", "application/json");
  if (requireAuth && settings.apiToken) headers.set("Authorization", `Bearer ${settings.apiToken}`);
  try {
    const response = await fetch(`${settings.backendUrl}${path}`, { ...init, headers });
    if (!response.ok) {
      let body: unknown = {};
      try { body = await response.json(); } catch { /* non-JSON local error */ }
      throw mapApiError(response.status, body);
    }
    if (response.status === 204) return undefined as T;
    return await response.json() as T;
  } catch (cause) {
    if (cause instanceof ApiError) throw cause;
    throw new ApiError("BACKEND_UNAVAILABLE", "The local DeutschFlow service is unavailable. Start it and retry.");
  }
}

export async function downloadExport(path: "/api/v1/export/json" | "/api/v1/export/csv", filename: string): Promise<void> {
  const settings = await getSettings();
  const response = await fetch(`${settings.backendUrl}${path}`, { headers: { Authorization: `Bearer ${settings.apiToken}` } });
  if (!response.ok) throw mapApiError(response.status, await response.json());
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url; anchor.download = filename; anchor.click(); URL.revokeObjectURL(url);
}

