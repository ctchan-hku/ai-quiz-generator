import { useCallback, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import type { QuizResponse } from "../types/quiz";
import {
  appendQuizRecord,
  buildQuizExportRecord,
  clearJournal,
  downloadJournalFile,
  loadJournal,
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
        Notes for Q{index + 1}
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
  const [isPlainTextPreviewOpen, setIsPlainTextPreviewOpen] = useState(false);
  const [clipboardError, setClipboardError] = useState<string | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [journalCount, setJournalCount] = useState(
    () => loadJournal().quizzes.length,
  );

  const plainTextPreview = useMemo(() => {
    if (!isPlainTextPreviewOpen) return "";
    return buildQuizClipboardText(quiz, topic, comments);
  }, [isPlainTextPreviewOpen, quiz, topic, comments]);

  const refreshJournalCount = useCallback(() => {
    setJournalCount(loadJournal().quizzes.length);
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

  const handleTogglePlainTextPreview = useCallback(() => {
    setIsPlainTextPreviewOpen((v) => !v);
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

  const handleDownloadJson = useCallback(() => {
    setDownloadError(null);
    try {
      const record = buildQuizExportRecord({
        quiz,
        topic,
        commentsByIndex: comments,
      });
      const journal = appendQuizRecord(record);
      downloadJournalFile(journal);
      refreshJournalCount();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Download failed.";
      setDownloadError(message);
    }
  }, [quiz, topic, comments, refreshJournalCount]);

  const handleClearJournal = useCallback(() => {
    const ok = window.confirm(
      "Clear the export journal? This removes all saved quizzes from this browser only. This cannot be undone.",
    );
    if (!ok) return;
    clearJournal();
    refreshJournalCount();
  }, [refreshJournalCount]);

  return (
    <section className="card text-left" aria-labelledby="export-panel-heading">
      <h2
        id="export-panel-heading"
        className="mt-0 mb-3 font-[family-name:var(--font-heading)] text-lg font-semibold text-[var(--color-text)]"
      >
        Export / notes
      </h2>
      <p className="mt-0 mb-4 text-sm text-[var(--color-text)] opacity-80">
        Add optional notes per question, then <strong>View plain text</strong> to
        preview what you will copy, append this quiz to your JSON journal, or
        download. Journal is stored only in this browser ({journalCount}{" "}
        {journalCount === 1 ? "quiz" : "quizzes"} saved).
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
          onClick={handleTogglePlainTextPreview}
          aria-expanded={isPlainTextPreviewOpen}
          aria-controls="plain-text-preview-panel"
        >
          {isPlainTextPreviewOpen ? "Hide plain text" : "View plain text"}
        </button>
        <button
          type="button"
          className="btn-primary"
          onClick={handleDownloadJson}
        >
          Append &amp; download JSON
        </button>
        <button
          type="button"
          className="btn-secondary"
          onClick={handleClearJournal}
        >
          Clear journal
        </button>
      </div>

      {!isPlainTextPreviewOpen ? (
        <p className="mt-3 mb-0 text-sm text-[var(--color-text)] opacity-75">
          View plain text shows the exact string that Copy will put on your
          clipboard (including your notes).
        </p>
      ) : null}

      {isPlainTextPreviewOpen ? (
        <div
          id="plain-text-preview-panel"
          className="mt-4 rounded-lg border border-[rgb(30_41_59/0.15)] bg-white/40"
        >
          <div className="border-b border-[rgb(30_41_59/0.1)]">
            <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-2">
              <span className="text-sm font-semibold text-[var(--color-text)]">
                Plain text preview
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
            {plainTextPreview}
          </pre>
        </div>
      ) : null}
    </section>
  );
}
