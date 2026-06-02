import { useCallback, useState } from "react";
import type { GenerateTestResponse } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { buildTestClipboardText } from "@/lib/test-exports/clipboard";
import { appendExportTestRecord } from "@/lib/test-exports/journal/persistence";
import { notifyJournalRecorded } from "@/hooks/useJournal";

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
      appendExportTestRecord({
        exportedAt: new Date().toISOString(),
        modelUsed: test.modelUsed,
        costUsd: test.costUsd,
        questions: test.questions.map((q, i) => ({
          index: i,
          questionType: q.questionType,
          question: q.question,
          options: q.options,
          correctIndices: q.correctIndices,
          explanation: q.explanation,
          comment: (comments[i] ?? "").trim(),
        })),
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
