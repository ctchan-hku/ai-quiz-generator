import { describe, expect, it, vi, beforeEach } from "vitest";
import type { GenerateTestResponse } from "@/api/contracts";
import { testFormFieldDefaults } from "@/config/test-form";
import { recordTestToJournal } from "./record-test";

vi.mock("./journal", () => ({
  appendTestRecord: vi.fn(),
  buildTestExportRecord: vi.fn(() => ({ exportedAt: "2026-01-01" })),
}));

import { appendTestRecord, buildTestExportRecord } from "./journal";

const test: GenerateTestResponse = {
  modelUsed: "m1",
  costUsd: 0.1,
  questions: [],
};

describe("recordTestToJournal", () => {
  beforeEach(() => {
    vi.mocked(buildTestExportRecord).mockClear();
    vi.mocked(appendTestRecord).mockClear();
  });

  it("builds and appends a journal record", () => {
    recordTestToJournal({
      test,
      commentsByIndex: ["note"],
      generationForm: testFormFieldDefaults,
    });
    expect(buildTestExportRecord).toHaveBeenCalledOnce();
    expect(appendTestRecord).toHaveBeenCalledOnce();
  });
});
