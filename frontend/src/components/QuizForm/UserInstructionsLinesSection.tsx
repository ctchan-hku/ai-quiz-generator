import type { Dispatch, SetStateAction } from "react";
import {
  USER_INSTRUCTION_LINE_MAX_CHARS,
  USER_INSTRUCTIONS_MAX,
} from "../../config/quiz";

interface UserInstructionsLinesSectionProps {
  lines: string[];
  onLinesChange: Dispatch<SetStateAction<string[]>>;
  isLoading: boolean;
}

/** Each entry is one line (`<input type="text">`); server receives `user_instructions: string[]`. */
export function UserInstructionsLinesSection({
  lines,
  onLinesChange,
  isLoading,
}: UserInstructionsLinesSectionProps) {
  return (
    <details className="mb-4 text-left">
      <summary className="cursor-pointer font-[family-name:var(--font-heading)] text-sm font-semibold text-[var(--color-text)]">
        Quiz-specific instructions{" "}
        <span className="font-normal opacity-75">
          (optional; merged with field rules, not examples)
        </span>
      </summary>
      <div className="mt-3 space-y-3 pl-0">
        {lines.map((line, index) => (
          <div
            key={index}
            className="flex flex-col gap-2 sm:flex-row sm:items-end"
          >
            <div className="min-w-0 flex-1">
              <label
                className="mb-1 block text-xs font-bold text-[var(--color-text)]"
                htmlFor={`quiz-user-instruction-${index}`}
              >
                Line {index + 1}
              </label>
              <input
                id={`quiz-user-instruction-${index}`}
                type="text"
                className="input w-full max-w-full min-w-0"
                maxLength={USER_INSTRUCTION_LINE_MAX_CHARS}
                autoComplete="off"
                placeholder="Optional tone, exclusions, grading emphasis…"
                value={line}
                onChange={(e) => {
                  const next = e.target.value;
                  onLinesChange((prev) => {
                    const copy = [...prev];
                    copy[index] = next;
                    return copy;
                  });
                }}
                disabled={isLoading}
              />
            </div>
            <button
              type="button"
              className="btn-secondary shrink-0"
              onClick={() => {
                onLinesChange((prev) => prev.filter((_, i) => i !== index));
              }}
              disabled={isLoading}
              aria-label={`Remove instruction line ${index + 1}`}
            >
              Remove
            </button>
          </div>
        ))}
        <div>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => {
              if (lines.length < USER_INSTRUCTIONS_MAX) {
                onLinesChange((prev) => [...prev, ""]);
              }
            }}
            disabled={isLoading || lines.length >= USER_INSTRUCTIONS_MAX}
          >
            Add line
          </button>
          {lines.length >= USER_INSTRUCTIONS_MAX ? (
            <p className="mt-1 mb-0 text-xs text-[var(--color-text)] opacity-75">
              Maximum {USER_INSTRUCTIONS_MAX} lines.
            </p>
          ) : null}
        </div>
      </div>
    </details>
  );
}
