import { useCallback, useState } from "react";
import type { GenerateTestResponse } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { buildTestClipboardText } from "@/lib/export-test/clipboard";
import { recordTestToJournal } from "@/lib/export-test/record-test";

interface UseTestExportActionsParams {
  test: GenerateTestResponse;
  comments: string[];
  generationForm: TestFormConfig;
  onRecorded?: () => void;
}

export function useTestExportActions({
  test,
  comments,
  generationForm,
  onRecorded,
}: UseTestExportActionsParams) {
  const [clipboardError, setClipboardError] = useState<string | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [recordError, setRecordError] = useState<string | null>(null);

  const copySummary = useCallback(async () => {
    setClipboardError(null);
    setCopyDone(false);
    const text = buildTestClipboardText(test, {
      commentsByIndex: comments,
      generationForm,
    });
    try {
      await navigator.clipboard.writeText(text);
      setCopyDone(true);
      window.setTimeout(() => setCopyDone(false), 2000);
    } catch {
      setClipboardError(
        "Could not copy — allow clipboard permission or use HTTPS.",
      );
    }
  }, [test, comments, generationForm]);

  const recordToJournal = useCallback(() => {
    setRecordError(null);
    try {
      recordTestToJournal({
        test,
        commentsByIndex: comments,
        generationForm,
      });
      onRecorded?.();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to record.";
      setRecordError(message);
    }
  }, [test, comments, generationForm, onRecorded]);

  const previewText = buildTestClipboardText(test, {
    commentsByIndex: comments,
    generationForm,
  });

  return {
    copySummary,
    recordToJournal,
    previewText,
    clipboardError,
    copyDone,
    recordError,
  };
}
