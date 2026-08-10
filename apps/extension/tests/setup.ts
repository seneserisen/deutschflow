import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

const store: Record<string, unknown> = {};
const event = () => ({ addListener: vi.fn(), removeListener: vi.fn() });
Object.assign(globalThis, {
  chrome: {
    storage: {
      local: {
        get: vi.fn(async (key: string) => ({ [key]: store[key] })),
        set: vi.fn(async (value: Record<string, unknown>) => { Object.assign(store, value); }),
      },
      onChanged: event(),
    },
    runtime: { onInstalled: event(), onMessage: event(), sendMessage: vi.fn(), getURL: vi.fn((path: string) => `chrome-extension://test/${path}`) },
    contextMenus: { removeAll: vi.fn((callback: () => void) => callback()), create: vi.fn(), onClicked: event() },
    sidePanel: { open: vi.fn(), setPanelBehavior: vi.fn() },
    tabs: { create: vi.fn(), query: vi.fn() }, scripting: { executeScript: vi.fn() },
  },
});

