import { useMemo } from "react";
import { ListChecks } from "lucide-react";

import type { SelectedTestLabel } from "@/lib/selected-tests";
import {
  groupSelectedTestLabels,
  totalSelectedQuestions,
} from "@/lib/selected-tests";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

interface SelectedTestsSummaryProps {
  labels: SelectedTestLabel[];
  numGroups: number;
  onClearAll: () => void;
}

function SummaryStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-border bg-muted/40 px-2.5 py-2">
      <p className="m-0 text-lg font-semibold leading-none tabular-nums text-foreground">
        {value}
      </p>
      <p className="m-0 mt-1 text-[0.65rem] font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
    </div>
  );
}

export function SelectedTestsSummary({
  labels,
  numGroups,
  onClearAll,
}: SelectedTestsSummaryProps) {
  const groupedLabels = useMemo(
    () => groupSelectedTestLabels(labels),
    [labels],
  );
  const numQuestions = totalSelectedQuestions(labels);

  return (
    <div className="flex max-h-[calc(100vh-6rem)] flex-col overflow-hidden rounded-xl bg-card text-sm ring-1 ring-foreground/10">
      <div className="shrink-0 space-y-3 border-b border-border px-3 py-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="m-0 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Reference selection
            </p>
            <p className="m-0 mt-1 text-sm text-muted-foreground">
              Tests used as few-shot examples for generation
            </p>
          </div>
          {labels.length > 0 ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7 shrink-0 bg-background px-2 text-xs"
              onClick={onClearAll}
            >
              Clear all
            </Button>
          ) : null}
        </div>

        {labels.length > 0 ? (
          <div className="grid grid-cols-3 gap-2">
            <SummaryStat label="Tests" value={labels.length} />
            <SummaryStat label="Groups" value={numGroups} />
            <SummaryStat label="Questions" value={numQuestions} />
          </div>
        ) : null}
      </div>

      {labels.length === 0 ? (
        <div className="flex flex-col items-center gap-2 px-4 py-8 text-center">
          <div className="flex size-10 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <ListChecks className="size-5" aria-hidden />
          </div>
          <p className="m-0 text-sm font-medium text-foreground">
            No reference tests selected
          </p>
          <p className="m-0 max-w-[14rem] text-xs leading-relaxed text-muted-foreground">
            Expand a course group and select tests to include as generation
            references.
          </p>
        </div>
      ) : (
        <div className="min-h-0 flex-1 overflow-y-auto px-3 py-3">
          <ul className="m-0 flex list-none flex-col gap-4 p-0">
            {groupedLabels.map((group, groupIndex) => (
              <li key={group.groupName}>
                {groupIndex > 0 ? <Separator className="mb-4" /> : null}
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <p className="m-0 min-w-0 truncate text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      {group.groupName}
                    </p>
                    <Badge variant="secondary" className="shrink-0 text-[0.65rem]">
                      {group.tests.length}
                    </Badge>
                  </div>
                  <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
                    {group.tests.map((label) => (
                      <li
                        key={label.testId}
                        className="rounded-lg border border-border bg-muted/20 px-2.5 py-2"
                      >
                        <p className="m-0 text-sm font-medium leading-snug text-foreground">
                          {label.testName}
                        </p>
                        <p className="m-0 mt-1 text-xs text-muted-foreground">
                          {label.numQuestions} question
                          {label.numQuestions === 1 ? "" : "s"}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
