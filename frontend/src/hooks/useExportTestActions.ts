import { useCallback, useState } from "react";
import type { GenerateTestResponse } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { buildTestClipboardText } from "@/lib/export-test/clipboard";
import { notifyJournalRecorded } from "@/hooks/useJournal";
import { recordExportTestToJournal } from "@/lib/export-test/use-cases";

interface UseExportTestActionsParams {
  test: GenerateTestResponse;
  comments: string[];
  formConfig: TestFormConfig;
}

export function useExportTestActions({
  test,
  comments,
  formConfig,
}: UseExportTestActionsParams) {
  const [clipboardError, setClipboardError] = useState<string | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [recordError, setRecordError] = useState<string | null>(null);

  const copySummary = useCallback(async () => {
    setClipboardError(null);
    setCopyDone(false);
    const text = buildTestClipboardText(test, {
      commentsByIndex: comments,
      formConfig,
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
  }, [test, comments, formConfig]);

  const recordToJournal = useCallback(() => {
    setRecordError(null);
    try {
      recordExportTestToJournal({
        test,
        commentsByIndex: comments,
        formConfig,
      });
      notifyJournalRecorded();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to record.";
      setRecordError(message);
    }
  }, [test, comments, formConfig]);

  const previewText = buildTestClipboardText(test, {
    commentsByIndex: comments,
    formConfig,
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
