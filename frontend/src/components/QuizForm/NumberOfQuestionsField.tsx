import { Minus, Plus } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
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
      <Label
        className="mb-2 block text-sm font-bold text-foreground"
        id="num-q-label"
      >
        Number of questions
      </Label>
      <div
        className="flex items-center gap-2"
        role="group"
        aria-labelledby="num-q-label"
      >
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={() => bump(-1)}
          disabled={isLoading || numQuestions <= NUM_QUESTIONS_MIN}
          aria-label="Decrease question count"
        >
          <Minus className="h-4 w-4" aria-hidden />
        </Button>
        <Input
          type="text"
          readOnly
          className="max-w-[4rem] text-center"
          value={numQuestions}
          aria-live="polite"
        />
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={() => bump(1)}
          disabled={isLoading || numQuestions >= NUM_QUESTIONS_MAX}
          aria-label="Increase question count"
        >
          <Plus className="h-4 w-4" aria-hidden />
        </Button>
      </div>
      <p className="mt-1.5 mb-0 text-xs text-muted-foreground">
        Between {NUM_QUESTIONS_MIN} and {NUM_QUESTIONS_MAX}
      </p>
    </div>
  );
}
