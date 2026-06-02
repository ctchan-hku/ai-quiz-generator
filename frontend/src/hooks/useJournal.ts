import { useCallback, useEffect, useState } from "react";
import type { ModelInfo } from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import { pipelineVersionCaption } from "@/config/test-form";
import { formatEstimatedCostUsd } from "@/lib/display/format-usd";
import { modelDisplayLabel } from "@/lib/model-board/model-label";
import {
  clearJournal,
  downloadJournalFile,
  loadJournal,
  removeExportTestRecord,
} from "@/lib/test-exports/journal";

const listeners = new Set<() => void>();

/** Call after a test is saved to local journal storage so open sidebars refresh. */
export function notifyJournalRecorded() {
  for (const listener of listeners) {
    listener();
  }
}

function subscribeToJournalRecorded(callback: () => void) {
  listeners.add(callback);
  return () => {
    listeners.delete(callback);
  };
}

export interface JournalEntryQuestion {
  question: string;
  comment: string;
}

export interface JournalGenerationSummary {
  topicLine: string | null;
  numQuestions: number;
  pipelineCaption: string;
  primaryModelLabel: string;
  battleOpponentLabel: string | null;
  instructionLines: string[];
  fewShotLines: string[];
}

export interface JournalEntry {
  index: number;
  title: string;
  questionCount: number;
  pipelineCaption: string;
  recordModelLine: string;
  generationSummary: JournalGenerationSummary;
  questions: JournalEntryQuestion[];
  isExpanded: boolean;
}

function buildGenerationSummary(
  formConfig: TestFormConfig,
  models: ModelInfo[] | undefined,
): JournalGenerationSummary {
  const topicTrimmed = formConfig.topic.trim();
  const opponentId = formConfig.models[1]?.trim() ?? "";
  return {
    topicLine: topicTrimmed !== "" ? topicTrimmed : null,
    numQuestions: formConfig.numQuestions,
    pipelineCaption: pipelineVersionCaption(formConfig.pipelineVersion),
    primaryModelLabel: modelDisplayLabel(models, formConfig.models[0]),
    battleOpponentLabel:
      formConfig.battleEnabled && opponentId !== ""
        ? modelDisplayLabel(models, opponentId)
        : null,
    instructionLines: formConfig.userInstructions,
    fewShotLines: formConfig.fewShotExamples,
  };
}

export function useJournal(models?: ModelInfo[]) {
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
  }, [refreshJournal]);

  const handleExportJournal = useCallback(() => {
    setDownloadError(null);
    try {
      downloadJournalFile(journal);
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : "Download failed.");
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

  const entries: JournalEntry[] = journal.tests.map((record, index) => {
    const pipelineCaption = pipelineVersionCaption(
      record.formConfig.pipelineVersion,
    );
    const costLabel = formatEstimatedCostUsd(record.costUsd);
    const modelLabel = modelDisplayLabel(models, record.modelUsed);
    return {
      index,
      title: record.formConfig.topic.trim() || "Untitled test",
      questionCount: record.questions.length,
      pipelineCaption,
      recordModelLine: `${modelLabel} · ${costLabel} · ${pipelineCaption}`,
      generationSummary: buildGenerationSummary(record.formConfig, models),
      questions: record.questions,
      isExpanded: expandedJournalIndex === index,
    };
  });

  return {
    downloadError,
    journalEmpty: journal.tests.length === 0,
    entries,
    handleExportJournal,
    handleClearJournal,
    handleRemoveFromJournal,
    handleToggleJournalItem,
  };
}
