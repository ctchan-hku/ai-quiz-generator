import { useCallback, useId, useState } from "react";

import type { GenerateTestResponse } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { useExportTestActions } from "@/hooks/useExportTestActions";
import { Button } from "@/components/ui/button";

export interface CurrentTestActionsProps {
  test: GenerateTestResponse;
  comments: string[];
  formConfig: TestFormConfig;
}

export function CurrentTestActions({
  test,
  comments,
  formConfig,
}: CurrentTestActionsProps) {
  const previewPanelId = useId();
  const [isTestSummaryPreviewOpen, setIsTestSummaryPreviewOpen] =
    useState(false);

  const {
    copySummary,
    recordToJournal,
    previewText,
    clipboardError,
    copyDone,
    recordError,
  } = useExportTestActions({ test, comments, formConfig });

  const handleToggleTestSummaryPreview = useCallback(() => {
    setIsTestSummaryPreviewOpen((v) => !v);
  }, []);

  const testSummaryPreviewText = !isTestSummaryPreviewOpen ? "" : previewText;

  return (
    <div className="flex flex-col gap-3 border-t border-border bg-background pt-6 md:border-t-0 md:pt-0">
      <h3 className="m-0 text-sm font-semibold text-foreground">
        Current test actions
      </h3>
      {recordError ? (
        <p className="mb-0 text-sm text-destructive" role="alert">
          {recordError}
        </p>
      ) : null}
      <div className="flex flex-wrap items-center gap-2">
        <Button
          type="button"
          className="w-full justify-center"
          onClick={recordToJournal}
        >
          Record to journal
        </Button>
        <Button
          type="button"
          variant="secondary"
          className="w-full justify-center"
          onClick={handleToggleTestSummaryPreview}
          aria-expanded={isTestSummaryPreviewOpen}
          aria-controls={previewPanelId}
        >
          {isTestSummaryPreviewOpen
            ? "Hide summary"
            : "Preview & copy the summary"}
        </Button>
      </div>

      {isTestSummaryPreviewOpen ? (
        <div
          id={previewPanelId}
          className="mt-2 rounded-lg border border-border bg-card/40"
        >
          <div className="border-b border-border">
            <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-2">
              <span className="text-sm font-semibold text-foreground">
                Test summary preview
              </span>
              <Button
                type="button"
                size="sm"
                className="shrink-0 px-2 py-1 text-xs h-7"
                onClick={copySummary}
              >
                {copyDone ? "Copied!" : "Copy"}
              </Button>
            </div>
            {clipboardError ? (
              <p
                className="mx-3 mb-2 mt-0 text-xs text-destructive"
                role="alert"
              >
                {clipboardError}
              </p>
            ) : null}
          </div>
          <pre className="max-h-60 overflow-auto p-3 text-xs leading-relaxed whitespace-pre-wrap text-foreground m-0 font-body">
            {testSummaryPreviewText}
          </pre>
        </div>
      ) : null}
    </div>
  );
}
