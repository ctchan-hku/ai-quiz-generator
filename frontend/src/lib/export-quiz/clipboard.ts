import type { QuizGenerationRequestSnapshot } from "../../types/export-journal";
import type { QuizResponse } from "../../api";
import { formatEstimatedCostUsd } from "../format-usd";
import { optionLabel } from "../option";

function indicesToAnswerLetters(indices: number[]): string {
  return indices
    .map((i) => optionLabel(i))
    .filter(Boolean)
    .join(", ");
}

function appendGenerationSettingsLines(
  lines: string[],
  topicTrimmed: string,
  snapshot: QuizGenerationRequestSnapshot,
) {
  lines.push("Your generation inputs");
  if (topicTrimmed !== "") {
    lines.push(`Topic: ${topicTrimmed}`);
  }
  lines.push(`Questions requested: ${String(snapshot.num_questions)}`);
  lines.push(`Primary model: ${snapshot.primary_model_id}`);
  if (snapshot.battle_opponent_model_id?.trim()) {
    lines.push(`Battle opponent: ${snapshot.battle_opponent_model_id.trim()}`);
  }
  if (snapshot.user_instruction_lines.length > 0) {
    lines.push("Instructions:");
    snapshot.user_instruction_lines.forEach((line, i) => {
      lines.push(`${i + 1}. ${line}`);
    });
  }
  if (snapshot.few_shot_examples.length > 0) {
    lines.push("Few-shot examples:");
    snapshot.few_shot_examples.forEach((ex, i) => {
      lines.push(`${i + 1}. ${ex}`);
    });
  }
}

export interface BuildQuizClipboardTextOptions {
  topic?: string;
  commentsByIndex?: string[];
  generationSnapshot?: QuizGenerationRequestSnapshot | null;
}

/** Plain-text quiz for `navigator.clipboard.writeText` (separate from the downloadable journal file). */
export function buildQuizClipboardText(
  quiz: QuizResponse,
  options: BuildQuizClipboardTextOptions = {},
): string {
  const { topic: topicMaybe, commentsByIndex, generationSnapshot } = options;
  const topicTrimmed = topicMaybe?.trim() ?? "";

  const lines: string[] = [];

  if (generationSnapshot != null) {
    appendGenerationSettingsLines(lines, topicTrimmed, generationSnapshot);
    lines.push("");
    lines.push("Quiz output");
  } else if (topicTrimmed !== "") {
    lines.push(`Topic: ${topicTrimmed}`);
  }

  lines.push(`Model used: ${quiz.model_used}`);
  lines.push(`Cost (est.): ${formatEstimatedCostUsd(quiz.cost_usd)}`);
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
