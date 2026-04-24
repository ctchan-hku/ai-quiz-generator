import { useCallback, useMemo, useState } from "react";
import type { QuizResponse } from "../types/quiz";
import {
  appendQuizRecord,
  buildQuizExportRecord,
  clearJournal,
  downloadJournalFile,
  loadJournal,
  removeQuizRecord,
} from "../lib/quiz-export/journal";
import { buildQuizClipboardText } from "../lib/quiz-export/clipboard";

interface JournalSidebarProps {
  quiz: QuizResponse | null;
  topic: string;
  comments: string[];
  isOpen: boolean;
  onClose: () => void;
}

export function JournalSidebar({
  quiz,
  topic,
  comments,
  isOpen,
  onClose,
}: JournalSidebarProps) {
  const [isQuizSummaryPreviewOpen, setIsQuizSummaryPreviewOpen] =
    useState(false);
  const [clipboardError, setClipboardError] = useState<string | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [journal, setJournal] = useState(() => loadJournal());
  const [expandedJournalIndex, setExpandedJournalIndex] = useState<
    number | null
  >(null);

  const quizSummaryPreviewText = useMemo(() => {
    if (!isQuizSummaryPreviewOpen || !quiz) return "";
    return buildQuizClipboardText(quiz, topic, comments);
  }, [isQuizSummaryPreviewOpen, quiz, topic, comments]);

  const refreshJournal = useCallback(() => {
    setJournal(loadJournal());
  }, []);

  const handleToggleQuizSummaryPreview = useCallback(() => {
    setIsQuizSummaryPreviewOpen((v) => !v);
  }, []);

  const handleCopyFromPreview = useCallback(async () => {
    if (!quiz) return;
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
    if (!quiz) return;
    try {
      const record = buildQuizExportRecord({
        quiz,
        topic,
        commentsByIndex: comments,
      });
      appendQuizRecord(record);
      refreshJournal();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to record.";
      setDownloadError(message);
    }
  }, [quiz, topic, comments, refreshJournal]);

  const handleExportJournal = useCallback(() => {
    setDownloadError(null);
    try {
      downloadJournalFile(journal);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Download failed.";
      setDownloadError(message);
    }
  }, [journal]);

  const handleClearJournal = useCallback(() => {
    const ok = window.confirm(
      "Clear the export journal? This removes all saved quizzes from this browser only. This cannot be undone.",
    );
    if (!ok) return;
    clearJournal();
    refreshJournal();
  }, [refreshJournal]);

  const handleRemoveFromJournal = useCallback(
    (index: number) => {
      removeQuizRecord(index);
      refreshJournal();
      setExpandedJournalIndex((prev) => (prev === index ? null : prev));
    },
    [refreshJournal],
  );

  const handleToggleJournalItem = useCallback((index: number) => {
    setExpandedJournalIndex((prev) => (prev === index ? null : index));
  }, []);

  return (
    <>
      {isOpen ? (
        <div
          className="fixed inset-0 z-40 bg-[rgb(0_0_0/0.2)] backdrop-blur-sm md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 right-0 z-50 flex w-full max-w-full shrink-0 flex-col gap-6 overflow-y-auto bg-[var(--color-background)] p-6 shadow-2xl transition-transform duration-300 ease-in-out md:static md:z-auto md:w-96 md:translate-x-0 md:bg-transparent md:p-0 md:shadow-none md:overflow-visible lg:w-[28rem] ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="mb-2 flex items-center justify-between md:hidden">
          <h2 className="m-0 font-[family-name:var(--font-heading)] text-xl font-semibold text-[var(--color-text)]">
            Journal Menu
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary px-3 py-1.5 text-sm"
          >
            Close
          </button>
        </div>

        <section className="text-left" aria-labelledby="journal-heading">
          <h2
            id="journal-heading"
            className="mb-3 hidden font-[family-name:var(--font-heading)] text-lg font-semibold text-[var(--color-text)] md:block"
          >
            Journal Menu
          </h2>
          <p className="mt-0 mb-4 text-sm text-[var(--color-text)] opacity-80">
            The journal stores your recorded quizzes in this browser. You can
            export the entire journal as a single JSON file.
          </p>

          {downloadError ? (
            <p
              className="mb-3 text-sm text-[var(--color-destructive)]"
              role="alert"
            >
              {downloadError}
            </p>
          ) : null}

          <h3 className="mb-3 font-[family-name:var(--font-heading)] text-base font-semibold text-[var(--color-text)]">
            Recorded Quizzes
          </h3>

          {journal.quizzes.length === 0 ? (
            <p className="text-sm italic text-[var(--color-text)] opacity-60">
              No quizzes recorded yet.
            </p>
          ) : (
            <div className="mb-4 flex flex-col gap-2">
              {journal.quizzes.map((q, i) => (
                <div
                  key={i}
                  className="flex flex-col rounded border border-[rgb(30_41_59/0.1)] bg-white/50"
                >
                  <div className="flex flex-col justify-between gap-2 px-3 py-2 sm:flex-row sm:items-center">
                    <div className="flex flex-col min-w-0 flex-1">
                      <span className="truncate text-sm font-medium text-[var(--color-text)]">
                        {q.topic || "Untitled quiz"}
                      </span>
                      <span className="text-xs text-[var(--color-text)] opacity-70">
                        {q.questions.length} question
                        {q.questions.length === 1 ? "" : "s"}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0 pt-2 sm:pt-0">
                      <button
                        type="button"
                        className="btn-secondary shrink-0 px-2 py-1 text-xs"
                        onClick={() => handleToggleJournalItem(i)}
                        aria-expanded={expandedJournalIndex === i}
                      >
                        {expandedJournalIndex === i ? "Collapse" : "Expand"}
                      </button>
                      <button
                        type="button"
                        className="btn-secondary shrink-0 px-2 py-1 text-xs text-[var(--color-destructive)] hover:bg-[var(--color-destructive)] hover:text-white"
                        onClick={() => handleRemoveFromJournal(i)}
                        aria-label={`Remove quiz ${i + 1}`}
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  {expandedJournalIndex === i ? (
                    <div className="border-t border-[rgb(30_41_59/0.1)] px-3 py-3">
                      <p className="mb-2 mt-0 text-xs text-[var(--color-text)] opacity-70">
                        Model: {q.model_used}
                      </p>
                      <div className="flex flex-col gap-3">
                        {q.questions.map((question, qIdx) => (
                          <div
                            key={qIdx}
                            className="text-xs text-[var(--color-text)]"
                          >
                            <p className="mt-0 mb-1 font-medium">
                              {qIdx + 1}. {question.question}
                            </p>
                            {question.comment ? (
                              <p className="mt-0 mb-0 italic text-[var(--color-primary)]">
                                Comment: {question.comment}
                              </p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              className="btn-primary w-full justify-center"
              onClick={handleExportJournal}
              disabled={journal.quizzes.length === 0}
            >
              Export journal as JSON
            </button>
            <button
              type="button"
              className="btn-secondary w-full justify-center"
              onClick={handleClearJournal}
              disabled={journal.quizzes.length === 0}
            >
              Clear journal
            </button>
          </div>

          {quiz ? (
            <div className="sticky top-8 mt-6 flex flex-col gap-3 border-t border-[rgb(30_41_59/0.1)] pt-6 bg-[var(--color-background)] z-10 pb-6">
              <h3 className="m-0 text-sm font-semibold text-[var(--color-text)]">
                Current Quiz Actions
              </h3>
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
                  aria-controls="quiz-summary-preview-panel"
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
                  id="quiz-summary-preview-panel"
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
          ) : null}
        </section>
      </aside>
    </>
  );
}
