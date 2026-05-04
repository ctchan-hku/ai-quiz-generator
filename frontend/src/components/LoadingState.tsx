import type { ReactNode } from "react";

interface LoadingStateProps {
  toolbarRight?: ReactNode;
}

/** Pulse-only skeleton — avoids continuous bounce animations that read as noisy. */
export function LoadingState({ toolbarRight }: LoadingStateProps) {
  return (
    <div className="card text-left" aria-busy="true" aria-live="polite">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="mt-0 mb-0 font-[family-name:var(--font-heading)] text-xl font-semibold text-[var(--color-text)]">
          Generating questions...
        </p>
        {toolbarRight}
      </div>
      <div className="flex flex-col gap-3">
        <div className="h-4 w-3/4 max-w-md animate-pulse rounded-md bg-[var(--color-secondary)]/20" />
        <div className="h-4 w-full max-w-lg animate-pulse rounded-md bg-[var(--color-secondary)]/15" />
        <div className="h-4 w-5/6 max-w-md animate-pulse rounded-md bg-[var(--color-secondary)]/15" />
        <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
          <div className="h-14 animate-pulse rounded-lg bg-white/40" />
          <div className="h-14 animate-pulse rounded-lg bg-white/40" />
        </div>
      </div>
    </div>
  );
}
