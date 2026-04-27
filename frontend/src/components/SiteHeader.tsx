import type { ReactNode } from "react";

interface SiteHeaderProps {
  /** e.g. Journal button (opens the journal drawer on all viewports). */
  trailing?: ReactNode;
}

export function SiteHeader({ trailing }: SiteHeaderProps) {
  return (
    <header className="sticky top-0 z-40 flex items-start justify-between gap-4 border-b border-slate-200/80 bg-[var(--color-background)] py-3 text-left shadow-[var(--shadow-sm)]">
      <div>
        <h1 className="mt-0 mb-2 font-[family-name:var(--font-heading)] text-3xl font-semibold text-[var(--color-text)] md:text-4xl">
          AI Quiz Generator
        </h1>
        <p className="mb-0 text-base text-[var(--color-text)] opacity-85">
          Turn a topic into a multiple-choice quiz — academic style preview.
        </p>
      </div>
      {trailing}
    </header>
  );
}
