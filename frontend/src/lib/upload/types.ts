import type { KnowledgeDocumentSummary } from "@/api/contracts";

export interface UploadedPdfDocument extends KnowledgeDocumentSummary {
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
