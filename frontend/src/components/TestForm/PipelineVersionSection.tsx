import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { TestFormSectionTitle } from "./TestFormSectionTitle";

interface PipelineVersionSectionProps {
  /** `1` = single-call test; `2` = multi-step pipeline (default). */
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
      <TestFormSectionTitle id={groupId} as="legend" className="mb-2 block">
        Generation Pipeline Version
      </TestFormSectionTitle>
      <p className="mb-3 mt-0 text-xs leading-relaxed text-muted-foreground">
        Pick how the AI builds your test before you hit generate.
      </p>
      <RadioGroup
        aria-labelledby={groupId}
        value={`${value}`}
        onValueChange={(val: string) => onChange(val === "1" ? 1 : 2)}
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
