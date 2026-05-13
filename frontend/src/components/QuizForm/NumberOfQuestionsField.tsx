import { Minus, Plus } from "lucide-react";
import { NUM_QUESTIONS_MAX, NUM_QUESTIONS_MIN } from "../../config/quiz";

interface NumberOfQuestionsFieldProps {
  numQuestions: number;
  onNumQuestionsChange: (n: number) => void;
  isLoading: boolean;
}

export function NumberOfQuestionsField({
  numQuestions,
  onNumQuestionsChange,
  isLoading,
}: NumberOfQuestionsFieldProps) {
  function bump(delta: number) {
    const next = Math.min(
      NUM_QUESTIONS_MAX,
      Math.max(NUM_QUESTIONS_MIN, numQuestions + delta),
    );
    onNumQuestionsChange(next);
  }

  return (
    <div>
      <span
        className="mb-1 block text-sm font-bold text-[var(--color-text)]"
        id="num-q-label"
      >
        Number of questions
      </span>
      <div
        className="flex items-center gap-2"
        role="group"
        aria-labelledby="num-q-label"
      >
        <button
          type="button"
          className="btn-secondary !p-2"
          onClick={() => bump(-1)}
          disabled={isLoading || numQuestions <= NUM_QUESTIONS_MIN}
          aria-label="Decrease question count"
        >
          <Minus className="h-5 w-5" aria-hidden />
        </button>
        <input
          type="text"
          readOnly
          className="input max-w-[4rem] text-center"
          value={numQuestions}
          aria-live="polite"
        />
        <button
          type="button"
          className="btn-secondary !p-2"
          onClick={() => bump(1)}
          disabled={isLoading || numQuestions >= NUM_QUESTIONS_MAX}
          aria-label="Increase question count"
        >
          <Plus className="h-5 w-5" aria-hidden />
        </button>
      </div>
      <p className="mt-1 mb-0 text-xs text-[var(--color-text)] opacity-75">
        Between {NUM_QUESTIONS_MIN} and {NUM_QUESTIONS_MAX}
      </p>
    </div>
  );
}
