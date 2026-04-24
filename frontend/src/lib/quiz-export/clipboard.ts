import type { QuizResponse } from "../../types/quiz";

const LABELS = ["A", "B", "C", "D"] as const;

function indicesToAnswerLetters(indices: number[]): string {
  return indices
    .map((i) => LABELS[i] ?? String(i + 1))
    .filter(Boolean)
    .join(", ");
}

/** Plain-text quiz for `navigator.clipboard.writeText` (separate from the downloadable journal file). */
export function buildQuizClipboardText(
  quiz: QuizResponse,
  topic?: string,
  commentsByIndex?: string[],
): string {
  const lines: string[] = [];

  if (topic != null && topic.trim() !== "") {
    lines.push(`Topic: ${topic.trim()}`);
  }
  lines.push(`Model: ${quiz.model_used} · Source: ${quiz.source}`);
  lines.push("");

  quiz.questions.forEach((q, qIdx) => {
    const n = qIdx + 1;
    const note = commentsByIndex?.[qIdx]?.trim();

    lines.push(`${n}. ${q.question}`);
    q.options.forEach((opt, optIdx) => {
      const label = LABELS[optIdx] ?? String(optIdx + 1);
      lines.push(`${label}. ${opt}`);
    });
    lines.push(`Answer: ${indicesToAnswerLetters(q.correct_indices)}`);
    if (q.explanation.trim() !== "") {
      lines.push(`Explanation: ${q.explanation}`);
    }
    if (note) {
      lines.push(`Notes: ${note}`);
    }
    lines.push("");
  });

  return lines.join("\n").trimEnd();
}
