import { describe, expect, it } from "vitest";
import type { ParsedPdfDocument } from "@/api/contracts";
import {
  formatUploadNotice,
  isPdfFile,
  mergeUploadedDocuments,
  partitionIncomingFiles,
} from "./dedupe";

function makeFile(name: string, type = "application/pdf"): File {
  return new File(["content"], name, { type });
}

describe("isPdfFile", () => {
  it("accepts application/pdf MIME", () => {
    expect(isPdfFile(makeFile("a.pdf", "application/pdf"))).toBe(true);
  });

  it("accepts .pdf extension when MIME is empty", () => {
    expect(isPdfFile(makeFile("a.pdf", ""))).toBe(true);
  });

  it("rejects non-pdf", () => {
    expect(isPdfFile(makeFile("a.txt", "text/plain"))).toBe(false);
  });
});

describe("partitionIncomingFiles", () => {
  it("sends new hashes to upload and skips duplicates", () => {
    const existing = new Set(["hash-a"]);
    const incoming = [
      { file: makeFile("a.pdf"), contentHash: "hash-a" },
      { file: makeFile("b.pdf"), contentHash: "hash-b" },
    ];
    const result = partitionIncomingFiles(existing, incoming);
    expect(result.toUpload).toHaveLength(1);
    expect(result.toUpload[0].contentHash).toBe("hash-b");
    expect(result.skippedDuplicates).toHaveLength(1);
    expect(result.skippedDuplicates[0].name).toBe("a.pdf");
  });
});

describe("mergeUploadedDocuments", () => {
  it("appends uploaded docs with content hashes in order", () => {
    const existing = [
      { contentHash: "h1", filename: "one.pdf", chunkCount: 0 },
    ];
    const uploaded: ParsedPdfDocument[] = [
      { filename: "two.pdf", chunkCount: 3 },
    ];
    const merged = mergeUploadedDocuments(existing, uploaded, ["h2"]);
    expect(merged).toHaveLength(2);
    expect(merged[1].filename).toBe("two.pdf");
    expect(merged[1].contentHash).toBe("h2");
    expect(merged[1].chunkCount).toBe(3);
  });
});

describe("formatUploadNotice", () => {
  it("returns null when nothing skipped", () => {
    expect(
      formatUploadNotice({ skippedDuplicates: 0, skippedNonPdf: 0 }),
    ).toBeNull();
  });

  it("combines duplicate and non-pdf counts", () => {
    expect(formatUploadNotice({ skippedDuplicates: 2, skippedNonPdf: 1 })).toBe(
      "2 files skipped — duplicate content. 1 file skipped — PDF only.",
    );
  });
});
