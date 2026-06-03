import type { ParsedPdfDocument } from "@/api/contracts";
import type {
  HashedFile,
  PartitionIncomingFilesResult,
  UploadedPdfDocument,
  UploadNoticeCounts,
} from "./types";

export function isPdfFile(file: File): boolean {
  if (file.type === "application/pdf") {
    return true;
  }
  return file.name.toLowerCase().endsWith(".pdf");
}

export function partitionIncomingFiles(
  existingHashes: Set<string>,
  hashedPdfFiles: HashedFile[],
): Pick<PartitionIncomingFilesResult, "toUpload" | "skippedDuplicates"> {
  const toUpload: HashedFile[] = [];
  const skippedDuplicates: File[] = [];

  for (const entry of hashedPdfFiles) {
    if (existingHashes.has(entry.contentHash)) {
      skippedDuplicates.push(entry.file);
      continue;
    }
    toUpload.push(entry);
  }

  return { toUpload, skippedDuplicates };
}

export function mergeUploadedDocuments(
  existing: UploadedPdfDocument[],
  uploaded: ParsedPdfDocument[],
  contentHashes: string[],
): UploadedPdfDocument[] {
  const appended = uploaded.map((doc, index) => ({
    ...doc,
    contentHash: contentHashes[index],
  }));
  return [...existing, ...appended];
}

export function formatUploadNotice(counts: UploadNoticeCounts): string | null {
  const parts: string[] = [];
  if (counts.skippedDuplicates > 0) {
    const n = counts.skippedDuplicates;
    parts.push(`${n} file${n === 1 ? "" : "s"} skipped — duplicate content`);
  }
  if (counts.skippedNonPdf > 0) {
    const n = counts.skippedNonPdf;
    parts.push(`${n} file${n === 1 ? "" : "s"} skipped — PDF only`);
  }
  if (parts.length === 0) {
    return null;
  }
  return `${parts.join(". ")}.`;
}
