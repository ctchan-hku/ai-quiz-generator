import type { SelectedTestLabel } from "@/lib/selected-tests";
import { Button } from "@/components/ui/button";

interface SelectedTestsSummaryProps {
  labels: SelectedTestLabel[];
  numGroups: number;
  onClearAll: () => void;
}

export function SelectedTestsSummary({
  labels,
  numGroups,
  onClearAll,
}: SelectedTestsSummaryProps) {
  if (labels.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-muted/30 px-3 py-3">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <p className="m-0 text-sm font-medium text-foreground">
          {labels.length} test{labels.length === 1 ? "" : "s"} selected across{" "}
          {numGroups} course group{numGroups === 1 ? "" : "s"}
        </p>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="h-7 px-2 text-xs"
          onClick={onClearAll}
        >
          Clear all
        </Button>
      </div>
      <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
        {labels.map((label) => (
          <li
            key={label.testId}
            className="text-xs text-muted-foreground"
          >
            <span className="font-medium text-foreground">{label.groupName}</span>
            {" · "}
            {label.testName} ({label.numQuestions} question
            {label.numQuestions === 1 ? "" : "s"})
          </li>
        ))}
      </ul>
    </div>
  );
}
