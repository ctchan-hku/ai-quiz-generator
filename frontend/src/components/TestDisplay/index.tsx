import { useCallback, useState } from "react";

import type { ChangeEvent } from "react";

import type {
  GenerateTestResponse,
  ModelInfo,
  MultipleChoiceQuestion,
} from "../../api";
import type {
  TestBattleBranchState,
  TestFormConfig,
  RefineQuestionParams,
} from "../../types/test-machine";

import { pipelineVersionCaption } from "../../config/test-form";
import { formatEstimatedCostUsd } from "../../lib/format-usd";

import { BattleOpponentCarousel } from "./BattleOpponentCarousel";
import { CurrentTestActions } from "./CurrentTestActions";
import { TestQuestionCard } from "./TestQuestionCard";
import { TestRunSummaryHero } from "./TestRunSummary";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

export type TestDisplayProps =
  | {
      mode: "battle";
      battle: { left: TestBattleBranchState; right: TestBattleBranchState };
      topic: string;
      pipelineVersion: 1 | 2;
      models: ModelInfo[];
      onPickWinner: (side: "left" | "right") => void;
    }
  | {
      mode: "review";
      test: GenerateTestResponse;
      topic: string;
      generationForm: TestFormConfig;
      models: ModelInfo[];
      resolvedModel: string;
      comments: string[];
      onCommentChange: (index: number, value: string) => void;
      questionVersions: MultipleChoiceQuestion[][];
      selectedVersionIndex: number[];
      onSetQuestionVersion: (index: number, selected: number) => void;
      onRefine: (params: RefineQuestionParams) => void;
      onRefinePanelClose: () => void;
      onCancelRefine?: () => void;
      refiningIndex: number | null;
      refineErrorIndex: number | null;
      refineErrorMessage: string | null;
    };

function labelForModel(models: ModelInfo[], modelId: string) {
  return models.find((m) => m.id === modelId)?.label ?? modelId;
}

function BattleTestQuestions({ test }: { test: GenerateTestResponse }) {
  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-4">
      {test.questions.map((q, qIdx) => (
        <TestQuestionCard key={qIdx} questionIndex={qIdx} question={q} />
      ))}
    </div>
  );
}

