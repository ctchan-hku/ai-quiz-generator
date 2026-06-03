import { useCallback, useRef, useState, type DragEvent } from "react";
import { ChevronRight, Upload } from "lucide-react";

import type { ParsedPdfDocument } from "@/api/contracts";
import { TestFormSectionTitle } from "./TestFormSectionTitle";

type UploadedDocumentListItem = ParsedPdfDocument & { contentHash: string };

interface DocumentUploadSectionProps {
  documents: UploadedDocumentListItem[];
  onUploadFiles: (files: FileList | File[]) => void;
  isUploading: boolean;
  notice: string | null;
  error: string | null;
  disabled?: boolean;
}

function chunkCountLabel(n: number): string {
  return n === 1 ? "1 chunk" : `${n} chunks`;
}

export function DocumentUploadSection({
  documents,
  onUploadFiles,
  isUploading,
  notice,
  error,
  disabled = false,
}: DocumentUploadSectionProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const isDisabled = disabled || isUploading;

  const openFilePicker = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const handleInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const { files } = event.target;
      if (files && files.length > 0) {
        onUploadFiles(files);
      }
      event.target.value = "";
    },
    [onUploadFiles],
  );

  const handleDragOver = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragging(false);
      if (isDisabled) {
        return;
      }
      if (event.dataTransfer.files.length > 0) {
        onUploadFiles(event.dataTransfer.files);
      }
    },
    [isDisabled, onUploadFiles],
  );

  return (
    <details
      className="mb-4 text-left"
      open={isOpen}
      onToggle={(event) => setIsOpen(event.currentTarget.open)}
    >
      <TestFormSectionTitle
        as="summary"
        className="flex cursor-pointer list-none items-center gap-2 [&::-webkit-details-marker]:hidden"
      >
        <ChevronRight
          className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200${isOpen ? " rotate-90" : ""}`}
          aria-hidden
        />
        Document upload
        <span className="sr-only">
          {isOpen ? "Collapse section" : "Expand section"}
        </span>
      </TestFormSectionTitle>

      <div className="mt-3 space-y-3">
        <div
          role="button"
          tabIndex={isDisabled ? -1 : 0}
          aria-disabled={isDisabled}
          aria-busy={isUploading}
          className={[
            "flex min-h-28 cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed px-4 py-6 text-center transition-colors",
            isDragging
              ? "border-primary bg-primary/5"
              : "border-border bg-muted/20 hover:bg-muted/30",
            isDisabled ? "cursor-not-allowed opacity-60" : "",
          ]
            .filter(Boolean)
            .join(" ")}
          onClick={() => {
            if (!isDisabled) {
              openFilePicker();
            }
          }}
          onKeyDown={(event) => {
            if (isDisabled) {
              return;
            }
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              openFilePicker();
            }
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="h-5 w-5 text-muted-foreground" aria-hidden />
          <p className="m-0 text-sm text-foreground">
            {isUploading ? "Uploading…" : "Drag PDFs here or browse"}
          </p>
          <p className="m-0 text-xs text-muted-foreground">PDF files only</p>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          multiple
          className="sr-only"
          disabled={isDisabled}
          onChange={handleInputChange}
        />

        {notice ? (
          <p className="m-0 text-sm text-muted-foreground" role="status">
            {notice}
          </p>
        ) : null}

        {error ? (
          <p className="m-0 text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}

        {documents.length > 0 ? (
          <ul className="m-0 list-none space-y-2 p-0">
            {documents.map((doc) => (
              <li
                key={doc.contentHash}
                className="flex items-center justify-between gap-3 rounded-md border border-border bg-card/40 px-3 py-2 text-sm"
              >
                <span className="min-w-0 truncate font-medium text-foreground">
                  {doc.filename}
                </span>
                <span className="shrink-0 text-muted-foreground">
                  {chunkCountLabel(doc.chunkCount)}
                </span>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </details>
  );
}
