import type { TestFormConfig } from "../../types/test-machine";
import type { GenerateTestResponse } from "../../api";
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
  form: TestFormConfig,
) {
  const topicTrimmed = form.topic.trim();
  lines.push("Your generation inputs");
  if (topicTrimmed !== "") {
    lines.push(`Topic: ${topicTrimmed}`);
  }
  lines.push(`Questions requested: ${String(form.numQuestions)}`);
  lines.push(`Primary model: ${form.models[0]}`);
  if (form.battleEnabled && form.models[1].trim() !== "") {
    lines.push(`Battle opponent: ${form.models[1].trim()}`);
  }
  lines.push("Instructions:");
  form.user_instructions.forEach((line, i) => {
    lines.push(`${i + 1}. ${line}`);
  });
  lines.push("Few-shot examples:");
  form.few_shot_examples.forEach((ex, i) => {
    lines.push(`${i + 1}. ${ex}`);
  });
}

export interface BuildTestClipboardTextOptions {
  commentsByIndex?: string[];
  generationForm: TestFormConfig;
}

export function buildTestClipboardText(
  test: GenerateTestResponse,
  options: BuildTestClipboardTextOptions,
): string {
  const { commentsByIndex, generationForm } = options;

  const lines: string[] = [];
  appendGenerationSettingsLines(lines, generationForm);
  lines.push("");
  lines.push("Test output");
  lines.push(`Model used: ${test.model_used}`);
  lines.push(`Cost (est.): ${formatEstimatedCostUsd(test.cost_usd)}`);
  lines.push("");

  test.questions.forEach((q, qIdx) => {
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
