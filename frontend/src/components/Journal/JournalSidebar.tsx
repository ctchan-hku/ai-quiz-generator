import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { GenerationSummary } from "./GenerationSummary";
import type { JournalEntry } from "@/hooks/useJournal";

export interface JournalSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  downloadError: string | null;
  journalEmpty: boolean;
  entries: JournalEntry[];
  handleExportJournal: () => void;
  handleClearJournal: () => void;
  handleRemoveFromJournal: (index: number) => void;
  handleToggleJournalItem: (index: number) => void;
}

export function JournalSidebar({
  isOpen,
  onClose,
  downloadError,
  journalEmpty,
  entries,
  handleExportJournal,
  handleClearJournal,
  handleRemoveFromJournal,
  handleToggleJournalItem,
}: JournalSidebarProps) {
  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader className="mb-6">
          <SheetTitle className="font-heading text-xl">Journal Menu</SheetTitle>
          <SheetDescription>
            The journal stores your recorded tests in this browser. You can
            export the entire journal as a single JSON file.
          </SheetDescription>
        </SheetHeader>

        <section className="text-left">
          {downloadError ? (
            <p className="mb-4 text-sm text-destructive" role="alert">
              {downloadError}
            </p>
          ) : null}

          <h3 className="mb-4 font-heading text-base font-semibold text-foreground">
            Recorded tests
          </h3>

          {journalEmpty ? (
            <p className="text-sm italic text-muted-foreground">
              No tests recorded yet.
            </p>
          ) : (
            <div className="mb-6 flex flex-col gap-3">
              {entries.map((entry) => (
                <div
                  key={entry.index}
                  className="flex flex-col rounded-lg border border-border bg-card/50"
                >
                  <div className="flex flex-col justify-between gap-3 px-4 py-3 sm:flex-row sm:items-center">
                    <div className="flex min-w-0 flex-1 flex-col">
                      <span className="truncate text-sm font-medium text-foreground">
                        {entry.title}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {entry.questionCount} question
                        {entry.questionCount === 1 ? "" : "s"}
                        {` · ${entry.pipelineCaption}`}
                      </span>
                    </div>
                    <div className="flex shrink-0 items-center gap-2 pt-2 sm:pt-0">
                      <Button
                        variant="secondary"
                        size="sm"
                        className="h-7 text-xs px-2"
                        onClick={() => handleToggleJournalItem(entry.index)}
                        aria-expanded={entry.isExpanded}
                      >
                        {entry.isExpanded ? "Collapse" : "Expand"}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="h-7 text-xs px-2"
                        onClick={() => handleRemoveFromJournal(entry.index)}
                        aria-label={`Remove test ${entry.index + 1}`}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>

                  {entry.isExpanded ? (
                    <div className="border-t border-border px-4 py-4 bg-muted/20">
                      <GenerationSummary {...entry.generationSummary} />
                      <p className="mb-3 mt-0 text-xs text-muted-foreground">
                        Model: {entry.recordModelLine}
                      </p>
                      <div className="flex flex-col gap-4">
                        {entry.questions.map((question, qIdx) => (
                          <div key={qIdx} className="text-xs text-foreground">
                            <p className="mt-0 mb-1.5 font-medium leading-relaxed">
                              {qIdx + 1}. {question.question}
                            </p>
                            {question.comment ? (
                              <p className="mt-0 mb-0 italic text-primary">
                                Comment: {question.comment}
                              </p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 flex flex-col gap-3">
            <Button
              className="w-full"
              onClick={handleExportJournal}
              disabled={journalEmpty}
            >
              Export journal as JSON
            </Button>
            <Button
              variant="secondary"
              className="w-full"
              onClick={handleClearJournal}
              disabled={journalEmpty}
            >
              Clear journal
            </Button>
          </div>
        </section>
      </SheetContent>
    </Sheet>
  );
}
