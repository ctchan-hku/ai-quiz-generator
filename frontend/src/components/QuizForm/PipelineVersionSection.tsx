import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { QUIZ_FORM_SECTION_TITLE_CLASS } from "../../config/quiz-form";

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
    <fieldset className="mb-6 min-w-0 border-0 p-0">
      <legend
        id={groupId}
        className={`${QUIZ_FORM_SECTION_TITLE_CLASS} mb-2 block`}
      >
        Generation Version
      </legend>
      <p className="mb-3 mt-0 text-xs leading-relaxed text-muted-foreground">
        Pick how the AI builds your quiz before you hit generate.
      </p>
      <RadioGroup
        aria-labelledby={groupId}
        value={value.toString()}
        onValueChange={(val) => onChange(Number(val) as 1 | 2)}
        disabled={isLoading}
        className="flex flex-col gap-3"
      >
        <Label
          htmlFor="pipeline-v1"
          className="flex cursor-pointer gap-3 rounded-md border border-border bg-card p-3 has-[:checked]:border-primary has-[:checked]:ring-1 has-[:checked]:ring-primary font-normal"
        >
          <RadioGroupItem
            id="pipeline-v1"
            value="1"
            className="mt-1 shrink-0"
          />
          <span className="min-w-0">
            <span className="block text-sm font-bold text-foreground">
              Version 1
            </span>
            <span className="mt-1 block text-xs leading-relaxed text-muted-foreground">
              Everything in one reply—stems, correct answers, and wrong answers
              together. Quicker, with no separate passes.
            </span>
          </span>
        </Label>
        <Label
          htmlFor="pipeline-v2"
          className="flex cursor-pointer gap-3 rounded-md border border-border bg-card p-3 has-[:checked]:border-primary has-[:checked]:ring-1 has-[:checked]:ring-primary font-normal"
        >
          <RadioGroupItem
            id="pipeline-v2"
            value="2"
            className="mt-1 shrink-0"
          />
          <span className="min-w-0">
            <span className="block text-sm font-bold text-foreground">
              Version 2{" "}
              <span className="font-normal text-muted-foreground">
                (default)
              </span>
            </span>
            <span className="mt-1 block text-xs leading-relaxed text-muted-foreground">
              Questions, then correct answers, then wrong choices—built in
              separate passes so each part can settle before the next.
            </span>
          </span>
        </Label>
      </RadioGroup>
    </fieldset>
  );
}
