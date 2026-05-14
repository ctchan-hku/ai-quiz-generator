import type { ModelInfo } from "../../api";
import { pipelineVersionCaption } from "../../config/quiz-form";
import type { QuizFormConfig } from "../../types/quiz-machine";

function resolvedModelLabel(models: ModelInfo[] | undefined, modelId: string) {
  if (!models?.length) return modelId;
  return models.find((m) => m.id === modelId)?.label ?? modelId;
}

interface GenerationSettingsSummaryProps {
  topic: string;
  formConfig?: QuizFormConfig | null;
  models?: ModelInfo[];
}

/**
 * Displays the original generate-form inputs (topic, counts, instructions, examples).
 */
export function GenerationSettingsSummary({
  topic,
  formConfig,
  models,
}: GenerationSettingsSummaryProps) {
  if (!formConfig) {
    const t = topic.trim();
    return t ? (
      <div className="mb-4 text-left">
        <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-60">
          Topic
        </p>
        <p className="mt-0 mb-0 text-sm font-medium text-[var(--color-text)]">
          {t}
        </p>
      </div>
    ) : null;
  }

  const fewShot = formConfig.few_shot_examples;
  const instructions = formConfig.user_instructions;

  return (
    <div className="mb-4 space-y-3 border-b border-[rgb(30_41_59/0.12)] pb-4 text-left">
      <p className="m-0 text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-60">
        Your generation inputs
      </p>
      {topic.trim() !== "" ? (
        <div>
          <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Topic
          </p>
          <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
            {topic.trim()}
          </p>
        </div>
      ) : null}

      <div>
        <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
          Questions requested
        </p>
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
          {formConfig.numQuestions}
        </p>
      </div>

      <div>
        <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
          Generation pipeline
        </p>
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
          {pipelineVersionCaption(formConfig.pipeline_version)}
        </p>
      </div>

      <div>
        <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
          Primary model
        </p>
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
          {resolvedModelLabel(models, formConfig.models[0])}
        </p>
      </div>

      {formConfig.battleEnabled && formConfig.models[1].trim() !== "" ? (
        <div>
          <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Battle opponent
          </p>
          <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
            {resolvedModelLabel(models, formConfig.models[1].trim())}
          </p>
        </div>
      ) : null}

      {instructions.length > 0 ? (
        <div>
          <p className="mt-0 mb-1 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Instructions
          </p>
          <ul className="mt-0 mb-0 space-y-1 pl-4 text-sm text-[var(--color-text)]">
            {instructions.map((line, i) => (
              <li key={i} className="leading-snug">
                {line.trim() !== "" ? line : "—"}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {fewShot.length > 0 ? (
        <div>
          <p className="mt-0 mb-1 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Few-shot examples
          </p>
          <ul className="mt-0 mb-0 space-y-1 pl-4 text-sm text-[var(--color-text)]">
            {fewShot.map((example, i) => (
              <li key={i} className="leading-snug">
                <span className="font-medium opacity-70">{i + 1}. </span>
                {example.trim() !== "" ? example : "—"}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
