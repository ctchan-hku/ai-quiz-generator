import { useCallback, useEffect, useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

import { GenerationSummary } from "./GenerationSummary";
import { pipelineVersionCaption } from "@/config/test-form";
import { formatEstimatedCostUsd } from "@/lib/format-usd";
import {
  clearJournal,
  downloadJournalFile,
  loadJournal,
  removeExportTestRecord,
} from "@/lib/export-test/journal";

import type { ModelInfo } from "@/api/contracts";

import { useJournal } from "./useJournal";

export interface JournalSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  /** Optional resolve model ids → labels in recorded generation snapshots. */
  models?: ModelInfo[];
}

export function JournalSidebar({
  isOpen,
  onClose,
  models,
}: JournalSidebarProps) {
  const { subscribeToJournalRecorded } = useJournal();
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [journal, setJournal] = useState(() => loadJournal());
  const [expandedJournalIndex, setExpandedJournalIndex] = useState<
    number | null
  >(null);

  const refreshJournal = useCallback(() => {
    setJournal(loadJournal());
  }, []);

  useEffect(() => {
    return subscribeToJournalRecorded(refreshJournal);
  }, [refreshJournal, subscribeToJournalRecorded]);

  const handleExportJournal = useCallback(() => {
    setDownloadError(null);
    try {
      downloadJournalFile(journal);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Download failed.";
      setDownloadError(message);
    }
  }, [journal]);

  const handleClearJournal = useCallback(() => {
    const ok = window.confirm(
      "Clear the export journal? This removes all saved tests from this browser only. This cannot be undone.",
    );
    if (!ok) return;
    clearJournal();
    refreshJournal();
  }, [refreshJournal]);

  const handleRemoveFromJournal = useCallback(
    (index: number) => {
      removeExportTestRecord(index);
      refreshJournal();
      setExpandedJournalIndex((prev) => (prev === index ? null : prev));
    },
    [refreshJournal],
  );

  const handleToggleJournalItem = useCallback((index: number) => {
    setExpandedJournalIndex((prev) => (prev === index ? null : index));
  }, []);

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

          {journal.tests.length === 0 ? (
            <p className="text-sm italic text-muted-foreground">
              No tests recorded yet.
            </p>
          ) : (
            <div className="mb-6 flex flex-col gap-3">
              {journal.tests.map((q, i) => (
                <div
                  key={i}
                  className="flex flex-col rounded-lg border border-border bg-card/50"
                >
                  <div className="flex flex-col justify-between gap-3 px-4 py-3 sm:flex-row sm:items-center">
                    <div className="flex min-w-0 flex-1 flex-col">
                      <span className="truncate text-sm font-medium text-foreground">
                        {q.formConfig.topic.trim() || "Untitled test"}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {q.questions.length} question
                        {q.questions.length === 1 ? "" : "s"}
                        {` · ${pipelineVersionCaption(q.formConfig.pipelineVersion)}`}
                      </span>
                    </div>
                    <div className="flex shrink-0 items-center gap-2 pt-2 sm:pt-0">
                      <Button
                        variant="secondary"
                        size="sm"
                        className="h-7 text-xs px-2"
                        onClick={() => handleToggleJournalItem(i)}
                        aria-expanded={expandedJournalIndex === i}
                      >
                        {expandedJournalIndex === i ? "Collapse" : "Expand"}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="h-7 text-xs px-2"
                        onClick={() => handleRemoveFromJournal(i)}
                        aria-label={`Remove test ${i + 1}`}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>

                  {expandedJournalIndex === i ? (
                    <div className="border-t border-border px-4 py-4 bg-muted/20">
                      <GenerationSummary
                        formConfig={q.formConfig}
                        models={models}
                      />
                      <p className="mb-3 mt-0 text-xs text-muted-foreground">
                        Model: {q.modelUsed} ·{" "}
                        {formatEstimatedCostUsd(q.costUsd)}
                        {` · ${pipelineVersionCaption(q.formConfig.pipelineVersion)}`}
                      </p>
                      <div className="flex flex-col gap-4">
                        {q.questions.map((question, qIdx) => (
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
              disabled={journal.tests.length === 0}
            >
              Export journal as JSON
            </Button>
            <Button
              variant="secondary"
              className="w-full"
              onClick={handleClearJournal}
              disabled={journal.tests.length === 0}
            >
              Clear journal
            </Button>
          </div>
        </section>
      </SheetContent>
    </Sheet>
  );
}
