import { useCallback, useId, useMemo, useState } from "react";

import type { QuizResponse } from "../../types/quiz";
import type { QuizFormConfig } from "../../types/quiz-machine";
import {
  appendQuizRecord,
  buildQuizExportRecord,
  toQuizGenerationRequestSnapshot,
} from "../../lib/export-quiz/journal";
import { buildQuizClipboardText } from "../../lib/export-quiz/clipboard";
import { useJournal } from "../Journal";

export interface CurrentQuizActionsProps {
  quiz: QuizResponse;
  topic: string;
  comments: string[];
  generationForm: QuizFormConfig;
}

export function CurrentQuizActions({
  quiz,
  topic,
  comments,
  generationForm,
}: CurrentQuizActionsProps) {
  const { notifyJournalRecorded } = useJournal();
  const previewPanelId = useId();
  const [isQuizSummaryPreviewOpen, setIsQuizSummaryPreviewOpen] =
    useState(false);
  const [clipboardError, setClipboardError] = useState<string | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [recordError, setRecordError] = useState<string | null>(null);

  const generationSnapshot = useMemo(
    () => toQuizGenerationRequestSnapshot(generationForm),
    [generationForm],
  );

  const quizSummaryPreviewText = useMemo(() => {
    if (!isQuizSummaryPreviewOpen) return "";
    return buildQuizClipboardText(quiz, {
      topic,
      commentsByIndex: comments,
      generationSnapshot,
    });
  }, [
    isQuizSummaryPreviewOpen,
    quiz,
    topic,
    comments,
    generationSnapshot,
  ]);

  const handleToggleQuizSummaryPreview = useCallback(() => {
    setIsQuizSummaryPreviewOpen((v) => !v);
  }, []);

  const handleCopyFromPreview = useCallback(async () => {
    setClipboardError(null);
    setCopyDone(false);
    const text = buildQuizClipboardText(quiz, {
      topic,
      commentsByIndex: comments,
      generationSnapshot,
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
  }, [quiz, topic, comments, generationSnapshot]);

  const handleRecordToJournal = useCallback(() => {
    setRecordError(null);
    try {
      const record = buildQuizExportRecord({
        quiz,
        topic,
        commentsByIndex: comments,
        generationRequestSnapshot: generationSnapshot,
      });
      appendQuizRecord(record);
      notifyJournalRecorded();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to record.";
      setRecordError(message);
    }
  }, [
    quiz,
    topic,
    comments,
    generationSnapshot,
    notifyJournalRecorded,
  ]);

  return (
    <div className="flex flex-col gap-3 border-t border-[rgb(30_41_59/0.1)] bg-[var(--color-background)] pt-6 md:border-t-0 md:pt-0">
      <h3 className="m-0 text-sm font-semibold text-[var(--color-text)]">
        Current Quiz Actions
      </h3>
      {recordError ? (
        <p
          className="mb-0 text-sm text-[var(--color-destructive)]"
          role="alert"
        >
          {recordError}
        </p>
      ) : null}
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          className="btn-primary w-full justify-center"
          onClick={handleRecordToJournal}
        >
          Record to journal
        </button>
        <button
          type="button"
          className="btn-secondary w-full justify-center"
          onClick={handleToggleQuizSummaryPreview}
          aria-expanded={isQuizSummaryPreviewOpen}
          aria-controls={previewPanelId}
        >
          {isQuizSummaryPreviewOpen
            ? "Hide summary"
            : "Preview & copy the summary"}
        </button>
      </div>

      {isQuizSummaryPreviewOpen ? (
        <div
          id={previewPanelId}
          className="mt-2 rounded-lg border border-[rgb(30_41_59/0.15)] bg-white/40"
        >
          <div className="border-b border-[rgb(30_41_59/0.1)]">
            <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-2">
              <span className="text-sm font-semibold text-[var(--color-text)]">
                Quiz summary preview
              </span>
              <button
                type="button"
                className="btn-primary shrink-0 px-2 py-1 text-xs"
                onClick={handleCopyFromPreview}
              >
                {copyDone ? "Copied!" : "Copy"}
              </button>
            </div>
            {clipboardError ? (
              <p
                className="mx-3 mb-2 mt-0 text-xs text-[var(--color-destructive)]"
                role="alert"
              >
                {clipboardError}
              </p>
            ) : null}
          </div>
          <pre className="max-h-60 overflow-auto p-3 text-xs leading-relaxed whitespace-pre-wrap text-[var(--color-text)] m-0 font-[family-name:var(--font-body)]">
            {quizSummaryPreviewText}
          </pre>
        </div>
      ) : null}
    </div>
  );
}
