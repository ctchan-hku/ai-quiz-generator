import type { JournalGenerationSummary } from "@/hooks/useJournal";

export function GenerationSummary({
  topicLine,
  numQuestions,
  pipelineCaption,
  primaryModelLabel,
  battleOpponentLabel,
  instructionLines,
  fewShotLines,
}: JournalGenerationSummary) {
  return (
    <div className="mb-4 space-y-3 border-b border-[rgb(30_41_59/0.12)] pb-4 text-left">
      <p className="m-0 text-xs font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-60">
        Your generation inputs
      </p>
      {topicLine != null ? (
        <div>
          <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Topic
          </p>
          <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
            {topicLine}
          </p>
        </div>
      ) : null}

      <div>
        <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
          Questions requested
        </p>
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
          {numQuestions}
        </p>
      </div>

      <div>
        <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
          Generation pipeline
        </p>
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
          {pipelineCaption}
        </p>
      </div>

      <div>
        <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
          Primary model
        </p>
        <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
          {primaryModelLabel}
        </p>
      </div>

      {battleOpponentLabel != null ? (
        <div>
          <p className="mt-0 mb-0.5 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Battle opponent
          </p>
          <p className="mt-0 mb-0 text-sm text-[var(--color-text)]">
            {battleOpponentLabel}
          </p>
        </div>
      ) : null}

      {instructionLines.length > 0 ? (
        <div>
          <p className="mt-0 mb-1 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Instructions
          </p>
          <ul className="mt-0 mb-0 space-y-1 pl-4 text-sm text-[var(--color-text)]">
            {instructionLines.map((line, i) => (
              <li key={i} className="leading-snug">
                {line.trim() !== "" ? line : "—"}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {fewShotLines.length > 0 ? (
        <div>
          <p className="mt-0 mb-1 text-xs font-semibold text-[var(--color-text)] opacity-70">
            Few-shot examples
          </p>
          <ul className="mt-0 mb-0 space-y-1 pl-4 text-sm text-[var(--color-text)]">
            {fewShotLines.map((example, i) => (
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
