const EXAMPLE_PROMPTS = [
  "Photosynthesis and cellular respiration",
  "The French Revolution — causes and outcomes",
  "Introduction to linear algebra: vectors and matrices",
] as const;

interface EmptyStateProps {
  onAutoFill: (topic: string) => void;
}

export function EmptyState({ onAutoFill }: EmptyStateProps) {
  return (
    <div className="card text-left">
      <h2 className="mt-0 mb-2 font-[family-name:var(--font-heading)] text-2xl font-semibold text-[var(--color-text)]">
        What do you want to learn about?
      </h2>
      <p className="mb-6 text-base text-[var(--color-text)] opacity-90">
        Enter a topic or try one of the examples below to generate a quiz.
      </p>
      <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-[var(--color-text)] opacity-80">
        Example topics
      </p>
      <ul className="m-0 flex list-none flex-col gap-2 p-0">
        {EXAMPLE_PROMPTS.map((prompt) => (
          <li key={prompt}>
            <button
              type="button"
              className="btn-secondary w-full justify-start text-left font-normal"
              onClick={() => onAutoFill(prompt)}
            >
              {prompt}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
