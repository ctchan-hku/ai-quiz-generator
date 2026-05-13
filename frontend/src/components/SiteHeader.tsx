import type { ReactNode } from "react";
import { BookOpen } from "lucide-react";

interface SiteHeaderProps {
  /** e.g. Journal button (opens the journal drawer on all viewports). */
  trailing?: ReactNode;
}

export function SiteHeader({ trailing }: SiteHeaderProps) {
  return (
    <header className="sticky top-0 z-40 -mx-4 flex items-center justify-between gap-4 border-b border-border bg-background/95 px-4 py-3 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-background/60 md:-mx-8 md:px-8">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
          <BookOpen className="h-6 w-6" />
        </div>
        <div>
          <h1 className="m-0 font-heading text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            AI Quiz Generator
          </h1>
          <p className="m-0 text-sm text-muted-foreground hidden sm:block">
            Turn a topic into a multiple-choice quiz
          </p>
        </div>
      </div>
      {trailing}
    </header>
  );
}
