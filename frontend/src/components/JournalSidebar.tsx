import { useCallback, useEffect, useState } from "react";
import { JOURNAL_RECORDED_EVENT } from "./CurrentQuizActions";
import { formatEstimatedCostUsd } from "../lib/format-cost-usd";
import {
  clearJournal,
  downloadJournalFile,
  loadJournal,
  removeQuizRecord,
} from "../lib/quiz-export/journal";

interface JournalSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function JournalSidebar({ isOpen, onClose }: JournalSidebarProps) {
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [journal, setJournal] = useState(() => loadJournal());
  const [expandedJournalIndex, setExpandedJournalIndex] = useState<
    number | null
  >(null);

  const refreshJournal = useCallback(() => {
    setJournal(loadJournal());
  }, []);

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

  useEffect(() => {
    const onJournalUpdated = () => {
      refreshJournal();
    };
    window.addEventListener(JOURNAL_RECORDED_EVENT, onJournalUpdated);
    return () => {
      window.removeEventListener(JOURNAL_RECORDED_EVENT, onJournalUpdated);
    };
  }, [refreshJournal]);

  return (
    <>
      {isOpen ? (
        <div
          className="fixed inset-0 z-40 bg-[rgb(0_0_0/0.2)] backdrop-blur-sm"
          onClick={onClose}
          aria-hidden="true"
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 right-0 z-50 flex w-full max-w-md shrink-0 flex-col gap-6 overflow-y-auto bg-[var(--color-background)] p-6 shadow-2xl transition-transform duration-300 ease-in-out lg:max-w-lg ${
          isOpen
            ? "translate-x-0"
            : "translate-x-full pointer-events-none"
        }`}
        aria-hidden={!isOpen}
      >
        <div className="mb-2 flex items-center justify-between gap-4">
          <h2
            id="journal-heading"
            className="m-0 font-[family-name:var(--font-heading)] text-xl font-semibold text-[var(--color-text)]"
          >
            Journal Menu
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary shrink-0 px-3 py-1.5 text-sm"
          >
            Close
          </button>
        </div>

        <section className="text-left" aria-labelledby="journal-heading">
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
                        Model: {q.model_used} ·{" "}
                        {formatEstimatedCostUsd(q.cost_usd)}
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

        </section>
      </aside>
    </>
  );
}