function TestBattleView({
  battle,
  topic,
  pipelineVersion,
  models,
  onPickWinner,
}: {
  battle: { left: TestBattleBranchState; right: TestBattleBranchState };
  topic: string;
  pipelineVersion: 1 | 2;
  models: ModelInfo[];
  onPickWinner: (side: "left" | "right") => void;
}) {
  const leftTest = battle.left.baseTestResponse;
  const rightTest = battle.right.baseTestResponse;

  const leftTab = {
    roleLabel: "Left",
    modelLabel: labelForModel(models, leftTest.model_used),
    estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(leftTest.cost_usd)}`,
  };
  const rightTab = {
    roleLabel: "Right",
    modelLabel: labelForModel(models, rightTest.model_used),
    estimatedCostDisplay: `Est. cost ${formatEstimatedCostUsd(rightTest.cost_usd)}`,
  };

  const topicLine =
    topic.trim() !== "" ? (
      <p className="mb-0 mt-0 text-sm text-foreground">
        <span className="font-semibold">Topic: </span>
        {topic.trim()}
      </p>
    ) : null;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        {topicLine}
        <p className="mb-0 mt-0 text-sm text-muted-foreground">
          <span className="font-semibold text-foreground">
            Generation pipeline:{" "}
          </span>
          {pipelineVersionCaption(pipelineVersion)}
        </p>
      </div>

      <BattleOpponentCarousel
        leftTab={leftTab}
        rightTab={rightTab}
        leftPane={<BattleTestQuestions test={leftTest} />}
        rightPane={<BattleTestQuestions test={rightTest} />}
        onConfirmSelection={onPickWinner}
      />
    </div>
  );
}

function TestReviewView(props: Extract<TestDisplayProps, { mode: "review" }>) {
  const {
    test,
    topic,
    generationForm,
    models,
    resolvedModel,
    comments,
    onCommentChange,
    questionVersions,
    selectedVersionIndex,
    onSetQuestionVersion,
    onRefine,
    onRefinePanelClose,
    onCancelRefine,
    refiningIndex,
    refineErrorIndex,
    refineErrorMessage,
  } = props;

  const [refinePanelOpen, setRefinePanelOpen] = useState<
    Record<number, boolean>
  >({});

  const handleVersionChange = useCallback(
    (qIdx: number, e: ChangeEvent<HTMLSelectElement>) => {
      onSetQuestionVersion(qIdx, Number(e.target.value));
    },
    [onSetQuestionVersion],
  );

  const handleCommentChange = useCallback(
    (index: number, e: ChangeEvent<HTMLTextAreaElement>) => {
      onCommentChange(index, e.target.value);
    },
    [onCommentChange],
  );

  const handleConfirmRefine = useCallback(
    (qIdx: number) => {
      onRefine({
        index: qIdx,
        question: test.questions[qIdx],
        comment: comments[qIdx] ?? "",
        model: resolvedModel,
        topic,
      });
    },
    [onRefine, test.questions, comments, resolvedModel, topic],
  );

  function renderQuestionHeader(
    qIdx: number,
    nVersions: number,
    isRefining: boolean,
  ) {
    return (
      <>
        <Label
          className="text-sm font-bold text-foreground"
          htmlFor={`question-version-${qIdx}`}
        >
          Version
        </Label>
        <select
          id={`question-version-${qIdx}`}
          className="flex h-9 w-full max-w-[12rem] items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1"
          value={String(selectedVersionIndex[qIdx])}
          onChange={(e) => handleVersionChange(qIdx, e)}
          disabled={isRefining}
        >
          {Array.from({ length: nVersions }, (_, v) => (
            <option key={v} value={v}>
              Version {v + 1}
            </option>
          ))}
        </select>
      </>
    );
  }

  function renderQuestionFooter(
    qIdx: number,
    isRefining: boolean,
    showRefineError: boolean,
  ) {
    return (
      <>
        <div>
          <Label
            className="mb-2 block text-sm font-bold text-foreground"
            htmlFor={`export-comment-${qIdx}`}
          >
            Comment
          </Label>
          <Textarea
            id={`export-comment-${qIdx}`}
            className="min-h-[4.5rem] resize-y bg-background"
            value={comments[qIdx] ?? ""}
            onChange={(e) => handleCommentChange(qIdx, e)}
            placeholder="Optional comment..."
            rows={2}
            disabled={isRefining}
          />
        </div>

        <div className="mt-4 flex flex-col gap-2">
          {refinePanelOpen[qIdx] ? (
            <div className="flex flex-wrap items-center gap-2">
              <Button
                type="button"
                onClick={() => handleConfirmRefine(qIdx)}
                disabled={isRefining || !resolvedModel.trim()}
              >
                {isRefining ? "Refining…" : "Confirm refinement"}
              </Button>
              {isRefining && onCancelRefine ? (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onCancelRefine}
                >
                  Stop
                </Button>
              ) : null}
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setRefinePanelOpen((prev) => ({ ...prev, [qIdx]: false }));
                  onRefinePanelClose();
                }}
                disabled={isRefining}
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              type="button"
              variant="secondary"
              className="w-full sm:w-auto"
              onClick={() => {
                onRefinePanelClose();
                setRefinePanelOpen((prev) => ({ ...prev, [qIdx]: true }));
              }}
              disabled={isRefining}
            >
              Refine this question
            </Button>
          )}
        </div>

        {showRefineError && refineErrorMessage ? (
          <p className="mb-0 mt-3 text-sm text-destructive" role="alert">
            {refineErrorMessage}
          </p>
        ) : null}
      </>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <TestRunSummaryHero
        test={test}
        models={models}
        pipelineVersion={generationForm.pipeline_version}
      />

      <div className="flex flex-col gap-6 md:flex-row md:items-start md:gap-6 lg:gap-8">
        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-6">
            {test.questions.map((q, qIdx) => {
              const nVersions = questionVersions[qIdx].length;
              const isRefining = refiningIndex === qIdx;
              const showRefineError = refineErrorIndex === qIdx;

              return (
                <TestQuestionCard
                  key={qIdx}
                  questionIndex={qIdx}
                  question={q}
                  header={renderQuestionHeader(qIdx, nVersions, isRefining)}
                  footer={renderQuestionFooter(
                    qIdx,
                    isRefining,
                    showRefineError,
                  )}
                />
              );
            })}
          </div>
        </div>

        <div className="w-full shrink-0 md:w-72 md:self-start md:sticky md:top-30 md:z-30 lg:w-80">
          <CurrentTestActions
            test={test}
            comments={comments}
            generationForm={generationForm}
          />
        </div>
      </div>
    </div>
  );
}

export function TestDisplay(props: TestDisplayProps) {
  if (props.mode === "battle") {
    const { battle, topic, pipelineVersion, models, onPickWinner } = props;
    return (
      <TestBattleView
        battle={battle}
        topic={topic}
        pipelineVersion={pipelineVersion}
        models={models}
        onPickWinner={onPickWinner}
      />
    );
  }

  return <TestReviewView {...props} />;
}
