import { api, mapApiError } from "../src/api/client";

describe("API errors", () => {
  test("maps stable server error codes", () => {
    expect(mapApiError(409, { error: { code: "DUPLICATE_ITEM", message: "Already saved" } })).toMatchObject({ code: "DUPLICATE_ITEM", message: "Already saved" });
    expect(mapApiError(503, { error: { code: "TRANSLATION_PROVIDER_UNAVAILABLE", message: "Install Argos" } })).toMatchObject({ code: "TRANSLATION_PROVIDER_UNAVAILABLE" });
  });

  test("maps a network failure to backend unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("fetch failed")));
    await expect(api("/api/v1/items")).rejects.toMatchObject({ code: "BACKEND_UNAVAILABLE" });
  });

  test("preserves a provider unavailable server response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ error: { code: "TRANSLATION_PROVIDER_UNAVAILABLE", message: "Set up Argos" } }), { status: 503, headers: { "Content-Type": "application/json" } })));
    await expect(api("/api/v1/translate")).rejects.toEqual(expect.objectContaining({ code: "TRANSLATION_PROVIDER_UNAVAILABLE" }));
  });
});
