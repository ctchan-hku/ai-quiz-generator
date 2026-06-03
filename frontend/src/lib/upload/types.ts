import type { ParsedPdfDocument } from "@/api/contracts";

export interface UploadedPdfDocument extends ParsedPdfDocument {
  contentHash: string;
}

export interface HashedFile {
  file: File;
  contentHash: string;
}

export interface PartitionIncomingFilesResult {
  toUpload: HashedFile[];
  skippedDuplicates: File[];
  skippedNonPdf: File[];
}

export interface UploadNoticeCounts {
  skippedDuplicates: number;
  skippedNonPdf: number;
}
