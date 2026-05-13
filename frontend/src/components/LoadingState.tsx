import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";

interface LoadingStateProps {
  toolbarRight?: ReactNode;
  /** When set, replaces the default headline (e.g. battle mode parallel generation). */
  headline?: string;
}

/** Pulse-only skeleton — avoids continuous bounce animations that read as noisy. */
export function LoadingState({ toolbarRight, headline }: LoadingStateProps) {
  return (
    <Card
      size="sm"
      className="text-left"
      aria-busy="true"
      aria-live="polite"
    >
      <CardContent className="pt-0">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <p className="mt-0 mb-0 font-heading text-xl font-semibold text-foreground">
            {headline ?? "Generating questions..."}
          </p>
          {toolbarRight}
        </div>
        <div className="flex flex-col gap-3">
          <div className="h-4 w-3/4 max-w-md animate-pulse rounded-md bg-secondary/40" />
          <div className="h-4 w-full max-w-lg animate-pulse rounded-md bg-secondary/30" />
          <div className="h-4 w-5/6 max-w-md animate-pulse rounded-md bg-secondary/30" />
          <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className="h-14 animate-pulse rounded-lg bg-muted/50" />
            <div className="h-14 animate-pulse rounded-lg bg-muted/50" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
