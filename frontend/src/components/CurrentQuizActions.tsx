import { useCallback, useId, useMemo, useState } from "react";

import type { QuizResponse } from "../types/quiz";
import { appendQuizRecord, buildQuizExportRecord } from "../lib/quiz-export/journal";
import { buildQuizClipboardText } from "../lib/quiz-export/clipboard";

/** Dispatched on `window` after a quiz is appended so the journal list can refresh. */
export const JOURNAL_RECORDED_EVENT = "mastery-exec-journal-updated";

export interface CurrentQuizActionsProps {
  quiz: QuizResponse;
  topic: string;
  comments: string[];
  /** Sticky block styling for the desktop journal column; inline flow on mobile. */
  isInSidebar: boolean;
}

export function CurrentQuizActions({
  quiz,
  topic,
  comments,
  isInSidebar,
}: CurrentQuizActionsProps) {
  const previewPanelId = useId();
  const [isQuizSummaryPreviewOpen, setIsQuizSummaryPreviewOpen] =
    useState(false);
  const [clipboardError, setClipboardError] = useState<string | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [recordError, setRecordError] = useState<string | null>(null);

  const quizSummaryPreviewText = useMemo(() => {
    if (!isQuizSummaryPreviewOpen) return "";
    return buildQuizClipboardText(quiz, topic, comments);
  }, [isQuizSummaryPreviewOpen, quiz, topic, comments]);

  const handleToggleQuizSummaryPreview = useCallback(() => {
    setIsQuizSummaryPreviewOpen((v) => !v);
  }, []);

  const handleCopyFromPreview = useCallback(async () => {
    setClipboardError(null);
    setCopyDone(false);
    const text = buildQuizClipboardText(quiz, topic, comments);
    try {
      await navigator.clipboard.writeText(text);
      setCopyDone(true);
      window.setTimeout(() => setCopyDone(false), 2000);
    } catch {
      setClipboardError(
        "Could not copy — allow clipboard permission or use HTTPS.",
      );
    }
  }, [quiz, topic, comments]);

  const handleRecordToJournal = useCallback(() => {
    setRecordError(null);
    try {
      const record = buildQuizExportRecord({
        quiz,
        topic,
        commentsByIndex: comments,
      });
      appendQuizRecord(record);
      window.dispatchEvent(
        new CustomEvent(JOURNAL_RECORDED_EVENT, { bubbles: true }),
      );
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to record.";
      setRecordError(message);
    }
  }, [quiz, topic, comments]);

  const outerClassName = isInSidebar
    ? "sticky top-8 mt-6 flex flex-col gap-3 border-t border-[rgb(30_41_59/0.1)] pt-6 bg-[var(--color-background)] z-10 pb-6"
    : "mt-6 flex flex-col gap-3 border-t border-[rgb(30_41_59/0.1)] pt-6";

  return (
    <div className={outerClassName}>
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
            ? "Hide quiz summary"
            : "Preview quiz summary"}
        </button>
      </div>

      {!isQuizSummaryPreviewOpen ? (
        <p className="mt-1 mb-0 text-xs text-[var(--color-text)] opacity-75 text-center">
          Preview and copy your quiz summary, including any comments.
        </p>
      ) : null}

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
