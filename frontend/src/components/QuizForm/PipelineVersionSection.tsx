interface PipelineVersionSectionProps {
  /** `1` = single-call quiz; `2` = multi-step pipeline (default). */
  value: 1 | 2;
  onChange: (next: 1 | 2) => void;
  isLoading: boolean;
}

export function PipelineVersionSection({
  value,
  onChange,
  isLoading,
}: PipelineVersionSectionProps) {
  const groupId = "pipeline-version-label";

  return (
    <fieldset className="mb-4 min-w-0 border-0 p-0">
      <legend id={groupId} className="mb-2 block text-sm font-bold text-[var(--color-text)]">
        Generation version
      </legend>
      <p className="mb-3 mt-0 text-xs leading-relaxed text-[var(--color-text)] opacity-75">
        Pick how the AI builds your quiz before you hit generate.
      </p>
      <div
        className="flex flex-col gap-3"
        role="radiogroup"
        aria-labelledby={groupId}
      >
        <label className="flex cursor-pointer gap-3 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] p-3 has-[:checked]:border-[var(--color-accent)] has-[:checked]:ring-1 has-[:checked]:ring-[var(--color-accent)]">
          <input
            type="radio"
            name="pipeline_version"
            className="mt-1 shrink-0 accent-[var(--color-accent)]"
            checked={value === 2}
            disabled={isLoading}
            onChange={() => onChange(2)}
          />
          <span className="min-w-0">
            <span className="block text-sm font-bold text-[var(--color-text)]">
              Version 2{" "}
              <span className="font-normal opacity-70">(default)</span>
            </span>
            <span className="mt-1 block text-xs leading-relaxed text-[var(--color-text)] opacity-80">
              Questions, then correct answers, then wrong choices—built in
              separate passes so each part can settle before the next.
            </span>
          </span>
        </label>
        <label className="flex cursor-pointer gap-3 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] p-3 has-[:checked]:border-[var(--color-accent)] has-[:checked]:ring-1 has-[:checked]:ring-[var(--color-accent)]">
          <input
            type="radio"
            name="pipeline_version"
            className="mt-1 shrink-0 accent-[var(--color-accent)]"
            checked={value === 1}
            disabled={isLoading}
            onChange={() => onChange(1)}
          />
          <span className="min-w-0">
            <span className="block text-sm font-bold text-[var(--color-text)]">
              Version 1
            </span>
            <span className="mt-1 block text-xs leading-relaxed text-[var(--color-text)] opacity-80">
              Everything in one reply—stems, correct answers, and wrong answers
              together. Quicker, with no separate passes.
            </span>
          </span>
        </label>
      </div>
    </fieldset>
  );
}
