import { useCallback, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
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

interface ExportPanelProps {
  quiz: QuizResponse;
  topic: string;
}

interface ExportCommentRowProps {
  index: number;
  previewLabel: string;
  value: string;
  onValueChange: (index: number, value: string) => void;
}

function ExportCommentRow({
  index,
  previewLabel,
  value,
  onValueChange,
}: ExportCommentRowProps) {
  const handleChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      onValueChange(index, e.target.value);
    },
    [index, onValueChange],
  );

  return (
    <div>
      <label
        className="mb-1 block text-sm font-bold text-[var(--color-text)]"
        htmlFor={`export-comment-${index}`}
      >
        Comment for Q{index + 1}
        {previewLabel ? `: ${previewLabel}` : ""}
      </label>
      <textarea
        id={`export-comment-${index}`}
        className="input min-h-[4.5rem] resize-y"
        value={value}
        onChange={handleChange}
        placeholder="Optional comment…"
        rows={3}
      />
    </div>
  );
}

export function ExportPanel({ quiz, topic }: ExportPanelProps) {
  const [comments, setComments] = useState<string[]>(() =>
    quiz.questions.map(() => ""),
  );
  const [isQuizSummaryPreviewOpen, setIsQuizSummaryPreviewOpen] = useState(false);
  const [clipboardError, setClipboardError] = useState<string | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [journal, setJournal] = useState(() => loadJournal());

  const [expandedJournalIndex, setExpandedJournalIndex] = useState<number | null>(null);

  const quizSummaryPreviewText = useMemo(() => {
    if (!isQuizSummaryPreviewOpen) return "";
    return buildQuizClipboardText(quiz, topic, comments);
  }, [isQuizSummaryPreviewOpen, quiz, topic, comments]);

  const refreshJournal = useCallback(() => {
    setJournal(loadJournal());
  }, []);

  const handleCommentChange = useCallback((index: number, value: string) => {
    setComments((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  }, []);

  const getPreviewLabel = useCallback(
    (q: QuizResponse["questions"][number]) => {
      const t = q.question;
      return t.length > 80 ? `${t.slice(0, 80)}…` : t;
    },
    [],
  );

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
    <section className="card text-left" aria-labelledby="export-panel-heading">
      <h2
        id="export-panel-heading"
        className="mt-0 mb-3 font-[family-name:var(--font-heading)] text-lg font-semibold text-[var(--color-text)]"
      >
        Export / comments
      </h2>
      <p className="mt-0 mb-4 text-sm text-[var(--color-text)] opacity-80">
        Add optional comments to evaluate each question—such as what works well or what needs improvement. These comments are only saved if you record the quiz to your journal or copy it to your clipboard.
      </p>

      <div className="mb-4 flex flex-col gap-4">
        {quiz.questions.map((q, i) => (
          <ExportCommentRow
            key={i}
            index={i}
            previewLabel={getPreviewLabel(q)}
            value={comments[i] ?? ""}
            onValueChange={handleCommentChange}
          />
        ))}
      </div>

      {downloadError ? (
        <p
          className="mb-3 text-sm text-[var(--color-destructive)]"
          role="alert"
        >
          {downloadError}
        </p>
      ) : null}

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="btn-secondary"
          onClick={handleToggleQuizSummaryPreview}
          aria-expanded={isQuizSummaryPreviewOpen}
          aria-controls="quiz-summary-preview-panel"
        >
          {isQuizSummaryPreviewOpen ? "Hide quiz summary" : "Preview quiz summary"}
        </button>
        <button
          type="button"
          className="btn-primary"
          onClick={handleRecordToJournal}
        >
          Record to journal
        </button>
      </div>

      {!isQuizSummaryPreviewOpen ? (
        <p className="mt-3 mb-0 text-sm text-[var(--color-text)] opacity-75">
          Preview and copy your quiz summary, including any comments.
        </p>
      ) : null}

      {isQuizSummaryPreviewOpen ? (
        <div
          id="quiz-summary-preview-panel"
          className="mt-4 rounded-lg border border-[rgb(30_41_59/0.15)] bg-white/40"
        >
          <div className="border-b border-[rgb(30_41_59/0.1)]">
            <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-2">
              <span className="text-sm font-semibold text-[var(--color-text)]">
                Quiz summary preview
              </span>
              <button
                type="button"
                className="btn-primary shrink-0"
                onClick={handleCopyFromPreview}
              >
                Copy to clipboard
              </button>
            </div>
            {clipboardError ? (
              <p
                className="mx-3 mb-2 mt-0 text-sm text-[var(--color-destructive)]"
                role="alert"
              >
                {clipboardError}
              </p>
            ) : null}
            {copyDone ? (
              <p
                className="mx-3 mb-2 mt-0 text-sm text-[var(--color-text)]"
                role="status"
              >
                Copied!
              </p>
            ) : null}
          </div>
          <pre className="max-h-72 overflow-auto p-3 text-sm leading-relaxed whitespace-pre-wrap text-[var(--color-text)] m-0 font-[family-name:var(--font-body)]">
            {quizSummaryPreviewText}
          </pre>
        </div>
      ) : null}

      <div className="mt-8 border-t border-[rgb(30_41_59/0.1)] pt-6">
        <h3 className="mb-3 font-[family-name:var(--font-heading)] text-base font-semibold text-[var(--color-text)]">
          Export journal
        </h3>
        <p className="mb-4 text-sm text-[var(--color-text)] opacity-80">
          The journal stores your recorded quizzes in this browser. You can
          export the entire journal as a single JSON file.
        </p>

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
                <div className="flex items-center justify-between gap-3 px-3 py-2">
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-[var(--color-text)]">
                      {q.topic || "Untitled quiz"}
                    </span>
                    <span className="text-xs text-[var(--color-text)] opacity-70">
                      {q.questions.length} question
                      {q.questions.length === 1 ? "" : "s"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
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
                        <div key={qIdx} className="text-xs text-[var(--color-text)]">
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

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            className="btn-primary"
            onClick={handleExportJournal}
            disabled={journal.quizzes.length === 0}
          >
            Export journal as JSON
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={handleClearJournal}
            disabled={journal.quizzes.length === 0}
          >
            Clear journal
          </button>
        </div>
      </div>
    </section>
  );
}
