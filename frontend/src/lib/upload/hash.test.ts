import { describe, expect, it } from "vitest";
import { hashFileContent } from "./hash";

describe("hashFileContent", () => {
  it("returns stable SHA-256 hex for the same bytes", async () => {
    const file = new File(["hello-pdf"], "test.pdf", {
      type: "application/pdf",
    });
    const a = await hashFileContent(file);
    const b = await hashFileContent(file);
    expect(a).toBe(b);
    expect(a).toMatch(/^[0-9a-f]{64}$/);
  });

  it("returns different hashes for different bytes", async () => {
    const left = new File(["left"], "left.pdf", { type: "application/pdf" });
    const right = new File(["right"], "right.pdf", {
      type: "application/pdf",
    });
    expect(await hashFileContent(left)).not.toBe(await hashFileContent(right));
  });
});
