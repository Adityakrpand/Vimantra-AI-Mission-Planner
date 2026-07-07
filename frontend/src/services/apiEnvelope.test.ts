import { describe, expect, it } from "vitest";
import { parseApiResponse } from "./apiEnvelope";

describe("parseApiResponse", () => {
  it("returns data from a successful API envelope", async () => {
    const response = new Response(
      JSON.stringify({
        success: true,
        request_id: "request-1",
        data: { ok: true },
        error: null
      }),
      { status: 200 }
    );

    await expect(parseApiResponse(response, "Request failed.")).resolves.toEqual({
      ok: true
    });
  });

  it("uses the fallback message for malformed responses", async () => {
    const response = new Response("<html>not json</html>", { status: 500 });

    await expect(parseApiResponse(response, "Request failed.")).rejects.toThrow(
      "Request failed."
    );
  });
});
