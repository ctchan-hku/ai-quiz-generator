import { useCallback, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { getRequestErrorMessage, uploadDocuments } from "@/api";
import {
  formatUploadNotice,
  isPdfFile,
  mergeUploadedDocuments,
  partitionIncomingFiles,
} from "@/lib/upload/dedupe";
import { hashFileContent } from "@/lib/upload/hash";
import type { UploadedPdfDocument } from "@/lib/upload/types";

export function useDocumentUpload() {
  const queryClient = useQueryClient();
  const [documents, setDocuments] = useState<UploadedPdfDocument[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const existingHashes = useMemo(
    () => new Set(documents.map((doc) => doc.contentHash)),
    [documents],
  );

  const uploadMutation = useMutation({
    mutationFn: uploadDocuments,
  });

  const uploadFiles = useCallback(
    async (fileList: FileList | File[]) => {
      setError(null);
      const files = [...fileList];
      if (files.length === 0) {
        return;
      }

      const pdfFiles: File[] = [];
      const skippedNonPdf: File[] = [];
      for (const file of files) {
        if (isPdfFile(file)) {
          pdfFiles.push(file);
        } else {
          skippedNonPdf.push(file);
        }
      }

      const hashedPdfFiles = await Promise.all(
        pdfFiles.map(async (file) => ({
          file,
          contentHash: await hashFileContent(file),
        })),
      );

      const { toUpload, skippedDuplicates } = partitionIncomingFiles(
        existingHashes,
        hashedPdfFiles,
      );

      setNotice(
        formatUploadNotice({
          skippedDuplicates: skippedDuplicates.length,
          skippedNonPdf: skippedNonPdf.length,
        }),
      );

      if (toUpload.length === 0) {
        return;
      }

      try {
        const response = await uploadMutation.mutateAsync(
          toUpload.map((entry) => entry.file),
        );
        const contentHashes = toUpload.map((entry) => entry.contentHash);
        setDocuments((prev) =>
          mergeUploadedDocuments(prev, response.documents, contentHashes),
        );
        queryClient.invalidateQueries({ queryKey: ["knowledge-documents"] });
      } catch (err) {
        setError(getRequestErrorMessage(err));
      }
    },
    [existingHashes, uploadMutation, queryClient],
  );

  const reset = useCallback(() => {
    setDocuments([]);
    setNotice(null);
    setError(null);
  }, []);

  return {
    documents,
    uploadFiles,
    isUploading: uploadMutation.isPending,
    notice,
    error,
    reset,
  };
}
