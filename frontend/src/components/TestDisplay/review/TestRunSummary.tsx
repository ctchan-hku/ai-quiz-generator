import { Card, CardContent } from "@/components/ui/card";

/** Review header: model and estimated cost for the generated test. */
export function TestRunSummaryHero({
  modelLabel,
  costLabel,
  pipelineCaption,
}: {
  modelLabel: string;
  costLabel: string;
  pipelineCaption: string;
}) {
  return (
    <Card size="sm" className="text-left">
      <CardContent className="pt-0">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 sm:gap-8">
          <div>
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Model
            </p>
            <p className="mt-0 mb-0 text-sm font-medium text-foreground">
              {modelLabel}
            </p>
          </div>
          <div>
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Cost (est.)
            </p>
            <p className="mt-0 mb-0 text-sm font-medium text-foreground">
              {costLabel}
            </p>
          </div>
          <div>
            <p className="mt-0 mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Pipeline
            </p>
            <p className="mt-0 mb-0 text-sm font-medium text-foreground">
              {pipelineCaption}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
