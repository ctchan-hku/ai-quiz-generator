import type { QuizResponse } from "../../types/quiz";
import { optionLabel } from "../option";

function indicesToAnswerLetters(indices: number[]): string {
  return indices
    .map((i) => optionLabel(i))
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
    const comment = commentsByIndex?.[qIdx]?.trim();

    lines.push(`${n}. ${q.question}`);
    q.options.forEach((opt, optIdx) => {
      const label = optionLabel(optIdx);
      lines.push(`${label}. ${opt}`);
    });
    lines.push(`Answer: ${indicesToAnswerLetters(q.correct_indices)}`);
    if (q.explanation.trim() !== "") {
      lines.push(`Explanation: ${q.explanation}`);
    }
    if (comment) {
      lines.push(`Comment: ${comment}`);
    }
    lines.push("");
  });

  return lines.join("\n").trimEnd();
}
