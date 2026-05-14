import { useCallback, useId, useState } from "react";

import type { QuizResponse } from "../../api";
import type { QuizFormConfig } from "../../types/quiz-machine";
import { appendQuizRecord, buildQuizExportRecord } from "../../lib/export-quiz/journal";
import { buildQuizClipboardText } from "../../lib/export-quiz/clipboard";
import { useJournal } from "../Journal";
import { Button } from "@/components/ui/button";

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

  const quizSummaryPreviewText =
    !isQuizSummaryPreviewOpen
      ? ""
      : buildQuizClipboardText(quiz, {
          topic,
          commentsByIndex: comments,
          generationForm,
        });

  const handleToggleQuizSummaryPreview = useCallback(() => {
    setIsQuizSummaryPreviewOpen((v) => !v);
  }, []);

  const handleCopyFromPreview = useCallback(async () => {
    setClipboardError(null);
    setCopyDone(false);
    const text = buildQuizClipboardText(quiz, {
      topic,
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
  }, [quiz, topic, comments, generationForm]);

  const handleRecordToJournal = useCallback(() => {
    setRecordError(null);
    try {
      const record = buildQuizExportRecord({
        quiz,
        topic,
        commentsByIndex: comments,
        generationForm,
      });
      appendQuizRecord(record);
      notifyJournalRecorded();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to record.";
      setRecordError(message);
    }
  }, [quiz, topic, comments, generationForm, notifyJournalRecorded]);

  return (
    <div className="flex flex-col gap-3 border-t border-border bg-background pt-6 md:border-t-0 md:pt-0">
      <h3 className="m-0 text-sm font-semibold text-foreground">
        Current Quiz Actions
      </h3>
      {recordError ? (
        <p className="mb-0 text-sm text-destructive" role="alert">
          {recordError}
        </p>
      ) : null}
      <div className="flex flex-wrap items-center gap-2">
        <Button
          type="button"
          className="w-full justify-center"
          onClick={handleRecordToJournal}
        >
          Record to journal
        </Button>
        <Button
          type="button"
          variant="secondary"
          className="w-full justify-center"
          onClick={handleToggleQuizSummaryPreview}
          aria-expanded={isQuizSummaryPreviewOpen}
          aria-controls={previewPanelId}
        >
          {isQuizSummaryPreviewOpen
            ? "Hide summary"
            : "Preview & copy the summary"}
        </Button>
      </div>

      {isQuizSummaryPreviewOpen ? (
        <div
          id={previewPanelId}
          className="mt-2 rounded-lg border border-border bg-card/40"
        >
          <div className="border-b border-border">
            <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-2">
              <span className="text-sm font-semibold text-foreground">
                Quiz summary preview
              </span>
              <Button
                type="button"
                size="sm"
                className="shrink-0 px-2 py-1 text-xs h-7"
                onClick={handleCopyFromPreview}
              >
                {copyDone ? "Copied!" : "Copy"}
              </Button>
            </div>
            {clipboardError ? (
              <p
                className="mx-3 mb-2 mt-0 text-xs text-destructive"
                role="alert"
              >
                {clipboardError}
              </p>
            ) : null}
          </div>
          <pre className="max-h-60 overflow-auto p-3 text-xs leading-relaxed whitespace-pre-wrap text-foreground m-0 font-body">
            {quizSummaryPreviewText}
          </pre>
        </div>
      ) : null}
    </div>
  );
}
